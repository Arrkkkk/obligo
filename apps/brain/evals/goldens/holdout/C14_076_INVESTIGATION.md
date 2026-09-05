# `C14-076` band risk — investigation of the 2026-09-04 §2.7 retrofit finding

Scope: the two un-annotated sentences the §2.7 (v0.50) per-sentence disposition retrofit
surfaced on `C14-076`, and the two sub-questions `CLAUDE.md` scoped for them —

- **(a)** does bare cost-allocation language with no stated act-verb clear §2.5's
  monitorable-stakes bar?
- **(b)** how does §3.5.3's agentless-passive rule handle a sentence naming **no party at
  all**?

**Nothing is ruled here.** Both candidates are escalated under §14.4 and both are scheduled
as their own sessions. What this note establishes is that one premise of the finding is
false, that its stated arithmetic is wrong in a way that changes which candidate is urgent,
and that the false premise is an instance of a **repo-wide record-scope gap**, not a
one-segment slip. Scripts and their known-answer checks: `band_risk/`.

**Scope note added 2026-09-05.** *"Nothing is ruled here"* refers to the two **candidates**,
and still holds — both remain escalated. **§8, appended later the same day, DOES rule one
thing**: the §5/§5.1 both-`ABSENT` scoring question §3.2 raised is answered and §5 is confirmed
final. **That ruling is not a prerequisite for either candidate** and does not touch candidate
2's field assignment — see §8.0, which states the non-dependence in full.

---

## 0. The three corrections, up front

| # | the finding as recorded 2026-09-04 | what the artifacts say |
| :-- | :--- | :--- |
| 1 | *"Neither the gold drafter nor the independent cold annotator flagged this sentence … neither recorded why"* | **False for the cold annotator.** `holdout/cold/17_C14-076.json`'s `segment_notes` disposes of **both** sentences explicitly, with rules cited |
| 2 | *"IF BOTH CLAUSES ARE GENUINE, the segment totals 4"* — a conjunctive risk | **Candidate 2 alone is decisive.** It carries two verbs with **different obligors**, so it cannot be one item; candidate 2 genuine ⇒ segment = 4 ⇒ over band, whatever candidate 1 turns out to be |
| 3 | (a) framed against §2.5 | **§2.5 is the wrong section** — its operative trigger is *unreviewable discretion*, which candidate 1 has none of. The governing family is §8.8's copular status-vs-conduct class, and candidate 1 falls in a **cell of it that has never been adjudicated** |

---

## 1. Correction 1, generalised: the record audit's scope, and a repo-wide re-check

### 1.1 Why the false premise arose

`splitting/records.py`'s own docstring scopes it correctly:

> *"The record audit: is there ANY **gold-side** disposition for each surplus clause? Three
> sources are searched exhaustively: `exclusions.json` …, the populated §21 R6
> `not_annotatable` spans, and every gold item's `annotator_notes` …"*

That is the right question for §2.1 step 4's bias safeguard, whose rejection sample can only
sample **gold-side** logs — and §2.7 exists precisely because that record was empty. The
defect is not in `records.py`. It is that the retrofit **generalised its result** from *"no
gold-side disposition exists"* (true, and the whole point of §2.7) to *"neither annotator
recorded why"* (false, and load-bearing, because it was then offered as **evidence for one
of two competing readings**: *"which is some evidence both readers judged it
non-obligation-bearing on sight"*).

`holdout/cold/*.json` is a fourth source. All 22 files carry a substantive `segment_notes`
(734–3,260 characters); **16 of 22 explicitly discuss excluded sentences**. No script reads
any of it. `disposition_cost.py` carries both `C14-076` anchor phrases at its line 124 and
searches the same three gold-side sources.

### 1.2 The re-check across all 22 retrofitted segments — `band_risk/cold_dispositions.py`

Of **44** non-`ANNOTATED` dispositions:

| verdict | n | |
| :--- | --: | :--- |
| `COLD_ITEM` — the cold annotator **annotated** the span | 8 | all on the six count-disagreeing segments; **tautological**, these *are* the nine surplus clauses |
| `COLD_NOTE` — disposed in cold prose, with rules cited | **17** | across 10 segments; **never read by any script** |
| `NONE` | 19 | headings, connectives, corpus artifacts — exactly §2.7's permitted bulk-disposition classes |

**Every one of the 10 `AMBIGUOUS` / `NOT_ANNOTATABLE` spans — the consequential ones — has a
cold-side disposition. Eight are full cold gold items with field-level adjudication and
`rules_cited`; two are reasoned prose exclusions. None is genuinely undisposed.**

