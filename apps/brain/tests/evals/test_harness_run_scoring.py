"""The scoring driver's own guarantees, each planted individually.

These cover the five things run_scoring.py's docstring names as ways the run
could quietly lie (W1-W5) plus W6's miss diagnosis and report.py's G5 short-run
rule. Pure where possible: only the functions that genuinely need Postgres are
left out, and they are exercised by the real end-to-end run instead.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from obligo_brain.compiler import ast

from evals.harness import cassette as cassette_mod
from evals.harness import registry as registry_mod, report as report_mod
from evals.harness import run_scoring as rs
from evals.harness.score import Outcome

GOLD_DIR = Path(__file__).resolve().parents[2] / "evals" / "goldens"


def _obl(char_start: int, char_end: int, reg) -> ast.Obligation:
    return ast.Obligation(
        modality="MUST", action="PROVIDE",
        obligor=ast.ResolvedParty(party_id="p1",
                                  canonical_name=reg.resolve("Vendor").canonical_name),
        obligee=ast.ResolvedParty(party_id="p2",
                                  canonical_name=reg.resolve("AT&T").canonical_name),
        object=ast.ObjectRef(class_="technical_support", raw_text="technical assistance"),
        temporal=None, conditions=(),
        source=ast.SourceRef(segment_id="seg", char_start=char_start, char_end=char_end),
        confidence=0.9, underspecified=False, missing_fields=(),
    )


@pytest.fixture(scope="module")
def c03_gold() -> dict:
    return json.loads((GOLD_DIR / "batch01" / "items" / "C03-01.json").read_text())


@pytest.fixture(scope="module")
def c03_reg():
    return registry_mod.load("C03")


# --- W5: this run's compile figure is not criterion 1b ----------------------

def test_compile_success_is_labelled_as_not_criterion_1b():
    stats = rs.compile_success_not_criterion_1b(
        [rs.SegmentRun("S", 1, typechecked=[object()], n_quarantined=1, n_rejected=2)]
    )
    assert "NOT criterion 1b" in stats["label"]
    assert "Unmeasured" in stats["label"]
    assert stats["compiled_over_grounded"].startswith("1/2")


def test_compile_success_denominator_excludes_grounding_rejections():
    """Rejected-at-grounding candidates never reached the compiler, so counting
    them in a COMPILE success rate would understate it against a different
    stage's failures."""
    stats = rs.compile_success_not_criterion_1b(
        [rs.SegmentRun("S", 1, typechecked=[object()], n_quarantined=0, n_rejected=99)]
    )
    assert stats["compiled_over_grounded"].startswith("1/1")


# --- input integrity --------------------------------------------------------

def test_mixed_guideline_stamps_are_refused():
    """PLANTED: scoring 18 items as one set when they were annotated under
    different rulesets silently mixes two questions."""
    items = [{"guideline_version": "v0.28"}, {"guideline_version": "v0.25"}]
    with pytest.raises(ValueError, match="conforming pass"):
        rs.guideline_version_from_items(items)


def test_a_single_guideline_stamp_is_returned():
    assert rs.guideline_version_from_items(
        [{"guideline_version": "v0.28"}, {"guideline_version": "v0.28"}]) == "v0.28"


def test_disagreeing_segment_text_is_fatal():
    """PLANTED: two items claiming the same segment_id with different text means
    one of them was scored against input the model never saw."""
    items = [
        {"item_id": "A", "segment_id": "S", "doc_id": "D", "segment_text": "one"},
        {"item_id": "B", "segment_id": "S", "doc_id": "D", "segment_text": "two"},
    ]
    with pytest.raises(ValueError, match="disagree"):
        rs.segments_from_items(items)


def test_the_real_gold_set_has_consistent_segments_and_one_guideline_stamp():
    items = rs.load_gold_items()
    assert len(items) == 18
    assert len(rs.segments_from_items(items)) == 12
    assert rs.guideline_version_from_items(items) == "v0.28"


# --- W6: a MISSED says which kind of missed it is ---------------------------

def test_missed_with_no_overlapping_prediction_is_diagnosed_as_such(c03_gold, c03_reg):
    """n_quarantined is non-zero but NO quarantined span is supplied, so there is
    no evidence the clause was extracted -- NOT_EXTRACTED is correct here."""
    sr = rs.SegmentRun("C03-192", 1, typechecked=[], n_quarantined=1, n_rejected=0)
    scores, unexpected = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 2000)
    sc = scores[c03_gold["item_id"]]
    assert sc.outcome is Outcome.MISSED
    assert sc.detail["miss_kind"] == "NOT_EXTRACTED"
    assert unexpected == []


