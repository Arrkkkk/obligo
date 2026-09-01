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

# C10-01 and C10-02 were restamped v0.40 -> v0.44 by section 3.6.1's slot
# correction, AFTER the 2026-08-29 comparison was computed. Reproducing the
# published per-clause result therefore requires the pre-v0.44 labels. Keeping
# them here rather than reaching into git makes the ruling's finding (4)
# executable: the restamp was justified as free because section 5 clause 5
# never reads gold's SLOT -- true for the pipeline, and false for `A`, where
# the slot is exactly what is compared.
PRE_V044 = {
    "C10-01": {
        "object_class": "product_liability_indemnification",
        "object_class_accept_set": [
            "product_liability_indemnification", "distributor_liability_indemnification",
            "design_defect_liability", "relevant_claim_indemnification",
        ],
    },
    "C10-02": {
        "object_class": "distributor_insurance_certificate_listing",
        "object_class_accept_set": [
            "distributor_insurance_certificate_listing", "insurance_certificate_addition",
            "additional_insured_designation",
        ],
    },
}

# The published run's clause names, in section 5's numbering.
PUBLISHED_CLAUSE = {
    "modality": "1_modality", "action": "2_action", "obligor": "3_obligor",
    "obligee": "4_obligee", "object_class": "5_object", "temporal": "6_temporal",
    "conditions": "7_conditions", "underspecified": "8_underspec",
}


def _load_gold(pre_v044: bool = False) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for path in glob.glob(str(GOLD_DIR / "batch0*" / "items" / "*.json")):
        item = json.loads(Path(path).read_text())
        if pre_v044 and item["item_id"] in PRE_V044:
            item = {**item, **PRE_V044[item["item_id"]]}
        out.setdefault(item["segment_id"], []).append(item)
    return out


def _load_cold() -> dict[str, list[dict]]:
    out = {}
    for path in sorted(glob.glob(str(HOLDOUT_DIR / "cold" / "*.json"))):
        rec = json.loads(Path(path).read_text())
        out[rec["segment_id"]] = rec["items"]
    return out


@pytest.fixture(scope="module")
def gold():
    return _load_gold()


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

def test_legacy_mode_reproduces_the_published_run_item_by_item(published_rows, cold):
    """K = 14/32, AND every per-item clause-failure list, exactly."""
    result = compute(_load_gold(pre_v044=True), cold, symmetric=False, gate=False)
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
    result = compute(_load_gold(pre_v044=True), cold, symmetric=False, gate=False)
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
    conformance failure, cold never once using `action_not_in_taxonomy`."""
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
    assert (published.n, published.g_count, published.g_swing_count) == (31, 6, 2)
    assert published.d_band == (15, 17)
    assert published.g_overall_verdict == "REDESIGN"

    corrected = compute_gap_agreement(conforming)
    assert (corrected.n, corrected.g_count, corrected.g_swing_count) == (26, 4, 1)
    assert corrected.d_band == (14, 15)
    assert corrected.g_overall_verdict == "DIAGNOSE"
    assert corrected.disjoint_items == ()      # GAP_AGREEMENT_DESIGN section 6's only instance
