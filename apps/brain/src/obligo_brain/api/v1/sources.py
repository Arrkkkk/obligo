"""Segmentation trigger + status endpoints (blueprint §11, §21 Phase 3).

**Contract change from the synchronous checkpoint, not an addition to it:**
POST used to compute segments inline and return them. OCR is genuinely slow
(Tesseract -- see CLAUDE.md's OCR-checkpoint notes), so extraction now runs
on a Celery worker (obligo_brain.tasks.segmentation.segment_source_task);
this endpoint's job shrank to validating the source, recording a
segmentation_jobs row (V15), enqueuing the task, and returning 202
immediately -- it never calls extract_segments itself anymore. GET is new:
it's how a caller (apps/core, until SSE exists) learns the outcome, since
apps/core deliberately has no DB grant on segmentation_jobs -- see V15's
own migration comment for why that's a status-endpoint call, not a DB read.

**Known, deliberate gap -- not silently assumed solved, same note carried
over from the synchronous version, now wider in scope, not narrower:**
org_id is still a plain, trusted field, not a cryptographically verified
claim. It previously only had to survive one HTTP request; now it also
travels as a serialized Celery task argument on the Redis broker, and can
be replayed across that task's full retry lifecycle. Anyone holding the
Redis broker credentials can now also assert an arbitrary org_id, not just
whoever can reach this endpoint with BRAIN_SERVICE_TOKEN. See
tasks/segmentation.py's module docstring for the full statement of this,
and CLAUDE.md's debt list for why the real fix (a short-lived, per-request
token apps/core mints after its own JWT verification) is still missing.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from obligo_brain.platform.security.internal_auth import require_internal_service_token
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope
from obligo_brain.tasks.segmentation import segment_source_task

router = APIRouter()

STALE_PROCESSING_AFTER = timedelta(seconds=900)
"""A job stuck at PROCESSING past this bound is treated as failed on read,
rather than trusted to eventually resolve on its own. Deliberately larger
than segmentation.py's HARD_TIME_LIMIT_SECONDS (600s) to allow room for
Celery's own retry/backoff cycle to still be legitimately in flight --
this bound is about "worker died and nothing is coming," not "still
retrying." This is the interim, on-read version of the staleness
reconciliation blueprint's design calls for; a periodic Celery beat sweep
is the more robust version and is real future work, not built here --
same "bounded, not solved" posture as this codebase's other interim
mitigations (e.g. SourceUploadService.MAX_PENDING_AGE started the same
way)."""


class SegmentSourceRequest(BaseModel):
    org_id: UUID


class SegmentSourceAcceptedResponse(BaseModel):
    source_id: UUID
    status: str


class SegmentationJobStatusResponse(BaseModel):
    source_id: UUID
    status: str
    attempt_count: int
    segment_count: int | None
    last_error: str | None


@router.post(
    "/api/v1/sources/{source_id}/segment",
    response_model=SegmentSourceAcceptedResponse,
    status_code=202,
    dependencies=[Depends(require_internal_service_token)],
)
def segment_source(source_id: UUID, body: SegmentSourceRequest) -> SegmentSourceAcceptedResponse:
    TenantContext.set(body.org_id)
    try:
        with tenant_scope() as conn:
            row = conn.execute(
                text("SELECT status FROM sources WHERE id = :id"), {"id": source_id}
            ).mappings().first()

        if row is None:
            # RLS-scoped: indistinguishable from "exists but belongs to
            # another org" by design -- fail closed, no cross-tenant
            # existence leak via a 404-vs-403 distinction.
            raise HTTPException(status_code=404, detail="source not found")

        if row["status"] != "UPLOADED":
            raise HTTPException(
                status_code=409, detail=f"source is not in UPLOADED status (status={row['status']})"
            )

        try:
            with tenant_scope() as conn:
                conn.execute(
                    text("INSERT INTO segmentation_jobs (org_id, source_id) VALUES (:org_id, :source_id)"),
                    {"org_id": body.org_id, "source_id": source_id},
                )
        except IntegrityError as e:
            # segmentation_jobs_source_id_uidx (V15) -- a re-call on a
            # source that already has a job (in any status, including a
            # prior terminal FAILED). Loud, typed 409, same
            # not-silently-duplicated discipline the old UNIQUE
            # (source_id, ordinal)-based 409 had. Reprocessing/retry-a-
            # failed-job semantics are a real open question, same one
            # V12's own comment already named -- not resolved here.
            raise HTTPException(status_code=409, detail="source already has a segmentation job") from e

        try:
            segment_source_task.delay(str(source_id), str(body.org_id))
        except Exception as e:
            # The job row already committed above -- if enqueueing fails
            # (broker unreachable/misconfigured), leaving it at QUEUED
            # forever would be exactly the "silently lost" failure mode
            # this whole design exists to prevent. Close it out loudly
            # instead: mark it FAILED with the enqueue error, then 503 so
            # the caller knows to retry the POST itself (a fresh INSERT
            # attempt), not poll a job that was never actually enqueued.
            with tenant_scope() as conn:
                conn.execute(
                    text(
                        "UPDATE segmentation_jobs SET status = 'FAILED', "
                        "last_error = :error, updated_at = now() WHERE source_id = :source_id"
                    ),
                    {"source_id": source_id, "error": f"failed to enqueue: {e!r}"[:2000]},
                )
            raise HTTPException(status_code=503, detail="segmentation queue unavailable") from e

        return SegmentSourceAcceptedResponse(source_id=source_id, status="QUEUED")
    finally:
        TenantContext.clear()


@router.get(
    "/api/v1/sources/{source_id}/segment",
    response_model=SegmentationJobStatusResponse,
    dependencies=[Depends(require_internal_service_token)],
)
def get_segmentation_status(source_id: UUID, org_id: UUID) -> SegmentationJobStatusResponse:
    TenantContext.set(org_id)
    try:
        with tenant_scope() as conn:
            row = conn.execute(
                text(
                    "SELECT status, attempt_count, segment_count, last_error, updated_at "
                    "FROM segmentation_jobs WHERE source_id = :source_id"
                ),
                {"source_id": source_id},
            ).mappings().first()

        if row is None:
            raise HTTPException(status_code=404, detail="no segmentation job for this source")

        status = row["status"]
        last_error = row["last_error"]
        if status == "PROCESSING" and (datetime.now(UTC) - row["updated_at"]) > STALE_PROCESSING_AFTER:
            # Staleness reconciliation (see this module's own constant
            # comment): the worker most likely died without ever getting a
            # chance to run its own except-block (SIGKILL/OOM/hard
            # time_limit -- see tasks/segmentation.py's module docstring on
            # why acks_late's redelivery doesn't, by itself, cap this).
            # Actively closes out the stuck state on read, not just reports
            # a synthetic status -- same "fix it, don't just describe it"
            # precedent as SourceUploadService's staleness handling.
            last_error = (
                "stale: exceeded staleness bound without completing (worker likely crashed or was killed)"
            )
            with tenant_scope() as conn:
                conn.execute(
                    text(
                        "UPDATE segmentation_jobs SET status = 'FAILED', last_error = :error, "
                        "updated_at = now() WHERE source_id = :source_id"
                    ),
                    {"source_id": source_id, "error": last_error},
                )
            status = "FAILED"

        return SegmentationJobStatusResponse(
            source_id=source_id,
            status=status,
            attempt_count=row["attempt_count"],
            segment_count=row["segment_count"],
            last_error=last_error,
        )
    finally:
        TenantContext.clear()
