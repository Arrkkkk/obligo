"""Applies PREREGISTRATION.md's conform predicate to recorded cassettes.

The predicate is three-valued by design -- CONFORM / MERGED / DROPPED / OTHER --
because `v3` fails the two `C11-094` pairs by DIFFERENT mechanisms (pair 1
merges, pair 2 drops a phrase). Collapsing them to a boolean would hide that a
wording had changed behaviour without conforming.

Reads cassettes only. No model call, no database. Safe to re-run.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]

# PREREGISTRATION.md §1's targets, quoted from the committed gold items and from
# the hold-out's own sentence. Nothing here is derived at runtime: these are the
# strings the pass/fail turns on, fixed before any call was sent.
PAIRS = {
    ("C11-094", 1): ("If the Principal is a natural person",
                     "upon the death or mental incapacity of a Principal"),
    ("C11-094", 2): ("In the case of transfer by devise or inheritance",
                     "if the heir is not approved or there is no heir"),
    ("E02-010", 1): ("if payment is not received in full when due",
                     "upon ten (10) days prior written 3 notice from MedQuist to CBay"),
}
# The single-condition control inside C11-094 (gold item C11-02). Splitting it is
# a FALSE POSITIVE for Rule B.
CONTROL = ("C11-094", "If the conveyance of the Principal's interest to a party acceptable "
                      "to BKC has not taken place within the twelve (12) month period")
# E02-010's artifact-stripped variant, recorded so a normalisation failure stays
# distinguishable from a merge or a drop (PREREGISTRATION.md's second disclosure).
ARTIFACT_STRIPPED = {
    "upon ten (10) days prior written 3 notice from MedQuist to CBay":
        "upon ten (10) days prior written notice from MedQuist to CBay",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def classify(entries: list[str], a: str, b: str) -> tuple[str, str]:
    """Returns (verdict, evidence)."""
    ents = [norm(e) for e in entries]
    na, nb = norm(a), norm(b)
    if na in ents and nb in ents:
        return "CONFORM", "both phrases as separate entries"
    merged = {f"{na}, {nb}", f"{na},{nb}"}
    for e in ents:
        if e in merged:
            return "MERGED", f"one comma-joined entry: {e[:70]!r}"
    stripped = norm(ARTIFACT_STRIPPED.get(b, b))
    if na in ents and stripped in ents and stripped != nb:
        return "CONFORM_ARTIFACT_STRIPPED", (
            "both phrases present, but phrase B was NORMALISED -- the OCR artifact "
            "was silently dropped, so this is a corpus-artifact effect, not Rule B")
    present = [p for p, v in (("A", na), ("B", nb)) if v in ents]
    if len(present) == 1:
        return "DROPPED", f"only phrase {present[0]}; emitted {ents!r}"[:160]
    return "OTHER", f"neither phrase verbatim; emitted {ents!r}"[:160]


def entries_of(cassette_path: pathlib.Path) -> list[list[str]]:
    """Every `condition_raws` list the recorded responses contain, in order."""
    d = json.loads(cassette_path.read_text())
    out = []
    for r in d["responses"]:
        content = r["json"]["choices"][0]["message"]["content"]
        try:
            obj = json.loads(content)
        except Exception:
            continue
        for o in obj.get("obligations", []) or []:
            if isinstance(o, dict) and isinstance(o.get("condition_raws"), list):
                out.append([str(x) for x in o["condition_raws"]])
    return out


def modal(verdicts: list[str]) -> tuple[str, str]:
    """§6's modal outcome, with §6.1's tie rule: ties resolve to the WORST
    observed outcome, never rounding in the pipeline's favour."""
    if not verdicts:
        return "NO RUNS", "nothing recorded"
    counts = {v: verdicts.count(v) for v in set(verdicts)}
    top = max(counts.values())
    winners = sorted(v for v, n in counts.items() if n == top)
    order = ["OTHER", "DROPPED", "MERGED", "CONFORM_ARTIFACT_STRIPPED", "CONFORM"]
    if len(winners) > 1:
        worst = min(winners, key=lambda v: order.index(v) if v in order else 0)
        return worst, f"TIE {counts} -> worst observed (§6.1/G2), UNSTABLE"
    unstable = "" if top == len(verdicts) else f" UNSTABLE {counts}"
    return winners[0], f"{top}/{len(verdicts)}{unstable}"


def score_dir(label: str, root: pathlib.Path) -> dict:
    print(f"\n{'='*78}\n{label}   ({root})\n{'='*78}")
    if not root.is_dir():
        print("  no cassettes recorded")
        return {}
    results = {}
    for seg_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        seg = seg_dir.name
        pairs = [k for k in PAIRS if k[0] == seg]
        if not pairs:
            continue
        runs = sorted(seg_dir.glob("run*.json"))
        print(f"\n  {seg}: {len(runs)} run(s) recorded")
        for key in sorted(pairs):
            a, b = PAIRS[key]
            verdicts = []
            for rp in runs:
                best = ("OTHER", "no candidate carried both phrases")
                for ents in entries_of(rp):
                    v, ev = classify(ents, a, b)
                    rank = ["OTHER", "DROPPED", "MERGED",
                            "CONFORM_ARTIFACT_STRIPPED", "CONFORM"]
                    if rank.index(v) > rank.index(best[0]):
                        best = (v, ev)
                verdicts.append(best[0])
                print(f"     pair {key[1]} {rp.stem}: {best[0]:26} {best[1][:90]}")
            m, note = modal(verdicts)
            passed = m in ("CONFORM",)
            print(f"     pair {key[1]} MODAL: {m:26} [{note}]  -> "
                  f"{'PASS' if passed else 'FAIL'}")
            results[key] = {"runs": verdicts, "modal": m, "note": note, "pass": passed}
        # the single-condition control
        if seg == CONTROL[0]:
            ctl = norm(CONTROL[1])
            for rp in runs:
                splits = [e for ents in entries_of(rp) for e in ents
                          if norm(e) != ctl and norm(e) and norm(e) in ctl]
                emitted = any(ctl in [norm(e) for e in ents] for ents in entries_of(rp))
                print(f"     CONTROL {rp.stem}: "
                      f"{'intact (single entry)' if emitted else 'not emitted'}"
                      f"{'  *** SPLIT -- FALSE POSITIVE: ' + str(splits[:2]) if splits else ''}")
    return results


def main() -> int:
    v3_probe = score_dir("v3 -- HOLD-OUT BASELINE (recorded live)", HERE / "v3")
    v4 = score_dir("v4 -- THE CANDIDATE", HERE / "v4")
    gold = score_dir("v3 -- C11-094 BASELINE (committed gold cassettes, zero spend)",
                     ROOT / "apps/brain/evals/cassettes/gold")
    print(f"\n{'='*78}\nSUMMARY\n{'='*78}")
    for label, res in (("v3 gold baseline", gold), ("v3 hold-out baseline", v3_probe),
                       ("v4", v4)):
        if not res:
            print(f"  {label:24} -- nothing scored")
            continue
        for key in sorted(res):
            r = res[key]
            print(f"  {label:24} {key[0]} pair {key[1]}: {r['modal']:26} "
                  f"{'PASS' if r['pass'] else 'FAIL'}  [{r['note']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
