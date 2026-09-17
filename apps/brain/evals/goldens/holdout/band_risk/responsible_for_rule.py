"""The COMPLEMENT axis of `be/remain responsible|liable for X` -- the drafting evidence
behind guideline §8.8.4, and the successor to `responsible_for.py`'s 2x2 census.

WHY A SECOND SCRIPT RATHER THAN AN EDIT. `responsible_for.py` answered the question
C14_076_INVESTIGATION.md §2 actually asked -- "does the affirmative + bare-burden cell have
an adjudicated precedent?" -- and its answer (no; 15 instances, 9 documents) stands and is
reproduced here unchanged. It is left untouched because its known-answer block is a dated
record of what was checked then. THIS script answers the different question the §10
amendment needs: what is the rule, and does it decide `C03-024`?

THE FINDING THAT FORCED A DIFFERENT SHAPE. `C03-024` -- the edge case the drafting
instruction named -- IS NOT IN THE BARE_BURDEN CELL AT ALL. Its complement is
"such Affiliate's failure to satisfy its obligations hereunder": no cost word, no act
nominalisation, so `responsible_for.py` files it in OTHER. The starting-point rule recorded
in C14_076_INVESTIGATION.md §2.4 ("act-nominalisation -> obligation-bearing, bare-burden ->
§8.8 status class") is therefore not merely untested against `C03-024`, it is STRUCTURALLY
UNABLE TO CLASSIFY IT. Drafting against `C14-076` alone would have shipped a binary with a
hole exactly where the instruction said to look.

THE AXIS THAT DOES CLASSIFY IT is the head noun of the complement, read against §8.8.1's
own removal test (does the clause command CONDUCT, or assert a STATUS?):

    RENDER  -- the complement names a performance the obligor must render or procure
               ("the payment of X to Y", "the performance of all obligations", "ordering")
    ABSORB  -- the complement names a burden the obligor must absorb: a cost, tax, expense,
               loss, damage, liability, or ANOTHER PERSON'S breach or failure

`C03-024` ("...failure...") is ABSORB. `C03-016` ("...any and all obligations of any such
Affiliate...") is RENDER. Same document, same obligor (AT&T Mobility LLC), same
Affiliate-accountability subject -- and the drafter chose different complements. That pair,
not `C14-076`, is what the rule is drafted against.

TWO DETECTOR FAULTS FOUND BY KNOWN-ANSWER CHECKS AND KEPT (Standing Principle 7).

  (1) The first head extractor took "the first token that is not a determiner or adjective",
      which requires an adjective list that is complete -- it is not, and the failures were
      silent: "all regulatory activities" returned `regulatory`, "the direct, personal
      supervision" returned `personal`, "all supplementary costs" returned `supplementary`.
      Fifteen affirmative instances came back UNCLASSIFIED with an adjective as the head.
      Replaced by a left-to-right scan for the first token in EITHER vocabulary, which needs
      no adjective list to be complete.

  (2) That scan then introduced its own fault, and it is the more instructive one: `-ing`
      is in the RENDER vocabulary as the gerund test, so "all travel and LIVING expenses"
      (`C11-041`) classified RENDER on an ADJECTIVE. The true head is `expenses` -> ABSORB.
      A gerund test cannot distinguish a deverbal adjective from an act nominalisation by
      shape alone; `ADJ_ING` is the explicit, enumerated correction and is stated as a known
      limitation rather than presented as general.

WHAT THIS SCRIPT DOES NOT DECIDE. Polarity (§8.8.1), non-party subject (§3.5) and
non-main-predicate embedding are PRIOR filters that apply before the complement is reached;
they are reported separately, not folded into the RENDER/ABSORB counts. Two are carried as
established known answers rather than re-detected: `C04-163` (negative) and `E07-010`
(non-party subject, excluded under §3.5 -- an ORTHOGONAL ground, so it neither confirms nor
falsifies anything about its complement), plus `C04-117`, whose "which Party(ies) is/are
responsible for payment" sits INSIDE locked item `C04-02`'s span as the CONTENT OF A
NEGOTIATION, not as an undertaking.

Run: python evals/goldens/holdout/band_risk/responsible_for_rule.py
"""
import sys, re, pathlib, collections

