"""Typed state for the extraction graph's first two nodes (Extractor ->
Span Grounder; blueprint §6.8, §21). LangGraph itself is deliberately not
wired up at this checkpoint -- §6.8's own guidance ("do NOT use when the
flow is linear... only the branching parts are in the graph") applies
directly, since Extractor -> Grounder has no conditional edge yet. These
are the typed payloads a future graph would pass between nodes; today
they're just the input/output shapes of two plain functions
(extraction.py's extract_candidates() and ground_candidates()).

The load-bearing design decision lives here: LLMCandidate carries no
character offsets. A model cannot count characters reliably, so an offset
field is an invitation to hallucinate a number that looks verifiable but
isn't. The model emits only verbatim quoted text; ground_candidates()
(extraction.py) computes offsets mechanically by locating that text in the
segment. Offsets are always derived, never asserted by the model -- the
same "offsets by construction" discipline Phase 3 used for PyMuPDF
extraction, carried across the LLM trust boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from obligo_brain.compiler.ast import SourceRef


@dataclass(frozen=True)
class SegmentRecord:
    """The minimal slice of a `segments` row (V12) the extraction graph
    needs. Deliberately not the whole row -- page/ordinal/layout/
    ocr_confidence live on the DB row and are read by extraction.py's
    DB-touching orchestration, but ground_candidates() itself only ever
    needs an id to stamp into SourceRef and the segment's own text to
    search against.
    """

    id: str
    text: str


class LLMCandidate(BaseModel):
    """The untrusted shape an Extractor LLM call is asked to produce, one
    per obligation-bearing clause it thinks it found in a segment.

    Every string-typed field except `modality`/`action`/`object_class` is
    documented as "must be a verbatim quote from the segment" in the
    extraction prompt (prompts/extraction/v1.yaml) -- but that's a prompt
    instruction, not a guarantee (Standing Principle 4: every LLM output is
    untrusted input). ground_candidates() is what actually proves it.

    Nothing on this model is validated against the closed taxonomies
    (MODALITIES, ACTIONS in compiler/ast.py) or the five temporal forms --
    that's the (not-yet-built) IR Compiler stage's job, matching
    grammar/obligation.lark's own header: "this grammar's only job is to
    validate and structure [an already-extracted] candidate." This class
    is deliberately more permissive than the DSL grammar; it's a raw
    extraction guess, not a parsed AST.
    """

    span_text: str = Field(min_length=1)
    modality: str
    obligor_alias: str
    obligee_alias: str
    action: str
    object_class: str
    object_raw_text: str
    temporal_raw: str | None = None
    condition_raws: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class GroundingTier(str, Enum):
    """Which mechanism proved span_text is real. See extraction.py's
    ground_candidates() docstring for the full Tier A/B design -- Tier C
    (Levenshtein-tolerant fuzzy matching, blueprint §6.3's "≤5% Levenshtein
    tolerance for OCR noise") is a deliberate, documented omission at this
    checkpoint, not a gap: a small edit distance can flip a modality
    ("shall" -> "shall not" is ~2% of a 200-char clause) and OCR noise is
    already surfaced separately via segments.ocr_confidence (V14) /
    LOW_OCR_CONFIDENCE, which doesn't carry this hazard.
    """

    EXACT = "EXACT"
    NORMALIZED = "NORMALIZED"


class RejectionReason(str, Enum):
    """Why a candidate never became a GroundedCandidate. Every rejection is
    recorded (agent_runs.node_trace), never silently dropped -- §13.8 says
    "discard silently, log as FP," which this codebase reads as "never
    surfaced as an obligation," not "unrecorded." A recorded rejection is a
    false-positive signal with a prompt_version attached; throwing it away
    would make the extractor un-evaluable.
    """

    SCHEMA_INVALID = "SCHEMA_INVALID"  # raw LLM output didn't even parse as LLMCandidate
    EMPTY_SPAN = "EMPTY_SPAN"
    SPAN_NOT_FOUND = "SPAN_NOT_FOUND"
    AMBIGUOUS_SPAN = "AMBIGUOUS_SPAN"
    NESTED_FIELD_NOT_IN_SPAN = "NESTED_FIELD_NOT_IN_SPAN"


@dataclass(frozen=True)
class GroundedCandidate:
    """A candidate that survived span grounding. Everything under `source`
    is a mechanically verified fact (segment.text[char_start:char_end] is
    literally what's stored, by construction -- see extraction.py); every
    other field is still an unverified LLM guess, unchanged from
    LLMCandidate, carried forward for the (not-yet-built) IR Compiler stage
    to structure and typecheck.
    """

    llm_candidate: LLMCandidate
    source: SourceRef
    grounding_tier: GroundingTier


@dataclass(frozen=True)
class RejectedCandidate:
    """A candidate that did not survive grounding (or never reached it,
    for SCHEMA_INVALID). `llm_candidate` is None only for SCHEMA_INVALID,
    where the raw response didn't validate into an LLMCandidate at all --
    `raw_detail` carries whatever diagnostic is available instead.
    """

    reason: RejectionReason
    detail: str
    segment_id: str
    llm_candidate: LLMCandidate | None = None
