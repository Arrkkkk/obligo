"""AUDIT: does a cold-side disposition exist for every non-ANNOTATED §2.7 disposition?

Written after the C14-076 investigation found that `splitting/records.py` -- correctly,
per its own docstring -- searches only the three GOLD-side places a disposition can live
(exclusions.json, §21 R6 not_annotatable, gold annotator_notes). The §2.7 retrofit
inherited that scope and then generalised "no gold-side record" into "neither annotator
recorded why", which is a different and falsifiable claim.

`holdout/cold/*.json` is a fourth source. Each of the 22 files carries a substantive
`segment_notes` (734-3,260 chars) and, for the segments where the cold annotator found
more obligations than gold, full field-level items. This script asks, per span:

  COLD_ITEM  the cold annotator ANNOTATED this span -- the strongest possible disposition
  COLD_NOTE  cold disposed of it in prose in segment_notes, with rules cited
  NONE       genuinely no cold-side record either

Standing Principle 7: the classifier is pinned to six spans whose answer was established
by reading the files directly during the investigation, before any total is reported.
"""
import json, glob, re, sys, collections, pathlib

G = pathlib.Path(__file__).resolve().parents[2]          # evals/goldens
COLD = {json.load(open(p))["segment_id"]: json.load(open(p))
        for p in sorted(glob.glob(str(G / "holdout/cold/*.json")))}
SEGTEXT = {}
for p in glob.glob(str(G / "batch0*/items/*.json")):
    d = json.load(open(p)); SEGTEXT.setdefault(d["segment_id"], d["segment_text"])

def norm(s): return re.sub(r"\s+", " ", s).strip().lower()

def locate(hay, needle):
    """char span of `needle` inside `hay`, whitespace-insensitively; None if absent."""
    i = norm(hay).find(norm(needle))
    return None if i < 0 else (i, i + len(norm(needle)))

def classify(seg_id, span_text):
    cold = COLD.get(seg_id)
    if cold is None:
        return "NONE", "no cold file"
    seg = SEGTEXT.get(seg_id, "")
    a = locate(seg, span_text)
    for n, it in enumerate(cold.get("items", []), 1):
        b = locate(seg, it["span_text"])
        if a and b:
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if hi > lo:
                inter = hi - lo
                iou = inter / ((a[1]-a[0]) + (b[1]-b[0]) - inter)
                # containment alone is only meaningful for a span with real clause
                # content: a 6-char connective (', and ') sits 100% inside a long
                # §8.3.1 span and was classified COLD_ITEM by an earlier draft.
                contained = inter / (a[1] - a[0]) >= 0.60 and (a[1] - a[0]) >= 40
                if iou >= 0.30 or contained:
                    return "COLD_ITEM", f"cold item {n}, IoU {iou:.3f}"
    notes = norm(cold.get("segment_notes") or "")
    words = norm(span_text).split()
    for w in (12, 9, 6):                       # longest distinctive run that still matches
        for i in range(0, max(1, len(words) - w + 1)):
            frag = " ".join(words[i:i+w])
            if len(frag) > 25 and frag in notes:
                return "COLD_NOTE", f"quoted in segment_notes ({w}-word run)"
    return "NONE", "no cold item overlap, not quoted in segment_notes"

rows = []
for p in sorted(glob.glob(str(G / "batch0*/segments/*.json"))):
    d = json.load(open(p))
    for x in d.get("dispositions", []):
        if x["disposition"] == "ANNOTATED":
            continue
        verdict, why = classify(d["segment_id"], x["span_text"])
        rows.append({"seg": d["segment_id"], "disp": x["disposition"],
                     "span": x["span_text"], "verdict": verdict, "why": why})

# --- KNOWN-ANSWER CHECK (Standing Principle 7) -------------------------------
KNOWN = {
    ("C14-076", "Each party will be solely responsible"): "COLD_NOTE",
    ("C14-076", "Israel value added tax shall be added"): "COLD_NOTE",
    ("C11-094", "In the case of transfer by devise"):     "COLD_ITEM",
    ("C11-094", "If the conveyance of the Principal"):    "COLD_ITEM",
    ("C04-117", "Miltenyi, acting reasonably, reserves"):  "COLD_ITEM",
    ("C17-066", "Each Party making purchases"):            "COLD_ITEM",
}
print("=== KNOWN-ANSWER CHECK (6 spans read by hand during the investigation) ===")
ok = True
for (seg, frag), want in KNOWN.items():
    hit = [r for r in rows if r["seg"] == seg and r["span"].startswith(frag)]
    if not hit:
        print(f"  MISS {seg}: no disposition starting {frag!r}"); ok = False; continue
    got = hit[0]["verdict"]
    ok &= got == want
    print(f"  {'ok ' if got == want else 'BAD'} {seg}: {got:9} (want {want:9})  {frag!r}")
print(f"\nCLASSIFIER VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
if not ok:
    sys.exit(1)

c = collections.Counter(r["verdict"] for r in rows)
print(f"\n=== TOTALS: {len(rows)} non-ANNOTATED dispositions across 22 segments ===")
for k in ("COLD_ITEM", "COLD_NOTE", "NONE"):
    print(f"  {k:10} {c[k]:>3}   ({100*c[k]/len(rows):.0f}%)")

print("\n=== every AMBIGUOUS / NOT_ANNOTATABLE span (the consequential ones) ===")
for r in rows:
    if r["disp"] in ("AMBIGUOUS", "NOT_ANNOTATABLE"):
        print(f"  {r['seg']:10} {r['disp']:17} {r['verdict']:10} {r['why']:34} {r['span'][:52]!r}")

print("\n=== NOT_OBLIGATION_BEARING spans with NO cold-side record ===")
n = [r for r in rows if r["disp"] == "NOT_OBLIGATION_BEARING" and r["verdict"] == "NONE"]
print(f"  {len(n)} of {sum(1 for r in rows if r['disp']=='NOT_OBLIGATION_BEARING')} "
      f"-- these are the §2.7 bulk classes (headings, connectives, artifacts)")
for r in n[:8]:
    print(f"    {r['seg']:10} {r['span'][:60]!r}")
