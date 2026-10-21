# F34 temporal-interaction probe — RESULTS

Run **2026-10-21** against `PREREGISTRATION.md`, **committed before any `v4` call was sent**
(`d49378d`, cap revised to 18 at `adabe90`). Nothing below changes the predicate, the buckets, the
thresholds, the control criterion or the baselines; all five were fixed in those two commits.

**Spend: 12 of the 18 approved calls** — `v4 × C04-017` `[2,2,2]` and `v4 × C17-006` `[2,2,2]`,
read from the cassettes rather than from a tally. **No halt, no 400, no 429, no unobtainable run,
no retry loop, no parameter change, teardown clean.** Every run was obtained, so §6.1's inline
run-count disclosure does not apply to any figure here — all are modal over a full 3 runs.
Both `v3` baselines and the whole control arm are **committed cassettes at zero spend**.

---

## 1. VERDICT — REFUTED

| arm | modal bucket | runs |
| :--- | :--- | :--- |
| baseline `v3 × C17-006` | `QUARANTINED_SAME` | 3/3 |
| baseline `v3 × C04-017` | `QUARANTINED_SAME` | 2/3 **UNSTABLE** (`SPAN_NOT_FOUND` on run 2) |
| **TARGET `v4 × C17-006`** | **`QUARANTINED_SAME`** | **3/3** |
| **TARGET `v4 × C04-017`** | **`QUARANTINED_SAME`** | **3/3** |

Per §4 — **REFUTED** iff `QUARANTINED_SAME` is the modal bucket on **both** targets — the
**hazard verdict is REFUTED**, and it is **persisted in `_scored.json`** (`hazard_verdict`, with
`hazard_verdict_basis` naming each target's modal) rather than left on stdout. The verdict was
re-derived independently from that file, not read off the scorer's printed line.

**The mechanism §10.4.4 feared does not occur on these two segments.** `v4` quotes the `During …`
phrase on **6 of 6** target runs, byte-identically to `v3`:

- `C17-006` → `During the applicable Term of any Service`
- `C04-017` → `During the Term of this Agreement`

So the candidate still hits `UNMAPPABLE_TEMPORAL`, is still quarantined, and **never reaches the
`None == None` clause-6 pass** by which a dropped period would have raised criterion 2 while the
pipeline silently discarded a stated timing phrase.

## 2. CONTROL — HOLDS, AND IT IS CHECKED FIRST

`C11-01`, both arms: **IoU 1.000 on 3/3**, `temporal_raw` byte-identical under `v3` and `v4`
(`within a reasonable time after the Principal's death or mental incapacity`), **clause 6 True on
all six runs**. Per §5 this is **CONTROL HOLDS**: `v4` does not drop a timing phrase on a duty the
IR can represent.

**The control-first gate caught a defect in the scorer at zero spend.** Its first version pushed
the control through §3's *target* bucket set and returned `OTHER` 3/3 for a candidate that had in
fact compiled with its temporal intact. §5 defines the control criterion separately and the code
had not implemented it; fixed, and a `v3` control baseline arm added, **before any live call**.
A control failure would have outranked a target confirmation (§5), so an instrument that could not
express `CONTROL HOLDS` could not have been trusted on the targets either.

## 3. WHAT THE RESULT LICENSES, AND WHAT IT DOES NOT

- **It removes F34's own stated blocker.** §10.4.4's interaction was the reason the flip was not
  scheduled; on these two segments it does not occur, with the control holding.
- **It is NOT a flip decision and none is made here.** The result is **two segments at n=3** — an
  observation on the cases selected *because* they are the null-gold quarantined ones, not a rate
  and not a safety claim about `v4` generally.
- **`INDETERMINATE` was a real available outcome and did not occur** (§4). No second wording was
  drafted, and none would have been: that is the tuning §3.8.2 refused for Rule A.
- **F14 remains UNPROBED.** No segment here exercises it — the only cassette-backed segment with a
  gold `obligor: ABSENT` item is `C14-095`, deliberately out of scope (§7). The bundled F14 + `v4`
  candidate would still ship that half unvalidated unless `C14-095` is probed or it is accepted
  unprobed. F14's measured numerator value is **zero** (§10.4.3 finding 2); zero value is not zero
  risk.

## 4. INCIDENTAL OBSERVATIONS — n=3, NOT THIS PROBE'S QUESTION

Recorded because they are visible in the cassettes, labelled so they are not read as findings:

- **`C04-017` is MORE stable under `v4`**: `v3` lost run 2 to `SPAN_NOT_FOUND`; `v4` grounded on
  all three.
- **`C17-006` stopped narrowing.** Under `v3`, run 3 produced `During the applicable Term` after
  **two** repair calls (`[2,2,3]`); under `v4` all three runs keep the full phrase at one repair
  call each (`[2,2,2]`).
- Call counts: `v3` `[2,2,3]` / `[2,1,2]` = 12, `v4` `[2,2,2]` / `[2,2,2]` = 12.

## 5. GATES, IN THE ORDER THEY RAN

| gate | result |
| :--- | :--- |
| `git ls-remote` vs local `HEAD` | matched (`f669d669`) — pre-registration pushed before any call |
| pool rebuild | 1,547 segments, both targets present |
| `registry.yaml` | byte-unchanged, `extraction: default: v3` (`v4` is **injected**, not activated) |
| **control-first instrument gate** | ran before any live call; **caught and forced the scorer fix above** |
| dry run | **recorded=6, skipped=0**, written to `_dryrun/` only |
| mock guard | verified **two-sided**: `True` on all 6 dry artifacts, `False` on a real gold cassette, and `refuse_stray_mocks()` **fired** on a planted one |
| model catalogue | via the project's own **httpx** path (not `urllib`): 11 models, `openai/gpt-oss-120b` **PRESENT** |
| TPM | **MEASURED 8,000** from real `x-ratelimit-limit-tokens` headers — not `BOOTSTRAP_TPM` |
| write scope | probe root only; no gold cassette written, re-recorded or staled |

## 6. WHAT IS NOT TOUCHED

`registry.yaml` byte-unchanged at `extraction: default: v3`. **No gold cassette written or staled**
(gold root holds **66**, unchanged). No gold item created, edited or restamped. No tag minted. **No
published figure moved: in-force criterion 2 `6/18 = 33.3%`, all-items `9/33 = 27.3%`.** The `v4`
flip remains **Tier C** and unapproved. Batch 7 remains held.
