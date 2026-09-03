# Splitting/exclusion investigation scripts

Preserved for the same reason `audit/`'s are: `RESULTS.md`'s own Finding 2 counts are not
reproducible because its script was never kept, and §0 of `OBJECT_CLASS_INVESTIGATION.md`
could be corrected only because its numbers *were* re-derivable. Every count in
`SPLITTING_EXCLUSION_INVESTIGATION.md` comes from one of these four.

| file | what it produces | known-answer check |
| :-- | :-- | :-- |
| `counts.py` | §1's per-segment table, the 9-vs-10 reconciliation, §5's batch/density confound | asserts 41 cold / 32 gold / 22 segments / the six named transitions against `RESULTS.md` before reading any new number |
| `may_scan.py` | §4's `MAY`-shaped clause census | asserts the three established cases (`C13-041`, `C04-117`, `C11-094`) are flagged; prints **every** flagged sentence in full so false positives are adjudicated by reading, not suppressed |
| `unexpected.py` | §6's candidate classification and the 54% figure | asserts `C17-066` run 1 = 1 `GOLD_MATCH` + 1 `COLD_ONLY`; also asserts each cassette's `segment_sha256` against the packet segment text |
| `records.py` | §3's record audit — sub-sentence exclusion entries, populated R6 spans, notes grep | none needed (exhaustive enumeration, not a detector); its notes grep returns raw context for reading, and one hit is a **false positive** adjudicated in §3 |

Run from anywhere; paths are absolute to `apps/brain/evals/goldens`. `counts.py` imports
`evals.corpus` for `_MODAL_RE`/`split_sentences` and needs the repo venv:

```
/Users/rajitagrawal/obligo/.venv/bin/python splitting/counts.py
```

**These scripts do not implement §4.2's content tie-break.** No case in this investigation
needs it — the one segment in the set with byte-identical spans (`C04-139`) has agreeing item
counts and is not part of the surplus. `unexpected.py` reproduces `align.py`'s greedy IoU >= 0.5
rule for *classification only*; it is not a scorer and emits no outcome.

**The known-answer checks are `assert`s, not prints, and they were falsification-controlled.**
A check that only prints is a check nobody reads. Each assert was re-run once with a planted
mutation (`counts.py` expecting 99 gold items; `may_scan.py` expecting a nonexistent segment;
`unexpected.py` expecting a nonexistent classification pair) and each exited non-zero — so a
clean exit means the check ran and passed, not that it was vacuous. Same discipline as
`audit/inject.py`'s planted-instance control for §10.3.
