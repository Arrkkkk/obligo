"""Proves ground_candidates() -- the single most important correctness
gate in this checkpoint (blueprint §21's acceptance criterion:
span-grounding rate exactly 100%, zero ungrounded obligations reach the
database, by construction). Pure function, no I/O, no LLM, no DB -- this
is why it gets the heaviest test suite of anything built in this
checkpoint.

Table-driven cases cover both grounding tiers, every rejection reason, and
-- most importantly -- the concrete adversarial case that justifies NOT
building Tier C (Levenshtein-tolerant fuzzy matching): a small edit
distance ("shall" -> "shall not") that inverts an obligation's meaning
must never be treated as "close enough."

Hypothesis properties close out two of test_properties.py's deferred
blueprint §19.3 properties -- "grounding invariant" (the stored span is
always a real slice of the segment) -- at the level where segment text
actually exists; the DSL-level parser test file explains why it can't
prove this itself.
"""

from __future__ import annotations

import string

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from obligo_brain.graphs.extraction import ground_candidates
from obligo_brain.graphs.state import GroundingTier, LLMCandidate, RejectionReason, SegmentRecord


def _candidate(span_text: str, **overrides) -> LLMCandidate:
    # Nested fields default to "" -- _is_grounded_substring treats an
    # empty needle as trivially satisfied, so a test only needs to
    # override the fields it actually cares about instead of hand-fitting
    # every field to whatever span_text it's using.
    defaults = dict(
        span_text=span_text,
        modality="MUST",
        obligor_alias="",
        obligee_alias="",
        action="NOTIFY",
        object_class="obligation",
        object_raw_text="",
        temporal_raw=None,
        condition_raws=[],
        confidence=0.9,
    )
    defaults.update(overrides)
    return LLMCandidate(**defaults)


def _segment(text: str, seg_id: str = "11111111-1111-1111-1111-111111111111") -> SegmentRecord:
    return SegmentRecord(id=seg_id, text=text)


# --- Table-driven cases ---------------------------------------------------


def test_exact_match_grounds_with_correct_offsets():
    segment = _segment("Vendor must notify Customer of a Security Incident within 5 days.")
    span = "Vendor must notify Customer of a Security Incident"
    candidate = _candidate(span, obligor_alias="Vendor", obligee_alias="Customer", object_raw_text="a Security Incident")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert rejected == []
    assert len(grounded) == 1
    g = grounded[0]
    assert g.grounding_tier == GroundingTier.EXACT
    assert segment.text[g.source.char_start : g.source.char_end] == span
    assert g.source.segment_id == segment.id


def test_whitespace_run_grounds_via_normalized_tier():
    segment = _segment("Vendor  must\nnotify Customer promptly.")
    span = "Vendor must notify Customer promptly."

    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert rejected == []
    assert len(grounded) == 1
    g = grounded[0]
    assert g.grounding_tier == GroundingTier.NORMALIZED
    assert segment.text[g.source.char_start : g.source.char_end] == "Vendor  must\nnotify Customer promptly."


def test_nbsp_grounds_via_normalized_tier():
    segment = _segment("Vendor must notify Customer.")
    span = "Vendor must notify Customer."

    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert len(grounded) == 1
    assert grounded[0].grounding_tier == GroundingTier.NORMALIZED


def test_smart_quotes_ground_via_normalized_tier():
    segment = _segment("Vendor must notify “the Customer” within 5 days.")
    span = 'Vendor must notify "the Customer" within 5 days.'

    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert len(grounded) == 1
    assert grounded[0].grounding_tier == GroundingTier.NORMALIZED


def test_em_dash_grounds_via_normalized_tier():
    segment = _segment("Vendor must notify Customer — in writing — within 5 days.")
    span = "Vendor must notify Customer - in writing - within 5 days."

    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert len(grounded) == 1
    assert grounded[0].grounding_tier == GroundingTier.NORMALIZED


def test_zero_width_character_grounds_via_normalized_tier():
    segment = _segment("Vendor must​ notify Customer.")
    span = "Vendor must notify Customer."

    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert len(grounded) == 1
    assert grounded[0].grounding_tier == GroundingTier.NORMALIZED


def test_multiple_exact_occurrences_are_ambiguous():
    segment = _segment("Vendor must pay. Vendor must pay. Something else.")

    grounded, rejected = ground_candidates(segment, [_candidate("Vendor must pay.")])

    assert grounded == []
    assert len(rejected) == 1
    assert rejected[0].reason == RejectionReason.AMBIGUOUS_SPAN


def test_hallucinated_span_is_rejected():
    segment = _segment("Vendor must notify Customer within 5 days.")

    grounded, rejected = ground_candidates(
        segment, [_candidate("Vendor must indemnify Customer for all damages.")]
    )

    assert grounded == []
    assert rejected[0].reason == RejectionReason.SPAN_NOT_FOUND


def test_paraphrase_is_rejected_not_fuzzy_matched():
    segment = _segment("The Vendor shall provide written notice to the Customer promptly.")
    # A plausible model paraphrase instead of a verbatim quote -- must be
    # rejected exactly like a hallucination, not partially credited.
    candidate = _candidate("Vendor must notify Customer promptly.")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.SPAN_NOT_FOUND


