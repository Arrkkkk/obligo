"""Section 6's modal outcome and section 9's denominators, proven by planted
cases rather than by a well-behaved fixture.

The tie-break (G2) and the denominator split (G3) are both places a report
could overstate silently: rounding a three-way split toward the best outcome,
or emitting the not-in-force figure as though it were criterion 2.
"""

from __future__ import annotations

import pytest

from evals.harness.report import R6_CAVEAT, UnscoreableCandidate, build, modal_outcome
from evals.harness.score import Outcome

FC, PARTIAL, MISSED, UNEXPECTED = (
    Outcome.FULLY_CORRECT, Outcome.PARTIAL, Outcome.MISSED, Outcome.UNEXPECTED,
)


# --- G2: modal outcome and the tie-break ------------------------------------

@pytest.mark.parametrize(
    "outcomes,expected_modal,expected_unstable,why",
    [
        ([FC, FC, FC], FC, False, "unanimous"),
        ([PARTIAL, PARTIAL, PARTIAL], PARTIAL, False, "unanimous non-correct"),
        ([FC, FC, PARTIAL], FC, True, "clear majority, still unstable"),
        ([PARTIAL, FC, FC], FC, True, "majority regardless of order"),
        ([MISSED, MISSED, FC], MISSED, True, "majority is the worse outcome"),
        ([FC, PARTIAL, MISSED], MISSED, True, "NO unique mode -> worst, never the best"),
        ([FC, PARTIAL, UNEXPECTED], UNEXPECTED, True, "no mode -> worst of three"),
        ([FC, FC], FC, False, "two runs, unanimous"),
        ([FC, PARTIAL], PARTIAL, True, "two runs, tied -> worst"),
    ],
)
def test_modal_outcome_and_stability(outcomes, expected_modal, expected_unstable, why):
    modal, unstable = modal_outcome(outcomes)
    assert modal is expected_modal, why
    assert unstable is expected_unstable, why


def test_no_unique_mode_never_reports_the_best_outcome():
    """The specific way this could round in the pipeline's favour."""
    for combo in ([FC, PARTIAL, MISSED], [FC, MISSED, PARTIAL], [MISSED, FC, PARTIAL]):
        modal, unstable = modal_outcome(combo)
        assert modal is not FC
        assert unstable is True


def test_modal_outcome_rejects_zero_runs():
    with pytest.raises(ValueError):
        modal_outcome([])


# --- G3: the two denominators -----------------------------------------------

def _gold(item_id, gaps=(), vague=None):
    return {"item_id": item_id, "known_gaps": list(gaps), "vague_temporal_phrase": vague}


def test_denominators_split_on_known_gaps_membership_not_count():
    """§9: an item leaves the clean denominator when len(known_gaps) > 0. A
    two-tag item is treated identically to a one-tag item."""
    gold = {
        "A": _gold("A"),                                  # clean, correct
        "B": _gold("B"),                                  # clean, wrong
        "C": _gold("C", ("mutual_obligation",)),          # 1 tag, correct
        "D": _gold("D", ("mutual_obligation", "exception_unsupported")),  # 2 tags, correct
    }
    runs = {"A": [FC] * 3, "B": [PARTIAL] * 3, "C": [FC] * 3, "D": [FC] * 3}
    r = build(runs, gold)
    assert r.criterion2_all_items == (3, 4)
    assert r.criterion2_no_known_gaps == (1, 2), "only A and B are in the clean denominator"


def test_per_tag_counts_are_non_summable_and_deduplicated_per_item():
    gold = {
        "A": _gold("A", ("mutual_obligation", "exception_unsupported")),
        "B": _gold("B", ("mutual_obligation",)),
    }
    r = build({"A": [FC], "B": [FC]}, gold)
    assert r.per_tag_counts == {"exception_unsupported": 1, "mutual_obligation": 2}
    assert sum(r.per_tag_counts.values()) > len([i for i in r.items if i.known_gaps]), (
        "per-tag counts overlap by construction -- summing them is the §9 reporting error"
    )


def test_the_not_in_force_figure_is_labelled_as_such_in_the_render():
    r = build({"A": [FC]}, {"A": _gold("A")})
    text = r.render()
    assert "Criterion 2 (IN FORCE, all items)" in text
    assert "RECOMMENDED, NOT IN FORCE" in text


# --- G4: no predicted ceiling ------------------------------------------------

def test_render_states_that_no_ceiling_was_computed(monkeypatch):
    r = build({"A": [FC]}, {"A": _gold("A")})
    text = r.render()
    assert "NO PREDICTED CEILING IS STATED" in text
    assert "39-61" in text, "the superseded figure is named so it is not re-derived"
    for forbidden in ("expected ceiling:", "predicted ceiling:"):
        assert forbidden not in text.lower()


# --- G1 + R6: unexpected predictions carry their span ------------------------

def test_r6_caveat_is_emitted_verbatim_whenever_unexpected_is_reported():
    r = build({"A": [FC]}, {"A": _gold("A")})
    assert R6_CAVEAT in r.render()


def test_unscoreable_candidates_carry_span_text_for_triage():
    cand = UnscoreableCandidate(run=1, segment_id="E03-005", char_start=10, char_end=60,
                                span_text="each Order Forecast shall itemize the quantities")
    r = build({"A": [FC]}, {"A": _gold("A")}, unscoreable_candidates=[cand])
    text = r.render()
    assert "E03-005[10:60]" in text
    assert "shall itemize" in text, "the span must be triageable against the exclusion log"


# --- misc reporting figures ---------------------------------------------------

def test_vague_temporal_and_unscoreable_counts():
    gold = {
        "A": _gold("A", vague="promptly"),
        "B": _gold("B"),
        "C": _gold("C", ("redacted_clause",)),
    }
    r = build({k: [FC] for k in gold}, gold)
    assert r.vague_temporal_items == 1
    assert r.unscoreable_items == 1


def test_provenance_is_rendered():
    r = build({"A": [FC]}, {"A": _gold("A")},
              provenance={"guideline_version": "v0.28", "model_id": "llama-3.3-70b-versatile"})
    text = r.render()
    assert "guideline_version: v0.28" in text
    assert "model_id: llama-3.3-70b-versatile" in text
