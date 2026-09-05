"""Clause 8 on a partyless span is STRUCTURALLY guaranteed to pass -- the proof
behind §8.4 of C14_076_INVESTIGATION.md, and the evidence for §10.1 F15.

THE ARGUMENT, and it is a proof rather than a rate.
  1. ground_candidates() requires obligor_alias/obligee_alias to be a substring of
     the grounded span (extraction._is_grounded_substring).
  2. symbols.resolve_party() matches only a registered canonical_name (case-
     INsensitively) or a registered alias (case-SENSITIVELY, §21 R2).
  3. So if NO registry party name occurs anywhere in the span, no grounded alias
     can resolve, whatever the model emits.
  4. typecheck._resolve_party() then appends BOTH roles to missing_fields, and
     underspecified = bool(missing_fields) is True unconditionally.
  5. Gold says True (§3.9 trigger 1). Clause 8 passes for ANY prediction --
     including a wholly wrong one.

Steps 1-4 are code facts. What this script establishes is step 3's antecedent for
the spans that matter, against the REAL registries.

THE SECOND MEASUREMENT. §5 excludes missing_fields from the predicate ("reported
but excluded") while scoring underspecified, which §3.9 states IS
bool(missing_fields). If that is a real tension rather than a formality it should
show up as clause 8 being a function of clauses 3/4/6's inputs across the locked
set, not an independent eighth check. Measured below.
"""
import sys, re, json, glob, pathlib, collections

HERE = pathlib.Path(__file__).resolve()
BRAIN = HERE.parents[4]                                   # apps/brain
REGISTRY = BRAIN / "evals/registry"

CAND2 = ("Israel value added tax shall be added, if applicable, to all amounts "
         "payable hereunder and will be paid against submission of appropriate "
         "tax invoices.")

# KNOWN-ANSWER CHECK. A detector that only ever answers "no party here" would
# "prove" the claim for every span. It is pinned against a span that DOES name
# registered parties -- C04-03's, which names both Bellicum and Miltenyi.
KA_ITEM, KA_DOC, KA_EXPECT = "C04-03", "C04", {"Bellicum", "Miltenyi"}


def parties_in(span, doc):
    """resolve_party()'s own strictness: canonical_name case-INsensitive,
    aliases case-SENSITIVE (§21 R2's trap, which F2 already caught once)."""
    path = REGISTRY / f"{doc}.json"
    if not path.exists():
        return None                                        # unfalsifiable, not "none"
    hits = []
    for party in json.load(open(path))["parties"]:
        if re.search(r"\b" + re.escape(party["canonical_name"]) + r"\b", span, re.I):
            hits.append(party["canonical_name"])
        for a in party["aliases"]:
            if re.search(r"\b" + re.escape(a) + r"\b", span):
                hits.append(a)
    return sorted(set(hits))


def resolves(alias, doc):
    """Does this gold alias resolve under resolve_party()? None means the document
    has no committed registry, so the question is unfalsifiable and the item is
    skipped rather than counted as a non-resolution."""
    if alias == "ABSENT":
        return False
    path = REGISTRY / f"{doc}.json"
    if not path.exists():
        return None
    for party in json.load(open(path))["parties"]:
        if alias.lower() == party["canonical_name"].lower():
            return True
        if alias in party["aliases"]:                      # §21 R2: case-SENSITIVE
            return True
    return False


def locked_items():
    out = []
    for p in sorted(glob.glob(str(BRAIN / "evals/goldens/batch*/items/*.json"))):
        d = json.load(open(p))
        d["doc"] = d["segment_id"].split("-")[0]
        out.append(d)
    return out


