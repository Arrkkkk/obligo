"""Section 5.1's predicate `A`, proven against known answers before its own
numbers are used (Standing Principle 7).

THE LOAD-BEARING TESTS ARE THE REPRODUCTIONS, not the planted cases. `A` exists
to replace the comparison that produced `K = 14/32` on 2026-08-29, and that
comparison's script was NEVER PRESERVED -- the defect
`evals/goldens/holdout/audit/README.md` was written about, and the reason
`RESULTS.md` Finding 2's counts are not re-derivable at all. So this module is
required to reproduce the published run EXACTLY, per item and per clause, in
its `symmetric=False, gate=False` legacy form, before any corrected number it
produces is trusted. An aggregate match would not be enough: the struck
reproduction in `OBJECT_CLASS_INVESTIGATION.md` section 0 matched a published
aggregate while carrying two errors that cancelled.
"""

from __future__ import annotations

import ast
import copy
import glob
import json
from pathlib import Path

import pytest

from obligo_brain.compiler.ast import ACTIONS

from evals.harness.annotator_agreement import (
    Agreement,
    SECTION_8_TAGS,
    compare_clauses,
    compute,
    conformance_failures,
    pair_items,
)
from evals.harness.gap_agreement import GapPair, compute_gap_agreement

GOLD_DIR = Path(__file__).resolve().parents[2] / "evals" / "goldens"
HOLDOUT_DIR = GOLD_DIR / "holdout"

# Gold values as they stood when the 2026-08-29 comparison was computed, for
# every item RETROACTIVELY RESTAMPED since. Reproducing the published
# per-clause result requires them, and keeping them here rather than reaching
# into git is what makes each restamp's effect on `A` executable rather than
# merely asserted in prose.
#
# Two restamps are represented, and both are instances of the SAME rule --
# section 3.6.1's v0.45 forward requirement that a retroactive edit state its
# effect on BOTH predicates, because section 5 and `A` have OPPOSITE
# sensitivities: section 5 clause 5 never reads gold's slot, while `A` compares
# it directly.
#
#   C10-01, C10-02  v0.40 -> v0.44, section 3.6.1's slot correction.
#                   Moved the published `5_object` count 6 -> 5 of 23.
#   C17-02          v0.28 -> v0.52, section 8.6.1 / section 10.1 F13's
#                   representable-vs-reachable ruling: `temporal` null -> the
#                   WITHIN form. The cold annotator annotated this span under
#                   section 8.6 AS WRITTEN (temporal null) and its output is
#                   sealed, so gold moving flips clause 6 from agree to
#                   disagree. Published `6_temporal` count 2 -> 3 of 23.
#                   K is UNCHANGED at 14/32 -- C17-02 already disagreed on
#                   2_action -- and under the IN-FORCE predicate `A` the item
#                   is NON_CONFORMING anyway (cold's action slot OBTAIN is
#                   off-taxonomy, section 5.1 A1), so it sits outside both K
#                   and n there and A's 7/27 does not move either.
#
# THE ASSERTION BELOW IS NOT WEAKENED BY EITHER ENTRY. The published run must
# still reproduce EXACTLY, item by item and clause by clause; what this map
# does is hold the inputs it was computed from, so a later retroactive ruling
# cannot quietly erase the record it is supposed to be checked against.
PRE_RESTAMP = {
    # v0.62 (F1). `C10-01` HELD TWO SEPARATE ENTRIES UNDER ONE KEY AND PYTHON
    # KEPT ONLY THE SECOND. The v0.44 slot correction below was written here at
    # v0.45 and then SILENTLY OVERWRITTEN at v0.61, when F19's `known_gaps`
    # block reused the same key further down the literal -- so from v0.61 until
    # now `PRE_RESTAMP["C10-01"]` held `known_gaps` ALONE and the sealed
    # `object_class` values were dead. Merged into one entry here.
    #
    # It was INERT, and that is stated rather than glossed: measured both ways
    # against the sealed artifact, `C10-01` fails `5_object` either way, so K
    # reproduced at 14/32 with the correct per-clause profile throughout and no
    # published figure was ever wrong. What was lost is the GUARD -- had
    # `C10-01`'s live `object_class_accept_set` ever been widened (exactly what
    # this commit does to three other items), the reproduction would have
    # drifted with nothing holding its inputs. `test_pre_restamp_has_no_duplicate
    # _keys` below reads this file's own source so the class cannot recur.
    "C10-01": {
        "object_class": "product_liability_indemnification",
        "object_class_accept_set": [
            "product_liability_indemnification", "distributor_liability_indemnification",
            "design_defect_liability", "relevant_claim_indemnification",
        ],
        "known_gaps": ["compound_action", "exception_unsupported"],  # F11
    },
    # v0.62 (F1). The accept-set widening is invisible to the PIPELINE's
    # criterion-2 baseline (§5 clause 5 reads gold's SET, and widening it is the
    # whole point) but VISIBLE to `A`, which compares slots by mutual
    # membership -- so without this entry the published legacy profile would
    # drift `5_object` 6 -> 5. `K` itself is unmoved at 14/32 either way:
    # `C11-01` disagrees on `obligee` and `obligor` independently. Same
    # mechanism as the two restamps above, applied to a widening rather than a
    # restamp -- the item is NOT restamped (see §3.4's v0.62 execution note).
    "C11-01": {
        "object_class_accept_set": [
            "franchise_interest", "equity_interest", "ownership_interest",
        ],
    },
    "C10-02": {
        "object_class": "distributor_insurance_certificate_listing",
        "object_class_accept_set": [
            "distributor_insurance_certificate_listing", "insurance_certificate_addition",
            "additional_insured_designation",
        ],
    },
    "C17-02": {
        "temporal": None,
    },
    # v0.61 (F19). `known_gaps` is not one of §5's eight clauses, so these four
    # entries are invisible to K and to `A` -- they exist for the ONE test in
    # this file that computes G, which reads tags directly. Sealed values
    # measured at commit 628f67c, not reconstructed from the rulings' prose.
    # Kept here rather than in a second map so there is one answer to "what did
    # gold look like on 2026-08-29", whichever instrument is asking.
    "C04-02": {"known_gaps": ["mutual_obligation"]},                      # F7
    # F11's `C10-01` entry is MERGED INTO THE `C10-01` ENTRY ABOVE at v0.62 --
    # repeating the key here is what silently killed the v0.44 slot correction.
    "E01-01": {"known_gaps": ["exception_unsupported"]},                  # F8
    "E03-01": {"known_gaps": ["redacted_value"]},                         # F19
}

