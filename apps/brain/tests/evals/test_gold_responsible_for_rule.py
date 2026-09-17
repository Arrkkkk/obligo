"""Regression tests for guideline §8.8.4 (v0.56) -- the `be`/`remain responsible`/`liable
for X` ruling, and for the two things about it that are easiest to undo by accident.

WHAT IS ACTUALLY AT RISK HERE, and why these are the tests rather than a prose assertion:

  (1) THE RULING'S BEHAVIOURAL EFFECT. Ruling `C14-076` candidate 1 NOT_OBLIGATION_BEARING
      only means anything downstream because the span lands in `not_annotatable`, where
      align.py sets aside a prediction covering it (§4.4: neither, in either direction).
      The model DOES emit a candidate at that span on run 1, so the effect is live and not
      hypothetical -- before the ruling it was counted as an UNEXPECTED prediction.

  (2) THE THING THE RULING DELIBERATELY DID NOT DO. §8.8.4 states against interest that
      excluding candidate 1 does NOT rescue `C14-076`'s band: candidate 2 alone takes the
      segment to 4 obligation-bearing clauses, because its two verbs carry DIFFERENT
      obligors. A later session reading "candidate 1 is settled" could easily flip the
      segment to RECONCILED and quietly un-escalate a live band question. That is pinned.

  (3) THE EVIDENCE THE RULE RESTS ON. The rule is drafted against `C03-024` -- and its
      whole shape comes from `C03-024` and `C03-016` landing on OPPOSITE sides while
      sitting in the same document with the same obligor. If the classifier ever stops
      reproducing that pair, §8.8.4's central worked example has gone out from under it.

GROUP (3) DOES NOT RUN IN CI, AND THAT IS STATED HERE RATHER THAN LEFT TO BE INFERRED FROM A
SKIP COUNT. Those five tests rebuild the 1,547-segment pool from `.corpus/`, which is
git-ignored (28 source documents plus CUAD's 106MB zip, re-acquired on demand and
hash-verified by `evals/corpus.py fetch`). No other test in `tests/evals/` touches the raw
corpus -- every one of them reads only committed artifacts -- so this file is the first to
need the guard, and it is `skipif`, not a silent no-op.

**Why that is acceptable, stated precisely.** Groups (1) and (2) are the tests that protect
anything a scoring run can see -- the `not_annotatable` wiring, the band staying escalated,
no item restamped -- and they read only committed gold JSON, so they run everywhere. Group
(3) pins a measurement over source documents that CI does not have; it is checked locally,
and the first run of this file recorded 13 passed with the corpus present. **Do not read a
green CI as having re-verified §8.8.4's corpus evidence** -- it verifies the ruling's effect
on the gold set, which is a different and smaller claim. This distinction is exactly the one
CLAUDE.md's own audit entry names, where a checkpoint's "0 failed... clean" turned out to be
a without-DB-env number with 33 tests silently skipping.
"""
import json
import pathlib
import sys

import pytest

from evals.harness import run_scoring as rs

GOLDENS = pathlib.Path(rs.__file__).resolve().parents[1] / "goldens"
SEGMENT = GOLDENS / "batch02" / "segments" / "C14-076.json"

CANDIDATE_1 = (
    "Each party will be solely responsible for any and all taxes imposed thereon, "
    "including, without limitation, all income taxes, sales taxes, goods and services taxes."
)
CANDIDATE_2 = (
    "Israel value added tax shall be added, if applicable, to all amounts payable hereunder "
    "and will be paid against submission of appropriate tax invoices."
)


@pytest.fixture(scope="module")
def segment():
    return json.loads(SEGMENT.read_text())


def _disposition(segment, span_text):
    hits = [d for d in segment["dispositions"] if d["span_text"] == span_text]
    assert len(hits) == 1, f"expected exactly one disposition for the span, got {len(hits)}"
    return hits[0]


# --- (1) the ruling's behavioural effect ------------------------------------

def test_candidate_1_is_ruled_not_obligation_bearing_under_8_8_4(segment):
    d = _disposition(segment, CANDIDATE_1)
    assert d["disposition"] == "NOT_OBLIGATION_BEARING"
    assert "8.8.4" in d["rule"]


def test_candidate_1s_span_actually_reaches_the_scorer_as_not_annotatable(segment):
    """The disposition is inert unless it is ALSO in `not_annotatable` -- that array, not
    `dispositions`, is the one run_scoring.load_not_annotatable() reads (§2.7's own schema
    note). A ruling recorded in only one of the two places is a ruling with no effect."""
    d = _disposition(segment, CANDIDATE_1)
    spans = rs.load_not_annotatable(GOLDENS)["C14-076"]
    assert (d["span_char_start"], d["span_char_end"]) in spans


def test_the_ruled_span_is_where_the_segment_text_says_it_is(segment):
    """Guards the char offsets themselves: an off-by-N here would silently set aside the
    wrong region of the segment, which no other assertion in this file would catch."""
    d = _disposition(segment, CANDIDATE_1)
    text = rs.segments_from_items(rs.load_gold_items(GOLDENS))["C14-076"][1]
    assert text[d["span_char_start"]:d["span_char_end"]] == CANDIDATE_1


# --- (2) what the ruling deliberately did NOT settle -------------------------

def test_candidate_2_is_still_ambiguous_and_the_band_question_is_still_open(segment):
    """§8.8.4's against-interest disclosure, made mechanical. Candidate 2 ALONE takes the
    segment over §2's 1-3 band (different obligors on its two verbs), so ruling candidate 1
    settles nothing about eligibility -- and `C14-01`/`C14-02`'s locked status stays open."""
    assert _disposition(segment, CANDIDATE_2)["disposition"] == "AMBIGUOUS"
    assert segment["reconciliation"]["status"] == "ESCALATED_BAND_RISK"


