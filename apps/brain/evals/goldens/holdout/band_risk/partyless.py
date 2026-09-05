"""Fully PARTYLESS modal sentences -- the census behind §3 of C14_076_INVESTIGATION.md.

C14-076's second un-annotated sentence ("Israel value added tax shall be added, if
applicable, to all amounts payable hereunder and will be paid against submission of
appropriate tax invoices") names NO party at all, so §3.5.3 would give it obligor =
ABSENT and obligee = ABSENT. §3.5.3's rule text anticipates exactly this ("Where no party
is named at all ... obligee = ABSENT"), but none of its worked cases reaches it and NO
locked gold item has both slots ABSENT -- so the question is how often the shape recurs.

SCOPE RESTRICTION, STATED RATHER THAN PAPERED OVER. Only the 10 documents carrying a
committed §21 R3 party registry are measured. The other 18 have no authored alias list,
so a "partyless" verdict there would be unfalsifiable -- the detector could not tell a
genuinely partyless sentence from one naming a party it had never been told about.
"""
import sys, re, json, glob, pathlib, collections

BRAIN = pathlib.Path(__file__).resolve().parents[4]      # apps/brain
sys.path.insert(0, str(BRAIN))
import evals.corpus as corpus                            # noqa: E402

CORPUS = BRAIN.parents[1] / ".corpus"

GENERIC = re.compile(r"\b(?:part(?:y|ies)|purchaser|supplier|vendor|customer|client|"
                     r"contractor|licensee|licensor|seller|buyer|franchisee|franchisor|"
                     r"distributor|recipient|provider|company|manufacturer)\b", re.I)
MODAL = re.compile(r"\b(?:shall|must|will|may|should)\b", re.I)
PASSIVE = re.compile(r"\b(?:shall|will|must|may)\s+(?:not\s+)?be\s+([a-z]+ed|[a-z]+n)\b", re.I)

# copular/status participles: `shall be deemed`, `shall be entitled` etc. are §8.8's
# "not an obligation clause at all" class, NOT §3.5.3 agentless performance passives.
STATUS = {"deemed", "entitled", "liable", "responsible", "construed", "governed",
          "binding", "effective", "valid", "void", "unenforceable", "invalid", "illegal",
          "subject", "interpreted", "required", "permitted", "allowed", "limited",
          "excluded", "included", "understood", "final", "conclusive", "cumulative",
          "null", "superseded", "amended"}
# contract-artifact subjects (severability, survival, headings, definitions)
ARTIFACT = re.compile(r"^\s*(?:\(?[ivxa-z0-9]{1,4}\)\s*)?(?:capitalized\s+terms|the\s+)?"
                      r"(?:section|article|provision|agreement|notice|heading|term|clause|"
                      r"paragraph|exhibit|schedule|appendix|amendment|waiver|remedy)\b", re.I)


def run():
    reg = {}
    for p in sorted(glob.glob(str(BRAIN / "evals/registry/*.json"))):
        d = json.load(open(p))
        reg[d["doc_id"]] = {t for party in d["parties"]
                            for t in [party["canonical_name"], *party["aliases"]]}
    pool = corpus.build_pool(CORPUS, corpus.load_manifest())
    hits, examined = [], 0
    for seg in pool:
        if seg["doc_id"] not in reg:
            continue
        for sent in corpus.split_sentences(seg["text"]):
            if not MODAL.search(sent):
                continue
            examined += 1
            if GENERIC.search(sent):
                continue
            if any(re.search(rf"\b{re.escape(t)}\b", sent) for t in reg[seg["doc_id"]]):
                continue
            hits.append({"seg": seg["segment_id"], "doc": seg["doc_id"],
                         "sent": re.sub(r"\s+", " ", sent).strip()})
    narrow = []
    for h in hits:
        if ARTIFACT.match(h["sent"]):
            continue
        verbs = [m.group(1).lower() for m in PASSIVE.finditer(h["sent"])
                 if m.group(1).lower() not in STATUS]
        if verbs:
            narrow.append({**h, "verbs": verbs})
    return reg, pool, examined, hits, narrow


CAND2 = "israel value added tax shall be added"
# locked §3.5.3 agentless-passive items that DO name a party -> must NOT be flagged
NAMED = {"C04-087": "each quantity of miltenyi product(s) ordered by bellicum",
         "C14-044": "all such rescheduling shall be performed by sending contractor"}

if __name__ == "__main__":
    reg, pool, examined, hits, narrow = run()
    print("registries:", ", ".join(f"{k}({len(v)})" for k, v in sorted(reg.items())))
    print("\n=== KNOWN-ANSWER CHECK ===")
    ok = True
    for label, coll in (("broad", hits), ("narrowed", narrow)):
        got = any(CAND2 in h["sent"].lower() for h in coll)
        ok &= got
        print(f"  {'ok ' if got else 'MISS'} candidate 2 flagged partyless ({label}): {got}")
    for seg_id, frag in NAMED.items():
        bad = [h for h in hits if frag[:40] in h["sent"].lower()]
        ok &= not bad
        print(f"  {'ok ' if not bad else 'BAD'} {seg_id} names a party, NOT flagged: {not bad}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    print(f"\n=== TOTALS over the {len(reg)} registry-backed documents ===")
    print(f"  modal-bearing sentences examined      : {examined}")
    print(f"  fully partyless                       : {len(hits)} "
          f"({100*len(hits)/examined:.1f}%), {len({h['seg'] for h in hits})} segments")
    print(f"  ... of which agentless PERFORMANCE     : {len(narrow)} "
          f"({100*len(narrow)/examined:.1f}% of modal sentences), "
          f"{len({n['seg'] for n in narrow})} segments")
    print("  by document (narrowed):",
          dict(sorted(collections.Counter(n["doc"] for n in narrow).items())))
    print("\n=== the narrowed class in full -- read it, do not trust the count ===")
    print("    (residual noise is visible and left visible: 'non-binding'/'shall be in")
    print("     addition' surface as participles and are not performance passives)")
    for n in sorted(narrow, key=lambda n: n["seg"]):
        print(f"  {n['seg']:10} {str(n['verbs']):24} {n['sent'][:88]!r}")