BRAIN = pathlib.Path(__file__).resolve().parents[4]          # apps/brain
sys.path.insert(0, str(BRAIN))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import evals.corpus as corpus                                # noqa: E402
import responsible_for as rf                                 # noqa: E402

CORPUS = BRAIN.parents[1] / ".corpus"
GOLD = BRAIN / "evals" / "goldens"

# Deverbal ADJECTIVES that end in -ing. The gerund limb of RENDER cannot tell these from an
# act nominalisation by shape, so they are enumerated. Found by fault (2) above.
ADJ_ING = re.compile(r"^(?:living|outstanding|remaining|existing|following|foregoing|"
                     r"operating|resulting|arising|relating|including|pending|leading|"
                     r"willing|ongoing|underlying)$", re.I)

ABSORB = re.compile(
    r"^(?:cost|costs|expense|expenses|tax|taxes|taxation|fee|fees|charge|charges|"
    r"tariff|tariffs|surcharge|surcharges|vat|amount|amounts|sum|sums|price|prices|"
    r"loss|losses|damage|damages|liability|liabilities|deficiency|deficiencies|"
    r"penalty|penalties|value|"
    r"breach|breaches|failure|failures|default|defaults|negligence|misconduct|"
    r"act|acts|omission|omissions|claim|claims|delay|delays|error|errors)$", re.I)

RENDER = re.compile(
    r"^(?:\w+ing|payment|payments|performance|delivery|deliveries|compliance|"
    r"provision|provisions|maintenance|execution|procurement|reimbursement|filing|filings|"
    r"removal|repair|repairs|supply|conduct|management|administration|installation|"
    r"inspection|inspections|collection|remittance|disposal|observance|discharge|"
    r"submission|submissions|transportation|handling|training|supervision|deployment|"
    r"development|approval|approvals|resolution|fulfilment|fulfillment|validation|"
    r"obligation|obligations|duty|duties|matter|matters|logistics|content|activity|"
    r"activities|work|works|service|services|resource|resources|return|shipment|"
    r"arrangement|arrangements|coverage)$", re.I)


def head(tail):
    """First token of the complement in either vocabulary -> (token, class).

    Left-to-right scan rather than skip-the-adjectives: see fault (1). A head noun precedes
    its own post-modifiers, so the first vocabulary hit is the head -- "the payment of all
    COSTS" is RENDER on `payment`, "such Affiliate's FAILURE to satisfy its OBLIGATIONS" is
    ABSORB on `failure`, both correctly and for the same reason.
    """
    for t in re.findall(r"[A-Za-z][\w\-'’]*", tail):
        if ADJ_ING.match(t):
            continue
        if ABSORB.match(t):
            return t, "ABSORB"
        if RENDER.match(t):
            return t, "RENDER"
    return "", "UNCLASSIFIED"


# Every case whose disposition is already on record, both sides of the line, plus the edge
# case. A rule that cannot reproduce these is not a clarification of existing practice.
KNOWN = {
    "C02-045": ("payment",     "RENDER", "AFFIRM", "ANNOTATED as C02-04, action PAY"),
    "C14-139": ("performance", "RENDER", "AFFIRM", "counted obligation-bearing, band clause (4)"),
    "C14-028": ("ordering",    "RENDER", "AFFIRM", "counted obligation-bearing, band clause (5)"),
    "C03-016": ("obligations", "RENDER", "AFFIRM", "the C03-024 contrast pair -- same document"),
    "E01-024": ("obligations", "RENDER", "AFFIRM", "accrued obligations survive termination"),
    "C14-076": ("taxes",       "ABSORB", "AFFIRM", "candidate 1 -- the case that raised the question"),
    "C03-024": ("failure",     "ABSORB", "AFFIRM", "THE EDGE CASE the drafting instruction named"),
    "C14-118": ("loss",        "ABSORB", "AFFIRM", "liable for loss of/damage to components"),
    "C04-151": ("breach",      "ABSORB", "AFFIRM", "responsible for a THIRD PARTY's breach"),
    "C11-041": ("expenses",    "ABSORB", "AFFIRM", "the ADJ_ING regression -- 'travel and LIVING expenses'"),
    # THE TWO-AXIS PROOF, and the check that caught a mis-specified expectation of my own:
    # C04-163's complement is an act nominalisation, so the COMPLEMENT axis says RENDER --
    # yet the clause is EXCLUDED, because the PRIOR polarity filter removes it first. The
    # first version of this block asserted RENDER on the affirmative axis and FAILED, which
    # is the detector correctly refusing to let one axis answer for the other.
    "C04-163": ("payments",    "RENDER", "NEGATIVE",
                "EXCLUDED on POLARITY (§8.8.1); its complement would read RENDER"),
}

