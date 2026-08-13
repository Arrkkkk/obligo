-- Phase 4 (§21, §6.3 stage 3, §3.9's AI-flow diagram): the parse-error
-- repair loop's terminal destination -- "≤2 repairs, then quarantine"
-- (§6.3) / "fail 3× -> Quarantine: needs_review" (§3.9).
--
-- Deliberately NOT the `quarantine` table §8.2's inventory names. That one
-- is defined by §11.6/§12 as poison-message and failed-upload storage
-- (a storage bucket path, 30-day purge, ClamAV/scan failures). Routing a
-- compiler failure -- a fully-grounded candidate obligation with real
-- offsets that the grammar rejected -- into a poison-message table would
-- be a category error: different lifecycle, different retention, different
-- reader. This is its own table.
--
-- WHY IT EXISTS NOW, at this checkpoint, rather than being deferred to
-- Phase 5's review queue (which is where a *human* eventually sees these):
-- agent_runs (V17) cannot honestly absorb this, for two independent
-- reasons found by reading V17 directly rather than assuming:
--
--   1. obligo_brain holds GRANT INSERT only on agent_runs -- no UPDATE. The
--      repair stage physically cannot amend the extractor's own row to
--      append a terminal verdict. (That grant is correct and stays; it just
--      means one row per LLM call, which is what §13.1 wants anyway.)
--   2. A candidate quarantined for lack of an actionable repair hint makes
--      ZERO LLM calls -- and agent_runs.model_id / prompt_id /
--      prompt_version / prompt_hash / input_hash are all NOT NULL. Recording
--      a non-LLM event there means writing fabricated values into the exact
--      columns whose only purpose is reproducibility (NFR-10, §13.5). Worse
--      than not recording it.
--
-- Same precedent V17 itself set: build the table at the checkpoint that
-- first produces the data, because backfilling a decision that has already
-- been made and discarded is impossible. CLAUDE.md's "never silently drop"
-- rule is load-bearing here -- a quarantined candidate that lives only in
-- a Python return value is dropped the moment no orchestrator persists it,
-- and the orchestrator (the LangGraph extraction graph) does not exist yet.
CREATE TABLE compile_quarantine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations (id),
    segment_id UUID NOT NULL REFERENCES segments (id),

    -- The grounded span, carried forward verbatim. A quarantined candidate
    -- is one that ALREADY PASSED span grounding (§6.3 stage 2 hard-discards
    -- ungrounded candidates and never reaches the repair loop), so these
    -- offsets are mechanically verified facts, not model claims:
    -- segments.text[char_start:char_end] is the real clause. That is
    -- precisely what makes a quarantine row reviewable by a human later --
    -- it can be rendered back onto the source page.
    char_start INT NOT NULL,
    char_end INT NOT NULL,
    CONSTRAINT compile_quarantine_span_nonempty CHECK (char_end > char_start),

    -- The full GroundedCandidate (llm_candidate fields + source +
    -- grounding_tier), so review does not depend on re-running extraction
    -- against a model whose output is not reproducible.
    candidate JSONB NOT NULL,

    -- Terminal state. `cause` is why the loop stopped
    -- (graphs/repair.py's QuarantineCause); `failure_reason`/
    -- `failure_detail` are the last compiler verdict
    -- (compiler/ir_compile.py's CompileFailureReason plus, for a
    -- PARSE_ERROR, Lark's own diagnostic with line/column). Deliberately no
    -- CHECK constraint enumerating either: unlike agent_runs.status, whose
    -- domain ('ok','error') is closed by definition, both of these are
    -- application enums expected to gain members as the compiler grows, and
    -- a CHECK would make every such addition a migration.
    cause TEXT NOT NULL,
    failure_reason TEXT NOT NULL,
    failure_detail TEXT NOT NULL,

    -- Total COMPILE attempts for this candidate, including the initial one
    -- made before the repair loop was entered. 1 = quarantined with no
    -- repair attempted (no actionable hint, zero model calls); 3 = the
    -- full §6.8 budget (1 initial + max_repairs=2) exhausted.
    attempts INT NOT NULL,
    CONSTRAINT compile_quarantine_attempts_positive CHECK (attempts >= 1),

    -- Lineage into agent_runs for every repair call this candidate was part
    -- of, in order. Empty for the zero-call case above. This is the join
    -- the eval harness needs to answer "what did repair actually cost, and
    -- did it ever work" -- agent_runs has no parent_run_id column, so the
    -- edge is recorded from this side.
    agent_run_ids UUID[] NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX compile_quarantine_org_id_created_at_idx
    ON compile_quarantine (org_id, created_at DESC);
CREATE INDEX compile_quarantine_segment_id_idx ON compile_quarantine (segment_id);

ALTER TABLE compile_quarantine ENABLE ROW LEVEL SECURITY;
ALTER TABLE compile_quarantine FORCE ROW LEVEL SECURITY;

CREATE POLICY compile_quarantine_tenant_isolation ON compile_quarantine
    USING (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid)
    WITH CHECK (org_id = NULLIF(current_setting('app.org_id', true), '')::uuid);

-- obligo_brain (V11) is the only writer -- the compiler runs there and
-- nowhere else. INSERT only: nothing in this checkpoint reads quarantine
-- rows back, and the eventual reader (Phase 5's review queue, which lives
-- in apps/core alongside the obligations aggregate) gets its own
-- SELECT-only grant to obligo_app in a later migration, when that endpoint
-- actually exists. Same minimal-grant-until-a-real-caller-exists
-- discipline as V12/V16/V17.
--
-- No UPDATE and no DELETE: a quarantine row is an immutable record of a
-- decision the compiler made at a point in time. "This was later fixed" is
-- a new fact belonging to whatever supersedes it (a re-extraction under a
-- bumped grammar_version, per §6.2's recompile job), not an in-place edit
-- of the history.
GRANT INSERT ON compile_quarantine TO obligo_brain;
