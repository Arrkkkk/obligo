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


# --- the v0.58 population, pinned so a later batch cannot re-baseline it -----
#
# §3.6.2's "35 of 36" and §3.6/F5's "13/36" are DATED published figures from the
# v0.58 rulings. Batch 4 (v0.62) adds 12 items, and letting these assertions
# read the live tree would silently recompute a published measurement over gold
# the ruling never saw -- the exact defect v0.53 fixed for `K` by deriving its
# population from the sealed `comparison.json`, and the one F19 found in `G`,
# where a published figure survived three drifts BY COINCIDENCE.
#
# There is no sealed artifact for these two, so the population is frozen here by
# stamp instead: every item annotated at or before v0.57. A NEW batch is outside
# it by construction, and `test_the_v058_population_is_exactly_the_36` fails
# loudly if an item ever leaves it.
# Derived from the committed tree, not from memory: an INCLUDE-list, so a future
# batch's stamp is outside it automatically rather than needing this line edited.
V058_STAMPS = frozenset({"v0.28", "v0.38", "v0.41", "v0.44", "v0.48", "v0.52",
                         "v0.53", "v0.55", "v0.57"})


def _v058_population(items):
    """The 36 items §3.6.2's and §3.6's v0.58 figures were measured over."""
    return [i for i in items if i["guideline_version"] in V058_STAMPS]


def test_the_v058_population_is_exactly_the_36_the_rulings_measured(items):
    """The guard that makes the two scoped figures below trustworthy.

    A population that silently grew or shrank would make them reproduce a
    DIFFERENT measurement while still printing the published number -- which is
    precisely how `G` stayed at 6/31 through four item drifts without anyone
    noticing (§10.1 F20).
    """
    pop = _v058_population(items)
    assert len(pop) == 36, (
        f"the v0.58 population must stay at the 36 items those rulings measured; "
        f"got {len(pop)}. If an item was legitimately restamped, this frozen set "
        f"needs a reasoned update, not a bumped number."
    )
    assert len(items) > len(pop), (
        "this scoping is pointless if the live set has not grown past it"
    )


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
    # The offenders assertion is a LIVE invariant and stays live on purpose: a
    # new offender in ANY batch is a new adjudication owed, which is what this
    # message says and what makes the test worth having.
    offenders = screen_mod.items_without_a_clean_member(items)
    assert offenders == ["C22-01"], (
        "§3.6.2 asserts exactly one item lacks a clean member, adjudicated under "
        f"carve-out 1. Got {offenders!r}. A NEW offender is a new adjudication owed, "
        "not something this rule absorbs silently."
    )
    # The COUNT is the dated v0.58 headline and is scoped to its own population.
    pop = _v058_population(items)
    assert len(pop) - len([o for o in offenders if o in {i["item_id"] for i in pop}]) == 35


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
    hits = screen_mod.screen(_v058_population(items))
    assert {h[0] for h in hits["accept_set_verb"]} == {"C04-01", "C04-04", "C14-01"}
    # C04-04 reproduces the recorded slot-side instance exactly.
    slot_side = [h for h in hits["accept_set_verb"] if h[1] == "SLOT"]
    assert [(h[0], h[2], h[3]) for h in slot_side] == [
        ("C04-04", "self_regulatory_compliance", "COMPLY")
    ]


def test_e08_03_is_a_new_accept_set_verb_hit_and_clears_under_carve_out_1(items):
    """Batch 4 adds ONE accept-set-verb hit, and it is disclosed rather than
    absorbed into F12's dated three.

    `E08-03`'s `dispute_notice` restates `NOTIFY`, which sits in its own
    `action_accept_set` -- exactly the cell F12 measured. It CLEARS under
    §3.6.2's carve-out 1 on the same ground as `C22-01`: the span reads "written
    NOTICE", the document's own word for the thing, so the label names the object
    rather than restating the duty. The item is NOT a §3.6.2 offender -- its set
    carries clean members -- so the set rule holds and no adjudication is owed.

    This is §3.6.2's accepted cognate-object residue, which that section rules is
    irreducible rather than a defect to design around: for NOTIFY/notice, clauses
    2 and 5 co-vary because the object of the duty simply IS the action's nominal.
    """
    hits = screen_mod.screen(items)
    live = {h[0] for h in hits["accept_set_verb"]}
    dated = {h[0] for h in screen_mod.screen(_v058_population(items))["accept_set_verb"]}
    assert live - dated == {"E08-03"}, (
        f"batch 4 should add exactly one accept-set-verb hit; got {sorted(live - dated)}"
    )
    assert "E08-03" not in screen_mod.items_without_a_clean_member(items)
    e08 = next(i for i in items if i["item_id"] == "E08-03")
    assert screen_mod.restates("dispute_notice", "NOTIFY") == ["notice"]
    assert "notice" in e08["span_text"], "carve-out 1 needs the span to name the thing"


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
    carried, total = census_mod.head_only_coverage(_v058_population(items))
    assert (carried, total) == (13, 36)


