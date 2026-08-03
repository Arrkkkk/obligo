-- Identity-plane table, no RLS — same reasoning as users/org_members/
-- refresh_tokens (V4-V6): the preview endpoint is looked up by token hash,
-- unauthenticated, with no TenantContext at all, so RLS keyed on org_id
-- would simply block it regardless of policy.
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    invited_by UUID NOT NULL REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);

CREATE INDEX invitations_org_id_idx ON invitations (org_id);
CREATE INDEX invitations_email_idx ON invitations (email);

GRANT SELECT, INSERT, UPDATE, DELETE ON invitations TO obligo_app;
