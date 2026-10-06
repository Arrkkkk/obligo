# Tier-B `v4` conditions probe — PRE-REGISTRATION

**Written and committed BEFORE any `v4` call was sent.** Everything below — the segments, the
conform predicate, the thresholds, the `v3` baselines and the call cap — is fixed here so none of
it can be adjusted once results are known. This is §7's pre-registration discipline applied to a
prompt probe.

**Authority.** Guideline §10.1 **F31(1)**: §3.8.2's Rules A and B were written at v0.33, four
months before the 2026-08-29 §7 run, and §3.8.2 still says of itself that *"neither rule is
validated against model behaviour"* and *"neither may be assumed to fix anything"*. F31(1) makes
this probe the gate on further conditions-heavy annotation. Reviewer-approved scope and cap.

---

## 0. RULE A NEEDS NO LIVE CALL, AND THIS IS THE ANSWER RATHER THAN A DEFERRAL

Rule A says a condition quote begins at the qualifier's own marker — `provided that`, not
`further provided that`. Its motivating failure is `C04-01`, whose gold entry reads
*"**further** provided that amounts owed…"* against a model emission of *"provided that amounts
owed…"*: 97.8% string similarity, clause-7 failure.

**Replayed from the committed `v3` cassettes at `C04-117`, the model already emits Rule A's
convention on 3 of 3 runs, byte-identically, with no leading `further`.** So:

- The probe question for Rule A was **mis-scoped**. It is not *"can the prompt be worded to
  produce Rule A's convention"* — the model produces it unprompted and always. It is *"does gold
  conform to Rule A"*, and `C04-01` (locked at **v0.28**, four versions before Rule A existed)
  does not.
- **No `v4` wording can improve this and one could only make it worse.** A prompt change here
  would be fitting the model to gold's own arbitrary choice — which §3.8.2 explicitly considered
  **and rejected** for this very case (*"fitting the model to an accident"*).
- **The fix is gold-side conforming at the §10 freeze pass, not a prompt change.** Rule A is
  therefore **excluded from the live arm** and `v4` says nothing about it.

**Zero calls are spent on Rule A.** Its answer is a replay result, recorded in `RESULTS.md`.

---

## 1. WHAT THE LIVE ARM TESTS — RULE B ONLY

**Rule B:** adjacent conditional phrases are separate entries, one per syntactically distinct
phrase, even when juxtaposed with only a comma and no conjunction.

### Segments

| # | segment | role | why |
| :-- | :--- | :--- | :--- |
| 1 | **`C11-094`** | the known-failing case | §3.8.2's own motivating failure. Carries **TWO** Rule-B pairs **and one single-condition control**, so it is two-sided within one segment. |
| 2 | **`E02-010`** | **HOLD-OUT** | Clean Rule-B pair, outside the gold set, not used to draft `v4`, and not imitated by `v4`'s worked example. |

**AMENDMENT, made BEFORE any `v4` call was sent and recorded rather than silently applied.** The
hold-out was first specified as **`C13-010`**, which is the *better* case: it reverses the phrase
order (`Upon …, if …` against `C11-094`'s `If …, upon …`), so it tests the rule rather than a
surface pattern. **A dry run with a mock transport — zero spend — rejected it: `_seed_document()`
requires a committed §21 R3 scoring registry per document, and `evals/registry/C13.json` does not
exist.** `C13` is one of the five documents CLAUDE.md's proactive sweep already names as
registry-less. Authoring one mid-probe is scope creep with a figure-moving risk that would need its
own verification, so the hold-out moved to a registry-backed document.

**The cost of that substitution is stated rather than glossed: `E02-010` shares `C11-094`'s phrase
order (`if …, upon …`), so it is a WEAKER generalisation test than `C13-010` would have been.** It
still tests different documents, different parties, a different duty and a different modality, and
the `v4` worked example imitates neither. `C13-010` remains the better hold-out and is blocked only
on an authoring task.

**A second disclosure, because it could have produced an uninterpretable result: `E02-010`'s
second phrase contains an OCR artifact — `upon ten (10) days prior written 3 notice from MedQuist
to CBay`, with a stray page number mid-phrase.** If the model silently normalised it the entry
would not be a verbatim substring, the grounding gate would discard the candidate, and a
corpus defect would be indistinguishable from a Rule-B failure. **The risk is judged acceptable on
committed evidence rather than on hope:** at `C04-117` run 2 this same model and prompt family
quoted the page-header artifact *"27 Miltenyi Biotec-Bellicum Supply Agreement (Execution Copy,
March 27, 2019)"* **verbatim, mid-phrase, inside a `condition_raws` entry**. The model copies
corpus noise rather than cleaning it. The predicate below nonetheless **records the exact emitted
string**, so a normalisation failure stays distinguishable from a merge or a drop.

`E07-010`, named in the originally-approved three, is **dropped with a reason**: replayed from its
committed cassettes it emits `condition_raws: []` on **3 of 3** runs across all candidates, so it
tests neither Rule A nor Rule B but a **third** thing — whether non-`if` conditions are emitted at
all. That is a different question from entry *count* and does not belong in this arm.

### Targets, quoted from the committed gold items

- **`C11-094` pair 1** (`C11-01`, v0.28) — `["If the Principal is a natural person", "upon the
  death or mental incapacity of a Principal"]`