Narrowing to the **21 undisposed sentences `SPLITTING_EXCLUSION_INVESTIGATION.md` §3 actually
reaches** (`disposition_cost.py`'s own anchor set, now carrying a cold-side column), the
result is starker: **21 of 21 have a cold-side disposition** — 7 cold items, 14 cold notes —
**including all 10 that the gold-side search reports as `NONE`, "nothing anywhere."** The
gold-side tally is unchanged at 10 of 21 disposed; it is the *"anywhere"* that was wrong.

That source claim is corrected at its origin: `SPLITTING_EXCLUSION_INVESTIGATION.md` §3's
heading is accurate (*"7 of 9 have no **gold-side** disposition of any kind"*) while its body
sentence — *"7 of 9 surplus clauses have no record **anywhere**"* — is not, and now carries a
correction note in place rather than an edit.

### 1.3 Answering the scheduling question directly: yes, the pattern recurs

Three retrofitted segments assert an explicit false negative, **five spans in total**:

| segment | span | the retrofit's claim | the artifact |
| :--- | :--- | :--- | :--- |
| `C11-094` | *"In the case of transfer by devise or inheritance…"* | *"No disposition of any kind exists on record — investigation table says 'none — nowhere'"* | **cold item 2**, IoU 0.996 |
| `C11-094` | *"If the conveyance of the Principal's interest…"* | same | **cold item 3**, IoU 0.995 |
| `C04-117` | *"Miltenyi, acting reasonably, reserves the right to defer…"* | *"No disposition of any kind exists on record for this clause"* | **cold item 3**, IoU 0.994 |
| `C14-076` | *"Each party will be solely responsible…"* | *"neither annotator flagged this sentence … neither recorded why"* | **reasoned §8.8 exclusion** in cold `segment_notes` |
| `C14-076` | *"Israel value added tax shall be added…"* | *"neither annotator flagged it, but neither recorded a reason"* | **reasoned exclusion, with the competing §3.5.3 reading written out in full** |

A cold **item** is a stronger disposition than a prose exclusion, not a weaker one: cold did
not merely say why not, it said what the clause *is*, field by field.

Four further segments — `C17-021`, `C17-066`, `E03-005`, `E08-005` — make no silence-claim
but likewise had unread cold dispositions available for their `AMBIGUOUS` /
`NOT_ANNOTATABLE` spans.

**The corrections do not all cut the same way, and that is stated rather than smoothed:**
`C11-094`×2 and `C04-117` cut **toward** the clause being obligation-bearing (cold annotated
them); `C14-076`'s candidate 1 cuts **toward exclusion** (cold excluded it, on §8.8 grounds
this note independently reaches).

### 1.4 One cold disposition is contaminated and must not be relied on

Cold's second stated ground for rejecting candidate 2:

> *"admitting it would take the segment to 3-4 obligation-bearing clauses, **pressing §2's
> 1-3 band for no gain**."*

