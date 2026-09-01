"""Section 5's conjunctive predicate and sections 4.1/4.2's alignment, proven clause
by clause rather than by a handful of fixtures that happen to cover them.

Every one of section 5's eight clauses gets its own named test that plants a
defect violating THAT CLAUSE ALONE and asserts the outcome flips to PARTIAL
with exactly that clause failing. A suite that only checks "a broken
obligation scores PARTIAL" would pass even if two clauses were wired to the
same comparison, or if one were never evaluated at all.

No database and no network: the scorer is pure over
(gold item, ast.Obligation, DocumentRegistry).
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from obligo_brain.compiler import ast

from evals.harness import align, registry as registry_mod, score

GOLD = Path(__file__).resolve().parents[2] / "evals" / "goldens" / "batch01" / "items" / "C03-01.json"


@pytest.fixture(scope="module")
def gold() -> dict:
    return json.loads(GOLD.read_text())


@pytest.fixture(scope="module")
def reg() -> registry_mod.DocumentRegistry:
    return registry_mod.load("C03")


@pytest.fixture(scope="module")
def other_party() -> registry_mod.Party:
    """A party from a DIFFERENT document's registry -- a genuinely wrong
    identity, not merely a different spelling of the right one."""
    return registry_mod.load("C02").resolve("AMAG")


@pytest.fixture
def baseline(reg: registry_mod.DocumentRegistry) -> ast.Obligation:
    return ast.Obligation(
        modality="MUST",
        action="PROVIDE",
        obligor=ast.ResolvedParty(party_id="p1", canonical_name=reg.resolve("Vendor").canonical_name),
        obligee=ast.ResolvedParty(party_id="p2", canonical_name=reg.resolve("AT&T").canonical_name),
        object=ast.ObjectRef(class_="technical_support", raw_text="technical assistance"),
        temporal=None,
        conditions=(),
        source=ast.SourceRef(segment_id="seg", char_start=0, char_end=100),
        confidence=0.9,
        underspecified=False,
        missing_fields=(),
    )


def _assert_only(clause: str, gold: dict, obligation: ast.Obligation, reg) -> None:
    result = score.score_item(gold, obligation, reg)
    assert result.outcome is score.Outcome.PARTIAL, result.detail
    assert result.failed == [clause], f"expected only {clause!r} to fail, got {result.failed}"


def test_baseline_is_fully_correct(gold, baseline, reg):
    result = score.score_item(gold, baseline, reg)
    assert result.outcome is score.Outcome.FULLY_CORRECT, result.detail
    assert set(result.clauses) == set(score.CLAUSES), "every clause must be evaluated, not skipped"


# --- section 5, clause by clause -------------------------------------------

def test_clause1_modality_flips_alone(gold, baseline, reg):
    _assert_only("modality", gold, dataclasses.replace(baseline, modality="MAY"), reg)


def test_clause2_action_outside_accept_set_flips_alone(gold, baseline, reg):
    _assert_only("action", gold, dataclasses.replace(baseline, action="DELETE"), reg)


def test_clause3_obligor_wrong_party_flips_alone(gold, baseline, reg, other_party):
    wrong = ast.ResolvedParty(party_id="pX", canonical_name=other_party.canonical_name)
    _assert_only("obligor", gold, dataclasses.replace(baseline, obligor=wrong), reg)


def test_clause4_obligee_wrong_party_flips_alone(gold, baseline, reg, other_party):
    wrong = ast.ResolvedParty(party_id="pY", canonical_name=other_party.canonical_name)
    _assert_only("obligee", gold, dataclasses.replace(baseline, obligee=wrong), reg)


def test_clause5_object_class_outside_accept_set_flips_alone(gold, baseline, reg):
    obj = ast.ObjectRef(class_="unrelated_thing", raw_text="x")
    _assert_only("object_class", gold, dataclasses.replace(baseline, object=obj), reg)


def test_clause6_temporal_flips_alone(gold, baseline, reg):
    temporal = ast.RelativeToTriggerTemporal(
        direction="AFTER", trigger=ast.UnresolvedTrigger(raw="the Effective Date")
    )
    _assert_only("temporal", gold, dataclasses.replace(baseline, temporal=temporal), reg)


def test_clause7_conditions_flips_alone(gold, baseline, reg):
    conds = (ast.Condition(predicate=ast.AtomPredicate(raw="if requested")),)
    _assert_only("conditions", gold, dataclasses.replace(baseline, conditions=conds), reg)


def test_clause8_underspecified_flips_alone(gold, baseline, reg):
    _assert_only("underspecified", gold, dataclasses.replace(baseline, underspecified=True), reg)


# --- the v0.28 party-comparison rule ---------------------------------------

def test_resolved_party_compares_by_identity_not_by_span_alias(gold, baseline, reg):
    """Gold holds the span alias ('Vendor'); a correct extraction that resolved
    the party carries only a party_id and canonical name. Clause 3 must pass on
    identity, because the model's own alias is discarded by ResolvedParty and is
    not recoverable from PipelineResult."""
    amended = dict(gold, obligor="Commnet Wireless, LLC")
    assert score.score_item(amended, baseline, reg).clauses["obligor"] is True


def test_absent_matches_absent_and_a_resolved_party_does_not(gold, baseline, reg):
    amended = dict(gold, obligee="ABSENT")
    absent_pred = dataclasses.replace(baseline, obligee=ast.UnresolvedParty(alias=""))
    assert score.score_item(amended, absent_pred, reg).clauses["obligee"] is True
    assert score.score_item(amended, baseline, reg).clauses["obligee"] is False


# --- clause 7's comparison rule ---------------------------------------------

def _with_conditions(baseline: ast.Obligation, *raws: str) -> ast.Obligation:
    return dataclasses.replace(
        baseline,
        conditions=tuple(ast.Condition(predicate=ast.AtomPredicate(raw=r)) for r in raws),
    )


@pytest.mark.parametrize(
    "predicted,expected,why",
    [
        (("upon    notice", "if the Customer requests"), True, "order-insensitive, whitespace-normalized"),
        (("if the Customer requests", "upon notice"), True, "same set, source order"),
        (("upon notice", "IF THE CUSTOMER REQUESTS"), False, "case is NOT folded (section 17)"),
        (("upon notice",), False, "count-sensitive: one of two"),
        (("upon notice", "if the Customer requests", "extra"), False, "count-sensitive: three of two"),
    ],
)
def test_clause7_condition_set_semantics(gold, baseline, reg, predicted, expected, why):
    amended = dict(gold, conditions=["if  the   Customer requests", "upon notice"])
    got = score.score_item(amended, _with_conditions(baseline, *predicted), reg).clauses["conditions"]
    assert got is expected, why


@pytest.mark.parametrize(
    "accept,predicted,expected,why",
    [
        ([[], []], ("upon notice", "if the Customer requests"), True,
         "empty accept-sets behave exactly as before (the 31-of-32 case)"),
        ([["the Customer so requests"], []], ("upon notice", "the Customer so requests"), True,
         "an accepted equivalent phrasing matches its own entry (section 3.8.3)"),
        ([["the Customer so requests"], []], ("upon notice", "some other clause"), False,
         "a phrasing in NEITHER the entry nor its accept-set still fails"),
        ([["the Customer so requests"], []],
         ("upon notice", "if the Customer requests", "the Customer so requests"), False,
         "count stays len(conditions): an accept-set never raises the count"),
        ([["a shared phrasing"], ["a shared phrasing"]],
         ("a shared phrasing", "if the Customer requests"), True,
         "two entries sharing an accepted phrasing must still match by backtracking, "
         "not be rejected because a greedy first-fit consumed the wrong entry"),
    ],
)
def test_clause7_reads_conditions_accept_set(gold, baseline, reg, accept, predicted, expected, why):
    """Section 3.8.3's field (v0.41), wired into clause 7 on 2026-09-01.

    The last case is the one a greedy matcher gets wrong, and it took two attempts
    to make it actually discriminate -- recorded because the reason is a trap, not
    a typo. "a shared phrasing" is accepted by BOTH gold entries, so a first-fit
    binds it to entry 0; "if the Customer requests" is then accepted ONLY by entry
    0, which is already consumed, and a complete match is reported as a failure on
    nothing but iteration order.

    THE LEADING "a" IS LOAD-BEARING. `_condition_multiset` SORTS the predicted
    strings, so the order written in this parametrize tuple never reaches the
    matcher -- only lexicographic order does. The first draft used "shared
    phrasing", which sorts AFTER "if the Customer requests" and hands the matcher
    the one ordering greedy happens to get right. Both drafts read identically at a
    glance and only one tests anything.

    Caught by breaking the matcher to greedy and watching the suite stay green
    (Standing Principle 7: a test is not evidence until it has been seen to fail on
    the case it was written for) -- and the same check is what proved the fix.
    """
    amended = dict(gold,
                   conditions=["if the Customer requests", "upon notice"],
                   conditions_accept_set=accept)
    got = score.score_item(amended, _with_conditions(baseline, *predicted), reg).clauses["conditions"]
    assert got is expected, why


def test_clause7_accept_set_is_absent_from_almost_every_locked_item():
    """Section 3.8.3 is explicitly not a general paraphrase-tolerance mechanism.
    If this count grows without a ruling, clause 7 is quietly being loosened."""
    import glob
    carrying = [
        json.loads(Path(p).read_text())["item_id"]
        for p in glob.glob(str(GOLD.parents[2] / "batch0*" / "items" / "*.json"))
        if any(json.loads(Path(p).read_text()).get("conditions_accept_set") or ())
    ]
    assert carrying == ["C06-01"]


# --- sections 4.1 / 4.2 alignment -------------------------------------------

@pytest.mark.parametrize(
    "gold_span,pred_span,expected,why",
    [
        ((0, 99), (33, 132), (1, 0, 0), "IoU is exactly 0.500 and the threshold is inclusive"),
        ((0, 99), (34, 133), (0, 1, 1), "IoU 0.489, just below"),
        ((0, 100), (0, 100), (1, 0, 0), "identical spans"),
        ((0, 100), (200, 300), (0, 1, 1), "disjoint"),
    ],
)
def test_alignment_threshold_boundary(gold_span, pred_span, expected, why):
    a = align.align([gold_span], [pred_span])
    assert (len(a.pairs), len(a.missed_gold), len(a.unexpected_pred)) == expected, why


def test_adversarial_two_close_gold_items_are_not_misassigned():
    """Two overlapping gold items and two predictions, arranged so that a naive
    gold-major "first prediction over threshold wins" would pair A with the
    prediction that actually belongs to B.

    A=(0,100) B=(60,160); P=(50,150) Q=(0,110).
    IoU(A,P)=0.333 (below threshold), IoU(B,P)=0.562,
    IoU(A,Q)=0.909,                   IoU(B,Q)=0.312.
    The only admissible pairing is Q->A and P->B.
    """
    a = align.align([(0, 100), (60, 160)], [(50, 150), (0, 110)])
    pairs = {p.gold_index: p.pred_index for p in a.pairs}
    assert pairs == {0: 1, 1: 0}, f"misassigned: {pairs}"
    assert not a.missed_gold and not a.unexpected_pred


def test_adversarial_one_prediction_between_two_gold_items_takes_the_better():
    """A single prediction admissible against BOTH gold items must take the
    higher-IoU one and leave the other MISSED -- never both, and never the
    weaker pairing (section 4.2: one predicted span aligns to at most one gold item)."""
    a = align.align([(0, 100), (0, 90)], [(0, 100)])
    assert len(a.pairs) == 1
    assert a.pairs[0].gold_index == 0, "must pair the IoU-1.0 item, not the 0.9 one"
    assert a.missed_gold == [1]


def test_alignment_is_deterministic_under_input_reordering():
    """Section 4.2 requires the chosen pairing to be recorded with the score, so it
    must not depend on the order predictions happen to arrive in."""
    gold_spans = [(0, 100), (60, 160)]
    forward = align.align(gold_spans, [(50, 150), (0, 110)])
    reverse = align.align(gold_spans, [(0, 110), (50, 150)])
    assert {p.gold_index for p in forward.pairs} == {p.gold_index for p in reverse.pairs}
    assert sorted(round(p.iou, 6) for p in forward.pairs) == sorted(
        round(p.iou, 6) for p in reverse.pairs
    )


def test_not_annotatable_prediction_is_neither_correct_nor_a_false_positive():
    """Section 4.4, and the shape section 21 R6 will populate."""
    a = align.align([(0, 100)], [(0, 100), (200, 300)], not_annotatable=[(200, 300)])
    assert len(a.pairs) == 1
    assert a.unexpected_pred == []
    assert a.not_annotatable_pred == [1]
