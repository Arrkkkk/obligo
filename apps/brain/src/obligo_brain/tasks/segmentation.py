"""The async segmentation task (blueprint §11, §21 Phase 3) -- the actual
extraction logic that used to run inline inside
POST /api/v1/sources/{source_id}/segment now runs here instead, on a Celery
worker. The endpoint's job shrank to: validate, INSERT a QUEUED
segmentation_jobs row, enqueue this task, return 202. See
api/v1/sources.py's module docstring for the endpoint side of this split.

**Tenant isolation through a task, not an HTTP request -- the load-bearing
difference from the synchronous endpoint.** contextvars.ContextVar does not
cross a process boundary; a Celery worker executing this task is a separate
OS process from the FastAPI request that enqueued it. TenantContext.set()
is called explicitly below, fresh, from this task's own (org_id) argument --
exactly what the old endpoint did, just relocated to a new entrypoint. Same
discipline: try/finally -> TenantContext.clear(), except now the "session"
this brackets is one task execution, not one HTTP request.

**What changed about the trust picture, stated plainly, not glossed over as
"no different":** org_id now travels as a plain, serialized argument in a
message on the Redis broker, not just in an HTTP request body. This is the
same underlying trust gap CLAUDE.md's shared-secret-gate debt note already
documents (org_id is trusted, not cryptographically verified) -- but it
widens *who* can assert that claim: previously only HTTP-reaching the
endpoint with a valid BRAIN_SERVICE_TOKEN sufficed; now anyone holding the
Redis broker credentials can also enqueue a task asserting an arbitrary
org_id. And because a message can be retried, a single unverified claim
now gets replayed across this task's full retry lifecycle, not just one
request. Not a new problem in kind -- a real widening, worth remembering
when the shared-secret-gate debt note is revisited.

**Failure handling -- two genuinely different failure classes, not one:**
1. Catchable, in-Python failures (a bad PDF, a transient Supabase fetch
   error, SoftTimeLimitExceeded): caught below, retried via self.retry()
   with backoff up to max_retries, then marked FAILED in segmentation_jobs
   on the last attempt. self.request.retries tracks this.
2. The worker process dying outright (SIGKILL/OOM -- exactly the risk
   blueprint names Tesseract/PaddleOCR as capable of causing; or hitting
   Celery's hard time_limit, which SIGKILLs the worker child itself): no
   Python exception handler in this file ever runs. task_acks_late=True
   (celery_app.py) means the un-acked message gets redelivered to another
   worker instead of silently vanishing -- but redelivery is a
   broker-level mechanism, NOT the same thing as self.retry(), and does
   NOT increment self.request.retries. A task stuck in this failure class
   could in principle be redelivered indefinitely without ever tripping
   the max_retries check above. This is exactly why a staleness
   reconciliation check exists on the read side (see
   api/v1/sources.py's status endpoint) as a second, independent
   mitigation layer -- not redundant with max_retries, covering a
   failure class it structurally cannot.
"""

from __future__ import annotations

import random
from uuid import UUID

from sqlalchemy import text

from obligo_brain.ingestion.loaders.pdf import extract_segments
from obligo_brain.platform.storage.supabase import fetch_object
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope
from obligo_brain.tasks.celery_app import OCR_QUEUE_NAME, app

MAX_RETRIES = 3
SOFT_TIME_LIMIT_SECONDS = 300
HARD_TIME_LIMIT_SECONDS = 600
# Blueprint's own §14 numbers for the ocr queue (300s/600s soft/hard,
# 3 retries + backoff/jitter) -- a reasonable starting anchor, though sized
# with PaddleOCR's cost profile in mind. Worth revisiting against
# Tesseract's actually-observed latency (~1-2 min for the 1-2 page OCR
# fixtures in this checkpoint's own tests) rather than trusting unchecked;
# not revised here since nothing observed so far has approached these caps.


def _retry_countdown(retry_number: int) -> float:
    """Exponential backoff + jitter, computed manually since manual
    self.retry() calls don't consume the autoretry_for decorator's
    retry_backoff/retry_jitter options -- those only apply to Celery's own
    automatic-retry machinery, not explicit self.retry() calls."""
    base = min(2**retry_number, 60)
    return base + random.uniform(0, base * 0.1)


def _mark_job_processing(source_id: UUID, org_id: UUID) -> None:
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            conn.execute(
                text(
                    "UPDATE segmentation_jobs SET status = 'PROCESSING', updated_at = now() "
                    "WHERE source_id = :source_id"
                ),
                {"source_id": source_id},
            )
    finally:
        TenantContext.clear()