def test_candidate_2_is_not_in_not_annotatable(segment):
    """An AMBIGUOUS span is an open reviewer question, not a settled non-item; putting it in
    the scoring array would resolve it silently. §2.7 states this for AMBIGUOUS in terms."""
    d = _disposition(segment, CANDIDATE_2)
    spans = rs.load_not_annotatable(GOLDENS)["C14-076"]
    assert (d["span_char_start"], d["span_char_end"]) not in spans


def test_the_clause_count_dropped_by_exactly_one_and_the_items_did_not_move(segment):
    r = segment["reconciliation"]
    assert r["obligation_bearing_clauses"] == 3   # was 4; candidate 1 removed
    assert r["items_annotated"] == 2              # C14-01, C14-02 -- untouched


def test_no_item_was_restamped_by_this_ruling():
    """§8.8.4 is a §10.2 Part 1 clarification whose measured conforming cost is ONE locked
    SEGMENT and ZERO locked ITEMS. `C14-01`/`C14-02` keep their v0.28 stamps: restamping
    them would stale three cassettes for a ruling that does not touch either item."""
    items = {i["item_id"]: i for i in rs.load_gold_items(GOLDENS)}
    assert items["C14-01"]["guideline_version"] == "v0.28"
    assert items["C14-02"]["guideline_version"] == "v0.28"


def test_the_set_is_unchanged_at_35_items_over_22_segments():
    items = rs.load_gold_items(GOLDENS)
    assert len(items) == 35
    assert len(rs.segments_from_items(items)) == 22


# --- (3) the evidence the rule rests on --------------------------------------
#
# Corpus-gated: see the module docstring. `.corpus/` is git-ignored and absent in CI, so
# these five are SKIPPED there and run only where the corpus has been fetched.

CORPUS = pathlib.Path(rs.__file__).resolve().parents[4] / ".corpus"

corpus_required = pytest.mark.skipif(
    not (CORPUS / "cuad").is_dir(),
    reason=(
        "needs the git-ignored .corpus/ working copy (28 documents + CUAD zip; fetch with "
        "`python -m evals.corpus fetch`). §8.8.4's corpus evidence is therefore NOT "
        "re-verified by CI -- see this module's docstring, which says so rather than "
        "leaving it to be inferred from a skip count."
    ),
)


# No marker here: pytest markers are inert on a fixture. The guard belongs on each test,
# and the fixture body only ever runs for a test that was not skipped.
@pytest.fixture(scope="module")
def classifier():
    sys.path.insert(0, str(GOLDENS / "holdout" / "band_risk"))
    import responsible_for_rule as rr
    return rr


@corpus_required
def test_the_c03_contrast_pair_still_lands_on_opposite_sides(classifier):
    """§8.8.4's central worked example. `C03-016` ('...any and all OBLIGATIONS of any such
    Affiliate') and `C03-024` ('...such Affiliate's FAILURE to satisfy its obligations') are
    the same document, the same obligor and the same subject -- and the rule turns entirely
    on them coming out differently. If they ever agree, the section has lost its anchor."""
    _, _, rows = classifier.classify_all()
    cls = {seg: (ov or c)
           for seg, _, side, c, _, _, ov in rows
           if side == "AFFIRM" and seg in ("C03-016", "C03-024")}
    assert cls == {"C03-016": "RENDER", "C03-024": "ABSORB"}


@corpus_required
def test_candidate_1_classifies_absorb_like_the_ruling_says(classifier):
    _, _, rows = classifier.classify_all()
    got = [(ov or c) for seg, _, side, c, _, _, ov in rows
           if seg == "C14-076" and side == "AFFIRM"]
    assert got == ["ABSORB"]


@corpus_required
def test_c02_045_the_falsified_near_miss_classifies_render(classifier):
    """The citation §8.8.4 overturns: `C02-045` reads as 'almost identical language' and is
    RENDER ('the timely PAYMENT of ... TO the applicable Governmental Authority'), locked as
    C02-04 with action PAY. Near-identical construction, opposite complement."""
    _, _, rows = classifier.classify_all()
    got = [(ov or c) for seg, _, side, c, _, _, ov in rows
           if seg == "C02-045" and side == "AFFIRM"]
    assert got == ["RENDER"]


@corpus_required
def test_polarity_is_a_prior_filter_that_the_complement_axis_does_not_answer_for(classifier):
    """`C04-163`'s complement is an act nominalisation -- it reads RENDER -- yet the clause
    is EXCLUDED, because §8.8.1's polarity filter removes it first. The two axes are
    independent, and an earlier draft of the classifier's own known-answer block asserted
    the affirmative class here and correctly FAILED. Pinned so the axes stay separate."""
    _, _, rows = classifier.classify_all()
    got = [(c, side) for seg, _, side, c, _, _, _ in rows if seg == "C04-163"]
    assert got == [("RENDER", "NEGATIVE")]


@corpus_required
def test_the_classifiers_known_answer_gate_still_passes(classifier):
    """Standing Principle 7: the totals are not evidence unless the gate passes. Runs the
    same 11-case check the script runs before printing anything."""
    _, _, rows = classifier.classify_all()
    for seg, (want_head, want_cls, want_side, why) in classifier.KNOWN.items():
        got = [(h, c, s) for sg, _, s, c, h, _, _ in rows if sg == seg]
        assert (want_head, want_cls, want_side) in got, f"{seg}: {why} -- got {got}"
