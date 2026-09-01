# `object_class` — investigation of REDESIGN scope item 1 (§3.6's missing specificity convention)

**Run 2026-08-30, against the sealed cold output (`cold_manifest.json`, rolling SHA-256
`e5d0b42a…d87623`), the 32 locked gold items, and the 35 gold cassettes.** Nothing here
changes a rule, restamps an item, or invalidates a cassette. **No rule is proposed** — the
REDESIGN response's own discipline is that a precedent-setting convention is investigated
before it is drafted, and this note is the investigation half only.

Companion to `RESULTS.md`, whose Finding 2 this note takes apart. It does not supersede it:
Finding 2's counts are reproduced exactly and its 7–0 direction is confirmed. What changes is
the **diagnosis**, and therefore what a fix would have to be.

---

## 0. Reproduction, and the known-answer check on it

`RESULTS.md` Finding 2 was recomputed from source rather than quoted. The pairing was rebuilt
independently — per-segment greedy maximum-IoU alignment at the §4.1 threshold of 0.5 — and
`object_class` pairs classified by strict token-subset relation, with §5's v0.33 number rule
applied on both sides.

| | Finding 2 | this reconstruction |
| :--- | ---: | ---: |
| matched pairs | 31 | 31 |
| identical labels (number-normalized) | 13 | 13 |
| strict-subset pairs, cold more generic | 7 | 7 |
| strict-subset pairs, cold more specific | 0 | 0 |
| orthogonal | 11 | 11 |

**Standing Principle 7 check on the reconstruction itself.** The first pass returned 12/7/12,
not 13/7/11 — the discrepancy was `retained_sample`/`retained_samples`, which is identical
under §5's number rule and differing without it. The mismatch against a *known* published
answer is what surfaced that the normalizer had been omitted. Recorded because it is the
principle working as intended: the script was wrong in a way that looked entirely plausible
(19 differing pairs instead of 18) and was caught only by comparison against an established
number, not by re-reading the code.

The seven: `C02-03` `C06-01` `C10-01` `C10-02` `C13-01` `C17-02` `E07-01`.

