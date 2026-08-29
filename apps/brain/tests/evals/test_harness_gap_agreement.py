"""GAP_AGREEMENT_DESIGN.md's G/G_swing instrument, proven by planted cases and
by a real-data reproduction of the 2026-08-29 §7 cold-annotator run.

The real-data test (`test_reproduces_the_2026_08_29_holdout_run_exactly`) is
the load-bearing one per Standing Principle 7 -- a detector is not evidence
until it is checked against a known answer, and this instrument's known
answer is `evals/goldens/holdout/GAP_AGREEMENT_DESIGN.md` and `RESULTS.md`'s
own published G=6/31, G_swing=2/31, D=15 [15-17].
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import pytest

from evals.harness.gap_agreement import (
    DIAGNOSE_ANCHOR,
    GSWING_BANDED,
    GSWING_STABLE,
    GSWING_UNREPORTABLE,
    G_DIAGNOSE,
    G_REDESIGN,
    G_TAXONOMY_OK,
    GapClass,
    GapPair,
    REDESIGN_ANCHOR,
    classify_gap_pair,
    compute_gap_agreement,
    pair_matched_items,
    wilson95,
)
from evals.harness.report import build

GOLD_DIR = Path(__file__).resolve().parents[2] / "evals" / "goldens"
HOLDOUT_DIR = GOLD_DIR / "holdout"


def _fs(*tags: str) -> frozenset[str]:
    return frozenset(tags)


# --- classify_gap_pair: design section 2's three-way decomposition ---------

@pytest.mark.parametrize(
    "gold,cold,expected,why",
    [
        (_fs(), _fs(), None, "both empty -> agree"),
        (_fs("a"), _fs("a"), None, "identical non-empty sets -> agree"),
        (_fs("a", "b"), _fs("b", "a"), None, "set equality is order-insensitive"),
        (_fs("a"), _fs(), GapClass.SWING, "gold tags, cold does not"),
        (_fs(), _fs("a"), GapClass.SWING, "cold tags, gold does not"),
        (_fs("a", "b"), _fs("a"), GapClass.SUPERSET, "gold strictly contains cold"),
        (_fs("a"), _fs("a", "b"), GapClass.SUPERSET, "cold strictly contains gold"),
        (_fs("a"), _fs("b"), GapClass.DISJOINT, "no overlap at all"),
        (_fs("a", "b"), _fs("b", "c"), GapClass.DISJOINT, "partial overlap, neither a subset"),
    ],
)
def test_classify_gap_pair(gold, cold, expected, why):
    assert classify_gap_pair(gold, cold) is expected, why


# --- wilson95: reproduced from the same formula K's own figures use --------

@pytest.mark.parametrize(
    "x,n,expected_lo,expected_hi",
    [
        (14, 32, 0.2816, 0.6067),   # RESULTS.md: K=14/32, Wilson95 [28.2%, 60.7%]
        (6, 31, 0.0919, None),      # GAP_AGREEMENT_DESIGN.md §4: G=6/31 lower 0.0919
        (3, 31, 0.0335, None),      # design §4: 3/31 gives lower 0.0335
        (5, 31, 0.0709, None),      # design §4: 5/31 falls short at 0.0709
        (0, 31, None, 0.1103),      # design §3: G_swing=0 -> Wilson95 upper 11.0%
        (1, 31, None, 0.1619),      # design §3: 1/31 -> upper 16.2%
        (2, 31, None, 0.2072),      # design §3: 2/31 -> upper 20.7%
        (3, 31, None, 0.2490),      # design §3: >=3 -> upper >=24.9%, 3/31 gives 24.9%
    ],
)
def test_wilson95_matches_published_figures(x, n, expected_lo, expected_hi):
    lo, hi = wilson95(x, n)
    if expected_lo is not None:
        assert lo == pytest.approx(expected_lo, abs=5e-4)
    if expected_hi is not None:
        assert hi == pytest.approx(expected_hi, abs=5e-4)


def test_wilson95_rejects_degenerate_input():
    with pytest.raises(ValueError):
        wilson95(0, 0)
    with pytest.raises(ValueError):
        wilson95(5, 3)


# --- verdict thresholds: planted counts, not just the one real n=31 run ----

@pytest.mark.parametrize(
    "swing_count,n,expected",
    [
        (0, 31, GSWING_STABLE),
        (1, 31, GSWING_BANDED),
        (2, 31, GSWING_BANDED),
        (3, 31, GSWING_UNREPORTABLE),
        (10, 31, GSWING_UNREPORTABLE),
    ],
)
def test_g_swing_verdict_thresholds(swing_count, n, expected):
    pairs = [GapPair(f"S{i}", _fs("x"), _fs()) for i in range(swing_count)]
    pairs += [GapPair(f"A{i}", _fs(), _fs()) for i in range(n - swing_count)]
    result = compute_gap_agreement(pairs)
    assert result.g_swing_verdict == expected, (swing_count, n)


@pytest.mark.parametrize(
    "g_count,expected",
    [
        (0, G_TAXONOMY_OK),
        (2, G_TAXONOMY_OK),
        (3, G_DIAGNOSE),   # design §4: 3/31 is the first to clear DIAGNOSE
        (5, G_DIAGNOSE),   # design §4: 5/31 falls short of REDESIGN
        (6, G_REDESIGN),   # design §4: 6/31 is the first to clear REDESIGN
        (10, G_REDESIGN),
    ],
)
def test_g_overall_verdict_thresholds_at_n31(g_count, expected):
    # Use DISJOINT pairs so g_count is driven purely by G, independent of G_swing.
    pairs = [GapPair(f"G{i}", _fs("x"), _fs("y")) for i in range(g_count)]
    pairs += [GapPair(f"A{i}", _fs(), _fs()) for i in range(31 - g_count)]
    result = compute_gap_agreement(pairs)
    assert result.g_count == g_count
    assert result.g_overall_verdict == expected, g_count


def test_diagnose_and_redesign_anchors_match_preregistration():
    # PREREGISTRATION.md §4: Wilson95 lower bound at K's own DIAGNOSE (K>=2/20)
    # and REDESIGN (K>=4/20) triggers.
    assert DIAGNOSE_ANCHOR == pytest.approx(0.0279, abs=5e-4)
    assert REDESIGN_ANCHOR == pytest.approx(0.0807, abs=5e-4)


# --- compute_gap_agreement: denominators, planted rather than incidental ---

def test_denominators_over_a_planted_set():
    pairs = [
        GapPair("clean_both", _fs(), _fs()),           # in D_gold, D_cold, D_int, D_uni
        GapPair("gold_gap_only", _fs("a"), _fs()),      # cold-clean only -> D_cold, D_uni
        GapPair("cold_gap_only", _fs(), _fs("a")),      # gold-clean only -> D_gold, D_uni
        GapPair("both_gappy", _fs("a"), _fs("b")),      # neither
    ]
    r = compute_gap_agreement(pairs)
    assert r.n == 4
    assert r.d_gold == 2      # clean_both, cold_gap_only
    assert r.d_cold == 2      # clean_both, gold_gap_only
    assert r.d_int == 1       # clean_both only
    assert r.d_uni == 3       # all but both_gappy
    assert r.d_band == (1, 3)
    assert r.g_count == 3     # gold_gap_only (swing), cold_gap_only (swing), both_gappy (disjoint)
    assert r.g_swing_count == 2


def test_criterion2_band_holds_numerator_fixed_and_varies_denominator():
    # design §5's own worked table: F=12 held fixed, D varying 14/15/16/17
    # gives 85.7% / 80.0% / 75.0% / 70.6%.
    pairs = [GapPair(f"I{i}", _fs(), _fs()) for i in range(15)]      # D_int = D_gold = 15
    pairs += [GapPair(f"S{i}", _fs("a"), _fs()) for i in range(2)]   # 2 swings -> D_uni = 17
    r = compute_gap_agreement(pairs)
    assert r.d_band == (15, 17)
    lo, hi = r.criterion2_band(12)
    assert lo == pytest.approx(12 / 17)
    assert hi == pytest.approx(12 / 15)


def test_criterion2_band_rejects_zero_denominator():
    r = compute_gap_agreement([GapPair("x", _fs("a"), _fs("b"))])  # d_int == d_uni == 0
    assert r.d_band == (0, 0)
    with pytest.raises(ValueError):
        r.criterion2_band(0)


# --- pair_matched_items: the alignment half, on synthetic spans ------------

def test_pair_matched_items_excludes_unmatched_and_uses_iou_alignment():
    gold_items = [
        {"item_id": "A", "span_char_start": 0, "span_char_end": 100, "known_gaps": ["mutual_obligation"]},
        {"item_id": "B", "span_char_start": 200, "span_char_end": 300, "known_gaps": []},
    ]
    cold_items = [
        {"span_char_start": 0, "span_char_end": 100, "known_gaps": []},   # aligns to A
        {"span_char_start": 500, "span_char_end": 600, "known_gaps": ["compound_action"]},  # surplus, no gold match
    ]
    pairs = pair_matched_items(gold_items, cold_items)
    assert len(pairs) == 1
    assert pairs[0].item_id == "A"
    assert pairs[0].gold_gaps == _fs("mutual_obligation")
    assert pairs[0].cold_gaps == _fs()
    # B (missed by cold) and the surplus cold item are excluded -- matched-pairs-only scope.


# --- real-data reproduction: the 2026-08-29 §7 cold-annotator run ----------

_HOLDOUT_ITEM_IDS = [
    "C02-01", "C02-02", "C02-03", "C02-04", "C03-01", "C03-02", "C03-03",
    "C04-01", "C04-02", "C04-03", "C04-04", "C04-05", "C05-01", "C06-01",
    "C10-01", "C10-02", "C11-01", "C13-01", "C13-02", "C13-03", "C14-01",
    "C14-02", "C14-04", "C14-05", "C17-01", "C17-02", "C22-01", "C22-02",
    "E01-01", "E03-01", "E07-01", "E08-01",
]


def _load_holdout_pairs() -> list[GapPair]:
    gold_by_seg: dict[str, list[dict]] = {}
    for item_id in _HOLDOUT_ITEM_IDS:
        matches = glob.glob(str(GOLD_DIR / "batch*" / "items" / f"{item_id}.json"))
        assert matches, f"gold item {item_id} not found under any batch"
        gold = json.loads(Path(matches[0]).read_text())
        gold_by_seg.setdefault(gold["segment_id"], []).append(gold)

    cold_by_seg: dict[str, list[dict]] = {}
    for path in sorted((HOLDOUT_DIR / "cold").glob("*.json")):
        cold = json.loads(path.read_text())
        cold_by_seg[cold["segment_id"]] = cold["items"]

    pairs: list[GapPair] = []
    for seg_id, gold_items in gold_by_seg.items():
        pairs.extend(pair_matched_items(gold_items, cold_by_seg.get(seg_id, [])))
    return pairs


def test_reproduces_the_2026_08_29_holdout_run_exactly():
    """Real evidence, not a planted fixture: reloads the actual 32 gold items
    (batch01/02/03) and the actual 22 cold/*.json files, realigns them with
    the same guideline-4.1/4.2 IoU matching the scorer itself uses, and
    checks the result against GAP_AGREEMENT_DESIGN.md §2/§5 and RESULTS.md's
    Finding 1 -- both written before this code existed."""
    pairs = _load_holdout_pairs()
    result = compute_gap_agreement(pairs)

    assert result.n == 31, "design §2: n=31 matched items (32 items, 1 unmatched -- C14-02)"
    assert result.g_count == 6
    assert result.g_swing_count == 2
    assert set(result.swing_items) == {"C04-02", "C10-02"}
    assert set(result.superset_items) == {"C04-03", "C14-01", "E01-01"}
    assert set(result.disjoint_items) == {"C14-04"}

    assert result.d_gold == 15
    assert result.d_int == 15
    assert result.d_uni == 17
    assert result.d_band == (15, 17)

    assert result.g_swing_verdict == GSWING_BANDED
    assert result.g_overall_verdict == G_REDESIGN


def test_holdout_reproduction_also_matches_comparisonjson_matched_count():
    """Cross-check against the independently-produced comparison.json (built
    by a prior, uncommitted session before this instrument existed) rather
    than only against the design doc's own prose numbers."""
    comparison = json.loads((HOLDOUT_DIR / "comparison.json").read_text())
    matched_rows = [r for r in comparison["rows"] if r["matched"]]
    assert len(matched_rows) == 31
    unmatched_rows = [r for r in comparison["rows"] if not r["matched"]]
    assert [r["item"] for r in unmatched_rows] == ["C14-02"]

    pairs = _load_holdout_pairs()
    assert {p.item_id for p in pairs} == {r["item"] for r in matched_rows}


# --- report.py integration: the mandatory display rule (G7) ----------------

def _gold(item_id, gaps=()):
    return {"item_id": item_id, "known_gaps": list(gaps), "vague_temporal_phrase": None}


def test_render_never_prints_a_bare_point_estimate_when_gap_agreement_is_present():
    from evals.harness.score import Outcome as O

    # gap_agreement's own item population MUST match the report's D_gold-scope
    # population (see the report.py coherence guard) -- "A" and "B" are the
    # report's two clean (known_gaps==[]) items, and the same two appear as
    # clean pairs here. "S1" is a third pair, gappy on gold's side only, that
    # exists solely in the cold-comparison population (not scored by this
    # report at all) -- exactly the design's own D_gold/D_uni split.
    pairs = [GapPair("A", _fs(), _fs()), GapPair("B", _fs(), _fs())]
    pairs += [GapPair("S1", _fs("mutual_obligation"), _fs())]
    ga = compute_gap_agreement(pairs)
    assert (ga.d_gold, ga.d_int, ga.d_uni) == (2, 2, 3)

    gold = {"A": _gold("A"), "B": _gold("B")}
    r = build({"A": [O.FULLY_CORRECT], "B": [O.PARTIAL]}, gold, gap_agreement=ga)
    text = r.render()

    assert "CRITERION 2 (IN FORCE, §9.1 — len(known_gaps)==0): 1/2 = 50.0%" in text
    # numerator fixed at 1 (only A is FULLY_CORRECT); band = [1/3, 1/2] = [33.3%, 50.0%]
    assert "[band 33.3%–50.0%]" in text
    assert "over D=2 [2–3]" in text
    assert f"G_swing={ga.g_swing_count}/{ga.n} → {ga.g_swing_verdict}" in text
    assert "G (overall known_gaps disagreement)" in text


def test_render_raises_on_a_gap_agreement_computed_over_a_different_population():
    """The coherence guard: a gap_agreement whose d_gold disagrees with the
    report's own clean denominator must not render silently -- that mismatch
    is exactly the "detector succeeds silently on unhandled input" shape
    Standing Principle 7 exists to catch."""
    from evals.harness.score import Outcome as O

    pairs = [GapPair(f"X{i}", _fs(), _fs()) for i in range(5)]  # d_gold=5
    ga = compute_gap_agreement(pairs)
    gold = {"A": _gold("A")}
    r = build({"A": [O.FULLY_CORRECT]}, gold, gap_agreement=ga)  # this report's n_ng == 1
    with pytest.raises(ValueError, match="does not match this report's own"):
        r.render()


def test_render_is_unchanged_when_gap_agreement_is_absent():
    from evals.harness.score import Outcome as O
    r = build({"A": [O.FULLY_CORRECT]}, {"A": _gold("A")})
    text = r.render()
    assert "band" not in text
    assert "G_swing" not in text


def test_render_end_to_end_with_the_real_holdout_gap_agreement():
    """The full wire-up, against real data rather than a synthetic fixture:
    `gap_agreement` here is the ACTUAL result of reloading the 32 real gold
    items and 22 real cold/*.json files and realigning them -- the same
    n=31/G=6/G_swing=2/D=15[15-17] the design doc and RESULTS.md publish.

    The Outcome numerator is NOT a real pipeline scoring run -- no
    run_pipeline(), no cassette replay, no Z3. Only 5 of the 15 real D_gold
    items' segments even have a stage-4 cassette, and a real score needs
    real Postgres + a real typecheck/verify pass, which is out of scope for
    wiring the reporting layer. The placeholder pattern is fixed and
    reproducible so this test pins the RENDER FORMAT against the real
    instrument, and `provenance` states plainly that the figure is
    illustrative -- the same "don't fabricate what you haven't run" rule
    the rest of this codebase holds itself to (see CLAUDE.md's compile-stage
    bottleneck and gold-set checkpoints, which name exactly this gap)."""
    from evals.harness.score import Outcome as O

    pairs = _load_holdout_pairs()
    ga = compute_gap_agreement(pairs)
    assert (ga.n, ga.g_count, ga.g_swing_count) == (31, 6, 2)
    assert (ga.d_gold, ga.d_int, ga.d_uni) == (15, 15, 17)
    assert ga.g_swing_verdict == GSWING_BANDED
    assert ga.g_overall_verdict == G_REDESIGN

    d_gold_items = sorted(p.item_id for p in pairs if not p.gold_gaps)
    assert len(d_gold_items) == 15

    gold_by_id = {}
    for item_id in d_gold_items:
        matches = glob.glob(str(GOLD_DIR / "batch*" / "items" / f"{item_id}.json"))
        gold_by_id[item_id] = json.loads(Path(matches[0]).read_text())

    pattern = [O.FULLY_CORRECT, O.FULLY_CORRECT, O.PARTIAL, O.MISSED, O.FULLY_CORRECT]
    placeholder_runs = {
        item_id: [pattern[i % len(pattern)]] * 3 for i, item_id in enumerate(d_gold_items)
    }

    report = build(
        placeholder_runs, gold_by_id, gap_agreement=ga,
        provenance={"note": "ILLUSTRATIVE -- outcomes are a placeholder pattern, "
                             "NOT a real pipeline scoring run"},
    )
    text = report.render()

    assert "CRITERION 2 (IN FORCE, §9.1 — len(known_gaps)==0): 9/15 = 60.0%" in text
    assert "[band 52.9%–60.0%]" in text
    assert "over D=15 [15–17]" in text
    assert "G_swing=2/31 → BANDED" in text
    assert "G (overall known_gaps disagreement) = 6/31 → REDESIGN (Wilson95 lower 9.2%)" in text
    assert "ILLUSTRATIVE -- outcomes are a placeholder pattern" in text
