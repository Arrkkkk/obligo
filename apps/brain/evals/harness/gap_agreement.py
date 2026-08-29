"""`known_gaps` agreement between two annotators.

Implements `evals/goldens/holdout/GAP_AGREEMENT_DESIGN.md` (approved
2026-08-29, item 0 of the REDESIGN response's scope -- read that file for the
full derivation; this module is the executable form of it, not a
re-derivation). Section 5's own words explain why this exists at all:
`known_gaps` is not one of `score.CLAUSES`, so two annotators can disagree
about whether an item is even scoreable while K stays silent about it --
and that disagreement moves section 9's in-force criterion-2 denominator.

Named distinctly from K on purpose (design section 2): K and G are different
instruments over different predicates and must never be added, averaged, or
reported as one number.

Two independent verdicts, not one (design sections 3-4):

  G_swing -- moves the criterion-2 DENOMINATOR (one side tags a gap, the
  other tags nothing at all for the same item). Gated on the Wilson95 UPPER
  bound of the observed rate, because the question is what a single swing
  rules out, not what it estimates.

  G (overall) -- any known_gaps set inequality between the two annotators;
  measures whether section 8's tag vocabulary itself is fit for scoring.
  Gated on the Wilson95 LOWER bound against the SAME anchors K's own
  DIAGNOSE/REDESIGN bands use (PREREGISTRATION.md section 4), reused rather
  than invented, because G measures the same kind of thing K does.

Both gates are per-run, not cumulative (design section 6, confirmed decision).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from evals.harness.align import align

# Two-sided 95% normal quantile. Reproduced (not re-derived) from the same
# formula PREREGISTRATION.md section 4 and RESULTS.md use for K, so K and G
# agree on what "Wilson95" means. Verified in
# tests/evals/test_harness_gap_agreement.py against six published figures:
# K=14/32, G=6/31, G=3/31, G=5/31, G_swing=1/31, G_swing=2/31.
_Z95 = 1.959963984540054


def wilson95(x: int, n: int) -> tuple[float, float]:
    """Wilson score interval at 95% confidence. Returns (lower, upper) as
    fractions in [0, 1]."""
    if n <= 0:
        raise ValueError(f"Wilson interval is undefined for n={n}")
    if not (0 <= x <= n):
        raise ValueError(f"x={x} must satisfy 0 <= x <= n={n}")
    phat = x / n
    denom = 1 + _Z95**2 / n
    center = phat + _Z95**2 / (2 * n)
    adjustment = _Z95 * math.sqrt(phat * (1 - phat) / n + _Z95**2 / (4 * n**2))
    return ((center - adjustment) / denom, (center + adjustment) / denom)


# Design section 4: reuse K's own evidential-strength anchors (the Wilson95
# LOWER bound at K's own DIAGNOSE/REDESIGN triggers, K>=2/20 and K>=4/20 --
# PREREGISTRATION.md section 4) rather than invent new ones for G. Computed,
# not transcribed, so a formula change here cannot silently drift from the
# constants K itself was checked against: 0.0279 / 0.0807.
DIAGNOSE_ANCHOR = wilson95(2, 20)[0]
REDESIGN_ANCHOR = wilson95(4, 20)[0]


class GapClass(str, Enum):
    """Design section 2's three-way decomposition of a `known_gaps`
    disagreement. Equal sets (including both empty) are agreement and are
    not a `GapClass` at all -- `classify_gap_pair` returns `None` for them."""

    SWING = "swing"
    SUPERSET = "superset"
    DISJOINT = "disjoint"


def classify_gap_pair(gold_gaps: frozenset[str], cold_gaps: frozenset[str]) -> GapClass | None:
    """`None` means the two sides agree (moves nothing). Otherwise:

    SWING     -- exactly one side's set is empty (moves the criterion-2
                 denominator: one annotator considers the item scoreable,
                 the other does not).
    SUPERSET  -- both non-empty, one strictly contains the other (agree the
                 item is gap-carrying, disagree which/how many gaps).
    DISJOINT  -- both non-empty, neither contains the other (disagree about
                 *which* gap the item has)."""
    if gold_gaps == cold_gaps:
        return None
    if not gold_gaps or not cold_gaps:
        return GapClass.SWING
    if gold_gaps <= cold_gaps or cold_gaps <= gold_gaps:
        return GapClass.SUPERSET
    return GapClass.DISJOINT


@dataclass(frozen=True)
class GapPair:
    """One matched item's `known_gaps` from each annotator. `matched` here
    means the design section 2 sense: the same span, aligned by
    `pair_matched_items` below -- NOT the `report.ItemReport` sense of a
    scored prediction."""

    item_id: str
    gold_gaps: frozenset[str]
    cold_gaps: frozenset[str]


# G_swing verdicts (design section 3). Deliberately count-based (0 / 1-2 /
# >=3), not a fixed Wilson-upper cutoff: the design table derives these
# specific bounds (11.0% / 16.2-20.7% / >=24.9%) FROM the n=31 counts, it does
# not define the bands as an independent rate threshold the way G_overall's
# anchors are. The Wilson upper bound is still exposed on the result for
# transparency, but the verdict is the count rule.
GSWING_STABLE = "STABLE"
GSWING_BANDED = "BANDED"
GSWING_UNREPORTABLE = "UNREPORTABLE"

# G (overall) verdicts (design section 4). Wilson95-lower-vs-anchor, exactly
# K's own method, so this generalizes across n the way the count-based
# G_swing rule deliberately does not.
G_TAXONOMY_OK = "TAXONOMY OK"
G_DIAGNOSE = "DIAGNOSE"
G_REDESIGN = "REDESIGN"


@dataclass
class GapAgreementResult:
    pairs: tuple[GapPair, ...]
    swing_items: tuple[str, ...]
    superset_items: tuple[str, ...]
    disjoint_items: tuple[str, ...]
    d_gold: int
    d_cold: int
    d_int: int
    d_uni: int

    @property
    def n(self) -> int:
        return len(self.pairs)

    @property
    def g_count(self) -> int:
        return len(self.swing_items) + len(self.superset_items) + len(self.disjoint_items)

    @property
    def g_swing_count(self) -> int:
        return len(self.swing_items)

    @property
    def g_rate(self) -> float:
        return self.g_count / self.n if self.n else 0.0

    @property
    def g_swing_rate(self) -> float:
        return self.g_swing_count / self.n if self.n else 0.0

    @property
    def g_swing_wilson_upper(self) -> float:
        return wilson95(self.g_swing_count, self.n)[1]

    @property
    def g_overall_wilson_lower(self) -> float:
        return wilson95(self.g_count, self.n)[0]

    @property
    def g_swing_verdict(self) -> str:
        if self.g_swing_count == 0:
            return GSWING_STABLE
        if self.g_swing_count <= 2:
            return GSWING_BANDED
        return GSWING_UNREPORTABLE

    @property
    def g_overall_verdict(self) -> str:
        lower = self.g_overall_wilson_lower
        if lower >= REDESIGN_ANCHOR:
            return G_REDESIGN
        if lower >= DIAGNOSE_ANCHOR:
            return G_DIAGNOSE
        return G_TAXONOMY_OK

    @property
    def d_band(self) -> tuple[int, int]:
        """Design section 5: the band is [D_int, D_uni]. D_int <= D_gold <=
        D_uni always (intersection <= either set <= union), so this already
        brackets D_gold without needing min/max over all three denominators."""
        return (self.d_int, self.d_uni)

    def criterion2_band(self, numerator: int) -> tuple[float, float]:
        """Design section 5's worked table: the numerator F is held FIXED
        (it is the scoring run's own count of FULLY_CORRECT items under
        D_gold's scope) and only the denominator varies -- recomputing F at
        the wider/narrower scope would need those extra items actually
        scored, which section 5 states plainly is not yet computable for
        this set. Returns (pct at D_uni, pct at D_int): the low and high
        ends of the band, since F/D_uni <= F/D_int always."""
        lo_d, hi_d = self.d_band
        if lo_d <= 0 or hi_d <= 0:
            raise ValueError("criterion2_band requires non-zero denominators")
        return (numerator / hi_d, numerator / lo_d)


def compute_gap_agreement(pairs: Sequence[GapPair]) -> GapAgreementResult:
    """Design section 2: matched-pairs-only scope, per-run (not cumulative).
    `pairs` must already be restricted to matched items -- an unmatched gold
    item is counted in K (as UNMATCHED) and in channel 4, and counting it
    here too would conflate three instruments measuring different things
    (design section 2, "Scope: matched pairs only")."""
    swing: list[str] = []
    superset: list[str] = []
    disjoint: list[str] = []
    d_gold = d_cold = d_int = d_uni = 0
    for p in pairs:
        cls = classify_gap_pair(p.gold_gaps, p.cold_gaps)
        if cls is GapClass.SWING:
            swing.append(p.item_id)
        elif cls is GapClass.SUPERSET:
            superset.append(p.item_id)
        elif cls is GapClass.DISJOINT:
            disjoint.append(p.item_id)
        gold_clean = not p.gold_gaps
        cold_clean = not p.cold_gaps
        d_gold += gold_clean
        d_cold += cold_clean
        d_int += gold_clean and cold_clean
        d_uni += gold_clean or cold_clean
    return GapAgreementResult(
        pairs=tuple(pairs),
        swing_items=tuple(swing),
        superset_items=tuple(superset),
        disjoint_items=tuple(disjoint),
        d_gold=d_gold,
        d_cold=d_cold,
        d_int=d_int,
        d_uni=d_uni,
    )


def pair_matched_items(
    gold_items: Sequence[Mapping],
    cold_items: Sequence[Mapping],
    *,
    threshold: float = 0.5,
) -> list[GapPair]:
    """Aligns one segment's gold items against that same segment's cold
    items by span IoU (guideline 4.1/4.2, via `evals.harness.align.align`,
    the identical alignment the pipeline-vs-gold scorer uses) and returns a
    `GapPair` for every matched pair. Unmatched gold (missed) and unmatched
    cold (surplus) are excluded by construction -- design section 2's
    matched-pairs-only scope.

    Each item mapping must carry `span_char_start`, `span_char_end`, and
    `known_gaps`; gold items must also carry `item_id`."""
    gold_spans = [(g["span_char_start"], g["span_char_end"]) for g in gold_items]
    gold_ids = [g["item_id"] for g in gold_items]
    cold_spans = [(c["span_char_start"], c["span_char_end"]) for c in cold_items]
    alignment = align(gold_spans, cold_spans, gold_ids=gold_ids, threshold=threshold)
    out = []
    for pr in alignment.pairs:
        g = gold_items[pr.gold_index]
        c = cold_items[pr.pred_index]
        out.append(
            GapPair(
                item_id=g["item_id"],
                gold_gaps=frozenset(g.get("known_gaps") or ()),
                cold_gaps=frozenset(c.get("known_gaps") or ()),
            )
        )
    return out
