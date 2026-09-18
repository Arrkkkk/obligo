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
    DIRECTION_BEARING_KINDS,
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


def test_direction_is_defined_for_exactly_the_direction_bearing_tags():
    """F10's resolution, stated as an invariant rather than as a comment: a tag
    of a kind where gold does NOT depart from the document has no direction BY
    RULING. If someone adds a direction for a REACHABILITY or CORPUS_DEFECT tag,
    that is the masquerade F10 was filed separately to prevent, and it fails
    here.

    v0.60 (F18) widens the set from REPRESENTATIONAL alone to
    DIRECTION_BEARING_KINDS. The assertion is deliberately written against that
    constant rather than against a literal pair of kind names: the v0.59 version
    of this test hardcoded "REPRESENTATIONAL", which is exactly the shape
    CLAUDE.md's debt list calls "a test pinning the very thing the mechanism
    exists to vary"."""
    bearing = {t for t, k in GAP_KIND.items() if k in DIRECTION_BEARING_KINDS}
    assert set(GAP_DIRECTION) == bearing


def test_withheld_value_is_direction_bearing_because_gold_departs_from_the_document():
    """§8.10.1's principle, pinned: direction is assignable wherever gold departs
    from the document -- REPRESENTATIONAL (the IR has no form) and
    WITHHELD_VALUE (§8.1 rules the field null though the IR HAS the form). The
    other three kinds must stay direction-free."""
    assert DIRECTION_BEARING_KINDS == {"REPRESENTATIONAL", "WITHHELD_VALUE"}
    assert direction_of("redacted_value") == "INCOMPLETENESS"
    for kind in ("REACHABILITY", "CORPUS_DEFECT", "ANNOTATION_CONVENTION"):
        assert kind not in DIRECTION_BEARING_KINDS


@pytest.mark.parametrize("tag,expected", [
    ("exception_unsupported", "OVERSTATING"),
    ("compound_action", "INCOMPLETENESS"),
    ("action_not_in_taxonomy", "INCOMPLETENESS"),
    ("within_preposition", None),
    ("relative_trigger_preposition", None),
    ("corpus_artifact_in_span", None),
    ("shared_subject_split", None),
    # v0.60 (F18): was None, now ruled INCOMPLETENESS -- §8.1 sets the field null
    # for a clause the document states IS constrained, so the IR claims less.
    ("redacted_value", "INCOMPLETENESS"),
])
def test_f10s_tags_resolve_to_no_direction_and_the_direction_bearing_ones_keep_theirs(tag, expected):
    assert direction_of(tag) == expected


def test_None_and_UNCLASSIFIED_are_different_answers_and_do_not_collapse():
    """None means "this kind has no direction to assign"; UNCLASSIFIED means "a
    decision is owed". Collapsing them would let a genuinely unruled tag hide
    among the deliberately direction-free ones."""
    assert direction_of("corpus_artifact_in_span") is None       # ruled: no direction
    assert direction_of("some_future_tag") is None               # unruled kind -> not direction-bearing
    assert kind_of("some_future_tag") == UNCLASSIFIED_KIND       # ...but the KIND is owed
    assert kind_of("corpus_artifact_in_span") != UNCLASSIFIED_KIND


# --- the denominator predicate ----------------------------------------------

