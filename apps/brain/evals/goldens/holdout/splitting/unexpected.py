"""§21 R6's UNEXPECTED over-count, measured for the first time.

Classifies every grounded model candidate in the 35 gold cassettes against BOTH annotators'
spans, using the harness's own alignment rule (align.py: IoU >= 0.5, per segment).

  GOLD_MATCH  aligns to a locked gold item                      -> scoreable today
  COLD_ONLY   aligns to NO gold item but to a cold item         -> scores UNEXPECTED today
  NEITHER     aligns to no item on either side                  -> scores UNEXPECTED today
  UNGROUNDED  span_text is not a substring of segment_text      -> rejected before scoring

Standing Principle 7: the known answer asserted before any total is used is C17-066 run 1,
established in RESULTS.md / comparison.json as gold item C17-02 matched plus the
'Each Party ... indemnify' clause that gold names in its own notes and does not annotate.
"""
import json, glob, os, hashlib, collections

G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
C = "/Users/rajitagrawal/obligo/apps/brain/evals/cassettes/gold"

seg_text = {}
for p in glob.glob(f"{G}/holdout/packet/segments/*.json"):
    d = json.load(open(p)); seg_text[d["segment_id"]] = d["segment_text"]
GOLD = collections.defaultdict(list)
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d = json.load(open(p))
    GOLD[d["segment_id"]].append((d["item_id"], d["span_char_start"], d["span_char_end"]))
COLD = collections.defaultdict(list)
for p in glob.glob(f"{G}/holdout/cold/*.json"):
    if p.endswith(".py"): continue
    d = json.load(open(p))
    for i, it in enumerate(d["items"], 1):
        COLD[d["segment_id"]].append((f"cold{i}", it["span_char_start"], it["span_char_end"]))

def iou(a, b):
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union else 0.0
def best(sp, lst):
    return max((iou(sp, (s, e)), n) for n, s, e in lst) if lst else (0.0, None)

rows = []
for seg in sorted(os.listdir(C)):
    text = seg_text[seg]
    for run in (1, 2, 3):
        p = f"{C}/{seg}/run{run}.json"
        if not os.path.exists(p): continue
        d = json.load(open(p))
        assert hashlib.sha256(text.encode()).hexdigest() == d["segment_sha256"], \
            f"{seg} run{run}: packet text does not match cassette segment_sha256"
        for r in d["responses"]:
            try: obj = json.loads(r["json"]["choices"][0]["message"]["content"])
            except Exception: continue
            for o in obj.get("obligations", []):
                st = o.get("span_text", ""); i = text.find(st)
                if i < 0:
                    rows.append((seg, run, "UNGROUNDED", 0.0, 0.0, st)); continue
                sp = (i, i + len(st))
                gi, _ = best(sp, GOLD[seg]); ci, _ = best(sp, COLD[seg])
                cls = "GOLD_MATCH" if gi >= 0.5 else ("COLD_ONLY" if ci >= 0.5 else "NEITHER")
                rows.append((seg, run, cls, round(gi, 3), round(ci, 3), st))

k = [r for r in rows if r[0] == "C17-066" and r[1] == 1]
print("KNOWN-ANSWER CHECK -- C17-066 run 1 must be 1 GOLD_MATCH + 1 COLD_ONLY:")
for r in k: print(f"   {r[2]:11} goldIoU={r[3]:<6} coldIoU={r[4]:<6} | {r[5][:78]}")
assert sorted(r[2] for r in k) == ["COLD_ONLY", "GOLD_MATCH"], "KNOWN-ANSWER CHECK FAILED"
print("   PASSED\n")

c = collections.Counter(r[2] for r in rows)
print(f"All 12 cassette-covered segments, all {len({(r[0],r[1]) for r in rows})} recorded runs "
      f"-- {len(rows)} candidates:")
for key in ("GOLD_MATCH", "COLD_ONLY", "NEITHER", "UNGROUNDED"):
    print(f"   {key:11} {c[key]}")
scoreable_fp = c["COLD_ONLY"] + c["NEITHER"]
print(f"\n   currently UNEXPECTED (grounded, aligns to no gold item): {scoreable_fp}")
print(f"   of which on a clause the second annotator ruled a genuine obligation: "
      f"{c['COLD_ONLY']} = {c['COLD_ONLY']/scoreable_fp:.0%}")

for label in ("COLD_ONLY", "NEITHER"):
    print(f"\n{label} candidates, by distinct clause:")
    agg = collections.Counter((r[0], r[5][:72]) for r in rows if r[2] == label)
    for (seg, sp), n in sorted(agg.items()):
        print(f"   {seg}  x{n} run(s) | {sp}")