# The published run's clause names, in section 5's numbering.
PUBLISHED_CLAUSE = {
    "modality": "1_modality", "action": "2_action", "obligor": "3_obligor",
    "obligee": "4_obligee", "object_class": "5_object", "temporal": "6_temporal",
    "conditions": "7_conditions", "underspecified": "8_underspec",
}


def published_population() -> frozenset[str]:
    """The 32 gold items the published §7 run actually compared, read off the
    SEALED artifact rather than hardcoded as a count.

    Why this exists (v0.53). Every reproduction below pins a PUBLISHED, DATED
    measurement -- `K = 14/32` and the §5.1 `A` figures, computed 2026-08-29
    against a sealed cold annotation. `_load_gold` globs the live gold
    directory, so the moment a later session drafts a new item the reproduction
    silently compares a population the published run never had. That is not a
    stale assertion to bump: cold annotated at BOTH spans the v0.53 drafting
    session turned into `C11-02` and `C04-06`, so those items PAIR, and simply
    updating 32 -> 34 would have moved a published K by retroactively adding
    gold the run never saw.

    Deriving the set from `comparison.json` rather than listing it keeps the
    pin correct for every future addition automatically, and it fails LOUDLY
    (see the guard in `_load_gold`) if an item in the published run ever goes
    missing from disk -- the failure a hardcoded count cannot distinguish from
    an addition. Same discipline as `PRE_RESTAMP` above: the reproduction is
    extended to keep reproducing, never relaxed to keep passing.

    A future §7 re-run is a DIFFERENT measurement over the current set and must
    not reuse this scope -- see `test_new_items_are_outside_the_published_run`.
    """
    raw = json.loads((HOLDOUT_DIR / "comparison.json").read_text())
    return frozenset(r["item"] for r in raw["rows"])