def test_missed_from_a_wide_boundary_is_diagnosed_as_below_threshold(c03_gold, c03_reg):
    """PLANTED, and modelled on a REAL observation: C22-01's gold span is
    [22:128] while the model predicted [22:529] -- identical start, 4x the
    length, IoU 0.21. Reporting that as a plain MISSED would read as an
    extraction failure when it is a granularity mismatch."""
    gs, ge = c03_gold["span_char_start"], c03_gold["span_char_end"]
    wide = _obl(gs, ge + 4 * (ge - gs), c03_reg)
    sr = rs.SegmentRun("C03-192", 1, typechecked=[wide], n_quarantined=0, n_rejected=0)
    scores, unexpected = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 5000)
    sc = scores[c03_gold["item_id"]]
    assert sc.outcome is Outcome.MISSED
    assert sc.detail["miss_kind"] == "BELOW_IOU_THRESHOLD"
    assert float(sc.detail["best_iou"]) == pytest.approx(0.2, abs=0.05)
    assert len(unexpected) == 1, "the unaligned wide span is still an UNEXPECTED"


# --- W1: quarantined/rejected candidates are not predictions ----------------

def test_a_quarantined_candidate_never_becomes_an_unexpected(c03_gold, c03_reg):
    """W1: only typechecked obligations are predictions. A quarantined candidate
    has no ast.Obligation, so it can be neither aligned nor a false positive --
    counting it would invent one."""
    sr = rs.SegmentRun("C03-192", 1, typechecked=[], n_quarantined=5, n_rejected=5)
    scores, unexpected = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 2000)
    assert unexpected == []
    assert scores[c03_gold["item_id"]].outcome is Outcome.MISSED


def test_an_aligned_prediction_is_scored_rather_than_missed(c03_gold, c03_reg):
    good = _obl(c03_gold["span_char_start"], c03_gold["span_char_end"], c03_reg)
    sr = rs.SegmentRun("C03-192", 1, typechecked=[good], n_quarantined=0, n_rejected=0)
    scores, unexpected = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 2000)
    assert scores[c03_gold["item_id"]].outcome is Outcome.FULLY_CORRECT
    assert unexpected == []


# --- W3 / G5: section 6.1's short-run rule ----------------------------------

def test_an_unexplained_short_run_is_refused_by_the_report():
    """PLANTED: this is the failure mode section 6.1 exists to prevent -- a run
    silently dropped and reported as though the item were scored normally."""
    runs = {"A-01": [Outcome.FULLY_CORRECT] * 3, "B-01": [Outcome.PARTIAL]}
    gold = {"A-01": {"known_gaps": []}, "B-01": {"known_gaps": []}}
    with pytest.raises(ValueError, match="no reason given"):
        report_mod.build(runs, gold)


def test_an_explained_short_run_is_accepted_and_states_itself_inline():
    runs = {"A-01": [Outcome.FULLY_CORRECT] * 3, "B-01": [Outcome.PARTIAL, Outcome.PARTIAL]}
    gold = {"A-01": {"known_gaps": []}, "B-01": {"known_gaps": []}}
    rep = report_mod.build(runs, gold, short_run_reasons={"B-01": "provider refused run 3"})
    rendered = rep.render()
    assert [i.item_id for i in rep.short_run_items] == ["B-01"]

    # Section 6.1 requires the caveat where the figure appears, so assert it on the
    # PER-ITEM table line specifically -- the summary block above it also says so,
    # and matching the first "B-01" line would pass on the summary alone while the
    # per-item row stayed silent.
    lines = rendered.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Per item"))
    b_line = next(l for l in lines[start:] if l.strip().startswith("B-01"))
    assert "2 RUNS, not 3" in b_line, "the run count must appear on the item's OWN line (§6.1)"
    assert "provider refused run 3" in b_line

    summary_line = next(l for l in lines[:start] if l.strip().startswith("B-01"))
    assert "2 runs, not 3" in summary_line, "and again in the short-run summary block"


def test_a_short_run_item_still_counts_in_criterion_2s_denominator():
    """v0.30's reconciliation: deferring to G2 keeps the item honestly scored and
    INSIDE the denominator, rather than an undefined status a later reader must
    improvise a treatment for."""
    runs = {"A-01": [Outcome.FULLY_CORRECT] * 3, "B-01": [Outcome.PARTIAL, Outcome.PARTIAL]}
    gold = {"A-01": {"known_gaps": []}, "B-01": {"known_gaps": []}}
    rep = report_mod.build(runs, gold, short_run_reasons={"B-01": "r"})
    assert rep.criterion2_all_items == (1, 2)


def test_n2_disagreement_resolves_to_the_worst_outcome_per_g2():
    """Section 6.1 as written at v0.29 said 'no modal outcome'; v0.30 defers to
    G2. This pins the reconciled behaviour so the contradiction cannot silently
    return."""
    modal, unstable = report_mod.modal_outcome([Outcome.FULLY_CORRECT, Outcome.MISSED])
    assert modal is Outcome.MISSED
    assert unstable is True


# --- W4: the dual denominator passes through untouched ----------------------

