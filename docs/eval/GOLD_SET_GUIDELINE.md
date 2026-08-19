# Obligo Tier-2 Gold Set — Annotation Guideline

**Version:** v0.13 (DRAFT — not yet frozen)
**Created:** 2026-08-17
**Status:** No items have been annotated against this document yet.
**v0.2 change:** corpus rebuilt after a selection-bias audit — see §13.
**v0.3 change:** annotator-uncertainty protocol added — see §14. Two fields added to §1.
**v0.4 change:** vague-temporal-qualifier rule added — see §15. One non-scored field added to §1.
**v0.5 change:** efforts-qualifier rule added (§16); §3.2's contradictory "reasonable efforts" row corrected.
**v0.6 change:** internal-boolean condition rule added — see §17. §3.8 cross-referenced.
**v0.7 change:** corpus independently re-verified and the statistics made reproducible — see
§18. Three open questions decided: absent-obligee confirmed (§3.5), synthetic items confirmed
OUT (§11), held-out mechanism fixed (§7). Two stale internal numbers corrected (§9, §13).
**v0.8 change:** the last open question decided — parenthetical-numeral `WITHIN` items are
annotated honestly and criterion 1b is reported both ways (§11, §9). One field added to §1.
**v0.9 change:** a difficulty-correlated segment-enumeration defect found and fixed before
batch 1 was drawn — see §18.6. §18.3's re-measurement column updated to the corrected pool
and given a segment-size caveat. §11 retitled (all four questions are decided).
**v0.10 change:** two annotation rules added for classes found while walking batch 1's own
draw — redacted values (§8.1) and `UNLESS`-dependent clauses (§8.2), both as tagged
`known_gap` items rather than exclusions. One non-scored field added to §1
(`redacted_phrase`). E06 retired and replaced by E07 (§18.6); manifest v0.4.
**v0.11 change:** the four-step EDGAR sourcing rule made binding (§12.1) after an audit of
all six originally-sourced EDGAR documents. **E04 found defective — a whole Form 8-K, the
same defect as E06 — a 33% defect rate for the pre-step-3 method.**
**v0.12 change:** E04 retired and replaced by E08 under §12.1 (manifest v0.5); §12.1 step 3
tightened after its first version selected a GROUND LEASE. **No open questions remain.**
**v0.13 change:** redaction split into two tags — `redacted_value` and `redacted_clause`
(§3.7.1) — because "a deadline exists but its value is hidden" and "whether an obligation
exists at all is hidden" are different facts. Measured 155 embedded vs 85 whole-clause
occurrences. `redacted_clause` spans are unscoreable and leave both criteria's
denominators. v0.13 is the version batch 1 is annotated under.

*Why v0.8 and not an edit to v0.7:* v0.7 was committed, and every gold item stamps the
guideline version it was annotated under. Amending a committed version in place would make
one version string denote two different rulesets — precisely what this document's own
versioning discipline forbids.

This guideline governs the construction of the 100-item Tier-2 gold set that blueprint
§19.7 specifies and that Phase 4 acceptance criterion 2 (Tier-2 fully-correct-IR rate
≥80%) is measured against. Criterion 1b (compile success ≥90% on the dev corpus) is
measured against the same 28 documents with a different denominator — see §9.

**Every batch records the guideline version it was annotated under.** After the freeze
(§10), any amendment requires a logged re-check of the amended rule across all prior
batches. This document is versioned, never edited silently — the same discipline
`prompts/` and Flyway migrations follow in this repo.

---

## 1. What a gold item is

**One gold item = one obligation, as a human annotator reads it, located in one segment
of one document.**

An item is *not* a sentence and *not* a candidate. One sentence may yield two items
(§4.3); one item never spans two segments.

Each item records:

| Field | Source | Notes |
| :--- | :--- | :--- |
| `item_id` | assigned | `C03-07` = document C03, 7th item |
| `doc_id` | manifest | from `corpus_manifest.json` |
| `segment_text` | verbatim | the exact segment the pipeline will be given |
| `span_char_start` / `span_char_end` | computed | offsets into `segment_text` |
| `span_text` | derived | MUST equal `segment_text[start:end]`, byte-for-byte |
| `modality` | annotated | `MUST` \| `MUST_NOT` \| `SHOULD` \| `MAY` |
| `action` | annotated | + `action_accept_set` (§3.4) |
| `obligor` | annotated | alias as it appears, or `ABSENT` (§3.5) |
| `obligee` | annotated | alias as it appears, or `ABSENT` (§3.5) |
| `object_class` | annotated | + `object_class_accept_set` (§3.6) |
| `temporal` | annotated | one of five forms, or `null` (§3.7) |
| `conditions` | annotated | ordered list of verbatim strings (§3.8) |
| `underspecified` | annotated | bool (§3.9) |
| `missing_fields` | annotated | reported, **excluded from the scoring predicate** |
| `vague_temporal_phrase` | annotated | literal phrase or `null`; **not scored** (§15) |
| `redacted_phrase` | annotated | literal redacted phrase or `null`; **not scored** (§8.1) |
| `known_gap` | annotated | `null`, or the named v1 gap this item exercises (§8, §11) |
| `annotator_confidence` | annotated | `CONFIDENT` \| `AMBIGUOUS` \| `UNCERTAIN` (§14) |
| `annotated_at` | stamped | ISO-8601 timestamp; feeds per-item pace measurement |
| `rules_cited` | annotated | **required** — the § numbers invoked (§14.5) |
| `guideline_version` | stamped | e.g. `v0.6` |
| `annotator_notes` | free text | required whenever a rule was close to the line |

---

## 2. Choosing segments

A **segment** is the unit handed to `run_pipeline()`. For the gold set, segments are cut
by hand from the source document, not by the Phase 3 segmenter — this measures the
compiler, not the segmenter.

**A segment is eligible if all of the following hold:**

- 200–2,000 characters. (`MAX_SEGMENT_CHARS` is 20,000; this is far tighter on purpose.)
- Contains 1–3 obligation-bearing clauses.
- Is self-contained: the obligation's content is readable without following a
  cross-reference out of the segment.
- Comes from born-digital text. No scanned/OCR'd filings — that would confound
  extraction quality with OCR quality.

**A segment is excluded if any of the following hold:**

| Exclusion | Reason |
| :--- | :--- |
| Definitions, recitals, signature blocks, pure tables | No obligation-bearing sentences |
| 4+ chained obligations in one sentence | IoU alignment degrades; one failure contaminates the segment |
| Cross-reference-dependent ("in the manner set forth in Section 12.3") | Genuinely unannotatable at segment scope |
| Contains only a party's *right* with no correlative duty | Not an obligation under IR v1's four modalities |

Excluded segments are recorded with their exclusion reason. They are **not** silently
skipped — the exclusion log is part of the deliverable.

### 2.1 Segment selection is drawn, not chosen

The drafter does **not** pick which passages become gold items. Discretion at this step is
the largest and least visible bias risk in the whole build (§13).

1. The drafter **mechanically enumerates** every segment meeting the formal criteria
   above — length band, modal presence. No judgment, just the filter.
