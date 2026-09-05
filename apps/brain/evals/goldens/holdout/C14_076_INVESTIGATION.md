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
