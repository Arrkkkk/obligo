"""Empty-alias emission census over the 35 gold cassettes -- the measurement behind
§8.2 of C14_076_INVESTIGATION.md.

THE QUESTION. §5 encodes "this party is absent" as an UnresolvedParty carrying an
empty alias (score.py's ABSENT branch requires `norm(pred.alias) == ""`). So a
gold `ABSENT` slot is scoreable only if the model actually emits `""`. Whether it
ever does is a fact about `openai/gpt-oss-120b` under prompt v3, not something
readable off the predicate.

WHAT IT MEASURES. Every candidate in every recorded gold cassette, split by which
alias slot came back empty. It counts EMITTED candidates, before grounding and
before the pipeline -- deliberately, because the question is what the model
produces, not what survives.

WHY THE ASYMMETRY MATTERS. prompts/extraction/v3.yaml states no rule permitting an
empty alias anywhere. Its only signal is one worked example carrying
`"obligee_alias": ""`, with no obligor counterpart. §3.5 already called this
"undesigned behavior, not a chosen rule"; this census is what shows the undesign
is ONE-SIDED.
"""
import sys, json, glob, pathlib, collections, math

HERE = pathlib.Path(__file__).resolve()
BRAIN = HERE.parents[4]                                   # apps/brain
CASSETTES = BRAIN / "evals/cassettes/gold"

# KNOWN-ANSWER CHECK. C02-021 run1 was read by hand during the investigation:
# four candidates, in this order, obligor never empty and obligee empty on the
# first two. A census that cannot reproduce a cassette read by eye is measuring
# something other than what it claims to (Standing Principle 7).
KA_SEG, KA_RUN = "C02-021", 1
KA_EXPECTED = [
    ("Antares or its Subcontractor", ""),
    ("Antares", ""),
    ("All such samples", "AMAG"),
    ("AMAG", "Antares"),
]


def norm(s):
    return " ".join((s or "").split()).strip()


def run():
    rows = []
    for path in sorted(glob.glob(str(CASSETTES / "*/run*.json"))):
        d = json.load(open(path))
        for r in d["responses"]:
            if r.get("status_code") != 200:
                continue
            try:
                obs = json.loads(
                    r["json"]["choices"][0]["message"]["content"])["obligations"]
            except Exception:
                continue
            for o in obs:
                rows.append(dict(seg=d["segment_id"], run=d["run"],
                                 obr=norm(o.get("obligor_alias")),
                                 obe=norm(o.get("obligee_alias")),
                                 span=o.get("span_text", "")))
    return rows


def wilson_upper(k, n, z=1.96):
    """Upper 95% bound on a rate. Reported for the obligor slot because the point
    estimate there is 0 and "0%" alone overstates the certainty of a bounded
    sample -- the honest statement is a ceiling, not a zero."""
    if n == 0:
        return 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + r) / d


if __name__ == "__main__":
    rows = run()

    print("=== KNOWN-ANSWER CHECK ===")
    ka = [(r["obr"], r["obe"]) for r in rows if r["seg"] == KA_SEG and r["run"] == KA_RUN]
    ok = ka == KA_EXPECTED
    print(f"  {'ok  ' if ok else 'BAD '} {KA_SEG} run{KA_RUN} reproduces the "
          f"hand-read candidate list ({len(ka)} candidates)")
    if not ok:
        print(f"       expected {KA_EXPECTED}")
        print(f"       got      {ka}")
    print(f"\nDETECTOR VERDICT: {'PASSED' if ok else 'FAILED - totals withheld'}")
    if not ok:
        sys.exit(1)

    n = len(rows)
    cassettes = len({(r["seg"], r["run"]) for r in rows})
    obr = sum(1 for r in rows if r["obr"] == "")
    obe = sum(1 for r in rows if r["obe"] == "")
    both = sum(1 for r in rows if r["obr"] == "" and r["obe"] == "")

    print(f"\n=== TOTALS over {n} emitted candidates in {cassettes} cassettes ===")
    print(f"  obligor_alias empty : {obr}/{n} = {obr/n:.1%}   "
          f"(Wilson-95 upper {wilson_upper(obr, n):.2%})")
    print(f"  obligee_alias empty : {obe}/{n} = {obe/n:.1%}")
    print(f"  BOTH empty          : {both}/{n} = {both/n:.1%}")
    print("\n  The obligee figure is the prompt's one worked example being followed.")
    print("  The obligor figure is the absence of a counterpart example. §5's ABSENT")
    print("  branch is reachable for one slot and, on this evidence, not the other.")

    print("\n=== every candidate with an EMPTY obligor_alias (read it, do not "
          "trust the count) ===")
    hits = [r for r in rows if r["obr"] == ""]
    if not hits:
        print("  (none -- the list is empty, which IS the finding)")
    for r in hits:
        print(f"  {r['seg']} run{r['run']}: obligee={r['obe']!r} | {r['span'][:70]!r}")
