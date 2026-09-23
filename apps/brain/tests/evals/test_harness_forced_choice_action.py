"""Section 8.8.5 (guideline v0.64, section 10.1 F22): the single-verb
`action_accept_set` is CONFIRMED for the genuine-gap class, and clause 2 on such
an item is disclosed as a forced-choice agreement check (report.py's G9).

What could go wrong here is silent in every case, so each is planted rather than
assumed away:

  * an annotator widening a genuine-gap item's accept-set, which is exactly the
    move section 8.8 forbids and section 14.3 appears to invite;
  * G9 keying on a singleton accept-set instead of on the TAG, which would sweep
    in ordinary confident items whose sentence happens to admit one verb;
  * G9 falling silent when the class is entirely cassette-unscoreable -- the
    state the set is actually in today, and the one where a bare "None" line
    would read as "the class is empty";
  * `E08-04` being quietly restamped while its provisional status is discharged,
    which section 22.1 refuses and which would stale nothing today only because
    its segment has no cassette.
"""

from __future__ import annotations

import json

import pytest

from evals.harness.gap_kinds import in_force_scope, kind_of
from evals.harness.report import build
from evals.harness.run_scoring import GOLDENS_DIR, load_gold_items
from evals.harness.score import Outcome

TAG = "action_not_in_taxonomy"

# The eight-item census this ruling was made over, named rather than recomputed.
# A DATED population: a future batch adding a ninth tagged item must not silently
# re-baseline the figures section 8.8.5 publishes, the same mechanism K's
# published population uses (v0.53) and G's (F20).
V064_CLASS = frozenset({
    "C10-01", "C10-02", "C14-04", "E01-01",
    "C04-06", "C02-07", "E03-03", "E08-04",
})


@pytest.fixture(scope="module")
def gold_items():
    items = load_gold_items(GOLDENS_DIR)
    # Standing Principle 7: a known-answer gate BEFORE any count below is read
    # off this fixture. An empty or short load would make every assertion here
    # pass vacuously -- v0.58's preserved screen printed "12/12 PASS" over zero
    # items for exactly that reason.
    assert len(items) >= 48, f"expected at least the 48 locked items, loaded {len(items)}"
    ids = {i["item_id"] for i in items}
    assert V064_CLASS <= ids, f"census items missing from the load: {sorted(V064_CLASS - ids)}"
    return items


def _tagged(items):
    return [i for i in items if TAG in (i["known_gaps"] or ())]


# --- the rule itself --------------------------------------------------------

def test_every_genuine_gap_item_holds_a_single_verb_accept_set(gold_items):
    """Section 8.8's genuine-gap branch: `action_accept_set` holds the nearest
    verb ALONE. Confirmed at v0.64, so a widening is a rule violation and not a
    section 14.3 resolution."""
    widened = {
        i["item_id"]: i["action_accept_set"]
        for i in _tagged(gold_items)
        if list(i["action_accept_set"]) != [i["action"]]
    }
    assert widened == {}, (
        "§8.8.5 confirms the single-verb rule; these items are widened or their "
        f"set disagrees with their slot: {widened}"
    )


def test_the_class_is_the_eight_items_the_ruling_was_made_over(gold_items):
    """Stated as a DATED population, not as a live count. A ninth tagged item is
    legitimate and must not fail this file -- but it is outside the 16.7% and the
    4-of-4 narrow-fix measurement section 8.8.5 publishes, so it is asserted to
    be an ADDITION rather than allowed to drift into those figures."""
    live = {i["item_id"] for i in _tagged(gold_items)}
    assert V064_CLASS <= live, (
        f"items dropped out of the v0.64 census: {sorted(V064_CLASS - live)}"
    )
    # The dated arithmetic, reproduced over its own population only.
    assert len(V064_CLASS) == 8
    assert round(100 * 8 / 48, 1) == 16.7


def test_the_tag_is_representational_so_the_class_is_outside_the_in_force_denominator(gold_items):
    """The load-bearing half of §8.8.5's cost argument: a widening could not have
    moved the in-force criterion even if one had been permitted."""
    assert kind_of(TAG) == "REPRESENTATIONAL"
    for item in _tagged(gold_items):
        assert not in_force_scope(item["known_gaps"]), item["item_id"]


# --- G9 ---------------------------------------------------------------------

def _report(items, outcomes, unscoreable=None):
    gold_by_id = {i["item_id"]: i for i in items}
    return build(outcomes, gold_by_id, cassette_unscoreable_items=unscoreable or {})