- **`C11-094` pair 2** (`C11-03`, v0.55) — `["In the case of transfer by devise or inheritance",
  "if the heir is not approved or there is no heir"]`
- **`C11-094` control** (`C11-02`, v0.53) — `["If the conveyance of the Principal's interest to a
  party acceptable to BKC has not taken place within the twelve (12) month period"]`, a **single**
  entry. Splitting it is a FALSE POSITIVE.
- **`E02-010` hold-out pair** — `if payment is not received in full when due` /
  `upon ten (10) days prior written 3 notice from MedQuist to CBay`. **No gold item exists for this segment and none is being
  created**; the pair is read off the sentence, and the expected annotation under Rule B is two
  entries.

### Conform predicate — exact, and three-valued rather than binary

For a pair `(A, B)`, take the emitted `condition_raws` of the candidate whose span covers that
sentence, whitespace-normalised and case-sensitive:

- **`CONFORM`** — the list contains `A` and `B` as two separate entries.
- **`MERGED`** — the list contains one entry equal to `A` + `,` + `B` (the comma-joined string).
- **`DROPPED`** — the list contains exactly one of `A` or `B` and not the other.
- **`OTHER`** — anything else, including no candidate at that span. Counted as non-conforming.

`MERGED` and `DROPPED` are kept apart because **`v3` fails the two pairs in different ways** (see
§2), and a wording that converts a `DROPPED` into a `MERGED` has changed behaviour without
conforming. Collapsing them would hide that.

### Pass threshold — §6 with §6.1's fallback

- **3 runs per (segment, prompt)**, modal outcome per §6.
- A pair **PASSES** iff its modal outcome over the recorded runs is `CONFORM` — i.e. **≥2 of 3**.
- **Ties resolve to the WORST observed outcome** and the pair is counted unstable (§6.1, as
  amended at v0.30 to match `report.py`'s G2 — never round in the pipeline's favour).
- If a run is **unobtainable** (the `C17-021` failure mode), report over the runs that exist and
  **state the run count and reason inline wherever the figure appears** — §6.1, never a footnote.
- **No request parameter may be altered to obtain a missing run** (§6.1's third clause).

### What a PASS licenses, and what it does not

Reviewer-stated and adopted verbatim: **a pass shows ACHIEVABILITY on known-failing cases only.**

- `C11-094` is selected *because it fails today*, so conforming there shows the convention is
  **reachable by wording** — not that it generalises.
- **The hold-out is the only generalisation evidence, and it is ONE segment.** A pass there is a
  single data point, not a rate, and must not be quoted as one.
- A pass **does not** license a registry flip. That is **Tier C**: `prompt_version` is a
  `Cassette.verify()` staleness dimension, so activating `v4` stales **all 35** gold cassettes at
  once and `C17-021` run 3 is unobtainable (§6.1). The flip waits for the §10 freeze pass.
- A **FAIL** is equally informative and is not a reason to redraft and re-run: a second wording
  tried against the same case is tuning, which is what §3.8.2 refused for Rule A.

---

## 2. `v3` BASELINES — FIXED HERE, TAKEN FROM COMMITTED CASSETTES, ZERO SPEND

Replayed from `evals/cassettes/gold/C11-094/run{1,2,3}.json` (`prompt_version: v3`,
`model openai/gpt-oss-120b`, temperature 0.0):

| pair | run 1 | run 2 | run 3 | conform | `v3` modal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `MERGED` | `CONFORM` | `MERGED` | **1/3** | **NON-CONFORM** |
| 2 | `DROPPED` | `CONFORM` | `DROPPED` | **1/3** | **NON-CONFORM** |

Pair 2's `v3` failure is a **DROP**, not a merge: runs 1 and 3 emit only
`["if the heir is not approved or there is no heir"]` and lose
*"In the case of transfer by devise or inheritance"* entirely. §3.8.2 records the 2:1 instability
but not that the two pairs fail by **different mechanisms** — noted here before `v4` runs.

**The hold-out has no cassette, so its `v3` baseline must be RECORDED LIVE.** Without it a `v4` pass
on the hold-out is uninterpretable — the model might conform there under `v3` anyway. The baseline
is therefore part of the arm, not an optional extra.

---

## 3. BUDGET AND HALT

- **Hard cap: 36 model calls**, enforced by `record.Budget` in code rather than by counting.
  Exhaustion is checked at the START of each run, so a run already paid for is always written
  (guarantee 2).
- **Planned spend ≈ 19 calls** at the measured 2.09 calls/invocation (9 invocations). Repair calls
  count against the cap.
- **Execution order is chosen so an early halt still yields an interpretable result:**
  1. `v4` × `C11-094` × 3 — the achievability answer
  2. `v3` × `E02-010` × 3 — the hold-out baseline
  3. `v4` × `E02-010` × 3 — generalisation
- **On cap exhaustion: HARD HALT.** Everything written stays; the run does not resume without
  explicit reviewer approval.

## 4. WHAT IS NOT TOUCHED

- `registry.yaml` is **byte-unchanged** (`extraction: default: v3`), verified by `git diff`. The
  probe **injects** `v4` directly.
- **No gold cassette is written, re-recorded or staled.** Probe cassettes live under
  `evals/probes/conditions_v4/`, outside the gold set.
- **No gold item is created, edited or restamped**, including for the hold-out.
- `prompts/extraction/v3.yaml` is unmodified; `v4.yaml` is a new file (prompts are immutable).
