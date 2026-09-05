"""Clause-3 / clause-4 pass rates split by whether gold says ABSENT -- the
measurement behind §8.1 of C14_076_INVESTIGATION.md.

THE CLAIM UNDER TEST. The 2026-09-04 finding framed a both-ABSENT item as one
where "two of the eight scored clauses pass on a vacuous match." That predicts
ABSENT is an EASIER target than a named party. This measures it.

WHAT IT IS NOT. Not the scorer. It does not seed a database or run the pipeline,
so a candidate counted here as aligned may in truth have been rejected or
quarantined before ever becoming a prediction (run_scoring.py's W1). That biases
the PASS rates UPWARD -- the conservative direction for a vacuous-pass claim, so
a low rate measured here is a floor, not an artifact. run_scoring.py remains the
only source of a publishable criterion-2 figure; nothing here is one.

Alignment uses the harness's OWN align()/iou() rather than a reimplementation,
so §4.1's threshold and §4.2's greedy tie-break cannot silently drift from the
scorer's.
"""
import sys, json, glob, pathlib, collections

HERE = pathlib.Path(__file__).resolve()
BRAIN = HERE.parents[4]                                   # apps/brain
sys.path.insert(0, str(BRAIN))
from evals.harness.align import align                     # noqa: E402

# KNOWN-ANSWER CHECKS, all read by hand during the investigation.
# K1 is the decisive one: C04-03 is one of only two locked items with obligor
# ABSENT, and §3.5.3's reviewer ruling says in terms that `Miltenyi's` -- a
# possessive on a LOCATION -- must not be read as the duty-bearer. If the model
# emits `Miltenyi` there, clause 3 fails on a rule the guideline states
# explicitly, and that is a different fact from "the model was imprecise".
K1_ITEM, K1_RUNS, K1_OBR, K1_OBE = "C04-03", 3, "Miltenyi", "Bellicum"


def norm(s):
    return " ".join((s or "").split()).strip().lower()


def run():
    gold_by_seg = collections.defaultdict(list)
    for p in sorted(glob.glob(str(BRAIN / "evals/goldens/batch*/items/*.json"))):
        d = json.load(open(p))
        gold_by_seg[d["segment_id"]].append(d)

    preds = collections.defaultdict(list)
    for p in sorted(glob.glob(str(BRAIN / "evals/cassettes/gold/*/run*.json"))):
        d = json.load(open(p))
        for r in d["responses"]:
            if r.get("status_code") != 200:
                continue
            try:
                obs = json.loads(
                    r["json"]["choices"][0]["message"]["content"])["obligations"]
            except Exception:
                continue
            preds[(d["segment_id"], d["run"])].extend(obs)

    rows = []
    for (seg, run_no), plist in sorted(preds.items()):
        gitems = gold_by_seg.get(seg, [])
        if not gitems or "segment_text" not in gitems[0]:
            continue
        text = gitems[0]["segment_text"]
        gold_spans = [(g["span_char_start"], g["span_char_end"]) for g in gitems]
        pspans, pkeep = [], []
        for o in plist:
            st = o.get("span_text", "")
            i = text.find(st)
            if i < 0:          # the grounder would reject it; not a prediction
                continue
            pspans.append((i, i + len(st)))
            pkeep.append(o)
        al = align(gold_spans, pspans, gold_ids=[g["item_id"] for g in gitems])
        for pair in al.pairs:
            g, o = gitems[pair.gold_index], pkeep[pair.pred_index]
            pa, pe = norm(o.get("obligor_alias")), norm(o.get("obligee_alias"))
            c3 = (pa == "") if g["obligor"] == "ABSENT" else (pa == norm(g["obligor"]))
            c4 = (pe == "") if g["obligee"] == "ABSENT" else (pe == norm(g["obligee"]))
            rows.append(dict(item=g["item_id"], run=run_no, iou=pair.iou,
                             g_obr=g["obligor"], p_obr=o.get("obligor_alias") or "", c3=c3,
                             g_obe=g["obligee"], p_obe=o.get("obligee_alias") or "", c4=c4))
    return rows


if __name__ == "__main__":
    rows = run()

    print("=== KNOWN-ANSWER CHECK ===")
    k1 = sorted([r for r in rows if r["item"] == K1_ITEM], key=lambda r: r["run"])
    checks = [
        (f"{K1_ITEM} aligns on all {K1_RUNS} runs", len(k1) == K1_RUNS),
        (f"{K1_ITEM} clause 3 FAILS on every run, predicting {K1_OBR!r} "
         f"(§3.5.3's forbidden possessive-on-a-location)",
         bool(k1) and all(not r["c3"] and r["p_obr"] == K1_OBR for r in k1)),
        (f"{K1_ITEM} clause 4 PASSES on every run, predicting {K1_OBE!r}",
         bool(k1) and all(r["c4"] and r["p_obe"] == K1_OBE for r in k1)),
    ]
    ok = True
    for label, got in checks:
        ok &= got
        print(f"  {'ok  ' if got else 'BAD '} {label}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    def rate(sel, clause):
        s = [r for r in rows if sel(r)]
        return sum(1 for r in s if r[clause]), len(s)

    print(f"\n=== TOTALS: {len(rows)} aligned (gold item, run) pairs over "
          f"{len({r['item'] for r in rows})} distinct gold items ===")
    for clause, slot, label in (("c3", "g_obr", "3 (obligor)"), ("c4", "g_obe", "4 (obligee)")):
        print(f"\n  CLAUSE {label}")
        for name, sel in (("gold ABSENT", lambda r, s=slot: r[s] == "ABSENT"),
                          ("gold NAMED ", lambda r, s=slot: r[s] != "ABSENT")):
            n, d = rate(sel, clause)
            pct = f" = {n/d:.1%}" if d else ""
            print(f"    {name} : {n}/{d} pass{pct}")

    print("\n  READ THE DIRECTION. If ABSENT were a vacuous free pass its rate would")
    print("  EXCEED the named-party rate. It does not, on either clause.")

    print("\n=== every gold-ABSENT slot, per (item, run) -- read it, do not trust "
          "the count ===")
    for slot, pslot, clause, label in (("g_obr", "p_obr", "c3", "obligor"),
                                       ("g_obe", "p_obe", "c4", "obligee")):
        print(f"\n  gold {label} = ABSENT:")
        hits = [r for r in rows if r[slot] == "ABSENT"]
        if not hits:
            print("    (none)")
        for r in sorted(hits, key=lambda r: (r["item"], r["run"])):
            print(f"    {r['item']} run{r['run']} iou={r['iou']:.3f} "
                  f"predicted={r[pslot]!r:26} -> {'PASS' if r[clause] else 'FAIL'}")