AFFIRMATIVE_CELLS = ("ACT_NOM", "BARE_BURDEN", "OTHER")   # NEGATIVE = prior polarity filter

# EVERY instance where READING overrides the head-noun proxy, each with its reason. This
# table is the proxy's measured error rate, stated rather than absorbed: 4 of 99 affirmative
# sentences, 4.0%. It exists because §8.8.4's rule is "read the complement", and the proxy is
# a census aid -- so where the two disagree, the reading is recorded and the proxy is not
# quietly patched to agree with it. Keyed by (segment, head the proxy returned).
READING_OVERRIDES = {
    ("C05-057", "expense"): ("RENDER",
        "COORDINATED PREDICATE, not the complement. 'Biocept shall be responsible for AND "
        "BEAR THE EXPENSE OF any filing, prosecution, maintenance and enforcement' -- the "
        "proxy took `expense` from the second verb phrase. The shared complement is 'any "
        "filing, prosecution, maintenance and enforcement' = RENDER. Sole instance: a scan "
        "for `responsible|liable for and <verb>` over the pool returns exactly this one."),
    ("C15-052", "DAMAGES"): ("POLARITY_MISSED",
        "SUBJECT NEGATION. 'NO PARTY SHALL BE LIABLE FOR ...' is a limitation-of-liability "
        "disclaimer, so §8.8.1's prior polarity filter should remove it -- but "
        "responsible_for.py's FARNEG has no subject-negation limb (it tests `shall not`, "
        "`neither`, `in no event`, not `no <noun> shall`). Sole instance pool-wide. It never "
        "reaches the complement axis and is NOT counted in ABSORB."),
    ("C11-070", "act"): ("EMBEDDED",
        "NOT A MAIN PREDICATE: '...nor upon A CLAIM THAT BKC is responsible for Franchisee's "
        "act or omissions'. This is the content of a hypothetical claim being disclaimed. "
        "Right answer for the wrong reason if counted as ABSORB -- it is excluded one filter "
        "earlier. C11-070's OTHER match (the 'all losses or damages' sentence) is a genuine "
        "affirmative ABSORB and is unaffected."),
    # Head is "" -- `determination(s)` is deliberately in NEITHER vocabulary. Putting it in
    # RENDER (where an earlier draft had it) made the proxy assert an answer it cannot have.
    ("C03-107", ""): ("ESCALATE",
        "GENUINELY UNDECIDED BY THE PROXY, and recorded as such rather than forced. 'AT&T "
        "shall be responsible for such determinations' -- the determinations are ALREADY MADE "
        "earlier in the same sentence ('AT&T shall notify Vendor in writing of such "
        "determinations'), so `responsible for` here means answerable for their correctness "
        "(ABSORB), not a duty to make them (RENDER). A nominalisation of a COMPLETED act of "
        "the obligor's own is a third shape the head noun cannot see. §8.8.4 names it as an "
        "escalation trigger rather than pretending the vocabulary resolves it."),
}


