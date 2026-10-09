# Batches 5-6 cassette recording pass — results

Approved 2026-10-09: pass cap **80**; sub-caps **38 / 38 / 12**; three sessions in
that order; `E02-006` recorded at **v0.64**, so `E02-02` fails F16's per-item
check **by design** and is **not restamped**.

Pre-registration (tiers, reading rule, expected failures) was committed in
**`162fe22`**, **before any live call**, and is not restated here so it cannot
drift from the committed version.

---

## Spend ledger

Authoritative file: `_spend.json`. The pass cap is enforced **across
invocations**, because `record.Budget` is per-process and the three sub-caps sum
to 88 against a cap of 80.

| entry | guideline | recording calls | note |
| :-- | :-- | --: | :-- |
| `pre-session` | — | 1 | withdrawn TPM probe (below) |
| `session1` | v0.68 | 29 | 15/15 invocations, 0 failed |
| `session2-PARTIAL` | v0.65 | 11 | crashed on a 400 after 6 invocations |
| `session2-RESUME` | v0.65 | 1 | approved plain resume; 6 skipped, second 400 on the same call |

Pass spend **42 / 80**. Session 2's sub-cap has 26 left: per the reviewer's
ruling a resumed session's sub-cap is **not** refreshed (38 - 12), so a sub-cap
bounds the SESSION and not the attempt.

---

## FINDING 1 — the ledger silently understated real spend by 11 calls

**The defect.** `session2`'s `httpx.HTTPStatusError` propagated out of `main()`
and **skipped `save_spend` entirely**. The file still read **30** while true
spend was **41**.

**Why it matters more than the number.** On resume, the effective cap is
computed *from the ledger*. Against a stale 30 the driver would have granted a
further 38 calls, so the pass could have reached **79 real calls while believing
it had spent 68** — the cap would have been **nominal rather than true**, and
nothing in the run would have said so. A cap that is enforced against a figure
the crash path declines to write is not an enforced cap.

**How it was found.** By reconstructing spend from the artifacts rather than
trusting the ledger: summing `len(responses)` over every cassette on disk, plus
the one failed call. `record.py` charges in a `finally` precisely because a
400'd call still consumed tokens and rate limit, so the failed call **is** real
spend and is counted.

**Fixed.** A fatal HTTP error is now caught **in the loop**, so `save_spend`
always runs; the ledger merges rather than replaces (an earlier version's
session-1 write **erased** the `pre-session` provenance while leaving the total
correct — a ledger whose arithmetic reconciles and whose history is gone still
looks right); and a resumed session's prior spend is charged to **the same
session's sub-cap** (reviewer ruling: 38 − 11 = 27), so a sub-cap is
per-SESSION and not per-ATTEMPT.

**Family.** This is the project's recurring shape reached through a ledger: a
status/record that looks authoritative while measuring something other than what
is being asked. Standing Principle 7's family, via an accounting file.

---

## FINDING 2 — two 400s, from two different causes, and only one is the model's

### 2a. The withdrawn TPM probe — MY defect, 1 call

`groq.complete()` **hardcodes** `response_format: {"type": "json_object"}`. A
probe sending `system="ping", user="ping"` therefore asks for no JSON, the model
answers in prose, and Groq's **server-side** validation rejects the completion
with a 400. Tokens are consumed before that validation runs, **so the call is
not free**.

Read as "the key is revoked" or "the catalogue changed" it would have halted the
session wrongly — the catalogue check had already passed (11 models, model
PRESENT). **A 400 is evidence about the REQUEST before it is evidence about the
provider.**

**Withdrawn rather than repaired.** TPM is now read from
`x-ratelimit-limit-tokens` on the **first real recording call**, which
`TokenWindow.observe_ceiling()` already does for every call, and asserted
immediately after the first `RECORDED` run. Zero extra calls, same header, same
mechanism that caught 8,000-not-12,000 at stage 4. The gate was verified
**two-sided** against a mock: 8000 passes, 6000 halts after one invocation.

### 2b. `C04-144` run 2 — the `C17-021` class, NOT my defect

Raised inside `extract_candidates`, i.e. the real pipeline's own extraction
call, on a byte-identical request to one that had already recorded cleanly.
This is the failure mode already on record for `C17-021`: Groq returns
`json_validate_failed` with an **empty** `failed_generation` when reasoning
tokens exhaust the completion budget (measured at 85% of all completion tokens
across the stage-4 set).

**The body was not captured on the FIRST occurrence** — `HTTPStatusError`'s
message carries only the status line — so that attribution rested on the call
site, the status and the precedent. The driver was changed to print
`exc.response.text`, and **the approved plain resume returned it verbatim**:

```
{"error":{"message":"Failed to validate JSON. Please adjust your prompt. See
'failed_generation' for more details.","type":"invalid_request_error",
"code":"json_validate_failed","failed_generation":""}}
```

`failed_generation` is **empty**, which **confirms the class from this run's own
response** rather than by precedent.

### 2c. The segment is STRUCTURALLY MARGINAL, not stochastically unlucky

