CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS is Layer 3 (defense in depth, blueprint §10.9). The policy compares
-- the row's own id to the session-scoped app.org_id GUC set by
-- TenantConnectionPreparer at transaction start. current_setting(..., true)
-- returns NULL when the GUC is unset, and any comparison against NULL is
-- false — so a request that forgets to set tenant context sees zero rows
-- (fail closed), not every org's rows (fail open).
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

-- FORCE is required because Neon's connection role owns this table, and
-- table owners bypass RLS by default unless FORCE ROW LEVEL SECURITY is
-- set. Without this line the policy below would silently do nothing.
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;

CREATE POLICY organizations_tenant_isolation ON organizations
    USING (id = current_setting('app.org_id', true)::uuid)
    WITH CHECK (id = current_setting('app.org_id', true)::uuid);