def classify_all():
    """Head-classify EVERY cell, tag the polarity side, then apply the reading overrides."""
    pool, buckets = rf.run()
    rows = []
    for cell, v in buckets.items():
        side = "NEGATIVE" if cell == "NEGATIVE" else "AFFIRM"
        for seg, tail in v:
            h, c = head(tail)
            override = READING_OVERRIDES.get((seg, h))
            rows.append((seg, cell, side, c, h, tail, override[0] if override else None))
    return pool, buckets, rows


def locked_segments():
    import json
    out = {}
    for b in ("batch01", "batch02", "batch03"):
        for f in sorted((GOLD / b / "segments").glob("*.json")):
            out[f.stem] = json.loads(f.read_text())
    return out


if __name__ == "__main__":
    pool, buckets, rows = classify_all()

    print("=== KNOWN-ANSWER CHECK: 11 cases, both sides of the line, plus the edge case ===")
    ok = True
    for seg, (wh, wc, ws, why) in sorted(KNOWN.items()):
        got = [(h, c, s) for sg, _, s, c, h, _, _ in rows if sg == seg]
        good = (wh, wc, ws) in got
        ok &= good
        print(f"  {'ok ' if good else 'BAD'} {seg:9} want head={wh!r} class={wc} side={ws}")
        print(f"        got={got}")
        print(f"        {why}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    print(f"\n=== POOL: {len(pool)} segments (rebuild reproduces 1,547 = the pool's own gate) ===")
    print(f"=== CONSTRUCTION: {sum(len(v) for v in buckets.values())} sentences, "
          f"{len({r[0] for v in buckets.values() for r in v})} segments ===")
    print(f"    prior polarity filter (§8.8.1) removes the NEGATIVE cell: "
          f"{len(buckets['NEGATIVE'])} sentences")

    raw, final = collections.defaultdict(list), collections.defaultdict(list)
    for seg, cell, side, c, h, tail, ov in rows:
        if side != "AFFIRM":
            continue
        raw[c].append((seg, h, tail))
        final[ov or c].append((seg, h, tail))
    naff = sum(len(v) for v in raw.values())

    print(f"\n=== COMPLEMENT AXIS over the {naff} affirmative sentences ===")
    print(f"    RAW head-noun proxy, before reading: "
          + ", ".join(f"{c}={len(raw[c])}" for c in ("RENDER", "ABSORB", "UNCLASSIFIED")))
    print(f"    READING OVERRIDES applied: {len(READING_OVERRIDES)} of {naff} "
          f"= {100*len(READING_OVERRIDES)/naff:.1f}% proxy error rate")
    for k, (to, why) in sorted(READING_OVERRIDES.items()):
        print(f"      {k[0]} (proxy head {k[1]!r}) -> {to}\n        {why[:96]}...")

    print("\n    AFTER READING:")
    for c in ("RENDER", "ABSORB", "ESCALATE", "EMBEDDED", "POLARITY_MISSED", "UNCLASSIFIED"):
        docs = sorted({s.split("-")[0] for s, _, _ in final[c]})
        print(f"      {c:16} {len(final[c]):>3} sentences, {len(docs):>2} documents {docs}")

    for c in ("RENDER", "ABSORB", "ESCALATE", "EMBEDDED", "POLARITY_MISSED", "UNCLASSIFIED"):
        if not final[c]:
            continue
        print(f"\n{'='*97}\n{c} -- every instance printed: the class is established by "
              f"reading, not by trusting the count\n{'='*97}")
        for seg, h, tail in sorted(final[c]):
            print(f"  {seg:10} {h:15} {tail[:70]!r}")

    locked = locked_segments()
    print(f"\n{'='*97}\nEXPOSURE AGAINST THE {len(locked)} LOCKED GOLD SEGMENTS\n"
          f"(the retroactivity cost of §8.8.4 under §10.2)\n{'='*97}")
    for c in ("RENDER", "ABSORB", "ESCALATE", "EMBEDDED", "POLARITY_MISSED", "UNCLASSIFIED"):
        print(f"  {c:16} {sorted({s for s, _, _ in final[c] if s in locked})}")
    print(f"  {'NEGATIVE':16} {sorted({s for s, _ in buckets['NEGATIVE'] if s in locked})}")
