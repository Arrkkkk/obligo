# §7 cold second-annotator check — pre-registration

**Fixed 2026-08-29, before any cold annotation was compared against any draft.** Bands,
leak classification, seeds and reporting shape are all recorded here in advance. Nothing
below may be revised once K is known; a revision after that point is a different document
with its own date and its own statement of what changed and why.

**Baseline:** 32 items / 22 segments / 3 batches. Guideline `v0.41` (DRAFT, not frozen).
Batch 1 = 10, batch 2 = 8 (2 undrawn, §19.4), batch 3 = 14.

---

## 1. What this is, and what it is not

§7 as written specifies **prospective** blinding: 2 of 10 items per batch withheld *at draw
time*, so the reviewer never sees them. **That never happened for any batch**, and cannot be
recovered retroactively. There is no `gold/holdout/` anywhere in the repo's history; all 32
items are individually reviewer-signed-off (24 carry `adjudicated_by: reviewer`, 2 carry
`reviewer_status: RULED_BY_REVIEWER`, all 32 are `APPROVED`).

**What is being run is therefore a one-sided check: the cold annotator is blind to the
drafts; the reviewer is blind to nothing.** Calling the result "held-out" would be false.
It is a **cold second-annotator check**, and every published use of K must say so.

K therefore now carries **three** disclosures, not §7's one:

