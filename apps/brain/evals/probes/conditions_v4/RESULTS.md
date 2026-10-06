# Tier-B `v4` conditions probe — RESULTS

Run 2026-10-06 against `PREREGISTRATION.md`, which was **committed before any `v4` call was
sent** (`d0ba6ec`). Nothing below changes the predicate, the thresholds or the baselines; all four
were fixed in that commit.

**Spend: 21 of the 36 approved calls. No halt, no 429, no unobtainable run, teardown clean**
(`organizations` and `users` both back to 0). Because every run was obtained, §6.1's inline
run-count disclosure does not apply to any figure here — all are modal over a full 3 runs.

---

## 1. VERDICT

| arm | pair | `v3` baseline | `v4` | verdict |
| :--- | :--- | :--- | :--- | :--- |
| `C11-094` (known-failing) | 1 | `MERGED` 2/3 — FAIL | **`CONFORM` 3/3** | **PASS** |
| `C11-094` (known-failing) | 2 | `DROPPED` 2/3 — FAIL | **`CONFORM` 3/3** | **PASS** |
| `E02-010` (**hold-out**) | 1 | `MERGED` 2/3 — FAIL | **`CONFORM` 3/3** | **PASS** |

**Rule B is ACHIEVABLE BY WORDING. `v4` conforms on 3 of 3 runs on every pair, with no instability
at all**, against a `v3` baseline that conforms on only 1 of 3 and is unstable on all three pairs.
Entry counts on the target candidates move from `v3`'s `[1,1,2,2,1,1]` / `[1,1,2]` to `v4`'s
uniform `[2,2,2,2,2,2]` / `[2,2,2]`.

**THE HOLD-OUT'S OWN `v3` BASELINE FAILS, AND THAT IS WHAT MAKES ITS `v4` PASS MEAN ANYTHING.** Had
the model conformed at `E02-010` under `v3`, the `v4` pass there would have been uninterpretable.
It does not: `MERGED` on 2 of 3. The baseline was recorded live for exactly this reason and cost 6
of the 21 calls.

**The negative control holds.** `C11-02`'s single condition — a 127-character phrase that *contains*
`within the twelve (12) month period` and could plausibly have been split — stays **one entry** on
both `v4` runs where that candidate is emitted. `v4` did not simply make the model split
everything, which is the failure mode a one-sided test would have missed.

