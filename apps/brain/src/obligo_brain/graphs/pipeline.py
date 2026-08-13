"""End-to-end pipeline orchestration for one segment (blueprint §6.3
stages 1-4: Candidate extraction -> Span grounding -> Lark parse/AST ->
Type check + symbol resolution). The first checkpoint that actually
sequences run_extraction(), compile_candidates(), run_repair() and
typecheck() into one call -- every prior checkpoint built and tested one
stage in isolation.

Deliberately a plain function, not LangGraph. Checked directly against the
falsifiable trigger graphs/repair.py's own docstring wrote for itself:
adopt LangGraph only when BOTH (a) >=2 independent conditional edges exist
(the Critic or Router node, not just the repair back-edge) AND (b) the
pipeline spans more than one Celery task boundary. Neither holds here --
this orchestration introduces no new conditional edge (the repair loop,
already built, is still the only branch in the whole pipeline) and runs
synchronously, inside whatever process calls run_pipeline(). "It's about
time" is not a reason, per that same docstring.

Ordering is strict and never interleaved, matching ir_compile.py's own
documented invariant that compile (including repair) fully resolves for a
candidate before typecheck ever sees it:

    extract (run_extraction)
      -> ground (inside run_extraction, via ground_candidates())
        -> compile (compile_candidates)
          -> repair whatever failed to compile (run_repair)
            -> typecheck everything that ended up compiled, direct or repaired

No new persistence. CLAUDE.md's carried-forward debt list already commits
this module, before it was written, to persisting nothing for a
successfully typechecked Obligation beyond what run_extraction/run_repair
already persist on their own (agent_runs, compile_quarantine) -- there is
no `obligations` table to write into. That table is explicitly Phase 5's
deliverable (an event-sourced aggregate owned by apps/core, not something
apps/brain should insert into directly), per blueprint §21 Phase 5 and
packages/ir-spec/SPEC.md §11's identical scope line. PipelineResult is
returned to the caller in memory; what happens to it next is out of this
checkpoint's scope, the same boundary typecheck.py's own docstring already
draws for the review-queue routing its UNRESOLVED_PARTY signal implies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_compile import compile_candidates
from obligo_brain.compiler.typecheck import typecheck
from obligo_brain.graphs.extraction import run_extraction
from obligo_brain.graphs.repair import QuarantinedCandidate, run_repair
from obligo_brain.graphs.state import RejectedCandidate
from obligo_brain.models.providers import groq as groq_provider
from obligo_brain.models.providers.base import ChatModel


@dataclass(frozen=True)
class PipelineResult:
    """Every candidate extracted for one segment ends up in exactly one of
    these three buckets -- the same "always accounted for, never silently
    dropped" shape ground_candidates()/compile_candidates()/
    repair_candidates() each already guarantee individually; this is that
    guarantee, composed across all of them:

      - rejected: never survived span grounding (§6.3 stage 2's hard
        discard). Already logged in the extraction agent_runs row.
      - quarantined: survived grounding but never compiled, even after
        repair. Already persisted to compile_quarantine (V18).
      - typechecked: compiled (directly or via repair) and typechecked.
        Includes underspecified obligations with an unresolved party --
        that is a correct, surfaced outcome per CLAUDE.md ("underspecified
        obligations are stored and surfaced, not discarded"), not a
        failure bucket. Returned in memory only; see this module's
        docstring for why nothing writes it anywhere yet.
    """

    typechecked: list[ast.Obligation] = field(default_factory=list)
    rejected: list[RejectedCandidate] = field(default_factory=list)
    quarantined: list[QuarantinedCandidate] = field(default_factory=list)
    agent_run_ids: list[str] = field(default_factory=list)


def run_pipeline(
    segment_id: str,
    org_id: str,
    *,
    chat_model: ChatModel = groq_provider.complete,
) -> PipelineResult:
    """The whole extraction -> ground -> compile -> repair -> typecheck
    path for one segment.

    Relies on the caller having already called TenantContext.set(org_id)
    -- the same ambient-context convention every stage this function calls
    (run_extraction, run_repair, typecheck) already uses internally, so
    this function itself opens no tenant_scope() of its own.

    chat_model defaults to the real Groq adapter and is threaded unchanged
    into both run_extraction (the extractor call) and run_repair (the
    repair call) -- both stages can call the model, and tests inject one
    fake/cassette-backed callable that drives both.

    Propagates SegmentTooLargeError from run_extraction unchanged: whether
    to skip, split, or escalate an oversized segment is a Router/Loader
    policy decision run_extraction's own docstring already scopes away
    from this checkpoint, and wrapping or reinterpreting it here would
    just be a second place making the same non-decision.
    """
    extraction = run_extraction(segment_id, org_id, chat_model=chat_model)

    compiled, failures = compile_candidates(extraction.grounded)

    repair = run_repair(
        extraction.segment,
        org_id,
        failures,
        chat_model=chat_model,
        parent_run_id=extraction.agent_run_id,
    )

    typechecked = [typecheck(obligation) for obligation in [*compiled, *repair.compiled]]

    return PipelineResult(
        typechecked=typechecked,
        rejected=extraction.rejected,
        quarantined=repair.quarantined,
        agent_run_ids=[extraction.agent_run_id, *repair.agent_run_ids],
    )
