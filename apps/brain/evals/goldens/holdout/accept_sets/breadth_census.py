"""§3.6's accept-set breadth census -- the measurement behind §10.1 **F5** (ruled v0.58).

Two questions, kept apart because they have different answers:

  (1) HOW WIDE are the sets, against §3.6's own stated 3-6 band?
  (2) DO THEY SPAN THE DEPTH THE MODEL ACTUALLY EMITS -- i.e. does each set carry a
      head-only (1-token) member at all?

(2) is the one that matters for criterion 2. `OBJECT_CLASS_INVESTIGATION.md` §9.2/§9.3
measured the model emitting a head-only label 28% of the time while most gold sets
cannot accept one; this reproduces that coverage figure at n=36 so the v0.45 anchor
can be checked against the four items added since, rather than assumed to survive them.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO
-----------------------------------------
It does not propose per-item widenings. §3.4's justification test requires a widening
to be defensible FROM THE SPAN ALONE, stated without reference to any prediction, so a
script that ranked items by how often the model missed them would be building exactly
the artefact the rule forbids. The clause-5 outcomes that motivated F5's ruling are
produced by `run_scoring.run()` and read as DIAGNOSIS; the ruling itself is a uniform
forward rule, applied to every new item, for that reason.

Reads only committed gold JSON -- no corpus, no database, no network.
"""

from __future__ import annotations

import json
import pathlib
import statistics

GOLDENS = pathlib.Path(__file__).resolve().parents[2]
MIN_EXPECTED_ITEMS = 36

# §3.6's own stated authoring band.
BAND_LOW, BAND_HIGH = 3, 6


def load_items() -> list[dict]:
    items = sorted(
        (json.loads(p.read_text()) for p in GOLDENS.glob("batch0*/items/*.json")),
        key=lambda d: d["item_id"],
    )
    if len(items) < MIN_EXPECTED_ITEMS:
        raise AssertionError(
            f"loaded {len(items)} gold items from {GOLDENS}, expected at least "
            f"{MIN_EXPECTED_ITEMS} -- see restatement_screen.py's note on silent zeros"
        )
    return items


def tokens(label: str) -> list[str]:
    return [t for t in label.split("_") if t]


def has_head_only_member(item: dict) -> bool:
    return any(len(tokens(m)) == 1 for m in item["object_class_accept_set"])


def head_only_coverage(items: list[dict]) -> tuple[int, int]:
    """(items carrying a 1-token member, total). §3.6's v0.58 forward rule exists
    because this ratio is low while the model emits head-only labels often."""
    return sum(1 for i in items if has_head_only_member(i)), len(items)


def outside_band(items: list[dict]) -> dict[str, list[tuple[str, int]]]:
    below = [(i["item_id"], len(i["object_class_accept_set"]))
             for i in items if len(i["object_class_accept_set"]) < BAND_LOW]
    above = [(i["item_id"], len(i["object_class_accept_set"]))
             for i in items if len(i["object_class_accept_set"]) > BAND_HIGH]
    return {"below": below, "above": above}


def main() -> None:
    items = load_items()
    for field in ("object_class_accept_set", "action_accept_set"):
        sizes = [len(i.get(field) or []) for i in items]
        dist = {k: sizes.count(k) for k in sorted(set(sizes))}
        print(f"{field}: n={len(sizes)} mean={statistics.mean(sizes):.2f} "
              f"median={statistics.median(sizes)} min={min(sizes)} max={max(sizes)} dist={dist}")

    band = outside_band(items)
    print(f"\n=== outside §3.6's {BAND_LOW}-{BAND_HIGH} band ===")
    print(f"  below: {band['below'] or 'none'}")
    print(f"  above: {band['above'] or 'none'}")

    carried, total = head_only_coverage(items)
    print(f"\n=== head-only (1-token) member coverage: {carried}/{total} = "
          f"{100 * carried / total:.0f}% ===")
    print("  items carrying NO head-only member (the v0.58 forward rule's target "
          "shape -- NOT a retroactive to-do list, see §3.6):")
    for item in items:
        if not has_head_only_member(item):
            print(f"    {item['item_id']:8} {item['object_class']}")


if __name__ == "__main__":
    main()