2. Segments are auto-assigned to strata.
3. **The reviewer holds the seed and draws** which enumerated segments become items.
4. Every segment rejected as ineligible is logged **with its verbatim text and the rule
   invoked**, and a random sample of rejections goes into the reviewer's batch packet —
   so an exclusion that was really a difficulty dodge is visible.

### 2.2 Hard-document stratum

**At least 25 of the 100 items must come from documents at ≥20% cross-reference density**
(the `xref_pct` field in `corpus_manifest.json`). Seven of the 28 documents qualify and
hold 22% of the corpus's obligation sentences, so proportional sampling would land near
this figure anyway — the stratum makes it a floor rather than a hope.

---

## 3. Field rules

### 3.1 `span_text` — the grounded field

`span_text` MUST be a literal, byte-exact substring of `segment_text`. This is the same
discipline `ground_candidates()` enforces mechanically; the annotation is held to it too.

The span is the **minimal contiguous substring that states the complete obligation**,
including any leading subordinate clause that establishes its timing, condition, or
scope. This matches `prompts/extraction/v2.yaml`'s rule exactly and is deliberate: if
gold drew spans narrowly while the prompt asks for them widely, every fronted-clause item
would fail on a disagreement we created ourselves.

### 3.2 `modality`

Map the governing modal verb:

| Text | Modality |
| :--- | :--- |
| shall, must, will (obligatory sense), agrees to, is required to | `MUST` |
| shall not, must not, may not, is prohibited from | `MUST_NOT` |
| should, ought to, is encouraged to | `SHOULD` |
| may, is entitled to, is permitted to | `MAY` |

**Efforts qualifiers do not appear in this table** — "shall use reasonable efforts" is
`MUST`, not `SHOULD`. See §16; v0.4 and earlier had a contradictory row here.

**"Will" is ambiguous** and is the most common judgment call in real contracts. Rule:
`will` is `MUST` when it states a party's undertaking; it is *not* an obligation at all
when it states a future fact about the agreement ("this Agreement will terminate on...")
— the latter is an excluded segment, not a `MUST` item.

### 3.3 Modality is exact-match, not accept-set

Four closed values, and the choice is determined by the text. No accept-sets here.

### 3.4 `action` — exact-match against an **accept-set**

The 34-verb taxonomy (`compiler/ast.py`, `ACTIONS`) is closed, but **closed is not the
same as unique**: the eval pilot recorded a real case where `PROVIDE` and `REPORT` were
both defensible for "submit a compliance report." Hard exact-match would have scored a
correct extraction as wrong.

**Rule:** annotate the single best verb *and* an `action_accept_set` containing every
taxonomy verb a competent annotator could defend for this sentence. Scoring passes if the
predicted action is in the accept-set.

The accept-set is authored **at annotation time and frozen with the item**. It is never
widened after seeing a prediction — that would be fitting the gold to the model.

### 3.5 `obligor` / `obligee` — and the `ABSENT` rule

Annotate the party alias **exactly as it appears inside `span_text`**.

Real contracts routinely omit the beneficiary: *"Vendor shall maintain insurance."*
Owed to whom? The grammar requires an obligee, and the current extraction prompt's own
worked example emits `"obligee_alias": ""` — undesigned behavior, not a chosen rule.

**Rule (CONFIRMED v0.7):** a party genuinely not stated in the span is annotated `ABSENT`.
An item with an `ABSENT` party is `underspecified = true` with that role in
`missing_fields`. It is **not** a compile failure and **not** a correct fully-specified
extraction.

Rationale: this matches how v1 already treats every other unresolvable reference
(`PartyRef`/`DateRef`/`TriggerRef` are two-state, and "unresolved" is an honest state, not
an error). Treating an absent obligee as a failure would penalise the pipeline for
faithfully representing what the document actually says.

Do **not** infer a party from elsewhere in the document. If it isn't in the span, it's
`ABSENT`.

### 3.6 `object_class` — open vocabulary, accept-set required

`object_class` is free vocabulary (snake_case). Always author an
`object_class_accept_set`. The pilot recorded a real miss here (`customer_personal_data`
predicted, gold accept-set too narrow).

Author the accept-set generously at annotation time — 3–6 plausible labels is normal.
Same freeze rule as §3.4.

### 3.7 `temporal` — one of five forms, or `null`

Annotate the form and its constituents:

| Form | Example | Constituents |
| :--- | :--- | :--- |
| `WITHIN` | "within 30 days of receipt" | amount, unit, trigger |
| `BY` | "by 2027-03-01" | date or alias |
| `EVERY` | "every 30 days" | amount, unit |
| `DURING` | "during 2027-01-01..2027-12-31" | start, end |
| `RELATIVE_TO_TRIGGER` | "after the Effective Date" | direction, trigger |

