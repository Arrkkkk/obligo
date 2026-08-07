"""Segmentation endpoint (blueprint §11, §21 Phase 3): given an already-
committed source, extract segments (PyMuPDF text-layer per page, or
Tesseract OCR per page for scanned pages -- see
obligo_brain.ingestion.loaders.pdf's per-page routing) and persist them.

**Known, deliberate gap -- not silently assumed solved:** this endpoint
takes `org_id` as a plain request-body field, trusted from the caller.
`require_internal_service_token` (below) gates the endpoint on a shared
secret, but that only proves the caller reached this endpoint through a
channel that knows `BRAIN_SERVICE_TOKEN` -- it does not prove `org_id`
itself is a legitimate claim. See `platform/security/internal_auth.py`'s
docstring for the full distinction, and CLAUDE.md's debt list for why the
real fix (a short-lived, per-request token apps/core mints after its own
JWT verification, which apps/brain would verify cryptographically instead
of trusting the body) is still genuinely missing, not just "TBD."

TenantContext.set(org_id) here stands in for the tenant-derivation
middleware that real fix would provide, exactly the same stand-in role it
plays in test_tenant_isolation.py -- this endpoint IS the first real
(non-test) caller of that mechanism.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from obligo_brain.ingestion.loaders.pdf import PdfExtractionError, extract_segments
from obligo_brain.platform.security.internal_auth import require_internal_service_token
from obligo_brain.platform.storage.supabase import SupabaseObjectUnavailableError, fetch_object
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope

router = APIRouter()


class SegmentSourceRequest(BaseModel):
    org_id: UUID


class SegmentSourceResponse(BaseModel):
    source_id: UUID
    segment_count: int


@router.post(
    "/api/v1/sources/{source_id}/segment",
    response_model=SegmentSourceResponse,
    dependencies=[Depends(require_internal_service_token)],
)
def segment_source(source_id: UUID, body: SegmentSourceRequest) -> SegmentSourceResponse:
    TenantContext.set(body.org_id)
    try:
        with tenant_scope() as conn:
            row = conn.execute(
                text("SELECT storage_key, status FROM sources WHERE id = :id"), {"id": source_id}
            ).mappings().first()

        if row is None:
            # RLS-scoped: this is indistinguishable from "exists but belongs
            # to another org" by design -- fail closed, no cross-tenant
            # existence leak via a 404-vs-403 distinction.
            raise HTTPException(status_code=404, detail="source not found")

        if row["status"] != "UPLOADED":
            raise HTTPException(
                status_code=409, detail=f"source is not in UPLOADED status (status={row['status']})"
            )

        try:
            pdf_bytes = fetch_object(row["storage_key"])
        except SupabaseObjectUnavailableError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

        try:
            segments = extract_segments(pdf_bytes)
        except PdfExtractionError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

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
                            "org_id": body.org_id,
                            "source_id": source_id,
                            "ordinal": segment.ordinal,
                            "page": segment.page,
                            "char_start": segment.char_start,
                            "char_end": segment.char_end,
                            "text": segment.text,
                            "ocr_confidence": segment.ocr_confidence,
                        },
                    )
        except IntegrityError as e:
            # Most likely a re-call on an already-segmented source (UNIQUE
            # (source_id, ordinal), V13) -- reprocessing/supersession
            # semantics aren't decided yet (same open question V12's
            # comment already named), so this is a loud, typed failure on
            # retry, not idempotent re-verification and not silent
            # duplication either.
            raise HTTPException(status_code=409, detail="source already has segments") from e

        return SegmentSourceResponse(source_id=source_id, segment_count=len(segments))
    finally:
        TenantContext.clear()
