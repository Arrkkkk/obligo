-- Phase 3 (§21/§11): the first table apps/brain writes to. RLS enabled
-- from creation, same discipline as sources (V10) -- see CLAUDE.md's
-- tenant-isolation rule ("every tenant-scoped table has org_id and an RLS
-- policy from the moment it's created -- not retrofitted later").
--
-- Column set is deliberately minimal: this migration exists to prove the
-- tenant-isolation mechanism from the Python side (org_id for RLS,
-- source_id to anchor a segment to its document, text/char_start/char_end
-- as placeholder offset columns), not to model the final segment shape.
-- The real columns (page, layout metadata, confidence, etc. -- see
-- blueprint §11's acceptance criterion that offsets round-trip exactly to
-- the source text) arrive with the actual PyMuPDF/PaddleOCR segmentation
-- logic in a later slice.
CREATE TABLE segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    source_id UUID NOT NULL REFERENCES sources (id),
    text TEXT NOT NULL,
    char_start INT NOT NULL CHECK (char_start >= 0),
    char_end INT NOT NULL CHECK (char_end >= char_start),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX segments_org_id_idx ON segments (org_id);
CREATE INDEX segments_source_id_idx ON segments (source_id);

ALTER TABLE segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE segments FORCE ROW LEVEL SECURITY;

CREATE POLICY segments_tenant_isolation ON segments
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

-- obligo_brain (V11) is the only role that writes segments right now --
-- the Python segmentation pipeline. Deliberately no DELETE grant: nothing
-- in this phase needs to delete a segment (reprocessing semantics aren't
-- decided yet -- likely supersession, not hard delete, matching the
-- pattern used for obligation events elsewhere in the blueprint), so it
-- isn't granted reflexively. Add it when a real use case needs it.
--
-- obligo_app gets no grant here yet either: apps/core has no endpoint that
-- reads segments today. Add its (SELECT-only -- core never writes
-- segments) grant in a later migration when that endpoint exists, rather
-- than granting unused privilege now.
GRANT SELECT, INSERT, UPDATE ON segments TO obligo_brain;

-- apps/brain will need to read source metadata (storage_key, org_id) to
-- fetch the file bytes it segments. Not exercised by this checkpoint's
-- isolation test (which only proves the mechanism against segments), but
-- part of the role's steady-state minimal scope rather than something to
-- bolt on ad hoc in a follow-up migration.
GRANT SELECT ON sources TO obligo_brain;
