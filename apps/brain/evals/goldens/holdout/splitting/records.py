"""The record audit: is there ANY disposition for each surplus clause?

GOLD-SIDE (sections 1-3), three sources searched exhaustively: exclusions.json (segment- and
sub-sentence-level), the populated section 21 R6 not_annotatable spans, and every gold item's
annotator_notes on the six disagreeing segments. This is the question section 2.1 step 4's
bias safeguard actually asks, because the reviewer's rejection sample can only sample
gold-side logs.

COLD-SIDE (section 4, added 2026-09-05), a FOURTH source: holdout/cold/*.json. Added after
the C14-076 investigation found that this script's gold-side result had been generalised, in
three retrofitted segment files, from "no gold-side disposition exists" (true, and the whole
point of section 2.7) into "neither annotator recorded why" (false, and offered as evidence
for one of two competing readings). All 22 cold files carry a substantive segment_notes and
16 of 22 explicitly discuss excluded sentences; none of it was read by any script.

KEEP THE TWO SIDES LABELLED AND NEVER MERGE THEM. A cold-side disposition does NOT satisfy
section 2.1's safeguard -- the cold annotator is a second annotator, not the reviewer, and
its notes are evidence, not authority. Section 4 exists so a claim of silence is falsifiable,
not so cold prose can be counted as a gold-side record.

The per-span verdict across all 22 segments (not just these six) is
holdout/band_risk/cold_dispositions.py, which carries the known-answer check.
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

print("\n=== 4. COLD-SIDE (fourth source): holdout/cold/*.json -- NOT a gold-side record ==="
      "\n    A cold ITEM is a stronger disposition than a prose exclusion: the cold annotator"
      "\n    did not merely say why not, it said what the clause is, field by field.")
for p in sorted(glob.glob(f"{G}/holdout/cold/*.json")):
    d = json.load(open(p))
    seg, notes = d["segment_id"], (d.get("segment_notes") or "")
    if seg not in PROBE:
        continue
    hits = list(re.finditer(PROBE[seg], notes, re.I))
    items = [i["span_text"] for i in d.get("items", [])]
    print(f"  {seg}: {len(items)} cold item(s), segment_notes {len(notes)} chars, "
          f"{len(hits)} probe hit(s) in notes")
    for n, sp in enumerate(items, 1):
        print(f"     item {n}: {sp[:88]!r}")
    for m in hits:
        print("     notes ..." + notes[max(0, m.start()-95):m.end()+95].replace("\n", " ") + "...")