Quantified from `C04-144`'s own successful run-1 cassette:

| | |
| :-- | --: |
| prompt tokens | 1,783 |
| completion tokens | **3,072** (provider default ceiling) |
| reasoning tokens | **2,749 — 89.5%** |
| left for content | **323 — a 10.5% margin** |

`groq.complete()` sends **no `max_tokens`**, so 3,072 is the provider/model
default, not a project setting. Run 1 cleared it with a 10.5% content margin;
run 2's reasoning trace consumed the whole budget and left nothing, which is
exactly what an empty `failed_generation` reports.

`C04-144` is at the **97.4th percentile** of pool segment length (1,787 chars
against a median of 563), carries **3 redaction markers**, and is F28's own
disjunction case.

**This inverts the `C17-021` reading.** There, two runs succeeded and the third
failed three times, so the failure looked stochastic. Here **two consecutive
400s on a byte-identical request** say the failure is the normal outcome and
**run 1 was the lucky draw**. A retry is therefore not expected to help, which
is why the halt was reported rather than looped.

### 2d. The TPM gate DID NOT RUN on the resume, and the summary line looks like it did

`assert_tpm_or_halt()` fires after the first **`RECORDED`** run. The resume
produced 6 `SKIPPED` and then the fatal, so **no recorded run existed and the
gate never executed**. The session summary nonetheless printed
`ceiling_observed=12000`, which is **`BOOTSTRAP_TPM`** — a pre-read guess, not
a measurement — because `observe_ceiling()` is reached only after
`groq_provider.complete()` RETURNS, and here it raised.

**A session that records nothing never checks TPM, and prints a plausible
number anyway.** Standing Principle 7's exact shape, in a gate of my own
making: the catalogue gate ran and passed, so the session looked fully gated
when half of it had not run. The honest statement for the resume is
**"catalogue verified, TPM not measured"**.

### 2e. One fatal segment blocked EIGHT unrelated invocations

The loop is run-major (`for run: for segment:`) and the fatal handler `break`s
out of the whole session, so `C04-174`, `E01-004`, `E03-022` runs 2-3 and
`C04-033` run 3 were never attempted. None of them involves `C04-144`.

**No parameter was changed to force the recording through.** `C17-021`'s
precedent is explicit: a cassette recorded under different parameters is not
comparable with the others, trading one data point for a confound across the
set. The resume re-sends the identical request, which is what `C17-021` itself
did.

**A 400 cannot loop:** `record.py`'s `continue` is reachable only from
`except RateLimited`, so `MAX_ATTEMPTS_PER_RUN` bounds 429 retries only.

---

## Integrity of what was written

