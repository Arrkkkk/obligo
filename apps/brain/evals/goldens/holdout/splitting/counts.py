"""Per-segment item counts, the 9-vs-10 reconciliation, and the density confound.

Known-answer check: reproduces RESULTS.md's published 41 cold / 32 gold / 22 segments
and its six named transitions before any new number is read off this script.
"""
import json, glob, statistics, sys, collections

G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
sys.path.insert(0, "/Users/rajitagrawal/obligo/apps/brain")
sys.path.insert(0, "/Users/rajitagrawal/obligo/apps/brain/src")
from evals import corpus  # noqa: E402

gold = collections.Counter(); batch = {}; items = collections.defaultdict(list)
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d = json.load(open(p))
    gold[d["segment_id"]] += 1
    batch[d["segment_id"]] = p.split("/")[-3]
    items[d["segment_id"]].append(d["item_id"])

text = {}
for p in glob.glob(f"{G}/holdout/packet/segments/*.json"):
    d = json.load(open(p)); text[d["segment_id"]] = d["segment_text"]

cold = {}
for p in glob.glob(f"{G}/holdout/cold/*.json"):
    if p.endswith(".py"): continue
    d = json.load(open(p)); cold[d["segment_id"]] = len(d["items"])

rows = []
for s in sorted(cold):
    modal = len([x for x in corpus.split_sentences(text[s]) if corpus._MODAL_RE.search(x)])
    rows.append((s, batch[s], modal, len(text[s]), gold[s], cold[s], cold[s] - gold[s]))

print(f"{'segment':10} {'batch':8} {'modal':>5} {'chars':>6} {'gold':>4} {'cold':>4} {'surp':>4}")
for r in rows:
    print(f"{r[0]:10} {r[1]:8} {r[2]:>5} {r[3]:>6} {r[4]:>4} {r[5]:>4} {r[6]:>4}"
          + ("  <== DISAGREE" if r[6] else ""))

tg, tc = sum(r[4] for r in rows), sum(r[5] for r in rows)
dis = [r for r in rows if r[6]]
print(f"\nKNOWN-ANSWER CHECK vs RESULTS.md: gold={tg} (32) cold={tc} (41) segments={len(rows)} (22)")
print(f"  disagreeing segments = {len(dis)} (6): "
      + " · ".join(f"{r[0]} {r[4]}->{r[5]}" for r in dis))
# Asserted, not merely printed: a check that only prints is a check nobody reads.
assert (tg, tc, len(rows)) == (32, 41, 22), f"KNOWN-ANSWER CHECK FAILED: {(tg, tc, len(rows))}"
assert {r[0] for r in dis} == {"C04-117", "C11-094", "C17-021", "C17-066",
                               "E03-005", "E08-005"}, "KNOWN-ANSWER CHECK FAILED: transitions"
assert [(r[4], r[5]) for r in dis] == [(2, 3), (1, 3), (1, 3), (1, 3), (1, 2), (1, 2)], \
    "KNOWN-ANSWER CHECK FAILED: transition counts"
print("  PASSED")
print(f"\nITEM-COUNT SURPLUS = {sum(r[6] for r in dis)}   "
      f"(RESULTS.md channel-4 reports 10 UNMATCHED cold items; the 10th is C14-076, "
      f"where counts agree 2/2 -- see comparison.json per_seg)")

cmp = json.load(open(f"{G}/holdout/comparison.json"))
print("\ncomparison.json per_seg rows with unmatched cold, [seg, gold_n, cold_n, unmatched_cold]:")
for r in cmp["per_seg"]:
    if r[3]: print("   ", r)
print("  unmatched_cold total:", cmp["unmatched_cold"])

print("\nPER-BATCH (batch and density are CONFOUNDED; this script measures both, resolves neither)")
print(f"{'batch':8} {'segs':>4} {'gold':>4} {'cold':>4} {'g/seg':>6} {'c/seg':>6} {'surplus':>7} {'segs_w_surp':>11} {'mean_modal':>10}")
for b in sorted({r[1] for r in rows}):
    r = [x for x in rows if x[1] == b]
    print(f"{b:8} {len(r):>4} {sum(x[4] for x in r):>4} {sum(x[5] for x in r):>4} "
          f"{sum(x[4] for x in r)/len(r):>6.2f} {sum(x[5] for x in r)/len(r):>6.2f} "
          f"{sum(x[6] for x in r):>7} {sum(1 for x in r if x[6]):>11} "
          f"{statistics.mean([x[2] for x in r]):>10.2f}")

w = [r[2] for r in rows if r[6]]; wo = [r[2] for r in rows if not r[6]]
print(f"\nmodal-bearing sentences, segments WITH surplus:    {sorted(w)}  mean {statistics.mean(w):.2f}")
print(f"modal-bearing sentences, segments WITHOUT surplus: {sorted(wo)}  mean {statistics.mean(wo):.2f}")
dense = [r for r in rows if r[2] >= 3]
print("\nconditioning on density >= 3 modal-bearing sentences:")
for b in sorted({r[1] for r in dense}):
    r = [x for x in dense if x[1] == b]
    print(f"  {b}: {sum(1 for x in r if x[6])}/{len(r)} segments with surplus")