def test_both_denominators_are_rendered_and_the_in_force_one_is_no_known_gaps():
    """W4 still holds -- this module computes NEITHER figure and must never pick
    one -- but which figure is THE criterion changed at guideline v0.33 (section
    9.1). Both are still always emitted and always labelled; report.py's G3 owns
    the labelling, and this asserts run_scoring passes it through untouched."""
    runs = {"A-01": [Outcome.FULLY_CORRECT], "B-01": [Outcome.PARTIAL]}
    gold = {"A-01": {"known_gaps": []}, "B-01": {"known_gaps": ["mutual_obligation"]}}
    rendered = report_mod.build(runs, gold).render()
    assert "CRITERION 2 (IN FORCE, \u00a79.1 \u2014 len(known_gaps)==0)" in rendered
    assert "Reported alongside, over ALL items" in rendered
    assert "RECOMMENDED, NOT IN FORCE" not in rendered


# --- stale cassettes must not be silently skipped ---------------------------

def test_available_runs_propagates_a_stale_cassette_rather_than_skipping_it(tmp_path):
    """PLANTED: a stale cassette treated as a MISSING run would quietly shrink the
    run count and score the item over fewer runs -- exactly the short-run state
    section 6.1 requires a stated reason for, arrived at by accident."""
    cassette_mod.write(cassette_mod.Cassette(
        segment_id="S-001", run=1, model_id="old-model", prompt_version="v3",
        segment_sha256="0" * 64, guideline_version="v0.28",
        recorded_at="2026-01-01T00:00:00+00:00", responses=(),
    ), root=tmp_path)
    with pytest.raises(cassette_mod.StaleCassette):
        rs.available_runs("S-001", "some text", model_id="new-model", prompt_version="v3",
                          guideline_version="v0.28", root=tmp_path)


def test_available_runs_reports_only_runs_that_exist(tmp_path):
    text = "hello"
    import hashlib
    cassette_mod.write(cassette_mod.Cassette(
        segment_id="S-001", run=2, model_id="m", prompt_version="v3",
        segment_sha256=hashlib.sha256(text.encode()).hexdigest(),
        guideline_version="v0.28", recorded_at="2026-01-01T00:00:00+00:00", responses=(),
    ), root=tmp_path)
    assert rs.available_runs("S-001", text, model_id="m", prompt_version="v3",
                             guideline_version="v0.28", root=tmp_path) == [2]


# --- W6 refined: a compile-stage failure is not an extraction failure --------

class _FakeQuarantined:
    def __init__(self, start: int, end: int):
        self.candidate = type("C", (), {"source": ast.SourceRef(
            segment_id="seg", char_start=start, char_end=end)})()


def test_a_quarantined_candidate_on_the_gold_span_is_not_reported_as_not_extracted(
        c03_gold, c03_reg):
    """PLANTED, from a REAL observation: E01-01 and E03-01 each had a candidate
    quarantined at IoU 1.000 -- a PERFECT span -- and C04-03 at 0.988. Labelling
    those 'no prediction' reads a compiler rejection as an extraction miss and
    points the next investigation at entirely the wrong stage."""
    gs, ge = c03_gold["span_char_start"], c03_gold["span_char_end"]
    sr = rs.SegmentRun("C03-192", 1, typechecked=[], n_quarantined=1, n_rejected=0,
                       quarantined_spans=[(gs, ge)])
    scores, _ = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 5000)
    sc = scores[c03_gold["item_id"]]
    assert sc.outcome is Outcome.MISSED
    assert sc.detail["miss_kind"] == "EXTRACTED_THEN_QUARANTINED"
    assert sc.detail["best_iou"] == "1.000"
    assert "compile-stage failure" in sc.detail["alignment"]


def test_nothing_extracted_anywhere_is_reported_as_not_extracted(c03_gold, c03_reg):
    sr = rs.SegmentRun("C03-192", 1, typechecked=[], n_quarantined=0, n_rejected=0)
    scores, _ = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 5000)
    assert scores[c03_gold["item_id"]].detail["miss_kind"] == "NOT_EXTRACTED"


def test_a_quarantined_candidate_elsewhere_in_the_segment_does_not_claim_the_gold_span(
        c03_gold, c03_reg):
    """A quarantined candidate that does not overlap the gold span at all is NOT
    evidence the clause was extracted -- it is a different clause."""
    sr = rs.SegmentRun("C03-192", 1, typechecked=[], n_quarantined=1, n_rejected=0,
                       quarantined_spans=[(4000, 4200)])
    scores, _ = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 5000)
    assert scores[c03_gold["item_id"]].detail["miss_kind"] == "NOT_EXTRACTED"


def test_a_typechecked_alignment_still_wins_over_a_quarantined_candidate(c03_gold, c03_reg):
    """The quarantine branch must only fire when NO typechecked obligation aligned."""
    gs, ge = c03_gold["span_char_start"], c03_gold["span_char_end"]
    good = _obl(gs, ge, c03_reg)
    sr = rs.SegmentRun("C03-192", 1, typechecked=[good], n_quarantined=1, n_rejected=0,
                       quarantined_spans=[(gs, ge)])
    scores, _ = rs.score_segment_run(sr, [c03_gold], c03_reg, "x" * 5000)
    assert scores[c03_gold["item_id"]].outcome is Outcome.FULLY_CORRECT
