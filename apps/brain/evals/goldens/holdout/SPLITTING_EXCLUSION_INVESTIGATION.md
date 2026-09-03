# Splitting/exclusion — investigation of REDESIGN scope item 2 (the item-count directional signal)

**Run 2026-09-03, against the sealed cold output (`cold_manifest.json`, rolling SHA-256
`e5d0b42a…d87623`), the 32 locked gold items, `comparison.json`, and the 35 gold cassettes.**
Nothing here changes a rule, restamps an item, reverses an exclusion, or invalidates a cassette.
**No rule is proposed** — the REDESIGN response's own discipline is that a precedent-setting
convention is investigated before it is drafted, and this note is the investigation half only.
Four open decisions are *scoped* in §8; none is taken.

Companion to `RESULTS.md`, whose channel-4 finding this note takes apart, and sibling to
`OBJECT_CLASS_INVESTIGATION.md`, which does the same job for REDESIGN scope item 1. It does not
supersede `RESULTS.md`: the six disagreeing segments and their transitions reproduce exactly.
What changes is one count, and the **diagnosis** — and therefore what a fix would have to be.

Every number below is produced by a preserved script in `splitting/`; see that directory's
README for what each one does and which known answer it is checked against.

---

## 0. Reproduction, and the known-answer check on it

`RESULTS.md`'s channel-4 table was recomputed from source rather than quoted
(`splitting/counts.py`). Item counts were taken directly from the sealed cold files and the
locked gold items, not from `comparison.json`, so the two are independent.

| | `RESULTS.md` | this reconstruction |
| :--- | ---: | ---: |
| cold items | 41 | **41** |
| gold items | 32 | **32** |
| segments | 22 | **22** |
| segments disagreeing on item count | 6 | **6** |
| the six transitions | `C04-117` 2→3 · `C11-094` 1→3 · `C17-021` 1→3 · `C17-066` 1→3 · `E03-005` 1→2 · `E08-005` 1→2 | **identical** |
| direction | every disagreement is cold finding *more* | **confirmed, 6/6** |
| surplus cold items | 10 | **9** — see below |

### 0.1 One count correction: the item-count surplus is 9, not 10

`RESULTS.md`'s channel-4 table reads *"Surplus cold items 10 / Unmatched gold items 1."* Those
are two different quantities and only the first is stated as a channel-4 number:

- **Unmatched cold items = 10.** Correct, and it is what `comparison.json` reports
  (`unmatched_cold: 10`; 32 gold − 1 unmatched gold = 31 matched; 41 − 31 = 10).
- **Item-count surplus across the six disagreeing segments = 9.** `comparison.json`'s own
  `per_seg` rows carry the discrepancy in plain sight: seven segments have unmatched cold items,
  and the seventh is **`C14-076`, where the counts agree 2/2.**

`C14-076`'s tenth item is not a splitting or exclusion disagreement at all. Both annotators
found the same two obligations in the same sentence; they differ on **span mechanics**:

```
gold C14-01 [ 12:178]   cold1 [ 12:178]   -> pair, IoU 1.000
gold C14-02 [184:253]   cold2 [ 12:253]   -> IoU 0.286, no pair
```

Cold used §8.3.1's **v0.31 option-4** containing span for the shared-subject second duty; gold
keeps the **v0.23** bare span that §22.1 *deliberately retains* un-conformed. This is the
tracked non-conformance surfacing as an alignment artifact — `RESULTS.md` itself names `C14-02`
as the single unmatched gold item and attributes it to §22.1 correctly, three paragraphs above
the table that then counts its partner into channel 4.

**Consequence for scope, and it is the reason this is corrected rather than noted.** Reading 10
into channel 4 attributes one item to the splitting/exclusion class that belongs to an
already-decided, already-documented item. The class is 9.

---

## 1. The nine, in full

Each row is one obligation-bearing clause that cold annotated and gold did not, with **every**
gold-side disposition that exists for it anywhere in the repository (§3 documents the search).

