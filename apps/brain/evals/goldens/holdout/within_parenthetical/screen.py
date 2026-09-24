"""Decomposes every WITHIN deadline in the corpus by WHICH part of
`_WITHIN_RE` rejects it: the NUMERAL, the UNIT MODIFIER, or the PREPOSITION.

Standing Principle 7, and the first draft of this script failed it in the
instructive direction: it captured "three (3) calendar" as one numeral blob,
so the unit-modifier class came back 0 -- a clean zero that reproduced
corpus.py's own conflation instead of measuring it. The gate below is what
caught that, and it is kept.
"""
import importlib.util, json, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parents[6]
spec = importlib.util.spec_from_file_location("corpus", ROOT / "apps/brain/evals/corpus.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
from obligo_brain.compiler.ir_compile import _WITHIN_RE, _UNIT_ALTERNATION

# Split the material between `within` and the unit token into a NUMERAL part
# and any residual UNIT MODIFIER ("calendar", "consecutive", ...). The split
# point is the last token carrying a digit or a closing paren.
def split_numeral(blob: str) -> tuple[str, str]:
    toks = blob.split()
    last = -1
    for i, t in enumerate(toks):
        if re.search(r"[\d)]", t):
            last = i
    if last < 0:
        return blob.strip(), ""
    return " ".join(toks[: last + 1]), " ".join(toks[last + 1 :])

NUM_RE = re.compile(r"^\d+(?:\.\d+)?$")

def classify(blob: str, unit: str, prep_ok: bool) -> str:
    numeral, modifier = split_numeral(blob)
    num_ok = bool(NUM_RE.match(numeral.strip()))
    mod_ok = modifier.strip() == ""
    if num_ok and mod_ok and prep_ok:
        return "A_accepted"
    causes = []
    if not num_ok:
        causes.append("numeral")
    if not mod_ok:
        causes.append("unit")
    if not prep_ok:
        causes.append("prep")
    return "+".join(causes)

# --- KNOWN-ANSWER GATE ------------------------------------------------------
KNOWN = [
    ("thirty (30)",     "days",   True,  "numeral"),
    ("3 calendar",      "days",   True,  "unit"),
    ("three (3) calendar", "days", True, "numeral+unit"),
    ("24",              "months", False, "prep"),
    ("30",              "days",   True,  "A_accepted"),
    ("five (5) business", "days", False, "numeral+unit+prep"),
]
for blob, unit, prep, expected in KNOWN:
    got = classify(blob, unit, prep)
    assert got == expected, f"GATE FAILED: {blob!r}/{unit!r} prep={prep} -> {got}, expected {expected}"
print(f"known-answer gate: {len(KNOWN)}/{len(KNOWN)} PASS")
assert _WITHIN_RE.match("within 30 days of X")
assert not _WITHIN_RE.match("within 3 calendar days of X")
assert not _WITHIN_RE.match("within thirty (30) days of X")
assert not _WITHIN_RE.match("within 24 months following X")
print("production-regex gate: 4/4 PASS")

# --- the sweep --------------------------------------------------------------
manifest = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
PHRASE_RE = re.compile(
    r"\bwithin\s+([^,;.]{1,60}?)\s*\b(" + _UNIT_ALTERNATION + r")\b(\s+\w+)?",
    re.IGNORECASE,
)

counts = collections.Counter()
per_doc = collections.defaultdict(set)
examples = collections.defaultdict(list)
corpus_bare = corpus_paren = 0
recon_bare = recon_paren = 0

for kind, doc in c._iter_docs(manifest):
    text = c.extract_text(c._doc_path(ROOT / ".corpus", kind, doc["id"], doc).read_bytes(), kind)
    for sentence in [s for s in c.split_sentences(text) if c._MODAL_RE.search(s)]:
        b, p = c.classify_within(sentence)
        corpus_bare += b; corpus_paren += p
        for m in PHRASE_RE.finditer(sentence):
            blob, unit, tail = m.group(1), m.group(2), (m.group(3) or "")
            prep_ok = tail.strip().lower() == "of"
            cls = classify(blob, unit, prep_ok)
            counts[cls] += 1
            per_doc[cls].add(doc["id"])
            if len(examples[cls]) < 3:
                examples[cls].append(f'{doc["id"]}: "within {blob} {unit}{tail}..."')
            # corpus.py ignores the preposition entirely: it reconstructs " of X".
            if classify(blob, unit, True) == "A_accepted":
                recon_bare += 1
            else:
                recon_paren += 1

total = sum(counts.values())
print("\n--- RECONCILIATION against corpus.py's own metric (the second gate) ---")
print(f"  corpus.py   bare/paren = {corpus_bare} / {corpus_paren}")
print(f"  this script bare/paren = {recon_bare} / {recon_paren}")
assert (recon_bare, recon_paren) == (corpus_bare, corpus_paren), "RECONCILIATION FAILED"
print("  RECONCILES EXACTLY")

print(f"\n--- decomposition of all {total} WITHIN deadlines in modal sentences ---")
for k, n in counts.most_common():
    print(f"  {k:24} {n:4}  ({n/total:5.1%})  across {len(per_doc[k]):2} documents")

unit_class = sum(n for k, n in counts.items() if "unit" in k)
print(f"\n  UNIT-MODIFIER class (any cause set containing 'unit'): {unit_class}"
      f"  across {len(set().union(*[per_doc[k] for k in counts if 'unit' in k]) if unit_class else set())} documents")
print(f"  of corpus.py's {corpus_paren}-strong 'parenthetical' bucket, "
      f"{sum(n for k,n in counts.items() if 'unit' in k and 'prep' not in k)} are unit-caused")

mods = collections.Counter()
for kind, doc in c._iter_docs(manifest):
    text = c.extract_text(c._doc_path(ROOT / ".corpus", kind, doc["id"], doc).read_bytes(), kind)
    for sentence in [s for s in c.split_sentences(text) if c._MODAL_RE.search(s)]:
        for m in PHRASE_RE.finditer(sentence):
            _, modifier = split_numeral(m.group(1))
            if modifier.strip():
                mods[f"{modifier.strip().lower()} {m.group(2).lower()}"] += 1
print("\n  rejected unit strings:", dict(mods.most_common(15)))

print("\n--- examples ---")
for k, _ in counts.most_common():
    print(f"  {k}:")
    for e in examples[k]:
        print(f"     {e}")
