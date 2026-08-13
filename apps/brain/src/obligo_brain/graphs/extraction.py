"""The Extractor and Span Grounder nodes (blueprint §6.8's extraction
graph, §3.9's AI flow: Segments -> Extractor -> Span Grounder -> ...).
Deliberately plain functions, not LangGraph nodes -- §6.8's own guidance
("do NOT use when the flow is linear... only the branching parts are in
the graph") applies directly, since this checkpoint's Extractor ->
Grounder edge is unconditional. LangGraph gets introduced at whichever
future checkpoint adds the first real conditional edge (most likely the
parse-error repair loop, §6.3 stage 3).

Three functions matter here, in pipeline order:

1. extract_candidates() -- calls the LLM (an untrusted guess: which spans
   are obligations, who's obligor/obligee, the verb, the object, a raw
   temporal/condition phrase, a self-reported confidence). Never asked for
   character offsets.
2. ground_candidates() -- THE correctness gate (blueprint §21's acceptance
   criterion: "span-grounding rate exactly 100%... by construction";
   §19.3's grounding invariant; CLAUDE.md's "if a candidate's span text
   doesn't literally appear in the source segment, discard it"). Pure,
   deterministic, no I/O. Computes real offsets by locating the model's
   claimed span_text in the segment's own text -- offsets are derived,
   never asserted by the model, the same discipline Phase 3 used for
   PyMuPDF extraction, carried across the LLM trust boundary.
3. run_extraction() -- the orchestrator: fetches a segment, calls the
   model, grounds every candidate, and records exactly one agent_runs
   (V17) row for the whole call.

Span grounding, precisely (two tiers, deliberately not three):

Tier A -- EXACT: segment.text.find(span_text). If there is exactly one
occurrence, that's the match. Zero occurrences falls through to Tier B;
more than one occurrence is an unresolvable ambiguity in the source itself
(Tier B's normalization can only ever find equal-or-more matches, never
fewer, so there's no point trying it) -- rejected as AMBIGUOUS_SPAN
immediately, the same "an ambiguous match is a different failure the
review queue should still see as unresolved, not a guess" precedent
symbols.resolve_party() already set.

Tier B -- NORMALIZED: segment text and span_text are both passed through
an identical, reversible normalization (NBSP/whitespace-run collapse,
zero-width-character removal, smart-quote and dash-variant folding) that
tracks an index back to the ORIGINAL text for every normalized character.
A match in normalized space is mapped back to original character offsets,
and the stored span is always segment.text[char_start:char_end] -- the
document's own bytes, never the model's string. That's what keeps
"segment.text[cs:ce] == the grounded span" true BY CONSTRUCTION for both
tiers, exactly like Phase 3's PyMuPDF offset guarantee, and it's what
tests/graphs/test_ground.py's hypothesis property checks.

Tier C (Levenshtein-tolerant fuzzy matching, blueprint §6.3's "<=5%
Levenshtein tolerance for OCR noise") is a DELIBERATE, DOCUMENTED
OMISSION, not a gap left for later. In a 200-character clause, "shall" ->
"shall not" is a 4-character edit, about 2% -- comfortably under a 5%
threshold, and it inverts the obligation's meaning. A fuzzy gate on the
single most important correctness control in this project is disqualified
by that example alone; fuzzy matching would also break the by-construction
guarantee above, since a fuzzy match means the stored slice differs from
what was actually matched. The OCR-noise case the tolerance exists for is
already handled by data this codebase has that blueprint's §6.3 table
predates: segments.ocr_confidence (V14) and the existing
LOW_OCR_CONFIDENCE flag. If Tier C is ever wanted, it should be
flag-gated to low-confidence segments only and record its edit distance,
not silently relax this gate for every candidate.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import Connection

from obligo_brain.compiler.ast import SourceRef
from obligo_brain.graphs.state import (
    GroundedCandidate,
    GroundingTier,
    LLMCandidate,
    RejectedCandidate,
    RejectionReason,
    SegmentRecord,
)
from obligo_brain.models.providers import groq as groq_provider
from obligo_brain.models.providers.base import ChatCompletion, ChatModel
from obligo_brain.platform.tenancy.db import tenant_scope
from obligo_brain.prompts import registry as prompt_registry
from obligo_brain.prompts.registry import Prompt

# A rough, deliberately conservative proxy for Groq's free-tier 6k TPM
# budget (blueprint §13.3) -- not a real token count (no tokenizer is
# wired up at this checkpoint, and getting one exactly right is model
# router scope), just a hard stop so an oversized segment fails loudly
# instead of being silently truncated (which would silently lose whatever
# obligation-bearing text got cut off -- exactly the failure mode this
# project has repeatedly refused to accept elsewhere, e.g. Phase 3's
# decompression-bomb guard). ~4 chars/token is a standard rough English
# ratio; 20,000 chars stays well under the 6k-token input budget with
# headroom for the fixed system-prompt overhead and completion tokens.
MAX_SEGMENT_CHARS = 20_000


class SegmentTooLargeError(Exception):
    """Raised by run_extraction() instead of silently truncating an
    oversized segment. What happens next (skip and log, split the
    segment, escalate to the long-document Gemini path per §13.2) is a
    Router/Loader-node policy decision -- explicitly out of this
    checkpoint's scope (only Extractor and Span Grounder are built here)
    -- so this is deliberately left for the caller to decide, not guessed
    at here.
    """

    def __init__(self, segment_id: str, char_count: int, limit: int):
        super().__init__(
            f"segment {segment_id} is {char_count} chars, exceeding the {limit}-char "
            "extraction guard -- refusing to truncate; caller must decide how to split "
            "or route this segment"
        )
        self.segment_id = segment_id
        self.char_count = char_count
        self.limit = limit


# --- Tier B normalization ---------------------------------------------

_ZERO_WIDTH = frozenset("​‌‍﻿")
_QUOTE_FOLD = {
    "‘": "'", "’": "'", "‚": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "″": '"',
}
_DASH_FOLD = {"–": "-", "—": "-", "−": "-"}


def _normalize_with_index_map(source: str) -> tuple[str, list[int]]:
    """Returns (normalized_text, index_map) where index_map[j] is the
    index into `source` of the original character responsible for
    normalized_text[j]. Every transformation here is either a 1:1
    character substitution (quote/dash folding) or a removal (zero-width
    characters, collapsed whitespace runs) -- never an expansion -- so
    this mapping is always well-defined and exact, with no approximation.
    NFKC normalization is deliberately NOT applied here: it can expand a
    single character into multiple (e.g. a ligature), which would need a
    many-to-one map and add real complexity for a case that isn't observed
    in real contract text; the normalizations actually needed (NBSP/curly
    quotes/dash variants/zero-width junk) are all handled by the
    character-class rules below.
    """
    out_chars: list[str] = []
    index_map: list[int] = []
    prev_was_space = False
    for i, ch in enumerate(source):
        if ch in _ZERO_WIDTH:
            continue
        if ch.isspace():
            if prev_was_space:
                continue
            out_chars.append(" ")
            index_map.append(i)
            prev_was_space = True
            continue
        prev_was_space = False
        out_chars.append(_QUOTE_FOLD.get(ch) or _DASH_FOLD.get(ch) or ch)
        index_map.append(i)
    return "".join(out_chars), index_map


def _all_occurrences(needle: str, haystack: str) -> list[tuple[int, int]]:
    if not needle:
        return []
    matches: list[tuple[int, int]] = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            return matches
        matches.append((idx, idx + len(needle)))
        start = idx + 1


def _locate_span(
    span_text: str, segment_text: str
) -> tuple[int, int, GroundingTier] | RejectionReason:
    if not span_text.strip():
        return RejectionReason.EMPTY_SPAN

    exact = _all_occurrences(span_text, segment_text)
    if len(exact) == 1:
        start, end = exact[0]
        return start, end, GroundingTier.EXACT
    if len(exact) > 1:
        return RejectionReason.AMBIGUOUS_SPAN

    norm_segment, index_map = _normalize_with_index_map(segment_text)
    norm_span, _ = _normalize_with_index_map(span_text)
    normalized = _all_occurrences(norm_span, norm_segment)
    if len(normalized) == 1:
        norm_start, norm_end = normalized[0]
        orig_start = index_map[norm_start]
        orig_end = index_map[norm_end - 1] + 1
        # Defensive re-check, not a tautology: reslice the ORIGINAL text at
        # these mapped offsets and renormalize it independently. If that
        # doesn't reproduce exactly the normalized span that matched, the
        # index map has a bug -- fail loudly here (a real, meaningful
        # assertion) rather than grounding an offset the map got wrong.
        reslice_normalized, _ = _normalize_with_index_map(segment_text[orig_start:orig_end])
        assert reslice_normalized == norm_span, (  # noqa: S101
            f"Tier B index-map produced inconsistent offsets: "
            f"normalize(segment_text[{orig_start}:{orig_end}])={reslice_normalized!r} "
            f"!= matched normalized span {norm_span!r}"
        )
        return orig_start, orig_end, GroundingTier.NORMALIZED
    if len(normalized) > 1:
        return RejectionReason.AMBIGUOUS_SPAN

    return RejectionReason.SPAN_NOT_FOUND


def _is_grounded_substring(needle: str, haystack: str) -> bool:
    """Nested-field check (obligor_alias, obligee_alias, object_raw_text,
    temporal_raw, each condition_raws entry) against the already-grounded
    span -- not against offsets of their own, since ast.SourceRef (the
    frozen schema) has nowhere to hold per-field offsets. Same Tier A/B
    tolerance as the top-level span, applied for the identical reason:
    the model's own copy of a nested phrase can carry the same benign
    whitespace/quote variance as its copy of the full span.
    """
    if not needle:
        return True
    if needle in haystack:
        return True
    norm_needle, _ = _normalize_with_index_map(needle)
    norm_haystack, _ = _normalize_with_index_map(haystack)
    return bool(norm_needle) and norm_needle in norm_haystack


def _ground_one(segment: SegmentRecord, candidate: LLMCandidate) -> GroundedCandidate | RejectedCandidate:
    located = _locate_span(candidate.span_text, segment.text)
    if isinstance(located, RejectionReason):
        return RejectedCandidate(
            reason=located,
            detail=f"span_text {candidate.span_text!r} could not be uniquely grounded in segment {segment.id}",
            segment_id=segment.id,
            llm_candidate=candidate,
        )

    char_start, char_end, tier = located
    # The by-construction guarantee: the stored span is always a direct
    # slice of the segment's own text at the offsets grounding computed --
    # never the model's string. This is what makes "segment.text[cs:ce] ==
    # the grounded span" true for every GroundedCandidate this function
    # returns, not something asserted after the fact.
    grounded_span = segment.text[char_start:char_end]

    nested_fields: dict[str, str] = {
        "obligor_alias": candidate.obligor_alias,
        "obligee_alias": candidate.obligee_alias,
        "object_raw_text": candidate.object_raw_text,
    }
    if candidate.temporal_raw is not None:
        nested_fields["temporal_raw"] = candidate.temporal_raw
    for i, condition_raw in enumerate(candidate.condition_raws):
        nested_fields[f"condition_raws[{i}]"] = condition_raw

    for field_name, value in nested_fields.items():
        if not _is_grounded_substring(value, grounded_span):
            return RejectedCandidate(
                reason=RejectionReason.NESTED_FIELD_NOT_IN_SPAN,
                detail=f"{field_name}={value!r} is not a substring of the grounded span {grounded_span!r}",
                segment_id=segment.id,
                llm_candidate=candidate,
            )

    source = SourceRef(segment_id=segment.id, char_start=char_start, char_end=char_end)
    return GroundedCandidate(llm_candidate=candidate, source=source, grounding_tier=tier)


def ground_candidates(
    segment: SegmentRecord, candidates: Sequence[LLMCandidate]
) -> tuple[list[GroundedCandidate], list[RejectedCandidate]]:
    """Pure function: no I/O, no randomness, safe to call directly from a
    hypothesis property test. Returns (grounded, rejected) -- every input
    candidate ends up in exactly one of the two lists, so nothing is ever
    silently dropped (§13.8: "discard silently, log as FP" is read here as
    "never surfaced as an obligation," not "unrecorded" -- the caller
    records every rejection).
    """
    grounded: list[GroundedCandidate] = []
    rejected: list[RejectedCandidate] = []
    for candidate in candidates:
        result = _ground_one(segment, candidate)
        if isinstance(result, GroundedCandidate):
            grounded.append(result)
        else:
            rejected.append(result)
    return grounded, rejected


# --- Extractor ----------------------------------------------------------


@dataclass(frozen=True)
class ExtractionCallResult:
    candidates: list[LLMCandidate]
    rejected: list[RejectedCandidate]  # SCHEMA_INVALID only, at this stage
    completion: ChatCompletion


def _parse_response(raw_content: str, *, segment_id: str) -> tuple[list[LLMCandidate], list[RejectedCandidate]]:
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        return [], [
            RejectedCandidate(
                reason=RejectionReason.SCHEMA_INVALID,
                detail=f"model response was not valid JSON: {exc}",
                segment_id=segment_id,
            )
        ]

    if not isinstance(payload, dict) or not isinstance(payload.get("obligations"), list):
        return [], [
            RejectedCandidate(
                reason=RejectionReason.SCHEMA_INVALID,
                detail=f"model response missing a top-level 'obligations' array: {raw_content!r}",
                segment_id=segment_id,
            )
        ]

    candidates: list[LLMCandidate] = []
    rejected: list[RejectedCandidate] = []
    for item in payload["obligations"]:
        try:
            candidates.append(LLMCandidate.model_validate(item))
        except ValidationError as exc:
            rejected.append(
                RejectedCandidate(
                    reason=RejectionReason.SCHEMA_INVALID,
                    detail=f"candidate failed schema validation: {exc}",
                    segment_id=segment_id,
                )
            )
    return candidates, rejected


def extract_candidates(
    segment: SegmentRecord,
    *,
    chat_model: ChatModel,
    prompt: Prompt,
    model_id: str,
    temperature: float = 0.0,
) -> ExtractionCallResult:
    """Calls the model exactly once for this segment and parses its
    response into LLMCandidate instances. Everything returned here is
    still untrusted -- ground_candidates() is the actual gate. A response
    that isn't valid JSON, or an item that fails LLMCandidate's Pydantic
    validation, is recorded as a SCHEMA_INVALID rejection rather than
    raised, so one malformed item in a batch doesn't lose the rest.
    """
    system, user = prompt_registry.render(prompt, segment_text=segment.text)
    completion = chat_model(system=system, user=user, model_id=model_id, temperature=temperature)
    candidates, rejected = _parse_response(completion.content, segment_id=segment.id)
    return ExtractionCallResult(candidates=candidates, rejected=rejected, completion=completion)


# --- Orchestration: fetch segment, extract, ground, log -----------------


@dataclass(frozen=True)
class ExtractionResult:
    grounded: list[GroundedCandidate]
    rejected: list[RejectedCandidate]
    agent_run_id: str


def _fetch_segment(segment_id: str, conn: Connection) -> SegmentRecord:
    row = conn.execute(text("SELECT id, text FROM segments WHERE id = :id"), {"id": segment_id}).one()
    return SegmentRecord(id=str(row.id), text=row.text)


def _record_agent_run(
    conn: Connection,
    *,
    org_id: str,
    segment: SegmentRecord,
    prompt: Prompt,
    model_id: str,
    completion: ChatCompletion,
    grounded: list[GroundedCandidate],
    rejected: list[RejectedCandidate],
) -> str:
    """The non-negotiable rule, applied for the first time in this
    codebase: "every LLM call records model_id, prompt_version, cost, and
    latency" (CLAUDE.md), landing in agent_runs (V17), the table §6.9
    names for exactly this. `node_trace` carries a per-candidate summary
    (grounding tier or rejection reason) -- the same "node_trace" concept
    §6.8 says the UI's agent-run view maps 1:1 to.

    cost_usd is left NULL here: computing it needs a real per-model
    pricing table, which is model-router/budget-enforcement scope (§6.10),
    not built at this checkpoint. Recording tokens (which cost_usd would
    be derived from) is what this function does today.

    The row id is generated CLIENT-SIDE rather than read back with
    `RETURNING id`, and that is load-bearing, not stylistic: Postgres
    requires SELECT privilege on any column a RETURNING clause names, and
    V17 grants obligo_brain INSERT and nothing else, on purpose. This
    function originally used `RETURNING id` and would have failed with
    "permission denied for table agent_runs" on EVERY call against the real
    database -- found only when V18's checkpoint applied V17 to Neon for the
    first time and ran a real-database test (tests/graphs/test_repair_db.py;
    verified against the live database that the identical statement without
    RETURNING gets past the privilege check and reaches the RLS policy).
    Generating a surrogate key in the application is the fix that keeps
    V17's minimal grant intact; widening it to SELECT to satisfy a
    convenience clause would trade a real privilege for nothing.
    """
    node_trace = {
        "grounded": [
            {
                "grounding_tier": g.grounding_tier.value,
                "char_start": g.source.char_start,
                "char_end": g.source.char_end,
            }
            for g in grounded
        ],
        "rejected": [{"reason": r.reason.value, "detail": r.detail} for r in rejected],
    }
    # The general rule for input_hash is "hash the actual rendered call
    # inputs" (it is V17's recorded key for §6.10's future content-hash
    # response cache). This formula is a valid SPECIAL CASE of that rule,
    # not a different one: for extraction, segment_id plus prompt_hash fully
    # determine the rendered messages, so hashing the identifiers is
    # equivalent to hashing the text. That equivalence does NOT hold for
    # every caller -- graphs/repair.py's repair_input_hash() hashes the
    # rendered system/user directly, because several failing candidates can
    # share one segment_id and would otherwise collide on a cache key. See
    # that function's docstring.
    input_hash = hashlib.sha256(f"{segment.id}:{prompt.prompt_hash}:{model_id}".encode()).hexdigest()

    agent_run_id = str(uuid.uuid4())
    conn.execute(
        text(
            "INSERT INTO agent_runs "
            "(id, org_id, node, provider, model_id, prompt_id, prompt_version, prompt_hash, "
            " input_hash, segment_id, input_tokens, output_tokens, latency_ms, status, node_trace) "
            "VALUES (:id, :org_id, 'extractor', 'groq', :model_id, :prompt_id, :prompt_version, :prompt_hash, "
            " :input_hash, :segment_id, :input_tokens, :output_tokens, :latency_ms, 'ok', "
            " CAST(:node_trace AS jsonb))"
        ),
        {
            "id": agent_run_id,
            "org_id": org_id,
            "model_id": model_id,
            "prompt_id": prompt.id,
            "prompt_version": prompt.version,
            "prompt_hash": prompt.prompt_hash,
            "input_hash": input_hash,
            "segment_id": segment.id,
            "input_tokens": completion.input_tokens,
            "output_tokens": completion.output_tokens,
            "latency_ms": int(completion.latency_ms),
            "node_trace": json.dumps(node_trace),
        },
    )
    return agent_run_id


def run_extraction(
    segment_id: str,
    org_id: str,
    *,
    chat_model: ChatModel = groq_provider.complete,
) -> ExtractionResult:
    """The end-to-end Extractor -> Span Grounder pipeline for one segment.

    Relies on the caller having already called TenantContext.set(org_id)
    -- the same ambient-context convention typecheck.py documents and
    uses (platform/tenancy/db.py, api/v1/sources.py, tasks/segmentation.py)
    -- and opens its own tenant_scope() internally, twice: once to fetch
    the segment (RLS-scoped read), once to record the agent_runs row
    (RLS-scoped write). org_id is still passed explicitly here (unlike
    typecheck()) because it's needed as a literal INSERT value for
    agent_runs.org_id, not merely as a query filter RLS already handles --
    RLS proves *which rows this connection may touch*, it doesn't supply a
    value to write into a new row.

    chat_model defaults to the real Groq adapter; tests inject a
    cassette-backed or fake callable satisfying the same ChatModel
    signature.

    Raises SegmentTooLargeError before ever calling the model if the
    segment exceeds MAX_SEGMENT_CHARS -- never silently truncates.
    """
    prompt = prompt_registry.load("extraction")
    model_id = prompt.model_constraints["model_id"]
    temperature = float(prompt.model_constraints.get("temperature", 0.0))

    with tenant_scope() as conn:
        segment = _fetch_segment(segment_id, conn)

    if len(segment.text) > MAX_SEGMENT_CHARS:
        raise SegmentTooLargeError(segment.id, len(segment.text), MAX_SEGMENT_CHARS)

    call_result = extract_candidates(
        segment, chat_model=chat_model, prompt=prompt, model_id=model_id, temperature=temperature
    )
    grounded, grounding_rejected = ground_candidates(segment, call_result.candidates)
    all_rejected = [*call_result.rejected, *grounding_rejected]

    with tenant_scope() as conn:
        agent_run_id = _record_agent_run(
            conn,
            org_id=org_id,
            segment=segment,
            prompt=prompt,
            model_id=model_id,
            completion=call_result.completion,
            grounded=grounded,
            rejected=all_rejected,
        )

    return ExtractionResult(grounded=grounded, rejected=all_rejected, agent_run_id=agent_run_id)