def _load_gold(pre_restamp: bool = False, scope: frozenset[str] | None = None,
               ) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    seen: set[str] = set()
    for path in glob.glob(str(GOLD_DIR / "batch0*" / "items" / "*.json")):
        item = json.loads(Path(path).read_text())
        if scope is not None and item["item_id"] not in scope:
            continue
        if pre_restamp and item["item_id"] in PRE_RESTAMP:
            item = {**item, **PRE_RESTAMP[item["item_id"]]}
        seen.add(item["item_id"])
        out.setdefault(item["segment_id"], []).append(item)
    if scope is not None and seen != set(scope):
        raise AssertionError(
            "published-run scope no longer matches the gold set on disk; "
            f"missing from disk: {sorted(set(scope) - seen)}"
        )
    return out


def _load_cold() -> dict[str, list[dict]]:
    out = {}
    for path in sorted(glob.glob(str(HOLDOUT_DIR / "cold" / "*.json"))):
        rec = json.loads(Path(path).read_text())
        out[rec["segment_id"]] = rec["items"]
    return out


@pytest.fixture(scope="module")
def gold():
    """Scoped to the PUBLISHED run's 32 items -- every test in this file
    reproduces a dated, published figure. See `published_population`."""
    return _load_gold(scope=published_population())


@pytest.fixture(scope="module")
def cold():
    return _load_cold()


@pytest.fixture(scope="module")
def published_rows():
    raw = json.loads((HOLDOUT_DIR / "comparison.json").read_text())
    return {r["item"]: r for r in raw["rows"]}


# --------------------------------------------------------------------------
# Known-answer reproduction. Nothing below this line is trustworthy until
# these two pass.
# --------------------------------------------------------------------------

def test_pre_restamp_has_no_duplicate_keys():
    """A key written twice in `PRE_RESTAMP` keeps only the LAST entry, and
    Python reports nothing -- so a sealed override can die with every test in
    this file still green.

    THIS IS NOT HYPOTHETICAL. It happened: `C10-01`'s v0.44 slot correction was
    written at v0.45 and silently overwritten at v0.61 by an F19 `known_gaps`
    block reusing the key. It cost nothing only because the two readings
    happened to fail the same clause; the GUARD was dead for two rulings.

    It has to be caught by reading this module's SOURCE, because the evaluated
    dict is already collapsed -- by the time any assertion can see
    `PRE_RESTAMP`, the evidence of the duplicate is gone. Same shape as this
    project's tracked "a versioned-artifact indirection is only as real as the
    tests that don't bypass it": the override map exists to hold historical
    inputs, and a duplicate key silently stops it holding them.
    """
    tree = ast.parse(Path(__file__).read_text())
    literals = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(getattr(t, "id", None) == "PRE_RESTAMP" for t in node.targets)
    ]
    assert len(literals) == 1, "expected exactly one PRE_RESTAMP assignment"
    keys = [k.value for k in literals[0].keys]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert not dupes, (
        f"PRE_RESTAMP keys written more than once, so only the last survives: {dupes}. "
        "Merge them into a single entry."
    )
    # And the collapsed dict must still hold every key the source writes -- the
    # positive half, so the guard cannot pass on an empty or renamed literal.
    assert set(keys) == set(PRE_RESTAMP) and len(keys) == len(PRE_RESTAMP)


def test_c10_01s_merged_entry_still_holds_both_rulings_overrides():
    """The specific loss the test above now prevents, pinned by content.

    `C10-01` is overridden by TWO rulings at once -- F11's v0.44 slot correction
    and F19's sealed `known_gaps` -- and they must both survive in one entry.
    """
    entry = PRE_RESTAMP["C10-01"]
    assert entry["object_class"] == "product_liability_indemnification"
    assert "relevant_claim_indemnification" in entry["object_class_accept_set"]
    assert entry["known_gaps"] == ["compound_action", "exception_unsupported"]


def test_legacy_mode_reproduces_the_published_run_item_by_item(published_rows, cold):
    """K = 14/32, AND every per-item clause-failure list, exactly."""
    result = compute(_load_gold(pre_restamp=True, scope=published_population()),
                     cold, symmetric=False, gate=False)
    assert len(result.items) == 32
    assert result.k == 14
    assert result.n == 32
    for item in result.items:
        mine = sorted(PUBLISHED_CLAUSE.get(c, c) for c in item.failed_clauses)
        theirs = sorted(published_rows[item.item_id]["fails"])
        assert mine == theirs, f"{item.item_id}: {mine} != published {theirs}"


