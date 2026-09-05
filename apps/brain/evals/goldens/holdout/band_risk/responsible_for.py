"""`be/remain responsible|liable for X` across the 1,547-segment pool, as a
POLARITY x COMPLEMENT grid -- the census behind §2 of C14_076_INVESTIGATION.md.

WHY THIS SHAPE. C14-076's first un-annotated sentence ("Each party will be solely
responsible for any and all taxes imposed thereon") had to be placed against the
project's four established dispositions of the same construction:

    C02-045  "shall be solely responsible for THE TIMELY PAYMENT of ... to X"  ANNOTATED (C02-04, PAY)
    C14-139  "shall remain fully responsible for THE PERFORMANCE of ..."       counted obligation-bearing
    C14-028  "shall be responsible for ORDERING ... and for ENSURING ..."      counted obligation-bearing
    C04-163  "shall NOT be responsible for PAYMENTS relating to ..."           EXCLUDED (§8.8 copular)

THE FIRST DRAFT OF THIS SCRIPT FAILED ITS OWN KNOWN-ANSWER CHECK, AND THE FAILURE IS THE
REASON THE INVESTIGATION REACHED ITS ANSWER. It classified complements as act-vs-thing and
predicted C04-163 would be an act; the run returned THING, because the ACT vocabulary held
`payment` and the text says `payments`. Reading the flagged case -- Standing Principle 7's
actual instruction -- showed C04-163's complement IS an act nominalisation and that it was
excluded on POLARITY, not on complement type. The complement-type-alone hypothesis was
falsified by its own detector's failure, not by re-reading the pattern. Hence a 2x2.

A second detector fault, also kept: `IN NO EVENT SHALL X BE LIABLE FOR` and
`the foregoing shall not require ... to be responsible for` are negatives whose negator is
not adjacent to the copula. Six were flagged for reading; four were genuine negatives
(C04-145, C04-146, C15-052, C22-030) and two were false flags whose negator governs a
different clause of the same sentence (C03-024, C11-070). The totals below carry that
correction and the sub-classification is stated as approximate in the note.
"""
import sys, re, pathlib, collections

BRAIN = pathlib.Path(__file__).resolve().parents[4]      # apps/brain
sys.path.insert(0, str(BRAIN))
import evals.corpus as corpus                            # noqa: E402

CORPUS = BRAIN.parents[1] / ".corpus"

RESP = re.compile(
    r"(?P<neg>\bnot\s+)?\b(?:be|been|being|remain|remains|remained|is|are)\s+"
    r"(?:(?:solely|fully|wholly|entirely|primarily|jointly|severally|exclusively|"
    r"at\s+all\s+times|alone)\s+)*(?:responsible|liable)\s+for\b", re.I)

# a negator governing the copula from further left in the sentence
FARNEG = re.compile(r"\b(?:in\s+no\s+event|under\s+no\s+circumstances|shall\s+not|"
                    r"will\s+not|neither|nor\s+shall|not\s+require)\b", re.I)
# the two sentences where FARNEG fires on a DIFFERENT clause -- adjudicated by reading
FARNEG_FALSE_POSITIVES = {"C03-024", "C11-070"}

DET = (r"(?:(?:the|any|all|its|their|such|each|every|own|and|or|timely|prompt|proper|"
       r"full|due|complete|respective)\s+)*")
ACT_NOM = re.compile(
    rf"^\s*{DET}(?:[a-z]+ing\b|(?:payment|performance|delivery|compliance|provision|"
    r"maintenance|execution|procurement|reimbursement|filing|removal|repair|supply|"
    r"conduct|management|administration|installation|inspection|collection|remittance|"
    r"disposal|observance|discharge|submission|transportation|handling|training|"
    r"supervision)s?\b)", re.I)
BARE_BURDEN = re.compile(
    rf"^\s*{DET}(?:cost|expense|tax|fee|charge|amount|sum|duty|duties|tariff|surcharge|"
    r"vat|damage|loss|liabilit|price)", re.I)


def run():
    pool = corpus.build_pool(CORPUS, corpus.load_manifest())
    buckets = collections.defaultdict(list)
    for seg in pool:
        for sent in corpus.split_sentences(seg["text"]):
            for m in RESP.finditer(sent):
                tail = re.sub(r"\s+", " ", sent[m.end():]).strip()
                negated = bool(m.group("neg")) or (
                    FARNEG.search(sent[:m.start()])
                    and seg["segment_id"] not in FARNEG_FALSE_POSITIVES)
                key = ("NEGATIVE" if negated else
                       "ACT_NOM" if ACT_NOM.match(tail) else
                       "BARE_BURDEN" if BARE_BURDEN.match(tail) else "OTHER")
                buckets[key].append((seg["segment_id"], tail))
    return pool, buckets


KNOWN = {
    "C02-045": ("ACT_NOM",     "ANNOTATED as C02-04, action PAY"),
    "C14-139": ("ACT_NOM",     "counted obligation-bearing, band count clause (4)"),
    "C14-028": ("ACT_NOM",     "counted obligation-bearing, band count clause (5)"),
    "C04-163": ("NEGATIVE",    "EXCLUDED, §8.8 copular exemption, clause (2)"),
    "C14-076": ("BARE_BURDEN", "THE CASE IN QUESTION -- no disposition on record"),
}

if __name__ == "__main__":
    pool, buckets = run()
    print("=== KNOWN-ANSWER CHECK: five cases whose disposition is already on record ===")
    ok = True
    for seg_id, (want, why) in KNOWN.items():
        got = [k for k, v in buckets.items() if any(r[0] == seg_id for r in v)]
        good = want in got
        ok &= good
        print(f"  {'ok ' if good else 'BAD'} {seg_id}: {got} (want {want})\n"
              f"        established disposition: {why}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    total = sum(len(v) for v in buckets.values())
    segs = len({r[0] for v in buckets.values() for r in v})
    print(f"\n=== TOTALS: {total} sentences over {segs}/{len(pool)} pool segments "
          f"({100*segs/len(pool):.1f}%) ===")
    for k in ("ACT_NOM", "BARE_BURDEN", "OTHER", "NEGATIVE"):
        print(f"  {k:12} {len(buckets[k]):>4}")

    bb = sorted(buckets["BARE_BURDEN"])
    docs = sorted({s.split("-")[0] for s, _ in bb})
    print(f"\n=== BARE_BURDEN -- candidate 1's cell: {len(bb)} instances, "
          f"{len(docs)} documents {docs} ===")
    print("    Every one printed in full: this cell has NO adjudicated precedent, so the")
    print("    class is established by reading it, not by trusting the count.")
    for seg_id, tail in bb:
        print(f"  {seg_id:10} {tail[:74]!r}")
