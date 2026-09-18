"""Section 8.10's `kind` axis (section 10.1 F9) and F10's resolution of the five
formerly-UNCLASSIFIED tags.

The point of the ruling is that `kind` is the FIRST axis and `direction` is a
sub-axis of REPRESENTATIONAL only. Most of what could go wrong here is silent:
a new tag drifting into the headline denominator because a default admitted it,
a non-representational tag acquiring a direction because a lookup returned
something plausible, or the guideline's kind map falling out of step with the
tags the committed gold set actually uses. Each of those is planted below rather
than assumed away.
"""

from __future__ import annotations

import json

import pytest

from evals.harness.gap_kinds import (
    DENOMINATOR_EXCLUDING_KINDS,
    GAP_DIRECTION,
    GAP_KIND,
    UNCLASSIFIED_KIND,
    direction_of,
    excluding_tags,
    in_force_scope,
    kind_of,
)
from evals.harness.report import build
from evals.harness.run_scoring import GOLDENS_DIR, load_gold_items
from evals.harness.score import Outcome


@pytest.fixture(scope="module")
def gold_items():
    items = load_gold_items(GOLDENS_DIR)
    # A known-answer gate before any count below is read off this fixture
    # (Standing Principle 7): an empty or short load would make every
    # denominator assertion in this file pass vacuously.
    assert len(items) == 36, f"expected the 36 locked items, loaded {len(items)}"
    return items


# --- the vocabulary itself --------------------------------------------------

def test_every_tag_the_committed_gold_set_uses_has_a_ruled_kind(gold_items):
    """The forcing function. A tag added to an item without a §8.10 kind ruling
    fails HERE, not silently in a denominator months later."""
    live = {t for i in gold_items for t in i["known_gaps"]}
    unruled = sorted(t for t in live if kind_of(t) == UNCLASSIFIED_KIND)
    assert unruled == [], f"tags in live use with no §8.10 kind: {unruled}"


def test_direction_is_defined_for_exactly_the_representational_tags():
    """F10's resolution, stated as an invariant rather than as a comment: a tag
    of any other kind has no direction BY RULING. If someone adds a direction
    for a REACHABILITY or CORPUS_DEFECT tag, that is the masquerade F10 was
    filed separately to prevent, and it fails here."""
    representational = {t for t, k in GAP_KIND.items() if k == "REPRESENTATIONAL"}
    assert set(GAP_DIRECTION) == representational


@pytest.mark.parametrize("tag,expected", [
    ("exception_unsupported", "OVERSTATING"),
    ("compound_action", "INCOMPLETENESS"),
    ("action_not_in_taxonomy", "INCOMPLETENESS"),
    ("within_preposition", None),
    ("relative_trigger_preposition", None),
    ("corpus_artifact_in_span", None),
    ("shared_subject_split", None),
    ("redacted_value", None),
])
def test_f10s_five_tags_resolve_to_no_direction_and_the_other_five_keep_theirs(tag, expected):
    assert direction_of(tag) == expected


def test_None_and_UNCLASSIFIED_are_different_answers_and_do_not_collapse():
    """None means "this kind has no direction to assign"; UNCLASSIFIED means "a
    decision is owed". Collapsing them would let a genuinely unruled tag hide
    among the deliberately direction-free ones."""
    assert direction_of("corpus_artifact_in_span") is None       # ruled: no direction
    assert direction_of("some_future_tag") is None               # unruled kind -> not representational
    assert kind_of("some_future_tag") == UNCLASSIFIED_KIND       # ...but the KIND is owed
    assert kind_of("corpus_artifact_in_span") != UNCLASSIFIED_KIND


# --- the denominator predicate ----------------------------------------------

@pytest.mark.parametrize("tags,expected,why", [
    ([], True, "untagged items are in, unchanged"),
    (["corpus_artifact_in_span"], True, "CORPUS_DEFECT enters (§9.1 ground 1)"),
    (["shared_subject_split"], True, "ANNOTATION_CONVENTION enters"),
    (["mutual_obligation"], False, "REPRESENTATIONAL excluded (ground 2)"),
    (["within_preposition"], False, "REACHABILITY excluded (guaranteed failure)"),
    (["redacted_value"], False, "WITHHELD_VALUE held excluded pending its direction ruling"),
    (["some_future_tag"], False, "an unruled kind must NEVER enter silently"),
    (["mutual_obligation", "shared_subject_split"], False,
     "C14-02's real shape: one excluding tag is enough"),
    (["corpus_artifact_in_span", "shared_subject_split"], True,
     "several admitting tags still admit -- membership is by kind, never by count"),
])
def test_in_force_scope_by_kind(tags, expected, why):
    assert in_force_scope(tags) is expected, why


