"""F31's stratum-artifact test: attribute every live §10.1 queue row to the
stratum of the item or segment that opened it, and compare per-stratum rates.

F31 fixed the design before any row was looked at. This script executes it and
nothing else: it does NOT draw, and it does NOT decide F25/F28/F29 (see
`class_sizes.py`).

TWO ATTRIBUTION RULES ARE COMPUTED, DELIBERATELY, because F31 names only three
rows (F17/F20/F21) as unattributable and leaves the general criterion to be
stated. Both readings below are defensible from F31's own text, and they are
NOT nested -- F13 is attributable under STRICT and not under LOCUS:

  LOCUS  -- "the stratum of the ITEM OR SEGMENT that opened it": a row is
            attributed when its own `item(s)` column names a specific gold
            item or segment (or several, all in one stratum). A column reading
            "whole set", a bare instrument/reporting layer, or a locus
            spanning BOTH strata is unattributable.
  STRICT -- "...that OPENED it": a row is attributed only when the question was
            raised BY DRAFTING WORK on a segment (its annotation, exclusion or
            §2.7 disposition). A row raised by a screen, a ruling on another
            row, a scoring run, a report layer, the harness, a review of the
            guideline's own rule text or tag vocabulary, or a reviewer
            sequencing decision is unattributable. This is the reading F31
            itself applies to F21 ("OPENED v0.63 BY §8.12's RULING" ->
            unattributable) and to F27 (a tooling defect found WHILE
            DISPOSITIONING `C04-144` -> attributed to batch 5).

Standing Principle 7: every gate below is a KNOWN ANSWER fixed by someone
other than this script -- F31's own stated denominators and H0 shares, F31's
own three named unattributable rows, F31's own count of batch 5's rows, and
the pool's 1,547-segment rebuild. `load_*` raises below a floor, because a
known-answer gate over an empty corpus passes (v0.58's screen printed
"12/12 PASS" over zero items for exactly that reason).
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
GOLDENS = ROOT / "apps/brain/evals/goldens"
GUIDELINE = ROOT / "docs/eval/GOLD_SET_GUIDELINE.md"
BATCHES = ["batch01", "batch02", "batch03", "batch04", "batch05"]
BATCH_14 = BATCHES[:4]

# F31(b)/(c)'s own figures, quoted. These are the gate, not an output.
F31_DENOM_14 = (33, 40)
F31_DENOM_ALL = (42, 40)
F31_H0_14 = 0.452
F31_H0_ALL = 0.512
# F31(e)'s own three named unattributable rows.
F31_NAMED_UNATTRIBUTABLE = {"F17", "F20", "F21"}
# F31(3)'s own count: batch 5 "opened 7 of the queue's rows".
F31_BATCH5_OPENED = {"F24", "F25", "F26", "F27", "F28", "F29", "F30"}
# F31(c)'s bands, as shares of attributable rows.
BAND_HOLDS, BAND_SUGGESTIVE = 0.10, 0.20
# Rows THIS PASS opened. They are excluded from the measured population, not
# classified into it: counting a pass's own output in its own denominator is
# circular, and F31(d)'s "numerator and denominator must share scope" is the
# same discipline one level up. The measured population is the queue AS IT
# STOOD when the pass ran -- F1-F32.
OPENED_BY_THIS_PASS = {"F33"}


def _corpus():
    spec = importlib.util.spec_from_file_location(
        "corpus", ROOT / "apps/brain/evals/corpus.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doc_strata() -> dict[str, str]:
    """Stratum is a DOCUMENT property (`xref_pct` >= 20), read off the manifest
    the same way `corpus.build_pool()` reads it -- not recomputed here."""
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    out = {}
    for group in man["documents"].values():
        for doc in group:
            out[doc["id"]] = "hard" if int(doc["xref_pct"]) >= 20 else "standard"
    if len(out) < 28:
        raise RuntimeError(f"manifest yielded only {len(out)} documents")
    return out


def load_items() -> dict[str, dict]:
    items = {}
    for b in BATCHES:
        for f in sorted((GOLDENS / b / "items").glob("*.json")):
            d = json.loads(f.read_text())
            items[d["item_id"]] = {"batch": b, **d}
    if len(items) < 60:
        raise RuntimeError(f"load_items() loaded only {len(items)}; expected >= 60")
    return items


def bare(segment_id: str) -> str:
    """F32: batches 1 and 3 store a COMPOSITE id in `segment_id`; strip it."""
    return segment_id.split("#")[0]


def touched_segments() -> dict[str, set[str]]:
    """Every segment a batch consumed: annotated (via its items) or excluded."""
    out = {}
    for b in BATCHES:
        segs = {
            json.loads(f.read_text())["segment_id"]
            for f in (GOLDENS / b / "items").glob("*.json")
        }
        segs |= {
            bare(e["segment_id"])
            for e in json.loads((GOLDENS / b / "exclusions.json").read_text())
        }
        out[b] = segs
    return out


def live_queue_rows() -> list[str]:
    """Parses §10.1's queue, SCOPED TO THAT TABLE.

    An earlier draft matched `^| **Fn** | ` anywhere in the document and
    deduplicated by first occurrence. That was RIGHT ONLY BY DOCUMENT ORDER:
    §10.1 happens to precede both the 5-column audit sub-table that repeats
    four row labels and §10.3.4's own size table, which carries rows labelled
    `**F25**`/`**F28**`/`**F29**` and would otherwise be read as queue rows.
    A parse that is correct because of where a section sits is one edit away
    from being wrong, so the scan now starts at §10.1's heading and stops at
    the blank line that ends its table -- Standing Principle 7's shape applied
    to a document parser.

    The struck-through superseded F9 duplicate is excluded by construction:
    its cell reads `~~**F9 (original entry...)**~~`, which the anchored
    pattern does not match.
    """
    lines = GUIDELINE.read_text().splitlines()
    start = next(
        (i for i, l in enumerate(lines) if l.startswith("### 10.1 The freeze-pass queue")),
        None,
    )
    if start is None:
        raise RuntimeError("§10.1's heading not found; the queue parser needs re-anchoring")
    rows, in_table = [], False
    for line in lines[start:]:
        if re.match(r"^\| \*\*F\d+\*\* \| ", line):
            in_table = True
            rows.append(re.match(r"^\| \*\*(F\d+)\*\* \| ", line).group(1))
        elif in_table and not line.startswith("|"):
            break  # the blank line after the last row ends §10.1's table
    if len(rows) != len(set(rows)):
        dupes = sorted({r for r in rows if rows.count(r) > 1})
        raise RuntimeError(f"§10.1's queue has duplicate rows: {dupes}")
    if len(rows) < 32:
        raise RuntimeError(f"parsed only {len(rows)} queue rows; expected >= 32")
    return rows


# --- THE ATTRIBUTION TABLE --------------------------------------------------
# `locus`  : items/segments named by the row's own `item(s)` column, or None.
# `opener` : the segment whose DRAFTING WORK raised the question, or None with
#            the kind of work that did.
# Both are hand-authored from each row's own text and cited source; `basis`
# records which words carried the call, so a reader can falsify one row
# without re-deriving all of them.
A = collections.namedtuple("A", "locus opener basis")
TABLE: dict[str, A] = {
    "F1":  A(["C02-03", "C11-01", "C02-01"], None,
             "column names 3 items; opened by the v0.33 failure-driver SCORING RUN over the set (§3.4's bounded exception)"),
    "F2":  A(["C10-02"], None,
             "column names 1 item; opened by the v0.45 re-validation SCREEN"),
    "F3":  A(["C04-04", "C04-05"], None,
             "column names 2 items (one segment); opened by the v0.45 re-validation SCREEN"),
    "F4":  A(["C14-02"], None,
             "column names 1 item; opened by §22.1's CASSETTE-STALENESS DECISION"),
    "F5":  A(None, None,
             "column reads 'whole set'; opened by OBJECT_CLASS_INVESTIGATION's set-wide AUDIT"),
    "F6":  A(["C06-01", "C13-01", "C14-01"], None,
             "column names 3 items; opened by §3.6's v0.45 depth-convention REVIEW"),
    "F7":  A(["C04-02"], None,
             "column names 1 item; opened by the v0.46 §8 REVIEW"),
    "F8":  A(["E01-01"], None,
             "column names 1 item; opened by the v0.46 §8 REVIEW"),
    "F9":  A(None, None,
             "column reads 'whole set'; opened by the v0.46 TAG-VOCABULARY REVIEW"),
    "F10": A(None, None,
             "column reads 'n/a -- reporting layer'; REPORT LAYER"),
    "F11": A(["C10-01"], None,
             "column names 1 item; opened by §8.3.2's RE-CHECK"),
    "F12": A(None, None,
             "column reads 'whole set'; opened by the v0.48 F3 RULING (a screen's scope)"),
    "F13": A(None, "C11-094",
             "column reads 'whole set'; but surfaced BY THE COLD ANNOTATOR in C11-094 item 2's notes -- annotation work"),
    "F14": A(None, "C14-076",
             "column reads 'whole set'; opened during C14-076 candidate 2's ESCALATION investigation"),
    "F15": A(None, "C14-076",
             "column reads 'whole set'; opened during the same C14-076 escalation investigation"),
    "F16": A(None, None,
             "column reads 'whole set'; a HARNESS defect (run_scoring cannot execute)"),
    "F17": A(None, None,
             "column reads 'whole set -- reporting/instrument layer'; F31(e) names it unattributable"),
    "F18": A(["E03-01"], None,
             "column reads 'E03-01 today; the WITHHELD_VALUE kind generally'; opened by the v0.59 F9 RULING"),
    "F19": A(["E03-01"], None,
             "column names E03-01; opened by the v0.60 F18 RULING"),
    "F20": A(None, None,
             "the G instrument's reproduction; F31(e) names it unattributable"),
    "F21": A(None, None,
             "column names a TAG and an AXIS, no item; opened by the v0.63 §8.12 RULING; F31(e) names it unattributable"),
    "F22": A(["C10-02", "C14-04", "E08-04"], None,
             "column's 3 logged items span BOTH strata, plus 'the whole 8-item class'; opened by the v0.64 §8.8.5 RULING"),
    "F23": A(["E02-02"], None,
             "column reads 'the unit-modifier gap...; E02-02 today'; opened by the v0.65 §8.13 RULING -- and F31(3) does NOT count it among batch 5's rows"),
    "F24": A(["E03-046"], "E03-046",
             "column names the segment E03-046; 'OPENED 2026-09-24 BY E03-046's EXCLUSION'"),
    "F25": A(["C10-03"], "C10-025",
             "'OPENED 2026-09-24 BY C10-025's ANNOTATION'"),
    "F26": A(["E03-04", "E03-05"], "E03-022",
             "'OPENED 2026-09-25 BY E03-022's ANNOTATION'"),
    "F27": A(["C04-144"], "C04-144",
             "column names split_sentences() and 'C04-144 today'; 'FOUND 2026-09-26 WHILE DISPOSITIONING C04-144'"),
    "F28": A(["C04-144"], "C04-144",
             "column names 'C04-144 sentence A today'; 'OPENED 2026-09-26 BY C04-144's ANNOTATION'"),
    "F29": A(["C04-144"], "C04-144",
             "column names 'C04-144 sentence A today'; 'OPENED 2026-09-26 BY C04-144's ANNOTATION'"),
    "F30": A(["E03-046"], "C04-144",
             "column names E03-046's observation gloss; 'FOUND 2026-10-04 AT C04-144 SENTENCE B'"),
    "F31": A(None, None,
             "the draw itself; a REVIEWER SEQUENCING decision"),
    "F32": A(None, None,
             "a field CONVENTION spanning batches 1/3/4/5; found while computing F31's denominators"),
}


def _stratum_of_locus(locus, items, strata):
    """A locus resolves to a stratum only if every named item/segment agrees.
    A mixed locus is UNATTRIBUTABLE -- F31(e) forbids forcing one."""
    if not locus:
        return None, None
    segs, sts = [], set()
    for name in locus:
        if name in items:
            segs.append(items[name]["segment_id"])
            sts.add(items[name]["stratum"])
        else:  # a bare segment id
            segs.append(name)
            sts.add(strata[name.split("-")[0]])
    return (sorted(set(segs)), sts.pop()) if len(sts) == 1 else (sorted(set(segs)), None)


def run() -> dict:
    corpus = _corpus()
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = corpus.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)} segments, expected 1547"
    print(f"pool-rebuild gate: {len(pool)} segments  PASS")

    strata = doc_strata()
    items = load_items()
    rows = live_queue_rows()
    touched = touched_segments()

    # --- GATE: document-level stratum agrees with every draw queue ----------
    checked = disagree = 0
    for b in BATCHES:
        p = GOLDENS / b / "draw.json"
        if not p.exists():
            continue
        for queue in json.loads(p.read_text())["queues"].values():
            for r in queue:
                checked += 1
                if strata[r["doc_id"]] != r["stratum"]:
                    disagree += 1
    assert checked >= 180 and disagree == 0, f"STRATUM GATE FAILED: {disagree}/{checked}"
    assert len({strata[d] for d in strata}) == 2, "STRATUM GATE FAILED: one-sided map"
    print(f"stratum-map gate: {checked} queue entries, 0 disagreements, both strata present  PASS")

    # --- GATE: F32's five composite ids, two-sided -------------------------
    composites = [
        e["segment_id"]
        for b in BATCHES
        for e in json.loads((GOLDENS / b / "exclusions.json").read_text())
        if "#" in e["segment_id"]
    ]
    pool_ids = {s["segment_id"] for s in pool}
    assert len(composites) == 5, f"F32 GATE FAILED: {len(composites)} composite ids, expected 5"
    assert all(bare(c) in pool_ids for c in composites), "F32 GATE FAILED: a stripped id does not resolve"
    assert not any(c in pool_ids for c in composites), "F32 GATE FAILED: an unstripped id resolved"
    print(f"F32 strip gate: {len(composites)}/5 resolve stripped, 0/5 unstripped  PASS")

    # --- GATE: F31(b)'s denominators ---------------------------------------
    denoms = {}
    for name, bs in [("batches 1-4", BATCH_14), ("all five", BATCHES)]:
        segs = set().union(*[touched[b] for b in bs])
        c = collections.Counter(strata[s.split("-")[0]] for s in segs)
        denoms[name] = (c["hard"], c["standard"])
    assert denoms["batches 1-4"] == F31_DENOM_14, f"DENOM GATE FAILED: {denoms}"
    assert denoms["all five"] == F31_DENOM_ALL, f"DENOM GATE FAILED: {denoms}"
    h14 = F31_DENOM_14[0] / sum(F31_DENOM_14)
    hall = F31_DENOM_ALL[0] / sum(F31_DENOM_ALL)
    assert round(h14, 3) == F31_H0_14 and round(hall, 3) == F31_H0_ALL, "H0 GATE FAILED"
    print(f"denominator gate: 1-4 = {F31_DENOM_14[0]}h/{F31_DENOM_14[1]}s = {sum(F31_DENOM_14)}, "
          f"H0 {h14:.3f}; all five = {F31_DENOM_ALL[0]}h/{F31_DENOM_ALL[1]}s = {sum(F31_DENOM_ALL)}, "
          f"H0 {hall:.3f}  PASS")

    # --- GATE: the table covers exactly the live queue ---------------------
    measured = [r for r in rows if r not in OPENED_BY_THIS_PASS]
    assert set(TABLE) == set(measured), (
        f"TABLE GATE FAILED: missing {sorted(set(measured) - set(TABLE))}, "
        f"extra {sorted(set(TABLE) - set(measured))}"
    )
    assert OPENED_BY_THIS_PASS <= set(rows), (
        f"COVERAGE GATE FAILED: {sorted(OPENED_BY_THIS_PASS - set(rows))} is declared as "
        "opened by this pass but is not in the queue"
    )
    print(f"coverage gate: {len(rows)} live queue rows, {len(measured)} measured, "
          f"{sorted(OPENED_BY_THIS_PASS)} excluded as THIS PASS's own output  PASS")

    # --- resolve both rules ------------------------------------------------
    res = {}
    for row, a in TABLE.items():
        lsegs, lstratum = _stratum_of_locus(a.locus, items, strata)
        ostratum = strata[a.opener.split("-")[0]] if a.opener else None
        res[row] = {
            "locus_segments": lsegs, "LOCUS": lstratum,
            "opener": a.opener, "STRICT": ostratum,
            "batches": sorted({b for b in BATCHES
                               for s in (lsegs or []) + ([a.opener] if a.opener else [])
                               if s in touched[b]}),
            "basis": a.basis,
        }

    # --- GATE: F31's own answers -------------------------------------------
    for row in sorted(F31_NAMED_UNATTRIBUTABLE):
        r = res[row]
        assert r["LOCUS"] is None and r["STRICT"] is None, \
            f"F31(e) GATE FAILED: {row} is named unattributable but resolves {r}"
    print(f"F31(e) gate: {sorted(F31_NAMED_UNATTRIBUTABLE)} unattributable under BOTH rules  PASS")
    for row in sorted(F31_BATCH5_OPENED):
        assert res[row]["STRICT"] == "hard" and res[row]["batches"] == ["batch05"], \
            f"F31(3) GATE FAILED: {row} -> {res[row]}"
    assert {r for r, v in res.items() if v["STRICT"] and v["batches"] == ["batch05"]} \
        == F31_BATCH5_OPENED, "F31(3) GATE FAILED: batch-5-opened set is not exactly F24-F30"
    print(f"F31(3) gate: batch 5 opened exactly {len(F31_BATCH5_OPENED)} rows (F24-F30)  PASS")
    return {"res": res, "rows": measured, "all_rows": rows, "denoms": denoms,
            "items": items}


def report(state: dict) -> None:
    res, rows = state["res"], state["rows"]

    print(f"\n{'='*78}\nSTEP 1 -- THE UNATTRIBUTABLE COUNT, REPORTED BEFORE ANY SPLIT (F31(e))\n{'='*78}")
    print("  thresholds, fixed by F31 before any row was looked at:")
    print("    <= 6   proceed | 7-10  proceed with an explicit caveat | > 10  NOT MEASURABLE FROM THIS SET\n")
    verdicts = {}
    for rule in ("LOCUS", "STRICT"):
        un = [r for r in rows if res[r][rule] is None]
        gate = ("proceed" if len(un) <= 6 else
                "proceed WITH CAVEAT" if len(un) <= 10 else "NOT MEASURABLE FROM THIS SET")
        verdicts[rule] = (len(un), gate, un)
        print(f"  {rule:7} unattributable {len(un):2} of {len(rows)}  ->  {gate}")
        print(f"          {', '.join(un)}")
    print(f"\n  BOTH defensible rules exceed 10." if all(v[0] > 10 for v in verdicts.values())
          else "\n  The rules disagree on the gate.")

    print(f"\n{'='*78}\nSTEP 2 -- THE SPLIT (DESCRIPTIVE ONLY WHERE THE GATE ABOVE FIRED)\n{'='*78}")
    for rule in ("LOCUS", "STRICT"):
        print(f"\n  --- {rule} rule " + "-" * 50)
        for name, bs, h0 in [("batches 1-4 (THE VERDICT SCOPE)", BATCH_14, F31_H0_14),
                             ("all five (REPORTED ALONGSIDE, NOT THE VERDICT)", BATCHES, F31_H0_ALL)]:
            keep = [r for r in rows
                    if res[r][rule] and res[r]["batches"]
                    and set(res[r]["batches"]) <= set(bs)]
            c = collections.Counter(res[r][rule] for r in keep)
            n = len(keep)
            if not n:
                print(f"  {name}: 0 attributable rows -- no share definable")
                continue
            share = c["hard"] / n
            dev = abs(share - h0)
            band = ("H0 HOLDS" if dev <= BAND_HOLDS else
                    "SUGGESTIVE" if dev <= BAND_SUGGESTIVE else "REAL STRATUM EFFECT")
            print(f"  {name}:")
            print(f"     attributable rows {n}  (hard {c['hard']}, standard {c['standard']})")
            print(f"     hard share {share:.3f} vs H0 {h0:.3f}  deviation {dev:.3f}  -> band: {band}")
            print(f"     hard    : {', '.join(r for r in keep if res[r][rule]=='hard') or '-'}")
            print(f"     standard: {', '.join(r for r in keep if res[r][rule]=='standard') or '-'}")

    print(f"\n{'='*78}\nSTEP 3 -- PER-ROW RECORD\n{'='*78}")
    for r in rows:
        v = res[r]
        print(f"  {r:4} LOCUS={str(v['LOCUS']):9} STRICT={str(v['STRICT']):9} "
              f"{','.join(v['batches']) or '-':20} {v['basis']}")


if __name__ == "__main__":
    report(run())
