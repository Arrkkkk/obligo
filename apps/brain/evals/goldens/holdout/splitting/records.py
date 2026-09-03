"""The record audit: is there ANY gold-side disposition for each surplus clause?

Three sources are searched exhaustively: exclusions.json (segment- and sub-sentence-level),
the populated §21 R6 not_annotatable spans, and every gold item's annotator_notes on the
six disagreeing segments.
"""
import json, glob, re

G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"

print("=== 1. exclusions.json: sub-sentence ('#') entries by batch ===")
for p in sorted(glob.glob(f"{G}/batch0*/exclusions.json")):
    d = json.load(open(p)); sub = [e["segment_id"] for e in d if "#" in e["segment_id"]]
    print(f"  {p.split('/')[-2]}: {len(d):>2} entries, {len(sub)} sub-sentence  {sub}")

print("\n=== 2. §21 R6 not_annotatable spans actually populated ===")
tot = 0
for p in sorted(glob.glob(f"{G}/batch0*/segments/*.json")):
    d = json.load(open(p)); na = d.get("not_annotatable", []); tot += len(na)
    print(f"  {p.split('/')[-1]}: {len(na)} span(s)")
    for s in na:
        print(f"     [{s['span_char_start']}:{s['span_char_end']}] {s.get('reason','')[:100]}")
print(f"  TOTAL populated spans across the whole gold set: {tot}")
ex = {e["segment_id"] for p in glob.glob(f"{G}/batch0*/exclusions.json")
      for e in json.load(open(p))}
print("  'E03-005#discuss' IS logged in exclusions.json:", "E03-005#discuss" in ex)
print("  ...and was never transcribed into E03-005.json's not_annotatable list"
      " (only #itemize is present) -- R6 names BOTH as its transcription source.")

print("\n=== 3. every gold annotator_notes on the six disagreeing segments, searched for the"
      " omitted clauses ===")
PROBE = {
    "C04-117": r"acknowledg|reserves|defer",
    "C11-094": r"executor shall|best efforts|shall have the option|devise",
    "C17-021": r"Without limiting|assist|contain and remedy|second sentence",
    "C17-066": r"assumed|separated portion|indemnif|third sentence",
    "E03-005": r"discuss",
    "E08-005": r"It shall ensure|first sentence|pronoun",
}
for p in sorted(glob.glob(f"{G}/batch0*/items/*.json")):
    d = json.load(open(p))
    if d["segment_id"] not in PROBE: continue
    n = d.get("annotator_notes", "")
    hits = list(re.finditer(PROBE[d["segment_id"]], n, re.I))
    print(f"  {d['item_id']:8} ({d['segment_id']}, {d['guideline_version']}): "
          f"{len(hits)} hit(s)")
    for m in hits:
        print("     ..." + n[max(0, m.start()-95):m.end()+95].replace("\n", " ") + "...")
