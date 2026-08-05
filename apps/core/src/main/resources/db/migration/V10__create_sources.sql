-- Phase 3 (§21/§11.1-11.2): the first new tenant-scoped table since
-- organizations. RLS is enabled from creation (CLAUDE.md's tenant-isolation
-- rule), and SourceRepository implements TenantScopedRepository from the
-- start rather than having it retrofitted -- see TenantIsolationArchitectureTest.
--
-- Deliberately no source_versions table yet (§11.3): this slice is
-- first-upload + dedup + commit-verification only, not re-upload/
-- versioning, so "v1" in storage_key is currently the only version that
-- will ever exist. Versioning is real future work, not forgotten.
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    uploaded_by UUID NOT NULL REFERENCES users (id),
    filename TEXT NOT NULL,
    byte_size BIGINT NOT NULL CHECK (byte_size > 0),
    sha256 TEXT NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    mime_type TEXT,
    storage_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'UPLOADED', 'REJECTED', 'CORRUPT')),
    rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    committed_at TIMESTAMPTZ
);

CREATE INDEX sources_org_id_idx ON sources (org_id);

-- Dedup guard (§11.2): at most one UPLOADED source per (org, sha256). A
-- PENDING intent that's abandoned (client never commits -- §11.7's orphan-
-- intent failure mode) must not block a retry with the same hash, so the
-- partial index only covers rows that actually finished.
CREATE UNIQUE INDEX sources_org_sha256_uploaded_uidx ON sources (org_id, sha256) WHERE status = 'UPLOADED';

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources FORCE ROW LEVEL SECURITY;

CREATE POLICY sources_tenant_isolation ON sources
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

GRANT SELECT, INSERT, UPDATE, DELETE ON sources TO obligo_app;