| # | segment | the clause | gold's recorded reason | cold's rule and reasoning |
| :-- | :--- | :--- | :--- | :--- |
| 1 | `C04-117` | *"Miltenyi, acting reasonably, **reserves the right to defer** the inclusion of additional Miltenyi Products in Exhibit B hereto until the Parties have reached agreement on this matter"* | **none — nowhere** | §2.5/§2.5.1 monitorable-stakes test, run explicitly *because* "reserves the right to" is §2.5's own motivating phrasing. Clears on three independent stakes: a reviewable standard (*"acting reasonably"* — §2.5.1's own named discriminator), a bounded observable end-point (*"until the Parties have reached agreement"*), and a narrow specific object. Distinguished from `C04-026` and from §2.5.1's `C14-044` negative example |
| 2 | `C11-094` | *"In the case of transfer by devise or inheritance, if the heir is not approved or there is no heir, **the executor shall use best efforts to transfer** the Principal's interest to another party approved by BKC within twelve (12) months from the date of the Principal's death"* | **none — nowhere** | §4.3.1 step 1 applied against the segment's first item rather than assumed: differs on `conditions`, on `temporal`, and on the efforts standard, so not a restatement → §4.3's ordinary two-item treatment. §16.2 for `MUST` from *"shall use best efforts"*; §8.6 `within_preposition` (*"from"*, not *"of"*) |
| 3 | `C11-094` | *"If the conveyance … has not taken place within the twelve (12) month period, **BKC shall have the option, to purchase** the Principal's interest at fair market value"* | **none — nowhere** | §2.5/§2.5.1: clears on an observable gating condition (whether conveyance occurred inside the twelve months) and a reviewable price standard (*"at fair market value"*). §3.2 `MAY`; §3.5.4 `obligee` `ABSENT` |
| 4 | `C17-021` | *"…in the event a virus … is introduced …, the other Party shall, as soon as practicable, use its commercially reasonable efforts **to assist** such Party in reducing the effects of the virus…"* | **none — nowhere** | §4.3 split of sentence 2: assisting and remediating are gated by different circumstances (the second needs an actual loss **and** a request) and are independently breachable. §3.1 minimal-complete-span excludes the *"Without limiting the rights and remedies"* savings opener under §3.8.1's not-branch-1 class |
| 5 | `C17-021` | *"…and if the virus … causes a loss of operational efficiency or loss of data, upon such Party's request, **work** as soon as practicable **to contain and remedy** the problem and to restore lost data"* | **none — nowhere** | Same §4.3 split, second half, with §8.3.1's **v0.31 option-4** nested span (the shared subject *"the other Party shall"* cannot be carried by a span starting at *"and if the virus"*). Tagged `shared_subject_split` + `compound_action`; marked `AMBIGUOUS` on a live §8.9-vs-§3.8.4 conflict, both readings written out |
| 6 | `C17-066` | *"**The contract** constituting the separated portion of any Multi-party Contract … **shall be assumed by and become the responsibility of the Company**"* | **none — nowhere** | §3.5.3 (passive clause with a non-party grammatical subject **is** an obligation; here an explicit by-agent exists, so §3.5.3's `ABSENT`-obligor branch does not fire). Marked `AMBIGUOUS`; reading 2 — §8.8's copular status class, under which the segment yields 2 items — is recorded and rejected |
| 7 | `C17-066` | *"**Each Party** making purchases or receiving services under any Multi-party Contract **shall indemnify and hold harmless the other Party** and its Affiliates…"* | **named in `C17-02`'s own notes as *"a section 8.4 mutual case"* — and given no disposition** | §8.4 mutual: `Each Party … the other Party` makes the co-obligor the obligee, so tag `mutual_obligation` and annotate one direction — the identical treatment gold's own `C17-01` applies to `C17-021`'s sentence 1 |
| 8 | `E03-005` | *"**The Parties shall discuss and review** the Order Forecast at each regularly scheduled meeting of the JSC established by the Parties under the Collaboration and License Agreement…"* | **`exclusions.json` `E03-005#discuss`, rule "section 2"** — cross-reference-dependent, plus two supplementary grounds | §2's **v0.28 scored-field-dependence** test: no scored field's value turns on resolving the JSC reference, and the reference sits inside verbatim-quoted span text, which §2's own row says is annotatable. §8.4.1 collective obligor; §8.3 `compound_action` |
| 9 | `E08-005` | *"**It** shall ensure that the DC is clean and maintains certification from all applicable regulators"* | **`E08-01`'s `annotator_notes`, §2.6 self-containment, reviewer-confirmed** | §3.5.1 step 1 branch 2: a subject **is** stated, `ABSENT` would be factually false, and §3.5's test is positional not resolution-based, so `It` is a determinate answer. Marked `AMBIGUOUS`; **gold's exact reading is recorded as cold's "READING 3 (rejected, and the most consequential)"**, naming the 1-item outcome it produces |

Nine items over **eight distinct sentences** — rows 4 and 5 are one sentence split two ways.

---

## 2. The premise of REDESIGN item 2 holds for 2 of the 9

Scope item 2 asks *"which specific §2 exclusion rules and §4.3 splitting tests produce it."*
The premise is that two annotators applied the same rules and read them differently. Measured
against the nine, that premise is the minority case.

### 2.1 No §4.3 / §4.3.1 / §4.3.2 splitting test was read differently anywhere in this run

Every splitting decision the two annotators actually **joined** agrees exactly. Verified span by
span across all five multi-item segments where both sides annotated the same sentences:

```
C04-139  gold C04-04/C04-05 [4:207] x2   cold [4:206] x2   <- the §4.3.2 flow-down split
C14-044  gold C14-04 [377:508] C14-05 [509:607]
         cold      [377:507]        [509:606]              <- both exclude S1 (§2.5.1's C14-03 retraction)
C02-021  gold 22 / 999 / 1147          cold 22 / 999 / 1147
C03-192  gold 24 / 763 /  998          cold 24 / 763 /  998
C13-017  gold 807 / 916                cold 807 / 916
```

Two of these are the strongest possible positive results and are recorded as such rather than
passed over:

- **`C04-139` — §4.3.2's own motivating case, the hardest splitting rule in the guideline —
  was independently reproduced**, two items over a byte-adjacent span, matched in
  `comparison.json` at IoU 0.995 with **zero clause failures on either item.**
- **`C14-044` — §2.5.1's retraction of `C14-03` was independently reproduced.** The cold
  annotator, with no access to that ruling's existence, excluded exactly the sentence §2.5.1
  retracts and produced exactly the two surviving items.

**The one splitting decision inside the surplus (rows 4 and 5) is unopposed, not disputed.**
Gold produced zero items from `C17-021`'s sentence 2, so there is no competing count. Filing
two surplus items under "a splitting test read differently" would attribute them to a test that
was never joined.

### 2.2 The four-way decomposition

| category | items | what it is |
| :--- | :--- | :--- |
| **A — un-recorded omission, no identifiable exclusion rule** | **4** (#2, #4, #5, #7) | Plain party-or-role-subject `shall` clauses. No §2 row reaches them, and no gold-side record exists |
| **B — rights-shaped, decided under v0.28 before §2.5 existed, un-recorded** | **2** (#1, #3) | See §4 |
| **C — a live rule boundary neither section settles** | **1** (#6) | §3.5.3's by-agent passive against §8.8's copular status class. Cold flagged `AMBIGUOUS` and wrote out both readings; gold left no trace |
| **D — genuine rule disagreement, gold's reasoning on record** | **2** (#8, #9) | The only two of the shape scope item 2 assumed |

**Category A is the sharpest, and #7 is the sharpest instance in it.** These are not marginal
clauses. §16.2 makes *"shall use best efforts"* a `MUST` and gold's own `C17-01` applies exactly
that rule to exactly that construction in the same batch. §4.3.1 step 2 — the only rule that
could suppress #2 as a restatement — requires marking the span `NOT_ANNOTATABLE` and recording
it verbatim, and its own status line reads **"STEP 2: UNTESTED — no instance has arisen in any
material seen so far,"** so it cannot have been applied. And #7 is a clause gold **identified in
writing**, **classified** under §8.4, and then neither annotated nor excluded.

---

## 3. The record audit — 7 of 9 have no gold-side disposition of any kind

`splitting/records.py` searches all three places a disposition could live, exhaustively.

**Result: 7 of 9 surplus clauses have no record anywhere.** One has an `exclusions.json`
entry (#8). One has an `annotator_notes` paragraph (#9). The single mention of any other is
`C17-02`'s aside naming `C17-066`'s third sentence as a §8.4 mutual case — which states a
classification and stops, giving no disposition.

*One grep hit is a false positive and is adjudicated by reading rather than counted:* `C04-02`
matches `defer` on *"the restamp was deliberately **deferred** to this freeze-pass batch"*, not
on the *"reserves the right to defer"* clause. Recorded per Standing Principle 7 — the totals
are not the evidence, the flagged context is.

### 3.1 Sub-sentence exclusion logging stopped after batch 1

```
exclusions.json sub-sentence ('#') entries:   batch01 = 4    batch02 = 0    batch03 = 0
                                              (E03-005#itemize, E03-005#discuss,
                                               E07-010#sentence2, E07-010#sentence3)
```

Batch 1 logged four, covering 2 of its 8 segments. Batches 2 and 3 logged none at all.

### 3.2 §21 R6's `not_annotatable` data is populated for exactly one span in the whole gold set

```
E03-005.json  [433:665]  "Grammatical subject is a document ('each Order Forecast'), not a party…"
TOTAL across the entire gold set: 1 span, in 1 of 12 cassette-covered segments
```

**`E03-005#discuss` is logged in `exclusions.json` and was never transcribed into that same
segment's own `not_annotatable` list.** R6 names **both** `#itemize` and `#discuss` by name as
its transcription source; the one segment where the mechanism was populated at all is missing
one of the two entries R6 cites.

### 3.3 What this does to §2.1's bias safeguard

§2 requires exclusions to be logged — *"not silently skipped — the exclusion log is part of the
deliverable"* — and §2.1 step 4 requires *"Every segment rejected as ineligible is logged with
its verbatim text and the rule invoked"*, feeding a reviewer sample **"so an exclusion that was
really a difficulty dodge is visible."**

Both requirements are **segment**-level. **§2.6 moved the self-containment test to sentence
granularity at v0.41 and did not move the logging requirement with it.** §4.4 defines the
`NOT_ANNOTATABLE` label; R6 defines its file format; **nothing anywhere obliges an annotator to
record a sentence-level non-annotation inside a kept segment.**

The consequence is structural, not incidental: **the reviewer's rejection sample can only sample
logged rejections**, so seven un-recorded omissions were never eligible to be reviewed — and
every gold item on all six segments is nonetheless `APPROVED` or `RULED_BY_REVIEWER`. Approval
of an item is not approval of a non-item, and nothing was ever put in front of the reviewer for
the clauses that were dropped.

---

## 4. Category B is measurable, and the measurement is a version boundary

`splitting/may_scan.py`. The detector prints every flagged sentence in full and asserts three
established answers before any total is read; two false positives (relative-clause `may` —
*"as may be required by Applicable Laws"*, *"the same conditions as may be imposed"*) are
adjudicated by reading and excluded.

| | |
| :--- | ---: |
| `MAY` items in the locked gold set | **1 of 32** |
| that item's `guideline_version` (`C13-03`) | **v0.41** — after §2.5 (v0.39) |
| `MAY` items among cold's 41 | 3 |
| genuine `MAY`-shaped clauses in the 22 segments | **4** |
| …decided at v0.41+ (`C13-041` annotated · `C14-044` S1 excluded with a written §2.5.1 ruling) | **2 — both AGREE with cold** |
| …decided at v0.28 (`C04-117` S4 · `C11-094` S5) | **2 — both DISAGREE, and both un-recorded** |

§2.5 states in terms that §2's bare row *"read literally would swallow the entire `MAY`
modality … That cannot be the intent, or no `MAY` item could ever be annotated at all."* A
v0.28 annotator reading that row literally excludes every `MAY` clause, and the gold set in fact
contains no `MAY` item until v0.41. The two `MAY`-shaped clauses decided under the pre-§2.5 row
are both surplus; the two decided after it both agree.

**On n = 2 this is consistent with a version effect and does not prove one.** It is recorded as
a measured alignment between a rule's arrival date and a decision boundary, not as a cause.

---

## 5. The batch trend is real and is confounded with difficulty — stated, not resolved

| batch | segments | gold/seg | cold/seg | surplus items | segments with surplus | mean modal-bearing sentences |
| :--- | --: | --: | --: | --: | --: | --: |
| batch01 | 8 | 1.25 | 2.12 | **7** | 4/8 | **3.12** |
| batch02 | 4 | 2.00 | 2.25 | 1 | 1/4 | 2.75 |
| batch03 | 10 | 1.40 | 1.50 | 1 | 1/10 | **1.50** |

7 of 9 surplus items are batch 1 — but batch 1 also drew far denser segments, and density
tracks surplus directly:

```
modal-bearing sentences, segments WITH surplus:    [2, 2, 3, 3, 5, 5]                     mean 3.33
modal-bearing sentences, segments WITHOUT surplus: [1,1,1,1,1,1,1,1,1,2,2,3,3,3,4,5]      mean 1.94
```

Conditioning on density ≥ 3 leaves batch01 at 3/5 segments, batch02 at 1/3, batch03 at 0/1.
**n is far too small to separate batch from difficulty, and no attempt is made here to** — the
same posture `RESULTS.md` correctly took for the leak-level gradient, which is confounded the
same way and for the same reason.

**What is NOT a rate claim and is exact:** 7 of 9 surplus clauses have no gold-side record; 1
has an `exclusions.json` entry; 1 has an `annotator_notes` paragraph. That count does not depend
on the confound.

---

## 6. The consequence is already inside the project's own published numbers

This is where the class stops being an annotation-quality question. §21 R6 states it directly:
*"a prediction on any un-annotated clause inside a gold segment scores `UNEXPECTED` — a false
positive charged to extraction for correctly reading a clause §2 excludes."* `align.py` confirms
the mechanism (`not_annotatable` defaults to empty; IoU ≥ 0.5).

### 6.1 The model finds the surplus clauses

**8 of the 9 surplus clauses sit in cassette-covered segments** (only `E08-005` is batch 3 and
uncassetted). **The model emitted a grounded candidate for all 7 distinct surplus sentences
among them** — three of them on every recorded run:

| clause | runs |
| :--- | :--- |
| `C11-094` *"In the case of transfer by devise or inheritance…"* | **3/3** |
| `C17-066` *"Each Party making purchases … shall indemnify…"* | **3/3** |
| `E03-005` *"The Parties shall discuss and review the Order Forecast…"* | **3/3** |
| `C04-117` *"Miltenyi… reserves the right to defer…"* | 1/3 |
| `C11-094` *"If the conveyance … BKC shall have the option…"* | 1/3 |
| `C17-021` *"…in the event a virus … use its … efforts to assist…"* | 1/2 (run 3 unobtainable, §6.1) |
| `C17-066` *"The contract constituting the separated portion…"* | 1/3 |

### 6.2 R6's over-count, measured for the first time

`splitting/unexpected.py` classifies every candidate in all 35 cassettes against **both**
annotators' spans using the harness's own rule, and asserts each cassette's `segment_sha256`
against the packet segment text before reading anything.

| classification | candidates |
| :--- | --: |
| aligns to a locked gold item | 46 |
| **aligns to no gold item but to a cold item — scores `UNEXPECTED` today** | **13** |
| aligns to no item on either side | 11 |
| ungrounded (fails the grounding gate, never reaches scoring) | 11 |
| **total** | **81** |

**Of the 24 grounded candidates that currently score `UNEXPECTED`, 13 — 54% — are on clauses an
independent annotator ruled genuine obligations.**

R6 says its over-count *"is a measured over-count, not an unknown one: the error is
one-directional and can only shrink."* The direction was right and the size had never been
measured. **On this sample it is over half.**

### 6.3 R6's own remediation assumption no longer holds

R6 states that populating §4.4 data is *"partly transcription from the exclusion logs, not
wholly fresh judgment."* That was true of batch 1's log when R6 was written at v0.28. Measured
now: the exclusion logs cover **1 of the 9** surplus clauses (`E03-005#discuss`, ~11%), batches
2 and 3 contribute **zero** sub-sentence entries, and the one logged entry that R6 names by name
was never transcribed into the file R6 designed for it (§3.2).

**The §4.4 population work is therefore ~89% fresh judgment on this sample, not transcription** —
which changes its cost estimate, and is recorded here because R6's *"Scheduling, stated so this
does not quietly become permanent"* paragraph rests on the transcription assumption.

---

## 7. The falsifiable claim in §2, tested — one entry of six does not survive

§2's cross-reference row makes a checkable assertion:

> *"Checked against all six existing cross-reference exclusions (`C04-018`, `C04-118`,
> `E03-005`, `C05-043`, `C11-079`, `C15-046`): every one is a genuine dependence case and
> survives this test unchanged, so this writes down existing practice rather than altering it."*

The test is: *"Excluded when **a scored field's value (§5's eight clauses) cannot be determined
without resolving the reference**."* Run against `E03-005#discuss`, clause by clause:

| § 5 clause | value | needs the JSC reference resolved? |
| :-- | :--- | :--- |
| 1 modality | `MUST` (*"shall"*) | no |
| 2 action | `DISCUSS`/`REVIEW` | no |
| 3 obligor | `The Parties` | no |
| 4 obligee | `ABSENT` | no |
| 5 object_class | the Order Forecast — **defined in this same segment** | no |
| 6 temporal | `null` — *"at each regularly scheduled meeting of the JSC"* has no amount, no unit, no `before`/`after` head and no two dates, so it fits none of §3.7's five frozen forms **whatever the JSC turns out to be** | no |
| 7 conditions | `[]` | no |
| 8 underspecified | `true` (§3.9 trigger 1, `ABSENT` obligee) | no |

**No scored field's value turns on the reference**, and §2's own row says a cross-reference
inside verbatim-quoted text *"requires no resolution and is annotatable."* The cold annotator
reached this independently, and recorded that a reader applying the **pre-v0.28 presence** test
would exclude the segment whole.

Two things sharpen this, and both are about the re-check rather than about the exclusion:

1. **The list names `E03-005` bare, and two entries carry that prefix.** Only `#discuss` is a
   cross-reference exclusion; `#itemize`'s rule is *"section 1 / section 3.5"* (non-party
   subject) and survives on entirely unrelated grounds. A re-check over a list whose entries are
   not uniquely identified cannot be re-run to a determinate answer — **Standing Principle 7's
   shape, reached through a third door: not a detector defaulting wrongly and not a status
   measuring the wrong command, but a known-answer list whose items are ambiguous.**
2. **Two of `#discuss`'s three stated grounds are contradicted by rules that predate it.**
   *"'discuss and review' has no clean taxonomy verb (nearest CONSULT)"* — §8.8 (v0.24) makes an
   off-taxonomy verb an `action_not_in_taxonomy` **tag**, explicitly not an exclusion.
   *"the obligor 'The Parties' is generic"* — §8.4.1 (v0.19) puts a collective reference in the
   slot **verbatim**, explicitly not an exclusion. Both rules existed when the exclusion was
   logged on 2026-08-20.

**The other five survive, and the finding is bounded to one entry, not to the re-check
wholesale.** `C15-046` (*"in the manner aforesaid"* — the **action's own manner** is outside),
`C11-079` (the consent mechanism gating the permission), `C05-043` (agreement-to-agree,
independently re-ruled 2026-08-22 against the amended rule), `C04-118` (prices and volume
thresholds wholly in Exhibit F), `C04-018` (three references, plus an independent rights-row
ground). `C04-118`'s own entry corroborates this note's central mechanism in the drafter's own
words — it records that sentence 3's duty *"is itself self-contained"* and excludes it anyway as
collateral of a segment-level judgment.

---

## 8. Four open decisions — scoped, NOT taken

Deliberately not ruled here, per this note's opening. They are genuinely independent; §9 records
the priority read rather than a sequence commitment.

**Decision 1 — does a kept segment require a complete disposition for every obligation-bearing
sentence in it?** The load-bearing one, and a real trade rather than an obvious fix. Cost:
materially more work per segment (batch 1's segments average 3.12 modal-bearing sentences, and
the disposition would need the same per-item adjudication a gold item gets). Benefit: §2.1's
bias safeguard and R6's `not_annotatable` data both become by-products of drafting rather than
separate scheduled work, and the class becomes *visible* — which is the property 7 of these 9
items lack. Note the interaction with §2's own **1–3 obligation-bearing-clause band**: a required
clause count would have caught `C11-094` (3 clauses, 1 annotated) and `C17-021` mechanically, at
annotation time, with no judgment involved.

**Decision 2 — `E03-005#discuss`.** A logged exclusion whose stated ground does not survive the
test §2 claims it was re-checked against (§7), and whose two supplementary grounds are
contradicted by rules that predate it. Reversing it adds a locked item on a cassette-covered
segment — §22 territory, all three of that segment's cassettes stale. Leaving it keeps a
known-wrong exclusion. **Structurally the same choice §22.1 already made for `C14-02`**, and
§22.2's *"is this the second instance?"* question is directly engaged.

**Decision 3 — the two v0.28-era `MAY` clauses (#1, #3).** Whether §2.5/§2.5.1's clarification
is retroactive over batch-1/2 segments, or whether v0.28-era rights decisions stand as made.
§3.6.1 is the precedent for a retroactive correction; §22.1 is the precedent for deliberate
retention. Both are on the books and they point opposite ways.

**Decision 4 — `C17-066` sentence 2 (#6).** §3.5.3's by-agent passive branch against §8.8's
copular status class — a boundary neither section settles, on which a careful annotator marked
`AMBIGUOUS` and wrote out both readings. Decidable entirely on its own; touches no other item.

---

## 9. Priority read

**Decision 1 outranks 2–4, and for the same reason Finding 1 outranks the rest of `RESULTS.md`:
it is about the instrument, not about an item.** Until a non-annotation is recorded, no future
item-count comparison can distinguish *a considered exclusion* from *an omission* — which is
precisely the ambiguity that leaves 7 of these 9 uninterpretable on their merits today, and it
would leave the next run's channel-4 number uninterpretable in exactly the same way. It is also
the only one of the four that is **forward-looking**: 2–4 each dispose of one already-drawn
clause, while 1 changes what every future batch produces.

**Decisions 2–4 are real and narrower, and none should be compressed to fit inside whatever
session rules on 1.** Each carries its own precedent weight — 2 engages §22's conforming
blocker directly, 3 asks a retroactivity question with precedents pointing both ways, 4 is a
clean two-way rule boundary — and none of the three is a prerequisite for any other.

---

## 10. What this note deliberately does not do

- **It does not rule that gold is wrong.** §7 is explicit that K counts *disagreements, not
  confirmed drafter errors*, and that holds here. For Categories C and D the cold annotator's
  reading is one of two defensible ones and says so itself. What is asserted is narrower and
  is a **process** claim: for 7 of 9, no reasoning of any kind was recorded, so no reading was
  ever available to be reviewed.
- **It does not reverse `E03-005#discuss`.** §7 tests §2's assertion about it and reports the
  result; reversing a logged exclusion on a cassette-covered segment is decision 2.
- **It does not restamp, widen, or conform any item, and no cassette goes stale.**
- **It does not resolve the batch-versus-difficulty confound** (§5), and does not treat the
  monotone batch trend as evidence of improvement.
- **It does not propose the §4.4 data population as scheduled work.** §6.3 corrects R6's cost
  assumption; what follows from that correction is decision 1's to settle.

---

## 11. Ruling log

*Empty. Nothing in this note has been ruled. Decisions 1–4 are open as of 2026-09-03.*
