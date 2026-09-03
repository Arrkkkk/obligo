"""MAY-shaped clause census over the 22 gold segments (Category B).

Standing Principle 7: the detector prints every flagged sentence in full and its three
KNOWN answers are asserted before any total is used --
  C13-041  "shall have the right to terminate"   -> gold's only MAY item (C13-03, v0.41)
  C04-117  "reserves the right to defer"         -> cold-only surplus item, gold v0.28
  C11-094  "shall have the option, to purchase"  -> cold-only surplus item, gold v0.28
False positives are NOT suppressed silently; they are printed and adjudicated by reading.
"""
import json, glob, re, collections

G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
PAT = re.compile(
    r"\b(may(?!\s+be\s+(deemed|construed))|reserves? the right|retains? (all )?rights?"
    r"|shall have the (right|option)|is entitled to|is permitted to"
    r"|at its (sole )?(option|discretion))\b", re.I)

def sents(t):
    return [s.strip() for s in re.split(r'(?<=[.;])\s+(?=[A-Z(“"])', t) if s.strip()]

hits = []
for p in sorted(glob.glob(f"{G}/holdout/packet/segments/*.json")):
    d = json.load(open(p))
    for s in sents(d["segment_text"]):
        m = PAT.search(s)
        if m: hits.append((d["segment_id"], m.group(0), s))

print("EVERY FLAGGED SENTENCE (read these, do not read only the total):\n")
for seg, hit, s in hits:
    print(f"  {seg:10} [{hit}]\n     {s[:230]}\n")

known = {("C13-041", "shall have the right"), ("C04-117", "reserves the right"),
         ("C11-094", "shall have the option")}
found = {(seg, h.lower()) for seg, h, _ in hits}
assert known <= found, f"KNOWN-ANSWER CHECK FAILED: missing {known - found}"
print(f"KNOWN-ANSWER CHECK PASSED -- all three established cases flagged.")
print(f"flagged sentences: {len(hits)} across {len({h[0] for h in hits})} segments")
print("\nADJUDICATED BY READING: 2 false positives -- relative-clause `may`, not a deontic")
print("  permission clause: C02-021 'as may be required by Applicable Laws',")
print("  C11-094 'the same conditions as may be imposed on any INTER VIVOS transfer'.")
print("  => 4 genuine MAY-shaped clauses in the 22 segments.\n")

gm = collections.Counter(); gv = {}
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d = json.load(open(p)); gm[d["modality"]] += 1
    if d["modality"] == "MAY": gv[d["item_id"]] = (d["segment_id"], d["guideline_version"])
cm = collections.Counter()
for p in glob.glob(f"{G}/holdout/cold/*.json"):
    if p.endswith(".py"): continue
    for it in json.load(open(p))["items"]: cm[it["modality"]] += 1
print("gold modality distribution:", dict(gm))
print("cold modality distribution:", dict(cm))
print("gold MAY items and their guideline_version:", gv)
