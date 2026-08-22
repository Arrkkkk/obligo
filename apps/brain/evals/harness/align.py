"""Span alignment: guideline sections 4.1 and 4.2.

A predicted obligation aligns to a gold item when their span offsets overlap
with IoU >= 0.5 within the same segment (4.1). One predicted span aligns to
at most one gold item; pairing is greedy by descending IoU and the chosen
pairing is recorded with the score (4.2).

Greedy-by-descending-IoU is not optimal in general -- a maximum-weight
matching could pair differently -- but section 4.2 specifies greedy, and the
pairing must be reproducible and explainable per item rather than merely
maximal. Ties are broken deterministically by (gold item_id, predicted span
start) so a rerun cannot silently produce a different pairing.

`not_annotatable` spans are accepted from the outset and default to empty
(section 21 R6). A prediction aligning to one is neither correct nor a false
positive; until those spans are annotated for all 12 gold segments the
UNEXPECTED count is a known, one-directional over-count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


def iou(a: tuple[int, int], b: tuple[int, int]) -> float:
    lo = max(a[0], b[0])
    hi = min(a[1], b[1])
    overlap = max(0, hi - lo)
    union = (a[1] - a[0]) + (b[1] - b[0]) - overlap
    return overlap / union if union > 0 else 0.0


@dataclass(frozen=True)
class Pair:
    gold_index: int
    pred_index: int
    iou: float


@dataclass
class Alignment:
    pairs: list[Pair] = field(default_factory=list)
    missed_gold: list[int] = field(default_factory=list)
    unexpected_pred: list[int] = field(default_factory=list)
    not_annotatable_pred: list[int] = field(default_factory=list)


def align(
    gold_spans: Sequence[tuple[int, int]],
    pred_spans: Sequence[tuple[int, int]],
    *,
    gold_ids: Sequence[str] | None = None,
    not_annotatable: Sequence[tuple[int, int]] = (),
    threshold: float = 0.5,
) -> Alignment:
    gold_ids = list(gold_ids or [str(i) for i in range(len(gold_spans))])
    scored = [
        (iou(g, p), gold_ids[gi], p[0], gi, pi)
        for gi, g in enumerate(gold_spans)
        for pi, p in enumerate(pred_spans)
        if iou(g, p) >= threshold
    ]
    # Descending IoU; ties broken deterministically so a rerun cannot pair
    # differently (section 4.2 requires the chosen pairing to be recorded with the
    # score, which is meaningless if it varies by input order).
    #
    # KNOWN LATENT ISSUE, low risk today: when `gold_ids` is not supplied the
    # fallback ids are str(index), which sort LEXICOGRAPHICALLY -- "10" < "2".
    # Harmless at the current scale (at most 3 gold items per segment, and the
    # real caller always passes item_id), but it would silently reorder tie-breaks
    # past ten items per segment. Fix by zero-padding the fallback ids, or by
    # making gold_ids required, whenever a segment can carry double digits.
    scored.sort(key=lambda r: (-r[0], r[1], r[2]))

    result = Alignment()
    used_gold: set[int] = set()
    used_pred: set[int] = set()
    for score, _, _, gi, pi in scored:
        if gi in used_gold or pi in used_pred:
            continue
        used_gold.add(gi)
        used_pred.add(pi)
        result.pairs.append(Pair(gold_index=gi, pred_index=pi, iou=score))

    result.missed_gold = [i for i in range(len(gold_spans)) if i not in used_gold]
    for pi, p in enumerate(pred_spans):
        if pi in used_pred:
            continue
        if any(iou(na, p) >= threshold for na in not_annotatable):
            result.not_annotatable_pred.append(pi)   # section 4.4: neither, in either direction
        else:
            result.unexpected_pred.append(pi)
    return result
