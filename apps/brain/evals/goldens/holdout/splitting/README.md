# Splitting/exclusion investigation scripts

Preserved for the same reason `audit/`'s are: `RESULTS.md`'s own Finding 2 counts are not
reproducible because its script was never kept, and §0 of `OBJECT_CLASS_INVESTIGATION.md`
could be corrected only because its numbers *were* re-derivable. Every count in
`SPLITTING_EXCLUSION_INVESTIGATION.md` comes from one of these five.

| file | what it produces | known-answer check |
| :-- | :-- | :-- |
| `counts.py` | §1's per-segment table, the 9-vs-10 reconciliation, §5's batch/density confound | asserts 41 cold / 32 gold / 22 segments / the six named transitions against `RESULTS.md` before reading any new number |
| `may_scan.py` | §4's `MAY`-shaped clause census | asserts the three established cases (`C13-041`, `C04-117`, `C11-094`) are flagged; prints **every** flagged sentence in full so false positives are adjudicated by reading, not suppressed |
| `unexpected.py` | §6's candidate classification and the 54% figure | asserts `C17-066` run 1 = 1 `GOLD_MATCH` + 1 `COLD_ONLY`; also asserts each cassette's `segment_sha256` against the packet segment text |
| `disposition_cost.py` | §11's ruling-log numbers for decision 1 — the per-segment cost distribution, the pool-weighted forward cost, the §6.3 denominator correction, the non-modal census, and the 79% `UNEXPECTED` retirement | asserts `counts.py`'s 32/22/6 **and** `unexpected.py`'s 46/13/11/11 before reading any new figure; also asserts `C04-117`'s §2.5 rights clause is non-modal, which is the fact §2.7's sentence-level unit rests on |
| `records.py` | §3's record audit — sub-sentence exclusion entries, populated R6 spans, notes grep | none needed (exhaustive enumeration, not a detector); its notes grep returns raw context for reading, and one hit is a **false positive** adjudicated in §3 |

**`disposition_cost.py` corrected two of its own detectors mid-run, and both corrections are
in the file rather than only in the output** — Standing Principle 7 applied to this script's own
totals. (1) The arithmetic proxy `modal − gold` **undercounts** the undisposed sentences (20 vs
the true 21): `C14-076` carries two gold items inside one sentence (§8.3.1), so subtracting item
counts from sentence counts double-credits the covered sentence. Undisposed is computed by span
overlap instead. (2) Matching an anchor phrase anywhere in an `exclusions.json` entry gives
**false positives**: `E03-005#discuss` quotes its neighbouring sentences inside its own
`segment_text` field, so two sentences appeared disposed by an entry that says nothing about
them. Only `reason`/`rule`/`segment_id` are searched.

Run from anywhere; paths are absolute to `apps/brain/evals/goldens`. `counts.py` and
`disposition_cost.py` import `evals.corpus` for `_MODAL_RE`/`split_sentences` and need the repo
venv:

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
`unexpected.py` expecting a nonexistent classification pair; `disposition_cost.py` expecting 99 undisposed sentences) and each exited non-zero — so a
clean exit means the check ran and passed, not that it was vacuous. Same discipline as
`audit/inject.py`'s planted-instance control for §10.3.
