-- Phase 3 (§21/§11): async segmentation checkpoint. Segmentation moves from
-- a synchronous FastAPI request to a Celery task (OCR is genuinely slow --
-- see CLAUDE.md's OCR-checkpoint notes on Tesseract latency); this table is
-- the durable job-state record that survives worker crashes/restarts,
-- matching blueprint's own already-quoted design intent ("durability
-- handled via Postgres job-state reconciliation, not a second broker" --
-- CLAUDE.md's RabbitMQ-deferred note).
--
-- Deliberately NOT modeled by extending sources.status (currently
-- PENDING/UPLOADED/REJECTED/CORRUPT, a Java-owned enum + CHECK constraint,
-- V10). sources.status represents the *upload* lifecycle (has the file
-- itself been received and verified); segmentation is a separate lifecycle
-- layered on top of an already-UPLOADED source. Conflating them would mean
-- every future segmentation-state addition requires touching apps/core's
-- SourceStatus enum for a concern apps/brain actually owns end to end.
CREATE TABLE segmentation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    source_id UUID NOT NULL REFERENCES sources (id),
    status TEXT NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED', 'PROCESSING', 'SUCCEEDED', 'FAILED')),
    attempt_count INT NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_error TEXT,
    segment_count INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One job per source at a time -- a second segment request on a source
-- that already has a job is a re-call, handled the same "loud, typed 409,
-- not silent duplication" way the old synchronous endpoint already handled
-- re-segmentation via UNIQUE (source_id, ordinal) on segments. Reprocessing
-- semantics are still the same open question V12's own comment named --
-- this constraint doesn't resolve that, it just keeps this table's shape
-- honest about "at most one job record per source" until it is resolved.
CREATE UNIQUE INDEX segmentation_jobs_source_id_uidx ON segmentation_jobs (source_id);

CREATE INDEX segmentation_jobs_org_id_idx ON segmentation_jobs (org_id);

-- Staleness reconciliation index (mirrors SourceUploadService's
-- MAX_PENDING_AGE pattern for abandoned upload intents): a job stuck at
-- PROCESSING past some bound is swept and marked FAILED rather than
-- trusted to eventually resolve on its own. Partial index since only
-- PROCESSING rows are ever scanned this way.
CREATE INDEX segmentation_jobs_processing_updated_at_idx ON segmentation_jobs (updated_at) WHERE status = 'PROCESSING';

ALTER TABLE segmentation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE segmentation_jobs FORCE ROW LEVEL SECURITY;

CREATE POLICY segmentation_jobs_tenant_isolation ON segmentation_jobs
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

-- obligo_brain both enqueues (INSERT, from the FastAPI request) and
-- executes (UPDATE, from the Celery task) job rows -- same role as
-- segments, no DELETE for the same "reprocessing semantics undecided"
-- reason.
GRANT SELECT, INSERT, UPDATE ON segmentation_jobs TO obligo_brain;

-- obligo_app deliberately gets NO grant here. apps/core learns job status
-- through a new brain-side HTTP status-check endpoint (gated by the same
-- BRAIN_SERVICE_TOKEN channel as /segment itself), not a direct DB read --
-- preserves the existing boundary where apps/core has zero grants on any
-- brain-owned table (V12's own comment: "apps/core has no endpoint that
-- reads segments today"). Add a grant here instead of the HTTP endpoint
-- only if that boundary is deliberately revisited later, not as a
-- convenience shortcut.
