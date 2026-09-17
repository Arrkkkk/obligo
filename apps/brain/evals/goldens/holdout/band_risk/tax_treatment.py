"""Is there ANY adjudicated corpus precedent for a tax-INCLUSION / gross-up clause -- the
`C14-076` candidate 2 question -- or is the construction genuinely unprecedented?

WHY THIS EXISTS. `C14_076_INVESTIGATION.md` §10.4 asserted "the construction is UNIQUE
pool-wide" off a SINGLE narrow regex (a tax term plus `shall/will be
added|charged|invoiced|billed`). That is one pattern's opinion, not a census, and "no
precedent exists" is exactly the kind of negative claim that a too-narrow detector produces
for free. This script asks the question the way §8.8.4's lines were checked: cast a
deliberately WIDE net over every way this corpus could express "tax is added to / included
in / excluded from the amount payable", then cross-reference every hit against everything
that has actually been CLASSIFIED -- locked gold items, committed per-sentence dispositions,
and the exclusion logs -- and print every row for reading.

THE DISTINCTION THAT MATTERS. A hit is only *precedent* if some annotator has already ruled
on it. A hit in an unannotated pool segment is not precedent, it is just another instance.
The script reports the two separately and never merges them.

KNOWN ANSWERS. Three, spanning both verdicts and the case in question:
  C14-076  candidate 2  -- THE CASE. Must be flagged, and must show as UNCLASSIFIED/AMBIGUOUS.
  C14-076  candidate 1  -- flagged, and CLASSIFIED NOT_OBLIGATION_BEARING (§8.8.4, v0.56).
  C02-045  locked item C02-04 -- a tax clause CLASSIFIED obligation-bearing (action PAY).
A detector that cannot see a classified instance on both sides cannot support a claim that
no classified instance exists.
"""
import sys, re, json, pathlib, collections

BRAIN = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(BRAIN))
import evals.corpus as corpus                                  # noqa: E402

CORPUS = BRAIN.parents[1] / ".corpus"
GOLD = BRAIN / "evals" / "goldens"

TAX = r"(?:tax|taxes|taxation|vat|value[- ]added tax|gst|sales tax|duty|duties|tariff|tariffs|surcharge|surcharges|levy|levies)"

# Deliberately wide: every shape this corpus could use to put tax ON TOP OF, or INSIDE, or
# OUTSIDE, an amount payable. Each alternative is named so the output can be read by shape.
SHAPES = {
    "ADDED_TO":      re.compile(rf"\b{TAX}\b[^.;]{{0,90}}?\bbe\s+(?:added|charged|invoiced|billed|imposed|levied)\s+(?:to|on|upon)\b", re.I),
    "ADD_ACTIVE":    re.compile(rf"\b(?:add|adds|adding)\b[^.;]{{0,40}}?\b{TAX}\b[^.;]{{0,40}}?\b(?:to|on)\b", re.I),
    "EXCLUSIVE_OF":  re.compile(rf"\b(?:exclusive of|excluding|net of|before)\s+(?:any\s+|all\s+|applicable\s+)*{TAX}\b", re.I),
    "INCLUSIVE_OF":  re.compile(rf"\b(?:inclusive of|including|includes)\s+(?:any\s+|all\s+|applicable\s+)*{TAX}\b", re.I),
    "PLUS_TAX":      re.compile(rf"\b(?:plus|together with|in addition to)\s+(?:any\s+|all\s+|applicable\s+)*{TAX}\b", re.I),
    # RECALL HOLE FOUND BY THE KNOWN-ANSWER CHECK, not by re-reading the patterns. PLUS_TAX
    # requires the tax term AFTER the marker ("... plus any Taxes"). `C02-044`'s near-twin
    # sentence puts it BEFORE, as the subject -- "Such VAT and taxes, if any, will be payable
    # IN ADDITION TO the Transfer Price" -- so the single most on-point comparison in the
    # whole corpus was being missed by a census whose entire purpose is to find it.
    "TAX_ON_TOP":    re.compile(rf"\b{TAX}\b[^.;]{{0,70}}?\b(?:payable|added|charged)\b[^.;]{{0,40}}?\bin addition to\b", re.I),
    "GROSS_UP":      re.compile(r"\bgross(?:ed)?[- ]up\b", re.I),
    "AMOUNTS_PAYABLE": re.compile(rf"\bamounts?\s+payable\b[^.;]{{0,90}}?\b{TAX}\b|\b{TAX}\b[^.;]{{0,90}}?\bamounts?\s+payable\b", re.I),
    "BORNE_BY":      re.compile(rf"\b{TAX}\b[^.;]{{0,60}}?\bbe\s+borne\s+by\b", re.I),
}


def classified_index():
    """Everything an annotator has already ruled on, keyed by segment id.

    Three sources, kept LABELLED rather than merged: a locked gold item's span, a committed
    per-sentence disposition, and an exclusion-log entry.
    """
    idx = collections.defaultdict(list)
    for b in ("batch01", "batch02", "batch03"):
        for f in sorted((GOLD / b / "items").glob("*.json")):
            d = json.loads(f.read_text())
            idx[d["segment_id"]].append(("GOLD_ITEM", d["item_id"], d.get("span_text", "")))
        for f in sorted((GOLD / b / "segments").glob("*.json")):
            d = json.loads(f.read_text())
            for x in d.get("dispositions", []):
                idx[d["segment_id"]].append(
                    (f"DISPOSITION:{x['disposition']}", x.get("rule", "-"), x.get("span_text", "")))
        ex = GOLD / b / "exclusions.json"
        if ex.exists():
            for e in json.loads(ex.read_text()):
                sid = (e.get("segment_id") or e.get("id", "")).split("#")[0]
                idx[sid].append(("EXCLUSION_LOG", e.get("reason", "")[:70], e.get("span_text", "")))
    return idx


