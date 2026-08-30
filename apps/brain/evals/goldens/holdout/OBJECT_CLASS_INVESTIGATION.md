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
| 2 | **accept-set breadth** (§5 of this note) | **HELD pending REDESIGN item 0** | promoted above the remaining rules — the only lever here that provably touches criterion 2 — but its shape depends on whether §5 is one predicate or two |
| 3 | **depth rule** (`C06-01`, `C13-01`) | open | also free (batch-3, no cassette); genuinely underdetermined, and §5's number-rule precedent leaves a comparison-rule option unargued |
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
