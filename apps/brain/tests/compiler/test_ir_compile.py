"""Tests for the IR Compiler stage (compiler/ir_compile.py) -- deterministic
GroundedCandidate -> ast.Obligation compilation. No DB, no LLM, no network:
every input here is hand- or hypothesis-constructed.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_compile import (
    CompileFailure,
    CompileFailureReason,
    compile_candidate,
    compile_candidates,
)
from obligo_brain.graphs.state import GroundedCandidate, GroundingTier, LLMCandidate

_SEGMENT_ID = "00000000-0000-0000-0000-000000000001"


def _candidate(
    *,
    modality: str = "MUST",
    obligor_alias: str = "Vendor",
    obligee_alias: str = "Customer",
    action: str = "NOTIFY",
    object_class: str = "security incident",
    object_raw_text: str = "a Security Incident",
    temporal_raw: str | None = None,
    condition_raws: list[str] | None = None,
    confidence: float = 0.9,
) -> GroundedCandidate:
    llm = LLMCandidate(
        span_text="irrelevant to compilation -- grounding already happened",
        modality=modality,
        obligor_alias=obligor_alias,
        obligee_alias=obligee_alias,
        action=action,
        object_class=object_class,
        object_raw_text=object_raw_text,
        temporal_raw=temporal_raw,
        condition_raws=condition_raws or [],
        confidence=confidence,
    )
    return GroundedCandidate(
        llm_candidate=llm,
        source=ast.SourceRef(segment_id=_SEGMENT_ID, char_start=0, char_end=50),
        grounding_tier=GroundingTier.EXACT,
    )


# --- no temporal, no conditions: the baseline shape --------------------


def test_compiles_baseline_candidate_with_no_temporal_or_conditions():
    result = compile_candidate(_candidate())
    assert isinstance(result, ast.Obligation)
    assert result.modality == "MUST"
    assert result.obligor == ast.UnresolvedParty(alias="Vendor")
    assert result.obligee == ast.UnresolvedParty(alias="Customer")
    assert result.action == "NOTIFY"
    assert result.object == ast.ObjectRef(class_="security_incident", raw_text="a Security Incident")
    assert result.temporal is None
    assert result.conditions == ()
    assert result.source == ast.SourceRef(segment_id=_SEGMENT_ID, char_start=0, char_end=50)
    assert result.confidence == 0.9


def test_object_class_is_canonicalized_to_lower_snake_case():
    result = compile_candidate(_candidate(object_class="Security Incident"))
    assert isinstance(result, ast.Obligation)
    assert result.object.class_ == "security_incident"


def test_modality_and_action_are_case_normalized():
    result = compile_candidate(_candidate(modality="must", action="notify"))
    assert isinstance(result, ast.Obligation)
    assert result.modality == "MUST"
    assert result.action == "NOTIFY"


# --- each of the 5 frozen Temporal forms --------------------------------


def test_within_form():
    result = compile_candidate(
        _candidate(temporal_raw="within 5 business days of discovering a Security Incident")
    )
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.WithinTemporal(
        duration=ast.Duration(amount=5.0, unit="bd"),
        of=ast.UnresolvedTrigger(raw="discovering a Security Incident"),
    )


def test_within_form_bare_unit_letter():
    result = compile_candidate(_candidate(temporal_raw="within 5d of the Effective Date"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal.duration == ast.Duration(amount=5.0, unit="d")


def test_by_form_with_date_literal():
    result = compile_candidate(_candidate(temporal_raw="by 2026-12-31"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.ByTemporal(datetime=ast.ResolvedDate(date="2026-12-31"))


def test_by_form_with_alias():
    result = compile_candidate(_candidate(temporal_raw="by the Delivery Date"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.ByTemporal(datetime=ast.UnresolvedDate(raw="the Delivery Date"))


def test_every_form():
    result = compile_candidate(_candidate(temporal_raw="every 30 days"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.EveryTemporal(duration=ast.Duration(amount=30.0, unit="d"))


def test_during_form():
    result = compile_candidate(_candidate(temporal_raw="during 2026-01-01 .. 2026-12-31"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.DuringTemporal(
        start=ast.ResolvedDate(date="2026-01-01"), end=ast.ResolvedDate(date="2026-12-31")
    )


def test_relative_form_before():
    result = compile_candidate(_candidate(temporal_raw="before the Closing Date"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.RelativeToTriggerTemporal(
        direction="BEFORE", trigger=ast.UnresolvedTrigger(raw="the Closing Date")
    )


def test_relative_form_after():
    result = compile_candidate(_candidate(temporal_raw="after a Security Incident"))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.RelativeToTriggerTemporal(
        direction="AFTER", trigger=ast.UnresolvedTrigger(raw="a Security Incident")
    )


# --- adversarial: realistic verbatim-quoted phrasing, not textbook -------
# Found by testing against phrasing closer to what a verbatim quote of a
# real sentence looks like, not just hand-picked happy-path fixtures.


def test_by_form_tolerates_trailing_sentence_period_and_still_resolves():
    # A verbatim quote of "...deliver notice by 2026-01-01." legitimately
    # ends with a period that isn't part of the date. Without this, a
    # resolvable date silently downgraded to an unresolved alias instead of
    # ResolvedDate -- a real bug found via adversarial testing, not a
    # deliberate strictness boundary.
    result = compile_candidate(_candidate(temporal_raw="by 2026-01-01."))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.ByTemporal(datetime=ast.ResolvedDate(date="2026-01-01"))


def test_every_form_tolerates_trailing_sentence_period():
    result = compile_candidate(_candidate(temporal_raw="every 30 days."))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.EveryTemporal(duration=ast.Duration(amount=30.0, unit="d"))


def test_during_form_tolerates_trailing_sentence_period():
    result = compile_candidate(_candidate(temporal_raw="during 2026-01-01 .. 2026-12-31."))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.DuringTemporal(
        start=ast.ResolvedDate(date="2026-01-01"), end=ast.ResolvedDate(date="2026-12-31")
    )


def test_within_form_trailing_period_stays_verbatim_in_trigger_text():
    # The opposite case: a trailing period that IS meaningful (an
    # abbreviation inside free-text trigger content) must NOT be stripped --
    # only fixed-format tokens (dates, units) get period tolerance.
    result = compile_candidate(_candidate(temporal_raw="within 5d of Corp."))
    assert isinstance(result, ast.Obligation)
    assert result.temporal.of == ast.UnresolvedTrigger(raw="Corp.")


# --- unmappable temporal: reject the whole candidate ---------------------


def test_unclassifiable_temporal_rejects_whole_candidate():
    result = compile_candidate(_candidate(temporal_raw="promptly"))
    assert isinstance(result, CompileFailure)
    assert result.reason == CompileFailureReason.UNMAPPABLE_TEMPORAL
    assert "promptly" in result.detail


# Real, common contract phrasings deliberately NOT covered by the 5 closed-
# vocabulary keyword patterns -- the "strict over loose" scope decision this
# checkpoint made explicitly. Pinned here as regression tests, not left as
# an unexamined gap: each of these correctly rejects (UNMAPPABLE_TEMPORAL)
# rather than being silently misclassified or guessed at. Widening coverage
# to include synonyms ("no later than", "prior to", "on or before"),
# spelled-out numbers, or "calendar days" is a real, separate scope decision
# for a future checkpoint, not something to add quietly here.
@pytest.mark.parametrize(
    "phrase",
    [
        "no later than 5 business days after the date of discovery",
        "not later than 30 days following the Effective Date",
        "on or before December 31, 2026",
        "prior to the Closing Date",
        "within thirty (30) days of receipt",
        "annually",
        "within 5 calendar days of",
    ],
)
def test_realistic_out_of_scope_phrasings_reject_rather_than_misclassify(phrase):
    result = compile_candidate(_candidate(temporal_raw=phrase))
    assert isinstance(result, CompileFailure)
    assert result.reason == CompileFailureReason.UNMAPPABLE_TEMPORAL


def test_during_with_alias_termini_is_unmappable_not_guessed():
    # DURING only accepts two ISO date literals in this checkpoint -- see
    # ir_compile.py's _DURING_RE comment. Must fail loudly, not guess a
    # split of the alias text into two termini.
    result = compile_candidate(_candidate(temporal_raw="during the Term"))
    assert isinstance(result, CompileFailure)
    assert result.reason == CompileFailureReason.UNMAPPABLE_TEMPORAL


def test_none_temporal_raw_compiles_to_none_not_a_failure():
    result = compile_candidate(_candidate(temporal_raw=None))
    assert isinstance(result, ast.Obligation)
    assert result.temporal is None


# --- conditions: one atom per raw string, never AND/OR/NOT-parsed --------


def test_single_condition_raw_becomes_one_atom_predicate():
    result = compile_candidate(_candidate(condition_raws=["Customer has not cured the breach"]))
    assert isinstance(result, ast.Obligation)
    assert result.conditions == (
        ast.Condition(predicate=ast.AtomPredicate(raw="Customer has not cured the breach")),
    )


def test_multiple_condition_raws_become_multiple_conditions():
    result = compile_candidate(
        _candidate(condition_raws=["a Security Incident has occurred", "notice has not been waived"])
    )
    assert isinstance(result, ast.Obligation)
    assert len(result.conditions) == 2
    assert result.conditions[0].predicate == ast.AtomPredicate(raw="a Security Incident has occurred")
    assert result.conditions[1].predicate == ast.AtomPredicate(raw="notice has not been waived")


def test_condition_raw_containing_boolean_looking_words_is_still_one_atom():
    # "not later than" contains "not" but this is not a boolean NOT -- must
    # not be misinterpreted as predicate structure.
    result = compile_candidate(_candidate(condition_raws=["delivery is not later than agreed"]))
    assert isinstance(result, ast.Obligation)
    assert result.conditions == (
        ast.Condition(predicate=ast.AtomPredicate(raw="delivery is not later than agreed")),
    )


# --- PARSE_ERROR: the grammar is the closed-taxonomy authority -----------


def test_action_outside_closed_taxonomy_is_a_parse_error_not_pre_validated():
    result = compile_candidate(_candidate(action="LEVITATE"))
    assert isinstance(result, CompileFailure)
    assert result.reason == CompileFailureReason.PARSE_ERROR


def test_modality_outside_closed_taxonomy_is_a_parse_error():
    result = compile_candidate(_candidate(modality="MIGHT"))
    assert isinstance(result, CompileFailure)
    assert result.reason == CompileFailureReason.PARSE_ERROR


def test_compile_failure_carries_the_original_candidate_for_accounting():
    candidate = _candidate(temporal_raw="promptly")
    result = compile_candidate(candidate)
    assert isinstance(result, CompileFailure)
    assert result.candidate is candidate


# --- batch form: every input accounted for, nothing silently dropped -----


def test_compile_candidates_partitions_success_and_failure():
    ok = _candidate()
    bad = _candidate(temporal_raw="promptly")
    compiled, failed = compile_candidates([ok, bad])
    assert len(compiled) == 1
    assert len(failed) == 1
    assert failed[0].candidate is bad


# --- property test: WITHIN/EVERY duration classification round-trips ----
# (the closed-vocabulary classifier's own analog to test_properties.py's
# round-trip property for the grammar itself)

_UNIT_TOKENS = st.sampled_from(["h", "d", "bd", "w", "mo", "y"])
_POSITIVE_AMOUNT = st.integers(min_value=1, max_value=1000)


@given(amount=_POSITIVE_AMOUNT, unit=_UNIT_TOKENS, trigger=st.text(alphabet="abcdefgh ", min_size=1, max_size=20))
@settings(max_examples=100)
def test_within_duration_round_trips_for_every_unit(amount, unit, trigger):
    trigger = trigger.strip() or "x"
    raw = f"within {amount}{unit} of {trigger}"
    result = compile_candidate(_candidate(temporal_raw=raw))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.WithinTemporal(
        duration=ast.Duration(amount=float(amount), unit=unit),
        of=ast.UnresolvedTrigger(raw=trigger),
    )


@given(amount=_POSITIVE_AMOUNT, unit=_UNIT_TOKENS)
@settings(max_examples=100)
def test_every_duration_round_trips_for_every_unit(amount, unit):
    raw = f"every {amount}{unit}"
    result = compile_candidate(_candidate(temporal_raw=raw))
    assert isinstance(result, ast.Obligation)
    assert result.temporal == ast.EveryTemporal(duration=ast.Duration(amount=float(amount), unit=unit))
