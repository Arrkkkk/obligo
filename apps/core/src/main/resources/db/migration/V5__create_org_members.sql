-- No RBAC matrix yet (§10.7 deferred) — role exists as a column so the
-- access-token claim shape is stable, but every membership created in this
-- phase is 'OWNER' (the auto-created-personal-org case, §10.8).
--
-- No RLS here either, same reasoning as users: "which org(s) is this user
-- a member of" is a cross-tenant-by-definition lookup used to bootstrap
-- TenantContext during login/refresh, not a query that runs inside an
-- already-scoped request.
CREATE TABLE org_members (
    org_id UUID NOT NULL REFERENCES organizations (id),
    user_id UUID NOT NULL REFERENCES users (id),
    role TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (org_id, user_id)
);

CREATE INDEX org_members_user_id_idx ON org_members (user_id);

GRANT SELECT, INSERT ON org_members TO obligo_app;