`temporal = null` **only** when the obligation genuinely carries no timing phrase. A
vague phrase ("promptly", "as soon as practicable") is annotated as `null` **with
`annotator_notes` recording the phrase** — v1's typechecker cannot distinguish vague-
temporal from no-temporal by design (`typecheck.py`'s module docstring), so gold must not
pretend to either.

**Known-gap forms (§8) are annotated normally.** Do not avoid them.

#### 3.7.1 Two redaction tags, because they are two different facts (v0.13)

Confidential-treatment redactions come in two shapes, and collapsing them would destroy
real information — the same reason §14.1 keeps `AMBIGUOUS` and `UNCERTAIN` strictly apart.
**Measured across the corpus: 155 embedded occurrences against 85 whole-clause ones, over
96 segments.** Both are common; neither is a corner case.

| Tag | The fact it records | Shape in the document |
| :--- | :--- | :--- |
| `redacted_value` | **A constraint of this kind exists; its magnitude is unknown.** | The clause survives and its wording establishes what kind of constraint it is; only the operative value is withheld — *"At least \*\* before the \*\* of each Calendar Quarter"* |
| `redacted_clause` | **Whether an obligation exists here at all is unknown.** | An entire clause or sentence is replaced, leaving nothing to read — *"…unless otherwise mutually agreed. \[\*\*\] ."* |

**`redacted_value` — annotate the item.** The obligor, action and object survive, so the
obligation is real and annotatable. Set the affected field to `null`, `underspecified =
true` with that field in `missing_fields`, `known_gap = "redacted_value"`, and the literal
phrase in `redacted_phrase` (§8.1, unchanged).

**`redacted_clause` — do not annotate an item for the redacted clause.** There is no
obligation to annotate; asserting one would be fabrication, and asserting its absence would
be equally unfounded. Other obligations in the same segment are annotated normally. The
segment is tagged `redacted_clause` at segment level so the gap is visible downstream.

**The scoring consequence, which is the real reason this needs its own tag.** A
whole-clause redaction makes the ground truth for that span *unknowable*, not merely
absent. So over a `redacted_clause` span the pipeline's output cannot be scored in either
direction: an extraction there is **not** counted as a spurious extraction, and the absence
of one is **not** counted as a `MISSED`. Both are excluded from criterion 1b's and
criterion 2's denominators and reported separately as an unscoreable count. Tagging these
as `redacted_value` would have silently pushed 85 unknowable spans into a denominator as
though they were known-empty — which is precisely the information loss this split
prevents.

### 3.8 `conditions`

A list of verbatim condition phrases from within `span_text`. Order-insensitive but
**count-sensitive** when scored: two conditions in gold require two `Condition` entries in
the output.

Do **not** split a single condition string on internal `AND`/`OR` — `ir_compile.py`
deliberately does not do this, and gold must test what the extractor produces, not ask
the compiler for behavior it doesn't have.

### 3.9 `underspecified`

`true` when any of: an `ABSENT` party (§3.5); a `DateRef` that cannot resolve; a
`TriggerRef` that cannot resolve; a business-day (`bd`) duration.

**In v1 this will be true for a large share of real items**, because
`symbols.resolve_date()` and `resolve_trigger()` unconditionally return `None`. That is a
**pass**, not a failure — the item is scored correct if the pipeline also reports
`underspecified = true`. See §9 for why this must be stated whenever the headline number
is reported.

---

## 4. Alignment and splitting

### 4.1 Alignment
A predicted obligation aligns to a gold item when their span offsets overlap with
**IoU ≥ 0.5** within the same segment.

### 4.2 Tie-break
**One predicted span aligns to at most one gold item.** Pairing is greedy by descending
IoU, and the chosen pairing is recorded with the score.

### 4.3 Multi-obligation sentences
*"Vendor shall notify Customer and shall deliver a report within 5 days."*

**Rule:** split into separate items when the sentence has **two distinct governing
verbs with separately identifiable objects**. Do not split on a compound object of one
verb ("shall deliver the report and the invoice") — that is one item.

A gold item that ends up unaligned because the model emitted one merged span is scored
`MISSED`. That is a real recall finding, not an annotation error.

### 4.4 `NOT_ANNOTATABLE`
A clause inside an otherwise-good segment that the exclusion rules of §2 would reject on
its own is labelled `NOT_ANNOTATABLE`. A prediction aligning to it counts as **neither**
a correct item **nor** a false positive.

---

## 5. The scoring predicate

An aligned item is `FULLY_CORRECT` iff **all** of the following hold — this is
**conjunctive**, not weighted:

1. `modality` exact
2. `action` ∈ `action_accept_set`
3. `obligor` matches (including `ABSENT` matching `ABSENT`)
4. `obligee` matches (including `ABSENT` matching `ABSENT`)
5. `object_class` ∈ `object_class_accept_set`
6. `temporal` form matches, **and** amount/unit/date constituents match exactly
7. `conditions` match as an order-insensitive, count-sensitive set
8. `underspecified` matches

`missing_fields` is **reported but excluded** from the predicate.

Other outcomes: `PARTIAL` (aligned, predicate fails), `MISSED` (no aligned prediction),
`UNEXPECTED` (prediction aligned to no gold item and not `NOT_ANNOTATABLE`).

---

## 6. Non-determinism

Temperature 0.0 is **not** a determinism guarantee — the eval pilot reproduced different
extractions for 2 of 10 items across two identical runs.

**The harness runs the full gold set 3× and reports the per-item modal outcome plus a
count of items unstable across runs.** Three, not two: with two you cannot break a tie.
No single-run number is ever published without this caveat attached.

---

## 7. Held-out blinding

- Per batch, a seeded draw selects **2 of 10** items to withhold.
- **The reviewer holds the seed and runs the draw.** The drafter never sees which items
  are held out until session 11.
- Withheld drafts live in `gold/holdout/drafts/` (gitignored). Review packets are
  *generated* documents containing only the reviewable items — the reviewer never
  navigates the raw annotation tree.

**Second-annotator mechanism (CONFIRMED v0.7).** At the held-out checkpoint, a **fresh
subagent** annotates all 20 cold from `holdout_annotation.md` (guideline + raw segments +
empty templates; no drafts, no access to this session's history). Its completed
annotations are **committed and hashed before** the comparison is run. The reviewer then
adjudicates every disagreement, and additionally **spot-checks 5 of the 20 items** drawn
by the same seeded mechanism — the spot-check is what keeps the reviewer's own eyes on
items where the two annotators *agreed*, which is exactly where a shared blind spot hides.

**This is a weaker claim than an independent human second annotator, and is reported as
one.** The subagent shares a model family, and therefore shares priors, with the drafter.
Its errors are **correlated** with the drafter's in a way a second human's would not be:
where the guideline is ambiguous in a way that biases a language model, both annotators
tend to go wrong in the same direction, and the disagreement count K cannot see it. K is
therefore a **lower bound** on the true disagreement rate against a genuinely independent
annotator, not an estimate of it. Every published use of K must say so. The 5-item
reviewer spot-check is a partial, deliberately-acknowledged-as-partial mitigation: five
items cannot certify anything, but they can catch a gross shared error.
- **K counts disagreements, not confirmed first-pass errors** — if adjudication finds the
  second annotator wrong, it still counts. Item-level, not field-level. A prediction
  inside the accept-set is not a disagreement; a defensible label *outside* it is.

**Thresholds, fixed in advance:**

| K / 20 | Verdict |
| :--- | :--- |
| 0–1 | **PROCEED** — report K/20 with its Wilson CI; claim no rate below 5% |
| 2–3 | **DIAGNOSE** — clustered (≥2 on one field/rule) → fix rule, re-check across all 100, draw a second disjoint 20, proceed iff K₂ ≤ 1. Diffuse → treat as ≥4 |
| ≥4 | **REDESIGN** — re-annotate all 100 under a revised guideline *and* a changed process |

N=20 catches a ≥15% error rate ~82% of the time, is a coin flip at 10%, and cannot
certify 5%. It is a tripwire, not an estimator, and must be reported as one.

---

## 8. Known v1 gaps — annotate honestly, do not avoid

These forms are **deliberately included** in the gold set. Annotate what the document
says; if v1 cannot compile it, that is a measurement, not an annotation error.

| Gap | v1 behavior |
| :--- | :--- |
| `within thirty (30) days` | `UNMAPPABLE_TEMPORAL` — `_WITHIN_RE` requires a bare digit |
| `no later than` / `on or before` / `prior to` | `UNMAPPABLE_TEMPORAL` (pinned regression) |
| `during the Term` | `UNMAPPABLE_TEMPORAL` — `_DURING_RE` needs two ISO dates |
| business-day durations | always `underspecified` (no calendar model) |
| any trigger-bearing temporal | always `underspecified` (`resolve_trigger()` returns `None`) |
| `EVERY` + `DURING` composed | `EVERY` only, with a composition warning |
| `UNLESS` / any exception carve-out | **Fails to parse** — v1's grammar has no exception construct at all (§8.2) |
| Redacted value (`**`, `[***]`) | Value withheld in the filing; unresolvable by any pipeline stage (§8.1) |

**Measured in this corpus: 74% of `WITHIN` deadlines (119 of 161) use the parenthetical
form v1 rejects.** See §11 — this is the open scope question from session 1. The ratio
held at 74% both before and after the corpus was rebuilt (§13), across 12 and then 28
documents, which makes it a property of real contract drafting rather than of the sample.

**Independently re-measured in v0.7: 84% (152 of 180).** The second measurement
(`apps/brain/evals/corpus.py profile`) counts every `WITHIN` deadline in the corpus and
classifies it by asking the real `_WITHIN_RE` — imported from `compiler/ir_compile.py`,
not reimplemented — whether it would accept the numeral. It therefore measures what the
compiler actually rejects rather than what a proxy regex predicts it rejects. The two
measurements disagree on the exact count (their sentence-splitting and phrase-extraction
rules differ) and agree on the finding: **the large majority of real `WITHIN` deadlines in
this corpus are uncompilable under v1.** No plausible reading of either number changes the
scope decision in §11.

### 8.1 Redacted values (v0.10)

Confidential-treatment redactions (`**`, `[***]`) replace the operative value of a field —
most often a deadline or a quantity. **Measured: 96 of 1,679 pool segments (5.7%) carry
one, but 14.5% of the hard stratum does** — the high-cross-reference documents are the
complex commercial agreements that got confidential treatment (C04, C02 and E03 hold 91 of
the 96).

**Rule.** Annotate the item. Set the affected field to `null`, `underspecified = true` with
the field named in `missing_fields`, `known_gap = "redacted_value"`, and record the literal
redacted phrase in the non-scored `redacted_phrase` field.

**Why not exclude them.** Excluding redacted segments is the one answer that is clearly
wrong: at 2.5× concentration in the hard stratum it would deplete exactly the documents
§2.2's 25-item floor exists to protect — the same failure mode as the enumeration defect in
§18.6, arriving through an annotation rule instead of a parsing one.

**Why not simply `temporal: null` with no tag.** That conflates *"the contract states no
deadline"* with *"a deadline exists and was withheld from the filing"*. They are different
facts about the document, and untagged they become indistinguishable in criterion 1b and
criterion 2.

### 8.2 `UNLESS`-dependent clauses (v0.10)

IR v1 has **no exception construct at all** — `UNLESS` does not underspecify, it fails to
parse, by the deliberate freeze decision recorded in `packages/ir-spec/`. A clause whose
operative meaning sits in an `unless` therefore cannot be represented faithfully.

**Rule.** Annotate the **carve-out-free reading** with `known_gap = "unless_unsupported"`,
and record the full carve-out verbatim in `annotator_notes`.

**The cost, stated rather than hidden:** the annotated obligation is *stronger* than the
one the contract imposes — a flat prohibition where the document has a conditional one.
That is deliberate. The alternative, excluding the class, makes v1's single largest
representational gap invisible in the gold set, and §8's standing posture is that a known
gap is annotated honestly and measured, never avoided. Every such item is tagged, so the
overstatement is always recoverable from the data rather than baked silently into a score.

---


---

## 9. The two criteria have different denominators

- **Criterion 2 (≥80%)** — `FULLY_CORRECT` / 100 gold items.
- **Criterion 1b (≥90%)** — of candidates that survive grounding and reach the compiler,
  the fraction producing a typechecked `Obligation` within ≤2 repairs, over all 28
  documents.

**1b is gameable in isolation**: a prompt emitting fewer, safer candidates scores higher
while extracting less. **1b is therefore always reported paired with the `MISSED` count.**

**1b is also always reported twice (v0.8, §11):** once over all items, once excluding
items tagged `known_gap`. Both are published together; neither is quoted alone. The split
is computed mechanically from the `known_gap` field, not reconstructed by hand.

Both numbers are reported alongside: the spurious-extraction count over zero-obligation
segments, the share of items correctly `underspecified` (so "compiled faithfully" is not
misread as "resolved"), and the prompt/model/grammar versions in force.

---

## 10. Versioning and freeze

- v0.1 → amended freely during batches 1–3.
- **Freeze after batch 3 (30 items).** Batches 1–3 are conformed to the frozen version.
- Post-freeze amendments require a logged re-check of the amended rule across all prior
  batches, recorded in the manifest.
- Every item stamps its `guideline_version`. If held-out disagreements cluster in
  pre-freeze batches, that is diagnostic — the freeze worked.

---

## 11. Decisions (formerly open questions)

**RESOLVED v0.8 — 1. The parenthetical-numeral finding (§8).** Decided as **(c)**:
annotate, measure both ways, and only then consider a code change. The figure was deferred
pending verification and **was independently verified** (§18): 74% by the original
measurement, 84% by a second, differently-defined measurement taken against `_WITHIN_RE`
itself. The finding is real at either number.

**The rule this fixes, binding on every batch:**

- Parenthetical-form `WITHIN` items are **annotated honestly**, exactly as the document
  writes them. The annotator records what the contract says; the expected v1 outcome is
  `UNMAPPABLE_TEMPORAL` under the current grammar, and that is a **measurement, not an
  annotation error** (§8's standing rule, unchanged).
- **Criterion 1b is reported twice**: over all items, and excluding known-gap items. Both
  numbers are published together. Neither is presented alone, in either direction — the
  with-gap number is not buried, and the without-gap number is not quoted as if it were
  the headline compile rate.
- Every such item is tagged `known_gap: "within_parenthetical"` so the two denominators
  are computed mechanically rather than reconstructed by hand afterward.
- **Widening `_WITHIN_RE` is deferred, not rejected.** Revisit only once the paired
  numbers exist. Changing the classifier first would tune the compiler to the corpus it is
  about to be graded on, and would destroy the baseline that makes the widening's value
  measurable at all.

Rejected alternatives, recorded so they are not relitigated: **(a)** absorb the loss into
a single 1b number — honest but discards the diagnostic split for free; **(b)** widen
`_WITHIN_RE` before measuring — the tuning-to-the-corpus objection above.

**RESOLVED v0.7 — 2. Absent-obligee rule (§3.5).** Confirmed: carried as underspecification
(`missing_fields: ["obligee"]`), not a compile failure. The basis is that the extraction
prompt's own worked example already emits an empty `obligee_alias` as undesigned behavior
rather than a chosen rule, so treating it as a failure would penalise the pipeline for
faithfully representing what the document says.

**RESOLVED v0.7 — 3. Synthetic items.** Confirmed **OUT**. The gold set is 100% real
across the corpus. Synthetic items probing the `DURING`/`EVERY`/`BY` forms may be kept as
a separate probe set, but are **excluded from every reported and headline number**.

**RESOLVED v0.7 — 4. Held-out mechanism.** Confirmed: fresh subagent on all 20, reviewer
adjudicates disagreements plus a 5-item spot-check. Its correlated-error limitation is
recorded in §7 and must be stated wherever K is published.

---

## 12. Sources

- CUAD v1 — The Atticus Project, **CC BY 4.0**, 510 contracts / 13k expert clause labels.
- SEC EDGAR — public filings, retrieved via EDGAR full-text search.
- Per-document URLs, SHA-256 hashes, and measured density: `docs/eval/corpus_manifest.json`.

**Corpus v0.2: 28 documents** — 22 CUAD + 6 EDGAR. 3,760 obligation-bearing sentences,
242 with temporal phrases, 475 with a fronted subordinate clause.

### 12.1 EDGAR sourcing method — binding for all future draws (v0.11)

The original method (§13) was "seeded random from full hit lists" of an EDGAR full-text
keyword search. **That method is not sufficient on its own and must never be used alone
again**, because a full-text query for a contract type matches every contract that merely
*mentions* that type. Measured over a 28-document unique sample of a `"MAINTENANCE
AGREEMENT"` hit list: **21% had that type as their own title, 75% were other contract types
mentioning it in the body, and 3% were whole SEC forms.**

**Every EDGAR document entering this corpus must pass all four steps:**

1. EDGAR full-text search for the contract type, seeded-random over the hit list (§13).
2. Filter to exhibit-shaped filenames (`ex-10`, `exv10`, …).
3. **Fetch the document and require the type term in its own title** — the
   `<DESCRIPTION>` field *and* the document body's own heading. Body frequency is not
   evidence of document type; only the title is.
4. Reject whole SEC forms (a `10-K`/`10-Q`/`8-K`/`S-1` header) and anything failing a
   contract-shape floor: ≥15 KB, ≥20 `shall`, and at least one of `by and between` /
   `WHEREAS`.

Step 3 is the step whose absence produced both defects below. It was validated in use: the
first pass of E07's own redraw selected an *LLC Membership Interest Purchase Agreement*
that mentions maintenance agreements 24 times — E06's failure mode reproduced inside the
fix for it, and caught by step 3.

**Audit of the five originally-sourced EDGAR documents (v0.11).** Run because all six were
sourced by the pre-step-3 method, so all six carried the same risk:

| id | claimed type | `shall` | `by and between` / `WHEREAS` | verdict |
| :--- | :--- | ---: | :--- | :--- |
| E01 | data_processing | 105 | 1 / 3 | **CONTRACT** |
| E02 | service_level | 39 | 3 / 2 | **CONTRACT** |
| E03 | supply | 157 | 1 / 3 | **CONTRACT** |
| **E04** | **logistics** | **9** | **0 / 0** | **WHOLE SEC FORM — defective** |
| E05 | escrow | 66 | 1 / 5 | **CONTRACT** |
| E07 | maintenance | 34 | 1 / 2 | **CONTRACT** (sourced under the four-step rule) |

**E04 is a second instance of E06's defect**: `tllp8-k06x23x2014.htm` is a complete Form
8-K current report *announcing* a West Coast logistics drop-down, not the agreement itself
— no `by and between`, no `WHEREAS`, 9 `shall` in 20,631 characters. Two of the six
originally-sourced EDGAR documents were therefore not contracts, which is a **33% defect
rate for the pre-step-3 method** and the justification for making step 3 binding rather
than advisory.

E04 is standard-stratum (`xref_pct` 2) and contributed 20 of 1,514 pool segments (1.3%),
none to the hard stratum — so §2.2's floor and the hard queue were unaffected by its fate.

**Resolved in v0.12: E04 retired, replaced by E08** (manifest v0.5) — Kirkland's Inc.
`LOGISTICS SERVICES AGREEMENT` (EX-10.20, accession 0001056285-19-000017, 123,630 bytes,
140 `shall`, 5 `WHEREAS`), sourced under §12.1 with three logged rejections above it.

**§12.1 step 3 was tightened as a direct result of this draw, and the reason is worth
recording: the first version of the automated check selected a GROUND LEASE.** Its title —
"GROUND LEASE BETWEEN TESORO ALASKA COMPANY LLC, AS LANDLORD, AND TESORO **LOGISTICS**
OPERATIONS LLC, AS TENANT" — contains the type term inside a **party's name**. Requiring
only that the term appear in the title was therefore not enough; the term must **qualify
the type noun** (within two words of `AGREEMENT`/`CONTRACT`). This is the third distinct
variant of the same error class (E06: a whole 10-K; E04: a whole 8-K; this: a party-name
match), and the first produced by the automated rule written to prevent the other two —
which is the argument for keeping the manual body-verification step even now that the
check is code. `is_contract()` carries regression coverage: it accepts E07, and rejects
both the ground lease and E04.

---

## 13. Selection-bias audit (session 1)

Recorded because the finding is real and the corpus was rebuilt because of it.

**What happened.** The v0.1 corpus was selected by hand-writing a list of 16
"obligation-dense" agreement types and drawing seeded-random within each. That type
filter **excluded 319 of 510 CUAD documents — 63% of the corpus.** (The count is 510,
corrected in v0.7 from a stale 506: CUAD v1's `full_contract_txt/` holds exactly 510
`.txt` files, verified directly against the Zenodo archive — see §18.) The stated motivation
was obligation density, and that does appear to have been the actual motivation: sentence
length and cross-referencing were never measured or looked at during selection.

**But intent is not the test.** Sampling 8 documents from the excluded types and profiling
them against the 12 selected showed the filter had removed the harder classes:

| | docs | median len | p90 len | x-ref % | >400ch % |
| :--- | --: | --: | --: | --: | --: |
| v0.1 selected | 12 | 264 | 611 | **13** | 25 |
| Types excluded | 8 | 282 | 693 | **23** | 31 |

Strategic Alliance (30 docs), Content License (16), Intellectual Property (13), Joint
Venture (9) — the structurally messiest classes — were exactly what the filter removed.

Two smaller defects found in the same audit: 4 of 16 CUAD downloads failed and the result
(12) was accepted without replacement because it coincided with the target; and the EDGAR
picks were chosen by search-relevance rank rather than drawn randomly.

**Corrections applied.** Six documents imported from the excluded hard types by seeded
draw; the 4 failed picks traced to genuine absence from CUAD's `full_contract_txt` subset
(they exist only as PDF) and replaced by seeded draw within the same types; all 6 EDGAR
documents redrawn by seeded random from full hit lists.

**The fix is partial, and that is stated rather than glossed.** The corpus now *contains*
a genuinely hard tail — 7 of 28 documents at ≥20% cross-reference density, up to 49%, with
p90 sentence lengths to 1,406 characters, holding 22% of all obligation sentences. But the
**pooled cross-reference rate is still 13%**, against 23% in the excluded-type sample:
adding 6 documents to 22 imports a hard tail without moving the centre. This corpus is
therefore *harder than v0.1 and still not representative of CUAD's harder half.* §2.2's
25-item floor is what guarantees the hard documents actually reach the gold set; without
it, the tail could be sampled away.

**The general lesson**, in the same shape as Standing Principle 6: a selection filter
justified on one axis (density) can silently correlate with another (difficulty). Any
future corpus, eval slice, or fixture set selected by a hand-written category list should
be profiled against what the list excluded — before it is used, not after.

---

## 14. Annotator uncertainty

The rules above cover *known* failure modes. This section covers the case where the
annotator reads a real sentence and does not know what the correct gold answer is.

### 14.1 Three states, kept strictly apart

| State | What it means | Route |
| :--- | :--- | :--- |
| `CONFIDENT` | One reading, and I hold it | Annotate normally |
| `AMBIGUOUS` | **The sentence** admits ≥2 defensible readings that yield *different* gold values | §14.3 |
| `UNCERTAIN` | I believe one right answer exists; I could not determine it | §14.4 — escalate |

`AMBIGUOUS` is a property of the text. `UNCERTAIN` is a property of the annotator.
Do not merge them: the first is a finding about contract language, the second is a
finding about this process, and they call for different responses.

### 14.2 `underspecified` is NEVER a confidence signal — prohibited

**Do not mark an item `underspecified` because you are unsure of the answer.**

`underspecified` has a closed structural definition (§3.9): an `ABSENT` party, an
unresolvable `DateRef`/`TriggerRef`, or a `bd` duration. It is a fact about what v1 can
resolve, not about annotator confidence, and it is a **scored field in the conjunctive
predicate** (§5, clause 8). Using it to record doubt would score the pipeline against the
annotator's uncertainty instead of against the document — silently, and in a direction
nobody could later detect.

A sentence can be maximally confusing and still be `underspecified = false`. A sentence
can be perfectly clear and `underspecified = true`. The two axes are independent.

### 14.3 `AMBIGUOUS` — resolve by accept-set where possible, escalate where not

- **If the ambiguity falls in an accept-set field** (`action` §3.4, `object_class` §3.6):
  widen the accept-set to cover every defensible reading. This is what accept-sets exist
  for, and it is the correct, cheap resolution. Record both readings in
  `annotator_notes`.
- **If the ambiguity falls in an exact-match field** (`modality`, `obligor`, `obligee`,
  `temporal` form or constituents, `conditions` count, `underspecified`): **escalate**
  (§14.4). These fields have no representational room for "either answer is fine," so
  choosing one would score the pipeline against a coin flip.

### 14.4 Escalation — and why there is no "default to X" rule

An escalated item goes to the reviewer with: the segment, both/all candidate readings,
**which specific fields differ between them**, the annotator's best attempt, and what
information would resolve it.

**A "when uncertain, default to X" rule is deliberately rejected.** A default converts
random annotator error into *systematic* error pointing in one fixed direction — and if
the extraction model shares that same bias (both being trained on the same contract
language), the default rewards the pipeline for agreeing with a coin flip we pre-loaded.
Random error widens the confidence interval; systematic error moves the point estimate.
For a measurement instrument, the second is strictly worse.

**Escalation budget: ≤2 per batch of 10.** A batch exceeding it is evidence the guideline
is underspecified for that document class, and the correct response is a **guideline
amendment** (§10), not five individual adjudications. Repeated uncertainty is a missing
rule, and converting it into one is the entire point of the pre-freeze period.

**Outcomes**, both recorded:
- Reviewer decides → annotate per that decision; record `adjudicated_by: reviewer` and
  the reasoning. The item stays in the 100.
- Reviewer judges it genuinely ambiguous with no single right answer → the item is
  excluded, logged `AMBIGUOUS_EXCLUDED`, and a replacement is drawn by the §2.1 mechanism.

**Exclusion cap: ≤5 of 100.** Uncapped exclusion of hard items is exactly the
difficulty bias of §13 reappearing one level down, at item scope instead of document
scope. Every exclusion is listed in the final report with its segment text.

**Escalated items leave the holdout-eligible pool** (§7) — the reviewer has seen them, so
they can no longer serve as blind checks; the batch's holdout draw comes from the
remaining items. **Accepted limitation:** this makes the holdout sample systematically
*easier* than the gold set, since escalated items are by definition the hard ones. The
alternative — a contaminated holdout — is worse. Mitigation is disclosure: the escalation
count is reported alongside K, so a reader knows how much of the hard tail the tripwire
did not cover.

### 14.5 Rule citation is mandatory, not a habit

Every item records `rules_cited`: the § numbers actually invoked for any non-obvious
field. Example: `["§3.5 ABSENT-obligee", "§4.3 not-split (compound object)", "§3.7
vague-temporal→null"]`.

An annotation that applies a judgment call without citing the rule behind it is
**incomplete** and is returned in review, the same standing as a missing field. Every
§2 segment exclusion cites its rule (§2.1); every batch review packet carries a
rules-invoked column; every item stamps its `guideline_version` (§1).

This is the same discipline the codebase already applies to blueprint sections: a
decision traceable to a numbered rule can be audited and reversed. One that lives only in
a conversation cannot.

---

## 15. Vague temporal qualifiers ("promptly", "immediately")

**Status: v0.4 default, pending confirmation.** Raised in session 2 before any item was
drawn, because the pattern is common enough to move criterion 2 on its own.

### 15.1 Measured frequency

In the 960-segment eligible pool: **111 segments (12%) carry a vague temporal qualifier,
and 80 of those carry no quantified temporal form at all.** Sampled proportionally that is
roughly 8 of the 100 gold items. Frequency: `promptly` 63 · `immediately` 38 · `timely`
13 · `as soon as practicable` 6 · others 4.

### 15.2 The rule

For an obligation whose only timing signal is a vague, non-quantified qualifier:

| Field | Value | Why |
| :--- | :--- | :--- |
| `temporal` | `null` | None of the five frozen forms can represent it (§3.7, unchanged) |
| `underspecified` | **`false`** | See §15.3 — this is the non-obvious half |
| `vague_temporal_phrase` | the literal phrase | **New non-scored field**; verbatim from `span_text` |
| `annotator_notes` | records the phrase and this rule | §14.5 |

### 15.3 Why `underspecified` is `false` here, despite the semantics

`underspecified` has exactly three structural triggers in v1 (§3.9): an unresolvable
`DateRef`, an unresolvable `TriggerRef`, a `bd` duration. **`temporal is None` is a
deliberate, documented non-flag** — `compiler/typecheck.py:156` returns `None` without
appending to `missing_fields`, and that module's own docstring explains why: by the time an
AST exists the word "promptly" is gone, so `temporal: None` is genuinely indistinguishable
from an obligation that correctly has no timing element. CLAUDE.md's typechecker checkpoint
assigns recognising vague temporal phrases to a future extraction/critic stage.

Annotating `underspecified = true` would therefore make **every** such item fail clause 8
of the conjunctive predicate (§5) automatically — not because extraction was wrong, but
because gold asserted a capability v1 explicitly declined to build. That is measuring a
scope decision as a defect, silently, with no signal separating it from genuine extraction
errors.

This is **not** the §8 pattern. §8's known gaps fail *loudly* — `UNMAPPABLE_TEMPORAL`
surfaces in criterion 1b as a visible compile failure. A vague-temporal mismatch would fail
*silently* as a `PARTIAL` in criterion 2 with no attribution.

### 15.4 The gap is reported, not buried

`vague_temporal_phrase` is **excluded from the scoring predicate** and reported as its own
headline figure alongside criterion 2 (§9):

> *N of 100 gold items carry a vague temporal qualifier that v1 represents as no timing
> at all.*

Same shape as §9's "report alongside, never fold in" and §14's refusal to collapse distinct
things into one field. The resulting count is direct evidence for the deferred critic-stage
decision, which buried `PARTIAL`s would not be.

### 15.5 Boundary cases

- **Vague qualifier + a quantified form** ("shall promptly, and in any event within 30 days,
  notify") → annotate the quantified form normally (`WITHIN`, 30, d). Record the vague word
  in `vague_temporal_phrase` as well. Real drafting pairs them often.
- **Vague qualifier on a non-obligation** ("this Agreement shall terminate immediately upon…")
  → not an item at all; excluded under §3.2's future-fact rule.
- **"Immediately upon X"** → this is a `RELATIVE_TO_TRIGGER` with direction `after` and
  trigger `X`, **not** a vague qualifier. The word "immediately" modifies a real trigger, so
  the timing *is* specified relative to an event. Annotate the temporal form; do not set
  `vague_temporal_phrase`.
- **"within a reasonable time"** → vague. `temporal = null`, this rule applies.

---

## 16. Efforts qualifiers ("reasonable efforts", "best efforts")

**Status: v0.5 default, pending confirmation.** Raised in session 2 from a pool scan,
before any item was drawn.

### 16.1 The defect this corrects

v0.4's §3.2 table mapped `shall` → `MUST` **and** "will use reasonable efforts to" →
`SHOULD`. The dominant real form is **"shall use reasonable efforts"**, which matched both
rows simultaneously. §3.3 forbids accept-sets for modality, so each such item would have
been resolved by whichever row the annotator read first — 28 segments in the 960-segment
pool (3%), silently inconsistent.

### 16.2 The rule

**The modal verb governs modality. An efforts qualifier belongs to the action, never to the
deontic force.**

| Text | Modality | Note |
| :--- | :--- | :--- |
| shall use reasonable efforts to X | `MUST` | Obligation *of means*: trying is mandatory |
| shall use commercially reasonable / best / good faith efforts to X | `MUST` | Same |
| will use reasonable efforts to X | `MUST` | Per §3.2's undertaking rule for `will` |
| may use reasonable efforts to X | `MAY` | Modal governs |
| should use reasonable efforts to X | `SHOULD` | Modal governs |

Rationale: "shall use reasonable efforts" is a **binding** obligation whose *result* is
qualified, not whose *duty* is optional. Failing to try at all is a breach. `SHOULD` in IR
v1 asserts the duty itself is advisory — a materially different and stronger claim than the
text makes.

### 16.3 Consequences for other fields

- `action` — take the verb governing the qualified act (`AUDIT`, `INDEMNIFY`, `DELIVER`),
  not "USE". Author a generous `action_accept_set` (§3.4): efforts phrasing frequently makes
  more than one taxonomy verb defensible.
- `object_class` — describes the act being attempted, not the effort.
- `underspecified` — **unaffected.** An efforts standard is not one of §3.9's three
  structural triggers, and §14.2's prohibition applies: the qualifier makes the duty harder
  to *evaluate*, not structurally unresolved.
- IR v1 has **no field representing an efforts standard.** This is a real expressiveness gap
  and is not recorded per-item; it is noted here once so a future reader does not mistake
  `MUST INDEMNIFY` for an unqualified duty.

---

## 17. Internal booleans inside one condition

**Status: v0.6 default, pending confirmation.** Companion to §3.8. Distinguishes two shapes
that look alike on a fast read and must be scored differently.

### 17.1 The two shapes

| Shape | Example | Gold |
| :--- | :--- | :--- |
| **Two separable conditions** | "**If** the Agreement is renewed **and if** Customer requests it in writing, Vendor shall…" | **Two** `Condition` entries |
| **One condition, internal boolean** | "If Customer requests it in writing **or** by email, Vendor shall…" | **One** `Condition`, verbatim, boolean unparsed |

**Diagnostic:** count the scoping markers, not the connectives. A repeated `if` (or
`provided that`, `in the event that`) scopes a second, independently-satisfiable
condition → two entries. A single `if` governing a coordinated phrase → one entry, kept
verbatim including its internal `and`/`or`/`not`.

### 17.2 One entry with an internal boolean is CORRECT, not a failure

A single `Condition` whose text contains `and`/`or`/`not` is **the correct gold answer**.
It is not a `PARTIAL` on clause 7 of the predicate (§5), and it is not a defect to be
recorded as a known gap.

### 17.3 Where this boundary actually lives — and why that matters

**Not** the IR spec's frozen scope. `compiler/ast.py` defines real `AndPredicate`,
`OrPredicate`, and `NotPredicate` (lines 215/224/240), and `grammar/obligation.lark` has
explicit `->` rule aliases so the two are distinguishable in the parse tree. **IR v1 can
represent boolean structure.**

The boundary is `compiler/ir_compile.py`'s deliberate decision: each `condition_raws`
entry becomes exactly one `AtomPredicate` wrapping its raw text verbatim, never structured
by detecting connectives inside the string. Its reasoning, on record: boolean connectives
in free legal text are genuinely ambiguous — `"not later than"` contains "not" but is not
a boolean negation — a misclassification hazard a closed-vocabulary regex cannot safely
resolve. Only `parser.py`, parsing literal DSL `AND`/`OR` keywords, can produce a compound
predicate today; the extraction path never does.

**Consequence:** this is a revisitable compiler decision, not a frozen spec boundary. If
measurement shows internal booleans are common and materially wrong, that is a finding
that could change `ir_compile.py` — unlike §8's gaps, which are scope freezes. Recording
the distinction here so a future reader does not treat it as immovable.

### 17.4 Related known gap, deliberately not in scope here

`ir_hash.py` does **not** canonicalize AND/OR operand order *within* one predicate tree
(a documented gap with its own regression test). Dormant on the extraction path for the
same reason as above: `ir_compile.py` never builds a compound predicate from LLM output.
Named so the two facts are not later conflated.

### 17.5 Frequency

The 960-segment pool contains **2** segments with chained conditions (0.2%). This class is
rare in the real corpus; the rule exists for correctness, not volume. **Did not reproduce
in v0.7's re-measurement — see §18.4.**

---

## 18. Corpus verification (v0.7)

Recorded because the gap this closes was real and the result is load-bearing for every
number above.

### 18.1 The gap

This guideline and `corpus_manifest.json` were committed. **The corpus they describe was
not, and neither was the code that produced any statistic in either file.** The 28
documents lived only in a session scratchpad, which is deleted between sessions. The
hashes therefore survived; everything derived from them became unreproducible. A reader
could not confirm any density figure, and no corpus change could be re-measured.

`apps/brain/evals/corpus.py` closes it: `fetch` re-acquires all 28 documents from their
archival sources, `verify` hash-checks them, `profile` recomputes every per-document
statistic, and `pool` rebuilds the eligible-segment pool §§15–17 cite. Its metric
definitions are the specification — previously there was none.

### 18.2 Hash verification — unambiguous, and it passes

**All 28 documents re-acquired and verified byte-for-byte: 22/22 CUAD, 6/6 EDGAR, zero
mismatches.** CUAD from Zenodo (DOI `10.5281/zenodo.4595826`, `CUAD_v1.zip`, SHA-256
pinned in the script), EDGAR from the per-document URLs in the manifest.

**The corpus is exactly what the manifest says it is.** This is the one check in §18 with
no interpretation in it.

**CUAD license re-confirmed at the source**: the Zenodo record's own metadata returns
`"license": {"id": "cc-by-4.0"}`. CC BY 4.0 permits redistribution with attribution, which
every published eval number must carry (§12).

### 18.3 What re-measurement confirms

The original metric definitions were never written down, so the recomputation uses new,
explicitly-documented ones. **A delta is therefore ambiguous** between a wrong prior number
and a differing definition, and is not treated as convicting either. What matters is which
*findings* survive an independent measurement:

| Claim | Original | v0.7 re-measurement | Verdict |
| :--- | :--- | :--- | :--- |
| §8 `WITHIN` parenthetical share | 74% (119/161) | 84% (152/180) | **Confirmed** — differs in count, agrees in finding |
| §15 vague-temporal share of pool | 12% (111/960) | 12% (202/1679) | **Confirmed — exact rate match** |
| §16 efforts-qualifier share of pool | 3% (28/960) | 3% (52/1679) | **Confirmed — exact rate match** |
| §17 chained conditions | 0.2% (2/960) | 0.9% (15/1679) | **Not reproduced** — see §18.4 |
| Per-document raw counts | manifest | 134 of 196 values differ | Ambiguous by construction |

§15's and §16's rates reproducing **exactly**, off a pool built by a different rule, is
strong evidence both were genuinely measured.

**With one caveat found the hard way (§18.6): these rates are sensitive to segment size,
not just to segment count.** A defective intermediate enumeration that produced maximal
~2,000-character segments measured the same two properties at 24% and 7% — because a
longer segment has more chances to contain a qualifier. The agreement above therefore says
the original pool was built from *paragraph-sized* segments like the corrected one (median
561 characters), and is not a claim that any pool of any shape would reproduce it. A future
re-measurement must report its segment-size distribution alongside the rate, or the number
is not comparable.

### 18.4 §17's frequency did not reproduce, and is corrected downward in confidence

v0.7 measures chained conditions at 1.0% of the pool against the claimed 0.2% — a 5×
difference in rate, not a counting quibble. Both measurements agree the class is **rare**,
which is the only load-bearing part of §17.5's reasoning ("the rule exists for
correctness, not volume"), so §17's rule stands unchanged. But the specific figure `2` is
**no longer cited as established**; use the reproducible measurement or none.

### 18.5 What is still not verified

- **§13's selection-bias audit.** Its comparison table comes from re-running the original
  selection against the excluded types. Re-deriving it means redoing the sampling, not
  just re-profiling the 28 documents that were kept. The audit's conclusion is unaffected
  by anything in §18, and equally is not corroborated by it.
- **The eligible-segment pool is not the same pool.** v0.7's enumeration applies only
  §2.1's two mechanical criteria (length band, modal presence); the original 960 was
  reached some other way. §§15–17's *rates* reproduce, so the two pools appear to sample
  the same population — but they are not the same pool, and the 960 figure itself is not
  confirmed.
- **Nothing here is an annotation.** No gold item exists. §18 verifies the corpus and the
  statistics reasoned from it, nothing downstream of either.

### 18.6 The segment-enumeration defect (found before batch 1 was drawn)

The first enumeration split documents on single newlines. It put **24% fragments** into
the pool — entries beginning or ending mid-clause, which no annotator can annotate — and
they were **difficulty-correlated**: 48% of EDGAR segments against 21% of CUAD's, and 32%
of the hard stratum against 20% of the standard one.

**That is why this mattered enough to stop batch 1 for.** A drawn segment rejected under
§2 is replaced from its own stratum's queue, so the hard stratum would have been depleted
fastest — eroding §2.2's 25-item floor while every individual rejection looked perfectly
justified in its own log entry. It is the same class of difficulty-correlated selection
bias §13's audit was written about, arriving through a different mechanism, and it would
have been invisible in the finished gold set.

**Root cause: line structure is not consistent across this corpus and cannot be relied
on.** C04 stores one paragraph per line; C02 is hard-wrapped at ~93 characters *with blank
lines between the wrapped lines*, so blank lines are not paragraph boundaries there; EDGAR
emits a newline per block tag. No line-based rule survives all three.

Two candidate fixes were measured and one was rejected:

| Approach | Fragments | Verdict |
| :--- | :--- | :--- |
| Split on single newlines | 24% | Rejected — the original defect |
| Group whole sentences to the 2,000-char ceiling | 4.8% | **Rejected** — produced maximal blobs violating §2's "1–3 obligation-bearing clauses", and distorted §§15–16's rates to 24%/7% |
| Reconstruct paragraphs by sentence continuation | **4.6%** | Adopted (`reconstruct_paragraphs`) |

**Difficulty correlation is resolved**, which was the actual reason to stop:

| Slice | Before | After |
| :--- | :--- | :--- |
| Hard stratum | 32% | **4.6%** |
| Standard stratum | 20% | **4.5%** |
| CUAD | 21% | 3.4% |

The hard and standard strata are now within 0.1 points of each other. Pool: **1,679
segments** (408 hard, 1,271 standard), median segment 563 characters.

**The residual 4.6% is mostly the fragment detector's own false positives**, not
fragments: 34 complete clauses opening with a list marker (`(b) Except where AMAG is
required by Applicable Law…`), 24 opening with `$` in insurance-limit tables, 7 redaction
headers, 2 CUAD page-footer artifacts, 1 bankruptcy docket header. The last three classes
are removed by §2's semantic exclusions regardless.

**Separate finding, still open: E06 is not a contract.** It is `a04-3512_110k.htm`, a
complete Form 10-K annual report for AES Red Oak LLC (1.09 MB) — cover page, MD&A,
financial statements. The manifest labels it `contract_type: "maintenance"`, but
"MAINTENANCE AGREEMENT" appears **zero** times in it; the single "Maintenance Agreement"
hit is an MD&A heading *describing* a contract executed elsewhere. It contributes 194 pool
segments (11.6%) of disclosure prose and accounts for 114 of EDGAR's 137 residual
fragments — excluding it takes the pool to 4.6% overall and EDGAR to 13.1%. This was a
corpus-composition defect in the committed manifest, not an enumeration defect.

**Resolved in v0.10: E06 retired, replaced by E07** (manifest v0.4). E07 is Instinet
Group's `SOFTWARE MAINTENANCE AGREEMENT` (EX-10.35, accession 0000950123-02-002976,
30,246 bytes), drawn by seeded random — seed `20260817`, the reviewer's — from an EDGAR
full-text hit list of 352 exhibit-shaped candidates, per §13's own method, with **five
logged rejections above it**.

**The selection check that E06's original selection lacked:** a candidate now qualifies
only if `MAINTEN` appears in the document's **own title**, not merely somewhere in its
body. This was added after the first pass of the redraw selected an *LLC Membership
Interest Purchase Agreement* that mentions maintenance agreements 24 times — reproducing
E06's exact failure mode inside the fix for it. Body-frequency is not evidence of document
type; only the title is.

E06 is retained in the manifest under `retired_documents` with its real SHA-256, so the
substitution is auditable rather than silent. It was standard-stratum (`xref_pct` 1), so
§2.2's hard floor was unaffected and the hard queue is unchanged by the swap. Pool after
replacement: **1,514 segments** (408 hard, 1,106 standard); §15's and §16's rates still
reproduce at 12% and 3%.