if __name__ == "__main__":
    items = locked_items()
    by_id = {d["item_id"]: d for d in items}

    print("=== KNOWN-ANSWER CHECK ===")
    ka = parties_in(by_id[KA_ITEM]["span_text"], KA_DOC)
    ok = ka is not None and KA_EXPECT.issubset(set(ka))
    print(f"  {'ok  ' if ok else 'BAD '} {KA_ITEM}'s span names registered parties "
          f"{KA_EXPECT} -> detector found {ka}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - results withheld'}")
    if not ok:
        sys.exit(1)

    print("\n=== C14-076 candidate 2, against the real C14 registry ===")
    hits = parties_in(CAND2, "C14")
    print(f"  registry hits: {hits if hits else 'NONE'}")
    if hits:
        print("  => step 3's antecedent FAILS; the guarantee does not hold here")
        sys.exit(1)
    print("  => no grounded alias can resolve")
    print("  => underspecified = True unconditionally")
    print("  => CLAUSE 8 PASSES FOR ANY PREDICTION. Guaranteed, not merely likely.")

    print("\n=== is clause 8 independent of clauses 3/4/6 across the locked set? ===")
    u = collections.Counter(d["underspecified"] for d in items)
    print(f"  gold underspecified: True {u[True]}/{len(items)}, False {u[False]}/{len(items)}")
    print("  predicate tested: underspecified == NOT(obligor RESOLVES and obligee")
    print("  RESOLVES and temporal is null). Resolvability, not ABSENT-ness -- §3.9")
    print("  trigger 1 also catches collective, distributive and relational references")
    print("  and any alias absent from the registry. resolve_date()/resolve_trigger()")
    print("  return None unconditionally in v1, so ANY temporal makes it True.")
    print("  (A FIRST DRAFT OF THIS SCRIPT TESTED ABSENT-ness and reported 4")
    print("   mismatches -- C14-01, C14-02, C02-04, C06-01, every one a named but")
    print("   unresolvable party. The looser predicate was the defect, not the data.)")
    mismatch = []
    for d in items:
        both = [resolves(d["obligor"], d["doc"]), resolves(d["obligee"], d["doc"])]
        if None in both:
            continue                                       # no registry -> unfalsifiable
        pred = not (all(both) and d.get("temporal") is None)
        if pred != d["underspecified"]:
            mismatch.append(d)
    skipped = [d for d in items
               if None in (resolves(d["obligor"], d["doc"]),
                           resolves(d["obligee"], d["doc"]))]
    print(f"\n  items checked: {len(items) - len(skipped)} "
          f"({len(skipped)} skipped -- no committed registry for their document)")
    print(f"  items where `underspecified` is NOT predicted by resolvability: "
          f"{len(mismatch)}")
    for d in mismatch:
        print(f"    {d['item_id']}: underspecified={d['underspecified']} "
              f"obligor={d['obligor']!r} obligee={d['obligee']!r} "
              f"temporal={d.get('temporal')}")
    if not mismatch:
        print("    (none -- clause 8 is a FUNCTION of clauses 3/4/6's inputs, not an")
        print("     independent eighth check. This is the §5 tension F15 records:")
        print("     §5 excludes missing_fields from the predicate while scoring")
        print("     underspecified, which §3.9 states IS bool(missing_fields).)")

    print("\n=== how many scored slots already match on ABSENT/null? ===")
    def absent_slots(d):
        return ((d["obligor"] == "ABSENT") + (d["obligee"] == "ABSENT")
                + (d.get("temporal") is None))
    c = collections.Counter(absent_slots(d) for d in items)
    for k in sorted(c):
        print(f"  {k} absence-matched slot(s) (clauses 3/4/6): {c[k]} items")
    tnull = sum(1 for d in items if d.get("temporal") is None)
    print(f"\n  gold temporal is null on {tnull}/{len(items)} = {tnull/len(items):.1%}")
    print(f"  items with >=2 absence-matched slots: {sum(v for k, v in c.items() if k >= 2)}")
    print("  => a both-ABSENT item would NOT be the first item where two scored")
    print("     clauses match on absence. It would be the first where two PARTY")
    print("     clauses do -- a smaller and different claim.")
