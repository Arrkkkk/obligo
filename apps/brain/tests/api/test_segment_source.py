"""Full end-to-end proof of the segmentation trigger + status endpoints
(blueprint §11, §21 Phase 3), no mocks -- mirrors SourceUploadFlowTest's
discipline on the Java side: real Neon Postgres, real Supabase Storage,
real HTTP request/response through the actual FastAPI routes.

**Split across what does and doesn't need a live Celery broker, on
purpose, not as a workaround.** POST's job is now: validate, INSERT a
segmentation_jobs row, call segment_source_task.delay(...). This file
proves the validate+INSERT+enqueue-attempt path for real (including the
real failure path when the broker is unavailable -- CELERY_BROKER_URL is
a separate, not-yet-always-configured credential, so "enqueue fails, job
is marked FAILED, caller gets 503" is itself real, asserted behavior here,
not a skip). test_segmentation_task.py (same directory... actually
tests/tasks/) covers the actual extraction+persistence logic by calling
segment_source_task directly -- a Celery-decorated function is still a
plain callable when invoked without .delay()/.apply_async(), which runs it
synchronously in-process with no broker involved at all, exercising the
exact same TenantContext/tenant_scope code a real worker executes. Only
the broker round-trip itself (a real .delay() -> real Redis -> a real,
separately-running worker process picking it up) needs the live broker --
proven separately in test_celery_broker_integration.py once
CELERY_BROKER_URL is configured, not folded into this file.
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

REQUIRED_ENV = (
    "DATABASE_URL",
    "BRAIN_DB_PASSWORD",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_STORAGE_BUCKET",
    "BRAIN_SERVICE_TOKEN",
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


def _internal_auth_headers() -> dict[str, str]:
    return {"X-Internal-Service-Token": os.environ["BRAIN_SERVICE_TOKEN"]}


@dataclass
class SeededSource:
    org_id: uuid.UUID
    source_id: uuid.UUID
    storage_key: str
    pdf_bytes: bytes


@pytest.fixture
def seeded_uploaded_source() -> Iterator[SeededSource]:
    pdf_bytes = (FIXTURE_DIR / FIXTURE_NAME).read_bytes()
    sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    org_id, user_id, source_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    storage_key = f"{org_id}/{source_id}/v1/{sha256}.pdf"

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            conn.execute(text("INSERT INTO organizations (id, name) VALUES (:id, 'Async Segmentation Test Org')"), {"id": org_id})
            conn.execute(
                text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
                {"id": user_id, "sub": f"async-segment-test-{user_id}", "email": f"{user_id}@example.test"},
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
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"schema not provisioned on this branch yet: {exc}")

    _put_object(storage_key, pdf_bytes)

    try:
        yield SeededSource(org_id=org_id, source_id=source_id, storage_key=storage_key, pdf_bytes=pdf_bytes)
    finally:
        _delete_object(storage_key)
        with owner_engine.begin() as conn:
            conn.execute(text("DELETE FROM segments WHERE source_id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM segmentation_jobs WHERE source_id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def _job_row(source_id: uuid.UUID) -> dict | None:
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
            return dict(row) if row else None
    finally:
        owner_engine.dispose()


def test_post_segment_creates_a_queued_job_row_and_returns_202(seeded_uploaded_source: SeededSource) -> None:
    """Proves the new contract: POST no longer returns segments -- it
    returns 202 + {source_id, status} and a real, RLS-scoped
    segmentation_jobs row exists. Whether the broker enqueue itself
    succeeds is intentionally not asserted here (see
    test_post_segment_marks_the_job_failed_when_the_broker_is_unavailable
    for the specific, real behavior when it doesn't) -- this test only
    proves the INSERT half, which happens unconditionally before any
    enqueue attempt.
    """
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    response = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )

    row = _job_row(fixture.source_id)
    assert row is not None, "expected a segmentation_jobs row to exist regardless of enqueue outcome"

    if response.status_code == 202:
        assert response.json() == {"source_id": str(fixture.source_id), "status": "QUEUED"}
        assert row["status"] == "QUEUED"
    else:
        # No CELERY_BROKER_URL configured in this environment -- see the
        # dedicated test below for the precise, asserted shape of this path.
        assert response.status_code == 503


def test_post_segment_marks_the_job_failed_when_the_broker_is_unavailable(
    seeded_uploaded_source: SeededSource,
) -> None:
    """Real, asserted behavior for a real failure mode -- not a skip.
    Without CELERY_BROKER_URL configured (the common case until the
    Upstash Redis TCP credential is wired in), segment_source_task.delay()
    genuinely raises when it tries to connect. Proves the specific
    mitigation this checkpoint's design calls for: the already-inserted
    QUEUED row does not get silently abandoned -- it's actively flipped to
    FAILED with the enqueue error, and the caller gets 503, not a
    misleading 202.
    """
    if os.environ.get("CELERY_BROKER_URL"):
        pytest.skip("CELERY_BROKER_URL is configured -- this test proves the no-broker failure path specifically")

    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    response = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )

    assert response.status_code == 503, response.text

    row = _job_row(fixture.source_id)
    assert row is not None
    assert row["status"] == "FAILED"
    assert row["last_error"] is not None and "enqueue" in row["last_error"]


def test_post_segment_rejects_a_second_job_for_the_same_source(seeded_uploaded_source: SeededSource) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    first = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert first.status_code in (202, 503), first.text  # job row exists either way

    second = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert second.status_code == 409, second.text


def test_get_segment_status_returns_404_when_no_job_exists(seeded_uploaded_source: SeededSource) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    response = client.get(
        f"/api/v1/sources/{fixture.source_id}/segment",
        params={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert response.status_code == 404, response.text


def test_get_segment_status_reflects_a_real_job_row(seeded_uploaded_source: SeededSource) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    post_response = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert post_response.status_code in (202, 503)

    get_response = client.get(
        f"/api/v1/sources/{fixture.source_id}/segment",
        params={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert get_response.status_code == 200, get_response.text
    body = get_response.json()
    assert body["source_id"] == str(fixture.source_id)
    assert body["status"] in ("QUEUED", "FAILED")


def test_get_segment_status_reconciles_a_stale_processing_job(seeded_uploaded_source: SeededSource) -> None:
    """Directly seeds a PROCESSING job with an old updated_at (simulating a
    worker that died mid-task, past api/v1/sources.py's
    STALE_PROCESSING_AFTER bound) and proves GET actively closes it out to
    FAILED on read, rather than reporting PROCESSING forever.
    """
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO segmentation_jobs (org_id, source_id, status, updated_at) "
                    "VALUES (:org_id, :source_id, 'PROCESSING', now() - interval '20 minutes')"
                ),
                {"org_id": fixture.org_id, "source_id": fixture.source_id},
            )
    finally:
        owner_engine.dispose()

    client = TestClient(app)
    response = client.get(
        f"/api/v1/sources/{fixture.source_id}/segment",
        params={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "FAILED"
    assert "stale" in body["last_error"]

    # And the write actually landed -- not just a synthetic response value.
    row = _job_row(fixture.source_id)
    assert row["status"] == "FAILED"


def test_segment_endpoints_reject_requests_without_a_valid_internal_service_token(
    seeded_uploaded_source: SeededSource,
) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    missing = client.post(f"/api/v1/sources/{fixture.source_id}/segment", json={"org_id": str(fixture.org_id)})
    assert missing.status_code == 422, missing.text  # FastAPI's own missing-required-header response

    wrong = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers={"X-Internal-Service-Token": "not-the-real-token"},
    )
    assert wrong.status_code == 401, wrong.text

    wrong_get = client.get(
        f"/api/v1/sources/{fixture.source_id}/segment",
        params={"org_id": str(fixture.org_id)},
        headers={"X-Internal-Service-Token": "not-the-real-token"},
    )
    assert wrong_get.status_code == 401, wrong_get.text
