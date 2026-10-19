# F34 temporal-interaction probe — PRE-REGISTRATION

**Reviewer-approved 2026-10-19: Option B — `C04-017`, `C17-006`, `C11-094` as control; cap 27;
cap REVISED to 18 on 2026-10-19; halt and resume only on reviewer approval. NO CALL HAS BEEN MADE. This document is committed and
pushed BEFORE any call so that nothing in it can be adjusted once results are known** — the
`d0ba6ec` precedent, and §7's discipline applied to a prompt probe.

**The reviewer confirms after reading this and before the first call.**

---

## 0. WHAT THIS PROBE TESTS, AND WHAT IT CANNOT

It tests **one mechanism**, named in guideline §10.4.4 and given its exact target strings by the
2026-10-10 quarantine investigation:

> `score.py` computes clause 6 as `g_t == p_t`, so **`None == None` PASSES**. `C04-15` and
> `C17-03` carry gold `temporal: null` and are quarantined by `UNMAPPABLE_TEMPORAL` on precisely
> the phrase gold omits. So `v4`'s **measured `temporal_raw` drop** could convert those
> quarantines into **passes** — raising criterion 2 by having the pipeline silently discard a
> stated period, which is §8.6.1's named correctness-bug direction.

**It is NOT a general evaluation of `v4`.** The conditions probe (`../conditions_v4/`) measured
Rule B achievability; this measures one side effect of the same candidate wording on two segments
selected **because** they are the only cassette-backed in-force items whose gold temporal is
`null` and whose candidates are quarantined on a `During …` phrase.

---

## 1. THE HYPOTHESIS, AS A MECHANISM RATHER THAN A DIRECTION

Under `v3`, measured on the committed gold cassettes (quarantine investigation §2b):

| segment | `temporal_raw`, verbatim | outcome |
| :--- | :--- | :--- |
| `C04-017` | `During the Term of this Agreement` (on BOTH the `SUPPLY` and `PURCHASE` candidates) | `UNMAPPABLE_TEMPORAL` → quarantined |
| `C17-006` | `During the applicable Term of any Service` (runs 1-2); `During the applicable Term` (run 3, after two repair calls) | `UNMAPPABLE_TEMPORAL` → quarantined |

All three strings classify to `None` through the production `_classify_temporal()`, verified by
execution with a two-sided known-answer gate (`tests/evals/test_quarantine_investigation.py`).

**If `v4` drops the phrase**, the candidate carries `temporal_raw: null`, the classifier is never
asked, the candidate compiles, and clause 6 compares `None` to `None` and **passes**. The item
can then score `FULLY_CORRECT` — **bought by the pipeline discarding a stated period**.

---

## 2. ARMS — AND THE LIVE HALF IS SMALLER THAN THE APPROVED CAP WAS SIZED FOR

**Measured before sizing, not assumed: every `v3` baseline AND the whole control arm already
exist as committed cassettes, so they cost ZERO calls.**

| arm | source | live calls |
| :--- | :--- | --: |
| `v3` × `C04-017` × 3 | `evals/cassettes/gold/C04-017/run{1,2,3}.json` (prompt `v3`, guideline `v0.68`) | **0** |
| `v3` × `C17-006` × 3 | `evals/cassettes/gold/C17-006/run{1,2,3}.json` (prompt `v3`, guideline `v0.68`) | **0** |
| **control** `v4` × `C11-094` × 3 | `../conditions_v4/v4/C11-094/run{1,2,3}.json` (prompt `v4`, guideline `v0.66`) | **0** |
| `v4` × `C04-017` × 3 | **LIVE** | 3 invocations |
| `v4` × `C17-006` × 3 | **LIVE** | 3 invocations |

**So the live arm is 6 invocations, not the 9 the Option-B cap was sized against.** At stage 4's
measured basis (2.0857 calls/invocation, sd 0.6490) that is **13 expected, 17 at +3sd, and 18 as
the absolute ceiling** if every invocation takes the maximum 3 calls.