MIN_SPAN = 40   # see the docstring fault note below


def overlaps(sent, span):
    """Did the classification actually cover THIS sentence? Substring either way, since a
    disposition span may be a clause of the sentence or the sentence a clause of the span.

    FAULT FOUND BY THE KNOWN-ANSWER CHECK AND FIXED HERE, NOT IN THE OUTPUT. The first draft
    had no length floor, so `C14-076`'s two connective dispositions -- span_text `"."` and
    `", and"`, both legitimately `NOT_OBLIGATION_BEARING` under §2.6 -- are substrings of
    EVERY sentence in the segment and matched everything. The case in question came back
    classified `NOT_OBLIGATION_BEARING`, which is the answer the whole script exists to
    avoid asserting. This is the SAME fault class `band_risk/README.md` already records for
    `cold_dispositions.py` (which classified `", and "` as a cold item because it sits 100%
    inside a long span) and it is fixed the same way: a minimum span length.
    """
    a, b = re.sub(r"\s+", " ", sent).strip(), re.sub(r"\s+", " ", span).strip()
    if len(b) < MIN_SPAN:
        return False
    return a[:60] in b or b[:60] in a


def run():
    pool = corpus.build_pool(CORPUS, corpus.load_manifest())
    idx = classified_index()
    rows = []
    for seg in pool:
        for sent in corpus.split_sentences(seg["text"]):
            shapes = sorted(k for k, p in SHAPES.items() if p.search(sent))
            if not shapes:
                continue
            marks = [c for c in idx.get(seg["segment_id"], []) if overlaps(sent, c[2])]
            rows.append((seg["segment_id"], shapes, re.sub(r"\s+", " ", sent).strip(), marks))
    return pool, rows


# Two RECALL gates and two PRECISION gates. The precision gates matter as much as the recall
# ones here, and the first draft of this block got them wrong: it asserted that `C14-076`
# candidate 1 and `C02-045` would be flagged, on the assumption that "tax clause" and
# "tax-treatment clause" are the same class. THEY ARE NOT, and the check failing is what
# showed it -- both are ALLOCATION / PAYMENT clauses (who bears the tax, who pays it), not
# statements about tax being added to or included in an AMOUNT. Pinning them as NOT flagged
# is what keeps this census from quietly widening into "every sentence mentioning tax", which
# would make the precedent question unanswerable.
RECALL = {
    "C14-076-cand2": ("Israel value added tax shall be added",
                      "THE CASE. Must be flagged, and must read AMBIGUOUS -- NOT "
                      "NOT_OBLIGATION_BEARING, which is what the short-span overlap fault "
                      "produced before MIN_SPAN was added"),
    "C02-044":       ("will be payable in addition to the Transfer Price",
                      "the near-twin in another document: same two jobs, tax-on-top stated "
                      "agentlessly and the payment half carrying an explicit by-agent"),
}
PRECISION = {
    "C14-076-cand1": ("Each party will be solely responsible for any and all taxes",
                      "an ALLOCATION clause (§8.8.4 ABSORB), not a tax-treatment clause"),
    "C02-045":       ("solely responsible for the timely payment of all such VAT",
                      "a PAYMENT-DUTY clause (locked C02-04, PAY), not a tax-treatment clause"),
}

if __name__ == "__main__":
    pool, rows = run()

    print("=== KNOWN-ANSWER CHECK ===")
    ok = True
    print("  RECALL -- must be flagged:")
    for name, (needle, why) in RECALL.items():
        hit = [r for r in rows if needle.lower() in r[2].lower()]
        kinds = sorted({m[0] for r in hit for m in r[3]})
        good = bool(hit)
        if name == "C14-076-cand2":
            good = good and kinds == ["DISPOSITION:AMBIGUOUS"]
        ok &= good
        print(f"    {'ok ' if good else 'BAD'} {name:16} flagged={bool(hit)} classified_as={kinds or '[]'}")
        print(f"          {why}")
    print("  PRECISION -- must NOT be flagged (they are tax clauses, not tax-TREATMENT clauses):")
    for name, (needle, why) in PRECISION.items():
        hit = [r for r in rows if needle.lower() in r[2].lower()]
        good = not hit
        ok &= good
        print(f"    {'ok ' if good else 'BAD'} {name:16} flagged={bool(hit)}")
        print(f"          {why}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    print(f"\n=== POOL {len(pool)} segments | {len(rows)} tax-treatment sentences "
          f"in {len({r[0] for r in rows})} segments, {len({r[0].split('-')[0] for r in rows})} documents ===")
    byshape = collections.Counter(s for r in rows for s in r[1])
    for k, v in byshape.most_common():
        print(f"    {k:18} {v}")

    cls = [r for r in rows if r[3]]
    unc = [r for r in rows if not r[3]]
    print(f"\n=== ADJUDICATED: {len(cls)} of {len(rows)} sentences carry a classification ===")
    print("    (only these are PRECEDENT; an unannotated pool hit is just another instance)")
    for sid, shapes, sent, marks in sorted(cls):
        print(f"\n  {sid}  {shapes}")
        print(f"    {sent[:190]}")
        for k, w, _ in marks:
            print(f"      -> {k}  {w[:90]}")

    print(f"\n=== UNADJUDICATED: {len(unc)} sentences (printed in full: the class is "
          f"established by reading) ===")
    for sid, shapes, sent, _ in sorted(unc):
        print(f"  {sid:10} {'/'.join(shapes):28} {sent[:120]}")