def test_band_derivation_reproduces_the_preregistered_n32_bands(cold):
    """PREREGISTRATION.md section 4 fixed DIAGNOSE at K>=3 and REDESIGN at
    K>=6 for n=32. `bands` DERIVES those from the Wilson95 anchors rather than
    transcribing them, so deriving the published pair back is the check that
    the derivation is the same one -- and it is what makes the band at any
    other n trustworthy."""
    result = compute(_load_gold(pre_restamp=True, scope=published_population()),
                     cold, symmetric=False, gate=False)
    assert result.n == 32
    assert result.bands == (3, 6)
    assert result.verdict == "REDESIGN"


# --------------------------------------------------------------------------
# A1 -- the conformance gate, and the boundary that keeps it usable
# --------------------------------------------------------------------------

def test_gold_carries_no_conformance_failure_at_all(gold):
    """All 32 locked items, every closed vocabulary. The 2026-08-29 gate is
    entirely one-sided and the ruling says so; this is that claim as a test."""
    for items in gold.values():
        for item in items:
            assert conformance_failures(item) == (), item["item_id"]


def test_section_8_tag_list_covers_every_tag_gold_actually_uses(gold):
    """Guards the one way `SECTION_8_TAGS` could silently mark real items
    NON_CONFORMING: going stale as section 8 grows."""
    used = {t for items in gold.values() for i in items for t in (i.get("known_gaps") or ())}
    assert used <= SECTION_8_TAGS, f"tags missing from SECTION_8_TAGS: {sorted(used - SECTION_8_TAGS)}"


def test_the_gate_fires_on_an_off_taxonomy_slot_and_not_on_a_legal_one():
    base = {"modality": "MUST", "action": "PROVIDE", "temporal": None, "known_gaps": []}
    assert conformance_failures(base) == ()
    assert conformance_failures({**base, "action": "INVOICE"}) == ("action='INVOICE'",)
    assert conformance_failures({**base, "modality": "SHALL"}) == ("modality='SHALL'",)
    assert conformance_failures({**base, "known_gaps": ["not_a_real_tag"]}) == (
        "known_gaps='not_a_real_tag'",)


def test_off_vocabulary_accept_set_members_are_inert_and_so_are_not_gated(gold, cold):
    """A1's scope boundary, PROVEN rather than asserted. Stripping every
    off-taxonomy `action_accept_set` member from BOTH annotators must change no
    clause outcome on any item -- which is why the gate reads slots only.
    Gating members instead marked 27 of 32 items NON_CONFORMING and left K over
    n=5, destroying the instrument."""
    def strip(by_segment):
        out = copy.deepcopy(dict(by_segment))
        for items in out.values():
            for item in items:
                item["action_accept_set"] = [a for a in item["action_accept_set"] if a in ACTIONS]
        return out

    before = compute(gold, cold)
    after = compute(strip(gold), strip(cold))
    assert {i.item_id: (i.outcome, i.failed_clauses) for i in before.items} == \
           {i.item_id: (i.outcome, i.failed_clauses) for i in after.items}

    stripped = {a for items in cold.values() for i in items
                for a in i["action_accept_set"] if a not in ACTIONS}
    assert len(stripped) == 52                      # the population the claim is about
    assert not (stripped & set(ACTIONS))            # and none could ever match a legal slot


# --------------------------------------------------------------------------
# A2 / A3 -- symmetry, and what it deliberately does not do
# --------------------------------------------------------------------------

def test_accept_set_comparison_is_symmetric_in_both_directions():
    g = {"modality": "MUST", "action": "PROVIDE", "action_accept_set": ["PROVIDE"],
         "obligor": "X", "obligee": "Y", "object_class": "a", "object_class_accept_set": ["a"],
         "temporal": None, "conditions": [], "underspecified": False}
    other = {**g, "action": "REPORT", "action_accept_set": ["REPORT", "PROVIDE"]}
    assert compare_clauses(g, other, symmetric=True)["action"] is True
    assert compare_clauses(g, other, symmetric=False)["action"] is False