def _persist_segments_and_mark_succeeded(source_id: UUID, org_id: UUID, segments: list) -> int:
    """One transaction: segment rows and the SUCCEEDED status land together
    or not at all -- a status-endpoint caller must never observe SUCCEEDED
    with zero segments actually persisted."""
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            for segment in segments:
                conn.execute(
                    text(
                        "INSERT INTO segments "
                        "(org_id, source_id, ordinal, page, char_start, char_end, text, ocr_confidence) "
                        "VALUES (:org_id, :source_id, :ordinal, :page, :char_start, :char_end, :text, :ocr_confidence)"
                    ),
                    {
                        "org_id": org_id,
                        "source_id": source_id,
                        "ordinal": segment.ordinal,
                        "page": segment.page,
                        "char_start": segment.char_start,
                        "char_end": segment.char_end,
                        "text": segment.text,
                        "ocr_confidence": segment.ocr_confidence,
                    },
                )
            conn.execute(
                text(
                    "UPDATE segmentation_jobs SET status = 'SUCCEEDED', segment_count = :count, "
                    "updated_at = now() WHERE source_id = :source_id"
                ),
                {"source_id": source_id, "count": len(segments)},
            )
        return len(segments)
    finally:
        TenantContext.clear()


def _mark_job_failed(source_id: UUID, org_id: UUID, error: str, attempt_count: int) -> None:
    """Terminal failure only -- retries exhausted, or a non-retryable
    error. Never called for an attempt that's about to retry; see
    _record_retryable_attempt for that case.

    `AND status != 'SUCCEEDED'` is defense-in-depth, not redundant with
    celery_app.py's visibility_timeout tuning: that setting makes premature
    redelivery (a second worker starting the same task while the first is
    still legitimately running) structurally unlikely, not structurally
    impossible under every broker/network condition. If it ever did happen
    anyway, this guard is what stops the redundant worker's eventual
    failure from overwriting a job the first worker already completed
    successfully.
    """
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            conn.execute(
                text(
                    "UPDATE segmentation_jobs SET status = 'FAILED', last_error = :error, "
                    "attempt_count = :attempts, updated_at = now() "
                    "WHERE source_id = :source_id AND status != 'SUCCEEDED'"
                ),
                {"source_id": source_id, "error": error[:2000], "attempts": attempt_count},
            )
    finally:
        TenantContext.clear()


def _record_retryable_attempt(source_id: UUID, org_id: UUID, error: str, attempt_count: int) -> None:
    """Records the error and bumps attempt_count for diagnostic visibility,
    but deliberately leaves status at PROCESSING -- FAILED is a terminal
    state (see _mark_job_failed's docstring); a status-endpoint caller
    seeing FAILED should be able to assume the job is over, not "over for
    now, about to retry." last_error is still updated so this attempt's
    failure isn't invisible even while status stays PROCESSING.
    """
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            conn.execute(
                text(
                    "UPDATE segmentation_jobs SET last_error = :error, attempt_count = :attempts, "
                    "updated_at = now() WHERE source_id = :source_id"
                ),
                {"source_id": source_id, "error": error[:2000], "attempts": attempt_count},
            )
    finally:
        TenantContext.clear()


def _fetch_source_storage_key(source_id: UUID, org_id: UUID) -> str:
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            row = conn.execute(
                text("SELECT storage_key FROM sources WHERE id = :id"), {"id": source_id}
            ).mappings().first()
    finally:
        TenantContext.clear()
    if row is None:
        raise LookupError(f"source {source_id} not found or not visible to org {org_id}")
    return row["storage_key"]


@app.task(
    bind=True,
    name="obligo_brain.tasks.segmentation.segment_source_task",
    queue=OCR_QUEUE_NAME,
    max_retries=MAX_RETRIES,
    soft_time_limit=SOFT_TIME_LIMIT_SECONDS,
    time_limit=HARD_TIME_LIMIT_SECONDS,
)
def segment_source_task(self, source_id: str, org_id: str) -> None:
    source_uuid = UUID(source_id)
    org_uuid = UUID(org_id)

    _mark_job_processing(source_uuid, org_uuid)

    try:
        storage_key = _fetch_source_storage_key(source_uuid, org_uuid)
        pdf_bytes = fetch_object(storage_key)
        segments = extract_segments(pdf_bytes)
        _persist_segments_and_mark_succeeded(source_uuid, org_uuid, segments)
    # Broad by design: expected real failure modes are LookupError (source
    # row vanished/not visible), SupabaseObjectUnavailableError (storage
    # fetch), PdfExtractionError (malformed PDF), IntegrityError (a race on
    # segmentation_jobs), and celery.exceptions.SoftTimeLimitExceeded (the
    # 300s soft cap) -- all Exception subclasses, so a single broad catch
    # here is deliberate, not carelessness: anything unexpected still goes
    # through the same retry-then-terminal-failure path rather than
    # crashing the worker process silently.
    except Exception as exc:
        attempt = self.request.retries
        if attempt >= self.max_retries:
            _mark_job_failed(source_uuid, org_uuid, repr(exc), attempt + 1)
            raise
        _record_retryable_attempt(source_uuid, org_uuid, repr(exc), attempt + 1)
        raise self.retry(exc=exc, countdown=_retry_countdown(attempt))
