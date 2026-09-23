"""§8.12 / §10.1 F21: the `temporal_composition` tag, its scope, and its
DELIBERATELY DEFERRED direction.

Three things are pinned here, and they fail for different reasons on purpose:

1. The MECHANISM, verified through the production `_classify_temporal()` rather
   than read off the regexes -- including the two claims in the logged notes that
   do NOT survive execution, so the corrected record cannot silently revert.
2. The SCOPE (slot limit, not greedy swallow) as it lands on real items.
3. The DEFERRAL as a RULING: `DIRECTION_DEFERRED` is explicit, distinct from
   UNCLASSIFIED, and costs nothing because the denominator reads KIND.
"""
from __future__ import annotations

import glob
import json
import os

import pytest

from evals.harness.gap_kinds import (
    DEFERRED_DIRECTION,
    DIRECTION_DEFERRED,
    GAP_DIRECTION,
    GAP_KIND,
    UNCLASSIFIED_KIND,
    direction_of,
    excluding_tags,
    in_force_scope,
    kind_of,
)
from obligo_brain.compiler.ir_compile import _classify_temporal

GOLDENS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "evals", "goldens")

TAG = "temporal_composition"
TAGGED = {"E03-01", "C02-07", "C04-08"}


@pytest.fixture(scope="module")
def gold_items():
    items = [json.load(open(p)) for p in
             sorted(glob.glob(os.path.join(GOLDENS, "batch*", "items", "*.json")))]
    assert len(items) >= 48, "partial gold load; assertions below would go vacuous"
    return items


# --- 1. the mechanism -------------------------------------------------------

def test_the_composed_phrase_compiles_silently_rather_than_being_rejected():
    """The defect that makes this REPRESENTATIONAL rather than REACHABILITY-shaped:
    nothing is rejected. A greedy trailing capture swallows the surplus bounds
    into the trigger string and the candidate COMPILES."""
    one = _classify_temporal(
        "after expiry of the said 6-month period and during the Term of this Agreement, "
        "or until Bellicum has secured an alternate source of supply from a Third Party manufacturer")
    assert one is not None and one.startswith('AFTER "expiry of the said 6-month period and during')

    two = _classify_temporal(
        "within 30 days of the Effective Date, and thereafter by 31 December of each "
        "Calendar Year during the Term")
    assert two is not None and two.startswith('WITHIN 30d OF "the Effective Date, and thereafter')


def test_both_logged_notes_overclaim_that_EACH_element_has_a_v1_form():
    """§8.12's correction, pinned so it cannot silently revert to the original
    claim. ONE of instance one's three elements classifies, and TWO of instance
    two's -- not three in either case."""
    one = ["after expiry of the said 6-month period",
           "during the Term of this Agreement",
           "until Bellicum has secured an alternate source of supply from a Third Party manufacturer"]
    assert [_classify_temporal(e) is not None for e in one] == [True, False, False]

    two = ["within 30 days of the Effective Date",
           "by 31 December of each Calendar Year",
           "during the Term"]
    assert [_classify_temporal(e) is not None for e in two] == [True, True, False]


def test_the_8_11_distinction_survives_the_correction_on_instance_two():
    """Why this is not `lead_time_unrepresentable`: §8.11's decisive test is
    whether free composition would rescue the clause. For the deadline PAIR it
    would -- both classify on their own -- which is the opposite of §8.11, where
    no v1 form pairs a duration with a direction at all."""
    assert _classify_temporal("within 30 days of the Effective Date") == \
        'WITHIN 30d OF "the Effective Date"'
    assert _classify_temporal("by 31 December of each Calendar Year") == \
        'BY "31 December of each Calendar Year"'
    # ... while §8.11's own shape still has no form, composed or not.
    assert _classify_temporal("at least 30 days before the first day of each Calendar Quarter") is None


def test_the_near_miss_surplus_bound_classifies_to_None_on_its_own():
    """C02-07's terminal bound: unrepresented rather than swallowed, which is the
    mechanical difference the near-miss note recorded and which the ruling keeps
    while declining to scope the TAG by it."""
    assert _classify_temporal(
        "until a decision by AMAG has been made whether a Recall or some other "
        "corrective action is necessary") is None


# --- 2. the scope -----------------------------------------------------------

def test_exactly_three_items_carry_the_tag(gold_items):
    assert {i["item_id"] for i in gold_items if TAG in i["known_gaps"]} == TAGGED


def test_C02_07_is_in_scope_which_is_what_SLOT_LIMIT_scoping_decides(gold_items):
    """The scope choice is load-bearing on exactly this item: under a
    swallow-scoped rule it would be OUT (its surplus bound sits outside the
    annotated phrase), under the slot-limit rule it is IN. If someone re-scopes
    the tag to the greedy capture, this is the test that fails."""
    c02 = next(i for i in gold_items if i["item_id"] == "C02-07")
    assert TAG in c02["known_gaps"]


def test_E03_01_carries_BOTH_temporal_tags_and_neither_subsumes_the_other(gold_items):
    e03 = next(i for i in gold_items if i["item_id"] == "E03-01")
    assert {"lead_time_unrepresentable", TAG} <= set(e03["known_gaps"])
    assert GAP_KIND["lead_time_unrepresentable"] == GAP_KIND[TAG] == "REPRESENTATIONAL"
    # ... but they are NOT interchangeable: one carries a ruled direction, the
    # other is deferred, which is the sharpest statement that they are different
    # claims about the same item.
    assert direction_of("lead_time_unrepresentable") == "INCOMPLETENESS"
    assert direction_of(TAG) == DEFERRED_DIRECTION


