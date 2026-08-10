-- Phase 4 (§21, §6.9, §13.1 rule 5): CLAUDE.md's non-negotiable rule
-- "every LLM call records model_id, prompt_version, cost, and latency"
-- has no table to write to -- checked V1-V16 directly, agent_runs (named
-- in §8.2's own "Platform" table inventory row) was never migrated. Built
-- now, at the Extractor -> Span Grounder checkpoint, because this is the
-- first LLM call this codebase ever makes: CLAUDE.md's debt list is
-- already three entries deep in "called non-negotiable, never built"
-- (Idempotency-Key/X-Request-Id, the full cross-tenant leakage suite,
-- apps/brain's lint/type-check CI gate) -- the first real LLM call is
-- exactly the wrong moment to add a fourth, so this migration ships
-- alongside the checkpoint that needs it rather than being deferred
-- again.
--
-- Column set covers exactly what this checkpoint's one caller
-- (apps/brain/src/obligo_brain/graphs/extraction.py's run_extraction())
-- writes, plus the fields §6.9/§13.1/§13.5 name as required on every LLM
-- call (model_id, prompt_id/version/hash, tokens, latency, cost) and the
-- node_trace concept §6.8 says the UI's agent-run view maps 1:1 to.
-- input_hash is recorded now even though response caching (§6.10's
-- content-hash cache) isn't built yet -- it's the same cache-key
-- component (sha256(segment_id, prompt_hash, model_id)) that future
-- checkpoint will need, and adding the column later would mean backfilling
-- history that can never be reconstructed once these calls have happened.
--
-- cost_usd is nullable: computing it needs a real per-model pricing
-- table, which is model-router/budget-enforcement scope (§6.10), not
-- built at this checkpoint. Recording input_tokens/output_tokens (what
-- cost_usd would be derived from) is what this checkpoint's caller
-- actually does.
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    node TEXT NOT NULL,                    -- e.g. 'extractor' -- which pipeline stage made this call
    provider TEXT NOT NULL,                -- e.g. 'groq'
    model_id TEXT NOT NULL,
    prompt_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,             -- sha256 of the raw, unrendered prompt template
    input_hash TEXT NOT NULL,              -- sha256(segment_id, prompt_hash, model_id) -- future cache key
    segment_id UUID NOT NULL REFERENCES segments (id),
    input_tokens INT,
    output_tokens INT,
    cost_usd NUMERIC(10, 6),
    latency_ms INT,
    status TEXT NOT NULL CHECK (status IN ('ok', 'error')),
    error_detail TEXT,
    node_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX agent_runs_org_id_created_at_idx ON agent_runs (org_id, created_at DESC);
CREATE INDEX agent_runs_segment_id_idx ON agent_runs (segment_id);

ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs FORCE ROW LEVEL SECURITY;

CREATE POLICY agent_runs_tenant_isolation ON agent_runs
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

-- obligo_brain (V11) is the only writer -- it's the only process making
-- LLM calls today. INSERT only, no SELECT/UPDATE: nothing in this
-- checkpoint reads agent_runs back (the eval harness and any future
-- agent-run UI are separate, not-yet-built consumers), same
-- minimal-grant-until-a-real-caller-exists discipline as V12/V16's
-- deferred obligo_app grants. No DELETE either -- agent_runs is an
-- operational log, not corrected in place; if retention policy is ever
-- needed, it belongs in a dedicated GC job with its own grant, not a
-- blanket DELETE on the write role.
GRANT INSERT ON agent_runs TO obligo_brain;

-- No grant to obligo_app yet: apps/core has no endpoint that reads or
-- writes agent_runs today. Add its (SELECT-only) grant in a later
-- migration when that endpoint exists.