def test_g9_names_a_scored_genuine_gap_item(gold_items):
    rep = _report(gold_items, {"E08-04": [Outcome.FULLY_CORRECT]})
    assert rep.forced_choice_action_items == ["E08-04"]
    body = rep.render()
    assert "FORCED-CHOICE AGREEMENT CHECK (§8.8.5 G9)" in body
    assert "did the model settle on the same" in body


def test_g9_keys_on_the_TAG_and_not_on_a_singleton_accept_set(gold_items):
    """The planted defect. An untagged item can legitimately carry one verb --
    nothing else is defensible for its sentence -- and reading the SET instead of
    the tag would disclose it as a forced choice, which is false: for that item a
    correct answer exists and clause 2 measures whether extraction found it."""
    singletons_without_the_tag = [
        i["item_id"] for i in gold_items
        if len(i["action_accept_set"]) == 1 and TAG not in (i["known_gaps"] or ())
    ]
    assert singletons_without_the_tag, (
        "this test is vacuous unless such an item exists in the committed set"
    )
    victim = singletons_without_the_tag[0]
    rep = _report(gold_items, {victim: [Outcome.FULLY_CORRECT]})
    assert rep.forced_choice_action_items == []
    assert "None among SCORED items" in rep.render()


def test_g9_does_not_sweep_in_an_item_carrying_a_DIFFERENT_tag(gold_items):
    """The working near-miss, and the one a wrong predicate would actually pass
    with: `if i.known_gaps` -- any tag at all. `C03-02` carries `compound_action`
    and nothing else, so its `action` IS a taxonomy member that denotes the
    performance and clause 2 measures a real thing for it. G9 must stay silent.

    Recorded because the FIRST defect planted against this file did not compile
    (ItemReport carries no accept-set), so it failed for the wrong reason and
    proved nothing. This one runs.
    """
    victim = next(
        i["item_id"] for i in gold_items
        if (i["known_gaps"] or ()) and TAG not in i["known_gaps"]
    )
    rep = _report(gold_items, {victim: [Outcome.FULLY_CORRECT]})
    assert rep.forced_choice_action_items == [], (
        f"{victim} carries a tag but NOT {TAG}; clause 2 is a real measurement for it"
    )
    assert "None among SCORED items" in rep.render()


def test_g9_says_the_class_is_unscoreable_rather_than_empty(gold_items):
    """Today's real state: all eight are cassette-unscoreable, so G9's empty
    branch must distinguish 'no such item was SCORED' from 'no such item
    EXISTS'. A bare "None" would read as the second."""
    untagged = next(i["item_id"] for i in gold_items if not (i["known_gaps"] or ()))
    rep = _report(gold_items, {untagged: [Outcome.FULLY_CORRECT]})
    body = rep.render()
    assert "None among SCORED items" in body
    assert "The class is not empty" in body


def test_g9_is_printed_with_the_criterion_figures_and_not_in_a_methods_section(gold_items):
    """§6.1's own reason for on-the-spot disclosure: a reader who never reaches
    the methods section still gets the caveat. Pinned by ORDER, because moving
    the block far from the figures is the failure this guards."""
    rep = _report(gold_items, {"E08-04": [Outcome.FULLY_CORRECT]})
    body = rep.render()
    crit = body.index("CRITERION 2 (IN FORCE")
    g9 = body.index("FORCED-CHOICE AGREEMENT CHECK (§8.8.5 G9)")
    ceiling = body.index("NO PREDICTED CEILING IS STATED")
    assert crit < g9 < ceiling


# --- E08-04's discharge -----------------------------------------------------

def test_e08_04_is_discharged_without_a_single_field_changing(gold_items):
    item = next(i for i in gold_items if i["item_id"] == "E08-04")
    assert item["action"] == "PROCESS"
    assert item["action_accept_set"] == ["PROCESS"]
    assert item["known_gaps"] == [TAG]
    # NOT restamped: a rule that CONFIRMS an item's treatment earns no restamp
    # (C11-02/C04-06's v0.54 precedent, §22.1). Its segment has no cassette so a
    # restamp would be free -- and "free" is not a reason.
    assert item["guideline_version"] == "v0.62"
    assert "PROVISIONAL STATUS IS DISCHARGED" in item["annotator_notes"]


def test_the_segment_observation_is_closed_rather_than_deleted():
    path = GOLDENS_DIR / "batch04" / "segments" / "E08-016.json"
    seg = json.loads(path.read_text())
    obs = next(o for o in seg["observations"] if o["id"] == "E08-016#genuine-gap-widening")
    assert obs["status"].startswith("CLOSED")
    # The open question's own text survives as a dated record -- corrections are
    # new text, never silent edits.
    assert "INSTANCE THREE" in obs["note"]
    assert "RULED 2026-09-23" in obs["note"]