def test_no_item_gained_the_tag_as_its_ONLY_excluding_tag(gold_items):
    """The exclusion-neutrality claim, asserted on data rather than trusted from
    the ruling's prose: every tagged item was ALREADY out of the in-force
    denominator, so the amendment cannot have moved criterion 2."""
    for i in gold_items:
        if TAG in i["known_gaps"]:
            others = [t for t in i["known_gaps"] if t != TAG]
            assert excluding_tags(others), (
                f"{i['item_id']} would be newly excluded BY THIS TAG ALONE; the "
                f"ruling's exclusion-neutrality claim no longer holds")


def test_no_tagged_item_was_restamped(gold_items):
    """F19's precedent: `known_gaps` is not one of §5's eight scored clauses, so
    a tag is added without conforming the item."""
    stamps = {i["item_id"]: i["guideline_version"] for i in gold_items if TAG in i["known_gaps"]}
    assert stamps == {"E03-01": "v0.28", "C02-07": "v0.62", "C04-08": "v0.62"}


# --- 3. the deferral, as a ruling -------------------------------------------

def test_the_tag_is_representational_and_its_direction_is_DEFERRED_not_missing():
    assert kind_of(TAG) == "REPRESENTATIONAL"
    assert TAG in DIRECTION_DEFERRED
    assert TAG not in GAP_DIRECTION
    assert direction_of(TAG) == DEFERRED_DIRECTION


def test_deferred_and_unclassified_and_None_are_three_distinct_answers():
    """§8.12's mechanism note, pinned. Collapsing DEFERRED into UNCLASSIFIED
    would let a genuinely unruled tag hide behind a deliberate deferral -- the
    same inversion §8.10 keeps None and UNCLASSIFIED apart to prevent, one level
    down."""
    assert direction_of(TAG) == DEFERRED_DIRECTION            # ruled open
    assert direction_of("corpus_artifact_in_span") is None    # ruled: none to assign
    assert direction_of("some_future_tag") is None            # unruled KIND
    assert len({DEFERRED_DIRECTION, UNCLASSIFIED_KIND, "INCOMPLETENESS"}) == 3


def test_deferring_the_direction_costs_nothing_because_the_denominator_reads_KIND():
    """Why the deferral was available at all: §9.1 excludes on kind, so the tag
    does its denominator work with no direction assigned."""
    assert in_force_scope([TAG]) is False
    assert excluding_tags([TAG]) == [TAG]


def test_G6_discloses_a_deferred_tag_under_its_own_bucket():
    """The report must SHOW the deferral rather than bury it among the
    direction-free kinds. Exercised through the real bucket logic, over a
    minimal stand-in for a numerator item, because G6 reads only `.items`,
    `.modal` and `.known_gaps`."""
    from evals.harness import report as report_mod
    lines = report_mod.Report.numerator_gap_disclosure.fget(_FakeReport([_FakeItem("X-01", [TAG])]))
    assert any(line.strip().startswith(DEFERRED_DIRECTION) and "X-01" in line for line in lines)
    # ... and it is NOT reported as UNCLASSIFIED, which would read as "nobody ruled".
    assert not any(UNCLASSIFIED_KIND in line for line in lines)


class _FakeItem:
    def __init__(self, item_id, known_gaps):
        from evals.harness.score import Outcome
        self.item_id, self.known_gaps, self.modal = item_id, known_gaps, Outcome.FULLY_CORRECT


class _FakeReport:
    def __init__(self, items):
        self.items = items


# --- 4. second-instrument effects, MEASURED rather than assumed --------------

def test_the_ruling_is_G_neutral_and_the_reason_is_structural_not_lucky():
    """§3.6.1's v0.45 dual-predicate rule: a retroactive tag edit must state its
    effect on the ANNOTATOR instruments too, not only on §5.

    F19 moved `G` 6 -> 7 by adding a gold-only tag to E03-01. This ruling adds
    ANOTHER gold-only tag to the same item and `G` does NOT move -- because
    E03-01 is already in `superset_items` (gold ⊃ cold) and a further gold-only
    tag cannot change which class the pair falls in. That is a structural
    reason, not a coincidence, which matters: v0.61 found `G` had been matching
    its published figure by two drifts cancelling. Both are asserted.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_harness_gap_agreement import _load_holdout_pairs
    from evals.harness.gap_agreement import compute_gap_agreement

    live = compute_gap_agreement(_load_holdout_pairs())
    assert live.g_count == 7, "unmoved by this ruling (was 7 at v0.61)"
    assert "E03-01" in live.superset_items, (
        "the structural reason G cannot move: the pair is already a strict "
        "superset, so adding another gold-only tag changes no class")
    assert live.d_band == (16, 17), "F17's band is unmoved"

    sealed = compute_gap_agreement(_load_holdout_pairs(pre_tag=True))
    assert sealed.g_count == 6 and sealed.d_band == (15, 17), (
        "the DATED 2026-08-29 reproduction must be untouched by a live tag edit")


def test_the_tag_reached_the_SECOND_vocabulary_copy_so_A_did_not_move():
    """v0.61's own trap, avoided deliberately rather than re-sprung: adding a
    tag to `gap_kinds.GAP_KIND` alone leaves `annotator_agreement.SECTION_8_TAGS`
    stale, which marks every item carrying it NON_CONFORMING and moves `A` -- a
    failure in a DIFFERENT instrument from the one the tag was added for, caught
    by no test in the gap-kinds file."""
    from evals.harness.annotator_agreement import SECTION_8_TAGS
    assert TAG in SECTION_8_TAGS