1. **Correlated error** (§7's own, unchanged) — the cold annotator shares a model family,
   and therefore priors, with the drafter. K is a lower bound on the disagreement rate a
   genuinely independent annotator would produce, not an estimate of it.
2. **No reviewer blinding** — the reviewer adjudicated every item in the set being checked.
   §7's 5-item spot-check loses its stated purpose ("keeps the reviewer's own eyes on items
   where the two annotators agreed"); those eyes are not fresh.
3. **Guideline leakage** — see §3 below. The guideline is the cold annotator's required
   input and it states the answers for most of the set.
4. **Order-dependence within the cold pass** (added 2026-08-29, after the run, before K).
   The cold pass was not a single internally-consistent sweep: it settled an `upon <X>`
   question at segment 4 (`C13-017`) and then went back and revised segment 2
   (`C17-021`) to match, so segments annotated before that point were annotated under an
   understanding the annotator had not yet formed. **Stated as a limitation, but explicitly
   not assumed to bias K in either direction** — it is arguably the same shape as the
   drafters' own history, where 32 items were annotated across many sessions while the
   guideline grew from v0.12 to v0.41 and items were conformed backwards (§10, §19.3).
   Both sides evolved their understanding mid-build and retro-fitted earlier work. The
   honest reading is that this makes the two annotators *more* comparable in process, not
   less, and that any residual effect is of unknown sign.

**One thing is better than §7's design, and only one:** because nothing was filtered out of
the pool at draw time, this sample is **not** systematically easier than the gold set.
§14.4's own accepted easiness bias does not apply.

## 2. Decisions taken (reviewer-ruled 2026-08-29)

| | Decision |
| :-- | :--- |
| **D1** | **Census** over all 32 items / 22 segments — not a 20-of-32 draw. §3's leak caps the uncontaminated subgroup regardless of N, so a fixed-budget subset would spend effort on pre-contaminated items while leaving clean ones unexamined. |
| **D2** | **§14.4's pool filter is suspended.** Its only purpose is protecting blindness that §1 establishes no longer exists; applying it would reintroduce easiness bias for no remaining benefit. |
| **D3** | **Draw unit is the segment; item count per segment is withheld** from the cold annotator. Revealing it would hand over the §4.3 / §4.3.1 / §4.3.2 splitting decision — three of the last seven guideline versions. Pairing is by §4.1's IoU ≥ 0.5 and §4.2's tie-break, the project's existing machinery, not a new rule. |
| **D4** | Leak classification committed alongside the draw record; K reported by leak level with every N stated inline. **Amended before the run** — see §3. |
| **D5** | Verdict bands per §4 below, fixed in advance. |

## 3. Leak classification — method, validation, result

Two detectors. Full per-item output with line numbers and verbatim rationale in
`leak_classification.json`.

**Detector 1 — content leak, ID-independent.** Normalise whitespace; test whether any
12-gram of an item's `span_text` occurs in the guideline, falling back to 8-gram then
6-gram. Catches the severe case a citation search misses: a worked example that quotes the
segment *without naming the ID*.

*Validated against known ground truth before its output was trusted* (Standing Principle 7):
`E07-01` (§3.8.2's table), `C04-139`→`C04-04`/`C04-05` (§4.3.2), and `C13-017`→`C13-01`
(§2.6) are all known worked examples and all returned leaked, as they must. The loosest
6-gram tier fired on exactly 2 items (`C17-01`, `E07-01`), both manually confirmed genuine
quotes — no false positives at the tier most likely to produce them.

**Result: 20 of 32 items have `span_text` quoted verbatim in the guideline.**

**Detector 2 — ID-citation grading**, applied to the 12 items detector 1 clears. Extract
every guideline line matching the item ID **or** its segment ID — both keys are required,
since `C22-048`/`E01-047` are uncited *segments* whose items are cited 4 and 8 times — then
read each citation and grade:

- **L2** — states the span, multiple scored fields, or the splitting decision.
- **L1** — states ≥1 scored field, or a segment-level disposition that implies one.
- **L0** — named in a bookkeeping context only; no scored field stated.

Item level is the max over its citations. **L1 counts as leaked** (conservative: a partial
leak still contaminates the field it names).

| Level | N | Items |
| :-- | --: | :--- |
| **L0** | 3 | `C03-03`, `C05-01`, `E08-01` |
| **L1** | 3 | `C02-02`, `C03-01`, `C10-02` |
| **L2** | 26 | all others |

**D4 is amended here, before the run, and the amendment is recorded rather than made
silently.** D4 was ruled on an estimate of ~10 leak-free items, which came from citation
*counts* — a crude prior, labelled as one at the time, and wrong. Reading the citations
gives 3. A K over N=3 supports no inference whatever (K=0/3 has a Wilson₉₅ upper bound of
0.56), so "report leak-free K prominently" is not deliverable as ruled.

**Replaced by: K reported at all three leak levels as a gradient, each with its N inline,
plus a fourth channel — the item-count and exclusion decisions.** (Fourth channel adopted
2026-08-29, before K, on the cold annotator's own unprompted observation, which converged
with §3's detectors from the opposite direction: the guideline names these segments as
worked cases and quotes their spans and field values, but **it never states, for any
segment, how many gold items that segment yields or which of its clauses were excluded.**
That decision is therefore uncontaminated *even on L2 items*, and it is the channel D3's
withheld item count was designed to test. It matters disproportionately here because the
L0 subgroup is N=3.)
This is something a census can deliver and a 20-item draw could not. A flat profile is weak
evidence the leak is not doing work; a profile rising as leak severity falls is evidence the
headline K is optimistic, and triggers the escalation in §4. The L0 figure is reported as an
anecdote with N=3 on its face and is never called an estimate.

## 4. Verdict bands (D5)

**§7's own stated power figure was checked as a known-answer test before deriving
anything.** *"Catches a ≥15% error rate ~82% of the time"* reproduces exactly:
P(K≥2 | n=20, p=0.15) = 0.824. Its second claim, *"is a coin flip at 10%,"* **does not
reproduce** under either band boundary — P(K≥2 | p=0.10) = 0.608 and P(K≥4 | p=0.10) =
0.133, neither ≈ 0.5. Recorded as a correction to §7; it does not affect the bands.

**A census has no sampling error.** K/32 is the *exact* disagreement rate over the locked
set. The Wilson interval is needed only for the extrapolation question — what rate this
process produces for items 33–100 — and since PROCEED/DIAGNOSE/REDESIGN is a decision about
whether to continue the build, that is the question these bands govern.

**Derivation: preserve §7's evidential strength** (the Wilson₉₅ lower bound at each
trigger), not its raw counts.

| §7 trigger | Wilson₉₅ lower | smallest K/32 clearing it |
| :--- | ---: | :--- |
| DIAGNOSE, K≥2/20 | 0.0279 | **K=3** (0.0324; K=2 gives 0.0173) |
| REDESIGN, K≥4/20 | 0.0807 | **K=6** (0.0889; K=5 gives 0.0686) |

An independent rate-preserving derivation agrees: §7's 10% DIAGNOSE floor is 3.2 of 32, its
20% REDESIGN floor 6.4 of 32. The two agree exactly at DIAGNOSE and bracket REDESIGN at
6–7. **6 is taken**, the earlier trigger, because the costs are asymmetric — a false
REDESIGN costs re-annotation, a missed one costs the gold set's validity.

| K / 32 | rate | Verdict |
| :--- | :--- | :--- |
| **0–2** | ≤6.3% | **PROCEED** — report K/32 with its Wilson CI; claim no rate below 6% |
| **3–5** | 9.4–15.6% | **DIAGNOSE** — §7's branch unchanged: clustered (≥2 on one field/rule) → fix the rule, log a re-check across all locked items, re-run cold on a disjoint set, proceed iff K₂ ≤ 1. Diffuse → treat as ≥6 |
| **≥6** | ≥18.8% | **REDESIGN** — re-annotate under a revised guideline *and* a changed process |

**Power at N=32**, stated as §7 states its own: P(K≥3) = 0.878 at a true 15%, 0.633 at 10%,
0.214 at 5%. Going 20→32 buys little. **This remains a tripwire, not an estimator**, and is
near a coin flip around 8%. It must be reported as one.

**Escalation rule, one-directional.** If the §3 leak gradient shows disagreement rising as
leak severity falls, the verdict escalates exactly one band. It can never de-escalate — the
leak biases toward agreement, so the gradient can only reveal the headline K as optimistic,
never as pessimistic.

**K counts disagreements, not confirmed drafter errors** (§7, unchanged) — if adjudication
finds the cold annotator wrong, it still counts. Item-level, not field-level. A cold value
inside the drafter's accept-set is not a disagreement; a defensible value outside it is. A
segment where the two annotators produce different item *counts* is a disagreement on the
unmatched items, since the splitting decision is exactly what D3 exists to test.

## 5. Seeds

| | |
| :--- | :--- |
| `SEED1` | **29082026** — reviewer-supplied. Orders the 22 segments (`random.Random(SEED1).sample(sorted_segment_ids, 22)`), per §2.1's rule that the reviewer holds the seed. |
| `SEED2` | **2223141222** — derived by the stated rule `int(sha256(b"29082026").hexdigest()[:8], 16)`, for the post-comparison 5-item spot-check draw. Reproducible, no drafter discretion. |

The census runs in seeded segment order so that **a truncated run is still a valid seeded
random sample** rather than an alphabetical one. The three L0 items sit at ranks 10, 13 and
19, so a truncated run still reaches two of them.

## 6. Blinding enforcement — prevention, not detection

**An earlier proposal to audit the subagent's tool log for reads under `goldens/*/items/`
was withdrawn as unrunnable, and the fallback was tested rather than assumed.** A
subagent's tool output does not reach the orchestrating session — only its final report
does. The `atime` fallback is also dead: `cat` on a quarantined item file left `atime`
unchanged (`Aug 28 11:43:55` before and after) on this sealed APFS volume.

What is run instead:

1. `chmod 000` on `batch0{1,2,3}/items/`, `batch01/segments/`, and **`batch01/SUMMARY.md`**
   — that last one tabulates `modality`, `action` and `known_gap` for all ten batch-1 items
   and was nearly missed. Directory modes are untracked by git, so the working tree stays
   clean and the restore is exact.
2. **The safeguard is given its own known-answer test before the agent starts** — reads are
   attempted and confirmed to fail. A safeguard not watched failing is not evidence.
3. The cold annotator's working directory is a scratchpad packet dir that is not a git repo.
4. The packet is built by **field allowlist** (`segment_id`, `doc_id`, `stratum`,
   `segment_text`), never a denylist — a denylist silently leaks any field added later, and
   this schema has grown (`obligor_accept_set`, `adjudicated_by`). The generator asserts no
   disallowed key survives into any packet file.
5. Restore afterwards, verified by SHA-256 of all 34 quarantined files against
   `prerun_hashes.json`, plus a clean `git status`.

**Residual gap, stated rather than papered over:** the files remain in git objects, so
`git show HEAD:<path>` from inside the repo would still recover them. That requires two
deliberate acts and cannot be observed from here. The cold annotator is additionally asked
to list every file it read; that is recorded as a **self-report, not verification**.

## 7. Ordering discipline

Per §7, the cold annotations are **committed and hashed before** any comparison is run. The
sequence is: pre-registration (this document) → packet → cold pass → hash and commit the
cold output → *only then* compute K. Nothing in this document may change after the third
arrow.
