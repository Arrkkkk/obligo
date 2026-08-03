-- Global identity table (§10.1: identity lives entirely in obligo-core).
-- Not tenant-scoped, no RLS: looking a user up by google_sub is exactly
-- the step that determines which org_id applies, so it can't itself be
-- gated by one. See V5/V6 for the same reasoning on org_members and
-- refresh_tokens.
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_sub TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

GRANT SELECT, INSERT ON users TO obligo_app;