That is reasoning backwards from the eligibility outcome — precisely what `C14-139`'s own
process fix forbids (*"eligibility is decided before content is adjudicated, and the reviewer
explicitly declined to let sunk analysis cost bias the eligibility call"*). Cold's
**candidate 2** disposition is contaminated on this ground; its **candidate 1** disposition
is not, and rests entirely on §8.8/§8.8.1.

### 1.5 Consequence

The §2.7 retrofit's *dispositions* stand — the spans, offsets and rule citations are
unaffected. What is corrected is the **evidential claim of silence** in five `AMBIGUOUS`
readings, and the standing of the retrofit as a complete record. `records.py` and
`disposition_cost.py` now search `holdout/cold/*.json` as a fourth source, labelled
**cold-side** so it is never confused with the gold-side record §2.1's safeguard needs.

---

## 2. Sub-question (a): candidate 1 — cost allocation with no act-verb

> *"Each party will be solely responsible for any and all taxes imposed thereon, including,
> without limitation, all income taxes, sales taxes, goods and services taxes."*

### 2.1 §2.5 does not reach it, and none of its worked examples is structurally similar

Checked directly. §2.5/§2.5.1's three worked cases are **all discretion clauses**:
`C04-026` (*"reserves the right, at its sole discretion and without any restriction or
limitation whatsoever"*), `C11-046` (*"shall be made by BKC in its sole business
judgment"*), and the v0.41 negative example `C14-044` S1 (*"without any implication"*).
§2.5.1's operative rule requires **"unreviewable discretion and no correlative party,
deadline, or gating condition"** as its trigger. Candidate 1 vests no discretion at all.

So the sub-question as scoped points at a section that genuinely does not reach the clause.
That does **not** make the clause novel by itself: §2.5 states its own test as *"does the
clause have a future state worth monitoring"* and names it *"the identical underlying
principle §3.2.1 already applies"*. Three sections share that principle through different
surface patterns — §3.2.1 (performatives: effect complete at execution), §2.5/§2.5.1
(discretion: no standard to check against), §8.8/§8.8.1 (copular status: no conduct
commanded). Candidate 1 belongs to the **third**.

### 2.2 The citation that looked like it settled the question does not survive checking

Cold cites `C04-163` as *"the same construction affirmatively phrased"*. It is not:

> *"Bellicum **shall not** be responsible for **payments** relating to any portion of the
> Forecast applicable to any period after the effective date of termination."*

`C04-163` differs from candidate 1 on **two axes at once** — polarity *and* complement type
— so it cannot settle candidate 1 by citation. §8.8.1's *"negation placement does not decide
the class"* governs where negation sits **within** a status clause; it does not say polarity
cannot distinguish a conduct clause from a status one.

**This was found by a detector failing its own known-answer check, not by re-reading the
rule.** `responsible_for.py`'s first draft predicted `C04-163` would classify as an act
complement and it returned "thing" — because the ACT vocabulary held `payment` and the text
says `payments`. Reading the flagged case is what showed the complement **is** an act
nominalisation, falsifying the complement-type-alone hypothesis the script was written to
confirm.

### 2.3 The census, and the unadjudicated cell

`be/remain responsible|liable for` across the 1,547-segment pool: **121 sentences in 106
segments (6.9%)**. All five known-answer cases classify correctly.

| complement | affirmative | negative |
| :--- | --: | --: |
| **act nominalisation / gerund** | **47** — `C02-045` ✅ annotated (`C02-04`, `PAY`), `C14-139`(4) ✅ counted, `C14-028`(5) ✅ counted | **22** — `C04-163`(2) ❌ excluded |
| **bare burden** (cost / tax / expense / loss) | **15 — UNADJUDICATED, `C14-076` cand. 1** | *(within the 22)* |
| other | 37 | |

Every precedent reading "annotatable" is affirmative + act-nominalisation. The single
precedent reading "excluded" is negative. **The affirmative + bare-burden cell has no
adjudicated instance anywhere in the gold set**, and it is not a one-off: **15 instances
across 9 documents** (`C02`, `C03`, `C10`, `C11`, `C14`, `C15`, `C17`, `E03`, `E08`),
including `C15-050`'s near-twin *"be responsible for all Taxes or surcharges levied or
imposed on it by any Governmental Authority."*

### 2.4 Status: ESCALATED as §10 amendment territory, NOT ruled

Under §14.4 — *"repeated uncertainty is a missing rule, and converting it into one is the
entire point of the pre-freeze period"* — 15 instances across 9 documents is a guideline
amendment, not a per-item adjudication.

**A starting point, explicitly not a ruling:** act-nominalisation complement →
obligation-bearing; bare-burden complement → §8.8 status class. It correctly classifies all
four established precedents and is mechanically checkable. **It must be drafted against
`C03-024` directly** — *"AT&T Mobility LLC shall **remain liable for** such Affiliate's
**failure** to satisfy its obligations hereunder"* — whose complement is a bare noun but
whose function is accountability allocation, near-identical to `C14-139`(4)'s
reviewer-ruled-obligation-bearing *"remain fully responsible for the performance of all
obligations."* The line is sharp for cost allocation and fuzzy for accountability
allocation, and the edge needs drafting rather than discovering later.

---

## 3. Sub-question (b): candidate 2 — the fully partyless passive

> *"Israel value added tax shall be added, if applicable, to all amounts payable hereunder
> and will be paid against submission of appropriate tax invoices."*

### 3.1 §3.5.3's rule text already covers it; the worked cases do not

Verbatim from §3.5.3:

> *"`obligee` = the party named inside the span … **Where no party is named at all**, or more
> than one candidate is equally available, `obligee` = `ABSENT`."*

The no-party case is anticipated **in terms**, and `obligor = ABSENT` is the rule's headline.
The finding is right that no *worked case* reaches it and wrong that the *rule* does not.
Field assignment is therefore decidable by citation: `obligor: ABSENT`, `obligee: ABSENT`,
`underspecified: true` (§3.9 trigger 1), both roles in `missing_fields`.

Thing-subject alone does not exclude it, either: `C14-05` (*"All such rescheduling shall be
performed by sending Contractor a written request for rescheduling"*) is a locked item with a
thing subject and an agentless passive. The discriminator is passive-of-a-performance-verb
versus copular status predicate, and `be added` / `be paid` are the former — `be paid` maps
to `PAY`, an exact taxonomy member.

### 3.2 The genuinely novel part is downstream, in §5

**No locked item has both party slots `ABSENT`.** Across all 32: the only two obligor-`ABSENT`
items, `C04-03` and `C14-05`, both carry an in-span obligee, exactly as §3.5.3's reviewer
ruling intended; 11 items have obligee `ABSENT` with a named obligor.

§5 states *"`ABSENT` matches `ABSENT`."* Candidate 2 would therefore be the **first gold item
where two of the eight scored clauses pass on a vacuous match**. That is a §5/§5.1 question —
*is `§5` one predicate or two* — not a field-assignment question, and it has never been asked.

### 3.3 The shape recurs — `band_risk/partyless.py`

Over the 10 documents carrying a committed §21 R3 registry (the other 18 have no authored
alias list, so a partyless verdict there would be unfalsifiable): **221 of 2,015
modal-bearing sentences (11.0%)** name no party at all. Narrowed to agentless passives of
performance verbs — candidate 2's actual shape, excluding copular/status participles and
contract-artifact subjects — **62 (3.1%), across 59 segments**: *"Documentation shall be
mailed to the appropriate address"*, *"PO's will be issued at least two (2) weeks prior to
the designated Due Date"*, *"All requests for changes to Purchase Orders shall be submitted
in writing"*, *"A copy of the additional insured endorsement must be provided within sixty
(60) days."*

---

## 4. Correction 2: the band arithmetic, and why candidate 2 is the urgent one

**Candidate 2 is two clauses, and the argument does not need §4.3's judgment call.** The party
that *adds* VAT to its invoice is the payee; the party that *pays* it is the payer.
**Different obligors — and one item has one obligor slot.** It cannot be a single item however
the performances are read. (§4.3 gives the same answer independently: an invoice can carry
correct VAT and go unpaid, or omit VAT and be paid — the independently-breachable signature.
`C14-139`'s own exclusion counted its split clauses (5)–(6) separately in the band count, so
counting at splitting granularity is established practice.)

| candidate 1 | candidate 2 | segment total | §2 band |
| :--- | :--- | --: | :--- |
| excluded | excluded | 2 | ✅ |
| excluded | **genuine (2 clauses)** | **4** | ❌ **over** |
| genuine | excluded | 3 | ✅ |
| genuine | genuine | 5 | ❌ over |

The 2026-09-04 finding frames this as conjunctive — *"if this and the next sentence are both
genuine"* — and it is not. **Candidate 2 alone puts `C14-076` over §2's 1-3 band**, and
therefore alone determines whether `C14-01`/`C14-02` keep their locked status. Candidate 1 is
the question with corpus-wide reach; candidate 2 is the question that decides this segment.

Note what is and is not at stake: `C14-01`/`C14-02`'s **field-level annotations** are not in
question, only the segment's **eligibility**. `C14-02` is separately §22.1's deliberately
retained non-conformance and the single unmatched gold item of the §7.1 cold run.

---

## 5. Status

| item | disposition |
| :-- | :--- |
| Candidate 1 (cost allocation) | **ESCALATED (§14.4) → §10 guideline amendment, own session.** Reaches 15 instances / 9 documents. Starting point in §2.4; must be drafted against `C03-024` |
| Candidate 2 (partyless passive) | **ESCALATED (§14.4) → own session, and the more urgent of the two.** §3.5.3 answers the fields; the open question is the §5/§5.1 both-`ABSENT` scoring consequence, and it alone decides `C14-076`'s band eligibility |
| Record-scope gap | **CLOSED HERE.** `records.py` / `disposition_cost.py` now search `holdout/cold/*.json`; all 22 segments re-checked; five false silence-claims corrected |
| `C14-01` / `C14-02` field annotations | **NOT in question.** Only the segment's eligibility is |

## 6. What this note deliberately does not do

It does not rule either candidate; it does not restamp any item; it does not touch a
cassette (no item `guideline_version` changes, so `Cassette.verify()` is unaffected and §22's
conforming blocker is not engaged); and it does not re-open the six count-disagreeing
segments' own dispositions beyond recording that cold-side evidence exists for them.

---

## 7. Addendum (2026-09-05) — the `C11-094` / `C04-117` escalation re-read

§1.3 established that three retrofitted segments assert a false silence-claim, and that two of
them — `C11-094` (×2) and `C04-117` (×1) — set their escalation scope partly on that premise.
Those escalations are re-read here against the cold-side dispositions that actually exist,
**before** either §14.4 session is scheduled, so no session starts on a scope fixed under a
premise now known to be wrong.

**Verdict: neither is resolved outright; both are narrowed; one carries a correction that
changes what its session must do.**

### 7.1 `C11-094` #2 — *"the executor shall use best efforts to transfer…"* → NARROWED, and the retrofit's own best attempt is WRONG

The escalation's second reading was, in full: *"No annotator or reviewer has ever recorded a
reason for treating this differently from `C11-01` in the same segment; the omission may simply
be an unrecorded judgment call this retrofit cannot reconstruct."* That is precisely the
analysis cold performed, under the rule that governs it:

> *"A DISTINCT obligation from the segment's first item, **checked against §4.3.1 step 1 rather
> than assumed**: the two clauses share an obligor role and an object but differ on conditions …,
> on temporal …, and on the efforts standard, so not every scored field is identical and §4.3.1
> sends them to §4.3's ordinary two-item treatment. No restatement marker appears either."*
> — `annotator_confidence: CONFIDENT`, 14 rules cited.

The reading's entire content is falsified. What remains open is narrower and different: gold's
omission is still unexplained, and **cold is a second annotator, not the reviewer** (§14.4). The
reviewer now approves or rejects a drafted, rule-cited candidate rather than reconstructing the
question from scratch.

**THE CORRECTION, and it is the reason this re-read was worth doing before the session.** The
retrofit's *"Genuine MUST item (best attempt)"* reading asserts
`temporal: RELATIVE_TO_TRIGGER` — *"(within 12 months **of** the Principal's death)"*. Checked
against the real segment text rather than the paraphrase, the document reads:

> *"…to transfer the Principal's interest to another party approved by BKC **within twelve (12)
> months from the date of the Principal's death**."*

The reading silently substituted `of` — the single preposition `_WITHIN_RE` accepts — for the
`from` the contract actually uses. On the real text this is a **`WITHIN` construction, not
`RELATIVE_TO_TRIGGER` at all**, and §8.6's rule for exactly this is explicit: **`temporal: null`,
`known_gaps: ["within_preposition"]`**. `from` is one of the three rejected prepositions §8.6
measured (17 pool occurrences), and `twelve (12)` additionally hits §8's *separate*
parenthetical-numeral gap, which §8.6 is explicit must not be filed with it. Cold has both right,
and additionally splits `conditions` into **two** entries (§3.8.2 Rule B / §17.1's marker count)
where the retrofit's reading has one.

**A reviewer approving the retrofit's draft would have been approving a wrong item.** Draft from
cold's item, corrected as needed — not from the retrofit's reading.

### 7.2 `C11-094` #3 and `C04-117` #1 — the two `MAY` clauses → NARROWED to Decision 3 alone

Both escalations bundle a **substantive** question with a **procedural** one. Cold settles the
first and structurally cannot touch the second.

**Substantive — does the clause clear §2.5/§2.5.1? Concordant, and settled on the merits.**
On `C11-094` #3 cold reaches the retrofit's reading 2 with the same two discriminators: an
observable gating condition (whether conveyance occurred inside the twelve months) and *"at fair
market value"* as §2.5.1's own reviewable-standard discriminator, explicitly contrasted with
`C04-026`. On `C04-117` #1 the convergence is near-verbatim — cold lists the **identical three
stakes in the same order** (*"acting reasonably"*, the bounded end-point *"until the Parties have
reached agreement"*, the narrow specific object) and independently distinguishes §2.5.1's
`C14-044` negative example. Two annotators who could not see each other, same answer, same rule
path, both `CONFIDENT`.

**Procedural — Decision 3's retroactivity. Completely untouched.** Cold annotated from the
**current** guideline, so its agreement establishes what these clauses are under §2.5/§2.5.1 — it
says nothing about whether a clarification added at **v0.39/v0.41** reaches segments locked at
**v0.28** (confirmed: `C11-01` and `C04-01` both stamp `guideline_version: v0.28`; §2.5 is v0.39,
§2.5.1 is v0.41). That is a policy call with precedents pointing both ways — §3.6.1's retroactive
correction against §22.1's deliberate retention — and no amount of annotator agreement resolves
it.

**Scope consequence worth acting on:** with the merits settled concordantly for both spans,
**Decision 3 is now the single remaining question for both, and one policy call disposes of both
together** — not two sessions each re-arguing eligibility.

### 7.3 The standing of concordance, stated rather than left implicit

Per §7.1's own disclosures, agreement between these two annotators is a **lower bound on error,
not proof**: correlated model-family error applies, guideline leakage applies, and no reviewer was
blinded. Two annotators agreeing is evidence that raises the reviewer's starting point; it is not
a ruling and does not close §14.4.

### 7.4 One genuinely new item, surfaced by the re-read — filed as F13, not folded in

Cold flagged a guideline conflict in `C11-094` item 2's notes and resolved it unilaterally:

> *"I note the tension between §8.6's `temporal: null` instruction and §3.7's 'known-gap forms are
> annotated NORMALLY' plus §8.9's annotate-the-form rule; I follow §8.6 as literally written and
> apply the same resolution to `C17-066` in this pass so the two are consistent."*

It is real. For the **same** structural problem — a preposition the production regex does not
accept — the guideline gives opposite instructions:

| section | gap | instruction |
| :--- | :--- | :--- |
| **§8.6** | `within_preposition` (`_WITHIN_RE` wants `of`) | **`temporal: null`** |
| **§8.9** | `relative_trigger_preposition` (`_RELATIVE_RE` wants `before`/`after`) | **annotate the form** + trigger verbatim |
| **§3.7** | general | *"Known-gap forms (§8) are **annotated normally**. Do not avoid them."* |

§8.6 is the outlier against both, and it also makes gold assert `temporal: null` where the text
plainly carries a timing phrase — which §3.7 permits *"only when the obligation genuinely carries
no timing phrase."* §8.9 (v0.28) was written explicitly as §8.6's sibling and never reconciled it.

**Measured: the inconsistency is in the GUIDELINE, not in the annotation.** Both annotators
follow each section literally and consistently — `within_preposition` → `null` (gold `C17-02`;
cold `C17-066`, `C11-094` #2) and `relative_trigger_preposition` → the form (gold `C13-03`,
`C22-02`; cold ×5). Exposure, from §8.6's own measurement: the word after `within N <unit>` runs
`of` 40 vs `after` 34 / `from` 17 / `following` 8 — **59 pool-wide occurrences on the rejected
side**.

**Filed as guideline §10.1 F13. NOT a prerequisite for either escalation** — it is a field-level
question that arises only if `C11-094` #2 is annotated at all, and cold's resolution is already
consistent with locked `C17-02`.

### 7.5 Confirmed scope going into the sessions

| span | verdict | what its session actually decides |
| :--- | :--- | :--- |
| `C11-094` #2 | **NARROWED** | Approve/reject cold's drafted item. **Do NOT use the retrofit's best-attempt reading — its `temporal` is wrong** (§7.1) |
| `C11-094` #3 | **NARROWED to Decision 3 alone** | Retroactivity only; merits settled concordantly |
| `C04-117` #1 | **NARROWED to Decision 3 alone** | Retroactivity only; merits settled concordantly |
| §8.6 vs §8.9/§3.7 | **NEW** | Own ruling, F13; not a prerequisite |

---

## 8. Addendum (2026-09-05) — the §5/§5.1 both-`ABSENT` scoring question, ANSWERED

§3.2 above named the genuinely novel part of candidate 2 as downstream, in §5: *"Candidate 2
would be the **first gold item where two of the eight scored clauses pass on a vacuous
match**. That is a §5/§5.1 question … and it has never been asked."* §5 above records it as
the more urgent of the two escalations. It was asked, and this section answers it.

**Framed generally, as scoped: this is a question about the scoring predicate, not about one
segment.** It reaches the **62 partyless agentless performance passives (3.1% of modal-bearing
sentences)** §3.3 measured over the 10 registry-backed documents, and the 13 locked items that
already carry an `ABSENT` slot.

**Verdict: §5 handles a both-`ABSENT` item and needs no amendment — the concern ran backwards.
Two real defects surfaced in the course of checking it and are filed as §10.1 F14 and F15.**
Adopted as final at guideline v0.51. Scripts and their known-answer checks: `band_risk/`.

### 8.0 THIS SECTION IS NOT A PREREQUISITE FOR `C14-076`'s BAND-ELIGIBILITY RULING

Stated first, and at this length, because the escalation record made the §5 question sound like
a gate and it is not one. A future reader must not treat F14 or F15 as blocking.

- **Candidate 2's field assignment stands on existing rule text, whatever F14 and F15 decide.**
  §3.1 above already settled it by citation: §3.5.3's rule text anticipates the no-party case
  **in terms** (*"Where no party is named at all … `obligee` = `ABSENT`"*), and `obligor =
  ABSENT` is that section's headline. The fields are `obligor: ABSENT`, `obligee: ABSENT`,
  `underspecified: true` (§3.9 trigger 1), both roles in `missing_fields`. **Nothing below
  changes any of those five values.**
- **F14 is a prompt-wording question** — whether the model can be made to emit an empty obligor
  alias. That governs how a candidate-2-shaped item *scores*, never whether it is annotatable
  or how it is annotated.
- **F15 is a predicate-composition question** — whether clause 8 stays scored. Same: it moves a
  scoring figure, not an eligibility or field decision.
- **The band question is decided on §2's clause count**, which §4 above already showed candidate
  2 alone settles (two verbs, different obligors, so it cannot be one item; genuine ⇒ segment =
  4 ⇒ over band). That argument runs entirely on §4.3 and §2 and touches §5 nowhere.

**So the ordering is free.** `C14-076`'s eligibility session may be scheduled before, after, or
independently of F14 and F15, and F14/F15 may be resolved without reopening `C14-076`. The one
thing that would be wrong is deferring the band ruling *because* F14/F15 are open.

### 8.1 The premise is falsified: `ABSENT` is a HARDER target than a named party

`band_risk/party_alias_check.py`, over the 35 gold cassettes, aligned with the harness's **own**
`align()`/`iou()` rather than a reimplementation — 44 aligned (item, run) pairs, 17 distinct
items:

| clause | gold `ABSENT` | gold NAMED |
| :--- | ---: | ---: |
| 3 `obligor` | **0/3 = 0.0%** | 32/41 = 78.0% |
| 4 `obligee` | **13/17 = 76.5%** | 24/27 = 88.9% |

**Read the direction, which is the whole result.** A vacuous clause would score *above* the
named-party rate. Neither does. On the obligor slot the gap is not marginal — it is total.

**The mechanism, and it is a rule the guideline already states.** §5 can express "absent" only
as an empty alias, and the model supplies a hallucinated party instead. `C04-03` emits
`"Miltenyi"` on **all three runs** — precisely the possessive-on-a-**location** inference
§3.5.3's reviewer ruling forbids in terms (*"A possessive on a place is not a duty-bearer;
reading one as the obligor is §3.5's forbidden inference"*). That is a clause failing on a rule
gold states explicitly, not the model being imprecise. `C17-02` gives `"the counterparty"` ×2,
`C11-01` `"BKC"` ×1, `C04-02` `"the Parties"`.

**Stated limitation.** The obligor-`ABSENT` cell is one item × 3 runs (`C14-05`'s segment
`C14-044` is not cassette-covered), so it is n=3 and weak alone. It is load-bearing only in
combination with §8.2's 0/81, which is the same phenomenon measured on a much larger base. And
`party_alias_check.py` is **not the scorer** — it does not run the pipeline, so candidates that
would have been rejected or quarantined are still counted, which biases the pass rates
**upward**: the conservative direction for a vacuous-pass claim.

### 8.2 The cause is the prompt, and the asymmetry is one-sided — §10.1 F14

`band_risk/alias_census.py`, over all **81** emitted candidates in the 35 cassettes:

| slot | empty | rate |
| :--- | ---: | :--- |
| `obligee_alias` | 40/81 | **49.4%** |
| `obligor_alias` | **0/81** | **0.0%**, Wilson₉₅ upper **4.53%** |
| both | 0/81 | 0.0% |

`prompts/extraction/v3.yaml` states **no rule permitting an empty alias anywhere**. Its only
signal is one worked example carrying `"obligee_alias": ""`, with **no obligor counterpart**.
§3.5 already called that *"undesigned behavior, not a chosen rule"* — the measurement shows the
undesign is **one-sided**, and that one-sidedness is what produces the 0%.

**So clause 3's rate on an `ABSENT` slot is not measuring extraction quality. It is measuring an
unstated prompt convention.** Same class as the already-tracked `condition_raws` *"'if'-type"*
alignment question: a scored clause whose pass rate is fixed by prompt wording.

**Not a capability gap — verified by execution, not by reading** (`band_risk/both_absent_exec.py`,
on candidate 2's real text). Every prior instance of this shape in this repo was settled wrongly
by reading — the `UNLESS` carve-out, the `AndPredicate`/`OrPredicate` gap, the trailing-period
bug — each a guarantee held at the grammar/DSL layer that the real extraction path bypassed. Run
instead: grounding **accepts** an empty alias (`_is_grounded_substring`: `if not needle: return
True`, by design), `_build_dsl` emits `MUST "" PAY "" value_added_tax …`, and the parser returns
`UnresolvedParty(alias='')` on **both** slots. **The ABSENT branch is reachable; the 0/81 is
behavioural.**

### 8.3 What §5.1 has to say, and it is less than expected

`A` (v0.45) governs **annotator comparison** and never scores a prediction, so the both-`ABSENT`
question does not reach it — with one exception worth recording. **A3 compares parties as
strings with no registry branch**, so under `A` a both-`ABSENT` item agrees iff both annotators
wrote `ABSENT`. That is genuinely vacuous for `A`, but it is the *existing* A3 design decision
(*"deferred, not adopted … revisit when a cold run puts a genuine same-party/different-alias
pair in front of it"*), not a new consequence of both-`ABSENT`, and A3's own deferral note
already covers it.

### 8.4 The genuinely vacuous clause is 8, not 3 and 4 — §10.1 F15

`band_risk/clause8_vacuous.py`. On a span naming **no registered party**, this is a proof rather
than a rate:

1. `ground_candidates()` requires each alias to be a substring of the grounded span.
2. `symbols.resolve_party()` matches only a registered `canonical_name` (case-insensitively) or
   a registered alias (case-**sensitively**, §21 R2).
3. So if no registry party name occurs in the span, **no grounded alias can resolve**, whatever
   the model emits.
4. `typecheck._resolve_party()` appends **both** roles to `missing_fields`; `underspecified =
   bool(missing_fields)` is `True` unconditionally.
5. Gold says `True` (§3.9 trigger 1). **Clause 8 passes for any prediction whatsoever, including
   a wholly wrong one.**

Checked against the real `C14` registry: candidate 2 → **zero** hits. Known-answer check:
`C04-03`'s span → `Bellicum`, `Miltenyi` found, so the detector is not merely always answering
"no party here".

**And clause 8 is not an independent eighth check set-wide.** Across the **24** locked items
whose documents carry a committed §21 R3 registry, `underspecified` is predicted with **zero**
mismatches by *NOT(obligor resolves AND obligee resolves AND temporal is null)*. The 8 items on
registry-less documents are **skipped rather than counted as non-resolving** — the question is
unfalsifiable there, the same scope restriction `partyless.py` already applies.

**The §5 tension this exposes, stated plainly.** §5's own closing line reads *"`missing_fields`
is **reported but excluded** from the predicate"*, while §3.9 states *"`typecheck.py` computes
`underspecified = bool(missing_fields)`"*. **§5 excludes the field and scores its boolean.**

**A DETECTOR FAULT CORRECTED MID-INVESTIGATION, kept in the script rather than only here**
(Standing Principle 7, and the third such correction this `band_risk/` directory records). The
first draft tested `ABSENT`-ness instead of **resolvability** and reported **4** mismatches —
`C14-01`, `C14-02`, `C02-04`, `C06-01`. Reading them showed every one is a **named but
unresolvable** party (a collective, a distributive, or a relational reference), which §3.9
trigger 1 covers explicitly. **The looser predicate was the defect, not the data**, and the
corrected run is 0 of 24.

### 8.5 The "first item where 2 of 8 pass vacuously" count is wrong as stated

| absence-matched scored slots (clauses 3/4/6) | locked items |
| ---: | ---: |
| 0 | 2 |
| 1 | 20 |
| 2 | **10** |

**10 of 32** locked items already carry two absence-matched scored slots — obligee `ABSENT` plus
`temporal: null` — and 30 of 32 carry at least one. Gold `temporal` is null on **27/32 (84.4%)**.

A both-`ABSENT` item would be the first with two **party** clauses absent. That is a smaller and
different claim than the one §3.2 recorded, and it is corrected here rather than edited there.

### 8.6 Status

| item | disposition |
| :-- | :--- |
| §5's `ABSENT matches ABSENT` | **CONFIRMED FINAL, no amendment.** It is the strictest cell in the party clauses on this evidence; amending it would fit the predicate to a sample of one, which is what §22.1 exists to prevent |
| Unstated empty-alias prompt convention | **FILED — §10.1 F14.** Tier C, bundled with the approved-and-never-run `v4` probe |
| Clause 8 / `missing_fields` tension | **FILED — §10.1 F15.** Both candidate resolutions stated; **not decided here** |
| `C14-076` band eligibility | **UNAFFECTED — see §8.0.** Not gated on F14 or F15 |
| Candidate 2's field assignment | **UNCHANGED** — `obligor: ABSENT`, `obligee: ABSENT`, `underspecified: true`, both roles in `missing_fields`, per §3.5.3 and §3.9 |
| `C14-01` / `C14-02` field annotations | **STILL NOT in question**, as §4 already recorded |

### 8.7 What this section deliberately does not do

It rules neither F14 nor F15; it does not restamp any item; it does not touch a cassette (no item
`guideline_version` changes, so `Cassette.verify()` is unaffected and §22's conforming blocker is
not engaged); it does not change any published figure, including criterion 2's `3/9 = 33.3%`; and
it does not rule `C14-076`'s band eligibility, which remains escalated on its own merits.