def test_the_forward_head_only_rule_is_satisfied_by_every_batch_4_item(items):
    """§3.6's v0.58 rule binds batch 4 onward, and this is the first batch it
    reaches -- so it is checked by execution rather than assumed from the notes.

    The dated 13/36 anchor above says what the rule found when it was written;
    this says whether it is actually being followed. Both are needed: a forward
    rule nobody verifies is the "indirection only as real as the tests that
    don't bypass it" shape CLAUDE.md's debt list already records three times.
    """
    # v0.65: the rule binds batch 4 ONWARD, so this population is every
    # post-v0.58 item and GROWS with each batch. An equality here would make
    # every future batch look like a defect -- the same population-pinning
    # hazard v0.53's K fix and F20's `G` finding both record. A floor keeps the
    # vacuity gate (an empty `new` would pass the real assertion below).
    new = [i for i in items if i["guideline_version"] not in V058_STAMPS]
    assert len(new) >= 12, f"expected at least batch 4's 12 items, got {len(new)}"
    without = [i["item_id"] for i in new if not census_mod.has_head_only_member(i)]
    assert without == [], (
        f"§3.6's forward head-only rule is mandatory from batch 4: {without} carry no "
        f"head-only member. The only permitted exemption is §3.6.2's cognate-object "
        f"case, which must be argued per item, not defaulted."
    )
    # LIVE by design, unlike the dated `_v058_population` anchor above it: this
    # moves with every batch and is re-measured, never carried forward.
    # v0.62: 25/48. v0.65: 27/50 -- batch 5's E02-01 ("data") and E02-02
    # ("invoice") each carry a head-only member.
    carried, total = census_mod.head_only_coverage(items)
    assert (carried, total) == (27, 50)


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


def test_f1s_three_widenings_have_landed_together(items):
    """F1 EXECUTED v0.62, as ONE atomic event -- the sequencing F5 made binding.

    This test previously asserted the opposite (`..._have_not_silently_landed`), because
    F5's ruling authorised and SIZED F1 without executing it. F1 is worth a measured +2,
    large enough that landing it across two published baselines would make the next
    criterion-2 delta uninterpretable -- pipeline improvement and a loosened bar become
    indistinguishable. The guard is therefore ALL-THREE-OR-NONE in both directions: it
    fails if any one is missing, which is what "atomic" has to mean once they are in.

    Values, not just presence, because a member is only the widening it was authorised as
    if it is the exact string §3.5.1/§3.6 named.
    """
    by_id = {i["item_id"]: i for i in items}
    assert "invoice_costs" in by_id["C02-03"]["object_class_accept_set"]
    assert "principal_interest" in by_id["C11-01"]["object_class_accept_set"]
    assert "Antares or its Subcontractor" in (by_id["C02-01"].get("obligor_accept_set") or [])


def test_f1_widened_monotonically_and_restamped_nothing(items):
    """Two bounds §3.4 puts on the exception, both mechanically checkable.

    (1) WIDENING-ONLY: every member each set held before F1 is still there. A freeze-pass
        widening that quietly dropped a member would be §3.4's forbidden direction.
    (2) NOT RESTAMPED, and this is measured rather than stylistic: restamping the three
        stales their cassettes and reads `3/7 = 42.9%` -- the numerator does not move at
        all, both movers drop out of the denominator, and the figure "improves" purely by
        shrinking. That is the shape F19 refused ("a published figure improving for no
        improvement"), so the stamps are held at `v0.28`.
    """
    by_id = {i["item_id"]: i for i in items}
    assert set(by_id["C02-03"]["object_class_accept_set"]) >= {
        "retention_costs", "invoice", "costs", "service_costs"}
    assert set(by_id["C11-01"]["object_class_accept_set"]) >= {
        "franchise_interest", "equity_interest", "ownership_interest"}
    assert set(by_id["C02-01"]["obligor_accept_set"]) >= {"Antares", "its Subcontractor"}
    for iid in ("C02-01", "C02-03", "C11-01"):
        assert by_id[iid]["guideline_version"] == "v0.28", (
            f"{iid} was restamped; F1 holds every stamp -- see §3.4's v0.62 execution note")


def test_c11_01_is_the_widening_worth_zero_on_criterion_2(items):
    """Stated as a test rather than only in prose, because it is the F1 finding most
    likely to be misremembered: the item this project cites most often as breadth's
    motivating case is the one widening that moves criterion 2 by NOTHING.

    `C11-01` fails `conditions` and `obligee` independently of `object_class`, so removing
    one of three failing clauses leaves its modal outcome `PARTIAL`. The measured movers
    are `C02-01` and `C02-03`, each of which had `object_class`/`obligor` as its ONLY
    failing clause.
    """
    c11 = next(i for i in items if i["item_id"] == "C11-01")
    assert c11["obligee"] == "ABSENT"
    assert len(c11["conditions"]) == 2
    assert "principal_interest" in c11["object_class_accept_set"]