**DISCLOSED RATHER THAN SILENTLY BANKED: the approved cap of 27 therefore CANNOT BIND.** It is
set to 27 in code exactly as ruled and will not be exceeded — but a cap 50% above the arithmetic
ceiling is not a live halt mechanism, and a future reader should not mistake "the cap was
respected" for "the cap was tested". **If the reviewer wants a binding cap, 18 is the ceiling and
17 is +3sd.** The sizing is not changed unilaterally.

**REVISED 2026-10-19 BY THE REVIEWER: THE CAP IS 18, NOT 27.** Recorded as dated new text rather
than by editing the paragraph above, so the reasoning that produced the first figure stays
readable. **And a better basis than the global mean is now available, measured rather than
inherited: THE SAME SIX INVOCATIONS COST EXACTLY 12 CALLS UNDER `v3`** — read off the committed
gold cassettes' own `responses` arrays, `C04-017` `[2, 1, 2]` and `C17-006` `[2, 2, 3]`. That is
a **segment-specific** figure for the identical invocations, where the 13 above is the
28-document-corpus mean applied to a count of 6. **18 is therefore +50% over the directly
comparable measurement.**

**The control arm's cassettes carry `guideline_version: v0.66`** against the targets' `v0.68`.
That is **provenance only here**: `score_probe.py` reads cassettes with plain `json.loads` rather
than through `cassette.load()`/`verify()`, so no staleness dimension is consulted, and the
guideline governs scoring conventions rather than anything in a model request. Stated because a
mixed stamp is fatal in the gold-scoring path (F16) and is not in this one.

---

## 3. THE PREDICATE — CANDIDATE-LEVEL, AND THE REASON IS F37

Measured per `(segment, run, candidate)` on the candidate whose span best covers the gold span,
**not** per gold item. **`C04-14` and `C04-15` have BYTE-IDENTICAL gold spans `[23:363]`**
(verified by reading both items), which is §10.1 **F37**'s group: `align()` sorts on
`(-iou, gold_id, pred_start)` and reads no item content, so a single emitted candidate pairs to
`C04-14` **lexicographically regardless of content**. An item-level predicate at that segment
would therefore measure a pairing accident. Buckets:

- **`QUARANTINED_SAME`** — `temporal_raw` still carries a `During …` phrase; candidate is
  quarantined with `failure_reason == UNMAPPABLE_TEMPORAL`. The status quo.
- **`DROPPED_AND_COMPILED`** — `temporal_raw` is `null`/absent, the candidate reaches
  `PipelineResult.typechecked`, and its `temporal` is `None`. **The hazard, confirmed.**
- **`DROPPED_AND_FAILED_OTHERWISE`** — phrase gone, candidate still never reaches `typechecked`
  (any other rejection or quarantine cause).
- **`ABSORBED`** — the phrase, or a substring of it, appears in `condition_raws` instead. This is
  the mechanism the conditions probe actually observed at `C11-094`, so it is a named bucket
  rather than an `OTHER`.
- **`NARROWED_STILL_UNMAPPABLE`** — `temporal_raw` carries a *different* phrase that
  `_classify_temporal()` still returns `None` for. `C17-006` run 3 under `v3` is exactly this
  shape after two repair calls, so it is attested and must not fall into `OTHER`.
- **`NOT_EXTRACTED`** — no candidate emitted at the span.
- **`SPAN_NOT_FOUND`** — a candidate WAS emitted and the grounding gate rejected it.
- **`OTHER`** — anything else.

**`NOT_EXTRACTED` and `SPAN_NOT_FOUND` are kept apart deliberately**, applying the quarantine
investigation's own third finding: the production miss diagnosis conflates them, and `C04-017`
run 2 under `v3` is a real instance (both candidates emitted, both `SPAN_NOT_FOUND`, reported as
`NOT_EXTRACTED@IoU0.000`). Collapsing them here would reproduce the defect the investigation
found.

---

## 4. THRESHOLD — THREE-VALUED, AND `INDETERMINATE` IS A REAL VERDICT

