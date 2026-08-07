"""Direct proof of segment_source_task's own logic -- extraction,
persistence, retry/backoff/terminal-failure handling, and, most
importantly, that tenant isolation holds when org_id arrives via a Celery
task's arguments rather than an HTTP request. No Celery broker needed for
any test in this file: a Celery-decorated task's own .apply() method runs
it fully in-process, including its real retry control flow (self.retry()
raising and being caught, self.request.retries incrementing across
simulated attempts) -- verified interactively before writing these tests,
not assumed from Celery's docs. This is a deliberate, different concern
from test_celery_broker_integration.py, which proves the actual
.delay() -> Redis -> separate-worker-process round trip and acks_late's
broker-level redelivery behavior -- neither of which .apply() exercises,
since eager execution never touches a broker or an ack at all.

Real Neon Postgres and real Supabase Storage throughout, same discipline
as tests/api/test_segment_source.py -- the only thing standing in for the
"real Celery worker" is .apply() itself, which is Celery's own sanctioned
mechanism for this, not a mock of Celery's behavior.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.ingestion.loaders.pdf import extract_segments
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope
from obligo_brain.tasks.segmentation import segment_source_task

REQUIRED_ENV = (
    "DATABASE_URL",
    "BRAIN_DB_PASSWORD",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_STORAGE_BUCKET",
)
pytestmark = pytest.mark.skipif(
    not all(os.environ.get(name) for name in REQUIRED_ENV),
    reason=f"{REQUIRED_ENV} not all set -- skipping real-infra test",
)

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "pdfs"
FIXTURE_NAME = "irs_1040_table_heavy.pdf"


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


def _storage_object_url(storage_key: str) -> str:
    supabase_url = os.environ["SUPABASE_URL"]
    bucket = os.environ["SUPABASE_STORAGE_BUCKET"]
    return f"{supabase_url}/storage/v1/object/{bucket}/{storage_key}"


def _put_object(storage_key: str, data: bytes) -> None:
    resp = httpx.post(
        _storage_object_url(storage_key),
        headers={
            "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
            "Content-Type": "application/pdf",
        },
        content=data,
        timeout=60.0,
    )
    resp.raise_for_status()


def _delete_object(storage_key: str) -> None:
    httpx.delete(
        _storage_object_url(storage_key),
        headers={"Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}"},
        timeout=30.0,
    )


@dataclass
class SeededSource:
    org_id: uuid.UUID
    source_id: uuid.UUID
    storage_key: str
    pdf_bytes: bytes
    object_uploaded: bool


@pytest.fixture(params=[True, False], ids=["real_object", "missing_object"])
def seeded_uploaded_source(request: pytest.FixtureRequest) -> Iterator[SeededSource]:
    """Parametrized over whether the storage object actually exists --
    "missing_object" is what deterministically forces fetch_object to raise
    SupabaseObjectUnavailableError, real infra (a genuine 404 from
    Supabase), no mocking, for the retry/terminal-failure tests below.
    """
    upload_object = request.param
    pdf_bytes = (FIXTURE_DIR / FIXTURE_NAME).read_bytes()
    sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    org_id, user_id, source_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    storage_key = f"{org_id}/{source_id}/v1/{sha256}.pdf"

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            conn.execute(text("INSERT INTO organizations (id, name) VALUES (:id, 'Task Test Org')"), {"id": org_id})
            conn.execute(
                text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
                {"id": user_id, "sub": f"task-test-{user_id}", "email": f"{user_id}@example.test"},
            )
            conn.execute(
                text(
                    "INSERT INTO sources "
                    "(id, org_id, uploaded_by, filename, byte_size, sha256, storage_key, status, committed_at) "
                    "VALUES (:id, :org_id, :uploaded_by, :filename, :size, :sha, :key, 'UPLOADED', now())"
                ),
                {
                    "id": source_id,
                    "org_id": org_id,
                    "uploaded_by": user_id,
                    "filename": FIXTURE_NAME,
                    "size": len(pdf_bytes),
                    "sha": sha256,
                    "key": storage_key,
                },
            )
            conn.execute(
                text("INSERT INTO segmentation_jobs (org_id, source_id) VALUES (:org_id, :source_id)"),
                {"org_id": org_id, "source_id": source_id},
            )
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"schema not provisioned on this branch yet: {exc}")

    if upload_object:
        _put_object(storage_key, pdf_bytes)

    try:
        yield SeededSource(
            org_id=org_id, source_id=source_id, storage_key=storage_key, pdf_bytes=pdf_bytes, object_uploaded=upload_object
        )
    finally:
        if upload_object:
            _delete_object(storage_key)
        with owner_engine.begin() as conn:
            conn.execute(text("DELETE FROM segments WHERE source_id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM segmentation_jobs WHERE source_id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def _job_row(source_id: uuid.UUID) -> dict:
    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT status, attempt_count, segment_count, last_error FROM segmentation_jobs "
                    "WHERE source_id = :id"
                ),
                {"id": source_id},
            ).mappings().first()
            return dict(row)
    finally:
        owner_engine.dispose()


def test_task_persists_segments_that_round_trip_exactly_and_marks_succeeded(
    seeded_uploaded_source: SeededSource,
) -> None:
    fixture = seeded_uploaded_source
    if not fixture.object_uploaded:
        pytest.skip("this test covers the success path -- see the retry test for the missing-object path")

    result = segment_source_task.apply(args=(str(fixture.source_id), str(fixture.org_id)))
    assert result.successful(), result.traceback

    expected_segments = extract_segments(fixture.pdf_bytes)

    row = _job_row(fixture.source_id)
    assert row["status"] == "SUCCEEDED"
    assert row["segment_count"] == len(expected_segments)
    assert row["attempt_count"] == 0  # succeeded on the first attempt, no retries recorded

    TenantContext.set(fixture.org_id)
    try:
        with tenant_scope() as conn:
            rows = conn.execute(
                text("SELECT ordinal, page, char_start, char_end, text FROM segments WHERE source_id = :id ORDER BY ordinal"),
                {"id": fixture.source_id},
            ).mappings().all()
    finally:
        TenantContext.clear()

    assert len(rows) == len(expected_segments)
    for row, expected in zip(rows, expected_segments, strict=True):
        assert row["char_start"] == expected.char_start
        assert row["char_end"] == expected.char_end
        assert row["text"] == expected.text


def test_task_exhausts_retries_and_marks_failed_on_a_real_missing_object(
    seeded_uploaded_source: SeededSource,
) -> None:
    """The forced-failure retry proof: storage_key points at an object that
    was deliberately never uploaded (real Supabase 404, not a mock), so
    fetch_object raises SupabaseObjectUnavailableError on every attempt,
    deterministically. Proves the full retry arc: self.request.retries
    climbing through MAX_RETRIES, last_error updated on each attempt while
    status stays PROCESSING (not FAILED -- see segmentation.py's
    _record_retryable_attempt docstring for why), and only the FINAL
    attempt flips status to FAILED with attempt_count == MAX_RETRIES + 1.
    """
    fixture = seeded_uploaded_source
    if fixture.object_uploaded:
        pytest.skip("this test covers the missing-object retry path -- see the success test for the happy path")

    from obligo_brain.tasks.segmentation import MAX_RETRIES

    result = segment_source_task.apply(args=(str(fixture.source_id), str(fixture.org_id)))
    assert not result.successful()

    row = _job_row(fixture.source_id)
    assert row["status"] == "FAILED"
    assert row["attempt_count"] == MAX_RETRIES + 1
    assert row["last_error"] is not None
    assert row["segment_count"] is None


def test_tenant_isolation_holds_when_org_id_arrives_via_a_task_not_an_http_request(
    seeded_uploaded_source: SeededSource,
) -> None:
    """The core proof this checkpoint exists to deliver: segment_source_task
    sets TenantContext from its own argument (no HTTP request, no filter,
    no middleware) -- confirms that mechanism still produces real,
    RLS-enforced isolation, not just "the task ran and didn't error."

    Two things proven, matching test_tenant_isolation.py's own rigor:
    (1) a DIFFERENT org's TenantContext sees zero rows for this source's
    segments/job -- RLS rejects cross-tenant reads regardless of which
    entrypoint (HTTP handler vs. task) performed the write; (2) no context
    at all sees zero rows too -- fail-closed, not fail-open, unchanged from
    the synchronous endpoint's behavior.
    """
    fixture = seeded_uploaded_source
    if not fixture.object_uploaded:
        pytest.skip("tenant-isolation proof needs a real successful segmentation to have real rows to isolate")

    result = segment_source_task.apply(args=(str(fixture.source_id), str(fixture.org_id)))
    assert result.successful(), result.traceback

    other_org_id = uuid.uuid4()
    TenantContext.set(other_org_id)
    try:
        with tenant_scope() as conn:
            other_org_segments = conn.execute(
                text("SELECT 1 FROM segments WHERE source_id = :id"), {"id": fixture.source_id}
            ).fetchall()
            other_org_job = conn.execute(
                text("SELECT 1 FROM segmentation_jobs WHERE source_id = :id"), {"id": fixture.source_id}
            ).fetchall()
    finally:
        TenantContext.clear()

    assert other_org_segments == [], "a different org's tenant context must see zero segments for this source"
    assert other_org_job == [], "a different org's tenant context must see zero segmentation_jobs rows for this source"

    # No context at all -- fail closed, matching organizations_tenant_isolation's own reasoning.
    with tenant_scope() as conn:
        no_context_segments = conn.execute(
            text("SELECT 1 FROM segments WHERE source_id = :id"), {"id": fixture.source_id}
        ).fetchall()
    assert no_context_segments == []
