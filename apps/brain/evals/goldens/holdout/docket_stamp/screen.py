"""§8.7 furniture that a RECURRENCE test cannot see: templated page stamps whose
TOKENS vary per page.

WHY THIS EXISTS, stated as a defect history rather than a design. Batch 6 used two
furniture detectors in sequence and BOTH gave a false negative:

  1. A LITERAL-STRING check hardcoded to C04's "Miltenyi Biotec-Bellicum Supply
     Agreement" header. It returned NONE for `C03-125`, a segment that is ~50%
     furniture, because C03's furniture is a different string. Caught by eye, not
     by the detector.
  2. A RECURRENCE check (does a 6-or-8-word run repeat across >=5 of the
     document's pool segments?), which fixed (1)'s per-document hardcoding. It
     returned NONE for `C06-051`, whose S2 carries a bankruptcy docket stamp
     SPLICED MID-PREDICATE: "Merchant shall be 17 Case 18-10248-MFW Doc 632-1
     Filed 04/18/18 Page 19 of 60 solely responsible for...".

(2) failed for a reason (1)'s fix could not address: the stamp's TOKENS vary per
page -- the leading page number, `Doc`, and `Page N of 60` all differ -- so
VERBATIM occurrences across C06 are 1, and digit-normalised they are 2 of 122 pool
segments, still below any plausible recurrence floor. MEASURED, and the measurement
corrected an overclaim of mine: a first draft of this gate asserted the template
recurs >=5 times and it recurs TWICE, which the assertion caught.

The pool is a FILTERED subset (200-2000 chars, modal present), so most pages'
stamps never enter it at all. That is why no recurrence threshold works here and
why this class needs a SHAPE test -- a third approach, not a tuning of the second.

Standing Principle 7: the gate is two-sided and asserts BOTH that `C06-051`'s stamp
is matched AND that a clean segment is not, before any count is read off it.

    uv run --project apps/brain python \
        apps/brain/evals/goldens/holdout/docket_stamp/screen.py
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[4]
ROOT = BRAIN.parents[1]
POOL_EXPECTED = 1547

# Shape, not wording: a court/EDGAR page stamp. Digits are classes, so per-page
# variation cannot defeat it.
DOCKET = re.compile(
    r"\d*\s*Case\s+[\d:-]+-?\w*\s+Doc(?:ument)?\s+[\d.-]+\s+Filed\s+[\d/]{6,10}"
    r"(?:\s+Entered\s+[\d/: ]+)?\s+Page\s+\d+\s+of\s+\d+",
    re.I,
)
PAGE_OF = re.compile(r"\bPage\s+\d+\s+of\s+\d+\b", re.I)
EDGAR_SRC = re.compile(r"\bSource:\s+[A-Z][A-Za-z0-9 .,&'-]+,\s*\d{1,2}-[A-Z]", re.I)

# The TEN batch-6 segments walked BEFORE C06-051, retrospectively screened. (Corrected
# 2026-10-08: this comment read "six" over a ten-entry list -- a stale count, not a
# stale list; the list itself was always the full set of earlier segments.)
EARLIER = ["C04-172", "C22-039", "C04-017", "C04-045", "C03-125", "C14-030",
           "C02-079", "C06-028", "C17-006", "C14-095"]


def load(mod):
    pool = mod.build_pool(ROOT / ".corpus", mod.load_manifest())
    if len(pool) < POOL_EXPECTED:
        raise RuntimeError(f"pool rebuilt to {len(pool)}; a gate over a short pool proves nothing")
    return pool


def main() -> int:
    spec = importlib.util.spec_from_file_location("corpus", BRAIN / "evals/corpus.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    pool = load(mod)
    by = {s["segment_id"]: s["text"] for s in pool}

    # --- two-sided gate, before any count ---
    assert DOCKET.search(by["C06-051"]), "GATE FAILED: C06-051's docket stamp is not matched"
    assert not DOCKET.search(by["C17-006"]), "GATE FAILED: a clean segment matched the stamp shape"
    print("GATE PASSED: C06-051 matched, C17-006 (clean) not matched\n")

    print("RETROSPECTIVE SCREEN over every batch-6 segment walked, in order:")
    hits = []
    for sid in EARLIER + ["C06-051"]:
        t = by[sid]
        d = DOCKET.search(t); po = PAGE_OF.search(t); es = EDGAR_SRC.search(t)
        mark = []
        if d: mark.append(f"DOCKET[{d.start()}:{d.end()}]")
        if po and not d: mark.append(f"PAGE-OF[{po.start()}:{po.end()}]")
        if es: mark.append(f"EDGAR-SRC[{es.start()}:{es.end()}]")
        if mark: hits.append((sid, mark))
        print(f"  {sid:10s} {'  '.join(mark) if mark else '-- clean'}")

    print(f"\nHITS: {len(hits)} of {len(EARLIER)+1} batch-6 segments")
    for sid, mark in hits:
        t = by[sid]
        m = DOCKET.search(t) or PAGE_OF.search(t) or EDGAR_SRC.search(t)
        print(f"  {sid}: {t[m.start():m.end()]!r}")
        print(f"      splices: ...{t[max(0,m.start()-20):m.start()]!r} || "
              f"{t[m.end():m.end()+20]!r}")

    print("\nPool-wide, for scale (shape test, not recurrence):")
    n = sum(1 for s in pool if DOCKET.search(s["text"]))
    docs = sorted({s["doc_id"] for s in pool if DOCKET.search(s["text"])})
    print(f"  docket stamps: {n} of {len(pool)} segments, documents {docs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