def test_an_unruled_tag_excludes_conservatively_rather_than_defaulting_in():
    """The direction of the default is the whole safety property. Admitting an
    unruled tag would quietly move this phase's headline acceptance figure."""
    assert UNCLASSIFIED_KIND in DENOMINATOR_EXCLUDING_KINDS
    assert excluding_tags(["some_future_tag"]) == ["some_future_tag"]


# --- the committed gold set: the ruling's measured effect -------------------

def test_the_whole_set_denominators_move_17_to_20(gold_items):
    """The ruling's whole-set cost, pinned. Three items move; the rest is the
    cassette-unscoreable population, which this predicate does not touch."""
    legacy = [i["item_id"] for i in gold_items if not i["known_gaps"]]
    kinded = [i["item_id"] for i in gold_items if in_force_scope(i["known_gaps"])]
    assert len(legacy) == 17
    assert len(kinded) == 20
    assert sorted(set(kinded) - set(legacy)) == ["C04-01", "C04-03", "C14-06"]


def test_E03_01_stays_excluded_because_WITHHELD_VALUE_is_deliberately_held(gold_items):
    """Sub-choice 2, pinned so it cannot be quietly flipped: `redacted_value` is
    its own kind AND stays out of the denominator until its direction question
    is ruled. If someone admits it, the in-force figure moves 3/10 -> 3/11 and
    this test is the thing that says so."""
    e03 = next(i for i in gold_items if i["item_id"] == "E03-01")
    assert e03["known_gaps"] == ["redacted_value"]
    assert GAP_KIND["redacted_value"] == "WITHHELD_VALUE"
    assert in_force_scope(e03["known_gaps"]) is False


def test_C14_02_is_excluded_by_its_representational_tag_not_its_convention_tag(gold_items):
    """The mixed case. `shared_subject_split` now admits, so C14-02 stays out
    ONLY because `mutual_obligation` is present -- worth pinning, because if the
    predicate ever became "any admitting tag admits" this item would flip and
    nothing else in the suite would notice."""
    c14 = next(i for i in gold_items if i["item_id"] == "C14-02")
    assert set(c14["known_gaps"]) == {"mutual_obligation", "shared_subject_split"}
    assert excluding_tags(c14["known_gaps"]) == ["mutual_obligation"]
    assert in_force_scope(c14["known_gaps"]) is False


# --- G6's disclosure --------------------------------------------------------

def _report(rows):
    per_item = {i: [o, o, o] for i, o, _ in rows}
    gold_by_id = {i: {"item_id": i, "known_gaps": g, "vague_temporal_phrase": None}
                  for i, _, g in rows}
    return build(per_item, gold_by_id)


def test_G6_discloses_a_non_representational_tag_by_KIND_with_no_direction():
    rep = _report([("A-01", Outcome.FULLY_CORRECT, ["corpus_artifact_in_span"])])
    out = rep.render()
    assert "CORPUS_DEFECT: A-01 (corpus_artifact_in_span)" in out
    assert "OVERSTATING: A-01" not in out
    assert "INCOMPLETENESS: A-01" not in out


def test_G6_still_forces_a_decision_on_a_tag_with_no_ruled_kind():
    rep = _report([("A-01", Outcome.FULLY_CORRECT, ["some_future_tag"])])
    assert f"{UNCLASSIFIED_KIND}: A-01 (some_future_tag)" in rep.render()


def test_G6_splits_one_item_carrying_tags_of_two_different_kinds():
    """A planted mixed item: the representational tag goes to its direction
    bucket and the convention tag to its kind bucket, in the same render."""
    rep = _report([("A-01", Outcome.FULLY_CORRECT,
                    ["mutual_obligation", "shared_subject_split"])])
    out = rep.render()
    assert "INCOMPLETENESS: A-01 (mutual_obligation)" in out
    assert "ANNOTATION_CONVENTION: A-01 (shared_subject_split)" in out


def test_the_render_names_which_kinds_exclude_so_the_figure_is_readable_alone():
    rep = _report([("A-01", Outcome.FULLY_CORRECT, [])])
    out = rep.render()
    assert "kind-scoped, §8.10" in out
    assert "CORPUS_DEFECT and" in out and "ANNOTATION_CONVENTION do NOT" in out


# --- the legacy scope, retained only for gap_agreement's coherence check ----

def test_the_legacy_denominator_is_still_computable_and_differs(gold_items):
    """F17's precondition. `gap_agreement`'s d_gold is still legacy-scoped, so
    render() must be able to compare like with like rather than silently
    comparing two different questions."""
    rows = [(i["item_id"], Outcome.PARTIAL, i["known_gaps"]) for i in gold_items]
    rep = _report(rows)
    assert rep.legacy_no_known_gaps_denominator == 17
    assert rep.criterion2_no_known_gaps[1] == 20
