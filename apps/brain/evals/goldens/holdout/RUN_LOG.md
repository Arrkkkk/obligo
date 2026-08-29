# §7 cold second-annotator check — run log

Appended in order. Records every attempt, including failed ones, so the number of runs
behind any published K is visible rather than reconstructed.

## Attempt 1 — 2026-08-29 ~01:55 IST — FAILED, zero output

Fresh general-purpose subagent (deliberately not a fork: the orchestrating session's
context is saturated with the drafters' answers). Terminated early by an account session
limit (HTTP 429, `rate_limit`, resets 02:10 IST).

**Produced nothing.** `out/` was empty — it consumed its budget reading the 4,479-line
guideline and died before writing its first segment file.

**Diagnosis, and it is a design fault in the harness rather than in the model:** the run
was instructed to write one output file per segment but not told *when*. The seeded segment
order exists precisely so that a truncated run yields a valid seeded-random prefix
(PREREGISTRATION §5) — but that property is worthless unless output reaches disk as the run
proceeds. A run that batches its writes converts any interruption into total loss.

**No contamination risk from the failure.** The quarantine (PREREGISTRATION §6) held
throughout and was restored afterwards: all 34 quarantined files verified readable and
**byte-identical** to `prerun_hashes.json`, `git status` clean apart from this untracked
`holdout/` directory.

**Two `git status` anomalies were chased down rather than assumed benign**, since the
session-start snapshot showed `M batch01/SUMMARY.md` and `?? goldens/holdout/` and both
disappeared when the quarantine was lifted:
- No content was lost. `batch01/SUMMARY.md` is byte-identical to `HEAD` and to its pre-run
  hash; `git diff HEAD` is empty.
- Nothing pre-existing was overwritten in `holdout/`. Every file in it is timestamped
  01:51–01:54 on 2026-08-29, i.e. created by this session.
- Both anomalies are artifacts of this session's own work: git reports a `chmod 000` file as
  modified because it cannot read it to compare, and `holdout/` was newly untracked. The
  snapshot was therefore taken mid-session, not before it — confirmed by the fact that
  `holdout/` contains no file predating this session, which it would have to if the snapshot
  were genuinely from session start.

**Procedural gap recorded, small but real:** `prerun_hashes.json` captures content hashes
only, not file modes, so the quarantine's restore step could not prove modes were returned
to their prior values — it could only prove content was intact. Capture modes alongside
hashes next time.

## Attempt 2 — 2026-08-29 ~02:12 IST — launched

Relaunched after the session limit reset. Quarantine re-applied and re-verified by
known-answer test first: reads of `batch0{1,2,3}/items/`, `batch01/segments/` and
`batch01/SUMMARY.md` all confirmed blocked; the packet path confirmed still readable.

**One change from attempt 1, and only one** — the instrument itself is unchanged (same
packet, same seeded order, same guideline, same constraints): the agent is now instructed
to write each segment's output file immediately on finishing that segment, before starting
the next, and told explicitly that a partial run is useful provided the prefix is on disk.
It is also told to read the guideline once rather than re-reading it.

**Attempt 2 result — COMPLETE.** All 22 segments processed, **41 items** produced, written
incrementally as instructed. Quarantine restored afterwards: 34/34 files readable and
byte-identical to `prerun_hashes.json`; `git status` clean apart from this untracked
directory.

**Output independently re-validated, not taken on the agent's word.** The agent reported
"zero problems" from its own validator; that validator is exactly the kind of detector
Standing Principle 7 exists for, so the checks were re-run here against the *packet*
segments (never against the drafter items): span offsets reproduce `span_text` by slicing,
every `conditions` entry verbatim within its span, `action` and `object_class` inside their
own accept-sets, party values present in the segment or `ABSENT`. **41/41 items clean, 0
problems** — the agent's claim holds.

*The re-validation's own known-answer test failed on its first run, and the failure was in
the test rather than the checker*: it asserted that corrupting one record must yield ≥2
problems, but the checker `continue`s after a span mismatch, so only 1 fired. Re-run with
four independently planted corruptions (bad offsets, action outside accept-set,
object_class outside accept-set, party absent from segment) — all 4 caught. Recorded because
it is another instance of the principle it was written to satisfy: the detector-of-the-
detector failed silently on an input it did not handle.

**Cold output sealed before any comparison**, per §7 and PREREGISTRATION §7 —
`cold_manifest.json`, 50 files, rolling SHA-256
`e5d0b42a98883d43af8013e85d70a5e2d9bc60e551ea1fa46bbac62da3d87623`. Any later edit to a
`cold/` file invalidates that hash and voids the run.

**Convergent finding, worth recording because it was reached independently.** The cold
annotator, with no access to `leak_classification.json` or to this session, volunteered in
its own report that the guideline "is not blind to the other annotator's answers", listing
the segments it works through as motivating cases and noting that agreement on those is
"substantially guideline-mediated rather than independent". That is the same conclusion
PREREGISTRATION §3 reached by measurement, from the opposite direction. It names one thing
§3's detectors do not, and it is correct: the item-count and exclusion decisions are never
stated in the guideline for any segment, so they carry genuinely independent signal even on
L2 segments.

**STOPPED HERE, at the pre-registered gate.** K has not been computed. The comparison is
blocked on the cold output being committed (§7's ordering) and on the reviewer's ruling on
the amended D4 reporting shape (PREREGISTRATION §3).