def test_section_4_2_content_tie_break_pairs_byte_identical_spans_by_action(gold, cold):
    """C04-139's two gold items have byte-identical spans, so IoU cannot
    discriminate and plain greedy pairing is iteration-order-dependent.
    `align.align` does not implement the tie-break; this does."""
    gs = sorted(gold["C04-139"], key=lambda d: (d["span_char_start"], d["item_id"]))
    assert gs[0]["span_char_start"] == gs[1]["span_char_start"]
    assert gs[0]["span_char_end"] == gs[1]["span_char_end"]
    pairs, missed, surplus = pair_items(gs, cold["C04-139"])
    paired = {gs[gi]["item_id"]: cold["C04-139"][oi]["action"] for gi, oi, _ in pairs}
    assert paired == {"C04-04": "USE", "C04-05": "PROCURE"}
    assert not missed and not surplus

    # and reversing the other annotator's order must not change the pairing
    reversed_pairs, _, _ = pair_items(gs, list(reversed(cold["C04-139"])))
    assert {gs[gi]["item_id"]: list(reversed(cold["C04-139"]))[oi]["action"]
            for gi, oi, _ in reversed_pairs} == paired


# --------------------------------------------------------------------------
# The corrected figures this ruling publishes
# --------------------------------------------------------------------------

def test_corrected_framing_produces_the_published_ruling_figures(gold, cold):
    result = compute(gold, cold)
    assert len(result.items) == 32
    assert len(result.non_conforming) == 5
    assert {i.item_id for i in result.non_conforming} == {
        "C02-03", "C10-02", "C14-04", "C17-01", "C17-02"}
    assert result.n == 27
    assert result.k == 7
    assert result.bands == (3, 5)
    assert result.verdict == "REDESIGN"
    lower, upper = result.k_wilson
    assert (round(lower, 3), round(upper, 3)) == (0.132, 0.447)


def test_every_conformance_failure_is_the_cold_annotators_and_is_an_action_slot(gold, cold):
    """The ruling's finding (1): all five are cold writing the document's real
    verb where section 8.8 requires (nearest taxonomy verb + tag)."""
    for item in compute(gold, cold).non_conforming:
        assert len(item.conformance_failures) == 1
        assert item.conformance_failures[0].startswith("action=")


def test_gap_agreement_recomputed_over_conforming_pairs_only(gold, cold):
    """G belongs to `A` (section 5.1 clause 9) and is reported separately, never
    folded into K. Restricting it to conforming pairs moves it off its own
    REDESIGN trigger -- because both items it drops were dropped for the SAME
    conformance failure, cold never once using `action_not_in_taxonomy`.

    v0.48 UPDATE. The published (all-pairs) figures moved from
    (31, 6, 2) / band (15,17) to (31, 6, 1) / band (16,17), and the
    conforming-only figures from (26, 4, 1) / band (14,15) to
    (26, 4, 0) / band (15,15) -- all of it F7's restamp of C04-02, whose
    known_gaps is now empty and which cold had never tagged.

    THE CONFORMING-ONLY BAND IS NOW A POINT, AND THAT IS THE SUBSTANTIVE
    RESULT. Among conforming pairs the two annotators no longer disagree at
    all about which items are scoreable: G_swing = 0, D = 15 exactly. That
    is the instrument defect CLAUDE.md's REDESIGN entry calls the highest-
    priority open item -- "no future K is trustworthy until this is fixed" --
    now measuring zero on the conforming subset. It does NOT close that item:
    the all-pairs band is still (16,17), the five non-conforming pairs are
    still excluded rather than resolved, and F9's kind-axis question is
    untouched. Neither verdict changed (REDESIGN / DIAGNOSE both hold), so
    this is a real but bounded movement, stated at its size.

    v0.61 (F19) FIX, not an update. This test asserts the PUBLISHED G and was
    computing it from LIVE `known_gaps`, so every post-seal ruling that touched
    a tag silently re-baselined it -- four have. It now reads gold through
    `PRE_RESTAMP`, the same mechanism the clause-level restamps already use, so
    the figures below are the 2026-08-29 run's own again rather than whatever
    today's tags happen to produce. The all-pairs numbers consequently revert
    to the genuinely published `(31, 6, 2)` / band `(15,17)`: the v0.48 note
    above was describing LIVE drift, correctly, but under a name that claimed
    it was the published measurement."""
    gold = _load_gold(pre_restamp=True, scope=published_population())
    nc = {i.item_id for i in compute(gold, cold).non_conforming}
    all_pairs, conforming = [], []
    for segment_id, gold_items in sorted(gold.items()):
        gs = sorted(gold_items, key=lambda d: (d["span_char_start"], d["item_id"]))
        others = cold.get(segment_id, [])
        pairs, _, _ = pair_items(gs, others)
        for gi, oi, _ in pairs:
            pair = GapPair(gs[gi]["item_id"],
                           frozenset(gs[gi].get("known_gaps") or ()),
                           frozenset(others[oi].get("known_gaps") or ()))
            all_pairs.append(pair)
            if pair.item_id not in nc:
                conforming.append(pair)

    published = compute_gap_agreement(all_pairs)
    # v0.61: the ACTUAL published figures, reachable again now that gold is read
    # pre-restamp. Was asserting (31, 6, 1) / (16, 17) -- live drift, not the run.
    assert (published.n, published.g_count, published.g_swing_count) == (31, 6, 2)
    assert published.d_band == (15, 17)
    assert published.g_overall_verdict == "REDESIGN"

    corrected = compute_gap_agreement(conforming)
    assert (corrected.n, corrected.g_count, corrected.g_swing_count) == (26, 4, 1)
    assert corrected.d_band == (14, 15)
    assert corrected.g_overall_verdict == "DIAGNOSE"
    assert corrected.disjoint_items == ()      # GAP_AGREEMENT_DESIGN section 6's only instance


