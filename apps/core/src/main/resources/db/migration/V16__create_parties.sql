-- Phase 4 (§21/§6.2 type rule 3, §8.2): the first "obligation graph" table.
-- Party-alias symbol resolution (blueprint's own Phase 4 typechecker
-- deliverable) has nothing to resolve against without it -- found missing
-- during the typecheck.py checkpoint's own tenant-isolation audit (checked
-- V1-V15 directly; blueprint §8.2 names this table but it was never
-- migrated). Built now because it's a hard prerequisite of a Phase 4
-- deliverable, not a Phase 5 pull-forward -- Phase 5's own exclusion
-- (packages/ir-spec/SPEC.md section 11) is specifically the `obligations`
-- table's lifecycle columns, not this table.
--
-- Column set matches §8.2's table inventory entry exactly: PK id; U
-- (org_id, lower(canonical_name)); IX GIN(aliases); kind, external_ids
-- jsonb, merged_into -> self (merge is soft, auditable, reversible).
--
-- `kind` is deliberately left as free TEXT with no CHECK enum: unlike the
-- action taxonomy (grammar/obligation.lark's own header), there's no real
-- corpus of extracted party-kind values yet to derive a closed set from,
-- and inventing one now would be exactly the "on vibes" taxonomy-building
-- this project has repeatedly declined to do elsewhere. Revisit once real
-- extraction data exists.
CREATE TABLE parties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    canonical_name TEXT NOT NULL,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    kind TEXT,
    external_ids JSONB NOT NULL DEFAULT '{}'::jsonb,
    merged_into UUID REFERENCES parties (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX parties_org_id_idx ON parties (org_id);

-- §8.2's own unique key: one canonical name per org, case-insensitive.
CREATE UNIQUE INDEX parties_org_canonical_name_uidx ON parties (org_id, lower(canonical_name));

-- §8.3's own named index: alias resolution during normalisation (and now,
-- during typecheck.py's party-alias resolution) needs `alias = ANY(aliases)`
-- to be indexed, not a sequential scan per lookup.
CREATE INDEX parties_aliases_gin_idx ON parties USING gin (aliases);

ALTER TABLE parties ENABLE ROW LEVEL SECURITY;
ALTER TABLE parties FORCE ROW LEVEL SECURITY;

CREATE POLICY parties_tenant_isolation ON parties
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

-- obligo_brain (V11) only ever resolves an alias against an existing party
-- during typecheck -- it does not create, merge, or edit parties. That's a
-- human-facing review-queue/party-management concern (Phase 5's domain
-- layer, per blueprint), so obligo_brain gets SELECT only, same
-- minimal-grant discipline as V12's comment on segments.
GRANT SELECT ON parties TO obligo_brain;

-- No grant to obligo_app yet: apps/core has no party-management endpoint
-- today. Add its grant in a later migration when that endpoint exists,
-- rather than granting unused privilege now (same reasoning as V12's
-- deferred obligo_app grant on segments).