Every cassette written was verified against **each item's own**
`guideline_version` (F16's per-item mechanism, not a run-level version):
**35 verifications, 0 stale** at the point of the halt. Session 1's 8 items
verify on 3/3 runs. Session 2's survivors were valid but short of §6's
three-run requirement, which the resume completes.

Guarantee 2 held through the crash: 6 cassettes were on disk and complete.
Teardown was clean on every session (orgs created = orgs removed).

---

# RESULTS (read 2026-10-09, before any commit)

## Spend — 63 of 80, every sub-cap respected

| entry | guideline | calls | outcome |
| :-- | :-- | --: | :-- |
| `pre-session` | — | 1 | withdrawn TPM probe (my defect, finding 2a) |
| `session1-attempt1` | v0.68 | 29 | 15/15 recorded |
| `session2-attempt1` | v0.65 | 11 | 400 → crashed at 6/15 |
| `session2-attempt2` | v0.65 | 1 | 400 again, same call → halted, body captured |
| `session2-attempt3` | v0.65 | 12 | isolated; 7 recorded, 4 segments to 3/3 |
| `session3-attempt1` | v0.64 | 9 | 3/3 recorded |

Session totals against sub-caps: **29/38**, **24/38**, **9/12**. Zero 429s.
Teardown clean on every session. **TPM independently MEASURED at 8,000 from
real `x-ratelimit-limit-tokens` headers in all three sessions** and never once
reported from `BOOTSTRAP_TPM`.

## Recording outcome

10 of 11 segments at **3/3**. `C04-144` at **1/3** under §6.1, run 3 not
attempted, **no request parameter changed**.

## Cassette integrity — 0 anomalies

16 items verify on 3/3; `C04-10`/`C04-11` verify on their single run;
**`E02-02` stale on `guideline_version` ONLY**, exactly as stated in advance.
16 + 1 + 2 = 19 registry-backed items, all accounted for.

## BOTH CRITERION-2 FIGURES MOVED, AND BOTH MOVED DOWN

| | before | after |
| :-- | :-- | :-- |
| scored items | 15 | **33** |
| cassette-unscoreable (G8) | 54 | **36** |
| **in-force criterion 2 (§9.1)** | 5/10 = 50.0% | **6/18 = 33.3%** |
| all-items (NOT the criterion) | 7/15 = 46.7% | **9/33 = 27.3%** |

`33 + 36 = 69`, and the `+18 / -18` is exactly the 19 registry-backed items
**minus `E02-02`**, which stays unscoreable by design. Every `5/10 = 50.0%` and
`7/15 = 46.7%` in the record is a **dated figure from here on**.

**The direction is the safe one** for §3.6's monotone-widening hazard: the
denominators nearly doubled while the numerators rose by 1 and 2. This pass
bought *evidence*, not a better number — which is what it was for.

**`E02-01` is one of the six in-force numerator members**, so the reviewer's
v0.64 ruling delivered a new numerator item directly. The in-force numerator is
`C02-01`, `C02-02`, `C02-03`, `C03-01`, `C03-03`, `E02-01`.

## Pre-registration — all three Tier-1 predictions CONFIRMED

| item | modal | runs | failed clauses | verdict |
| :-- | :-- | :-- | :-- | :-- |
| `C04-15` | MISSED | 3/3 MISSED | **none** | **confirmed** |
| `C17-03` | MISSED | 3/3 MISSED | **none** | **confirmed** |
| `C14-09` | MISSED | MISSED/PARTIAL/MISSED | `obligor`, `obligee`, **`conditions`** | confirmed **+ one finding** |

`C04-15` and `C17-03` show an **EMPTY** failed-clause list, and that absence
**is** the predicted mechanism: `UNMAPPABLE_TEMPORAL` rejects the WHOLE
candidate, so nothing aligns and there are no clause-level failures to report.
Both carry `known_gaps: []`, so both sit **in** the in-force denominator and
contribute **zero** to its numerator — the cost F25's and F28's notes priced in
advance, now realised and measured.

**`C14-09` is the pass's ONE genuine finding outside a pre-registered cause.**
F14 is confirmed on **both** party slots, as predicted; `conditions` was not
predicted. Per the reading rule fixed in `162fe22`, that single clause is the
only thing in this pass the word "finding" applies to — and "REGRESSION" applies
to nothing, since no Tier-1 item failed outside its named cause in any other way
and Tier 2 has no predictions to regress from.

### Tier 2 — findings, no predictions

- **`E02-01`: FULLY_CORRECT on 3/3, stable** — the denominator-relevant item the
  v0.64 choice was made to serve.
- `C04-13`, `E01-05`: `FULLY_CORRECT`/`PARTIAL`/`PARTIAL` → modal **PARTIAL**,
  unstable (`object_class`+`conditions`; `obligor`).
- `C04-10`: **MISSED at n=1**, whole-candidate-rejection shape.

## §6.1 worked end to end, and its one divergence is now LIVE

G5 discloses three short-run items by id with the reason inline: `C04-10` and
`C04-11` at 1 run, `C17-01` at 2. `run_scoring` accepted n=1 **only** because
the `SHORT_RUN_REASONS["C04-144"]` entry exists — without it it raises rather
than rendering a silent gap.

**The divergence, unresolved and awaiting a ruling:** §6.1 says such an item is
*"always counted unstable"*, but `modal_outcome` computes
`unstable = len(set(outcomes)) > 1`, so at n=1 it returns **`unstable=False`**
(verified by execution). `C04-10` and `C04-11` are therefore reported **stable
off a single run**, which asserts more than the evidence supports and rounds in
the pipeline's favour — the one thing §6.1 says not to do. The clause is
textually bound to §6.1's n=2 tie-break sentence, so the code does not violate
the rule as written; §6.1 simply never contemplated n=1. Changing
`modal_outcome` would alter the scoring instrument, so it is not changed here.

`C04-11` is simultaneously in **G9's forced-choice class** and at **n=1**, so
its clause 2 is both a forced choice between near-misses and a single-run
observation. Neither caveat is visible without reading both G5 and G9.

## Instability is high and is the headline risk, not the figures

**13 of 33 items are UNSTABLE across runs.** Among them, three items
(`C02-01`, `C02-02`, `C02-03`) share one segment and all three read
`MISSED / FULLY_CORRECT / FULLY_CORRECT` — a single run-1 divergence moving
three items at once. Independent evidence that §6's 3× requirement is
load-bearing rather than ceremonial.

## A THIRD instance of the ledger defect class — aggregate right, row lost

After the merge fix, **both resumes wrote the same `session2-RESUME` key**, so
the second (12 calls) overwrote the first (1). The **total stayed correct at 54**
while the breakdown summed to 53. The consequence was live, not cosmetic:
`prior_spend_this_session(2)` read 23 instead of 24, so the sub-cap would have
granted **15 remaining when only 14 were**. Fixed to one key per ATTEMPT, lost
row restored, and an explicit `session2_total` field added.

**The pattern across all three instances is specific and worth naming:
AGGREGATE CORRECTNESS MASKS ROW LOSS.** No total-based check can catch it,
because the total is the thing that stays right.

## My verifier's `DO NOT COMMIT` was ITS OWN defect

It classified `C04-144` as an expected short run and then flagged **that
segment's items** as `UNEXPECTED` for the very runs it had just said would not
exist. An expected absence reported as an anomaly is as misleading as the
reverse: it buries the one genuine finding among known ones. Fixed; the true
anomaly count is **zero**.