**The OCR artifact was quoted verbatim, confirming the prediction the pre-registration made from
committed evidence.** `E02-010`'s phrase B is `upon ten (10) days prior written **3** notice from
MedQuist to CBay`, with a stray page number mid-phrase. A `CONFORM` verdict requires that string
exactly, and the predicate carried a separate `CONFORM_ARTIFACT_STRIPPED` bucket for the
normalising case. **It never fired** — the model copied the artifact rather than cleaning it, on 3
of 3 runs, exactly as `C04-117` run 2 predicted.

## 2. WHAT THE PASS LICENSES — unchanged from the pre-registration

- **Achievability, on cases selected because they fail today.** `C11-094` is §3.8.2's own motivating
  failure; conforming there shows the convention is reachable, not that it generalises.
- **`E02-010` is the only generalisation evidence and it is ONE segment.** One data point, not a
  rate, and it must not be quoted as one.
- **It does NOT license a registry flip**, which is Tier C: `prompt_version` is a
  `Cassette.verify()` staleness dimension, so activating `v4` stales **all 35** gold cassettes at
  once and `C17-021` run 3 is unobtainable (§6.1). §3's finding below is a second, independent
  reason the flip needs its own measurement.
- **The hold-out is weaker than it should have been.** `E02-010` shares `C11-094`'s `if …, upon …`
  phrase order. `C13-010` reverses it and is the better test; it was dropped only because
  `evals/registry/C13.json` does not exist (see the pre-registration's amendment).

## 3. `v4` IS NOT SIDE-EFFECT-FREE — STATED AGAINST INTEREST, AND MEASURED RATHER THAN ASSUMED

**Span selection is completely unaffected**, which is the strongest isolation result here: across
both segments the set of distinct `span_text` values is **byte-identical** between arms — 3 spans
each, **zero** `v4`-only and **zero** `v3`-only. `modality`, `action` and `object_class` likewise
match on every shared candidate.

**But `temporal_raw` moved, on a field `v4`'s text never mentions.** Nulls rise from **1 of 14
candidates (7.1%) under `v3` to 4 of 15 (26.7%) under `v4`**:

| where | `v3` | `v4` | mechanism |
| :--- | :--- | :--- | :--- |
| `E02-010`, the `MAY`/`CHARGE` candidate | `until paid in full` on **3/3** | on **1/3** | the phrase **VANISHES** — `temporal_raw: null` *and* `condition_raws: []`, so it is not relocated |
| `C11-094`, the `MAY`/`PURCHASE` candidate | phrase present when emitted | null on 1 of 2 emissions | the phrase is **ABSORBED into the condition entry** instead |

**Two different mechanisms, which is why they are tabulated apart.** A drop loses a stated timing
phrase outright — the direction §8.6.1 names as the correctness-bug direction for a compliance
tool. An absorption keeps the words but files them under the wrong field.

**Scope limits that cut the other way, stated so the finding is not inflated:**

- **The effect does not touch a single target candidate.** The two `MUST`/`TRANSFER` duties at
  `C11-094` keep their `temporal_raw` byte-identically in **6 of 6** candidate-runs across both
  arms. Every affected candidate is an adjacent **`MAY`** clause — a right, not a duty.
- **Attribution is SUGGESTIVE, NOT ESTABLISHED.** n is 14 and 15 candidates; this project has
  documented temperature-0 non-determinism since the eval pilot, and candidate counts are unstable
  in **both** arms (`v3` `[2,3,2]`/`[2,2,3]`, `v4` `[3,3,2]`/`[2,3,2]`), so instability is
  pre-existing rather than introduced. A 3/3 → 1/3 shift at this n points one way without settling
  it.
- A plausible mechanism exists and is **not** confirmed: `v4`'s paragraph names `upon`,
  `in the event of`, `where`, `subject to` and `to the extent` as condition markers, which may pull
  timing-ish phrases toward `condition_raws` and away from `temporal_raw`. The `C11-094` absorption
  fits that; the `E02-010` outright drop does not.

**Consequence, and it is the practical one: the §10 freeze pass must measure `temporal_raw` as well
as `conditions` before flipping `v4`.** Filed as a queue row rather than left in this file.

## 4. RULE A — ANSWERED AT ZERO SPEND, AND THE QUESTION WAS MIS-SCOPED

Replayed from the committed `v3` cassettes at `C04-117`: the model emits
`provided that amounts owed…` — Rule A's convention, **no leading `further`** — on **3 of 3 runs,
byte-identically**, and emits gold's `further provided that` form **zero** times.

So the probe question was never *"can the prompt be worded to produce Rule A's convention"*. The
model produces it unprompted and always. It is *"does gold conform to Rule A"*, and `C04-01`
— locked at **v0.28**, four versions before Rule A existed, so §10.2's reach-back does not apply
— does not. **A `v4` wording could only have made this worse**, and §3.8.2 had already considered
and rejected exactly that change for exactly this case, as *"fitting the model to an accident"*.

**The fix is gold-side conforming at the §10 freeze pass, not a prompt change.** Rule A was
therefore excluded from the live arm, and `v4` says nothing about it.

## 5. WHAT WAS NOT TOUCHED — verified, not asserted

- `registry.yaml` is **byte-unchanged** (`extraction: default: v3`), confirmed by `git diff`.
- **No gold cassette** was written, re-recorded or staled; probe cassettes live under
  `evals/probes/conditions_v4/{v3,v4}/`.
- **No gold item** was created, edited or restamped — including for the hold-out, which has no gold
  item and was not given one.
- `prompts/extraction/v3.yaml` is unmodified; `v4.yaml` is a new file, and its
  `model_constraints` are byte-identical to `v3`'s, so no behavioural difference here is
  attributable to a model or temperature change.

## 6. PROCESS DEFECTS FOUND AND FIXED WHILE BUILDING THIS, both Standing Principle 7's shape

1. **The dry run wrote mock cassettes to the LIVE output path.** `_already_good()` verifies on
   segment, model, prompt and guideline version — all of which matched — so the live run would have
   reported every run `SKIPPED` and recorded **nothing**, while looking like a clean success. Found
   by listing the output directory after the dry run, not by reading the code. Dry runs now write
   under `_dryrun/`.
2. **The first guard against that was blind to the artifacts it was written for.** It keyed on a
   `"MOCK"` string in `span_text` that had been added *after* the nine mock cassettes were already
   on disk, so it reported "guard would fire: False" over nine files it should have caught. Replaced
   with a structural test (`responses[0].json.id == "dry"`) and **verified RED against all nine**
   before being trusted.
