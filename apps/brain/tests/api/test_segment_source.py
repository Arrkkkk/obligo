"""Full end-to-end proof of the segmentation endpoint (blueprint §11, §21
Phase 3), no mocks -- mirrors SourceUploadFlowTest's discipline on the Java
side: real Neon Postgres, real Supabase Storage, real PyMuPDF extraction,
real HTTP request/response through the actual FastAPI route.

test_pdf_round_trip.py already proves offset correctness against the pure
extraction function; this file proves the same property survives the full
path -- storage fetch, DB insert, DB read-back -- not just the in-memory
return value.

Storage objects are written directly via Supabase's authenticated-upload
endpoint (service-role bearer, bypassing the presigned-URL flow) rather
than through Spring's real upload-intent/commit endpoints: that flow is
already proven end-to-end by SourceUploadFlowTest, and re-driving it here
would just be slower test setup for the same guarantee. What's under test
here is what happens *after* a source is already UPLOADED.
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
FIXTURE_NAMES = [
    "attention_is_all_you_need.pdf",
    "bert_two_column.pdf",
    "irs_1040_table_heavy.pdf",
    "public_domain_chart.pdf",
]


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


@pytest.fixture(params=FIXTURE_NAMES)
def seeded_uploaded_source(request: pytest.FixtureRequest) -> Iterator[SeededSource]:
    fixture_name: str = request.param
    pdf_bytes = (FIXTURE_DIR / fixture_name).read_bytes()
    sha256 = hashlib.sha256(pdf_bytes).hexdigest()

    org_id, user_id, source_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    storage_key = f"{org_id}/{source_id}/v1/{sha256}.pdf"

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            conn.execute(text("INSERT INTO organizations (id, name) VALUES (:id, 'Segmentation Test Org')"), {"id": org_id})
            conn.execute(
                text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
                {"id": user_id, "sub": f"segment-test-{user_id}", "email": f"{user_id}@example.test"},
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
                    "filename": fixture_name,
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
            conn.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def test_segment_source_persists_segments_that_round_trip_exactly(seeded_uploaded_source: SeededSource) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    response = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert response.status_code == 200, response.text
    body = response.json()

    expected_segments = extract_segments(fixture.pdf_bytes)
    assert body["segment_count"] == len(expected_segments)

    TenantContext.set(fixture.org_id)
    try:
        with tenant_scope() as conn:
            rows = conn.execute(
                text(
                    "SELECT ordinal, page, char_start, char_end, text FROM segments "
                    "WHERE source_id = :id ORDER BY ordinal"
                ),
                {"id": fixture.source_id},
            ).mappings().all()
    finally:
        TenantContext.clear()

    assert len(rows) == len(expected_segments)

    # Full DB round trip: what got persisted must exactly match a fresh,
    # independent re-extraction of the original bytes -- not just "some N
    # rows got written," but the exact (page, char_start, char_end, text)
    # for every one of them, in order.
    for row, expected in zip(rows, expected_segments, strict=True):
        assert row["ordinal"] == expected.ordinal
        assert row["page"] == expected.page
        assert row["char_start"] == expected.char_start
        assert row["char_end"] == expected.char_end
        assert row["text"] == expected.text

    # And the defining offset property, recomputed from the persisted rows
    # alone (no dependency on extract_segments' internals): grouping by
    # page and reconstructing each page's canonical text must place every
    # segment's text at exactly its own recorded (char_start, char_end).
    from collections import defaultdict

    by_page: dict[int, list] = defaultdict(list)
    for row in rows:
        by_page[row["page"]].append(row)
    for page_rows in by_page.values():
        running = ""
        for row in page_rows:
            if running:
                running += "\n"
            assert len(running) == row["char_start"]
            running += row["text"]
            assert len(running) == row["char_end"]
            assert running[row["char_start"] : row["char_end"]] == row["text"]


def test_segmenting_an_already_segmented_source_fails_loudly_not_silently(
    seeded_uploaded_source: SeededSource,
) -> None:
    from fastapi.testclient import TestClient

    from obligo_brain.main import app

    fixture = seeded_uploaded_source
    client = TestClient(app)

    first = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert first.status_code == 200, first.text

    second = client.post(
        f"/api/v1/sources/{fixture.source_id}/segment",
        json={"org_id": str(fixture.org_id)},
        headers=_internal_auth_headers(),
    )
    assert second.status_code == 409, second.text


def test_segment_source_rejects_requests_without_a_valid_internal_service_token(
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