def test_modality_inverting_mutation_is_rejected_the_tier_c_argument_made_executable():
    """The concrete reason Tier C (Levenshtein-tolerant fuzzy matching,
    blueprint §6.3's "<=5% tolerance for OCR noise") is NOT built:
    "shall" -> "shall not" is a small edit distance relative to a full
    clause -- comfortably under a plausible 5% threshold -- and it
    inverts the obligation's meaning. This proves the exact/normalized
    design correctly refuses to ground the mutated claim; a fuzzy gate
    tuned for OCR noise would not.
    """
    segment = _segment("Vendor shall deliver the Deliverables by March 1, 2027.")
    candidate = _candidate("Vendor shall not deliver the Deliverables by March 1, 2027.")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.SPAN_NOT_FOUND


def test_span_overrunning_segment_is_rejected():
    segment = _segment("Vendor must notify Customer.")
    candidate = _candidate("Vendor must notify Customer. And also do more things.")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.SPAN_NOT_FOUND


def test_empty_span_is_rejected():
    segment = _segment("Vendor must notify Customer.")

    grounded, rejected = ground_candidates(segment, [_candidate("   ")])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.EMPTY_SPAN


def test_nested_field_not_in_span_is_rejected():
    segment = _segment("Vendor must notify Customer of a Security Incident.")
    span = "Vendor must notify Customer of a Security Incident."
    # A hallucinated party assignment riding along on an otherwise-real span.
    candidate = _candidate(span, obligor_alias="Acme Corp")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.NESTED_FIELD_NOT_IN_SPAN
    assert "obligor_alias" in rejected[0].detail


def test_condition_raw_not_in_span_is_rejected():
    segment = _segment("Vendor must notify Customer of a Security Incident.")
    span = "Vendor must notify Customer of a Security Incident."
    candidate = _candidate(span, condition_raws=["if the Term has not expired"])

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.NESTED_FIELD_NOT_IN_SPAN


def test_temporal_raw_not_in_span_is_rejected():
    segment = _segment("Vendor must notify Customer of a Security Incident.")
    span = "Vendor must notify Customer of a Security Incident."
    candidate = _candidate(span, temporal_raw="within 5 days")

    grounded, rejected = ground_candidates(segment, [candidate])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.NESTED_FIELD_NOT_IN_SPAN


def test_nested_field_tolerates_the_same_normalization_as_the_span():
    segment = _segment("Vendor must notify “the Customer” of a Security Incident.")
    span = 'Vendor must notify "the Customer" of a Security Incident.'
    # The model's own copy of a nested phrase can carry the same benign
    # quote-style variance as its copy of the full span.
    candidate = _candidate(span, obligee_alias='"the Customer"')

    grounded, rejected = ground_candidates(segment, [candidate])

    assert rejected == []
    assert len(grounded) == 1


def test_grounded_and_rejected_partition_all_inputs_and_preserve_identity():
    segment = _segment("Vendor must notify Customer. Vendor must pay Customer.")
    good = _candidate("Vendor must pay Customer.")
    bad = _candidate("Vendor must indemnify Customer.")  # not present at all

    grounded, rejected = ground_candidates(segment, [good, bad])

    assert len(grounded) == 1
    assert len(rejected) == 1
    assert grounded[0].llm_candidate is good
    assert rejected[0].llm_candidate is bad


def test_no_candidates_yields_two_empty_lists():
    segment = _segment("Vendor must notify Customer.")

    grounded, rejected = ground_candidates(segment, [])

    assert grounded == []
    assert rejected == []


# --- Hypothesis properties -------------------------------------------------

_ALPHABET = string.ascii_letters + string.digits + " .,"


@given(
    prefix=st.text(alphabet=_ALPHABET, max_size=15),
    span=st.text(alphabet=_ALPHABET, min_size=1, max_size=20),
    suffix=st.text(alphabet=_ALPHABET, max_size=15),
)
@settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=200, deadline=None)
def test_grounding_invariant_stored_span_is_always_a_real_slice_of_the_segment(prefix, span, suffix):
    """blueprint §19.3's 'grounding invariant': no obligation exits the
    pipeline whose span text isn't a substring of its segment.
    test_properties.py explicitly defers this property because the
    DSL-level parser it tests never receives segment text as input (see
    that file's own docstring table) -- this is where the property
    actually gets proven, at the layer that does.
    """
    assume(span.strip() != "")
    segment_text = prefix + span + suffix
    assume(segment_text.count(span) == 1)  # keep the property about correctness, not ambiguity

    segment = _segment(segment_text)
    grounded, rejected = ground_candidates(segment, [_candidate(span)])

    assert rejected == []
    g = grounded[0]
    assert segment.text[g.source.char_start : g.source.char_end] == span
    assert g.source.char_start == len(prefix)
    assert g.source.char_end == len(prefix) + len(span)


@given(segment_text=st.text(alphabet=_ALPHABET, max_size=40))
@settings(max_examples=100, deadline=None)
def test_a_span_absent_from_the_segment_is_always_rejected(segment_text):
    # "@" is outside _ALPHABET, so this literal can never occur in
    # segment_text by construction -- no assume() needed to guarantee it.
    absent_span = "@ABSENT_MARKER@"

    grounded, rejected = ground_candidates(_segment(segment_text), [_candidate(absent_span)])

    assert grounded == []
    assert rejected[0].reason == RejectionReason.SPAN_NOT_FOUND