> **CORRECTION, 2026-08-30 — §0's reproduction above is WRONG, and it is struck rather than
> edited.** The table and its "reproduces exactly" claim are kept as the dated record they
> were; this block is the correction, found while investigating the depth rule (§9).
>
> **My pairing script had two defects that cancelled.** (1) It did not implement **§4.2's
> v0.36 content tie-break**, so `C04-139`'s two items — which have *byte-identical* spans, the
> exact case that tie-break was written for — were paired arbitrarily and reported as an
> `object_class` disagreement (`self_compliant_use` ↔ `third_party_compliant_use`). **The two
> annotators in fact agree exactly on both items**, matching on action as well
> (`USE`/`USE`, `ENSURE`/`PROCURE`, both within gold's `action_accept_set`). (2) The
> strict-subset test ran on **raw** tokens while the identity test ran on **number-normalized**
> ones, so `withholding_tax`/`taxes` was filed orthogonal instead of nested.
>
> **Corrected counts on the pre-v0.44 items, under the guideline's own rules (§4.2 tie-break,
> §5 number normalization): identical = 15, nested = 8, orthogonal = 8.** The nested set gains
> **`C14-01`** (`withholding_tax` / `taxes`), so the direction is **8–0, not 7–0** — *still zero
> the other way*.
>
> **RESULTS.md's own Finding 2 counts (13 / 7 / 11) are not reproducible from the sealed data
> either**, under any of four interpretations I ran; the closest is 14 / 7 / 10 (raw identity,
> correct pairing). Finding 2 states it files number-only pairs such as
> `retained_sample`/`retained_samples` as *orthogonal*, i.e. it does not apply §5's v0.33 number
> rule at all — which is a different convention from the one the guideline mandates. Its script
> was not preserved. A correction entry is filed in `RESULTS.md` rather than editing Finding 2.
>
> **What does NOT change, checked rather than assumed.** **K is untouched** — it is computed
> from `comparison.json`'s per-clause `disagree` field (14 disagreeing items, verified), not
> from Finding 2's label classification, and `comparison.json`'s own alignment pairs `C04-139`
> correctly (neither item is marked disagreeing). The **REDESIGN verdict stands**. §3's
> clause-5 analysis is unaffected (it reads `comparison.json`'s `fails`, not my pairing); §5's
> breadth measurements are unaffected (they do not depend on pairing at all); §2's model
> evidence is unaffected. The **four-mechanism decomposition below is unaffected in substance**
> and gains one item: `C14-01` joins mechanism **(D)**, which becomes 3 items, since both
> `withholding taxes` and `taxes` appear literally in its span.
>
> **This is the fifth instance of Standing Principle 7 in this workstream and the first in my
> own published output.** The reproduction *matched a known published answer*, which is exactly
> the check the principle prescribes — and it matched because two errors cancelled. **A
> known-answer check passing is evidence only when the answer it matches is itself verified**;
> here the reference number was not independently sound, so agreement with it proved nothing.

---

## 1. The seven are not one phenomenon — a four-mechanism decomposition

Read individually, with both annotators' slot values, both accept-sets, both recorded
reasonings, and the object noun phrase each label was built from, the seven separate into four
mechanisms that have almost nothing in common except the direction of the token-subset
relation. **"Specificity" names the symptom, not the mechanism.**

### (A) Head noun vs head noun + material from elsewhere in the span — 2 items

Gold's extra token is not in the object noun phrase at all.

| item | gold | cold | the object NP |
| :--- | :--- | :--- | :--- |
| `E07-01` | `on_site_personnel` | `personnel` | *"personnel"* |
| `C17-02` | `contract_consent` | `consent` | *"any needed consent"* |

`E07-01`'s span is *"…TIBCO shall maintain **personnel** at any of the Covered Sites."* The
object NP is one word. `on_site_` is gold's inference from the prepositional adjunct *"at any
of the Covered Sites"* — true, and not part of the thing the duty is about grammatically.
`C17-02` is the same shape: the NP is *"any needed consent"*, and `contract_` is drawn from
the surrounding *"Multi-party Contract"*. Cold's note records considering and rejecting even
the in-NP modifier (`needed_consent`), so it is not simply truncating — it is anchoring on the
head.

**Adjudication: cold is more faithful to the object phrase; gold imports adjunct material.**
Neither is *wrong* — gold's labels are more informative and both are true of the obligation —
but they are not derivable from the phrase either the cold annotator or the model quoted.

### (B) Material from outside the span entirely — 1 item

| item | gold | cold | the object NP |
| :--- | :--- | :--- | :--- |
| `C02-03` | `retention_costs` | `costs` | *"the costs associated with performing these activities"* |

The span is *"Antares shall invoice AMAG for the costs associated with performing these
activities"*. `retention_` requires resolving the anaphor *"these activities"* back to the
retained-sample duties stated in **sibling sentences of the segment**. Cold's note records
running §3.6's enum-1 anchor test and correctly finding a single nominal anchor.

**Adjudication: gold is over-specified relative to its own span.** This is a stronger claim
than (A) — the label is not merely built from the wrong part of the span, it is not
reconstructible from the span at all.

### (C) Whole-clause nominalization that duplicates other scored fields — 2 items

| item | gold | cold | what gold's extra tokens encode |
| :--- | :--- | :--- | :--- |
| `C10-01` | `product_liability_indemnification` | `liability` | `_indemnification` restates `action = INDEMNIFY` (clause 2) |
| `C10-02` | `distributor_insurance_certificate_listing` | `insurance_certificate` | `distributor_` restates `obligee` (clause 4); `_listing` restates the act (clause 2) |

`C10-02`'s span is *"The Supplier shall add the distributor to their current insurance
certificate."* Gold's label is a nominalization of the whole clause. Cold takes the literal
object NP in both cases.

**Adjudication: gold over-specified, and this is the one sub-pattern that is arguably a
defect rather than a convention gap.** `object_class` is carrying information that clauses 2
and 4 already score. That is not a stylistic preference between two faithful readings — it is
a field holding another field's content, which makes the conjunctive predicate double-count a
single correct or incorrect judgment.

**These are the only two of the seven that actually fail clause 5**, and they fail in the
hardest way available: neither accept-set contains the other's label, in either direction.
`C10-01`'s four-member set retains `indemnification` or a two-word qualifier in every entry,
so it has **no generic pole at all**.

**Both are batch 3, stamped v0.40** — the newest items in the set, authored *under* §3.6's
full v0.33 required enumerations. Whatever this is, it is current practice, not a legacy
artifact the existing rule has already fixed.

### (D) Truncation depth inside one literal object phrase — 2 items

| item | gold | cold | the object NP |
| :--- | :--- | :--- | :--- |
| `C06-01` | `adequate_assurance_of_future_performance` | `adequate_assurance` | *"adequate assurance of future performance"* |
| `C13-01` | `pertinent_records` | `records` | *"all of DD's pertinent records on MOXATAG"* |

Both labels come from the same phrase and both are verbatim. Gold keeps the whole NP or its
in-NP adjective; cold stops at the head.

**Adjudication: both defensible, and this is the only one of the four that is genuinely the
"which pole wins" question §3.6 is charged with answering.** Both pairs are symmetric — each
annotator's accept-set contains the other's label — which is the signature of two annotators
who agree the label is underdetermined and differ only on where to stop.

`C06-01` is worth naming precisely because gold cited §3.6 here and cited it correctly: its
notes invoke the v0.33 dual-anchor enumeration and author all four variants into the set. The
enumeration did its job. **It governs the set, not the slot**, and the slot is what
disagreed — which is the cleanest available demonstration that §3.6's existing rules do not
reach this question.

### Summary of the seven

| mechanism | items | adjudication |
| :--- | :--- | :--- |
| (A) outside the object NP, inside the span | `E07-01` `C17-02` | cold more faithful; gold imports adjunct material |
| (B) outside the span | `C02-03` | gold over-specified against its own span |
| (C) whole-clause nominalization | `C10-01` `C10-02` | gold over-specified; duplicates clauses 2/4 |
| (D) truncation depth in one NP | `C06-01` `C13-01` | both defensible; §3.6 states no rule |

**0 of 7 are cold under-specifying.** The 7–0 direction in `RESULTS.md` is real and is
confirmed. But what is one-directional is **where gold sources the label from**, not how
precise it is: cold and the model label the head of the object noun phrase, and gold sometimes
labels the *obligation*.

---

## 2. Model evidence — the axis behaves differently on the pipeline side

`RESULTS.md` Finding 2 is an annotator-vs-annotator measurement. The same axis was checked
against the 35 gold cassettes, reading `object_class` **and** `object_raw_text` out of the
recorded response bodies, so the phrase the model built each label from is visible rather than
assumed.

**Evidence coverage is partial and that bounds everything in this section.** Only 12 segments
were recorded (§stage-4 recording run). Of the seven, **4 have no model evidence at all**
(`C06-01`, `C13-01`, `C10-01`, `C10-02` — `C06-016`, `C13-017`, `C10-016` were never
recorded). Of the six clause-5 failures, `C10-01`, `C10-02` and `C22-02` have none.

**On the specificity axis the model sides with cold, stably:**

| segment | `object_raw_text` | model `object_class` | gold slot | runs |
| :--- | :--- | :--- | :--- | :-- |
| `E07-010` | *"personnel"* | `personnel` | `on_site_personnel` | 3/3 |
| `C17-066` | *"any needed consent"* | `consent` | `contract_consent` | 3/3 |
| `C02-021` | *"the costs associated with performing these activities"* | `costs` / `invoice_costs` | `retention_costs` | 2/2 aligned |
| `C11-094` | *"the Principal's interest in Franchisee"* | `principal_interest` | `franchise_interest` | 3/3 |

The model's rule is discoverable and consistent: **it labels the head of the noun phrase it
quoted, plus at most one in-NP modifier.** It never reaches outside that phrase. That is
mechanism (A)/(B) restated from the other side, and it is the same rule cold followed.

**Three of these pass clause 5 only because gold's accept-set happens to carry the generic
form.** Four of the seven pass on that accident. `C11-094` does not, and is the already-queued
§3.4 widening.

**But annotator disagreement does not predict pipeline failure.** On the orthogonal clause-5
failures where cassettes exist, the model picks a *third* label:

- `E03-005` returns `order_forecast` on **all three runs** — the document's own defined term,
  which is in **both** annotators' accept-sets. It passes clause 5 while the two annotators
  disagree (`demand_forecast` vs `rolling_forecast`). Gold's own slot value is the only one of
  the three that appears **nowhere in the document text**.
- `C17-021` returns `virus_prevention` — gold's label, not cold's.

**So the annotator-agreement instrument and the pipeline-scoring instrument disagree about
which items are hard on this clause.** Neither is measuring the other.

---

## 3. `object_class` as the largest failure clause is NOT explained by specificity

`RESULTS.md`'s clause profile puts `object_class` at 6 of 23 clause failures. Of those six,
**only two are nested pairs at all** — `C10-01` and `C10-02`, i.e. mechanism (C), which is
better described as field-duplication than as specificity. The other four are on axes no
specificity convention touches:

| item | gold | cold | axis | in §3.6? |
| :--- | :--- | :--- | :--- | :--- |
| `C11-01` | `franchise_interest` | `principal_interest` | possessor vs thing-owned | **yes — enum 1's own named example**, but §3.6 is forward-only from batch 3 and this is batch 1 / v0.28 |
| `C17-01` | `virus_prevention` | `virus_introduction` | **polarity** — the duty's goal vs the thing prevented | no |
| `C22-02` | `trademark_license_grant` | `third_party_trademark_license` | **which qualifier** — the act vs the beneficiary class | no |
| `E03-01` | `demand_forecast` | `rolling_forecast` | **literal vs interpretive naming** — the text's own adjective vs an interpretation | no |

So the clause is carrying **at least five distinct failure modes**: field-duplication (C),
possessor/thing-owned, polarity, qualifier selection, and literal-vs-interpretive naming — plus
the specificity axis itself, which accounts for none of the six on its own.

### The mechanism common to four of the six is accept-set breadth, not label choice

In **all four** orthogonal failures, cold's accept-set contains gold's label while gold's does
not contain cold's. The failure is one-sided coverage, not a wrong pick.

Measured over all 31 matched pairs:

| | gold | cold |
| :--- | ---: | ---: |
| mean `object_class_accept_set` size | **3.61** | **5.35** |
| median | 3 | 5 |
| min / max | 2 / 6 | 4 / 7 |

§3.6's own text says *"3–6 plausible labels is normal."* Gold sits at the floor of its own
stated band; cold sits at the ceiling. Directional coverage over the 18 non-identical pairs:
7 symmetric, 3 gold-set-covers-cold-only, 4 cold-set-covers-gold-only, 4 neither.

**This is not a rule gap.** §3.6 already asks for what would fix it. It is an authoring-breadth
gap against an existing rule — a different kind of problem from the three rule gaps in §4
below, and it is addressed in §5.

---

## 4. Three distinct rules are missing, and they are not one ruling

Stated as findings, not proposals. Which (if any) to write, and in what order, is the
reviewer's call.

1. **A source rule.** May `object_class` be built from material outside the object noun
   phrase (`E07-01`, `C17-02`), or outside the span (`C02-03`)? Two tiers, and they are not
   equally settled — see the cost table below. Both cold and the model already behave as
   though the answer is *no* to both; gold is the outlier.
2. **A depth rule.** How much of a literal object NP to keep (`C06-01`, `C13-01`). The only
   genuine specificity question, and the one where both readings are equally defensible.
3. **A field-independence rule.** `object_class` must not encode `action`, `obligor` or
   `obligee` (`C10-01`, `C10-02`). Closest of the three to a correction rather than a
   convention.

### Cost to rule, per item — measured, and it does not follow importance

Two operational facts govern what any ruling costs, both verified directly:

- **The gold set already stamps five guideline versions** — v0.28 ×18, v0.37 ×2, v0.38 ×1,
  v0.40 ×2, v0.41 ×9 — and `run_scoring.guideline_version_from_items()` raises on more than
  one. **Only the 18 v0.28 batch-1/2 items are scoreable today**, and those are exactly the
  cassette-backed ones. All 14 batch-3 items are already outside the scoreable set.
- Conforming a **cassette-backed** item restamps it, which under `Cassette.verify()`'s
  `guideline_version` dimension makes **all 35 cassettes stale at once** — §22's blocker, with
  `C17-021` run 3 known unobtainable (§6.1). Conforming a **batch-3** item costs nothing:
  no cassette, and no effect on the 18-item scoreable set's single stamp.

| item | mechanism | batch | stamp | cassette | cost to conform |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `C10-01` | (C) field-independence | batch03 | v0.40 | **no** | **free** |
| `C10-02` | (C) field-independence | batch03 | v0.40 | **no** | **free** |
| `C06-01` | (D) depth | batch03 | v0.41 | **no** | **free** |
| `C13-01` | (D) depth | batch03 | v0.41 | **no** | **free** |
| `C02-03` | (B) source, outside-span | batch02 | v0.28 | **YES** | all 35 stale |
| `E07-01` | (A) source, outside-NP | batch01 | v0.28 | **YES** | all 35 stale |
| `C17-02` | (A) source, outside-NP | batch01 | v0.28 | **YES** | all 35 stale |

**The cost structure maps onto the mechanisms almost exactly, and it inverts the intuitive
ordering.** Field-independence (C) and depth (D) are entirely on free batch-3 items. The
source rule (A)/(B) — the one whose answer is *least* in doubt, since both cold and the model
already follow it — is entirely on cassette-backed items and is the expensive one.

---

## 5. Accept-set breadth is a separate finding, and it is not on REDESIGN's list

Recorded here as the note's own contribution, distinct from item 1 as REDESIGN scoped it.

**Why it is not the same problem as §4's three rules.** Those are missing conventions: nothing
in the guideline decides them, and the fix is to write text. Breadth is an **authoring practice
falling short of a rule that already exists** — §3.6 asks for 3–6 and gold's median is 3. No
new rule would fix it; only re-authoring would.

**Why it plausibly matters more for criterion 2 than any of them.** §5 clause 5 tests
`prediction ∈ gold's accept_set` — one-sided, implemented that way in
`evals/harness/score.py:226–231`. A **convention binds annotators**; it cannot bind the model,
which has never read the guideline and whose prompt (`prompts/extraction/v3.yaml:130–132`)
says only *"a short lowercase snake_case label"* with mixed-specificity worked examples
(`customer_personal_data`, `invoice_payment`, `deliverables`). So a §3.6 slot convention would
move annotator-vs-annotator K and change **nothing** in pipeline scoring. **Breadth is the only
lever in this cluster that acts directly on criterion 2.**

**Two hazards that make it need its own pre-registration rather than folding into rule-writing.**

- **Widening is monotone: it can only turn a clause-5 fail into a pass.** If a breadth pass
  runs between two criterion-2 measurements, the delta is uninterpretable — pipeline
  improvement and a loosened bar are indistinguishable. §3.4 already knows this shape
  (*"stops measuring whether extraction identified the action at all"*). Either the pass runs
  before the next criterion-2 baseline, or criterion 2 is reported against both the pre- and
  post-widening sets so the two effects separate.
- **Cold's 5.35 is not a target.** Cold authored one-shot, unreviewed, knowing it would be
  compared; breadth is the risk-averse move under those conditions, and nothing here shows
  cold's breadth is *calibrated* rather than merely looser. Anchoring a breadth pass on
  "match the cold median" would be fitting gold to a single unvalidated second annotator. The
  defensible anchors are §3.6's own stated 3–6 band and the span text, authored **blind to any
  prediction** — which is the distinction that keeps it inside §3.4's freeze rule rather than
  in violation of it: widening authored from the span is legitimate authoring, widening
  authored from a scoring report is prediction-fitting.

**Venue.** §3.4's bounded exception already admits widening *"during §10's pre-scheduled
conforming pass and nowhere else"*, and three items (`C02-03`, `C11-01`, `C02-01`) are already
queued there. The proposal this note supports is therefore not a new mechanism but an
**expansion of that already-scheduled pass's scope** — from three individually-queued
widenings to a systematic breadth audit — carrying the two constraints above. Doing it
piecemeal would force a conforming pass per item, which is precisely §22's blocker.

---

## 6. What this note deliberately does not do

- **No rule is drafted**, for any of the three gaps or for breadth.
- **No item is restamped and no cassette is touched.** Every measurement here is read-only.
- **The specificity axis is not declared settled.** Mechanism (D) — the only true specificity
  question — has **no model evidence at all** (`C06-016` and `C13-017` were never recorded),
  and §5's own number-rule precedent suggests a fourth possibility nobody has raised: that an
  axis neither side was ever asked about may belong in a **comparison rule** rather than an
  authoring convention. That option is named here and not argued.
- **`RESULTS.md` Finding 2 is not amended.** Its counts reproduce exactly and its 7–0
  direction stands. This note refines the diagnosis beneath it; the finding as published is
  not falsified, and per this project's corrections-are-new-text discipline it is left as
  written.

## 7. Connection to item 0 — the same crux, independently, on a second clause

REDESIGN item 0 asks whether §5 is *one predicate serving both pipeline scoring and annotator
comparison, or two predicates that happen to share eight clauses*, and reaches it through
`known_gaps` — a field the pipeline cannot emit at all.

**This investigation reaches the identical question from a clause the pipeline emits on every
single candidate**, which is why it is worth recording as independent arrival rather than as
an echo. Clause 5 is one-sided by construction: the model's label is tested against gold's
accept-set, and gold's own label is tested against nothing. Consequently:

- an authoring convention on the **slot** changes annotator-vs-annotator K and cannot change
  criterion 2, because the model never reads it;
- authoring breadth in the **set** changes criterion 2 and is largely invisible to K, because
  K compares two slot values;
- and the two instruments demonstrably disagree about which items are hard — `E03-005` passes
  the pipeline while both annotators disagree, and four of the seven nested pairs pass only
  because gold's set happened to carry the generic pole.

**Item 0's question therefore cannot be answered as a `known_gaps`-specific question.** If §5
is one predicate, then §3.6 must be written to constrain the accept-set (the thing scoring
reads) rather than the slot (the thing annotators argue about) — and the same is true of §3.4.
If it is two, then the specificity convention belongs to the annotator-comparison predicate
only, and the breadth item in §5 above is the *entire* pipeline-side finding of this
investigation. **Which of those is true determines what item 1's fix even looks like, so item
0's ordering ahead of it is confirmed by a second, independent route.**

---

## 8. Ruling log

Appended as rulings land. The investigation above is unedited — per this project's
corrections-are-new-text discipline, a ruling is recorded here rather than folded back into
the findings it came from.

### Sequence, ruled 2026-08-30

Set against the measured cost table in §4, which inverts the intuitive ordering: the rule whose
answer is least in doubt (source) is the only one landing entirely on cassette-backed items.

| # | item | status | why here |
| :-- | :--- | :--- | :--- |
| 1 | **field independence** (`C10-01`, `C10-02`) | **RULED — §3.6.1, guideline v0.44** | free (batch-3, no cassette) and closest to a defect rather than a convention |
| 2 | **accept-set breadth** (§5 of this note) | ~~HELD pending REDESIGN item 0~~ **RULED — §3.6, guideline v0.45** | promoted above the remaining rules — the only lever here that provably touches criterion 2 — but its shape depends on whether §5 is one predicate or two. **Item 0 ruled "two", which confirmed the shape rather than merely releasing the hold — see Ruling 3** |
| 3 | **depth rule** (`C06-01`, `C13-01`, and `C14-01` per §0's correction) | ~~INVESTIGATED — §9; no ruling proposed~~ **SCOPED — §3.6, guideline v0.45; convention still unwritten** | free (batch-3, no cassette). §9 finds the comparison-rule option **falsified**, the pipeline half **collapsing into row 2**, and only an annotator-side convention over three items left live. **Ruled to be `A`'s scope only — see Ruling 4** |
| 4 | **source rule**, two tiers | open, **batched into §10's freeze pass** | outside-span (`C02-03`) and outside-NP (`E07-01`, `C17-02`) are separable and only the second is contentious; all three are cassette-backed, so ruling either tier stales all 35 at once — it goes with the widenings already queued there |

### Ruling 1 — field independence → §3.6.1 (guideline v0.44)

`object_class` must not carry material whose content is already the value of clause 2
(`action`), clause 3 (`obligor`) or clause 4 (`obligee`) for the same item. Full text, both
carve-outs, and the retroactivity argument live in `docs/eval/GOLD_SET_GUIDELINE.md` §3.6.1;
what follows is only what this note contributed and what the ruling changed.

**The defect argument.** §5 is conjunctive, so a label restating the `action` makes clauses 2
and 5 co-vary — one judgment scored twice, two clauses lost for one mistake or gained for one
lucky guess. Wrong under *any* specificity convention, which is what makes it a correction and
justifies retroactivity where §3.6's own enumerations are forward-only.

**Two items corrected, v0.40 → v0.44:**

| item | slot was | slot now | removed |
| :--- | :--- | :--- | :--- |
| `C10-01` | `product_liability_indemnification` | `product_liability` | `_indemnification` = `action` |
| `C10-02` | `distributor_insurance_certificate_listing` | `insurance_certificate` | `distributor_` = `obligee`; `_listing` = the real verb *"add"* |

**Three deliberate narrowings of the rule's own reach, each forced by something measured here.**

- **Slot half retroactive, and free.** Clause 5 never reads gold's slot (`score.py:226`), so a
  slot correction has zero effect on criterion 2 and cannot fit anything to a prediction.
- **Set half widening-only.** `C04-03`'s accept-set carries `product_delivery` against
  `action = DELIVER`, and **`C04-087` run 2 emits exactly `product_delivery`**. Retroactive
  stripping would have flipped a passing clause to failing — §3.4's prohibition running in the
  more dangerous direction, since narrowing can only manufacture failures. Discovered by
  checking the cassettes before writing the rule, not after.
- **Retroactive widening confined to cassette-less items.** `C10-016` was never recorded, so no
  prediction for either item exists and the widening is provably not prediction-fitted.
  Everything cassette-backed waits for the freeze pass.

**Cost, verified rather than assumed:** no accept-set member removed, no cassette staled, no
effect on the scoreable set. Stamps moved from `{v0.28 ×18, v0.37 ×2, v0.38 ×1, v0.40 ×2,
v0.41 ×9}` to the same with `v0.40 ×2 → v0.44 ×2`; `run_scoring.guideline_version_from_items()`
already refused the 32-item set on five stamps and refuses it on five still. All 32 items
re-validated clean afterwards (span offsets reproduce, slot ∈ accept-set, action ∈ accept-set).

**Standing Principle 7, and it failed in the instructive direction.** The §10 re-check screen
matches action nominalizations by stem and **did not flag `C10-02`'s own `_listing`** — the
item's `action` is `ESTABLISH` while the real verb is *"add"* (§8.8). It was visible only
because the investigation had already found it by hand. **The screen is a lower bound, not a
census, and is structurally blind to every `action_not_in_taxonomy` item**; §3.6.1 carries that
caveat and defers a hand re-check of the §8.8 items to the freeze pass. Four further candidates
it did raise were adjudicated individually and all four cleared — `C02-01` and `C14-01` name the
object by the document's own words (*"as retained repository samples"*, *"including withholding
taxes"*), `C22-02` is prefix noise (`license` ⊂ `Licensees`), and `C04-03`'s slot is clean.

**What the ruling deliberately did not do.** The corrections strip *only* the restating tokens.
`product_liability` was not further reduced to `liability`, because that is the depth question
(row 3 above) and ruling it by side effect would have prejudiced it. A named residue is
accepted and recorded: the violating members remain in both accept-sets, so the instrument
still *admits* a field-duplicating prediction — it merely no longer *requires* one.

---

## 9. The depth question — investigation (sequence row 3)

Investigation only. **No rule is proposed**, and the finding is partly that one of the three
candidate shapes for a depth rule is dead and another is not this item's to rule.

### 9.1 The two items, in full

Both are batch 3, both cassette-less, both **symmetric** — each annotator's accept-set contains
the other's label, which is the signature of two annotators who agree the label is
underdetermined and differ only on where to stop.

**`C06-01` — `adequate_assurance_of_future_performance` vs `adequate_assurance`.** Span:
*"the designee under any Lease/Contract Assumption Notice shall be required, if requested by
the applicable counterparty, to provide **adequate assurance of future performance** with
respect to such Lease or Contract…"*. The object NP is *"adequate assurance of future
performance"* — gold keeps it whole, cold stops at the head before the `of`-postmodifier.
**Both verbatim.** Gold's note records running §3.6's dual-anchor enumeration and authoring all
four variants into the set; cold's records the same two anchors and authors five. **The
enumeration did its job on both sides and the slots still disagreed** — the cleanest available
demonstration that §3.6's existing rules govern the set and not the slot.

**`C13-01` — `pertinent_records` vs `records`.** Span: *"In such a situation, DD will make
available to MBRK, upon request, all of DD's **pertinent records** on MOXATAG."* Gold keeps
the in-NP adjective, cold drops it. `pertinent` is in the text, so gold is not reaching outside
the phrase — this is not mechanism (A) or (B). It is also non-discriminating: the records are
pertinent by definition of what is requested.

**A third item joins under §0's correction: `C14-01` — `withholding_tax` vs `taxes`.** Span:
*"Each party shall deduct such **taxes** from the payments due to the other party hereunder as
required by law including **withholding taxes**…"*. **Both forms appear literally in the same
span**, which makes this the purest instance of the three: neither annotator is inferring
anything, they simply anchored on different in-text mentions.

### 9.2 The depth axis is a monotone three-way gradient, and it is measurable set-wide

Unlike the 8–0 nested count, this does not depend on pairing at all — it is a property of each
annotator's own output. `object_class` slot depth in tokens:

| | mean depth | 1-token slots | max | label literally present in its own span |
| :--- | ---: | ---: | ---: | ---: |
| **gold** (32 items) | **2.25** | 2 (6%) | 5 | 47% |
| **cold** (41 items) | **2.05** | 8 (20%) | 4 | 56% |
| **model** (83 emissions) | **1.77** | 23 (28%) | 3 | **70%** |

And the model's rule is explicit in its own output: **67 of 83 labels (81%) are built only from
tokens of the `object_raw_text` it quoted.** Gold is the deepest and least literal of the three;
the model is the shallowest and most literal; cold sits between them, nearer the model.

### 9.3 The finding that decides this item's scope: the pipeline half of "depth" IS the breadth item

§5 clause 5 tests `prediction ∈ gold's accept_set` and **never reads gold's slot**
(`score.py:226`) — the same one-sidedness that made §3.6.1's slot half free. So a depth
*convention* for the slot cannot move criterion 2. What moves criterion 2 is whether the **set
spans the depth range the model actually emits**, and it largely does not:

| | items whose accept-set contains a head-only (1-token) member |
| :--- | ---: |
| gold | **12 / 32 = 38%** |
| cold | 31 / 41 = 76% |

**The model emits a head-only label 28% of the time, and 62% of gold items cannot accept one at
all.** When those coincide, clause 5 fails no matter which depth convention gold adopts for its
own slot.

**So the depth question splits, and only one half belongs to this row.** Its pipeline half is
set coverage — i.e. it *is* the accept-set breadth item (§5 of this note), already promoted and
**held pending REDESIGN item 0**. Its annotator half — which label goes in the slot — is
rulable independently, free (all three items are batch-3 and cassette-less), and affects only
K and any §7 re-run. **Ruling the slot half would not be wrong; it would simply not do what a
reader might assume it does.**

### 9.4 A structural gap that blocks mechanical adjudication either way

**Neither gold nor cold records the object noun phrase the label was built from.** Verified
against the field lists: gold items carry `object_class` and `object_class_accept_set` and
nothing else object-related; cold the same. The pipeline **does** carry it — `LLMCandidate`'s
`object_raw_text`, surviving into `ast.Obligation` as `object.raw_text` (excluded from
`ir_hash`).

Any depth convention — "keep the head", "keep head plus restrictive modifiers", "keep the whole
NP" — is stated relative to an anchor phrase that gold does not record. Consequences, both
real: a depth convention is **checkable at authoring time and not afterwards**, and §9.2's
"literally present in span" figures are the closest available proxy rather than a direct
measurement. **This also bounds §3.6.1**, ruled at v0.44: its restatement test names the object
NP as its anchor, so it too is authoring-time-checkable only — which is precisely why that
rule's §10 screen had to approximate by stem-matching and why it missed `C10-02`'s `_listing`.
Adding an `object_raw_text`-equivalent field to gold items is a candidate remedy and is **not
proposed here** — it would touch every item's schema.

### 9.5 The comparison-rule option is FALSIFIED by measurement

§5's number rule sets a precedent for handling an axis neither side was asked about: normalize
it away in **comparison** rather than legislate an authoring convention. The natural analogue
for depth is **head-only matching** — compare only the final token, since English compounds are
head-final, so `product_liability` and `liability` would match.

**Measured before proposing it, per §8.6's discipline, over the 31 correctly-paired items:**
clause 5 passes 25/31 today and would pass **29/31** under head-only matching. Of the 4 items
that flip, **only 1 is a genuine depth pair**:

| item | gold | cold | is this a depth difference? |
| :--- | :--- | :--- | :--- |
| `C10-01` | `product_liability_indemnification` | `liability` | yes |
| `C11-01` | `franchise_interest` | `principal_interest` | **no** — possessor vs thing-owned, §3.6 enum 1's own named example |
| `E03-01` | `demand_forecast` | `rolling_forecast` | **no** — which qualifier |
| `C22-02` | `trademark_license_grant` | `third_party_trademark_license` | **no** — the act vs the beneficiary class |

**It buys one legitimate depth fix by erasing three real distinctions.** Worse, on the labels
themselves it would make these gold pairs interchangeable:

- `self_compliant_use` / `third_party_compliant_use` — **the exact pair §4.3.2's v0.37 naming
  convention exists to distinguish.** Head-matching deletes, by construction, the prefix that
  carries the distinction.
- `recall_costs` / `retention_costs`, and `vat_and_taxes` / `withholding_tax`.

**And the precedent does not transfer on its own stated terms.** §5 justifies number
normalization as deleting *"a distinction neither side was ever asked to make"*. Depth is a
distinction §4.3.2 **explicitly asks annotators to make**. This is exactly the *"nearly vacuous
— the opposite failure, and a worse one"* outcome §5 already warns of for Porter-class
stemming, now measured rather than predicted. **Head-only matching is rejected.**

### 9.6 Where this leaves row 3

- **Comparison-rule shape: dead**, on measurement (§9.5).
- **Pipeline-side shape: not this row's** — it is set coverage, i.e. the held breadth item.
- **Annotator-side shape: live, free, and low-value** — three symmetric items (`C06-01`,
  `C13-01`, `C14-01`), all batch-3 and cassette-less, affecting K and nothing else.
- **A precondition surfaces either way (§9.4):** without an anchor field, any depth rule is
  unverifiable after authoring — and that limitation now also attaches to §3.6.1.

**No ruling proposed.** The reviewer should decide whether an annotator-only convention worth
three items is worth writing before item 0 settles what §5 is for, given that the same question
determines whether the pipeline half ever comes back to this row at all.

---

## 10. Set-wide pairing-ambiguity audit — is `C04-139` the only instance? (2026-09-01)

§0's correction found that my pairing script mis-resolved `C04-139` because it did not implement
§4.2's v0.36 content tie-break. That correction established *that* the case existed; it did not
establish that it was the **only** one. Reviewer-requested check, run before the depth ruling is
treated as settled: re-audit all 32 gold items against all 41 cold items for anything sharing
`C04-139`'s shape.

### 10.1 Four independent detectors, all 22 segments

| Detector | What it catches | Hits |
| :-- | :-- | :-- |
| identical spans **within gold** for a segment | the gold half of the shape | `C04-139` (`C04-04`, `C04-05`, both `(4,207)`) |
| identical spans **within cold** for a segment | the cold half | `C04-139` (both `(4,206)`) |
| per-item IoU **tie** between top-2 cold candidates ≥ 0.5 | any pairing decided by a coin flip | `C04-04`, `C04-05` (both 0.9951 to both candidates) |
| **non-unique** max-total-IoU assignment (brute force over all permutations per segment) | ambiguity of the assignment as a whole, not just per item | `C04-139` only |

**`C04-139` is the only instance, on all four.**

### 10.2 The margin distribution says the rest of the set is not close to ambiguous

Top-1 vs top-2 IoU margin, per gold item:

- **29 of 32 items have exactly one cold candidate above IoU 0.5 at all** — for those the pairing
  is not a choice, so there is no tie-break to get wrong.
- **2 items** (`C04-04`, `C04-05`) are the exact tie.
- **1 item** (`C14-01`) has two candidates, at **1.000 vs 0.689** — a margin of 0.311, and the
  second candidate is a plainly different span, not a near-duplicate.
- **1 item** (`C14-02`) has **zero** candidates above 0.5 — §22.1's deliberately-retained
  non-conformance, and the single `UNMATCHED` in `comparison.json`. It reads correctly.

There is no near-tie band. The smallest nonzero margin anywhere is 0.311.

### 10.3 Standing Principle 7 — the detector was checked before its verdict was used

A "no other instances" result is a negative finding from a detector, which is precisely the shape
this project has been burned by seven times. Three controls:

1. **Positive control (known instance):** the detectors fire on `C04-139`, whose answer was
   already established in §0.
2. **Positive control (known second answer):** `C14-02` returns zero candidates, matching
   `comparison.json`'s independently-recorded single `UNMATCHED`.
3. **Planted-instance falsification:** a clone of `C02-01` was injected into its own segment
   (`C02-021`) and the audit re-run. The duplicate-span detector fired on the plant
   (`('C02-021', 'dup_gold', ['C02-01', 'ZZ-99'])`) while `C04-139`'s three baseline hits were
   preserved. The detector is not silently returning "nothing found."

The plant also exposed a **real coverage property worth stating**, since it did *not* trip the
tie detector: a gold-side-only duplication gives both gold items the *same single* best cold
candidate, which is a collision, not a tie. The duplicate-span detectors and the tie detector
cover **different halves** of the shape and only together cover both sides. `C04-139` trips all
three precisely because both sides duplicate. Any future re-run must keep all four, not just the
tie test.

### 10.4 The reference alignment is independently confirmed correct on this case

Read directly out of `comparison.json` rather than inferred:

- `C04-04` → `iou 0.995, fails: [], disagree: false`
- `C04-05` → `iou 0.995, fails: [], disagree: false`
- Whole-file recompute: **`disagree` = 14 of 32 (K unchanged)**, `matched` = 31, and the clause
  profile reproduces exactly — `object 6, action 5, obligor 3, obligee 3, temporal 2,
  conditions 2, underspec 1, UNMATCHED 1` (23 clause failures over 14 items).

And the tie-break is **load-bearing, not cosmetic** here, which is why my script's omission of it
mattered:

| | gold | cold | resolved by |
| :-- | :-- | :-- | :-- |
| pair 1 | `C04-04` — `USE`, accept `{USE, COMPLY}`, `self_compliant_use` | `#0` — `USE`, `self_compliant_use` | §4.2 action-accept-set membership |
| pair 2 | `C04-05` — `ENSURE`, accept `{ENSURE, PROCURE}`, `third_party_compliant_use` | `#1` — `PROCURE`, `third_party_compliant_use` | §4.2 action-accept-set membership |

Both pairs agree exactly on `object_class` and both pass clause 2. The **wrong** resolution pairs
`USE` against `PROCURE` and `self_` against `third_party_` — two clause failures on each item,
which is exactly the spurious "swap" §0's correction retracted.

### 10.5 Verdict

**Clean.** `C04-139` was the single instance; the corrected counts in §0 stand; K, the clause
profile, and every §1–§9 finding are unaffected. The depth ruling can be held on its own merits
rather than under a cloud from the correction that surfaced it.


---

### Ruling 2 — §5 is two predicates, not one → §5.1 (guideline v0.45)

**Ruled 2026-09-01.** §7's REDESIGN response item 0 asked whether §5 is one predicate serving
both pipeline-vs-gold scoring and gold-vs-cold annotator comparison, or two sharing eight
clauses. **Ruled: two.** §5 is unchanged and is the pipeline's; the annotator-comparison
predicate is `A` (§5.1), differing in a slot-only conformance gate, symmetric mutual-membership
accept-set comparison, and no registry branch for parties. Full statement and derivation in the
guideline; recorded here because §7 of this note reached the same question independently from
clause 5 and its own conclusion now resolves.

**§7 of this note asked which of two things item 0's answer would make true. It is the first:**

> *"If §5 is one predicate, then §3.6 must be written to constrain the accept-set (the thing
> scoring reads) rather than the slot (the thing annotators argue about) — and the same is true
> of §3.4. If it is two, then the specificity convention belongs to the annotator-comparison
> predicate only, and the breadth item in §5 above is the entire pipeline-side finding of this
> investigation."*

**So §5-of-this-note is confirmed as this investigation's entire pipeline-side finding**, and the
specificity/depth axis is annotator-side only. Rulings 3 and 4 are those two halves.

**Evidence this note did not have, added by the item-0 investigation** — the decisive argument
came from clause 2, not clause 5, and it is measured: cold wrote an **off-taxonomy `action` slot**
on exactly five matched items (`C02-03` `INVOICE`, `C10-02` `INSURE`, `C14-04` `COMPLETE`,
`C17-01` `PREVENT`, `C17-02` `OBTAIN`), which are **exactly** the five `comparison.json` marks
`2_action` — 5 of 5. Gold carries **zero** off-taxonomy values across 32 items; cold used
`action_not_in_taxonomy` **0 times in 41**, gold twice, on two of those same five. Recomputed
under `A`: **K = 7/27 = 25.9%** (from 14/32), **conformance 5/32**, **G = 4/26 → DIAGNOSE** (from
6/31 → REDESIGN), **`D` = 14 [14–15]**. **The REDESIGN verdict stands.**

**A note on ordering, logged rather than tidied away.** `GAP_AGREEMENT_DESIGN.md` §1 disqualified
option (a) on the ground that *"§5 is a gold-vs-prediction predicate… this alone settles it"* —
which **pre-answered this very question**, while `RESULTS.md` was simultaneously recording that it
*"has never been asked in this project and should be asked before either fix."* The conclusion
survives, independently re-derived here from clause 2 rather than from `known_gaps`. The ordering
does not, and is recorded.

---

### Ruling 3 — accept-set breadth: UNBLOCKED, pipeline-side, anchored (guideline v0.45, §3.6)

Row 2's hold is released **and its shape is settled**, which is the part that needed item 0.
Breadth acts on the **set** — what §5 clause 5 reads — so it is the only lever in this cluster
that can move criterion 2, exactly as §5 of this note argued.

**Anchors: §3.6's own 3–6 band and the model's measured depth distribution** (§9.2/§9.3 — the
model emits a head-only label 28% of the time while 62% of gold items cannot accept one).
**Cold's median is explicitly disqualified as an anchor**, and the item-0 investigation supplied
the measurement that settles it rather than leaving it an argument: cold's `action` accept-sets
average **3.51 as written and 1.93 once restricted to legal taxonomy verbs — below gold's 2.12 —
with 3 of 41 holding no legal member at all.** On the one field where breadth calibration is
checkable, cold's apparent generosity **inverts**. §5-of-this-note's warning that *"cold's 5.35 is
not a target"* is therefore confirmed by measurement, not merely by caution.

**Both hazards carry forward unchanged** (monotone widening makes an unsequenced delta
uninterpretable; every widening must be defensible from the span alone), and **venue is
unchanged**: §10's freeze pass, its scope expanded from three queued widenings to a systematic
audit.

---

### Ruling 4 — depth: scoped to `A`, convention deliberately NOT written (guideline v0.45, §3.6)

Row 3 is ruled to be **§5.1 `A`'s scope and nothing else**. It cannot constrain criterion 2 now
or ever, because clause 5 never reads gold's slot; its pipeline half is row 2 and does not exist
separately; and the comparison-rule shape stays falsified by §9.5.

**No convention is written, and that is the ruling rather than a deferral by default.** §9.4's
precondition is unmet — neither annotator records the object noun phrase the label was built
from, so any depth rule is checkable at authoring time and **unverifiable afterwards**, a
limitation that also attaches to §3.6.1. A rule whose compliance cannot be audited across the
locked set is the shape of guarantee this project has repeatedly had to undo. The cost of waiting
is stated and small: three items, all batch-3 and cassette-less, so writing it later is exactly
as cheap as writing it now.

**One thing this ruling hands to the §8 tag-vocabulary review.** `A`'s gate drops `C14-04` from
G, and `C14-04` was `GAP_AGREEMENT_DESIGN.md` §6's **only** motivating instance for the deferred
*"can §8 tags legitimately co-apply?"* question — `G_disjoint` falls to **zero**. That does not
answer the question; it removes its only evidence, and the review should be told so rather than
finding an empty cell and reading it as a result.

---

### Re-verification findings (2026-09-01) — TWO PREVIOUSLY-UNRECORDED DEFECTS, NEITHER FIXED

v0.45's close-out re-validated all 32 locked items against 17 invariants (544 assertions).
**Four items failed. One is expected — and is the validator's own known-answer check — and two
are real, new, and deliberately left unfixed**: restamping a locked item is §10's freeze pass and
the reviewer's call, not a close-out's.

**Expected.** `C14-02`'s `obligor` *"Each party"* does not appear in its `span_text` at all. This
is §22.1's **deliberately-retained** non-conformance — the item annotated under the superseded
§8.3.1 v0.23 rule whose span is documented as wrong and which knowingly scores `MISSED`. The
validator finding exactly the one item the guideline says is non-conforming, and no others, is
what makes its verdict on the other 31 worth anything.

**REAL, NEW (1) — `C10-02`'s party slots are NOT verbatim, and the published attribution of this
runs the wrong way.** §3.5 requires the alias *"exactly as it appears inside `span_text`"*. The
span reads *"**The Supplier** shall add **the distributor** to their current insurance
certificate."* Gold annotates `obligor: "the Supplier"` and `obligee: "the Distributor"` —
**both differ from the span in case, and in opposite directions**, so this is two independent
slips rather than a systematic convention.

- **`RESULTS.md`'s sensitivity B has the attribution backwards.** It records gold
  `the Supplier`/`the Distributor` against cold `The Supplier`/`the distributor` as a case
  difference costing nothing. **Cold is verbatim-correct on both slots; gold is not.** The
  sensitivity's *conclusion* survives — `C10-02` fails on other clauses either way and K is
  unchanged — but the finding as written reads as a cold-side quirk and it is a gold-side defect.
- **Not cosmetic: §21 R2 already names the mechanism.** The scoring registry matches `aliases`
  **case-SENSITIVELY**, so a non-verbatim gold alias is exactly the trap R2 flags and R5 fails
  loudly on. It costs nothing **today** only because `C10-016` has no cassette and `C10` has no
  registry — i.e. the guard that would catch it has never run on this document.
- **Consequence if fixed:** none for any published number. Under §5.1's `A` the item is
  `NON_CONFORMING` on cold's off-taxonomy `INSURE` regardless, and it sits outside
  `run_scoring`'s scoreable 18.
- **Tracked as guideline §10.1 item F2**, and corrected on the record in `RESULTS.md`'s own
  dated "Correction to Sensitivity B's attribution (2026-09-01)" — not only here, because
  `RESULTS.md` is the document a reader consults to find out what the §7 run found.

**REAL, NEW (2) — §3.6.1 and §4.3.2's naming convention CONFLICT at `C04-04`, structurally rather
than by slip.** `C04-04` holds `action = USE` and `object_class = self_compliant_use`: the slot
restates the action, which §3.6.1 (v0.44, retroactive) forbids in terms. But §4.3.2's v0.37
convention **requires** `self_`/`third_party_` prefixes over a **shared root**, and §9.5 of this
note leans on that very pair as the distinction head-only matching would destroy. Both rules are
live and both cannot be satisfied here.

- **The conflict is asymmetric, which is the diagnostic detail.** `C04-05` holds
  `action = ENSURE` against `third_party_compliant_use` and is clean — `use` is not `ensure`. So
  §4.3.2's shared root collides with §3.6.1 on **exactly one item of a split pair**: whichever
  half's action verb happens to equal the root. Any future §4.3.2 split whose root is a taxonomy
  verb reproduces it.
- **The v0.44 §10 screen missed it, consistent with its own recorded caveat.** That screen
  already logged a Standing Principle 7 note calling itself *"a lower bound, not a census"* after
  missing `C10-02`'s `_listing`. This is a second miss by a different mechanism: the screen looked
  for restated material, and `self_compliant_use` reads as a purpose-built §4.3.2 label rather
  than as a restatement.
- **Not adjudicated here.** It needs a ruling on which rule yields, and the options are visibly
  different: narrow §3.6.1 to exempt §4.3.2's shared root, amend §4.3.2 to require a root that is
  not a taxonomy verb, or restamp `C04-04`. The third touches a **cassette-backed** item
  (`C04-139` was recorded), so this is **freeze-pass work**, not close-out work. **Tracked as
  guideline §10.1 item F3**, which states the three options and their differing costs — filed as
  a rule conflict rather than a label fix, because the asymmetry above makes it reproducible by
  any future §4.3.2 split whose root is a taxonomy verb.