def test_the_LIVE_conforming_G_has_crossed_its_REDESIGN_anchor_since_the_run(gold, cold):
    """THE LIVE COUNTERPART, and it is disclosed rather than left to be found.

    The test above is now genuinely historical. This one is the current set, and
    it does NOT merely drift -- at v0.61 it changes a VERDICT. F19's second tag
    on E03-01 takes the conforming-only G from 4/26 to 5/26, which clears the
    REDESIGN anchor. So the v0.48 framing that restricting G to conforming pairs
    "moves it off its own REDESIGN trigger" is TRUE of the published run and
    FALSE of the current set.

    Stated against interest: F19 was priced as verdict-neutral because the
    ALL-PAIRS G stays REDESIGN either way (6/31 -> 7/31). That is correct and
    incomplete -- the conforming-scoped G is a second instrument with its own
    n, and there the tag is what tips it. No headline figure moves (criterion 2
    and K are untouched, confirmed by a real run), but "no verdict moves" would
    have been wrong.

    The v0.48 note's substantive finding survives in the part that was really
    about scoreability: G_swing on conforming pairs is 0 and the band is the
    POINT (15,15) -- the two annotators still do not disagree about which
    conforming items are scoreable. What moved is G_overall, which counts ANY
    set inequality, including the superset F19 creates."""
    nc = {i.item_id for i in compute(gold, cold).non_conforming}
    conforming = []
    for segment_id, gold_items in sorted(gold.items()):
        gs = sorted(gold_items, key=lambda d: (d["span_char_start"], d["item_id"]))
        others = cold.get(segment_id, [])
        pairs, _, _ = pair_items(gs, others)
        for gi, oi, _ in pairs:
            if gs[gi]["item_id"] in nc:
                continue
            conforming.append(GapPair(gs[gi]["item_id"],
                                      frozenset(gs[gi].get("known_gaps") or ()),
                                      frozenset(others[oi].get("known_gaps") or ())))

    live = compute_gap_agreement(conforming)
    assert (live.n, live.g_count, live.g_swing_count) == (26, 5, 0)
    assert live.d_band == (15, 15), "the SCOREABILITY agreement is unchanged"
    assert live.g_overall_verdict == "REDESIGN", "was DIAGNOSE at the published run"


# --------------------------------------------------------------------------
# v0.53 -- the published run's POPULATION is pinned, not just its numbers
# --------------------------------------------------------------------------

