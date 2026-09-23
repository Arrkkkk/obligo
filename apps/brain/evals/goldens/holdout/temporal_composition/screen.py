"""§8.12 (F21) exposure screen: which locked items owe `temporal_composition`?

PRESERVED RATHER THAN RUN-AND-DISCARDED, on this repo's own precedent
(`band_risk/`, `accept_sets/`), so the ruling's exposure claim is auditable
rather than asserted.

WHAT THIS SCRIPT IS AND IS NOT. It is a CANDIDATE GENERATOR, not an
adjudicator. A marker sweep over `span_text` is recall-oriented and its false
positives are real and numerous -- agentive `by` ("by devise", "by BKC"),
non-temporal `upon` ("agree upon terms"), and object-scope `during` ("made by
Life Technologies during the Term", which bounds the DISCOVERIES, not the duty).
Every flagged span is then adjudicated BY HAND against the production classifier,
and the adjudication -- not the sweep -- is the ruling's evidence.

STANDING PRINCIPLE 7. The screen is gated on known answers BEFORE any count is
read off it, and the gate is two-sided: the three items the ruling tags must all
be flagged (recall), and four specific false-positive SHAPES must be flagged and
then hand-rejected (so the gate proves the sweep is loose, not that it is right).
`load_items()` raises below the committed item count, because a known-answer gate
above an EMPTY corpus passes -- v0.58's own preserved screen printed "12/12 PASS"
over zero items for exactly that reason.
"""
from __future__ import annotations

import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDENS = os.path.normpath(os.path.join(HERE, "..", ".."))
MIN_ITEMS = 48

# Deliberately loose: heads that CAN introduce a temporal element, plus shapes
# that cannot (`by`, `upon`) and are here to make the hand pass do real work.
MARKERS = re.compile(
    r"\b(within|by|every|during|before|after|until|upon|thereafter|"
    r"no later than|commencing|prior to|following|from the date)\b", re.I)

# The hand adjudication, recorded as data so it can be diffed and argued with.
# FIRES = the span states >=2 temporal elements constraining the duty
# differently, and IR v1's single `temporal` slot can hold at most one.
ADJUDICATION = {
    "E03-01": (True,  "lead-time element + `during the Term of this Supply Agreement`, "
                      "a scope bound on how long the quarterly duty subsists. Swept in "
                      "from §8.11's own observation that F19's note omitted it."),
    "C02-07": (True,  "`Upon receiving any such notice...` (start trigger) + `until a decision "
                      "by AMAG has been made...` (terminal bound). The terminal bound sits "
                      "OUTSIDE the annotated phrase, so nothing is swallowed -- in scope under "
                      "the SLOT-LIMIT scope, out of scope under a swallow-scoped rule."),
    "C04-08": (True,  "`within [...] days of the Effective Date` + `thereafter by [...] of each "
                      "Calendar Year` + `during the Term`. Instance two."),
    "C11-01": (False, "RESTATEMENT, not composition: `upon the death...` and `within a reasonable "
                      "time after the Principal's death` anchor on the SAME event. Only the vague "
                      "magnitude is lost, which is §15.2's separate class."),
    "C02-06": (False, "CLOSEST CALL. `promptly (but no later than [***] of receipt)` is ONE "
                      "deadline stated twice, the parenthetical quantifying the qualifier -- not "
                      "a second constraint of a different kind."),
    "C11-03": (False, "one element (`within twelve (12) months from the date...`); flagged on "
                      "agentive `by devise`/`by BKC`."),
    "C17-02": (False, "one element (`within 24 months following the Commencement Date`)."),
    "C04-07": (False, "NON-TEMPORAL `upon`: `agree in writing upon commercially reasonable terms`."),
    "E07-01": (False, "`As requested by Client` / `upon reasonable notice` are CONDITIONS "
                      "(annotated as such); no second temporal element."),
    "C04-02": (False, "`during the Term` sits inside the IF-condition; the duty to negotiate "
                      "carries no temporal at all."),
    "C05-01": (False, "`during the Term` bounds the DISCOVERIES (object scope), not the "
                      "keep-informed duty."),
}


def load_items() -> list[dict]:
    items = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(GOLDENS, "batch*", "items", "*.json")))]
    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"loaded {len(items)} items, expected >= {MIN_ITEMS}. A known-answer gate "
            f"over an empty or partial corpus passes and means nothing.")
    return items


def flagged(items: list[dict]) -> list[str]:
    out = []
    for i in items:
        marks = {m.group(0).lower() for m in MARKERS.finditer(i["span_text"])}
        if len(marks) >= 2:
            out.append(i["item_id"])
    return sorted(out)


def main() -> int:
    items = load_items()
    hits = flagged(items)

    # GATE 1 (recall): every item the ruling tags must survive the sweep.
    must_flag = [k for k, (fires, _) in ADJUDICATION.items() if fires]
    missed = [k for k in must_flag if k not in hits]
    if missed:
        raise RuntimeError(f"screen MISSED an item the ruling tags: {missed}")

    # GATE 2 (the sweep is loose, and the hand pass is doing the work): four
    # named false-positive SHAPES must be flagged and then rejected by hand.
    for shape in ("C11-03", "C04-07", "C05-01", "C11-01"):
        if shape not in hits:
            raise RuntimeError(
                f"{shape} was expected to be a FALSE POSITIVE of the sweep and was not "
                f"flagged -- the gate no longer proves the hand pass is load-bearing")
        if ADJUDICATION[shape][0]:
            raise RuntimeError(f"{shape} is adjudicated as firing; the gate contradicts itself")

    # GATE 3: the sweep must not flag anything the hand pass never looked at.
    unadjudicated = [h for h in hits if h not in ADJUDICATION]
    if unadjudicated:
        raise RuntimeError(f"flagged but never adjudicated: {unadjudicated}")

    fires = sorted(k for k, (f, _) in ADJUDICATION.items() if f)
    print(f"items loaded:      {len(items)}")
    print(f"sweep flagged:     {len(hits)}  {hits}")
    print(f"adjudicated FIRES: {len(fires)}  {fires}")
    print(f"hand-rejected:     {len(hits) - len(fires)}")
    for k in hits:
        f, why = ADJUDICATION[k]
        print(f"  {'FIRES ' if f else 'reject'} {k}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