- **3 runs per (segment, prompt)**; modal outcome per §6, **ties resolving to the bucket least
  favourable to the flip** (§6.1 as amended at v0.30 — never round in the pipeline's favour).
- **CONFIRMED** iff `DROPPED_AND_COMPILED` is the modal bucket on **either** target segment.
- **REFUTED** iff `QUARANTINED_SAME` is the modal bucket on **both** target segments.
- **INDETERMINATE** otherwise — including any mix of `ABSORBED`,
  `NARROWED_STILL_UNMAPPABLE`, `DROPPED_AND_FAILED_OTHERWISE`, extraction and grounding failures.
  **An `INDETERMINATE` result must NOT be reported as refutation**, and it does not license the
  flip; it says the mechanism was not observed on these two segments, which is a weaker claim.
- If a run is **unobtainable** (the `C17-021`/`C04-144` failure mode), report over the runs that
  exist and **state the run count and reason inline wherever the figure appears** (§6.1).
- **No request parameter may be altered to obtain a missing run** (§6.1's third clause). A second
  wording is **not** tried if the first produces `INDETERMINATE`: that is tuning, which §3.8.2
  refused for Rule A.

---

## 5. CONTROL CRITERION — AND A CONTROL FAILURE IS THE MORE SERIOUS FINDING

`C11-094` carries `C11-01`, whose gold `temporal` is **non-null**
(`RELATIVE_TO_TRIGGER(after, …)`) on a `MUST`/`TRANSFER` duty. It is the one cassette-backed
in-force item where `v4` **must not** drop a timing phrase.

- **CONTROL HOLDS** iff, on ≥2 of 3 `v4` runs, `C11-01`'s aligned candidate retains a
  non-empty `temporal_raw` **and** its clause-6 outcome matches the `v3` arm's.
- **CONTROL FAILS** otherwise.

**A control failure is a worse result than a target confirmation and outranks it.** A target
confirmation says `v4` turns a known-unrepresentable period into a vacuous pass; a control
failure says `v4` **loses a stated deadline on a duty the IR can represent**, which is
§8.6.1's correctness-bug direction landing on a faithful item. **Either outcome argues against
scheduling the flip**, and a control failure argues against it regardless of what the targets
show.

**Stated so the control is not oversold: it is a ZERO-SPEND re-derivation of something already
measured once.** The conditions probe reported the two `MUST`/`TRANSFER` duties at `C11-094`
keeping `temporal_raw` byte-identically in **6 of 6** candidate-runs across both arms. What is
genuinely new is that this probe computes the **pipeline outcome** — compile and clause 6 —
where that probe measured only the emitted field, and it does so under **this** document's
predicate rather than citing another probe's prose. That is real but modest, and the control is
accordingly **unlikely to fail**; its value is that a failure would be loud rather than that a
pass is informative.

---

## 6. BUDGET AND HALT

- **HARD CAP: 18 MODEL CALLS — REVISED 2026-10-19 BY THE REVIEWER FROM 27.** Enforced by
  `record.Budget` in code rather than by counting. **At 18 the cap STOPS BEING HEADROOM AND
  BECOMES A STRUCTURAL ASSERTION, which is the substantive effect of the revision rather than
  mere tightening.** 6 invocations x a maximum of 3 calls each is **exactly 18**, and 3 is a
  structural per-invocation ceiling rather than an observed maximum: one extraction call plus at
  most `max_repairs = 2` repair calls, **with repair calls BATCHED ACROSS CANDIDATES rather than
  issued per candidate** — verified against the artifacts, not assumed, since `C04-017` run 1
  quarantines **two** candidates that both carry `repair_calls=[1]`, i.e. one shared call, and
  `C17-006` run 3 is the two-repair-call case at `repair_calls=[1, 2]`. **So the cap cannot be
  exceeded unless one of those documented invariants is false, and if `BudgetExhausted` ever
  fires it is evidence of that rather than of an over-spend.** The old 27 could not fire for a
  duller reason — it simply sat 50% above the ceiling.
- *(Superseded, left as written: "Hard cap: 27 model calls (reviewer-approved)", enforced by `record.Budget` in code rather
  than by counting.)*
- Exhaustion is checked at the START of each run, so a run already paid for is
  always written.
- **Planned spend: 12 calls**, the measured `v3` cost of these same six invocations (§2's dated revision); 13 is the global-mean estimate it supersedes. Repair calls count against the cap — and
  repair is expected here, since `C17-006` run 3 under `v3` spent two.
- **Execution order, chosen so an early halt still yields an interpretable result:**
  1. `v4` × `C17-006` × 3 — the cleaner target: ONE gold item, no byte-identical span group, and
     `UNMAPPABLE_TEMPORAL` on 3 of 3 under `v3`
  2. `v4` × `C04-017` × 3 — two candidates per run and an F37 span group, so it is read second
- **On cap exhaustion: HARD HALT.** Everything written stays; **the run does not resume without
  explicit reviewer approval**, per the ruling.
- **The mandatory pre-spend model-catalogue check runs first** (the 2026-08-22 retired-model
  incident is why it is mandatory). **TPM is read from `x-ratelimit-limit-tokens` on the FIRST
  REAL recording call** and asserted immediately after it — never from a dedicated probe call,
  which the batches 5-6 pass proved is not free, and never from `BOOTSTRAP_TPM`, which that same
  pass proved reads exactly like a measurement when no call has landed.

---

## 7. F14 IS NOT PROBED HERE, AND THE FLIP WOULD CARRY IT UNVALIDATED

The 2026-10-10 ruling bundles **F14 and `v4` into ONE candidate and ONE re-record**, so the
Tier C staling event is spent once. **This probe tests `v4` alone.**

- F14's defect is that `prompts/extraction/v3.yaml` carries one worked example with an empty
  `obligee_alias` and **no obligor counterpart**, measured at `obligor_alias` empty in **0 of 81**
  emitted candidates (Wilson₉₅ upper 4.53%).
- **No segment in this probe exercises it.** The only cassette-backed segment with a gold
  `obligor: ABSENT` item is **`C14-095`** (`C14-09`), and it is deliberately out of scope.
- **Consequence, stated rather than left to be found: if the bundled candidate is flipped at the
  freeze pass on the strength of this probe plus the conditions probe, the F14 half ships
  UNVALIDATED.** Closing that needs either a third probe at `C14-095` or an explicit reviewer
  decision to accept it unprobed. **F14's measured numerator value is zero** (§10.4.3 finding 2),
  which is why it has no claim on urgency — but zero value is not the same as zero risk, and a
  prompt change nobody probed is a prompt change nobody probed.

---

## 8. CONFOUNDS DISCLOSED IN ADVANCE

- **Temperature-0 non-determinism is pre-existing, not introduced.** This project has documented
  it since the eval pilot; the conditions probe found candidate counts unstable in **both** arms.
  A bucket changing between runs is therefore not by itself evidence of a `v4` effect, which is
  why the verdict is modal over 3 runs rather than any-run.
- **n is small and is stated as such.** Two target segments, 6 live invocations. A `CONFIRMED`
  verdict is evidence about these two segments and is **not** a rate.
- **F37's span group at `C04-017`** is handled by the candidate-level predicate (§3) and is
  **not fixed here** — porting the tie-break into `align()` changes the scoring instrument.
- **`C04-017` carries two gold items of which only `C04-15` is in the in-force denominator**
  (`C04-14` carries `compound_action`, a `REPRESENTATIONAL` kind). A flip at `C04-14` moves no
  published figure; a flip at `C04-15` does. Both are reported; only the second is priced.

---

## 9. WHAT IS NOT TOUCHED

- `registry.yaml` stays **byte-unchanged** at `extraction: default: v3`, to be verified by
  `git diff`. The probe **injects** `v4` by patching the loader, exactly as the conditions probe
  does.
- **No gold cassette is written, re-recorded or staled.** New probe cassettes land under
  `evals/probes/temporal_v4/`, outside the gold set.
- **No gold item is created, edited or restamped. No tag is minted.** F41 stays open.
- **No published figure moves by this probe.** In-force criterion 2 is `6/18 = 33.3%` and
  all-items `9/33 = 27.3%`; a probe records evidence and scores no gold item.
- `prompts/extraction/v3.yaml` and `v4.yaml` are both unmodified (prompts are immutable).
