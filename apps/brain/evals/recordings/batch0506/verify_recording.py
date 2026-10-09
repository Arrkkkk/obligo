"""Post-recording verification: Cassette.verify() per ITEM, one scoring run,
per-item outcome against the committed pre-registration.

Run AFTER the sessions, BEFORE any commit (reviewer instruction 2026-10-09).

Three things it does, in order:

1. **`Cassette.verify()` FOR EVERY (segment, run), AGAINST EACH ITEM'S OWN
   `guideline_version`** -- which is F16's per-item mechanism, not a single
   run-level version. `E02-006` is recorded at `v0.64`, so `E02-01` verifies
   and **`E02-02` FAILS BY DESIGN**: one cassette holds one
   `guideline_version` and neither item is restamped (§22.1 forbids
   restamping to force one stamp; §22.3 is the validity transfer). An
   expected failure is asserted as EXPECTED here, so it cannot be mistaken
   for a defect and a NEW failure cannot hide behind it.
2. **One `run_scoring.run()`**, reading both criterion-2 figures and the
   scored/unscoreable split off the real `Report` rather than hand-computing.
3. **Per-item outcome against the pre-registration's two tiers.** The reading
   rule, fixed in `162fe22` before any call: a Tier-1 item failing FOR ITS
   NAMED CAUSE is confirmation, not news; "REGRESSION" is used ONLY for a
   failure outside the pre-registered cause, and NEVER for a Tier-2 item,
   which has no prediction to regress from.
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "apps/brain"))
sys.path.insert(0, str(ROOT / "apps/brain/src"))

from evals.harness import cassette as cassette_mod  # noqa: E402

MODEL_ID = "openai/gpt-oss-120b"
PROMPT_VERSION = "v3"

# Committed in 162fe22 BEFORE any live call. Tier 1 = named cause; Tier 2 = no
# prediction, so a failure there is a finding rather than a regression.
TIER1 = {
    "C14-09": "F14 -- both party slots ABSENT; obligor_alias empty in 0 of 81 emitted "
              "candidates (Wilson95 upper 4.53%) against a v3.yaml with no obligor "
              "counterpart to its single empty-obligee_alias example, so clause 3 fails "
              "on PROMPT CONVENTION, not extraction quality",
    "C04-15": "untagged unrepresentable temporal 'During the Term of this Agreement' -- if "
              "quoted into temporal_raw, _classify_temporal returns None and "
              "UNMAPPABLE_TEMPORAL rejects the WHOLE candidate (the mechanism 15.3's "
              "falsified class placement measured at 5 of 5)",
    "C17-03": "TWO untagged gaps at once -- F28's disjunctive 'shall provide, OR shall "
              "cause ... to provide' whose cause limb maps to ENSURE/PROCURE against a "
              "singleton [PROVIDE], AND the same temporal mechanism on 'During the "
              "applicable Term of any Service'",
}
TIER2 = ["C04-10", "C04-13", "E01-05", "E02-01"]
# Stated in advance: one of E02-006's two items cannot verify, whichever stamp is used.
# Reviewer-ruled short run (§6.1): reported on the runs that exist, run 3 not
# attempted, reason stated inline wherever its figure appears. An EXPECTED short
# run must be distinguished from an unexpectedly incomplete one, or the one
# genuine anomaly hides among the known ones.
EXPECTED_SHORT = {"C04-144": 1}
EXPECTED_STALE = {"E02-02": "E02-006 recorded at v0.64 to serve E02-01 (Tier 2 AND "
                            "in-force-denominator); E02-02 is v0.65. NOT restamped."}


def locked_items() -> list[dict]:
    out = []
    for p in glob.glob(str(ROOT / "apps/brain/evals/goldens/batch0*/items/*.json")):
        d = json.load(open(p)); d["_p"] = p; out.append(d)
    assert len(out) >= 69, f"ITEM LOAD GATE FAILED: {len(out)} items (<69)"
    return out


def pool_segments() -> dict[str, str]:
    import importlib.util
    spec = importlib.util.spec_from_file_location("corpus", ROOT / "apps/brain/evals/corpus.py")
    c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = c.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)}"
    return {s["segment_id"]: s["text"] for s in pool}


TARGETS = ["C03-125", "C04-017", "C04-045", "C14-095", "C17-006",
           "C04-033", "C04-144", "C04-174", "E01-004", "E03-022", "E02-006"]


def step1_verify(items, segments) -> dict:
    print("=" * 78)
    print("1. Cassette.verify() PER ITEM (F16's per-item guideline_version)")
    print("=" * 78)
    by_seg = {}
    for i in items:
        by_seg.setdefault(i["segment_id"], []).append(i)

    results = {"verified": [], "expected_stale": [], "expected_short": [],
               "UNEXPECTED": [], "missing": []}
    for seg in TARGETS:
        segitems = by_seg.get(seg, [])
        runs = sorted(glob.glob(str(cassette_mod.CASSETTE_DIR / seg / "run*.json")))
        print(f"\n{seg}: {len(runs)} cassette(s) on disk, {len(segitems)} item(s)")
        if len(runs) != 3:
            if EXPECTED_SHORT.get(seg) == len(runs):
                print(f"  {len(runs)}/3 runs -- EXPECTED SHORT RUN, reviewer-ruled (§6.1); "
                      f"run 3 not attempted, no parameter changed")
                results["expected_short"].append((seg, len(runs)))
            else:
                print(f"  *** only {len(runs)} of 3 runs -- a stability number must never "
                      f"come from fewer (section 6)")
                results["missing"].append((seg, len(runs)))
        for it in segitems:
            iid, ver = it["item_id"], it["guideline_version"]
            oks, bad = [], []
            for run in (1, 2, 3):
                try:
                    c = cassette_mod.load(seg, run)
                    c.verify(segment_text=segments[seg], model_id=MODEL_ID,
                             prompt_version=PROMPT_VERSION, guideline_version=ver)
                    oks.append(run)
                except cassette_mod.CassetteMissing:
                    bad.append((run, "MISSING", frozenset()))
                except cassette_mod.StaleCassette as e:
                    bad.append((run, str(e).splitlines()[0], e.dimensions))
            if not bad:
                print(f"  {iid} ({ver}): VERIFIES on runs {oks}")
                results["verified"].append(iid)
            elif iid in EXPECTED_STALE:
                dims = sorted(set().union(*[d for _, _, d in bad]))
                print(f"  {iid} ({ver}): STALE on {[r for r,_,_ in bad]} -- EXPECTED BY DESIGN")
                print(f"      dimensions: {dims}   (must be ['guideline_version'] only)")
                print(f"      reason: {EXPECTED_STALE[iid]}")
                if dims != ["guideline_version"]:
                    print(f"      *** UNEXPECTED DIMENSION -- this is NOT the designed failure")
                    results["UNEXPECTED"].append((iid, dims))
                else:
                    results["expected_stale"].append(iid)
            else:
                dims = sorted(set().union(*[d for _, _, d in bad]) or {"missing"})
                print(f"  {iid} ({ver}): *** UNEXPECTED STALE/MISSING on "
                      f"{[r for r,_,_ in bad]}, dimensions {dims}")
                results["UNEXPECTED"].append((iid, dims))
    return results


def step2_score():
    print("\n" + "=" * 78)
    print("2. ONE run_scoring.run()")
    print("=" * 78)
    from evals.harness import run_scoring
    rep, _conditions, _compile = run_scoring.run(model_id=MODEL_ID)
    print(f"  items total              : {len(rep.items)} scored")
    print(f"  in-force criterion 2     : {rep.criterion2_no_known_gaps}")
    print(f"  all-items (NOT the crit) : {rep.criterion2_all_items}")
    return rep


def step3_prereg(rep):
    print("\n" + "=" * 78)
    print("3. PER-ITEM vs PRE-REGISTRATION (162fe22, committed before any call)")
    print("=" * 78)
    scored = {i.item_id: i for i in rep.items}

    print("\n-- TIER 1 (known cause: failing FOR THAT CAUSE is CONFIRMATION, not news) --")
    for iid, cause in TIER1.items():
        it = scored.get(iid)
        if it is None:
            print(f"\n  {iid}: NOT SCORED (see G8) -- no outcome, prediction untested")
            continue
        print(f"\n  {iid}: modal={it.modal}  runs={[str(o) for o in it.outcomes]}"
              f"  unstable={it.unstable}")
        print(f"    failed_clauses={sorted(it.failed_clauses)}  known_gaps={list(it.known_gaps)}")
        print(f"    predicted: {cause[:100]}...")

    print("\n-- TIER 2 (NO prediction: the word REGRESSION does not apply here) --")
    for iid in TIER2:
        it = scored.get(iid)
        if it is None:
            print(f"  {iid}: NOT SCORED (see G8)")
            continue
        print(f"  {iid}: modal={it.modal}  runs={[str(o) for o in it.outcomes]}  "
              f"unstable={it.unstable}  failed_clauses={sorted(it.failed_clauses)}")


def main() -> int:
    items = locked_items()
    segments = pool_segments()
    print(f"gates: {len(items)} locked items, 1547-segment pool  PASS\n")
    r = step1_verify(items, segments)
    rep = step2_score()
    step3_prereg(rep)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  verified          : {len(r['verified'])} items")
    print(f"  expected stale    : {r['expected_stale']}")
    print(f"  UNEXPECTED stale  : {r['UNEXPECTED']}")
    print(f"  expected short    : {r['expected_short']}  (§6.1, reviewer-ruled)")
    print(f"  incomplete runs   : {r['missing']}")
    print(f"\n  in-force criterion 2 : {rep.criterion2_no_known_gaps}")
    print(f"  all-items            : {rep.criterion2_all_items}")
    if r["UNEXPECTED"] or r["missing"]:
        print("\n*** DO NOT COMMIT until each line above is explained.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
