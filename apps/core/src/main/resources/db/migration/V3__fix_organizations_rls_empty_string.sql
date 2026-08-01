-- Once a custom GUC like app.org_id has been touched by SET LOCAL on a
-- connection, current_setting(..., true) reverts to '' (empty string)
-- outside that transaction — not NULL — because Postgres only treats a
-- placeholder GUC as fully "unset" before it has ever been referenced in
-- the session. On a pooled connection reused across requests, a later
-- request with no tenant context would otherwise hit ''::uuid and error
-- instead of seeing zero rows. NULLIF folds '' back to NULL so both cases
-- behave identically (fail closed, not an error).
DROP POLICY organizations_tenant_isolation ON organizations;

CREATE POLICY organizations_tenant_isolation ON organizations
    USING (id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (id = NULLIF(current_setting('app.org_id', true), '')::uuid);