def test_new_items_are_outside_the_published_run_and_would_have_moved_K(cold):
    """The §7 run published `K = 14/32` on 2026-08-29 against a sealed cold
    annotation. v0.53's §14.4 drafting session added `C11-02` and `C04-06`.

    This pins the two facts that make scoping the reproduction the right fix
    rather than bumping 32 -> 34:

      1. Both new items are OUTSIDE the published population, so no published
         figure moves -- which is what the v0.53 changelog claims.
      2. They are not inert. Cold annotated at BOTH spans, so each new item
         PAIRS, and an unscoped reproduction would have silently recomputed a
         published K over gold the run never saw.

    A future §7 re-run is a different measurement over the current 36-item set
    and SHOULD include them. It must not reuse `published_population()`.

    v0.57 UPDATE, and it splits fact 2 in two. `C14-06` is the fourth addition
    and the FIRST WITH NO COLD COUNTERPART: cold EXCLUDED `C14-076`'s VAT
    sentence in prose rather than annotating it, so there is no cold item at
    that span. That is not a weaker version of the same fact, it is the
    opposite one, and it matters -- the other three COULD have moved a
    published K had the reproduction not been scoped, whereas `C14-06` could
    not have moved it even in principle. Both facts are asserted separately so
    neither is read as covering the other.
    """
    published = published_population()
    live = {i["item_id"] for items in _load_gold().values() for i in items}

    added = live - published
    # v0.62: batch 4's 12 items join the four §14.4 additions. `published` does
    # NOT move -- it is derived from the sealed `comparison.json`, which is the
    # whole point of the v0.53 fix and the reason this assertion is safe to keep
    # as an equality while the live set grows.
    batch4 = {"E01-02", "E01-03", "C04-07", "C04-08", "E03-02", "E03-03",
              "E08-02", "E08-03", "E08-04", "C02-05", "C02-06", "C02-07"}
    # v0.65: batch 5 adds E02-01/E02-02 on a segment (E02-006) the cold run
    # never saw, so they fall in batch 4's category rather than the four §14.4
    # additions': OUTSIDE the published population AND unable to pair even in
    # principle. `published` still does not move -- it is derived from the
    # sealed comparison.json, which is what makes this equality safe to keep.
    # v0.65+ (2026-09-25): batch 5's remaining four items land on three
    # further NEW segments (C04-174, C10-025, E03-022) the cold run never
    # saw, so they join the same category. `published` STILL does not move.
    # v0.65+ (2026-09-25): E01-04/E01-05 land on E01-004, another segment the
    # cold run never saw. `published` STILL does not move.
    batch5 = {"E02-01", "E02-02", "C04-09", "C10-03", "E03-04", "E03-05",
              "E01-04", "E01-05"}
    assert added == {"C11-02", "C04-06", "C11-03", "C14-06"} | batch4 | batch5, added
    assert len(published) == 32
    assert len(live) == 56

    # Batch 4 is the first ADDITION WITH NO COLD COUNTERPART AT ALL, and that is
    # a stronger fact than `C14-06`'s. The 2026-08-29 cold run annotated the 22
    # segments then drawn; batch 4 draws SIX NEW SEGMENTS the cold annotator
    # never saw, so none of its 12 items could pair even in principle. A future
    # §7 re-run over the current 48-item set must therefore re-annotate cold
    # rather than reusing that output.
    cold_segments = set(_load_cold())  # keyed BY segment_id; items carry none
    new_segments = {i["segment_id"] for items in _load_gold().values()
                    for i in items if i["item_id"] in batch4 | batch5}
    assert not (new_segments & cold_segments), (
        f"batch 4/5 segments must be outside the cold run: "
        f"{sorted(new_segments & cold_segments)}"
    )

    # Fact 2a: three of the four pair against a real cold item at the same
    # span, so excluding them is a deliberate scope decision, not a no-op.
    for item_id, segment_id, char_start in [("C11-02", "C11-094", 1093),
                                            ("C04-06", "C04-117", 1442),
                                            ("C11-03", "C11-094", 822)]:
        gold_item = next(i for items in _load_gold().values() for i in items
                         if i["item_id"] == item_id)
        assert gold_item["span_char_start"] == char_start
        cold_spans = [c["span_text"] for c in cold[segment_id]]
        assert any(c in gold_item["span_text"] for c in cold_spans), (
            f"{item_id} has no cold counterpart; the premise of this test is wrong")

    # Fact 2b: C14-06 has NO cold counterpart -- cold disposed of the sentence
    # in `segment_notes` prose instead of annotating it. Pinned positively so a
    # future §7 re-run does not assume every added item brings a pair with it.
    c1406 = next(i for items in _load_gold().values() for i in items
                 if i["item_id"] == "C14-06")
    assert c1406["span_char_start"] == 420
    assert not any(c["span_text"] in c1406["span_text"] for c in cold["C14-076"]), (
        "C14-06 now has a cold counterpart; fact 2b is stale and the v0.57 "
        "reasoning that it could not have moved K needs re-checking")


def test_published_scope_fails_loudly_if_a_published_item_vanishes():
    """The guard distinguishes "an item was ADDED" (fine, scoped out) from "a
    published item is MISSING" (a real defect). A hardcoded count cannot tell
    those apart -- both just read as a wrong number."""
    with pytest.raises(AssertionError, match="missing from disk"):
        _load_gold(scope=published_population() | {"ZZ-99"})