@pytest.mark.parametrize("tags,expected,why", [
    ([], True, "untagged items are in, unchanged"),
    (["corpus_artifact_in_span"], True, "CORPUS_DEFECT enters (§9.1 ground 1)"),
    (["shared_subject_split"], True, "ANNOTATION_CONVENTION enters"),
    (["mutual_obligation"], False, "REPRESENTATIONAL excluded (ground 2)"),
    (["within_preposition"], False, "REACHABILITY excluded (guaranteed failure)"),
    (["redacted_value"], False, "WITHHELD_VALUE RULED excluded v0.60 (F18) on ground 2"),
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


def test_E03_01_stays_excluded_and_v060_made_that_a_RULING_not_a_hold(gold_items):
    """Pinned so it cannot be quietly flipped: `redacted_value` is its own kind
    AND stays out of the denominator. If someone admits it, the in-force figure
    moves 3/10 -> 3/11 and this test is the thing that says so.

    v0.60 (F18) changes the REASON without changing the membership: the kind is
    now excluded by ruling, on §9.1 ground 2, because it carries a direction.
    Both halves are asserted, because "excluded" alone would still pass if the
    direction were silently reverted to None -- and that revert is precisely what
    would reopen the question this ruling closed.

    EXTENDED v0.61 (F19), NOT relaxed. The item now carries a SECOND excluding
    tag, so `in_force_scope(e03["known_gaps"]) is False` would pass even if
    v0.60's ruling were reverted -- the assertion would go vacuous exactly
    where it is load-bearing. The fix is to test `redacted_value` ALONE for the
    v0.60 half, so this test keeps failing if that ruling is undone, and to
    assert the item's full tag set separately for the F19 half."""
    e03 = next(i for i in gold_items if i["item_id"] == "E03-01")
    assert sorted(e03["known_gaps"]) == ["lead_time_unrepresentable", "redacted_value"]
    assert GAP_KIND["redacted_value"] == "WITHHELD_VALUE"
    assert direction_of("redacted_value") == "INCOMPLETENESS"
    # v0.60's ruling, checked on its own tag so F19's tag cannot carry it.
    assert in_force_scope(["redacted_value"]) is False
    assert in_force_scope(e03["known_gaps"]) is False


def test_E03_01_gold_asserts_a_null_temporal_which_is_what_the_ruling_turns_on(gold_items):
    """§8.10.1's factual premise, pinned against the committed item rather than
    restated in prose: §8.1 sets the field null and names it in `missing_fields`,
    and `redacted_phrase` holds the literal withheld text. The ruling is that the
    first of those three is all §5's predicate can see -- so if a future edit
    moved `temporal` off null, the ground-2 argument would no longer apply and
    this test should be revisited rather than deleted."""
    e03 = next(i for i in gold_items if i["item_id"] == "E03-01")
    assert e03["temporal"] is None
    assert "temporal" in e03["missing_fields"]
    assert e03["redacted_phrase"].startswith("At least ** before the **")


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


def test_G6_buckets_a_redacted_value_item_under_INCOMPLETENESS_not_under_its_kind():
    """v0.60 (F18): the one live WITHHELD_VALUE tag now carries a direction, so a
    numerator item carrying it surfaces as a DIRECTION, alongside the
    representational incompleteness cases rather than in a kind-named bucket."""
    rep = _report([("A-01", Outcome.FULLY_CORRECT, ["redacted_value"])])
    out = rep.render()
    assert "INCOMPLETENESS: A-01 (redacted_value)" in out
    assert "WITHHELD_VALUE: A-01" not in out


def test_the_WITHHELD_VALUE_bucket_is_unreachable_and_an_unruled_one_routes_to_UNCLASSIFIED():
    """The consequence of the v0.60 ruling that was found BY EXECUTION rather
    than reasoned about, and that an earlier draft of the amendment got wrong in
    prose before this test existed.

    For any tag of a direction-bearing kind, `direction_of` returns a direction
    or UNCLASSIFIED and NEVER None -- so report.py's `else kind_of(tag)` branch
    cannot fire for it and the WITHHELD_VALUE bucket is dead. That is why the
    bucket was removed from `order` rather than left standing: a bucket kept
    after it can no longer be reached reads as "no such items" when it actually
    means "no such path".

    The routing that replaces it is the CORRECT one and is pinned here: a future
    withheld-value tag with no ruled direction lands in UNCLASSIFIED, which is
    exactly "a decision is owed" and the same treatment a new REPRESENTATIONAL
    tag already gets."""
    GAP_KIND["hypothetical_withheld"] = "WITHHELD_VALUE"
    try:
        assert direction_of("hypothetical_withheld") == UNCLASSIFIED_KIND
        assert direction_of("hypothetical_withheld") is not None
        rep = _report([("A-01", Outcome.FULLY_CORRECT, ["hypothetical_withheld"])])
        out = rep.render()
        assert f"{UNCLASSIFIED_KIND}: A-01 (hypothetical_withheld)" in out
        assert "WITHHELD_VALUE: A-01" not in out
        # ...and it still excludes from the denominator, by KIND, with no
        # direction ruled -- the loud default is not weakened by the routing.
        assert in_force_scope(["hypothetical_withheld"]) is False
    finally:
        del GAP_KIND["hypothetical_withheld"]


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


# --- v0.61 (F19): lead_time_unrepresentable --------------------------------
#
# These tests check the RULING'S OWN FACTUAL CLAIMS against the production IR,
# not just the bookkeeping. Section 8.11 argues from what the five temporal
# forms can hold; if that ever stops being true the ruling is wrong and these
# must fail rather than the prose quietly going stale.

def test_lead_time_tag_is_representational_and_incompleteness():
    assert GAP_KIND["lead_time_unrepresentable"] == "REPRESENTATIONAL"
    assert direction_of("lead_time_unrepresentable") == "INCOMPLETENESS"
    assert in_force_scope(["lead_time_unrepresentable"]) is False


def test_no_v1_temporal_form_pairs_a_duration_with_a_direction():
    """Section 8.11's DECISIVE claim, and the reason the gap is single-form
    rather than compositional: composition joins whole forms, so if no form
    holds {duration, direction} then no composition of forms can express a
    lead time either. Asserted against the real dataclasses."""
    import dataclasses
    from obligo_brain.compiler import ast

    forms = [ast.ByTemporal, ast.WithinTemporal, ast.EveryTemporal,
             ast.DuringTemporal, ast.RelativeToTriggerTemporal]
    slots = {f.__name__: {x.name for x in dataclasses.fields(f)} for f in forms}

    assert not [n for n, s in slots.items() if {"duration", "direction"} <= s]
    assert not [n for n, s in slots.items() if {"duration", "direction", "trigger"} <= s]
    # The two halves exist, just never together -- which is what makes this an
    # expressiveness gap rather than a missing feature nobody noticed.
    assert {n for n, s in slots.items() if "duration" in s} == {
        "WithinTemporal", "EveryTemporal"}
    assert {n for n, s in slots.items() if "direction" in s} == {
        "RelativeToTriggerTemporal"}


def test_a_lead_time_phrase_does_not_classify_but_its_stripped_form_does():
    """The gap is the DURATION, pinned by difference rather than asserted: the
    same phrase classifies once the lead time is removed, which is exactly the
    content the IR loses and why the direction is INCOMPLETENESS."""
    from obligo_brain.compiler.ir_compile import _classify_temporal as classify

    assert classify("at least 30 days before the first day of each Calendar Quarter") is None
    assert classify("30 days before the first day of each Calendar Quarter") is None
    assert classify("before the first day of each Calendar Quarter") == (
        'BEFORE "the first day of each Calendar Quarter"')


def test_E03_01s_temporal_fails_even_unredacted():
    """F19's conclusion, which SURVIVED the mechanism correction. Checked on a
    plausible unredacted phrase as well as the redacted one, because the whole
    question was whether the redaction is doing the work. It is not."""
    from obligo_brain.compiler.ir_compile import _classify_temporal as classify

    assert classify(
        "At least ** before the ** of each Calendar Quarter "
        "during the Term of this Supply Agreement") is None
    assert classify(
        "At least thirty (30) days before the first day of each Calendar Quarter "
        "during the Term of this Supply Agreement") is None


def test_the_recurrence_operand_the_annotator_claimed_is_not_available_either():
    """Section 8.11 ground (a). `EVERY` is only reachable for this clause via a
    paraphrase gold never performed -- `Duration` has no UNRESOLVED variant, so
    a recurrence named by a defined term has no form."""
    import dataclasses
    from obligo_brain.compiler import ast
    from obligo_brain.compiler.ir_compile import _classify_temporal as classify

    assert classify("each Calendar Quarter") is None
    assert classify("every Calendar Quarter") is None
    assert classify("every 3 months") == "EVERY 3mo"  # the paraphrase, for contrast
    assert {f.name for f in dataclasses.fields(ast.Duration)} == {"amount", "unit"}


def test_EVERY_plus_DURING_is_unmappable_on_the_extraction_path():
    """The guideline's corrected section 8 row, and the FOURTH tracked instance
    of a grammar-layer guarantee the extraction path bypasses. Both halves are
    asserted together, because the row was wrong precisely by stating one and
    being read as the other."""
    import warnings
    from obligo_brain.compiler.ir_compile import _classify_temporal as classify
    from obligo_brain.compiler.parser import parse

    # extraction path: no form matches at all
    assert classify("every 30 days during 2026-01-01 .. 2026-12-31") is None
    assert classify("every 30 days during the Term") is None

    # grammar path: the warn-and-degrade guarantee is REAL, just unreachable
    dsl = ('MUST "A" PROVIDE "B" rep "r" EVERY 30d DURING 2026-01-01 .. 2026-12-31 '
           "11111111-1111-1111-1111-111111111111 0 5 0.9")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        obligation = parse(dsl)
    assert obligation.temporal.duration.amount == 30
    assert any("cannot represent" in str(w.message) for w in caught)


def test_every_ruled_kind_is_a_tag_section_8_recognises():
    """The two hand-maintained copies of §8's vocabulary must not drift apart.

    Found the hard way at v0.61: adding `lead_time_unrepresentable` to GAP_KIND
    alone left `annotator_agreement.SECTION_8_TAGS` stale, which marked E03-01
    NON_CONFORMING and moved `A` -- a failure in a DIFFERENT instrument from the
    one the tag was added for, and one no test in this file would have caught.

    The invariant is the SUBSET direction, not equality: SECTION_8_TAGS is
    deliberately wider, holding tags §8 defines but no item uses yet."""
    from evals.harness.annotator_agreement import SECTION_8_TAGS

    unrecognised = sorted(set(GAP_KIND) - SECTION_8_TAGS)
    assert unrecognised == [], (
        f"tags with a ruled §8.10 kind that SECTION_8_TAGS does not recognise: "
        f"{unrecognised}. Add them there too, or gold items carrying them are "
        "silently NON_CONFORMING."
    )
