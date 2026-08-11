"""The IR Compiler stage (blueprint §6.8's extraction graph node of the
same name; §6.3 stage 3, "Lark parse -> AST"): the deterministic bridge
between a GroundedCandidate (graphs/state.py -- verbatim spans, an
unstructured temporal_raw phrase, unstructured condition_raws) and
parser.parse()'s DSL input.

Deliberately a plain, pure function -- no I/O, no LangGraph, same "do NOT
use a graph when the flow is linear" reasoning already applied to
extraction.py's Extractor/Span Grounder. It is also deliberately NOT the
parse-error repair loop (§6.3 stage 3's own failure path, ≤2 retries
feeding the parser's message back to the LLM): this function classifies or
fails once, with no retry and no model call of its own.

Two real parsing/classification problems live here, and both are resolved
by deterministic pattern matching rather than a second LLM call --
Standing Principle 2 ("anything a parser... can decide must not be decided
by an LLM") applies directly, because which of the five frozen Temporal
forms an obligation gets, and what its extracted duration/date/trigger
actually is, determines the compiled IR's meaning, not just a draft:

1. temporal_raw -> one of the five frozen Temporal forms. The five forms
   are signalled by a small, closed vocabulary of contract-drafting
   keywords ("within", "by", "every", "during", "before"/"after") -- the
   same kind of closed-taxonomy problem grammar/obligation.lark already
   solves for ACTION and modality, not open-ended NLU. Each form's regex is
   anchored to its own distinct leading keyword, so at most one form can
   ever match a given phrase (no AMBIGUOUS_TEMPORAL case is reachable under
   this design; UNMAPPABLE_TEMPORAL covers "no form's keyword matched").

2. condition_raws -> the IF/predicate grammar. Each entry becomes exactly
   one AtomPredicate wrapping its raw text verbatim; multiple entries
   become multiple separate `IF "..."` clauses (the grammar already
   supports condition*, and Obligation.conditions is already a tuple),
   read as implicit conjunction. This function does NOT attempt to detect
   AND/OR/NOT structure inside a single condition string -- unlike the
   temporal vocabulary, boolean connectives in free legal text are
   genuinely ambiguous ("not later than" contains "not" but isn't a
   boolean negation), and that would be real NLU with a real
   misclassification hazard. Because every string is trivially a valid
   atom, there is no failure mode for condition mapping.

Failure discipline: an unmappable temporal_raw REJECTS THE WHOLE
CANDIDATE (CompileFailure), it does not silently compile with
temporal=None. Dropping just the temporal field would silently understate
the obligation (a timed "notify within 5 days" quietly becoming an untimed
"notify" is a different, weaker obligation) -- the same reasoning
extraction.py's NESTED_FIELD_NOT_IN_SPAN already applies by discarding the
whole candidate rather than patching one field. There is also no AST slot
to hold "has a temporal phrase, couldn't classify its shape": Temporal is
frozen at exactly five variants (blueprint §21), so there is nowhere
honest to put a partial result. A GroundedCandidate whose temporal_raw is
genuinely None (no temporal phrase extracted at all) compiles temporal=None
correctly -- that is not a drop.

modality/action/object_class are only lightly, deterministically
canonicalized here (case/whitespace normalization) and then left for the
real grammar to validate as the closed-taxonomy authority -- re-checking
ast.MODALITIES/ast.ACTIONS here would duplicate what
grammar/obligation.lark's own terminals already enforce, and any mismatch
surfaces as a PARSE_ERROR with the parser's own precise diagnostic.

Ordering relative to typecheck.py: strictly before, never interleaved.
This function returns a plain ast.Obligation (parser.py's own output
shape); typecheck.py's tenant-scoped party/date/trigger resolution runs
separately, afterward, unchanged. This function opens no DB connection and
calls tenant_scope() nowhere -- it is pure, like ground_candidates() --so
introducing it changes nothing about typecheck()'s tenant-scoped party
resolution timing.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from obligo_brain.compiler import ast
from obligo_brain.compiler.parser import ObligationParseError, parse
from obligo_brain.compiler.unparse import format_confidence
from obligo_brain.graphs.state import GroundedCandidate

# word -> UNIT terminal (grammar/obligation.lark: "h"|"d"|"bd"|"w"|"mo"|"y").
# "business days?" must be tried before "days?" in the shared alternation
# below, or "business days" would match the "days?" branch first and lose
# the "business" qualifier.
_UNIT_ALTERNATION = r"business\s+days?|days?|hours?|weeks?|months?|years?|bd|h|d|w|mo|y"
_UNIT_WORDS = {
    "business day": "bd", "business days": "bd", "bd": "bd",
    "day": "d", "days": "d", "d": "d",
    "hour": "h", "hours": "h", "h": "h",
    "week": "w", "weeks": "w", "w": "w",
    "month": "mo", "months": "mo", "mo": "mo",
    "year": "y", "years": "y", "y": "y",
}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_WITHIN_RE = re.compile(
    rf"^within\s+(\d+(?:\.\d+)?)\s*({_UNIT_ALTERNATION})\s+of\s+(.+)$", re.IGNORECASE
)
# Trailing `\.?` before every fixed-format-token anchor below (EVERY's unit,
# DURING's second date) tolerates a sentence-terminating period -- real for
# any temporal_raw that is a verbatim quote of a full sentence (LLMCandidate
# requires verbatim quoting). This is safe ONLY because a unit token or an
# ISO date is a fixed, unambiguous format that can never legitimately
# contain a trailing period itself (unlike WITHIN's/RELATIVE's free-text
# trigger capture, or BY's alias fallback, which stay untouched -- an
# abbreviation like "Corp." at the end of a trigger phrase must be kept
# byte-verbatim, not silently stripped).
_EVERY_RE = re.compile(rf"^every\s+(\d+(?:\.\d+)?)\s*({_UNIT_ALTERNATION})\.?$", re.IGNORECASE)
# DURING only accepts two ISO-8601 date literals on either side, not a
# defined-term alias -- a deliberate scope limit (strict over loose, per
# this checkpoint's own strictness decision): a raw phrase naming an
# interval by two ALIAS termini ("during the Term") is common enough but
# genuinely ambiguous to split deterministically into two separate alias
# phrases from one free-text string, unlike WITHIN/BY's single trailing
# phrase. Falls through to UNMAPPABLE_TEMPORAL rather than guessing a split.
_DURING_RE = re.compile(
    r"^during\s+(\d{4}-\d{2}-\d{2})\s*\.\.\s*(\d{4}-\d{2}-\d{2})\.?$", re.IGNORECASE
)
_RELATIVE_RE = re.compile(r"^(before|after)\s+(.+)$", re.IGNORECASE)
_BY_RE = re.compile(r"^by\s+(.+)$", re.IGNORECASE)


def _unit_token(word: str) -> str:
    return _UNIT_WORDS[re.sub(r"\s+", " ", word.strip().lower())]


def _format_amount(amount_str: str) -> str:
    amount = float(amount_str)
    return str(int(amount)) if amount.is_integer() else amount_str


def _q(s: str) -> str:
    return json.dumps(s)


def _date_or_alias_dsl(raw: str) -> str:
    """A DateRef surface: a bare DATE literal if raw is ISO-8601 (tolerating
    one trailing sentence-terminating period, e.g. a verbatim "by
    2026-01-01." quote -- the period is stripped only for this fixed-format
    check, never from the alias fallback below), otherwise a quoted alias
    phrase kept exactly as extracted (an UnresolvedDate once parsed) -- the
    identical convention grammar/obligation.lark's datetime_ref documents.

    Without the trailing-period tolerance, a real resolvable date would
    silently downgrade to an unresolved alias whenever temporal_raw is
    quoted from the end of a sentence -- found via adversarial testing
    against realistic (non-textbook) phrasing, not covered by the original
    hypothesis/fixture suite.
    """
    stripped = raw.strip()
    without_trailing_period = stripped[:-1] if stripped.endswith(".") else stripped
    if _DATE_RE.match(without_trailing_period):
        return without_trailing_period
    return _q(stripped)


class CompileFailureReason(str, Enum):
    """Why a GroundedCandidate never became an ast.Obligation. Recorded,
    never silently dropped -- same discipline as
    graphs.state.RejectionReason.
    """

    UNMAPPABLE_TEMPORAL = "UNMAPPABLE_TEMPORAL"  # temporal_raw matched none of the 5 frozen forms
    PARSE_ERROR = "PARSE_ERROR"  # DSL built, but grammar/obligation.lark rejected it


@dataclass(frozen=True)
class CompileFailure:
    reason: CompileFailureReason
    detail: str
    candidate: GroundedCandidate


def _classify_temporal(temporal_raw: str) -> str | None:
    """Returns the DSL substring for one of the 5 frozen Temporal forms, or
    None if temporal_raw matches none of them. Each regex is anchored to a
    distinct leading keyword, so at most one can ever match.
    """
    if m := _WITHIN_RE.match(temporal_raw):
        amount, unit_word, trigger_text = m.groups()
        return f"WITHIN {_format_amount(amount)}{_unit_token(unit_word)} OF {_q(trigger_text.strip())}"

    if m := _EVERY_RE.match(temporal_raw):
        amount, unit_word = m.groups()
        return f"EVERY {_format_amount(amount)}{_unit_token(unit_word)}"

    if m := _DURING_RE.match(temporal_raw):
        start, end = m.groups()
        return f"DURING {start} .. {end}"

    if m := _RELATIVE_RE.match(temporal_raw):
        direction, trigger_text = m.groups()
        return f"{direction.upper()} {_q(trigger_text.strip())}"

    if m := _BY_RE.match(temporal_raw):
        (date_or_alias,) = m.groups()
        return f"BY {_date_or_alias_dsl(date_or_alias)}"

    return None


def _build_dsl(candidate: GroundedCandidate) -> str | CompileFailure:
    llm = candidate.llm_candidate

    modality = llm.modality.strip().upper()
    action = llm.action.strip().upper()
    object_class = re.sub(r"\s+", "_", llm.object_class.strip().lower())

    parts = [
        modality,
        _q(llm.obligor_alias),
        action,
        _q(llm.obligee_alias),
        object_class,
        _q(llm.object_raw_text),
    ]

    if llm.temporal_raw is not None:
        temporal_dsl = _classify_temporal(llm.temporal_raw.strip())
        if temporal_dsl is None:
            return CompileFailure(
                reason=CompileFailureReason.UNMAPPABLE_TEMPORAL,
                detail=f"temporal_raw {llm.temporal_raw!r} matches none of the 5 frozen Temporal forms",
                candidate=candidate,
            )
        parts.append(temporal_dsl)

    for condition_raw in llm.condition_raws:
        parts.append(f"IF {_q(condition_raw)}")

    parts.append(candidate.source.segment_id)
    parts.append(str(candidate.source.char_start))
    parts.append(str(candidate.source.char_end))
    parts.append(format_confidence(llm.confidence))

    return " ".join(parts)


def compile_candidate(candidate: GroundedCandidate) -> ast.Obligation | CompileFailure:
    """Deterministically builds a DSL string from `candidate` and parses it
    via the real grammar (parser.parse()) -- the grammar itself is the
    closed-taxonomy authority for modality/action/object_class, so this
    function does not duplicate that validation. Returns a CompileFailure,
    never raises, on either classification failure (UNMAPPABLE_TEMPORAL) or
    grammar rejection (PARSE_ERROR) -- symmetric with
    graphs.state.RejectedCandidate's "always accounted for, never silently
    dropped" shape.
    """
    dsl_or_failure = _build_dsl(candidate)
    if isinstance(dsl_or_failure, CompileFailure):
        return dsl_or_failure

    try:
        return parse(dsl_or_failure)
    except ObligationParseError as exc:
        return CompileFailure(
            reason=CompileFailureReason.PARSE_ERROR,
            detail=str(exc),
            candidate=candidate,
        )


def compile_candidates(
    candidates: Sequence[GroundedCandidate],
) -> tuple[list[ast.Obligation], list[CompileFailure]]:
    """Batch form, mirroring extraction.ground_candidates()'s shape: every
    input ends up in exactly one of the two lists.
    """
    compiled: list[ast.Obligation] = []
    failed: list[CompileFailure] = []
    for candidate in candidates:
        result = compile_candidate(candidate)
        if isinstance(result, CompileFailure):
            failed.append(result)
        else:
            compiled.append(result)
    return compiled, failed
