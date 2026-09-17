"""Regression tests for guideline §3.6.2 (v0.58, §10.1 F12) and §3.6's v0.58 breadth
ruling (§10.1 F5).

WHAT IS ACTUALLY AT RISK, and why these are the tests rather than prose:

  (1) BOTH RULINGS' HEADLINE CLAIM IS A *ZERO*. F12 extends a retroactive rule and
      claims it restamps nothing and moves no figure; F5 declines a retroactive pass
      and claims the same. A zero-cost claim is the easiest kind to break later
      without noticing, because nothing visibly changes when it breaks -- the set
      just quietly stops satisfying a rule it is asserted to satisfy.

  (2) THE ONE EXCEPTION IS AN ADJUDICATION, NOT AN OVERSIGHT. `C22-01` is the single
      item with no member free of restated material, and it clears under carve-out 1
      because its span names the thing "notice". If a future edit adds a second such
      item, that is a new adjudication owed -- not something to be absorbed silently
      by a rule that says "35 of 36 already conform".

  (3) THE SCREEN ITSELF IS THE THING MOST LIKELY TO ROT. It has already produced four
      recorded misses. Its known-answer gate is therefore asserted directly, including
      the suppletive `notify`->`notice` case that both prior sweeps missed and that no
      stemmer reaches.

  (4) F5's FORWARD/RETROACTIVE BOUNDARY. The head-only rule governs batch 4 onward and
      restamps nothing. The 23 locked items with no head-only member are EXPECTED to
      stay that way; a test that demanded they conform would silently convert a
      forward rule into the retroactive pass F5 explicitly refused.

EVERY TEST HERE READS ONLY COMMITTED GOLD JSON -- no corpus, no database, no network --
so all of them run in CI. That is deliberate and is the difference from
`test_gold_responsible_for_rule.py`, whose corpus-evidence group is `skipif`-gated:
§3.6.2's and §3.6's v0.58 claims are claims ABOUT THE COMMITTED GOLD SET, so CI can
verify all of them rather than a subset.

The criterion-2 figures these rulings leave unmoved (`3/9`, and F1's measured
`5/9` counterfactual) need a real database and the cassettes, and are covered by the
scoring-run tests rather than duplicated here.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_ACCEPT_SETS = (
    pathlib.Path(__file__).resolve().parents[2]
    / "evals" / "goldens" / "holdout" / "accept_sets"
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _ACCEPT_SETS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


screen_mod = _load("restatement_screen")
census_mod = _load("breadth_census")


@pytest.fixture(scope="module")
def items():
    return screen_mod.load_items()


# --------------------------------------------------------------------------
# (3) the screen's own gate
# --------------------------------------------------------------------------

def test_the_restatement_screen_passes_its_known_answer_gate():
    """Standing Principle 7: counts are not evidence until this passes."""
    screen_mod.check_gate()


def test_the_gate_covers_all_four_recorded_nominalisation_misses():
    """Three `y`/`e`-boundary misses plus the suppletive one, which is the point.

    `notify`->`notice` is not reachable by any stemmer, so the fix for the first
    three (stem more carefully) would not have caught the fourth. If someone
    replaces the hand-authored table with a stemmer, this is the test that fails.
    """
    gated = {(label, verb) for label, verb, _, _ in screen_mod.KNOWN_ANSWERS}
    for pair in [
        ("product_delivery", "DELIVER"),
        ("product_liability_indemnification", "INDEMNIFY"),
        ("self_regulatory_compliance", "COMPLY"),
        ("notice", "NOTIFY"),
    ]:
        assert pair in gated, f"{pair} is a recorded miss and must stay in the gate"
    assert screen_mod.restates("notice", "NOTIFY") == ["notice"]


def test_the_screen_is_still_structurally_blind_where_it_is_documented_to_be():
    """§3.6.1 calls the screen a lower bound, not a census, and specifically blind to
    any item whose real verb is outside the taxonomy (`C10-02`'s `_listing` against
    `action = ESTABLISH`, the real verb being "add").

    Pinned so the caveat cannot quietly stop being true while the prose still claims
    it -- an overclaim in the SAFE direction is still an overclaim.
    """
    assert screen_mod.restates("insurance_certificate_listing", "ESTABLISH") == []


def test_a_short_or_empty_gold_load_fails_loudly(tmp_path, monkeypatch):
    """The first draft of the screen printed "12/12 PASS" over ZERO items because its
    path was one level short. A passing matcher gate above an empty corpus is the
    Standing Principle 7 shape one layer out, so the load asserts its own floor."""
    monkeypatch.setattr(screen_mod, "GOLDENS", tmp_path)
    with pytest.raises(screen_mod.GateFailure, match="expected at least"):
        screen_mod.load_items()


# --------------------------------------------------------------------------
# (1) + (2) F12's zero-cost claim, and its single adjudicated exception
# --------------------------------------------------------------------------

def test_f12_extension_costs_nothing_every_item_but_c22_01_already_conforms(items):
    """§3.6.2's headline: 35 of 36 satisfy the accept-set-wide set rule as committed.

    This is what makes the extension retroactive at zero cost -- no restamp, no
    stale cassette, no member removed.
    """
    offenders = screen_mod.items_without_a_clean_member(items)
    assert offenders == ["C22-01"], (
        "§3.6.2 asserts exactly one item lacks a clean member, adjudicated under "
        f"carve-out 1. Got {offenders!r}. A NEW offender is a new adjudication owed, "
        "not something this rule absorbs silently."
    )
    assert len(items) - len(offenders) == 35


def test_c22_01_clears_because_its_span_names_the_thing_notice(items):
    """Carve-out 1 is content-relative to the item's own span, never a blacklist
    against ACTIONS. The clearing fact is textual, so it is asserted textually."""
    c22 = next(i for i in items if i["item_id"] == "C22-01")
    assert c22["action"] == "NOTIFY"
    assert c22["object_class"] == "notice"
    # The document's own word for the object, twice, inside the span itself.
    assert c22["span_text"].count("notice") == 2
    # And it is the hardest instance: a 1-token label whose ENTIRE content is the
    # action nominal, with no member escaping it -- unlike C02-01/C14-01, where the
    # restating token modifies a distinct head noun.
    assert all(screen_mod.restates(m, "NOTIFY") for m in c22["object_class_accept_set"])


def test_f12_scope_exposure_is_three_items_not_one(items):
    """The queue row's "exactly ONE" filled the slot x accept-set-verb cell. The
    member x accept-set-verb cell had never been measured, and holds two more."""
    hits = screen_mod.screen(items)
    assert {h[0] for h in hits["accept_set_verb"]} == {"C04-01", "C04-04", "C14-01"}
    # C04-04 reproduces the recorded slot-side instance exactly.
    slot_side = [h for h in hits["accept_set_verb"] if h[1] == "SLOT"]
    assert [(h[0], h[2], h[3]) for h in slot_side] == [
        ("C04-04", "self_regulatory_compliance", "COMPLY")
    ]


def test_the_widening_only_rule_still_holds_no_member_was_removed(items):
    """§3.6.1's `C04-03` reason, pinned. `product_delivery` restates `DELIVER` and
    `C04-087` run 2 emits exactly it, so stripping restating members retroactively
    would flip a passing clause 5 to failing -- §3.4's prohibition running in the
    direction that can only manufacture failures."""
    c04_03 = next(i for i in items if i["item_id"] == "C04-03")
    assert "product_delivery" in c04_03["object_class_accept_set"]
    assert c04_03["action"] == "DELIVER"


# --------------------------------------------------------------------------
# (4) F5's forward/retroactive boundary
# --------------------------------------------------------------------------

def test_head_only_coverage_reproduces_the_anchor_at_n36(items):
    """§3.6/Ruling 3's v0.45 anchor was measured at n=32 (12/32 = 38%). Four items
    have been added since, so the figure is re-measured rather than assumed to
    survive: 13/36 = 36%, against the model emitting head-only 28% of the time."""
    carried, total = census_mod.head_only_coverage(items)
    assert (carried, total) == (13, 36)


def test_the_head_only_rule_is_forward_only_and_restamped_nothing(items):
    """F5 REFUSED the retroactive pass, so the 23 locked items without a head-only
    member are expected to stay that way.

    This test exists to fail if someone "helpfully" conforms them: that would
    silently convert a forward rule into the systematic retroactive pass F5 declined,
    widening 23 sets with the clause-5 failure list visible -- §3.4's prediction-
    fitting shape, for a gain measured at zero on the in-force criterion.
    """
    without = [i["item_id"] for i in items if not census_mod.has_head_only_member(i)]
    assert len(without) == 23
    # Two of the three head-only-mechanism items genuinely carry no 1-token member.
    for item_id in ("C02-01", "E01-01"):
        assert item_id in without
    # Their failure is worth nothing on the in-force criterion: E01-01 carries
    # known_gaps (outside §9.1's denominator) and C02-01 already passes clause 5 on
    # runs 2-3. Anchors the "worth zero" claim to actual items.
    by_id = {i["item_id"]: i for i in items}
    assert by_id["E01-01"]["known_gaps"]


def test_c04_03_passes_the_mechanical_head_only_check_and_still_fails(items):
    """§3.6 bound 3's worked counter-example, and the reason that bound says PARTLY
    auditable rather than auditable.

    A first draft of this very test asserted C04-03 had NO head-only member. It
    failed, and the assertion was wrong, not the data: the set carries `goods`, which
    is 1 token AND present in the span ("the shipped goods"). So the mechanical check
    -- exists, and is span-present -- passes. The object phrase is "Each quantity of
    Miltenyi Product(s)", the head noun is `product`, the model emits exactly
    `product`, and the set holds it only inside the 2-token `miltenyi_product`.

    Pinned so nobody later "simplifies" the head-only rule down to the mechanical
    check, which would mark this item compliant while changing nothing about it.
    """
    c04_03 = next(i for i in items if i["item_id"] == "C04-03")
    assert census_mod.has_head_only_member(c04_03)
    assert "goods" in c04_03["object_class_accept_set"]
    assert "goods" in c04_03["span_text"].lower()
    # The noun the rule actually asks for is absent as a standalone member.
    assert "product" not in c04_03["object_class_accept_set"]
    assert "miltenyi_product" in c04_03["object_class_accept_set"]


def test_c17_01_is_not_treated_as_a_breadth_case(items):
    """The rule's first bound: a head-only member is the HEAD NOUN of the object
    phrase, not any 1-token label the model emits. `C17-01`'s `efforts` is a genuine
    model error -- no reading of "virus prevention" yields it -- and widening to admit
    it would make clause 5, the only check on an open vocabulary, meaningless."""
    c17 = next(i for i in items if i["item_id"] == "C17-01")
    assert "efforts" not in c17["object_class_accept_set"]
    assert c17["object_class"] == "virus_prevention"


def test_f1s_three_queued_widenings_have_not_silently_landed(items):
    """F5's ruling AUTHORISES and SIZES F1; it does not execute it.

    F1 is worth a measured +2 on a 9-item denominator (`3/9` -> `5/9`), which is large
    enough that landing it outside one atomic freeze-pass event would make the next
    criterion-2 delta uninterpretable -- pipeline improvement and a loosened bar become
    indistinguishable. So the widenings must still be ABSENT here, and this test is the
    guard on that sequencing rather than a statement about their merit.
    """
    by_id = {i["item_id"]: i for i in items}
    assert "invoice_costs" not in by_id["C02-03"]["object_class_accept_set"]
    assert "principal_interest" not in by_id["C11-01"]["object_class_accept_set"]
    assert "Antares or its Subcontractor" not in (by_id["C02-01"].get("obligor_accept_set") or [])
