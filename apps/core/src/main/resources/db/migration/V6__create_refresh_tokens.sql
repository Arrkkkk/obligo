-- Opaque refresh tokens, stored hashed (§10.5) — high-entropy random
-- values, so SHA-256 is sufficient; a slow KDF here would be cargo-culting.
-- User-scoped, not org-scoped: a session can outlive an org switch
-- (§10.4 — switching orgs mints a new access token from the same
-- refresh token), so this is identity-plane, no RLS, same as users.
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users (id),
    token_hash TEXT NOT NULL UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    used_at TIMESTAMPTZ,
    replaced_by UUID,
    revoked_at TIMESTAMPTZ,
    user_agent TEXT,
    ip TEXT
);

CREATE INDEX refresh_tokens_family_id_idx ON refresh_tokens (family_id);
CREATE INDEX refresh_tokens_user_id_idx ON refresh_tokens (user_id);

GRANT SELECT, INSERT, UPDATE ON refresh_tokens TO obligo_app;

-- Minimal stand-in for the real audit log (§11's crypto-shredding-aware
-- design is out of scope here) — just enough to make SECURITY_TOKEN_REUSE
-- DB-observable and testable, per §10.5.
CREATE TABLE security_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users (id),
    family_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

GRANT SELECT, INSERT ON security_audit_events TO obligo_app;
