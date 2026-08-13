"""The parse-error repair loop (blueprint §6.3 stage 3's failure path,
§13.6's level-2 "grammar-constrained retry", §3.9's repair back-edge) --
the first genuinely branching logic in the extraction pipeline.

Given the CompileFailures that compiler/ir_compile.py produced for one
segment, feed a precise, machine-derived diagnostic back to the model, take
its corrections, re-ground them, and re-compile -- at most twice. Whatever
still doesn't compile goes to compile_quarantine (V18), never silently
dropped.

--- The budget: max_repairs = 2, i.e. 3 total compile attempts -----------

Resolved against the blueprint rather than picked. §21's Phase 4
deliverable list (and CLAUDE.md, which copied it verbatim) says "≤3
retries"; FIVE other places say 2 -- §2's metrics table ("after ≤2
repairs"), §3.9's diagram (`parse error, ≤2 retries` ... `fail 3×` ->
quarantine), §6.3 stage 3 ("≤2 repairs, then quarantine"), §6.8
(`max_repairs=2`), and §6.11's metrics ("compile success after ≤2
repairs"). §3.9 disambiguates it arithmetically: "≤2 retries" and "fail 3×"
are one budget counted two ways (1 initial attempt + 2 repairs = 3
attempts), which is almost certainly how "3" ended up in §21 labelled
"retries."

There IS a real "≤3" in the blueprint, at §13.8 -- but it belongs to a
different row: "Output fails schema | Pydantic validation | Retry ≤3 with
error fed back." That is the SCHEMA_INVALID path (extraction.py's
_parse_response), a separate loop with a separate budget and a separate
feedback payload, and it is NOT built here -- SCHEMA_INVALID remains a
terminal rejection with no retry today. Tracked as debt, not assumed
covered by this module.

--- Why this is a plain bounded loop and not LangGraph ------------------

state.py and extraction.py both pre-committed to "LangGraph gets introduced
at whichever future checkpoint adds the first real conditional edge (most
likely the parse-error repair loop)." That prediction came due here, and
the answer is still no -- not because it is never right, but because the
reasons §6.8 gives for it don't hold yet:

 - The cycle is ONE node with ONE back-edge and a bounded counter. A
   `while pending and attempt < MAX_REPAIRS` loop is a complete, exhaustive
   expression of it; a StateGraph + TypedDict + add_conditional_edges is
   more machinery describing the same control flow.
 - §6.8's own justifications are already satisfied or not yet needed.
   Per-node retry: implemented here, with domain-specific hint derivation a
   generic retry cannot supply. Visual trace: agent_runs.node_trace already
   exists and is what §6.8 says the graph maps 1:1 *to*. Checkpoint/resume
   after a worker crash: the whole loop is one synchronous call inside one
   process -- there is nothing to resume across.
 - Postgres checkpointing is a SECOND dependency
   (langgraph-checkpoint-postgres) whose library-managed tables would hold
   org-scoped intermediate state (segment text, candidate JSON) outside
   this repo's RLS-from-creation discipline. Every tenant-scoped table here
   is ENABLE + FORCE ROW LEVEL SECURITY with a minimal explicit grant.
   Adopting that is real work and a real security decision, and it should
   be made when crash-resume is actually required.
 - The graph's other branches -- Router's doc-type dispatch, the Critic's
   reject edge, the Linker -- don't exist. Modelling graph state now means
   re-modelling it when they land.

The falsifiable adoption trigger, in the same shape as CLAUDE.md's Kafka
rule ("only if ≥3 independent event consumers actually exist"): introduce
LangGraph when BOTH (a) ≥2 independent conditional edges exist -- i.e. the
Critic or Router node is built, not just this back-edge -- AND (b) the
pipeline spans more than one Celery task boundary, so crash-resume is a
real requirement. "It's about time" is not a reason.

This module lives in graphs/ rather than blueprint §6.1's suggested
compiler/repair.py: it makes LLM calls and writes to the database, and
compiler/ is deliberately I/O-free (ir_compile.py, typecheck.py's pure
core, parser.py). A documented deviation, not an oversight.

--- What actually gets fed back, and why it is not the Lark message -----

Blueprint §6.3 stage 1 is "Candidate extraction (LLM -> DSL)" and §13.6
says "the DSL parse error is fed back as the next turn's user message" --
both assume the model authors DSL. This codebase deliberately does not work
that way: the model emits LLMCandidate JSON (state.py) and ir_compile.py
builds the DSL string deterministically. Handing the model a Lark
diagnostic about a string it never wrote would teach it to start authoring
DSL, routing around the deterministic bridge AND the grounding gate.

So the parser's error is translated into field-level diagnostics
(RepairHint) about the JSON the model did write. That translation is
possible because the set of things that can fail is exhaustively known.
Tracing every path from _build_dsl to the grammar: _q() is json.dumps so
every ESCAPED_STRING slot is well-formed by construction; segment_id comes
from the database (always a UUID matching SEGMENT_ID); offsets come from
the grounder; format_confidence produces a legal FLOAT; _format_amount /
_unit_token produce legal NUMBER/UNIT; _DATE_RE guards DATE. That leaves
EXACTLY THREE fields that can ever cause a PARSE_ERROR:

    modality      -> MUST | MUST NOT | MUST_NOT | SHOULD | MAY
    action        -> the closed 34-verb ACTION alternation
    object_class  -> OBJECT_CLASS: /[a-z][a-z_]*/

All three are CLASSIFICATION fields. None is span-grounded -- _ground_one
checks obligor_alias, obligee_alias, object_raw_text, temporal_raw and each
condition_raws entry against the span, and deliberately not these. That is
what makes repairing them safe: the model is re-choosing from a closed set,
never re-quoting text, so a wrong answer produces another parse error
rather than a fabricated quote.

If none of the three checks explains a PARSE_ERROR, NO REPAIR IS ATTEMPTED
-- straight to quarantine, zero model calls. A repair prompt with no
actionable hint is a coin flip that costs money and a rate-limit slot;
"strict over loose" is the same posture ir_compile.py takes on DURING.

UNMAPPABLE_TEMPORAL is included but is a different animal, and worth being
blunt about: temporal_raw IS span-grounded, so any repaired value must
still be verbatim. If the source says "no later than thirty (30) days after
the Effective Date", NO substring of it will ever match _WITHIN_RE, and no
model can repair that while staying verbatim -- the real fix for that class
is widening ir_compile._classify_temporal's vocabulary, already named as
future scope there. The one genuinely repairable case is OVER-CAPTURE: the
model quoted "within 30 days of receipt of an invoice, provided that ..."
when the timing phrase alone is a substring of the same span. Narrowing a
quote is legal, verbatim, and re-groundable. Expect a low success rate here
and MEASURE it (the eval harness, §19.7) rather than assuming it works; if
it lands near zero on real cassettes, demoting UNMAPPABLE_TEMPORAL to
quarantine-immediately is the right follow-up.

Grounding rejections are NOT repairable and never enter this loop, per
blueprint's own instruction: §6.3 stage 2 is "Hard discard", §3.9 routes
span-not-found straight to DISCARD + log FP.

--- The structural guarantee: repairs cannot fabricate a quote ----------

The repaired candidate is built by copying the ORIGINAL LLMCandidate and
overriding ONLY the specific fields that had a hint. Every other field the
model returns is ignored entirely -- span_text, obligor_alias,
obligee_alias, object_raw_text, condition_raws and confidence are not
merely "asked" to come back unchanged, they are structurally incapable of
changing. That is Standing Principle 2 applied to a repair: don't trust the
model to obey an instruction that determines correctness; make disobeying
it inert.

The one field that IS allowed to change and is also grounded -- temporal_raw
-- gets no bespoke check here. The repaired candidate is put back through
ground_candidates() in full, the same gate that admitted it originally, and
that gate remains the sole authority. A repair that broke grounding is
quarantined (REPAIR_BROKE_GROUNDING), which is §6.3 stage 2's hard discard
plus this project's "recorded, never unlogged" reading of it.

--- Batching by segment, not by candidate ------------------------------

max_repairs=2 is per candidate in §6.8's wording, but a segment yielding 10
failing candidates would then cost up to 20 extra calls against a free tier
that is rate-limited per minute AND per day (§13.7's ~40-50 docs/day
ceiling, §13.8's "treat 429 as an expected, planned-for state"). The model
router that would enforce §6.8's "hard cost budgets" isn't built.

So one repair call carries EVERY currently-failing candidate from the
segment, each with its own index and its own hints; the next attempt
carries only those still failing. That bounds repair calls at 2 per
segment regardless of candidate count, makes §3.9's "fail 3×" arithmetic
exact, and costs nothing in feedback precision.

An attempt that changes nothing at all short-circuits the loop
(REPAIR_MADE_NO_PROGRESS) instead of spending the second call: at
temperature 0 with an identical pending set and identical diagnostics, the
next payload differs only by its nonce, so the response is deterministic
and paying for it would be pure waste.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from enum import Enum

from sqlalchemy import text
from sqlalchemy.engine import Connection

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_compile import (
    CompileFailure,
    CompileFailureReason,
    canonical_action,
    canonical_modality,
    canonical_object_class,
    compile_candidate,
)
from obligo_brain.graphs.extraction import ground_candidates
from obligo_brain.graphs.state import GroundedCandidate, LLMCandidate, SegmentRecord
from obligo_brain.models.providers import groq as groq_provider
from obligo_brain.models.providers.base import ChatCompletion, ChatModel
from obligo_brain.platform.tenancy.db import tenant_scope
from obligo_brain.prompts import registry as prompt_registry
from obligo_brain.prompts.registry import Prompt

# Blueprint §6.8's `max_repairs=2` -- see this module's docstring for how
# the §21 "≤3" discrepancy was resolved. Total compile attempts per
# candidate is MAX_REPAIRS + 1 = 3, which is §3.9's "fail 3×".
MAX_REPAIRS = 2

# grammar/obligation.lark:81 -- OBJECT_CLASS: /[a-z][a-z_]*/
_OBJECT_CLASS_RE = re.compile(r"^[a-z][a-z_]*$")


# --- Diagnostics --------------------------------------------------------


@dataclass(frozen=True)
class RepairHint:
    """One actionable, deterministically-derived field-level diagnostic.

    `legal_values` is empty for constraints that are a shape rather than an
    enumeration (object_class, temporal_raw); the prompt carries the full
    closed vocabularies for modality/action itself, hardcoded and
    drift-tested, so these are a per-candidate pointer at the offending
    field rather than the vocabulary's source of truth.
    """

    field: str
    bad_value: str
    problem: str
    legal_values: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        payload: dict = {
            "field": self.field,
            "your_value": self.bad_value,
            "problem": self.problem,
        }
        if self.legal_values:
            payload["allowed_values"] = list(self.legal_values)
        return payload


def derive_hints(failure: CompileFailure) -> list[RepairHint]:
    """Translate a compiler verdict into field-level instructions the model
    can act on. Returns [] when nothing actionable can be derived, which the
    loop treats as "quarantine immediately, make no model call."

    The three PARSE_ERROR checks below are NOT a re-litigation of
    ir_compile.py's decision that the grammar is the sole taxonomy
    authority: they run only AFTER the grammar has already rejected the
    obligation, purely to explain why, and they never gate acceptance.
    """
    llm = failure.candidate.llm_candidate

    if failure.reason is CompileFailureReason.UNMAPPABLE_TEMPORAL:
        return [
            RepairHint(
                field="temporal_raw",
                bad_value=llm.temporal_raw or "",
                problem=(
                    "this timing phrase does not match any of the five supported "
                    "shapes: 'within <N> <unit> of <trigger>', 'by <YYYY-MM-DD>', "
                    "'every <N> <unit>', 'during <YYYY-MM-DD>..<YYYY-MM-DD>', or "
                    "'before <trigger>' / 'after <trigger>'. If a SHORTER "
                    "contiguous substring of span_text is the timing phrase on "
                    "its own, return exactly that substring, copied character "
                    "for character. Do not rewrite it into one of those shapes."
                ),
            )
        ]

    if failure.reason is not CompileFailureReason.PARSE_ERROR:
        return []

    hints: list[RepairHint] = []

    # `.replace(" ", "_")` matters: obligation.lark:45 defines
    # MUST_NOT: "MUST NOT" | "MUST_NOT", so a candidate whose modality
    # canonicalizes to "MUST NOT" parses perfectly well even though
    # ast.MODALITIES only lists the underscore spelling. Without this, a
    # field that is actually fine would be reported as the broken one and
    # the real cause would go unhinted.
    modality = canonical_modality(llm.modality)
    if modality.replace(" ", "_") not in ast.MODALITIES:
        hints.append(
            RepairHint(
                field="modality",
                bad_value=llm.modality,
                problem="not one of the four supported modalities",
                legal_values=ast.MODALITIES,
            )
        )

    action = canonical_action(llm.action)
    if action not in ast.ACTIONS:
        hints.append(
            RepairHint(
                field="action",
                bad_value=llm.action,
                problem="not in the closed action taxonomy",
                legal_values=ast.ACTIONS,
            )
        )

    object_class = canonical_object_class(llm.object_class)
    if not _OBJECT_CLASS_RE.match(object_class):
        hints.append(
            RepairHint(
                field="object_class",
                bad_value=llm.object_class,
                problem=(
                    "must be lower_snake_case using only the letters a-z and "
                    "underscores, starting with a letter -- no digits, spaces, "
                    "hyphens or capitals"
                ),
            )
        )

    return hints


# --- Terminal state -----------------------------------------------------


class QuarantineCause(str, Enum):
    """Why the loop stopped trying. Distinct from CompileFailureReason,
    which says what the COMPILER objected to -- both are recorded, because
    "the grammar rejected this action verb" and "we never asked the model to
    fix it" are different facts the eval harness needs separately.
    """

    # No actionable hint could be derived -- zero model calls made.
    NO_ACTIONABLE_HINT = "NO_ACTIONABLE_HINT"
    # MAX_REPAIRS calls spent, still failing to compile.
    REPAIR_BUDGET_EXHAUSTED = "REPAIR_BUDGET_EXHAUSTED"
    # An attempt produced no change at all for anyone; at temperature 0 the
    # next identical payload is deterministic, so the loop stopped early.
    REPAIR_MADE_NO_PROGRESS = "REPAIR_MADE_NO_PROGRESS"
    # The repaired candidate compiled-or-would-have but no longer grounds
    # (only reachable via a rewritten temporal_raw). §6.3 stage 2's hard
    # discard, recorded rather than unlogged.
    REPAIR_BROKE_GROUNDING = "REPAIR_BROKE_GROUNDING"


@dataclass(frozen=True)
class QuarantinedCandidate:
    """A candidate that will never become an obligation, with everything
    needed to review it by hand later without re-running a model whose
    output isn't reproducible.

    `attempts` counts COMPILE attempts, starting at 1 for the initial
    ir_compile.py call made before this loop was entered. `repair_calls` is
    the 1-based attempt numbers of the repair calls this candidate was part
    of -- deliberately a separate count, because a candidate the model
    silently omits from its response was paid for without producing a new
    compile attempt, and conflating the two would hide that.
    """

    candidate: GroundedCandidate
    cause: QuarantineCause
    failure_reason: str
    failure_detail: str
    attempts: int
    repair_calls: tuple[int, ...] = ()
    agent_run_ids: tuple[str, ...] = ()


# --- Loop internals -----------------------------------------------------


@dataclass(frozen=True)
class _Pending:
    index: int
    candidate: GroundedCandidate
    failure: CompileFailure
    hints: tuple[RepairHint, ...]
    attempts: int = 1
    repair_calls: tuple[int, ...] = ()

    def to_payload(self) -> dict:
        return {
            "index": self.index,
            "candidate": self.candidate.llm_candidate.model_dump(),
            "failure_reason": self.failure.reason.value,
            "fields_to_correct": [hint.to_payload() for hint in self.hints],
        }


@dataclass(frozen=True)
class RepairCallRecord:
    """One LLM call's worth of accounting, handed back for the caller to
    persist. Kept separate from the call itself so the whole loop stays
    runnable with no database (tests/graphs/test_repair.py).
    """

    attempt: int
    completion: ChatCompletion
    provider: str
    model_id: str
    prompt: Prompt
    input_hash: str
    node_trace: dict


@dataclass(frozen=True)
class RepairLoopResult:
    compiled: list[ast.Obligation] = field(default_factory=list)
    quarantined: list[QuarantinedCandidate] = field(default_factory=list)
    calls: list[RepairCallRecord] = field(default_factory=list)


def _parse_repair_response(raw_content: str) -> tuple[dict[int, dict], list[str]]:
    """Returns ({index: repair item}, [notes about anything ignored]).

    Never raises: the model's response is untrusted input like any other
    (Standing Principle 4), and a malformed repair response must degrade to
    "nothing got repaired this attempt", not to an exception that loses the
    candidates entirely.
    """
    notes: list[str] = []
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        return {}, [f"repair response was not valid JSON: {exc}"]

    if not isinstance(payload, dict) or not isinstance(payload.get("repairs"), list):
        return {}, [f"repair response missing a top-level 'repairs' array: {raw_content!r}"]

    items: dict[int, dict] = {}
    for entry in payload["repairs"]:
        if not isinstance(entry, dict):
            notes.append(f"ignored non-object repair entry: {entry!r}")
            continue
        index = entry.get("index")
        if not isinstance(index, int) or isinstance(index, bool):
            notes.append(f"ignored repair entry with a non-integer index: {entry!r}")
            continue
        if index in items:
            # Two corrections for one candidate is the model contradicting
            # itself; there is no principled way to choose, and choosing
            # silently is exactly the guess symbols.resolve_party() and the
            # grounder both refuse to make on an ambiguous match.
            notes.append(f"ignored duplicate repair for index {index}")
            items.pop(index)
            continue
        items[index] = entry
    return items, notes


# Fields a repair is ever permitted to change. Everything else on
# LLMCandidate -- span_text, obligor_alias, obligee_alias, object_raw_text,
# condition_raws, confidence -- is copied from the original and cannot be
# replaced by model output, so a repair is structurally incapable of
# fabricating a quote. See this module's docstring.
_REPAIRABLE_FIELDS = frozenset({"modality", "action", "object_class", "temporal_raw"})


def _apply_repair(pending: _Pending, item: dict) -> LLMCandidate | None:
    """Build the repaired LLMCandidate, or None if the model changed nothing
    usable. Only fields that actually carried a hint are taken -- a model
    volunteering a "correction" to a field the compiler never objected to is
    a chance to degrade a right answer, not a chance to fix a wrong one.
    """
    hinted = {hint.field for hint in pending.hints} & _REPAIRABLE_FIELDS
    original = pending.candidate.llm_candidate

    updates: dict[str, str] = {}
    for name in hinted:
        value = item.get(name)
        # A non-string (including an explicit null for temporal_raw) is
        # never accepted: nulling temporal_raw would silently turn a timed
        # obligation into an untimed, weaker one -- the exact drop
        # ir_compile.py refuses to make.
        if not isinstance(value, str) or not value.strip():
            continue
        if value == getattr(original, name):
            continue
        updates[name] = value

    if not updates:
        return None
    return original.model_copy(update=updates)


def repair_candidates(
    segment: SegmentRecord,
    failures: Sequence[CompileFailure],
    *,
    chat_model: ChatModel,
    prompt: Prompt,
    model_id: str,
    temperature: float = 0.0,
    max_repairs: int = MAX_REPAIRS,
) -> RepairLoopResult:
    """The whole bounded loop, with LLM calls but NO database access --
    mirroring extraction.py's own split between extract_candidates() (model,
    no DB) and run_extraction() (DB orchestration), so the branching logic
    is testable end to end against a fake ChatModel.

    Every input failure ends up in exactly one of `compiled` or
    `quarantined`; nothing is ever silently dropped.
    """
    result_compiled: list[ast.Obligation] = []
    quarantined: list[QuarantinedCandidate] = []
    calls: list[RepairCallRecord] = []

    pending: list[_Pending] = []
    for index, failure in enumerate(failures):
        hints = derive_hints(failure)
        if hints:
            pending.append(
                _Pending(
                    index=index,
                    candidate=failure.candidate,
                    failure=failure,
                    hints=tuple(hints),
                )
            )
            continue
        quarantined.append(
            QuarantinedCandidate(
                candidate=failure.candidate,
                cause=QuarantineCause.NO_ACTIONABLE_HINT,
                failure_reason=failure.reason.value,
                failure_detail=failure.detail,
                attempts=1,
            )
        )

    attempt = 0
    stopped_early = False
    while pending and attempt < max_repairs:
        attempt += 1

        failures_payload = json.dumps(
            [p.to_payload() for p in pending], ensure_ascii=False, indent=2
        )
        system, user = prompt_registry.render_repair(
            prompt, segment_text=segment.text, failures=failures_payload
        )
        completion = chat_model(
            system=system, user=user, model_id=model_id, temperature=temperature
        )
        items, notes = _parse_repair_response(completion.content)

        still_pending: list[_Pending] = []
        outcomes: list[dict] = []
        made_progress = False

        for p in pending:
            p = replace(p, repair_calls=(*p.repair_calls, attempt))
            item = items.get(p.index)

            if item is None:
                outcomes.append({"index": p.index, "outcome": "not_returned_by_model"})
                still_pending.append(p)
                continue

            repaired_llm = _apply_repair(p, item)
            if repaired_llm is None:
                outcomes.append({"index": p.index, "outcome": "no_usable_change"})
                still_pending.append(p)
                continue

            made_progress = True
            p = replace(p, attempts=p.attempts + 1)

            # The repaired candidate goes back through the SAME grounding
            # gate that admitted the original -- not a bespoke partial check
            # here. span_text is unchanged by construction, so this can only
            # fail on a rewritten temporal_raw, which is precisely the case
            # that must fail.
            grounded, rejected = ground_candidates(segment, [repaired_llm])
            if rejected:
                rejection = rejected[0]
                outcomes.append(
                    {
                        "index": p.index,
                        "outcome": "broke_grounding",
                        "rejection_reason": rejection.reason.value,
                    }
                )
                quarantined.append(
                    QuarantinedCandidate(
                        candidate=p.candidate,
                        cause=QuarantineCause.REPAIR_BROKE_GROUNDING,
                        failure_reason=rejection.reason.value,
                        failure_detail=rejection.detail,
                        attempts=p.attempts,
                        repair_calls=p.repair_calls,
                    )
                )
                continue

            compiled_or_failure = compile_candidate(grounded[0])
            if isinstance(compiled_or_failure, ast.Obligation):
                outcomes.append({"index": p.index, "outcome": "compiled"})
                result_compiled.append(compiled_or_failure)
                continue

            outcomes.append(
                {
                    "index": p.index,
                    "outcome": "still_failing",
                    "reason": compiled_or_failure.reason.value,
                }
            )
            new_hints = derive_hints(compiled_or_failure)
            if not new_hints:
                # The repair traded one failure for an unexplainable one.
                # Same rule as the initial pass: no actionable hint, no
                # further model call.
                quarantined.append(
                    QuarantinedCandidate(
                        candidate=grounded[0],
                        cause=QuarantineCause.NO_ACTIONABLE_HINT,
                        failure_reason=compiled_or_failure.reason.value,
                        failure_detail=compiled_or_failure.detail,
                        attempts=p.attempts,
                        repair_calls=p.repair_calls,
                    )
                )
                continue
            still_pending.append(
                replace(
                    p,
                    candidate=grounded[0],
                    failure=compiled_or_failure,
                    hints=tuple(new_hints),
                )
            )

        calls.append(
            RepairCallRecord(
                attempt=attempt,
                completion=completion,
                provider=str(prompt.model_constraints.get("provider", "unknown")),
                model_id=model_id,
                prompt=prompt,
                input_hash=repair_input_hash(system=system, user=user, model_id=model_id),
                node_trace={
                    "attempt": attempt,
                    "max_repairs": max_repairs,
                    "pending": [
                        {
                            "index": p.index,
                            "char_start": p.candidate.source.char_start,
                            "char_end": p.candidate.source.char_end,
                            "failure_reason": p.failure.reason.value,
                            # The raw Lark diagnostic is recorded HERE and
                            # deliberately never sent to the model -- it
                            # describes a DSL string the model neither wrote
                            # nor can see. Kept because it is the precise,
                            # machine-generated signal §6.3 calls "the
                            # design's signature", and the eval harness
                            # needs it even though the prompt does not.
                            "compiler_detail": p.failure.detail,
                            "hints": [h.to_payload() for h in p.hints],
                        }
                        for p in pending
                    ],
                    "outcomes": outcomes,
                    "ignored": notes,
                },
            )
        )

        pending = still_pending
        if not made_progress:
            stopped_early = True
            break

    terminal_cause = (
        QuarantineCause.REPAIR_MADE_NO_PROGRESS
        if stopped_early
        else QuarantineCause.REPAIR_BUDGET_EXHAUSTED
    )
    for p in pending:
        quarantined.append(
            QuarantinedCandidate(
                candidate=p.candidate,
                cause=terminal_cause,
                failure_reason=p.failure.reason.value,
                failure_detail=p.failure.detail,
                attempts=p.attempts,
                repair_calls=p.repair_calls,
            )
        )

    return RepairLoopResult(compiled=result_compiled, quarantined=quarantined, calls=calls)


def repair_input_hash(*, system: str, user: str, model_id: str) -> str:
    """agent_runs.input_hash for a repair call.

    NOT extraction.py's sha256(segment_id : prompt_hash : model_id). That
    formula is wrong here and it is a real hazard, not a style difference:
    two different failing candidates from the SAME segment, repaired with
    the same prompt and model, would collide on one input_hash -- and V17
    records that column as the future key for §6.10's content-hash response
    cache, so a collision would serve one candidate's repair for another's.

    The general rule is "hash the actual rendered call inputs", of which
    extraction's formula is a special case (given prompt_hash and
    segment_id, the rendered message is fully determined). Documented in
    both places rather than left as two unexplained formulas.
    """
    return hashlib.sha256(f"{system}\x00{user}\x00{model_id}".encode()).hexdigest()


# --- Orchestration: run the loop, persist the accounting ----------------


@dataclass(frozen=True)
class RepairResult:
    compiled: list[ast.Obligation]
    quarantined: list[QuarantinedCandidate]
    agent_run_ids: list[str]


def _record_repair_run(
    conn: Connection,
    *,
    org_id: str,
    segment: SegmentRecord,
    call: RepairCallRecord,
    parent_run_id: str | None,
) -> str:
    """One agent_runs row per LLM call -- never aggregated across a
    multi-call sequence. Collapsing three calls into one row would lose the
    per-call model_id and prompt_version, which is exactly what breaks once
    §6.10's router does provider failover mid-sequence or the repair prompt
    versions independently of extraction.

    node='repair' distinguishes these from the extractor's rows.
    obligo_brain holds INSERT only on agent_runs (V17) -- by design -- so
    this cannot and does not amend the extractor's row; lineage travels the
    other way, via parent_run_id inside node_trace. agent_runs has no
    parent_run_id column, and it does not need one for the accounting that
    is actually required: cost and latency per segment is a SUM over rows
    filtered by segment_id, which is already indexed
    (agent_runs_segment_id_idx). If the eval harness later needs a real
    join, adding the column is a clean additive migration then.

    cost_usd stays NULL for the same reason extraction.py leaves it NULL:
    deriving it needs a per-model pricing table, which is model-router
    scope (§6.10) and still not built. Tokens and latency -- what cost is
    derived from -- are recorded per row.

    The row id is generated client-side, deliberately: Postgres requires
    SELECT privilege on any column named in a RETURNING clause, and
    obligo_brain has INSERT only. See extraction.py's _record_agent_run()
    for the full account -- it had this exact bug, live, until this
    checkpoint's real-database test surfaced it.
    """
    node_trace = dict(call.node_trace)
    if parent_run_id is not None:
        node_trace["parent_run_id"] = parent_run_id

    agent_run_id = str(uuid.uuid4())
    conn.execute(
        text(
            "INSERT INTO agent_runs "
            "(id, org_id, node, provider, model_id, prompt_id, prompt_version, prompt_hash, "
            " input_hash, segment_id, input_tokens, output_tokens, latency_ms, status, node_trace) "
            "VALUES (:id, :org_id, 'repair', :provider, :model_id, :prompt_id, :prompt_version, :prompt_hash, "
            " :input_hash, :segment_id, :input_tokens, :output_tokens, :latency_ms, 'ok', "
            " CAST(:node_trace AS jsonb))"
        ),
        {
            "id": agent_run_id,
            "org_id": org_id,
            "provider": call.provider,
            "model_id": call.model_id,
            "prompt_id": call.prompt.id,
            "prompt_version": call.prompt.version,
            "prompt_hash": call.prompt.prompt_hash,
            "input_hash": call.input_hash,
            "segment_id": segment.id,
            "input_tokens": call.completion.input_tokens,
            "output_tokens": call.completion.output_tokens,
            "latency_ms": int(call.completion.latency_ms),
            "node_trace": json.dumps(node_trace),
        },
    )
    return agent_run_id


def _record_quarantine(
    conn: Connection, *, org_id: str, segment: SegmentRecord, item: QuarantinedCandidate
) -> None:
    """compile_quarantine (V18). See that migration's header for why this
    cannot live in agent_runs: obligo_brain has no UPDATE grant there, and a
    NO_ACTIONABLE_HINT quarantine makes zero LLM calls while agent_runs'
    model_id/prompt_* columns are all NOT NULL.
    """
    candidate_payload = {
        "llm_candidate": item.candidate.llm_candidate.model_dump(),
        "grounding_tier": item.candidate.grounding_tier.value,
        "source": {
            "segment_id": item.candidate.source.segment_id,
            "char_start": item.candidate.source.char_start,
            "char_end": item.candidate.source.char_end,
        },
    }
    conn.execute(
        text(
            "INSERT INTO compile_quarantine "
            "(org_id, segment_id, char_start, char_end, candidate, cause, "
            " failure_reason, failure_detail, attempts, agent_run_ids) "
            "VALUES (:org_id, :segment_id, :char_start, :char_end, CAST(:candidate AS jsonb), "
            " :cause, :failure_reason, :failure_detail, :attempts, CAST(:agent_run_ids AS uuid[]))"
        ),
        {
            "org_id": org_id,
            "segment_id": segment.id,
            "char_start": item.candidate.source.char_start,
            "char_end": item.candidate.source.char_end,
            "candidate": json.dumps(candidate_payload),
            "cause": item.cause.value,
            "failure_reason": item.failure_reason,
            "failure_detail": item.failure_detail,
            "attempts": item.attempts,
            "agent_run_ids": list(item.agent_run_ids),
        },
    )


def run_repair(
    segment: SegmentRecord,
    org_id: str,
    failures: Sequence[CompileFailure],
    *,
    chat_model: ChatModel = groq_provider.complete,
    parent_run_id: str | None = None,
) -> RepairResult:
    """The end-to-end repair stage for one segment: run the bounded loop,
    record one agent_runs row per LLM call, and persist every quarantined
    candidate to compile_quarantine.

    Takes a SegmentRecord rather than a segment_id (unlike run_extraction)
    because its only caller already holds one -- extraction fetched it, and
    grounding needs segment.text anyway. Re-fetching would be a redundant
    query whose only effect would be a chance for the two to disagree.

    Relies on the caller having already called TenantContext.set(org_id),
    the same ambient-context convention every other apps/brain DB access
    uses; org_id is still passed explicitly because it is a literal INSERT
    value for both tables, not merely a query filter RLS already handles.

    Returns early with no model call, no DB write and no side effect at all
    when `failures` is empty -- the common case once the compiler is
    working, and worth not paying a transaction for.

    All persistence happens in ONE transaction, deliberately: a quarantine
    row and the agent_runs rows recording the calls that produced it are one
    fact, and a crash between two transactions would leave a candidate
    quarantined with dangling lineage or, worse, silently unquarantined
    after its calls were logged. The accepted cost is that a failure writing
    the quarantine row also rolls back the agent_runs rows for calls that
    really happened and really cost money -- the LLM calls themselves are
    already made by then and are not undone. Worth revisiting if
    §6.10's budget enforcement ever needs spend to be durable independently
    of pipeline outcome.
    """
    if not failures:
        return RepairResult(compiled=[], quarantined=[], agent_run_ids=[])

    prompt = prompt_registry.load("repair")
    model_id = prompt.model_constraints["model_id"]
    temperature = float(prompt.model_constraints.get("temperature", 0.0))

    loop = repair_candidates(
        segment,
        failures,
        chat_model=chat_model,
        prompt=prompt,
        model_id=model_id,
        temperature=temperature,
    )

    with tenant_scope() as conn:
        run_ids_by_attempt: dict[int, str] = {}
        for call in loop.calls:
            run_ids_by_attempt[call.attempt] = _record_repair_run(
                conn, org_id=org_id, segment=segment, call=call, parent_run_id=parent_run_id
            )

        resolved: list[QuarantinedCandidate] = []
        for item in loop.quarantined:
            item = replace(
                item,
                agent_run_ids=tuple(
                    run_ids_by_attempt[n] for n in item.repair_calls if n in run_ids_by_attempt
                ),
            )
            _record_quarantine(conn, org_id=org_id, segment=segment, item=item)
            resolved.append(item)

    return RepairResult(
        compiled=loop.compiled,
        quarantined=resolved,
        agent_run_ids=list(run_ids_by_attempt.values()),
    )
