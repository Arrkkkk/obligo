# Obligo Tier-2 Gold Set — Annotation Guideline

**Version:** v0.51 (DRAFT — not yet frozen; all 16 v0.28 proposals are ruled and adopted into live rule sections — see §20's status line and §20.4's adjudication log. **v0.29 added §6.1**, the two-run exception; **v0.30 reconciled §6.1's tie rule with `report.py`'s G2**; **v0.31 amends §8.3.1** — its v0.23 default is unreachable by the pipeline — and opens **§22**, the conforming blocker, **decided at v0.32 as a deliberate deferral**. **v0.33 puts §9's dual denominator IN FORCE** on two independent grounds, adds §5 clause 5's number rule, §3.4's bounded freeze-pass exception, and the forward authoring rules §3.6 / §3.8.2 / §3.5.1 — **no annotation rule changed, no item restamped, no cassette stale**. **v0.34 records two MEASUREMENT corrections and changes no rule either** — §8.9's `on`/`until` rows and §15.3's loud-versus-silent class placement, both falsified by real model output from the compile-stage bottleneck investigation. **v0.35 adds §4.3.2** — a third splitting shape distinct from both existing §4.3 worked examples, reviewer-ruled at batch 3's `C04-139`: self-performance vs. a duty to bind/control a third party's conduct splits into two items even when the two verbs share an object phrase and a sentence subject, because the two performances do not share an actor. **v0.36 amends §4.2** — the resulting byte-identical spans (`C04-139`'s shared trailing object leaves neither item's minimal span shorter than the other's) break IoU's ability to discriminate between the two gold items, so a content-based tie-break on `action_accept_set` membership is added, falling through to ascending `item_id` when the tie-break itself is inconclusive. **v0.37 adds a
recommended `object_class` naming convention to §4.3.2** — `self_` / `third_party_` prefixes over
a shared root, so future flow-down splits land on visibly parallel labels rather than an
unrelated pair invented fresh each time. **v0.38 adds §3.2.1** — present-tense self-executing
performatives (`hereby grants`/`assigns`/`appoints`/`releases`/`waives`) are excluded as not
obligation-bearing under IR v1, on the identical non-obligation principle §3.2's own
"will"-future-fact rule already states one tense later: nothing is left to monitor once a
performative act takes effect at execution, whether that happens in the present or the future.
Reviewer-ruled at batch 3's `C22-022`, where a hereby-clause sits coordinated with a genuine
future undertaking. **v0.39 adds §2.5** — clarifying, not replacing, §2's own "party's right, no
correlative duty" exclusion row: a `MAY`-shaped clause excludes only when it lacks monitorable
stakes (no correlative party, no deadline, no gating condition), the identical underlying
principle §3.2.1 already applies to present-tense performatives, reached from a different
surface pattern. Reviewer-ruled at batch 3's `C04-026`, a broad "reserves the right to
manufacture/sell/export/... in any manner and for any purpose whatsoever" boilerplate clause.
**v0.40 adds a marker-equivalence ruling to §3.8.1's branch 3** — confirms, for the first time
in practice rather than in the abstract, that a non-`unless` carve-out marker (`except to the
extent`, reviewer-ruled at batch 3's `C10-016`) routes through branch 3 exactly like `unless`
does, tagged `exception_unsupported`; names a small citable set of equivalent markers (`unless`,
`except to the extent`, `save where`, `other than in cases where`); and notes, without editing
it, that §8.2's own "Rule" paragraph still names the pre-rename tag `unless_unsupported` —
superseded at the original consolidation pass (§20.4 decision 5, 2026-08-22) but never
corrected in §8.2's own prose.)
**v0.41 change:** Four additions from batch 3's first three standard-queue candidates,
`C11-046`, `C11-101`, and `C06-016` — three forward rule extensions, one MEASUREMENT
CORRECTION. Neither
restamps a locked item nor stales a cassette. **(1) §2.5 gains a generalizing note (§2.5.1)**:
its "no monitorable stakes" test is confirmed to reach beyond `MAY`-shaped rights-reservations
to `shall`-shaped clauses carrying the identical unreviewable-discretion character. `C11-046`'s
*"The allocation of the Advertising Contribution between international, national, regional, and
local expenditures shall be made by BKC in its sole business judgment"* is excluded not on
grammar (`shall`, not `may`) but because *"in its sole business judgment"* leaves no standard
BKC could be held to and no way the clause could ever be breached — the identical absence of
monitorable stakes §2.5 already named for `C04-026`'s rights-reservation. Reviewer-ruled; cited
as the confirming instance. **(2) §2.4's "6 segments, contained" claim is CORRECTED, not merely
supplemented.** `C11-046`'s own corruption (`uncle` for `under`) matched neither of §2.4's two
catalogued signatures, which is what motivated a dedicated re-sweep of document C11 — same
rigor as the original detection pass, and validated against the six known instances before
trusting any new output (Standing Principle 7's own discipline) — rather than logging a
seventh isolated instance and moving on. **Corrected finding: the corruption class reaches 14
of C11's 128 pool segments (10.9%), not 6**, and two of the original six (`C11-006`,
`C11-063`) each carry a **second**, previously unrecorded corruption instance the original
pass never logged. Full corrected table and methodology in §2.4. **(3) §8.8 gains a
clarifying note (§8.8.1)**: its own copular "not an obligation clause at all" class
(*"shall not be liable/entitled"*) is confirmed to cover the **negated-entitlement** form
too — *"shall have no right of X"* / *"shall have any right of X...unless"* states a legal
status, not commanded conduct, exactly like its affirmative counterpart; negation does not
change which test applies. `C11-101`'s *"No Principal shall have any right of subrogation,
repayment, reimbursement or indemnity whatsoever, unless and until the Obligations are paid or
performed in full"* is the confirming instance; its trailing *"...and all debts owed by the
Franchisee to any Principal are hereby subordinated to the Obligations"* independently
excludes under the existing §3.2.1 hereby-performative class, no extension needed there.
**(4) §3.8 gains a new subsection, §3.8.3**: a "belt-and-suspenders redundant condition
restatement" — the same real-world circumstance stated twice, non-adjacently, sandwiching an
obligation's verb and object — collapses to **one** `conditions` entry, chosen by a **hard
positional tiebreak** (the occurrence structurally closest to the governing modal verb, never
by "completeness" — the applicability gate that admits this section in the first place already
requires every candidate occurrence to be informationally identical, so there is nothing left
to compare on but position), with every non-winning occurrence recorded in `annotator_notes`
rather than dropped. Introduces a new, optional field, `conditions_accept_set` (parallel
list-of-lists indexed to `conditions`), so clause 7 accepts any non-winning occurrence's
verbatim phrasing too — the first accept-set-shaped mechanism `conditions` has ever needed.
Confirming instance: `C06-016`'s *"...shall be required, **if requested by the applicable
counterparty**, to provide adequate assurance of future performance with respect to such Lease
or Contract **if the applicable counterparty so requests**"*. §1's field table is updated to
list the new field. `C06-016` is locked as `C06-01`, batch 3's sixth item. **(5) §2 gains an
observational note, recorded not resolved**: a second batch-3 instance (`C14-139`, after
`C17-077`) of a segment exceeding the 1-3 clause band without being a chained-single-sentence
case — flagged so a third instance is recognized as a pattern rather than rediscovered, not
acted on from two data points. `C14-139` is excluded rather than annotated, mechanically, on
the identical band ground as `C17-077`; its two live judgment calls (§8.8.1 does not extend to
genuine liability-retention/"remain responsible" language, which stays a real `MUST`; and a
"comply with A, and also comply with B" sentence over two independently-breachable requirement
sets splits into two items under §4.3, the `"notify and remedy"` shape not the
`"deliver...and keep current"` one) are preserved as forward guidance in the exclusion's own
log entry rather than cashed in on this segment, since eligibility is decided before content is
adjudicated and the reviewer explicitly declined to let prior analysis on an item bias its own
eligibility call. **(6) §2 gains §2.6**: self-containment is checked at sentence granularity,
not segment granularity — a segment containing an orphan list fragment (`C04-024`/`C22-025`'s
shape) is not disqualified wholesale merely because part of it lacks a subject/modal or depends
on external content; it is annotated where a self-contained sentence is embedded inside the
fragment-heavy enumeration, excluded only where the specific sentence itself fails the test.
Confirming instance: `C13-017`, an orphan `(a)`–`(j)` enumeration wrapping two fully
self-contained sentences inside item (h)'s text. Does not reopen `C04-024`/`C22-025` — a
segment that is *only* orphan fragments is still excluded whole. **(7) §3.8 gains §3.8.4**: a
third condition-counting shape, distinct from both §3.8.2 Rule B (independent conditions) and
§3.8.3 (the identical fact restated as two condition-shaped phrases) — a phrase that passes the
bare removal test in isolation but only restates scope a **non-condition-shaped** anchor
elsewhere in the segment (a heading, a list-item label) already fixes is anaphoric scene-setting,
not an independent gate, and is not entered as a second `conditions` entry. Confirming
instance: `C13-01`'s span, where `"In such a situation"` restates item (h)'s own heading and
`"upon request"` alone is the genuine, unanchored condition — caught on reviewer challenge
after an initial draft entered both as separate conditions. **(8) §2.6 gains §2.6.1**: the
1-3 clause-band over-count question, deferred at two prior instances, is answered with
corpus-wide measurement rather than deferred a third time after `C14-028` became the third
batch-3 instance. A proxy count (modal-bearing sentences per pool segment, the identical
`_MODAL_RE` `enumerate_pool()` already uses) over all 1,547 pool segments finds a **12.6%
corpus-wide baseline**, document-concentrated (0% to 25%+, `C14` at 18.3%/`n=153`, `C04` at
16.0%/`n=181`, both meaningfully above the mean on real sample sizes). Batch 3's standard queue
drew `C14` three times out of twelve candidates (25.0%) — disproportionate to its actual 9.9%
corpus share by segment count (153/1,547 pool segments; 3.6% by document count) — which is
sufficient on its own to explain two of the three over-band exclusions as document
composition, not a segmenter or band defect. **Conclusion, evidence-backed rather than a
guess: the 1-3 band is intentionally conservative and this rate is the accepted, expected cost
of it** — not a case for segmenter tuning (no cutting defect found) or band narrowing (would
trade this failure mode for more truncated segments, not an obvious improvement). `C04`/`C14`
are named as documents expected to run a higher over-band rate than average going forward, so
a future batch hitting the same pattern cites this section rather than re-investigating.
**(9) §3.5 gains §3.5.4**: `obligee` assignment is modality-independent — §3.5's ordinary
positional test governs `obligee` the same way for `MAY`/`SHOULD` as for `MUST`; `ABSENT` is
reserved for a genuine absence of any named counterparty, not applied by default whenever
modality isn't `MUST`. Confirming instance: `C13-041` (`C13-03`), the gold set's first
`MAY`-modality item — *"Either party shall have the right to terminate this Agreement...upon
written notice **to the other party**..."* — where `"the other party"` is named in-span and
annotated as `obligee` on the identical positional ground §3.5.3 already uses to promote an
in-span party for agentless passives. **(10) §3.5 gains a clarifying note (no new numbered
subsection)**: an in-segment anaphoric antecedent from a non-adjacent sentence does **not**
satisfy §3.5's in-span requirement for `obligor`/`obligee`, even where the real-world agent is
contextually unambiguous — tested and held at `C14-044`'s S4 (`C14-05`), where *"such
rescheduling"* unambiguously refers back to `NICE`'s discretion two sentences earlier, and
`obligor` is annotated `ABSENT` rather than `NICE`. Deliberately a narrower boundary than
§2.6/§3.8.4's segment-scoped extensions, since this feeds §5 clause 3's scored predicate
directly; the strong contextual reading is recorded in `annotator_notes`, not acted on. Also
records the first instance of a `MAY` clause's exercise-mechanism sitting in a **non-adjacent**
sentence (`C14-044`'s S1/S4) rather than the same sentence (`C13-041`'s shape) — §3.1's
contiguity rule means the mechanism cannot be folded into the `MAY` clause's own span, so it
stands as its own item (`C14-05`) regardless of the `MAY` clause's own disposition, distinguished
by citation from `C13-041`'s single-item case. *(Note, added at change (12) below: S1 itself was
retracted under §2.5.1 — no monitorable stakes — after being briefly locked as `C14-03`, so this
segment ends up with only the mechanism half, `C14-05`, standing as a locked item. The
non-adjacency/contiguity principle stated here is unaffected by that retraction — it governs
what happens when a `MAY`-plus-mechanism pair is split across sentences at all, independent of
whether the `MAY` half itself clears §2.5.1.)* **(11) §3.8.1's
marker-equivalence note is clarified**: the enumerated marker list is citation convenience for
recognizing branch 3's test quickly, not an exhaustive whitelist requiring its own fresh
reviewer ruling per new preposition — made explicit after `except where` became a **fifth**
confirmed marker at `C02-045` (*"Except where AMAG is required by Applicable Law to account for
any VAT..., Antares shall be solely responsible for..."*) without needing separate
re-litigation; membership is decided by branch 3's own test (does the phrase narrow/remove the
duty under a stated circumstance?), not by matching an entry already on the list. **(12)
`C14-03` RETRACTED at batch verification, and §2.5.1 gains a negative worked example
documenting it.** `C14-044`'s S1 was briefly locked as `C14-03` on the reasoning that its
restricted scope ("already-issued POs only") supplied §2.5.1's required monitorable stakes —
re-checked and found wrong: scope restriction is not monitorable stakes, and *"without any
implication"* is at least as direct a no-stakes signal as `C11-046`'s "sole business judgment."
`C14-03` is excluded under §2.5.1, the identical disposition as `C04-026`/`C11-046`; `C14-04`
and `C14-05` (S3/S4 of the same segment) are confirmed independent of the retraction — neither
item's own field values were ever derived from `C14-03` remaining locked — and the segment's
clause count settles at 2, still comfortably within §2's 1-3 band. Two numeric errors in
change (8)/§2.6.1 above are also corrected here, found during the same verification pass:
`C14`'s corpus share was asserted as "~1.4%" without being checked and is actually **9.9%** by
segment count (153/1,547), and `C14-028` was drawn as the **twelfth** standard-queue candidate,
not the eleventh as originally written — both fixed in place per this document's own
corrections-are-new-text discipline, not silently edited.
**Created:** 2026-08-17
**Status:** **32 items locked** — no item restamped at v0.45 (§5.1 governs annotator comparison only and touches no annotation rule) — batch 1 complete (10), batch 2 at 8 of 10 with two
items still undrawn, **batch 3's draw target is FULLY MET: 10 of 10 segments locked**
(3 hard + 7 standard, per `draw.json`'s own `"count": 10, "hard": 3` — 14 items total, since
`C13-017` is this batch's only two-item segment; `C14-044` originally yielded three drafted
items but now stands at two after `C14-03`'s retraction, change (12) above) — `C04-04`/`C04-05`
(`C04-139`), `C22-02` (`C22-022`), `C10-01`/`C10-02` (`C10-016`), five items from three
hard-stratum segments; plus `C06-01` (`C06-016`), `C05-01` (`C05-027`), `C13-01`/`C13-02`
(`C13-017`), `C13-03` (`C13-041`, the gold set's **first `MAY`-modality item**), `C14-04`/
`C14-05` (`C14-044`, `C14-03` retracted — see change (12)), `C02-04` (`C02-045`), and
`E08-01` (`E08-005`), seven standard-queue segments, nine items. **Batch 3's own annotation
work is complete. §7 HAS NOW RUN, on 2026-08-29, in the amended one-sided form recorded at
§7.1 — the prospective 2-of-10 withhold it originally specified was never performed and is
established as unperformable under this project's reviewer-coupled cadence. Result:
`K = 14/32 = 43.8%` (Wilson₉₅ [28.2%, 60.7%]) against pre-registered bands, landing in
REDESIGN (≥6). Read §7.1 before quoting that number — it is a cold second-annotator check,
not a held-out one, and carries four disclosures.**
*(This line read "§7's held-out blinding/second-annotator process has not yet run" from
v0.41 until 2026-08-29, true when written.)* The
standard queue's first seventeen candidates run
`C11-046`/`C11-101`/`C06-016`/`C17-077`/`E08-046`/`C14-003`/`C17-038`/`C14-139`/`C05-027`/
`C06-022`/`C13-017`/`C14-028`/`C02-062`/`C13-041`/`C14-044`/`C02-045`/`E08-005` — seven
segments locked (`C06-016`→`C06-01`, `C05-027`→`C05-01`, `C13-017`→`C13-01`+`C13-02`,
`C13-041`→`C13-03`, `C14-044`→`C14-04`+`C14-05` (`C14-03` drafted, locked, then retracted —
change (12)), `C02-045`→`C02-04`, `E08-005`→`E08-01`, all genuinely reviewer-approved —
`C05-01` was briefly self-marked `APPROVED` without actual review, caught, reverted, then
properly reviewed and approved before being restored here), the other ten logged as §2
exclusions — see §2.6.1 for why three of those ten (`C17-077`, `C14-139`, `C14-028`) sharing
the 1-3-band exclusion is expected, measured, document-composition-driven, not a segmentation
concern). The consolidation pass (§19.4) is **complete** (§20): all 16 proposals
ruled, every approved rule written into a live rule section, and **all 18 locked items
conformed — every one now stamps `v0.28`**, verified by reading the items themselves.
**As of v0.31 that stamp is no longer current for one item:** §8.3.1's amendment changes
`C14-02`'s span, and it is deliberately **not** conformed. **That is now a settled decision,
not an open question** — §22.1 (v0.32) rejects both proposed fixes and defers the general
problem until a second, independent instance exists. The set is therefore conformed to
`v0.28` and carries **one known, deliberately-retained outstanding conformance**, not zero.

**UPDATED v0.48 — the sentence above is a dated record and this is the live count.** The first
§10.1 freeze-pass batch executed at v0.48 and **restamped five items to `v0.48`**: `C04-04`,
`C04-05` (F3), `C10-01` (F11), `E01-01` (F8) and `C04-02` (F7). Live stamp distribution across the
**32 locked items**: `v0.28` ×16, `v0.38` ×1, `v0.41` ×9, `v0.44` ×1, `v0.48` ×5. The set is
therefore **not** conformed to a single version and `run_scoring.guideline_version_from_items()`
raises by design — which is the pre-existing state, not something v0.48 created: the set has
carried multiple stamps since batch 3 opened at `v0.37`. `C14-02`'s deliberately-retained
non-conformance (§22.1) is **unchanged** and still the only *intended* outstanding conformance.
**Cassette consequence, stated exactly: 6 of 36 gold cassettes are now stale, in 2 of 12
segments** — `C04-117` ×3 and `E01-047` ×3, from F7's and F8's restamps. F3's and F11's items were
never recorded, so they staled nothing (see §10.1's cassette-backed table correction).
*(This line read "No items have been annotated against this document yet" from v0.1 through
v0.25 — false from 2026-08-19 onward, corrected at v0.26; see §19.3. It then read
"consolidation pass … in progress, not complete", "Items stamp guideline versions
v0.12–v0.25" and "the §10 conforming pass has not run" from v0.26 through v0.28 — all three
false once the pass completed, contradicted by v0.28's own changelog entry and by the items'
actual stamps. **This is the FOURTH false header claim this document has carried, and the
first one caught by §10's own close-out consistency check rather than by a later session** —
the check found it on its first application, which is the case for keeping it.)*
**v0.42 change:** **§7 ran for the first time and is AMENDED as a process, not corrected as
a typo — see the new §7.1.** Its prospective 2-of-10 withhold was never performed for any
batch and cannot be performed under this project's cadence: every locked item is
reviewer-signed-off item-by-item as it is drafted, so no unreviewed item exists to withhold,
and §14.4's own rule empties the holdout pool at 100% review coverage. The original §7 text
is **retained unedited** beneath a status banner as a dated record of the superseded design;
§7.1 is operative. What ran instead is **one-sided blinding** — a fresh cold annotator blind
to the drafts, a reviewer blind to nothing — over a **census** of all 32 items / 22 segments,
with bands re-derived for N=32 by preserving §7's evidential strength (PROCEED ≤2 / DIAGNOSE
3–5 / REDESIGN ≥6) and fixed before the comparison. **Result `K = 14/32` → REDESIGN.** Three
findings the K predicate could not see are recorded in §7.1 and in
`apps/brain/evals/goldens/holdout/RESULTS.md`, of which one is structural and outranks
everything else in the response: **`known_gaps` is not among §5's eight clauses, the two
annotators disagree on it for 19.4% of matched items, and that disagreement swings §9's
in-force criterion-2 denominator from 15 scoreable items to 17.** No K is trustworthy until
that is fixed, and whether the fix is a ninth §5 clause or a separately-thresholded agreement
rate is an open decision deliberately left untaken. **No annotation rule changed, no item
restamped, no cassette stale.**
**v0.43 change: item 0 of the REDESIGN response (the `known_gaps` agreement instrument, `G`/
`G_swing`) is IMPLEMENTED** — `evals/harness/gap_agreement.py`, wired into `report.py`'s
criterion-2 render per the mandatory display rule; see
`apps/brain/evals/goldens/holdout/GAP_AGREEMENT_DESIGN.md` for the design and
`tests/evals/test_harness_gap_agreement.py` for the real-data reproduction
(`G=6/31`, `G_swing=2/31` → BANDED, `D=15 [15–17]` → REDESIGN, matching v0.42's own figures
exactly). **Also closes item 4 of the same response — three already-tracked items marked
REINFORCED, not re-litigated** — see the confirming notes added to §3.4 and §22.1 below. **No
annotation rule changed, no item restamped, no cassette stale.**

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
denominators. **v0.14 change:** compound-action rule added (§8.3) — one item on the primary verb,
`known_gap: "compound_action"`, dropped verb recorded.
**v0.15 change:** §8.3 confirmed by the reviewer and given its named rule — shared
indivisible object stays one item, separate objects split. ~~v0.15 is the version batch 1 is
annotated under.~~ **SUPERSEDED v0.26 — false; batch 1 spans six versions. See §19.3.**
**v0.16 change:** mutual-obligation rule added (§8.4) — one item, `known_gap:
"mutual_obligation"`. PII redaction convention recorded (§2.3).
**v0.17 change:** `within_preposition` gap added (§8.6, 7 confirmed bare-numeral instances);
joint-obligor rule added (§3.5.1) as an accept-set, explicitly NOT a gap. ~~v0.17 is the
version batch 1 is annotated under.~~ **SUPERSEDED v0.26 — false, and it contradicted the
identical claim made for v0.15 two entries earlier. See §19.3.**
**v0.18 change:** `corpus_artifact_in_span` gap added (§8.7) — a running page header,
docket stamp or `Source:` footer spliced **mid-sentence**, inside a span §3.1 cannot
truncate around. Measured pool-wide before the rule was written: 76 of 1,547 segments
(4.9%) match, ~60 (3.9%) survive inspection, concentrated in C04 (22) and C06 (15).
Batch 2 is annotated under v0.18 from item `C04-01` onward; items annotated earlier in
the batch stamp their own version, per §10.
**v0.19 change:** §8.4's *"first-named party"* instruction scoped to spans that name the
parties individually, and the **collective-reference** sub-case carved out explicitly
(§8.4.1). Measured before the rule was written: the collective form is **7.4% of pool
segments (132 sentences / 114 segments, 42 hard-stratum)** — more than double the
named-conjunction form §8.4 was written for (3.2%).
**v0.20 change:** §2.4 added — OCR-damaged segments are excluded under §2's born-digital
requirement (reviewer-ruled). Measured: **6 segments, all in C11, zero in the other 27
documents**; batch 1's locked `C11-01` verified clean, so nothing retroactive.
**v0.21 change:** two obligee rules added. §3.5.2 — a **beneficiary-naming** purpose clause
supplies the obligee when no dative already does, with `on behalf of X` carved out as an
**obligor**-side marker. §3.5.3 — agentless passive clauses (reviewer-ruled at `C04-03`),
with the drafter's dissent recorded.
**v0.22 change:** `known_gap` (string | null) becomes **`known_gaps` (list)** — approved
after a dry-run migration over all 13 locked items (13/13 clean, 0 special-cased, 0
round-trip loss, idempotent). §9 gains the non-summable per-tag reporting sentence and
§3.7.1 gains a precedence note. Measured at the honest granularity: same-**sentence** gap
co-occurrence is **0.9% of sentences (38/4,289)**, not the 4.4% of *segments* first
reported — a 1.8× overstatement, corrected here.
**v0.23 change:** §8.3.1 added — the split-span case §8.3 deferred *"for whichever batch
first hits it"* arrived at `C14-076`. **Status: v0.23 default, pending confirmation.**
**v0.24 change:** §8.8 added — `action_not_in_taxonomy`, reviewer-ruled as case-by-case
tagging rather than an `ACTIONS` change. Measured item-level rate: **23% of annotatable
obligation clauses (6/26), 95% Wilson CI [11%, 42%]** — superseding an earlier
token-weighted 44%.
**v0.25 change:** §3.5.1.1 added — **disjunctive** obligors ("X *or* Y"), reviewer-confirmed
at `C02-021`. Accept-set, no gap tag, and non-registry-resolvable alternatives are admitted.
**v0.26 change:** **no annotation rule changed.** Recalibration only — §19 added, recording
the measured cost of batches 1–2 from session transcripts, the measured rule-discovery rate
and its trend test, three false claims in this document corrected (§19.3), and the
criterion-2 denominator problem stated (§9, §19.5). Batch 2 is **paused at 8 of 10** pending
the consolidation pass (§19.4). **The 100-item target is unchanged but is now explicitly a
working figure, not an analytically justified one (§19.5).**
**v0.27 change:** **no annotation rule changed.** Two corrections to v0.26's own §19, both
found while running the consolidation sweep: the conforming-debt count is **154 item × rule
pairs, not 127** (v0.26 counted version *bumps*, but v0.16, v0.17 and v0.21 each introduced
two rules), and the sweep's own result is recorded — **139 of the 154 clear mechanically, 15
need a reviewer look** (§19.7).
**v0.28 change:** ~~**no annotation rule changed.** Consolidation pass in progress; three merges
identified (M1/M2/M3); one probe run, which surfaced one new gap class and five defects in the
proposed amendments; no rule adopted yet. Every proposal is held unadopted in §20 and none has
been written into a rule section.~~ **SUPERSEDED — accurate only while the pass was in progress.**
The consolidation pass then COMPLETED: **all 16 items were ruled and every approved rule written
into its own live rule section** (§3.5.1 the merged party slot, §3.8.1 trailing-qualifier routing,
§8.9 the `RELATIVE_TO_TRIGGER` preposition gap, §4.3.1 restatements, §3.9's restated trigger,
§21's harness requirements, and the rest). Three probe passes were run, not one — `E05-019` twice
and `C06-113` once — producing three new gap classes and a defect rate of 5 → 0 → 0. All 18 locked
items were conformed. *(Struck rather than deleted, and the header corrected in place rather than
marked, per §19.3's own distinction: a changelog is a dated record, but a status line that
knowingly states the wrong status is a defect. This is the THIRD false header claim this document
has carried — see §19.3 for the first two.)* The probe is `apps/brain/evals/probes/E05-019.json`
(status `PROBE`, excluded from the 100 and from every reported number under §2.1).
**v0.29 change:** **no existing annotation rule changed.** §6.1 added: how to report a segment
whose third run is unobtainable because the provider reproducibly refuses the request. Created by
`C17-021` run 3 — three consecutive HTTP 400 `json_validate_failed` responses with an empty
`failed_generation` from `openai/gpt-oss-120b`, against a request byte-identical to runs 1 and 2,
which had both recorded cleanly. The rule forbids obtaining the missing run by changing any request
parameter, on comparability grounds. The stage-4 recording run that found it completed at **35 of 36
cassettes** (12 segments × 3 runs, less `C17-021`/run3), 41 of 80 approved calls.
**§10's close-out consistency check, added at the end of v0.28, fired for the first time and
caught a FOURTH false header claim** — the Status line's "consolidation pass in progress",
"items stamp v0.12–v0.25" and "§10 conforming pass has not run", all three contradicted by
v0.28's own changelog and by the items' actual stamps (all 18 read `v0.28`). Corrected in
place per §19.3; recorded in §19.3 as the fourth instance.
**v0.30 change:** **no existing annotation rule changed.** §6.1's n=2 tie clause reconciled
with `report.py`'s G2 rule: a two-run disagreement resolves to the **worst observed outcome**
and is counted unstable, rather than yielding "no modal outcome". §6.1 as written at v0.29
contradicted a rule already implemented in the reporter — caught while scoping the
scorer-wiring session, before any code depended on either reading. A defined conservative
status keeps the item inside criterion 2's denominator; an undefined one would have been
improvised downstream.
**v0.31 change:** **AN ANNOTATION RULE CHANGED** — the first such change since v0.25. §8.3.1's
v0.23 `DEFAULT, PENDING CONFIRMATION` rule is superseded: it chose the one branch of its own
trilemma that `ground_candidates()` forbids, having mis-classified "obligor outside span_text"
as a methodological cost when it is mechanically enforced as `NESTED_FIELD_NOT_IN_SPAN`. A
fourth option — contiguous from the shared subject through the end of the second verb phrase —
is adopted. Found by the first real scoring run, which put `C14-02` at `MISSED` on all three
runs for a duty the model had in fact extracted correctly. §22 records why the one affected
item is **not** yet conformed.
**v0.32 change:** **no annotation rule changed.** §22.1 added: the conforming blocker is
**decided**, not left open. Neither proposed fix is adopted — `guideline_version` stays a
cassette-staleness dimension and the scorer keeps refusing mixed stamps. `C14-02` remains
`MISSED` under the superseded v0.23 rule as a tracked conforming gap, on the ground that a
known wrong number with an honest label beats a harness in which fixing a broken rule costs
more than leaving it broken. Deferred until a **second, independent** instance exists — a
v0.32-or-later correction that also requires conforming — so the general question is designed
against more than one case rather than fitted to this one.

**v0.33 change:** **NO ANNOTATION RULE CHANGED — no item is restamped and no cassette goes
stale.** Five changes, all either reporting rules, comparison rules, or *forward* authoring
rules that explicitly do not reach locked items. (1) **§9's dual denominator is IN FORCE**,
superseding its v0.26 `RECOMMENDED, NOT YET APPROVED` status: `len(known_gaps) == 0` is now
**criterion 2**, all-items is reported alongside. Approved on **two independent grounds** —
the original *reachability* argument (contingent on the 38.9% gap rate) and a new *validity*
argument that is not: the all-items numerator already counts two knowingly-**incomplete** IRs
(`C03-02`, `C04-02`) and would count a knowingly-**overstated** one (`C14-01`) the moment
clause 5's number rule lands, which is precisely the outcome §8.2 promised would stay
"recoverable from the data rather than baked silently into a score." §9 also now requires
**inline gap disclosure at the numerator** (`report.py` G6). (2) **§5 clause 5 normalizes
grammatical number on both sides** — 7 of 37 aligned comparisons in the first scoring run were
number-only mismatches, and zero of the 18 accept-sets hedged on number, so the field was a
coin flip. Deliberately a narrow normaliser, never a stemmer. (3) **§3.4 gains one bounded,
named exception** permitting accept-set widening during §10's pre-scheduled freeze pass only —
recorded as an **amendment**, explicitly not as a reading of the existing categorical sentence,
so the softening is legible in the diff rather than absorbed into it. (4) **§3.6 and §3.5.1
gain required enumerations** (both nominal anchors; compounds of existing members; the whole
coordinated party phrase), forward from batch 3. (5) **§3.8.2 fixes the two conditions
conventions §3.8 never had** — where a qualifier quote starts, and when adjacent phrases are
separate entries — with `C04-01` recorded as a **symmetric** ambiguity in which gold's choice
was arbitrary rather than correct. `C02-03`, `C11-01` and `C02-01` are queued for the freeze
pass under (3) and **keep scoring as failures until then**.

**v0.34 change:** **NO ANNOTATION RULE CHANGED — no item is restamped and no cassette goes
stale.** Two corrections to *evidence*, both from the compile-stage bottleneck investigation
(CLAUDE.md), and both exposed by real recorded model output rather than by re-reading a pattern.
(1) **§8.9's preposition table has two wrong rows**: `on <trigger>` is recorded at **0 segments**
and measured at **5** — with the shape that actually occurs, `on the <Defined> Date`, at **12
(0.8%)** and invisible to the table's trigger-noun alternation — and `until` is **absent from the
table entirely** though the rule as written covers it, measured at **72 segments (4.7%)**. The
re-measurement is corroborated against the table's own `upon` (90 vs 92) and `after` (29 vs 29)
rows before its divergent ones are trusted. This is the **second** data correction to that one
table, on the identical ground as the first. (2) **§15.3's last paragraph is FALSIFIED** and
struck in place: it files the vague-temporal class on the *silent* side of its own
loud-versus-silent taxonomy, and the class in fact fails **loudly** — `UNMAPPABLE_TEMPORAL`
rejecting the whole candidate, scoring `MISSED` rather than `PARTIAL` — measured 5 times.
**§15.2's rule is unaffected**; only the class placement was wrong, and the new §15.3.1 says so in
terms. §15.4 is deliberately **not** amended: what to do about a headline count that no longer
matches the class's real cost is a decision, not a correction. Neither change touches §5's
predicate, and `run_scoring.guideline_version_from_items()` keeps returning `v0.28`.

**v0.35 change:** **AN ANNOTATION RULE ADDED — forward-only; no locked item restamped, no
cassette stale.** §4.3.2 added: a third obligation-splitting shape, distinct from both existing
§4.3 worked examples (*"provide... and keep current"*, one continuing duty; *"notify and
remedy"*, two acts by the same actor). Batch 3's `C04-139` — *"Bellicum shall use, and will cause
its Subcontractors and Licensees to use, Miltenyi Products in accordance with all Applicable
Laws..."* — coordinates one verb governing the obligor's own conduct with a second governing the
obligor's duty to bind or control a **third party's** conduct. Reviewer-ruled: split into two
items. The test is locus of accountability, not object identity — the two performances do not
share an actor, which is a *stronger* form of independence than §4.3 already requires, not a
weaker one. Flagged as a pattern expected to recur (flow-down compliance clauses — "X shall do Y,
and shall cause its Subcontractors/Affiliates/Licensees to do Y" — are common commercial
drafting), so future instances are decided by citation. No corpus-wide frequency measured.
**Span mechanics for the motivating case are adjudicated separately, per-instance, not settled by
this rule** — see the batch 3 session record for `C04-139`'s own resolution.

**v0.36 change:** **AN ANNOTATION-ADJACENT SCORING RULE ADDED — forward-only; no locked item
restamped, no cassette stale.** §4.2 gains a tie-break for byte-identical gold spans, the
mechanical consequence of §4.3.2's split at `C04-139`: the object clause trails and is shared by
both coordinated verbs, so neither item's minimal contiguous span (§3.1) can be made shorter than
the other's without either breaking contiguity or dropping a field from its own span — unlike
`C14-076`'s shared-subject-split (§8.3.1), whose spans nest rather than collide. Reviewer-ruled:
accept the byte-identical spans rather than narrow either item's object to force non-colliding
ones (narrowing item 1's object to avoid the collision would understate Bellicum's own
compliant-use duty purely to solve a mechanics problem — an incomplete IR is a worse outcome than
a span-alignment complication). Tie-break is by content: match the candidate's `action` against
each tied item's `action_accept_set`, falling through to ascending `item_id` when that is
inconclusive. Scoped strictly to byte-identical spans; does not touch the ordinary
descending-IoU path, including `C14-076`'s nested (non-identical) spans, which already resolve
correctly under it.

**v0.37 change:** **A RECOMMENDATION ADDED, not a binding rule — no locked item restamped, no
cassette stale.** §4.3.2 gains a suggested `object_class` naming convention (`self_` /
`third_party_` prefixes over a shared root), added while drafting `C04-139`'s own pair of items:
the first-drafted labels (`compliant_product_use` / `subcontractor_licensee_compliant_use`)
shared no visible root, which would let a future annotator hitting another flow-down clause drift
toward an unrelated pair of labels each time rather than a recognizable pattern. Recorded now
because `C04-139` is §4.3.2's precedent-setting instance. Not mandatory, since `object_class`
accept-sets are always author-time judgment (§3.6) — a recommendation, not an exact-match rule.

**v0.38 change:** **AN ANNOTATION RULE ADDED — forward-only; no locked item restamped, no
cassette stale.** §3.2.1 added: present-tense self-executing performatives (`hereby grants`,
`hereby assigns`, `hereby appoints`, `hereby releases`, `hereby waives`) are excluded as not
obligation-bearing under IR v1's four modalities. Found at batch 3's `C22-022` — *"the Seller
hereby grants (and will cause each other Seller Party to grant, following each applicable
Closing Date...) a... license..."* — where §3.2's modality table matches none of its rows to
`hereby grants`. **The connecting principle is stated explicitly, not left as an unrelated new
category**: this is the identical non-obligation class §3.2's own "will"-future-fact exclusion
already carves out ("this Agreement will terminate on..."), one tense earlier — a performative
that takes full legal effect at execution has no future state left to monitor, whether the tense
is present or future; only the tense differs, not the reason. Does not exclude a coordinated
clause stating a genuine future undertaking (as in `C22-022` itself, whose "will cause each other
Seller Party to grant..." half is annotated normally). Flagged as expected to recur in
license/IP/assignment/release-heavy segments, parallel to §4.3.2's own "expected to recur" note.

**v0.39 change:** **AN ANNOTATION RULE ADDED (clarifying an existing one, not replacing it) —
forward-only; no locked item restamped, no cassette stale.** §2.5 added: a broad, unrestricted,
no-correlative-party rights-reservation clause (`C04-026` — *"Miltenyi reserves the right...to
manufacture,...sell,...export,...or otherwise commercialize or dispose of Miltenyi Products in
any manner and for any purpose whatsoever"*) is excluded under §2's existing "party's right, no
correlative duty" row — but that row cannot mean "any right is excluded," since `MAY` is one of
IR v1's four modalities and is by definition a right with no correlative duty. **The connecting
principle, stated explicitly rather than left as an unrelated new exclusion**: the real test is
whether the clause has a **future state worth monitoring**, not whether it is grammatically a
right — the identical underlying principle §3.2.1 already applies to present-tense
performatives, reached here from the opposite surface pattern (an ongoing entitlement rather
than a completed act). A `MAY`-shaped clause with monitorable stakes (a correlative party, a
deadline, a gating condition) is still annotated normally; grammar alone (`"reserves the right
to"`) does not decide it. Flagged as expected to recur, the same posture §4.3.2 and §3.2.1 both
took.

**v0.40 change:** **A REVIEWER-RULED CONFIRMATION AND A CITATION LIST ADDED to an existing rule
— forward-only; no locked item restamped, no cassette stale.** §3.8.1's branch 3 gains a
marker-equivalence ruling: branch 3's own test (*"does it state a circumstance that removes or
narrows the duty?"*) was already written marker-agnostic, but until now only `unless` (`C14-01`)
had a reviewer-ruled instance confirming it actually routes there. `C10-016`'s *"except to the
extent the liability arises as a result of the wilful misconduct of the Distributor"* is that
confirmation for a second marker family — the identical shape as `C14-01`, tagged the identical
`exception_unsupported`. A small, non-exhaustive, citable set of equivalent markers is named
(`unless`, `except to the extent`, `save where`, `other than in cases where`) so a future
annotator recognizes the semantic class rather than pattern-matching the literal word "unless."
**Also notes, without silently correcting it:** §8.2's own "Rule" paragraph still names the
pre-rename tag `unless_unsupported`, superseded by the tag rename already approved at the
original consolidation pass (§20.4 decision 5, 2026-08-22) but never updated in §8.2's own
prose — `exception_unsupported` is, and remains, the tag actually in use by both locked items
and by `evals/harness/report.py`'s `GAP_DIRECTION` map.

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

**v0.44 change:** Adds **§3.6.1** — `object_class` must not encode `action`, `obligor` or
`obligee` — and is the **first amendment in this document's history to restamp a locked item**.
Ruled from the §3.6 investigation of REDESIGN scope item 1
(`evals/goldens/holdout/OBJECT_CLASS_INVESTIGATION.md`), which decomposed §7's 7–0
`object_class` specificity signal into four mechanisms and found that only two of the seven
nested pairs — `C10-01`, `C10-02` — are a **defect** rather than a convention gap: their labels
carried material already scored by clause 2 or clause 4, making those clauses co-vary with
clause 5 so a single judgment was scored twice. **Two items restamped v0.40 → v0.44**
(`C10-01` slot `product_liability_indemnification` → `product_liability`; `C10-02` slot
`distributor_insurance_certificate_listing` → `insurance_certificate`), **no accept-set member
removed**, and **no cassette staled** — `C10-016` was never recorded and all 14 batch-3 items
already sit outside `run_scoring`'s single-stamp scoreable set. The rule is deliberately
narrow in three ways, each argued in §3.6.1's own text: the **slot** half is retroactive
because clause 5 never reads gold's slot, so it cannot fit anything to a prediction; the
**set** half is **widening-only**, because retroactive stripping would have flipped `C04-03`'s
`product_delivery` from pass to fail against a prediction `C04-087` run 2 actually emits; and
retroactive widening is confined to items with **no recorded cassette**, everything else
waiting for §10's freeze pass under §3.4's bounded exception. §3.6's forward-only clause gains
a scope note saying it governs its own two enumerations and not §3.6.1. **The §10 re-check is
logged, not asserted** — all 32 items screened, four further candidates adjudicated and all
four cleared — and it carries a Standing Principle 7 note recording that the screener **missed**
`C10-02`'s own `_listing`, because `action` holds `ESTABLISH` while the real verb is *"add"*
(§8.8): the screen is a lower bound, not a census, and is structurally blind to every
`action_not_in_taxonomy` item. **The depth question is explicitly left open** — the corrections
strip only the restating tokens so the still-unruled `product_liability` vs `liability` choice
stays unprejudiced.

**v0.45 change:** Answers **REDESIGN scope item 0's architectural question** — *is §5 one
predicate serving both pipeline scoring and annotator comparison, or two?* — and rules **two**,
in a new **§5.1**. §5 is **unchanged** and remains the pipeline's predicate; the
annotator-comparison predicate is named `A` and differs in three ways, each forced by
measurement: a **slot-only conformance gate** (an out-of-vocabulary value is `NON_CONFORMING`,
never a disagreement), **symmetric mutual-membership** accept-set comparison, and **no registry
branch** for parties. The decisive argument is structural — §5 clause 2's one-sidedness is
coherent against a predictor bound by a closed grammar and incoherent against a peer annotator —
and it is **5 of the 14** disagreements the 2026-08-29 run counted: cold wrote an off-taxonomy
`action` slot on exactly the five items `comparison.json` marks `2_action`, gold carries zero
off-taxonomy values in 32 items, and cold never once used `action_not_in_taxonomy`. **`known_gaps`
is `A`'s ninth clause** — item 0's fix (b) re-derived from clause 2 rather than assumed — and is
still reported as `G`/`G_swing`, never folded into K. **Recomputed: `K = 7/27 = 25.9%` (from
14/32), conformance failures 5/32, `G = 4/26 → DIAGNOSE` (from 6/31 → REDESIGN), `D = 14 [14–15]`
— and the REDESIGN verdict STANDS**, which is what makes the fix safe to adopt: it was ruled on
structural grounds before its effect on the verdict was known. Executable and preserved as
`evals/harness/annotator_agreement.py`, whose tests reproduce the published run **item by item
and clause by clause** in a retained legacy mode — the original comparison's script was never
preserved. **Also lands three consequences of that ruling:** **§3.6 gains an accept-set BREADTH
ruling** (REDESIGN item 1's held half — unblocked, confirmed pipeline-side, anchored on §3.6's
3–6 band and the model's measured depth distribution, with the cold annotator's median explicitly
disqualified as an anchor because cold's `action` breadth **inverts** to 1.93 against gold's 2.12
once restricted to legal verbs); **§3.6 gains a DEPTH scope ruling** (annotator-predicate scope
only, cannot ever constrain criterion 2, comparison-rule shape stays falsified, and **no
convention written** — §9.4's anchor-field precondition is unmet); and **§3.6.1 gains a
correction** — its slot half was summarised as *"free"* when only *free on the pipeline side* was
ever established, since `A` reads the very field it edits (measured: `C10-02`'s clause-5
comparison flipped, `object_class` 6→5 of 23; **K did not move**). **§7's comparison clause is
superseded in part.** **No annotation rule changed, no item restamped, no cassette stale.**
**The close-out re-validation of all 32 items (17 invariants, 544 assertions) surfaced TWO
previously-unrecorded defects, both left UNFIXED as freeze-pass work** — `C10-02`'s `obligor`/
`obligee` are **not verbatim** against their own span (`"the Supplier"`/`"the Distributor"` where
the span reads `"The Supplier"`/`"the distributor"`), which also means `RESULTS.md`'s sensitivity
B attributed that case difference to the wrong annotator; and **§3.6.1 conflicts with §4.3.2's
shared-root naming convention at `C04-04`** (`action = USE` against `object_class =
self_compliant_use`), asymmetrically, on whichever half of a split pair has the root as its own
action verb. Both are recorded in `OBJECT_CLASS_INVESTIGATION.md`'s "Re-verification findings", and
`RESULTS.md` gains a **dated correction** for the sensitivity-B attribution. **§10 gains §10.1,
a single freeze-pass queue (F1–F6)**, because both defects were found by an invariant that had
never been run while the work they belong to was tracked across five different documents — the
new defects enter as **F2** and **F3**, the latter with its own subsection since it needs a
ruling on which rule yields rather than an item fix.

**v0.46 change:** The **§8 tag-vocabulary review** — scoped by `GAP_AGREEMENT_DESIGN.md` §4's
`G = 6/31 → REDESIGN` band, **run at `G = 4/26 → DIAGNOSE`** after §5.1's two-predicate ruling
recomputed it. **No annotation rule changed, no item restamped, no cassette stale.** Three
results. **(1) §8.2's Rule paragraph is CORRECTED IN PLACE** to name `exception_unsupported`,
the tag approved at §20.4 decision 5 on 2026-08-22 and in use by all five carrying items ever
since; §3.8.1 and v0.40 had each *noted* the staleness on the reading that §8.2's text was a
dated record, and it is not — an imperative *"annotate X"* is a live rule statement, which
§10's own process note is exactly the line for. Measured before the fix: both names sat in
`annotator_agreement.py`'s `SECTION_8_TAGS`, so an annotator following §8.2 literally would
clear A1's gate and then fail §5.1 clause 9 on every carve-out item — **`G` 4/26 → 7/26,
`G_disjoint` 0 → 5**. It is the **only** alternative-encoding pair in the vocabulary; every
other pair was checked and is disjoint by construction. **(2) `GAP_AGREEMENT_DESIGN.md` §6's
deferred question — "can §8 tags legitimately co-apply?" — is CLOSED as ANSWERED**, on the
guideline's own three prior rulings (v0.22's list schema, forced by `C14-01`; v0.22 §9's
non-summable per-tag rule; v0.28 §8.3 F2 branch 3's *"Both apply… Settled here rather than left
to be discovered"*), and **its inference is corrected**: co-application makes strict set
equality *more* correct, not less, so `G` keeps strict set equality and the caveat published
with it is withdrawn. **(3) What the review found INSTEAD of an equivalence problem** — two
applicability-criterion disagreements (§8.4.1's trigger, §8.3's branch 2/3 precedence) and a
`kind`-axis question about the vocabulary as a whole — is queued at **§10.1 F7–F9**, with the
`report.py` `GAP_DIRECTION` coverage gap filed separately as **F10** on the reviewer's explicit
direction that a reporting-layer gap must not be folded into a taxonomy review.

**v0.47 change:** **Two reviewer rulings from the §8 tag-vocabulary review (§10.1 F7, F8), each
with a §10 re-check logged across all 32 locked items. Two items are ruled to change and
NEITHER IS RESTAMPED HERE** — both are cassette-backed, so both are conforming events with §22's
blocker attached and both are batched into the freeze pass alongside F2/F3, on the reviewer's
explicit direction. **(1) §8.4.2 closes §8.4.1's OPEN SUB-QUESTION**, open since v0.19 and queued
nowhere until F7, with the first of the two answers that section permitted — a decision procedure.
`mutual_obligation`'s trigger is now §3.5.1's *"is the co-obligor also the obligee?"* test, gated
on a duty-bearing modality, replacing the party-slot **form** that had been triggering it in
practice. Re-check: **exactly one item changes** — `C04-02` loses the tag. Two findings came out
of the re-check rather than the ruling: clause (a), the modality gate, exists **only** because
`C13-03` is slot-identical to `C14-01` and would otherwise have been silently pulled in against
its own locked reasoning; and a **marker regex is explicitly not the test**, since it fires on
`C04-02`'s trigger-clause *"mutually"* and misses `C17-01`'s marker-free named conjunction —
Standing Principle 7 in both directions. **(2) §8.3.2 rules `E01-01` under §8.3 branch 3's
letter** — three tags — refusing a branch-2 exemption unsupported by any defensible mapping,
because branch 2 states a mechanical test and widening it to a "feels like a legal doublet"
judgment would trade a checkable boundary for an unfalsifiable one. That ruling forced a
**correction to how §8.3's three branches read together**: branch 3's determinant is
non-membership **plus** non-mappability, since bare non-membership would fire on branch 2's own
worked example (`hold harmless`). The re-check leaves `C03-02` unchanged and opens **F11** —
whether `defend` is defensibly `INDEMNIFY`, which decides `C10-01` and was not in front of the
reviewer.

**v0.48 change:** **The first §10.1 freeze-pass batch is EXECUTED — four entries ruled, five items
restamped, and this is the first version since the batch-1 conforming pass to change locked
items.** **(1) §4.3.2 gains a ROOT CONSTRAINT (F3)**: §3.6.1 does not yield, §4.3.2's root choice
does, and a shared root may no longer restate either half's own `action`. `C04-04` and `C04-05`
move to `self_`/`third_party_regulatory_compliance` on a root that was **already an accept-set
member of both**, so §3.4's justification test is met by construction; both sets widened
monotonically, no member removed. Two documents had misstated §4.3.2 as *requiring* its
convention — it recommends it, which is why the conflict resolved as cleanly as it did.
**(2) §8.8.2 rules `defend` a GENUINE GAP (F11)**, on evidence measured across the whole
28-document corpus rather than asserted: 33 sentences use it with no `indemnify`, `C03` disjoins
*"failed to defend or indemnify"*, `C03` §(c) owes the defence *"whether or not … the allegations
are meritorious"*, and `C11` converts a failed defence duty into a payment duty. `hold
harmless`→`INDEMNIFY` is untouched, so **the two non-member verbs of one triplet land on opposite
sides of §8.3's non-mappability limb** — its first real exercise against a verb §8.8 had not
ruled on. `C10-01` gains `action_not_in_taxonomy`. **(3) F8 and F7's v0.47 rulings are applied**:
`E01-01` gains **two** tags, not the one its queue row named (`compound_action` had never been
applied to it either), and `C04-02` loses `mutual_obligation`. **(4) THE ONE PUBLISHED NUMBER THAT
MOVES: §9.2 — `C04-02`'s empty `known_gaps` puts it into §9.1's in-force criterion-2 denominator,
8 → 9.** In-force criterion 2 is now `3/9 = 33.3%` or `4/9 = 44.4%` depending on how `C04-02`
itself scores; `3/8 = 37.5%` is superseded and must not be quoted. The denominator is asserted,
the numerator is not — it is a scorer output and no run exists against the restamped items.
**(5) F10 is partially executed, scoped**: `action_not_in_taxonomy` is classified
`INCOMPLETENESS`, because F8 and F11 apply that tag and shipping them alone would have widened a
reporting gap while claiming to close a taxonomy one; the other five live tags stay
`UNCLASSIFIED`, are now named in `report.py` with reasons, and wait on **F9**. **(6) F12 is filed,
not decided** — §3.6.1 tests the `action` slot only and not `action_accept_set`; zero exposure
today, and F3's own root creates the first instance. **(7) §10.1's cassette-backed column is
CORRECTED against the directory**: `C04-139` and `C10-016` were **never recorded**, so F3 and F11
were free and were executed first; **§22's blocker attached to F7 and F8 only**, and the three
`C04-117` and three `E01-047` cassettes are now stale by design. **Cassettes stale: 6 of 36, in 2
of 12 segments. Items restamped: 5 of 32.**

**v0.49 change: §9.2's `? / 9` RESOLVES to `3/9 = 33.3%` — a MEASUREMENT entry, no rule
changed, no item restamped (`C04-02` keeps the `v0.48` stamp F7 already gave it).** The narrow
path was taken deliberately, not the full §10 conform: `C04-117` alone was re-recorded live
(3 runs, 4 model calls, `openai/gpt-oss-120b`, prompt `v3`, guideline `v0.48`) — the one
cassette F7's restamp required, and mandatory regardless of path since it carries `C04-02`
itself. Scored by pure replay against the fresh recordings: `C04-02`'s three runs are
`PARTIAL`, `MISSED`, `MISSED` — three genuinely different failures (run 1 fails the `obligee`
clause; run 2 extracts nothing at this segment; run 3's best candidate is IoU 0.25, below the
0.5 alignment threshold) — so the modal outcome is `MISSED` and no run reaches `FULLY_CORRECT`.
**The numerator holds at 3. In-force criterion 2 is `3/9 = 33.3%`. Do not quote `4/9 = 44.4%`
— that branch is now closed, not merely undecided.**

**CAVEAT, stated inline rather than left implicit — same footing as `C14-02`'s §22.1
non-conformance.** This figure is measured over a population that is still guideline-mixed:
the 18-item cassette-covered set carries `v0.28×16` / `v0.48×2` (`C04-02`, `E01-01`). The full
§10 conforming pass — restamping the remaining 16 items and re-recording all 12 segments,
~35 cassettes — was deliberately **not** run; it was weighed against the narrow path and
rejected for this session on the ground that F5/F6/F9/F12 (§10.1) are real open design
questions a recording session should not rush to close just to earn a single-stamp
denominator, and F6 is structurally blocked regardless (§9.4's missing anchor field). `3/9` is
therefore an in-force figure computed over a genuinely mixed-stamp scoreable set, not the
uncaveated single-stamp number full conforming would produce — recorded here so it is never
read as the latter.

**A structural side effect of this same re-recording, disclosed on its own footing rather than
folded into the caveat above — see §22.3.** Restamping `C04-117`'s cassette to serve `C04-02`
(`v0.48`) made it newly stale against its own sibling `C04-01` (`v0.28`, same segment,
unrestamped) — cassette staleness did not disappear, it moved from one item sharing the
segment to the other. Costless to criterion 2 today (`C04-01` was never in its denominator),
but a real, general property of a single-`guideline_version`-per-cassette scheme worth its own
citable record.

**v0.50 change: §2.7 is ADDED — REDESIGN scope item 4, decision 1, RULED (adopt; forward AND
retrofit; reconciliation is a hard review failure).** A kept segment now requires a disposition
for **every sentence in it**, not only the sentences that become items. **No existing rule is
changed, no item is restamped, and no cassette is staled** — the data lives in
`goldens/batchNN/segments/<segment_id>.json`, the shape §21 R6 already decided and
`run_scoring.load_not_annotatable()` already reads, and `Cassette.verify()` compares the
*items'* stamp, which this file does not carry. **§2.7 therefore does not engage §22's
conforming blocker**, which distinguishes it from decisions 2 and 3 of the same investigation,
both still open.

**Ruled on measurement, not on principle, and two of the measurements moved the trade.**
**(1)** The forward cost is **0.37–0.67 dispositions per segment**, not the "materially more
work per segment" the investigation's §8 estimated: conditioning on density gives **0.00**
undisposed sentences for a single-modal-sentence segment (n=9, all nine), and §2.6.1's measured
pool is **57.8%** such segments. The §8 estimate priced batch01's 3.12 mean density, which §5 of
that same note flags as an unrepresentative draw; the observed series is 1.88 → 1.00 → **0.20**
across batches 1–3. **(2)** The benefit is **19 of 24 currently-`UNEXPECTED` candidates retired
(79%)**, measured across all 35 gold cassettes with the harness's own IoU rule — §21 R6's
caveat is narrowed for the first time since it was written, though **not retired**: the residual
5 are sub-sentence spans inside already-covered sentences, which §2.7 does not reach and says so.

**Two premises corrected in the course of ruling, both recorded rather than quietly fixed.**
**(a) `C11-094` and `C17-021` are NOT §2 band violations** — both sit exactly at the 1-3 band's
ceiling at 3 obligation-bearing clauses and were correctly eligible. What a required clause count
catches on them is the **3-versus-1 arithmetic**, not an eligibility failure; the investigation's
§8 said "would have caught", never "breached", and neither may be cited as a band violation.
**(b) §6.3's ~89%-fresh figure does not transfer**, because it was measured over the 9 surplus
clauses — selected *for disagreement*, which correlates with absence of record — while §2.7
reaches 21 sentences, of which **10 already carry a genuine disposition**. §6.3 stands for what
it measured; it is the wrong denominator for this decision.

**One design fault found by the measurement and fixed in the rule text before adoption:** the
trigger **cannot** be modal-keyed. `C04-117`'s *"reserves the right to defer"* — surplus clause
#1 and the §2.5 case — carries no modal verb, so a rule scoped to modal-bearing sentences would
silently drop exactly the class §2.5 exists for. Standing Principle 7's shape, caught inside a
proposed rule rather than inside a script.

**Decisions 2, 3 and 4 of the same investigation are UNCHANGED and remain open.** §2.7 rules
only decision 1, and deliberately does not dispose of `E03-005#discuss`, the two v0.28-era `MAY`
clauses, or `C17-066` sentence 2 — each carries its own precedent weight and none is a
prerequisite for another (investigation §9).

**v0.51 change: NO RULE CHANGES. §5's `ABSENT matches ABSENT` is CONFIRMED AS FINAL against a
concern that ran backwards on measurement, and two genuine defects it surfaced are filed as
§10.1 F14 and F15.** `CLAUDE.md` scoped a session on the question *"does §5/§5.1 handle a
both-`ABSENT` (obligor + obligee) item, given `ABSENT` matches `ABSENT` would make it the first
item where 2 of 8 scored clauses pass vacuously?"* — reaching the 62 partyless agentless
passives measured pool-wide, not only `C14-076`. **It does handle it, and the premise behind the
question is falsified three ways.** Full record and scripts:
`goldens/holdout/C14_076_INVESTIGATION.md` §8 and `goldens/holdout/band_risk/`.

**(1) `ABSENT` is measured as a HARDER target than a named party, not a free pass.** Over the 35
gold cassettes, aligned with the harness's own `align()`/`iou()`: clause 3 passes **0/3** where
gold says `ABSENT` against **32/41 (78.0%)** where gold names a party; clause 4 passes **13/17
(76.5%)** against **24/27 (88.9%)**. The direction is the whole point — a vacuous clause would
score *above* the named-party rate, and neither does. The mechanism is that §5 can express
"absent" only as an empty alias, and the model supplies a hallucinated party instead:
`C04-03` emits `"Miltenyi"` on all three runs, which is precisely the possessive-on-a-**location**
inference §3.5.3's reviewer ruling forbids in terms.

**(2) The vacuous clause is 8, not 3 and 4 — and it is a proof, not a rate.** On a span naming no
registered party, grounding requires each alias to be a substring of the span, no substring can
resolve, so `_resolve_party()` appends both roles to `missing_fields` and `underspecified` is
`True` unconditionally. Gold says `True`. **Clause 8 passes for any prediction whatsoever,
including a wholly wrong one.** Measured further: across the 24 locked items whose documents
carry a committed registry, `underspecified` is predicted with **zero** mismatches by
*NOT(obligor resolves AND obligee resolves AND temporal is null)* — clause 8 is a **function of
clauses 3/4/6's inputs**, not an independent eighth check. This is F15.

**(3) The "first item where 2 of 8 pass vacuously" count is wrong as stated.** **10 of 32** locked
items already carry two absence-matched scored slots (obligee `ABSENT` + `temporal: null`), 30 of
32 carry at least one, and gold `temporal` is null on **27/32 (84.4%)**. A both-`ABSENT` item
would be the first with two *party* clauses absent — a smaller and different claim than the one
recorded.

**Why no amendment.** §5's `ABSENT` branch is the strictest cell in the party clauses on this
evidence; amending it would be fitting the predicate to a sample of one, which is what §22.1
exists to prevent. The real defect is upstream in the prompt (F14) and sideways in clause 8's
dependence (F15). **This investigation is NOT a prerequisite for `C14-076`'s band-eligibility
ruling** — see §10.1 F14/F15's own scope lines and `C14_076_INVESTIGATION.md` §8.6.

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
| `conditions_accept_set` | annotated | **optional**, parallel list-of-lists indexed to `conditions`; equivalent verbatim phrasings for a belt-and-suspenders redundant restatement (§3.8.3). Empty/absent for almost every item |
| `underspecified` | annotated | bool (§3.9) |
| `missing_fields` | annotated | reported, **excluded from the scoring predicate** |
| `vague_temporal_phrase` | annotated | literal phrase or `null`; **not scored** (§15) |
| `obligor_accept_set` | annotated | co-obligors for a joint duty (§3.5.1) |
| `redacted_phrase` | annotated | literal redacted phrase or `null`; **not scored** (§8.1) |
| `known_gaps` | annotated | **list** of the named gaps this item exercises; `[]` when none (§8, §11). Was a single string through v0.21 — see the v0.22 note |
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

### 2.6 Self-containment is checked at sentence granularity, not segment granularity (v0.41 — REVIEWER-RULED)

**An orphan list fragment with no self-sufficient content of its own is excluded** — that
precedent (`C04-024`, `C22-025`: a list item opening mid-enumeration, e.g. *"(2) Reverse
engineer..."*, with no subject or modal of its own and a governing stem outside the segment)
was never written into this document as a rule, only established by exclusion-log citation,
and stays exactly that narrow.

**Confirming case, and the boundary this section actually draws** — `C13-017`: an
orphan enumeration `(a)`–`(j)` (bare noun phrases — *"manufacturing, storage, and distribution
of MOXATAG..."* — with no subject/modal of their own, the identical shape as `C04-024`) that
nonetheless **wraps two fully self-contained sentences** embedded inside item (h)'s text
(*"In such a situation, DD will make available to MBRK, upon request, all of DD's pertinent
records on MOXATAG."*; *"Any and all reasonable and documented costs...shall be reimbursed by
MBRK, except to the extent..."*). Neither embedded sentence needs anything from `(a)`–`(g)` or
`(i)`/`(j)` to be understood — *"such a situation"* resolves entirely from item (h)'s own label
and the second sentence's self-referential *"such recall or market withdrawal"*, both present
in the same segment.

**Rule.** §2's *"is self-contained"* eligibility test (and, by the same logic, whether a clause
is obligation-bearing at all) is checked **per sentence, not per segment**. A segment
containing an orphan list fragment is not disqualified wholesale merely because *some* of its
content has no subject/modal of its own or depends on something outside itself — it is
disqualified (whole, or in part) only where the **specific sentence being evaluated** fails the
test. Where a segment contains both orphan fragments and self-contained sentences, annotate the
self-contained ones normally and treat the orphan fragments as non-obligation content within an
otherwise-good segment — do not exclude the whole segment, and do not force the orphan
fragments into items they cannot support. This is the identical principle `C06-016`'s own
eligibility check already applied (a segment is not disqualified by an incidental list marker
that carries its own subject and modal) — reached here from the opposite direction: instead of
one self-contained sentence happening to carry a marker, several non-self-contained fragments
happen to surround self-contained sentences.

**Distinguish from `C04-024`/`C22-025` precisely.** Those exclusions hold because the *entire*
segment was one dependent fragment with nothing self-sufficient anywhere in it. This section
does not reopen or soften that precedent — a segment that is *only* orphan fragments is still
excluded whole, exactly as before. What changes is that "the segment contains an orphan
fragment" is no longer read as sufficient by itself to exclude the whole segment when
self-contained content also exists alongside it.

**Expected to recur.** Enumerated lists wrapping a genuine sentence mid-item (typically to
carve out an exception, a notice mechanism, or a payment term specific to that one list entry)
are common commercial drafting, the same "expected to recur, decided by citation" posture
`§2.5`, `§3.2.1`, `§4.3.2`, and `§3.8.1`'s marker-equivalence note all took at their own
precedent-setting instances. No corpus-wide frequency has been measured.

**A segment is excluded if any of the following hold:**

| Exclusion | Reason |
| :--- | :--- |
| Definitions, recitals, signature blocks, pure tables | No obligation-bearing sentences |
| 4+ chained obligations in one sentence | IoU alignment degrades; one failure contaminates the segment |
| Cross-reference-dependent — **the test is scored-field dependence, not presence (v0.28)** | Excluded when **a scored field's value (§5's eight clauses) cannot be determined without resolving the reference** — *"shall be given in writing in the manner set forth in Section 12.3"* leaves the action's manner unknowable. **Mere presence does not exclude**: a cross-reference inside text quoted *verbatim* — in `span_text`, in a `conditions` entry, or in a carve-out dropped under §3.8.1 branch 3 — requires no resolution and is annotatable. *Checked against all six existing cross-reference exclusions (`C04-018`, `C04-118`, `E03-005`, `C05-043`, `C11-079`, `C15-046`): every one is a genuine dependence case and survives this test unchanged, so this writes down existing practice rather than altering it.* |
| Contains only a party's *right* with no correlative duty | Not an obligation under IR v1's four modalities |

Excluded segments are recorded with their exclusion reason. They are **not** silently
skipped — the exclusion log is part of the deliverable.

### 2.6.1 The 1-3 band's over-count rate — MEASURED (v0.41), a third instance answered with corpus-wide evidence rather than deferred again

**A second failure mode for the 1-3 band, distinct from the "4+ chained obligations in one
sentence" row above.** Three batch 3 standard-queue segments have now exceeded the band
without being chained-in-one-sentence at all: `C17-077` (a services-schedule table flattened
into prose, 7+ clauses across separate bullets), `C14-139` (one coherent, well-formed
multi-sentence subcontracting provision resolving to 6 clauses), and `C14-028` (a components-
supply provision resolving to 5-7 clauses). `enumerate_pool()` only filters on length and modal
presence (§2.1), so nothing upstream catches this; all three were caught at the annotation
stage, mechanically. The first two instances were deliberately left unresolved, on the ground
that two data points don't justify a design decision. **A third instance arrived, and this
time the right response is to measure rather than defer a third time.**

**Measured, not guessed: how common is this across the whole pool, and is it document-
concentrated?** A proxy count — sentences per pool segment matching `_MODAL_RE` (the identical
regex `enumerate_pool()` already uses to decide modal presence), computed via
`corpus.split_sentences()` + `corpus.build_pool()` directly, no reimplementation — run
against all 1,547 pool segments:

| modal-bearing sentences per segment | count | % of pool |
| --: | --: | --: |
| 1 | 782 | 50.5% |
| 2 | 376 | 24.3% |
| 3 | 194 | 12.5% |
| **4+** | **195** | **12.6%** |

**The corpus-wide baseline is 12.6%, not a rare edge case** — roughly one pool segment in eight
carries this shape, hard and standard strata alike (hard 51/408 = 12.5%, standard 144/1139 =
12.6% — stratum is not a driver). This is a **proxy**, not an exact clause count: a
modal-bearing sentence can still fail to be a genuine obligation-bearing clause (a copular
`"shall be deemed"` sentence carries a modal but isn't obligation-bearing, e.g. `E08-046`
today), so the true over-band rate by §2's own clause definition is not identical to 12.6% —
but the proxy is applied identically pool-wide, so its *relative* signal (which documents run
hot) is trustworthy even where its *absolute* number is approximate.

**It is real, and it is document-concentrated, which is the more load-bearing finding.**
Per-document rate ranges from 0% (`C07`, `C10`, `C18`, `C21`) to 25%+ on small-`n` documents,
with `C14` — the document behind two of this batch's three real instances — at **28/153 =
18.3%**, meaningfully above the corpus mean on a substantial sample, not a small-`n` fluke.
`C04` (16.0%, `n=181`) is the other clearly-elevated large document. Batch 3's standard queue
drew `C14` **three times** (`C14-003`, `C14-139`, `C14-028`) out of **twelve** candidates so
far (25.0%) — disproportionate to `C14`'s **actual 9.9%** share of the pool by segment count
(153/1,547; corrected here — an earlier draft of this section asserted "~1.4%" without
verifying it, itself a small instance of the exact failure mode Standing Principle 7 exists to
catch), and two of those three draws are exactly the two `C14` over-band exclusions. **This is sufficient
to explain the batch's elevated exclusion run as sampling from a genuinely denser-than-average
document, not as a segmentation defect or a mis-set band**: `corpus.split_sentences()` and
`reconstruct_paragraphs()` are cutting real sentence boundaries correctly here (`C14-139` and
`C14-028` are both coherent, well-formed prose, not fragments), so there is no evidence the
segmenter itself is doing anything wrong.

**Answering the three options §19.5-style, with the evidence rather than by default:**

1. **Segmenter tuning** — not supported. Nothing in `C14-139`/`C14-028` shows a cutting defect;
   both are single, well-formed provisions that are simply dense on their own terms.
2. **Narrowing the 200-2,000 char band** — not supported by this evidence either, and would
   cut against §2's own char-band rationale (`MAX_SEGMENT_CHARS` is 20,000; 200-2,000 is
   already "far tighter on purpose"). A narrower band trades this failure mode for more
   truncated/non-self-contained segments, not obviously a better trade.
3. **The 1-3 band is intentionally conservative and a ~12-18% mechanical exclusion rate on
   this specific failure mode is the expected, accepted cost of it** — **supported by this
   measurement** and the one this document adopts. §2's own stated reason for the 1-3 band —
   "IoU alignment degrades; one failure contaminates the segment" — is a real scoring-mechanism
   concern, not an arbitrary number, and 12.6% pool-wide (higher in `C04`/`C14` specifically) is
   the band correctly doing its job on real, measured density variation across the corpus, not
   a defect to fix.

**Consequence for future batches, stated so it doesn't need re-deriving:** documents `C04` and
`C14` should be expected to produce a meaningfully higher over-band exclusion rate than the
corpus average when drawn into a batch — this is a property of those documents' drafting
density, confirmed by measurement, not noise. A batch drawing heavily from either should not
trigger a fresh investigation into segmentation on that basis alone; this section is the
citation. **Not resolved here: whether the exclusion log's high rate for *this specific batch*
should itself be reported as a caveat on batch 3's own representativeness** — that is a
reporting-layer question (§9/§19-shaped), not a segmentation or band question, and is left for
whoever writes the harness's summary report.

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

### 2.7 Complete segment disposition (v0.50 — REVIEWER-RULED)

**§2.1 step 4's bias safeguard is segment-level and has never reached inside a kept
segment.** §2.6 moved the self-containment test to sentence granularity at v0.41 and did not
move the logging requirement with it; §4.4 defines the `NOT_ANNOTATABLE` label and §21 R6
defines its file format, but nothing obliged an annotator to record a sentence-level
non-annotation inside a segment that was kept. The consequence is structural, not incidental:
**the reviewer's rejection sample can only sample logged rejections**, so seven un-recorded
omissions across six segments were never eligible to be reviewed, while every gold item on
those same six segments is `APPROVED` or `RULED_BY_REVIEWER`. Approval of an item is not
approval of a non-item. Measured in
`evals/goldens/holdout/SPLITTING_EXCLUSION_INVESTIGATION.md` §3.

**Rule.** For every segment admitted to the gold set, the drafter records a disposition for
**every sentence in the segment**, not only those that become items. A segment's annotation is
**incomplete** — returned in review on the same standing as a missing field (§14.5) — until its
dispositions account for all of its sentences.

**The unit is the sentence, not the modal-bearing sentence, and this is load-bearing rather
than pedantic.** A rights-reservation, a copular status clause and an acknowledgment carry no
modal verb at all. `C04-117`'s *"Miltenyi, acting reasonably, **reserves the right to defer**
the inclusion of additional Miltenyi Products in Exhibit B hereto until the Parties have
reached agreement on this matter"* — the §2.5 case, and one of the nine clauses that motivated
this section — matches none of `shall|must|will|may|should`. **Any modal-keyed trigger silently
drops exactly the class §2.5 exists for**, which is Standing Principle 7's shape reached inside
a rule rather than inside a script.

**A disposition minimally contains, and deliberately nothing more:**

1. `span_char_start` / `span_char_end` / `span_text` — verbatim, per §2.1 step 4's own
   "with its verbatim text" requirement and because the harness needs offsets;
2. `disposition` — one of `ANNOTATED` (carrying `item_id`), `NOT_OBLIGATION_BEARING`,
   `NOT_ANNOTATABLE` (§4.4), `EXCLUDED` (carrying `exclusion_log_id`);
3. `rule` — the § actually invoked (§14.5);
4. one sentence of reason.

**A disposition is explicitly NOT a shadow gold item.** No `action`, no `object_class`, no
accept-set, no `temporal`, no `underspecified`, no field-level adjudication. It answers *"why
is this not an item, and under which rule"* — never *"what would it be if it were."* **This is
the whole of the cost control**, and it is the specific point on which this section departs
from the cost the investigation's §8 estimated: that estimate assumed a disposition would need
*"the same per-item adjudication a gold item gets,"* and it does not.

**Bulk disposition is permitted for a named class.** Section headings, orphan list fragments
(§2.6), and corpus artifacts (§8.7) may be disposed as a single entry citing one rule and
enumerating the spans it covers. Measured over the 22 drawn segments: 13 of the 18 non-modal
sentences fall into exactly such classes.

**Segment-level reconciliation — REVIEWER-RULED as a HARD REVIEW FAILURE.** Each segment file
states `sentences_total`, `obligation_bearing_clauses`, and `items_annotated`, and asserts they
reconcile. A segment whose obligation-bearing clause count exceeds its item count by more than
its dispositions explain is **returned in review**, not merely noted. This is the mechanical
half of the section and the reason it was ruled the load-bearing one: it would have surfaced
`C11-094` (3 obligation-bearing clauses, 1 annotated) and `C17-021` (3, 1) **at annotation
time, with no judgment involved**.

**Note precisely what the two named segments are and are not.** *Neither breaches §2's 1-3
band* — both sit exactly at its ceiling at 3 clauses and were correctly eligible. What was lost
is not an eligibility decision but its arithmetic: the clause count is already performed
implicitly on every segment in order to admit it, and was then discarded. Do not cite either as
a band violation.

**A classification is not a disposition.** `C17-02`'s `annotator_notes` name that segment's
third sentence as *"a section 8.4 mutual case"* and stop. Under this section that entry is
incomplete: it states what the clause **is** and never states that it was not annotated, or
under which rule.

**Genuinely two-way dispositions are flagged `AMBIGUOUS` and escalated (§14.3/§14.4), never
disposed silently.** Three of the nine clauses that motivated this section were marked exactly
that way by the second annotator with both readings written out. The safeguard is worth nothing
if a hard call can be closed with a one-line dismissal.

**Reviewer sample.** §2.1 step 4's random rejection sample **extends to sentence-level
dispositions**. This is the entire purpose of the section, and without it the rest is
bookkeeping.

**Data location — additive to an already-decided shape, with no code change.**
`goldens/batchNN/segments/<segment_id>.json`, the file §21 R6 already specified and
`run_scoring.load_not_annotatable()` already reads (`align.py` consumes it and defaults to
empty). **No item is restamped and no cassette is staled**: `Cassette.verify()` compares the
*items'* `guideline_version` stamp, and this file carries none. Unlike the other open decisions
in the same investigation, §2.7 does **not** engage §22's conforming blocker.

**Measured cost, so this is adopted on evidence rather than on principle.** Across the 22 drawn
segments, undisposed sentences per segment distribute
`[0×11, 1×5, 2×4, 4×2]` — **zero extra work on half of them**. Conditioned on density: 1
modal-bearing sentence → **0.00** undisposed (n=9), 2 → 0.50 (n=4), 3 → 1.60 (n=5), 4+ → 2.75
(n=4). Weighting by §2.6.1's measured pool density, in which **57.8% of band-eligible segments
carry a single modal-bearing sentence**, the forward cost is **0.37–0.67 dispositions per
segment** — roughly **17–31 across the ~47 further segments** the 100-item working figure
(§19.5) implies, against 68 further full gold items, a 0.25×–0.46× surcharge. The
batch01→batch02→batch03 observed series is 1.88 → 1.00 → **0.20**; the investigation's §8 cost
sentence priced this against batch01's 3.12 mean density, which §5 of that same note flags as
an unrepresentative draw.

**Measured benefit.** Classifying all 35 gold cassettes' candidates with the harness's own
IoU rule: of the **24** grounded candidates that score `UNEXPECTED` today, **19 (79%) are
retired** by populating §4.4 from these dispositions (`COLD_ONLY` 12/13, `NEITHER` 7/11). §21
R6's caveat currently travels with every published `UNEXPECTED` figure and blocks any precision
claim from gold-set scoring.

**Known limit, stated here rather than discovered later.** This reaches **sentence** granularity
only. The residual 5 of those 24 are sub-sentence spans falling *inside* sentences that already
carry a gold item, where the model split differently within covered text. R6's caveat is
therefore **narrowed, not retired**, and must continue to travel with published figures until
those are addressed separately.

**§6.3's ~89%-fresh cost figure does not transfer to this section, and the difference is a
denominator not a contradiction.** That figure was measured over the **9 surplus clauses** — a
subsample selected *for annotator disagreement*, which correlates with absence of record. Over
the **21 sentences this section actually reaches**, 10 already carry a genuine disposition (4 in
`exclusions.json`, 6 in `annotator_notes` prose) and 1 more carries a classification without
one. Roughly half, not ~11%. §6.3 stands for what it measured.

**The practice already exists informally, and its correlation with completeness is the
strongest single argument for making it mandatory.** 9 of 32 locked items across **8 of 22
segments** already state an explicit clause count unprompted — `C14-04`: *"Segment clause count
after retraction: 2, comfortably within section 2's 1-3 band"*; `C03-02`: *"Under the rejected
two-item option this segment would hold FOUR duties and fail section 2's 1-3 band."* Of the six
segments carrying surplus clauses, **the only two that recorded a clause count (`E03-005`,
`E08-005`) are exactly the two whose surplus clauses have any recorded disposition at all.**
n=6, so this is a measured alignment and not a proven mechanism — but it is this section's own
mechanism, already observed working where it was applied voluntarily.

**Scope of adoption (v0.50).** Binding on batch 4 onward, **and** retrofitted to the 22
already-drawn segments: 39 spans (21 modal-bearing, 18 non-modal), of which ~half already have
prose to transcribe and 13 are one-line class entries. The retrofit is what retires the 79%
above on the 12 cassette-covered segments, and it is cassette-neutral. It is scheduled work with
a measured size, not a background intention.

### 3.5.2 Beneficiary-naming purpose clauses (v0.21 — REVIEWER-APPROVED)

**The rule is narrow on purpose, and the narrowing is the substance of it.** A purpose or
benefit clause supplies the `obligee` **only** when both hold:

1. No dative / indirect object already names the party owed (*"Antares shall provide
   **AMAG** with all information…"* already has its obligee; the trailing *"to enable AMAG
   to respond"* adds nothing and is not the basis).
2. The clause **names a party as the beneficiary of the duty** — `for the benefit of X`,
   `for X's account` — rather than explaining motivation or outcome.

**`on behalf of X` is explicitly NOT a beneficiary marker and does not supply an obligee.**
It routinely identifies whose *agent* is performing, i.e. it modifies the **obligor** side:
*"a Third Person manufacturing Drug and Pre-Filled Syringes **on behalf of AMAG**, shall
manufacture…"* (`C02-063`). Reading it as an obligee inverts the relationship. This carve-out
matters because `on behalf of` is the **most common** of the four constructions.

**Measured before the rule was written** (§8.6's discipline):

| Construction | segments | % of pool | Obligee-supplying? |
| :--- | --: | --: | :--- |
| `on behalf of X` | 36 | 2.3% | **No** — obligor-side marker |
| `for the benefit of X` | 9 | 0.6% | Yes |
| `to enable X to` | 6 | 0.4% | Only if condition 1 holds; usually redundant |
| `for X's account/benefit` | 2 | 0.1% | Yes |

**Why not the general rule ("any purpose clause naming a party is the obligee").** It would
be wrong on the largest class (2.3% `on behalf of`), and wrong in the opposite direction —
assigning the obligor's principal to the obligee slot. A rule that inverts the party
relationship on its most frequent input is worse than no rule.

**Not an extension of any prior precedent.** No gold item has ever been annotated on this
basis. The `"for the benefit of Customer"` phrasing sometimes associated with this question
comes from the **synthetic eval-harness pilot**, where the drafter rewrote a synthetic
*stimulus* to make its obligee explicit — not an annotation rule — and §11 places synthetic
items outside the gold set and outside every reported number.

### 3.5.3 Agentless passive clauses (v0.21 — REVIEWER-RULED, drafter dissent recorded)

**Motivating case** — `C04-03` / `C04-087`: *"Each quantity of Miltenyi Product(s) ordered by
Bellicum … **shall be delivered** FCA (Incoterms 2010) Miltenyi's Facility … to **Bellicum's**
designated carrier or freight forwarder … on the Delivery Date."*

The clause is passive with **no by-agent**. Both party names appear, and neither occupies a
core argument slot: `Miltenyi's` is a possessive on a **location**, `Bellicum` is the agent
of a *different* verb (`ordered`) inside a relative clause and a possessive on a **non-party**
recipient (the carrier).

**Rule.**

- `obligor` = **`ABSENT`**. There is no agent. A possessive on a place is not a duty-bearer;
  reading one as the obligor is §3.5's forbidden inference.
- `obligee` = **the party named inside the span** that the performance runs to, where exactly
  one such party exists — here `Bellicum`. It is *in* the span, so §3.5's positional test is
  satisfied. Where no party is named at all, or more than one candidate is equally available,
  `obligee` = `ABSENT`.
- `underspecified = true`, with `obligor` in `missing_fields`.

**Drafter's dissent, recorded rather than dropped.** The drafter recommended `ABSENT` for
both slots. The argument: `obligor` is `ABSENT` here precisely *because* a passive clause has
no agent, and `obligee` is unstated for the same grammatical reason — so taking a promoted
possessive for one slot while taking `ABSENT` for the other is asymmetric, and it lets
`ABSENT` absorb a whole construction rather than genuinely-missing parties. The reviewer
ruled for `Bellicum` on the ground that a party named in the span and owed the performance
should not be discarded. **Both readings are recorded here because this rule governs every
passive delivery and quality clause in the corpus**, and if the held-out check (§7) shows
disagreement clustering on `obligee` in passive clauses, this section is the first place to
look.

**This is NOT §3.5.2.** `C04-087` contains no purpose or benefit clause — verified
mechanically: zero occurrences of `for the benefit of`, `to enable`, `on behalf of`, `for the
account of`. The two rules cover different constructions and are cited separately.

**Precedence with §3.5.2 where a span contains both (v0.28).** Where the span contains an
`on behalf of` phrase, **§3.5.2's carve-out governs**: that party is **obligor-side** and is
never promoted to `obligee` by this section. If no other party occupies the recipient role,
`obligee` = `ABSENT`. *Measured: exactly **one** same-clause instance in the 1,547-segment pool
— `C14-148`, "the Dispute will be submitted to the project manager **on behalf of each party**
to be escalated" (0.06%). Eleven further co-occurrences were checked and rejected: three
definitions, three copular `shall be entitled/deemed` constructions, two with an explicit
by-agent (so this section never fires), and three where the two constructions sit 99–691
characters apart in different clauses.* Recorded so the two sections' overlap is settled rather
than re-derived, and so the class is never mistaken for a common one. The paragraph above
verifies only that **this section's own motivating case** has no benefit marker; it does not
ask what happens when a sentence has both, which is what this precedence line answers.

### 3.5.1 The party slot (v0.28 — merged; supersedes the v0.17 joint-obligor rule)

**This test applies to whichever slot is being filled — `obligor` or `obligee`.**

Formed at v0.28 by merging the v0.17 joint-obligor rule, §3.5.1.1's v0.25 disjunctive rule,
and §8.4.1's value half. All three answered one question — *what string goes in the party
slot?* — selected by one binary test, and stating them apart produced four different
`rules_cited` patterns across four locked items of the same shape (`C17-01` §8.4 only,
`C17-02` §3.5.1 only, `C02-01` both §3.5.1 and §3.5.1.1, `C14-01` three sections).

**Step 1 — does the span name the individual parties filling this slot?**

- **Yes** → the slot holds the **first-named** party. For the **`obligor`** slot,
  `obligor_accept_set` holds every co-obligor or alternative, verbatim, whether or not it is
  registry-resolvable. For the **`obligee`** slot there is no accept-set field — measured at
  joint 0 / disjunctive 3 of 1,547 pool segments and 0 of the 18 locked items (§20.4, F4) — so
  record the alternatives verbatim in `annotator_notes` instead. Conjunctive (`and`) and
  disjunctive (`or`) are annotated identically; record which in `annotator_notes`.
- **No, but a subject is stated** — collective (`the Parties`), distributive (`Each Party`),
  `both Parties`, or relational (`the other party`, `such parties`) → the slot holds the
  reference **verbatim**; `obligor_accept_set` is `[]`. `ABSENT` is factually false here: a
  subject *is* stated, and misusing `ABSENT` makes the item indistinguishable from a genuine
  absent-party item (§8.4.1's own reasoning, retained).
- **No party is named at all** → the slot is `ABSENT` (§3.5).

**No `known_gaps` entry in any branch.** The party slot is a field-value question, never an
item-count one: the obligation is fully representable and the only question is which co-party
a correct extraction may name, which is exactly what an accept-set decides. Whether a
*second, reciprocal* duty is lost is a separate question, answered by §8.4's tag, and
independent of this test — §8.4.1 measured the independence: only **31 of 132 (23%)**
collective-reference sentences carry any reciprocity marker.

**The accept-set must also carry the whole coordinated phrase (v0.33 — forward rule).** Where
the span names alternatives, `obligor_accept_set` holds each alternative verbatim **and** the
full coordinated string as it appears — for `C02-01`, `["Antares", "its Subcontractor",
"Antares or its Subcontractor"]`. **Measured reason:** the model stably emitted the whole
disjunction, *"Antares or its Subcontractor"*, on every aligned run — a form the rule as written
never enumerated, so clause 3 fails even once the accept-set is actually consulted (§5, v0.33).
Quoting the coordination whole is a faithful reading of a span that offers alternatives, not an
error. **Forward-only**; `C02-01` itself is queued for §3.4's freeze-pass exception.

**Non-registry-resolvable values are admitted** (`its Subcontractor`, `the other party`,
`the executor, administrator, or personal representative`). §3.5's test is **positional** —
is the alias in the span? — not resolution-based. Whether the value resolves is §3.9's
question, not this one. The rejected alternative, restricting accept-sets to
registry-resolvable parties, would score an extraction wrong for faithfully quoting an
alternative the contract itself offers.

**Distinguish from §8.4's mutual obligation.** The test is whether the co-obligor is also the
obligee:

| | Mutual (`C17-021`) | Joint (`C17-066`) |
| :--- | :--- | :--- |
| Obligee | the co-party | a third party |
| Duties that exist | **two**, mirror images | **one** |
| Lost by annotating one | **an entire second obligation** | only *which* co-party is named |
| Representable in IR v1 | **No** | **Yes** |

**Motivating cases, retained from the merged sections:** `C17-066` (*"**The Company and RGHI**
will use all commercially reasonable efforts to obtain … **from the counterparty**"*) — joint,
toward a third party. `C02-021` (*"**Antares or its Subcontractor** shall retain sufficient
quantities …"*) — disjunctive; the document promises a definition of `Subcontractor` it never
supplies, and the alternative stays in the accept-set anyway. `C04-117` sentence 3 (*"…then
**the Parties** will negotiate in good faith…"*) — collective, branch 2.

### 3.5.1.1 Disjunctive obligors — folded into §3.5.1 at v0.28

**Retained as a pointer, not deleted.** `C02-01` cites `3.5.1.1` in its `rules_cited`, and a
citation must resolve. Its rule — one item, `obligor` holds the first-named alternative,
`obligor_accept_set` lists every alternative verbatim, no `known_gaps` entry, and
non-registry-resolvable alternatives are admitted — is now §3.5.1 step 1 branch 1, which
annotates `and` and `or` identically. The v0.25 reasoning is preserved there: with `and` both
parties are bound and naming one loses information about the other; with `or` the contract
itself declines to fix which party performs, so the accept-set records the **contract's own**
indeterminacy rather than the annotator's.

**Corpus finding retained from v0.25**, relevant to the not-yet-built defined-terms registry:
of the **six** terms `C02` promises with *"(defined below)"* — `Agreement`, `Device`,
`Subcontractor`, `Syringes`, `Products`, `Trainers` — only **one** (`Device`) is actually
defined. A registry built on resolving that promise would find nothing five times out of six.

---

### 2.3 PII in archived segment text (v0.16)

Email addresses are replaced with a **same-length** placeholder
(`apps/brain/evals/corpus.py::redact_pii`) in the **exclusion log**, which is committed
permanently. Item files are **not** redacted: `segment_text` must stay byte-identical to
what `run_pipeline()` would be handed from the real document, or gold is measuring against
a text the pipeline never sees.

Measured: 6 of 1,547 pool segments carry an email, and **all six are notice or address
blocks** — already §2 exclusions — so PII does not reach item files in practice. Names are
left intact: they are sometimes part of the clause text, and §2.1 requires verbatim
exclusion text so a reviewer can tell a genuine exclusion from a difficulty dodge.

### 2.4 OCR-damaged segments (v0.20 — REVIEWER-RULED)

§2 already requires born-digital text and excludes scanned/OCR'd filings, *"that would
confound extraction quality with OCR quality."* This section states the segment-level
consequence, which §2 left implicit: **a segment carrying character-level OCR corruption is
excluded even when its document is otherwise born-digital.**

**Motivating case** — `C11-049`: *"the prime rate of **merest** charged by Citibank"*,
*"shall bear **merest** at three (3) percent"*, *"enforcing the **tern s** of this
Agreement."* Corrupted tokens would enter a **scored** span with no value any extractor
could be right about — the failure would be logged against extraction quality while
belonging entirely to the corpus.

**~~Measured extent, and it is contained.~~ SUPERSEDED AT v0.41 — see the re-sweep below.**
~~Two signatures — a word split by a stray space (excluding real one-letter words) and the
confirmed `interest`→`merest` substitution — hit 6 of 1,547 pool segments (0.4%), every one
of them in C11, and zero in the other 27 documents:~~

| segment | corruption |
| :--- | :--- |
| `C11-005` | `los s` |
| `C11-006` | `that t` |
| `C11-049` | `tern s`, `merest` ×2 |
| `C11-055` | `information o` |
| `C11-063` | `use c` |
| `C11-102` | `against o` |

~~**No retroactive re-check is required.** Batch 1's locked `C11-01` was checked before this
rule was written: clean in both its span and its full segment. C11 stays in the corpus —
this is a per-segment exclusion, not a document retirement, and retiring a whole document
over 0.4% of its segments would repeat §18.6's difficulty-correlated depletion for no gain.~~

~~**Standing consequence:** the six segment IDs above are excluded on sight in any future
draw, citing this section. A draw hitting one is logged as an exclusion, not silently
re-picked (§2.1).~~ *(Struck rather than deleted, per this document's own
corrections-are-new-text discipline. Both claims — the count and "contained" — are what the
re-sweep below falsifies. C11-01's clean-check finding is not struck: it is re-verified below
against the corrected list, independently, and still holds.)*

#### 2.4.1 Re-sweep of C11, v0.41 — the "6, contained" claim was wrong

**What triggered it.** Adjudicating batch 3's `C11-046` (standard queue) turned up
*"sold in the Franchised Restaurant **uncle** a brand name"* — plainly a corruption of
`under`, sitting inside the clause `C11-046`'s obligation-bearing span would otherwise cover.
It matches **neither** of §2.4's two catalogued signatures (no stray-space word-split; no
`interest`→`merest`-style substitution). Per this document's own Standing Principle 7 — a
detector's "measured and contained" claim is not evidence until re-checked against a case
that falsifies it — a seventh isolated instance was not simply logged and left; document C11
was re-swept in full.

**Method, and the known-answer check performed before trusting any new output (Standing
Principle 7's own discipline).** Two independent detectors run against the full raw text of
`C11.txt` (116,873 bytes) rather than against the enumerated pool alone, so nothing hides in
prose the pool filter drops:

1. A dictionary-hapax sweep — every alphabetic token checked against `/usr/share/dict/words`
   (with a narrow inflection-suffix stripper: `-s/-es/-ed/-d/-ing/-ies/-ly`), unknown tokens
   occurring exactly once inspected by hand against their surrounding context.
2. A stray-single-letter-token sweep — every whitespace-delimited token that is exactly one
   letter (excluding `a`/`I` and parenthesized list markers `(a)`, `(b)`, …) inspected the
   same way.

**Before trusting either detector's new output, both were run against the six already-known
instances and confirmed to still find every one of them** — `los s`, `that t (he)`, `tern s`,
`merest` ×2, `information o`, `use c (f)`, `against o (r)` were all independently recoverable
by these two detectors, not merely re-confirmed by re-reading the original list. This is the
check the original OCR-detector bug (`[a-hj-z]`, CLAUDE.md's Standing Principle 7 entry)
skipped, and skipping it is exactly what let that bug ship.

**Corrected finding: 14 of C11's 128 pool segments (10.9%), not 6 (0.4%) — nearly 2.5× the
document's own hard-vs-standard stratum share, and the true rate is likely still a floor**,
since both detectors miss corruption that happens to land on a real dictionary word by
accident, and a third category — corruption in paragraphs the pool filter drops entirely
(too long, too short, or no modal verb) — was also found (`availability o[f] labor`,
`BKC a[s] required`, `Franchisee Parties shall l[?] appoint`) but does not affect the gold-set
pool and is not tabulated here for that reason:

| segment | corruption | status |
| :--- | :--- | :--- |
| `C11-005` | `los s` (→ loss) | original 6 |
| `C11-006` | `that t he` (→ the) | original 6 |
| `C11-006` | `alI` (→ all) | **NEW — second instance in an already-excluded segment** |
| `C11-010` | `Franchise d Restaurant` (→ Franchised) | **NEW** |
| `C11-029` | `suppler` (→ supplier) | **NEW** |
| `C11-041` | `t e Franchisee's` (→ the) | **NEW** |
| `C11-044` | `; ny payment` (→ any) | **NEW** |
| `C11-046` | `uncle a brand` (→ under) | **NEW — the triggering instance** |
| `C11-049` | `tern s` (→ terms), `merest` ×2 (→ interest) | original 6 |
| `C11-055` | `information o` (→ information or) | original 6 |
| `C11-059` | `an d not to permit` (→ and) | **NEW** |
| `C11-063` | `use c f` (→ use of) | original 6 |
| `C11-063` | `illegal se` (→ use) | **NEW — second instance in an already-excluded segment** |
| `C11-073` | `lt is understood` (→ It), `ln the event` (→ In) | **NEW** |
| `C11-075` | `LNTEREST` (→ INTEREST, in a section heading) | **NEW** |
| `C11-102` | `against o r` (→ against or) | original 6 |

**14 distinct segment IDs** carry at least one instance (`C11-006` and `C11-063` each carry
two, one already known and one newly found, so the row count above is 16 against 14 unique
segments). Every instance is in document C11; the corpus-wide "zero in the other 27
documents" claim is not re-tested here — this re-sweep is scoped to C11 per the instruction
that produced it — and stays unverified rather than reasserted.

**Re-verified, not merely carried forward: batch 1's locked `C11-01` (segment `C11-094`) is
not among the 14** and remains clean under the corrected list, the same conclusion the
original (now-superseded) claim reached by a narrower check. No locked item requires
conforming.

**Why this is a correction to evidence, not a rule change** — the identical framing v0.34
used for §8.9's `on`/`until` rows. §2.4's *rule* (a segment carrying character-level OCR
corruption is excluded) is untouched and was never in question; only its own measurement of
how far the class reaches was wrong, in the same "detector under-reports because it was
never checked against a case it doesn't handle" shape as the `[a-hj-z]` bug this document
already carries as a named cautionary instance.

**Standing consequence, corrected.** All **14** segment IDs in the table above — not 6 — are
excluded on sight in any future draw, citing this section. A draw hitting one is logged as an
exclusion, not silently re-picked (§2.1). `C11-044` is already sitting, undrawn, in batch 2's
paused standard queue (`apps/brain/evals/goldens/batch02/draw.json`) — if batch 2 resumes and
reaches it, it excludes under this section rather than being annotated.

### 2.2 Hard-document stratum

**At least 25 of the 100 items must come from documents at ≥20% cross-reference density**
(the `xref_pct` field in `corpus_manifest.json`). Seven of the 28 documents qualify and
hold 22% of the corpus's obligation sentences, so proportional sampling would land near
this figure anyway — the stratum makes it a floor rather than a hope.

### 2.5 Unrestricted rights-reservations lack monitorable stakes (v0.39 — REVIEWER-RULED)

**Motivating case** — `C04-026`: *"Miltenyi reserves the right, at its sole discretion and
without any restriction or limitation whatsoever, to manufacture, have manufactured, use, have
used, sell, have sold, offer for sale, export, import or otherwise commercialize or dispose of
Miltenyi Products in any manner and for any purpose whatsoever."*

**This clarifies what §2's own exclusion row already means; it does not add a new, unrelated
exclusion.** §2's table excludes a segment that *"contains only a party's right with no
correlative duty."* Read literally that row would swallow the entire `MAY` modality, since
`MAY` — one of IR v1's four modalities (§1, §3.2: `is entitled to`/`is permitted to` → `MAY`) —
is by definition a right with no correlative duty on anyone else. That cannot be the intent, or
no `MAY` item could ever be annotated at all.

**The real test, stated explicitly: does the clause have a future state worth monitoring — not
whether it is grammatically phrased as a right.** This is the **identical underlying principle
§3.2.1 already applies to present-tense performatives**, reached from a different surface
pattern. §3.2.1 excludes a `hereby`-clause because it takes full effect at execution, leaving
nothing left to track. This section excludes a clause for the mirror reason: it is phrased as an
ongoing entitlement, but an **unrestricted, non-exclusive, no-correlative-party** rights
reservation — "we may do whatever we want with our own product, for any purpose" — has no
compliance stake either. There is no deadline, no correlative party relationship, no condition
whose satisfaction or breach anyone could ever observe. Structurally it can never be exercised
"wrongly" or left unexercised in a way that matters, which is the same absence of a monitorable
future state §3.2.1 already names, just reached via a right rather than a performative.

**Rule.** A `MAY`-shaped clause is annotated normally when its permission has **monitorable
stakes** — a correlative party relationship, a deadline or window, a condition gating when it
may be exercised, or any other fact whose presence or absence a monitor could meaningfully
observe (e.g. *"Customer may terminate for cause within 30 days"*). It is **excluded** under §2's
existing "party's right, no correlative duty" row when it is a **broad, unrestricted,
no-correlative-party rights reservation** with nothing to monitor either way — `C04-026`'s shape.
This is a clarification of what that row was always for, not a new criterion layered on top of
it.

**Not decided by grammar alone.** `"reserves the right to X"` is not per se excluded — a narrower,
conditioned, or correlative-party version of the identical phrasing could still be a genuine
`MAY` item. What excludes `C04-026` is the **combination** of unrestricted scope ("in any manner
and for any purpose whatsoever," "at its sole discretion and without any restriction or
limitation whatsoever"), the absence of any correlative party stake, and a ten-verb catch-all
enumeration whose evident purpose is legal completeness rather than describing ten distinct
actions — not the word "reserves" itself.

**Expected to recur.** *"Company reserves the right to..."* / *"Party retains all rights to..."*
boilerplate is extremely common contract drafting, independent of this document. No corpus-wide
frequency has been measured; recorded as a rule now so the next instance is decided by citation
rather than re-litigated, the same posture §4.3.2 and §3.2.1 both took at their own
precedent-setting instances.

#### 2.5.1 The test reaches `shall`-shaped discretion clauses too, not only `MAY`-shaped ones (v0.41 — REVIEWER-RULED)

**This section's own real test was already stated as principle, not grammar** — "does the
clause have a future state worth monitoring," not "is it phrased with `may`." §2.5's worked
example happened to be `MAY`-shaped (`C04-026`'s "reserves the right to"), which left it
untested whether the principle actually reaches a differently-phrased clause with the same
character. It does.

**Confirming case** — `C11-046`: *"The allocation of the Advertising Contribution between
international, national, regional, and local expenditures **shall be made by BKC in its sole
business judgment**."* Grammatically this is `shall`, not `may` — §3.2's table maps `shall` to
`MUST` — and unlike §3.5.3's agentless-passive class, the sentence names an explicit by-agent
(`by BKC`), so it is not excluded on that ground either. What excludes it is the **same
absence of monitorable stakes** §2.5 already named: *"in its sole business judgment"* is
explicit, unreviewable-discretion language. There is no standard BKC's allocation could be
measured against, and therefore no way the clause could ever be breached — the identical
structural absence (no deadline, no correlative party, no condition whose satisfaction a
monitor could observe) `C04-026`'s reservation had, reached here through a `shall`-phrased
duty-to-decide rather than a `may`-phrased right-to-act.

**Rule, stated so the next instance is decided by citation.** §2.5's exclusion is not scoped
to `MAY`-shaped clauses. Any clause — whatever its modal verb — that vests a party with
**unreviewable discretion and no correlative party, deadline, or gating condition capable of
being observed as satisfied or breached** is excluded under §2's "party's right, no
correlative duty" row on the identical monitorable-stakes ground, regardless of whether the
clause is phrased as a right (`may`) or as a duty-to-decide (`shall`/`must`). The modal verb
decides `modality` (§3.2) when a clause is annotated at all; it does not decide whether the
clause clears this exclusion in the first place.

**Not decided by "sole discretion" alone**, the identical caveat §2.5 already applies to
"reserves the right to." A `shall`-clause paired with a *reviewable* standard (*"BKC shall
allocate the Contribution in proportion to Gross Sales"*) or a correlative party stake (*"BKC
shall notify Franchisee of the allocation within 30 days"*) is annotated normally — what
excludes `C11-046` is the combination of an explicit unreviewable-discretion marker and the
absence of anything else a monitor could observe, not the word "discretion" by itself.

**A worked negative example, found by misapplying this section rather than by reading it
correctly the first time (v0.41).** `C14-044`'s S1 — *"NICE may, at its discretion, reschedule
delivery of units of Products for which a PO has already been issued, by shortening the Due
Date, **without any implication**"* — was briefly drafted and locked as its own item (`C14-03`)
on the reasoning that a **restricted scope** ("only already-issued POs") supplied the
monitorable stakes this section requires. That reasoning does not survive re-reading this
section's own test: **scope restriction (which instances a permission covers) is not the same
thing as monitorable stakes (whether an exercise can be checked against a standard).** No
correlative party is named in S1's own span (same as `C04-026`/`C11-046`), no deadline exists,
and *"without any implication"* is at least as direct a no-monitorable-stakes signal as
`C11-046`'s *"sole business judgment"* — arguably more direct, since it states in terms that
exercising the discretion carries no consequence at all. Caught at batch verification, not at
original drafting; `C14-03` is retracted and S1 is excluded under this section, the identical
disposition as `C04-026`/`C11-046`. Recorded here, deliberately, as a **negative** worked
example — restricted scope is *evidence worth noticing* but is not itself sufficient to clear
this section's test, and the next annotator tempted to treat "not unrestricted" as "therefore
monitorable" should check for an actual correlative party, deadline, or observable gating
condition before relying on scope alone.

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

### 3.2.1 Present-tense self-executing performatives ("hereby-clauses") (v0.38 — REVIEWER-RULED)

**Motivating case** — `C22-022`: *"the Seller **hereby grants** (and will cause each other Seller
Party to grant, following each applicable Closing Date, to the Purchaser Licensees) a
perpetual... license to use any and all Licensed Trademarks..."*

**The connecting principle, stated explicitly rather than left as an unrelated new category:
this is the same non-obligation class the "will"-ambiguity rule above already carves out, one
tense earlier.** This IR's entire purpose is monitoring a **future state** until fulfilled or
breached. The "will"-future-fact exclusion above excludes a clause that states a future fact
about the agreement rather than a party's undertaking, because there is no undertaking left to
monitor. A present-tense self-executing performative — `hereby grants`, `hereby assigns`,
`hereby appoints`, `hereby releases`, `hereby waives` — fails for the identical reason, just in
the present tense: it takes full legal effect **at execution**, so by the time any obligation
could be monitored, the act is already done. There is no future state for either construction to
monitor; only the tense differs.

**Rule.** A clause whose only verb is a present-tense self-executing performative of this kind is
**not obligation-bearing** under IR v1's four modalities and is **excluded**, the same disposition
as the "will"-future-fact case above — not annotated as `MUST` (or any other modality) on the
theory that a grant/assignment/appointment/release/waiver is implicitly an obligation to have
performed it. `§3.2`'s modality table is exhaustive of what maps to each of the four values;
`hereby grants` and its siblings match none of its rows.

**Does not exclude a coordinated clause that is genuinely future-looking.** Where a hereby-clause
is coordinated with a second verb stating a real future undertaking — as in the motivating case,
*"and will cause each other Seller Party to grant... following each applicable Closing Date"* —
the future-looking half is annotated normally under whatever rule it independently qualifies for
(here, §4.3.2's self-performance/third-party-compliance shape, reduced to **one** item because
the self-performance half is excluded under this rule rather than annotated — see `C22-02`'s own
`annotator_notes` for how this interacts with §4.3.2 in practice).

**Expected to recur.** Present-tense performatives are standard drafting in license, IP,
assignment, and release clauses specifically — exactly the segment classes where a hereby-clause
is likely to sit alongside a genuine future obligation, as it does here. No corpus-wide frequency
has been measured; recorded as a rule now so the next instance is decided by citation.

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

**AMENDMENT (v0.33) — one defined exception, and it is an amendment, not a reading of the
sentence above.** The rule as written is categorical, and it stays categorical everywhere
except here. An accept-set found to be **genuinely under-scoped** — it omits a label a
competent annotator would have defended *at authoring time*, independently of any prediction —
may be widened **only during §10's pre-scheduled freeze conforming pass**, never in between.

**Why the exception is bounded to that pass rather than granted generally.** Three properties
of the freeze pass are what make it safe, and none holds for an ad-hoc widening:

1. **It is pre-scheduled.** Its timing is fixed by §10 before any prediction is seen, so it
   cannot be reached for in response to a disappointing number.
2. **It restamps and re-records anyway.** Widening is free there; between passes it forces a
   conforming pass, mixed stamps, and **all cassettes stale at once** (§22).
3. **It is reviewed as one batch.** Every widening is adjudicated together against the whole
   set, where a pattern of self-serving widenings is visible; one at a time, it is not.

**The justification test, which is the real safeguard.** A widening qualifies only if the
omitted label is defensible **from the sentence alone**, stated without reference to what any
model emitted. If the argument for a label cannot be made without pointing at a prediction,
that is fitting gold to the model and the rule above forbids it, freeze pass or not.

**Explicitly NOT adopted: the reading that §3.4 only ever barred fitting to *this* prediction.**
That reading is defensible and was proposed, but it is a *softening* of a categorical rule, and
adopting it silently would mean the rule had been quietly relaxed by the first case that
pressed on it. It is recorded here as a **defined, bounded exception with its own name and its
own test**, so that what changed is legible in the diff and countable later.

**Applies identically to §3.6's `object_class_accept_set`** and to §3.5.1's
`obligor_accept_set`. **The full freeze-pass queue is §10.1**; these widenings are its item
**F1**, and §3.6's v0.45 breadth audit (**F5**) expands them from three to a systematic pass.
**Two locked items are queued under this exception** — `C02-03`
(`invoice_costs`, a compound of two of its own accept-set members) and `C11-01`
(`principal_interest`, the possessor-anchored reading of *"the Principal's interest in
Franchisee"*, where all three existing entries anchor on the thing owned). Both are
**deliberately NOT widened now** and both **keep scoring as failures until the freeze pass**;
see §9's inline disclosure requirement for how the resulting understatement is reported.

**REINFORCED, not re-litigated, by §7's cold second-annotator run (v0.43, 2026-08-29).** A
second annotator, working independently and blind to this queue, produced `INVOICE`- and
`principal_interest`-shaped labels for these same two items (`C02-03`, `C11-01`) —
`apps/brain/evals/goldens/holdout/RESULTS.md`'s Attribution section. This is independent
confirmation that the widening is warranted, not new evidence that changes when it happens:
the bounded-exception rule above still governs, and both items keep scoring as failures until
the pre-scheduled §10 freeze pass.

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

**Tested and held (v0.41):** an in-segment anaphoric antecedent from a non-adjacent sentence
does **not** satisfy this rule's in-span requirement, even where the real-world agent is
obvious from context — `"such rescheduling"` unambiguously pointing back to an earlier
sentence's named actor is not the same as that actor appearing in `span_text`. This rule's
span-scoped strictness is deliberate and stays deliberate: it is a different, more
consequential boundary than §2.6/§3.8.4's segment-scoped eligibility and condition-counting
extensions, because it feeds §5 clause 3's scored predicate directly rather than an eligibility
or count decision, and "the anaphora seems unambiguous here" does not stay clean at the next
instance once admitted once. See `C14-044`'s S4 for the confirming instance — considered and
declined, `obligor: ABSENT`, the strong contextual reading recorded in `annotator_notes`
instead of acted on.

### 3.5.4 `obligee` assignment is modality-independent (v0.41 — REVIEWER-RULED)

**The first `MAY`-modality item in the gold set**, and the first time this question could even
arise: does a permission (`MAY`) get an `obligee` the same way a duty (`MUST`) does, or is
`ABSENT` the default whenever modality isn't `MUST`, on the reasoning that a right isn't "owed"
to anyone the way a duty's performance is?

**Motivating case** — `C13-041`: *"Either party shall have the right to terminate this
Agreement effective upon written notice **to the other party** in the event the non-notifying
party becomes insolvent..."* `"the other party"` is named in-span, both as the recipient of
the termination notice and as the party actually affected by the termination being exercised.

**Rule, stated so it needs no re-deriving at the next `MAY`/`SHOULD` item.** §3.5's test —
*"annotate the party alias exactly as it appears inside `span_text`"*, positional, not
modality-conditioned — governs `obligee` **identically regardless of `modality`**. `obligee`
names the party toward whom the clause's right or duty runs, not specifically "who is owed a
`MUST`." A `MAY`-modality right exercised against a specific named counterparty gets that
counterparty as `obligee`, on the same positional ground §3.5.3 already promotes an in-span
party to `obligee` for an agentless passive. `ABSENT` is reserved for a **genuine absence of
any named counterparty** — `C04-026`'s unrestricted rights-reservation is `ABSENT` (excluded
entirely under §2.5, in fact) precisely because it names no correlative party at all, not
because it is `MAY`-shaped. Modality decides which of the four values goes in the `modality`
field; it does not decide which field-assignment rule applies to `obligor`/`obligee` — those
stay §3.5's ordinary positional test throughout.

**Not a license to invent a counterparty for every `MAY`.** Where a permission genuinely names
no one it runs against (a broad self-directed right, `C04-026`'s own shape), `obligee` stays
`ABSENT` — this section changes nothing about that outcome, only about *why* it's `ABSENT`:
absence of a named party, never absence of a `MUST`.

### 3.6 `object_class` — open vocabulary, accept-set required

`object_class` is free vocabulary (snake_case). Always author an
`object_class_accept_set`. The pilot recorded a real miss here (`customer_personal_data`
predicted, gold accept-set too narrow).

Author the accept-set generously at annotation time — 3–6 plausible labels is normal.
Same freeze rule as §3.4, including its v0.33 freeze-pass exception.

**Two enumerations are REQUIRED, not optional (v0.33 — forward rule, batch 3 onward).**
Both were derived from real failures in the first scoring run, and both are cheap to satisfy
at authoring time and expensive to fix afterwards:

1. **Both nominal anchors, where the object phrase has two.** *"the Principal's interest in
   Franchisee"* can be labelled from the **possessor** (`principal_interest`) or from the
   **thing owned** (`franchise_interest`). Both are faithful readings of the same phrase; the
   accept-set must carry both. `C11-01`'s three entries all anchored on the thing owned, and
   the model stably chose the possessor on all three runs.
2. **Compound forms built from members already in the set.** Where the set holds `invoice` and
   `costs`, it must also hold `invoice_costs`. `C02-03` failed on exactly that compound while
   a sibling run emitting the bare `costs` passed — the same clause scored two ways across two
   runs of the same segment.

**Number is NOT one of these enumerations.** Do not pad a set with plurals: §5 clause 5
normalizes grammatical number on both sides as of v0.33, so a set carrying both is redundant,
not safer.

**ACCEPT-SET BREADTH — UNBLOCKED AND SCOPED (v0.45 — REVIEWER-RULED).** REDESIGN scope item 1's
breadth half was **held pending item 0**, because its shape depended on whether §5 is one
predicate or two. §5.1 rules **two**, and that settles the shape rather than merely releasing the
hold: **breadth acts on the SET, which is the thing §5 clause 5 actually reads, so it is a
pipeline-side lever and the only one in this cluster that can move criterion 2.** A convention on
the *slot* — which annotators argue about — binds no model, since the model never reads this
document; its prompt asks only for *"a short lowercase snake_case label"*.

**Two anchors, and one explicitly disqualified.** The set is authored against (i) §3.6's own
stated **3–6** band and (ii) **the depth range the model actually emits**, measured in
`OBJECT_CLASS_INVESTIGATION.md` §9.2–§9.3: the model emits a head-only (1-token) label **28%** of
the time while **62% of gold items cannot accept one at all** (only 12 of 32 sets carry a
head-only member). Where those coincide clause 5 fails regardless of any convention.
**Disqualified as an anchor: the cold annotator's median.** Cold's `object_class` sets are wider
(median 5 against gold's 3.5) but nothing shows them *calibrated* rather than merely risk-averse,
and the one field where calibration is checkable **inverts** — cold's `action` accept-sets average
3.51 as written and **1.93 once restricted to legal taxonomy verbs, below gold's 2.12, with 3 of
41 holding no legal member at all.** Anchoring on cold would be fitting gold to a single
unvalidated second annotator.

**Both §5-of-the-note hazards carry forward unchanged**: widening is **monotone**, so a breadth
pass between two criterion-2 measurements makes the delta uninterpretable — it runs **before** the
next baseline, or criterion 2 is reported against both the pre- and post-widening sets; and every
widening must be defensible **from the span alone**, stated without reference to any prediction
(§3.4's justification test). **Venue is unchanged: §10's pre-scheduled freeze pass**, whose scope
expands from the three individually-queued widenings (`C02-03`, `C11-01`, `C02-01`) to a
systematic breadth audit. Doing it piecemeal forces a conforming pass per item, which is §22's
blocker.

**DEPTH — SCOPED TO `A`, AND STILL UNWRITTEN (v0.45 — REVIEWER-RULED).** The specificity/depth
question (`C06-01` `adequate_assurance_of_future_performance`/`adequate_assurance`, `C13-01`
`pertinent_records`/`records`, `C14-01` `withholding_tax`/`taxes`) is ruled to be **§5.1 `A`'s
scope and nothing else** — a convention on which label occupies the *slot*. Consequences, stated
so the scope cannot later be misread as larger than it is:

- It **cannot** constrain criterion 2, now or ever, because §5 clause 5 never reads gold's slot.
  Anything written here governs annotator agreement and any §7 re-run.
- Its **pipeline half does not exist separately** — it collapses into the breadth item above
  (`OBJECT_CLASS_INVESTIGATION.md` §9.3), which is where set coverage of the model's real depth
  range is handled.
- The **comparison-rule shape stays dead**: head-only matching was falsified by measurement
  (§9.5 — it buys one legitimate depth fix by erasing three real distinctions, including the
  `self_`/`third_party_` pair §4.3.2's naming convention exists to keep apart).

**No depth convention is written here, deliberately.** §9.4's precondition is unmet: neither
annotator records the object noun phrase a label was built from, so any depth rule
("keep the head", "keep head plus restrictive modifiers", "keep the whole NP") is stated against
an anchor gold does not store, and is therefore **checkable at authoring time and unverifiable
afterwards** — a limitation that now also attaches to §3.6.1. Writing a rule whose compliance
cannot be audited across the locked set would be the shape of guarantee this project has
repeatedly had to undo. **Open, with its cost stated: three items, all batch-3 and cassette-less,
so writing it later is as cheap as writing it now.**

**This rule is forward-only and restamps nothing.** It governs items annotated from batch 3
onward. Locked items are not re-authored against it — that is the freeze pass's job (§3.4's
exception, §10). **Scope note added at v0.44: this forward-only clause governs the two
enumerations above and nothing else.** §3.6.1 is retroactive and says so in its own text; the
two are different in kind, and the difference is argued there.

### 3.6.1 `object_class` must not encode `action`, `obligor` or `obligee` (v0.44 — REVIEWER-RULED, RETROACTIVE)

`object_class` names **the thing the obligation is about**. It must not carry material whose
content is already the value of clause 2 (`action`), clause 3 (`obligor`) or clause 4
(`obligee`) for the same item.

**The restatement test.** Take the object noun phrase — the phrase in `span_text` naming what
the duty acts on, the same phrase `prompts/extraction/v3.yaml` asks the model to record as
`object_raw_text`. Identify its head noun. For each remaining token group in a candidate label,
ask: **does it name the duty type or a party, rather than a property of the thing?** If it does,
it is restated material and does not belong in the label.

**Two carve-outs, both load-bearing, both derived from real locked items.**

1. **A token that appears in the span as part of the object's own name is never a restatement**,
   even where it shares a root with the item's `action`. `C02-01`'s span reads *"…as **retained
   repository samples**…"* and `C14-01`'s reads *"…including **withholding taxes**…"* — both
   label the object by the name the document itself gives it, and both were checked against this
   rule at v0.44 and cleared. The test is **content-relative to this item's own field values and
   its own span**, never a string blacklist against the `ACTIONS` list. §3.6's own enum-2 example
   `invoice_costs` clears for the same reason: `invoice` there names a document, not the act, and
   `C02-03`'s `action` is `PROVIDE`.
2. **§4.3.2's `self_` / `third_party_` naming convention is unaffected.** Those prefixes name
   *whose conduct* the object concerns in a flow-down split; in `C04-05` the third party is
   neither the obligor nor the obligee. A prefix falls foul of this rule only when it reproduces
   **this item's actual `obligor`/`obligee` value**, as `distributor_` does in `C10-02`.

**Why this is a CORRECTION and not a convention — the argument that makes it retroactive.**
§5 is conjunctive, so a label that restates the `action` makes clauses 2 and 5 **co-vary**: one
judgment gets scored twice. An item can lose two clauses for a single mistake and gain two for a
single lucky guess. That is a defect in the instrument rather than a preference between two
faithful labels, and it is wrong under *any* specificity convention — which is exactly what
distinguishes it from §3.6's two enumerations. An older item authored without those is merely
narrower; an item violating §3.6.1 is measuring the wrong thing. **It is also detectable without
reference to any prediction**, so applying it retroactively raises no §3.4 freeze-rule question.

**Scope, and the asymmetry between the slot and the set — this is the part that constrains the
rule, and it was settled by measurement.**

- **The slot rule is a correction and applies retroactively.** §5 clause 5 never reads gold's
  slot value at all (it tests `prediction ∈ accept_set`), so correcting a slot has **zero**
  effect on criterion 2 and cannot fit anything to a prediction. It affects annotator
  comparison only.

  > **CORRECTION (v0.45): "free" was the wrong word for this, and only "free on the pipeline
  > side" was ever established.** The bullet above is accurate as written — the correction is to
  > how the ruling was *summarised*, in v0.44's changelog entry and commit message, as a slot
  > half that is *"retroactive and free."* It is free of any effect on criterion 2. It is **not**
  > free of effect on the other predicate, because §5.1's `A` compares the **slot** — which is
  > exactly the field this rule changes — so a "free" retroactive edit moves a published
  > measurement. Measured rather than inferred: restamping `C10-02` flipped its clause-5
  > comparison against the sealed cold output from *disagree* to *agree*, moving the published
  > clause-level profile's `object_class` count from **6 to 5** of 23. **K itself did not move**
  > (`C10-02` still disagrees on clauses 2, 3 and 4, so it stays one of the 14) and no verdict
  > changes — this is a real but bounded effect, and it is stated at that size rather than
  > inflated. **The rule stands unchanged; what changes is the disclosure owed with it.**
  >
  > **A second, separate defect in this rule surfaced at v0.45's close-out and is NOT fixed
  > here: §3.6.1 CONFLICTS with §4.3.2's shared-root naming convention at `C04-04`** (`action =
  > USE` against `object_class = self_compliant_use`), asymmetrically, on whichever half of a
  > flow-down split has the root as its own action verb. It is a rule conflict rather than a bad
  > label, it is reproducible by any future §4.3.2 split on a taxonomy-verb root, and the v0.44
  > §10 screen missed it — its **second** recorded miss. Tracked as **§10.1's item F3**, with the
  > three candidate resolutions and their costs stated there.
  >
  > **RESOLVED v0.48 (§10.1 F3) — §3.6.1 does NOT yield; §4.3.2's root choice does.** The ruling
  > and both restamps are in **§4.3.2**, not here, because what changed is a *naming convention*
  > and not this rule: §4.3.2 now constrains the shared root so neither half's label restates its
  > own item's `action`, and `C04-04`/`C04-05` move to `self_regulatory_compliance` /
  > `third_party_regulatory_compliance`. **Nothing in this section is amended by that ruling** —
  > it stands categorical, and it stayed categorical because that is precisely why it won. One
  > premise of the conflict was also false and is corrected there: §4.3.2 *recommends* its
  > convention, it does not require it.
  >
  > **The v0.44 screen was re-run at v0.48 against all 32 items and validated first**, against 12
  > known answers including both this section's own corrected instances, `C04-03`'s retained
  > `product_delivery` member, and `C10-02`'s documented `_listing` blind spot. Its first draft
  > failed two of the twelve — it missed `deliver`→`delivery` and `indemnify`→`indemnification`,
  > both nominalisations of verbs this very section has already ruled on — and was corrected
  > before being trusted, Standing Principle 7 applied to a re-run of the screen that principle
  > was already attached to. **Result: after the two restamps, `C04-04` is cleared and the only
  > remaining slot-level hits in the whole set are `C02-01` and `C14-01`, both carve-out 1 clears
  > already adjudicated at v0.44.** The screen's stated limitation is unchanged — it is still a
  > lower bound, still blind to an item whose label restates a *real* verb `action` does not hold,
  > and the by-hand re-run against the §8.8 items is still owed at the freeze pass.
  >
  > **A THIRD defect in this rule is now filed rather than fixed: it tests the `action` SLOT
  > VALUE only, and not `action_accept_set`.** The v0.44 screen swept each item's `action`,
  > `obligor`, `obligee` and `obligor_accept_set` — the action accept-set was never in it. The
  > co-variance argument that makes this section a correction runs through the accept-sets, since
  > §5 clause 2 tests *membership*, not slot equality.
  >
  > **MEASURED, AND THE FIRST MEASUREMENT WAS WRONG — the corrected numbers are these.** Across
  > all 32 items, the accept-set screen finds **exactly one instance, and it is the same item
  > before and after F3**: `C04-04`'s *old* slot `self_compliant_use` restated `COMPLY` (via
  > `compliant`) as well as `USE`, and its new slot `self_regulatory_compliance` restates `COMPLY`
  > via `compliance`. **Exposure was 1 before v0.48 and is 1 after.** F3's root choice therefore
  > neither creates this hazard nor removes it — it **inherits** one that was already there, which
  > is a materially weaker objection to the chosen root than the one first written down.
  >
  > **The first pass reported ZERO, and that was a detector failure, not a fact.** The screen's
  > stemmer generated `complyance` rather than `compliance`, so `COMPLY` → `compliance` was
  > invisible to it; the miss surfaced only because the automated count contradicted a claim
  > reached by reading the label. **This is the THIRD nominalisation miss by this same screen in
  > one session** — `deliver`→`delivery` and `indemnify`→`indemnification` were the other two, both
  > caught by the known-answer gate before any count was trusted, this one caught by a
  > contradiction with prose. All three are the same `y`/`e`-boundary family. Standing Principle 7,
  > and specifically its *"a clean-looking result is not evidence until you have checked what it
  > does on a case whose answer you already know"* clause: **a zero is exactly as much a detector
  > output as a positive count, and reads more reassuringly.**
  >
  > Extending this rule to accept-sets is a retroactive rule change and is **§10.1 F12**,
  > deliberately not decided inside F3.
  >
  > **Forward requirement.** Any retroactive slot edit states its effect on **both** predicates,
  > and "free" is never used unqualified for either. §5.1 §A2 is why: the slot is unread by §5
  > and read by `A`, so the two predicates have *opposite* sensitivities to exactly this kind of
  > edit, and a single word cannot honestly cover both.
- **The set rule is WIDENING-ONLY: an accept-set must contain at least one member that names
  the object with no restated material.** A member is **never removed** by this rule. The
  reason is measured, not stylistic: `C04-03`'s set carries `product_delivery` (against
  `action = DELIVER`), and `C04-087` run 2 **emits exactly `product_delivery`**. Stripping
  restating members retroactively would therefore flip a currently-passing clause 5 to failing
  — a **narrowing made with the prediction already visible**, which is §3.4's prohibition
  running in the more dangerous direction, since narrowing can only manufacture failures.
  Widening-only is monotone and cannot.
- **Retroactive widening is confined to items with no recorded cassette.** For `C10-01` and
  `C10-02` there is *no prediction in existence* — `C10-016` was never recorded — so the
  widening is provably not prediction-fitted. For any item that **is** cassette-backed, a
  §3.6.1 widening waits for §10's freeze pass under §3.4's bounded exception, alongside the
  widenings already queued there.

**The v0.44 re-check across all prior batches (§10's requirement), logged rather than asserted.**
All 32 locked items were screened, every `object_class` slot value and every accept-set member,
against each item's own `action`, `obligor`, `obligee` and `obligor_accept_set`. Four candidates
beyond the two rulings were adjudicated individually and **all four cleared**: `C02-01` and
`C14-01` under carve-out 1 above; `C22-02` as a detector false positive (`license`, the thing
granted, prefix-matching the obligee `the Purchaser Licensees` — and its `action` is `ENSURE`,
so `_grant` restates nothing either); `C04-03`, whose **slot** `product_shipment` is clean, with
its `product_delivery` accept-set member retained under the widening-only rule above.

**Standing Principle 7 note on that screen, recorded because it failed in the instructive
direction.** The screener matches action nominalizations by stem, and **it did not flag
`C10-02`'s `_listing`** — the item's `action` is `ESTABLISH` while the real verb is *"add"*
(§8.8), so no stem could match. The violation was already known from the investigation, which is
the only reason the miss was visible. **The screen is therefore a lower bound on §3.6.1
violations, not a census**, and specifically it is blind to any item carrying an
`action_not_in_taxonomy` tag, where the label may restate the *real* verb while `action` holds a
different one. Re-run it by hand against the §8.8 items at the freeze pass.

**The two corrected instances (v0.44).**

| item | field | was | now | restated material removed |
| :--- | :--- | :--- | :--- | :--- |
| `C10-01` | slot | `product_liability_indemnification` | `product_liability` | `_indemnification` restates `action = INDEMNIFY` |
| `C10-02` | slot | `distributor_insurance_certificate_listing` | `insurance_certificate` | `distributor_` restates `obligee`; `_listing` restates the real verb *"add"* |

Both accept-sets gain their corrected slot value and keep every existing member. `C10-01`
already satisfied the set rule before this amendment — `design_defect_liability` carries no
restated material — so **only its slot changed**; `C10-02`'s set satisfied it nowhere (all three
members restate: `_listing`, `_addition`, `_designation`), so `insurance_certificate` is added
under the widening-only rule.

**A named, deliberate residue.** The violating members stay in both sets, so the instrument
still *admits* a prediction that duplicates a scored field — it simply no longer *requires* one.
Removing them is a narrowing and belongs to the freeze pass, not here. Recorded so it is a known
cost rather than an oversight.

**What this rule does NOT settle.** It says nothing about how specific a label should be once
the restated material is gone — `product_liability` versus `liability` is the **depth** question,
which is open and separately scoped. The slot corrections above therefore strip **only** the
restating tokens and change nothing else, so that the depth ruling stays unprejudiced.

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
obligation is real and annotatable. Set the affected field to `null`, name that field in
`missing_fields`, `known_gaps` gains `"redacted_value"`, and record the literal phrase in
`redacted_phrase` (§8.1). **Do not set `underspecified` on account of the redaction (v0.28)** —
§3.9's trigger list is closed and a missing temporal is not in it (§15.3).

**`redacted_clause` — do not annotate an item for the redacted clause.** There is no
obligation to annotate; asserting one would be fabrication, and asserting its absence would
be equally unfounded. Other obligations in the same segment are annotated normally. The
segment is tagged `redacted_clause` at segment level so the gap is visible downstream.

**Precedence when combined with another tag (v0.22).** `redacted_clause` is the one tag
whose semantics differ from every other: it removes a span from **both** criteria's
denominators as unscoreable, rather than merely flagging it. If it ever appears in a
`known_gaps` list alongside another tag, **unscoreable dominates** — the item leaves both
denominators regardless of what else it carries. This cannot arise under the rule as
written (a `redacted_clause` is tagged at *segment* level and no item is annotated for it),
but the list format makes the combination expressible for the first time, so the precedence
is stated rather than left to be discovered.

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

### 3.8.2 Where a condition quote starts, and when two phrases are two entries (v0.33)

Two conventions §3.8 never fixed, each of which cost a real clause-7 failure in the first
scoring run. **Both are forward authoring rules: they govern items annotated from batch 3
onward, restamp no locked item, and no cassette goes stale.**

**Rule A — the quote begins at the qualifier's own introducing marker, exclusive of any
coordinating adverb or conjunction that merely attaches it to the previous clause.** Quote
from `provided that`, not from `further provided that`; from `if`, not from `and if`. The
excluded words (`further`, `and`, `also`, `moreover`) join the qualifier to its neighbour and
say nothing about the circumstance itself.

*The failure that produced it.* `C04-01`'s gold entry reads *"**further** provided that amounts
owed…"*; the model emitted *"provided that amounts owed…"* — identical but for that one leading
word, **97.8% string similarity, and a clause-7 failure on all aligned runs**, because clause 7
is exact equality after whitespace normalization.

**This is recorded as a SYMMETRIC ambiguity, and the rule does not pretend otherwise.** Both
strings are verbatim substrings of the segment and §3.8 gave no rule for where a qualifier
quote begins, so gold's inclusion of `further` was **arbitrary, not correct**. Rule A picks a
convention for future items; it does **not** establish that the model was wrong, and it must
not be cited as evidence of an extraction defect. The alternative — changing the prompt to
match gold's arbitrary choice — was considered and rejected as fitting the model to an
accident.

**Rule B — adjacent conditional phrases are separate entries, one per syntactically distinct
phrase, even when juxtaposed with only a comma and no conjunction.**

*The failure that produced it.* `C11-094` opens *"If the Principal is a natural person, upon the
death or mental incapacity of a Principal, …"* — two distinct circumstances, annotated as two
entries. The model emitted them as **one** comma-joined string in runs 1 and 3 and as **two** in
run 2: unstable 2:1 against gold on byte-identical input at temperature 0.

**Rule B is NOT §17.2's boundary, and the two must not be conflated.** §17.2 declines to split
`and`/`or` **inside** one condition, because `ir_compile.py` deliberately does not do that and
gold must test what the extractor produces. Rule B concerns two **separate** phrases that were
never one condition — no internal boolean is involved, and nothing is being asked of the
compiler.

**Neither rule is validated against model behaviour, and neither may be assumed to fix
anything.** Whether the extraction prompt can be worded to produce either convention is a fact
about the model, settleable only by a live probe — see the Tier-B probe tracked in CLAUDE.md
against segments `E07-010`, `C11-094` and `C04-117`. Until that probe runs, these rules make
**gold's** side of the convention explicit and nothing more.

**What makes a phrase a condition (v0.28 — F8).** A `conditions` entry states a **circumstance
under which the duty applies**. A phrase that restricts **which instances of the object** are
covered belongs to the object, not to `conditions`.

**Removal test.** Delete the phrase. If the **duty** now applies in circumstances it previously
did not → **condition**. If the duty is unchanged and only the **set of things it covers** is
broader → **object scope**, and it is not a `conditions` entry.

| phrase | verdict |
| :--- | :--- |
| *"in connection with any action, suit or other proceeding"* (probe `E05-P1`) | **object scope** — the duty to indemnify is unchanged; only the covered Damages broaden |
| *"giving any notice required or permitted under this IP Agreement"* (`C22-01`) | **condition** — without it the duty applies to every party at all times |
| *"upon reasonable notice and approval by TIBCO"* (`E07-01`) | **condition** |
| *"solely to the extent Miltenyi's exercise of rights … is required"* (`C04-01`) | **condition** |

**This matches the extraction prompt's own field definitions**, which is what gold must predict:
`prompts/extraction/v2.yaml` asks for `object_raw_text` as *"the literal phrase from span_text
**naming** that object"* and `condition_raws` as *"a list of literal 'if'-type conditional
phrases … that this obligation depends on."* A scope modifier on the object is neither, so a
correct extraction emits it in neither field — and gold annotating it as a condition would score
a correct extraction wrong on §5's count-sensitive clause 7.

**Verified against every existing entry: all 8 `conditions` entries across the 18 locked items
pass the removal test as conditions, and none is an object-scope phrase.** The test overturns
nothing. Measured exposure for the class it settles: obligations carrying an
`in connection with` / `arising out of` / `relating to` post-modifier occur in **93 pool
segments (6.0%)**.

### 3.8.1 Routing a trailing qualifier (v0.28)

A qualifier attached to an obligation has **three** possible destinations, and through v0.27
no rule chose between them: an ordinary `conditions` entry (§3.8); a carve-out dropped from
`conditions` and tagged (§8.2); or a **second gold item** (§4.3). §8.2 covered exactly one
marker word. The locked set had already made this choice twice by intuition — `C14-01` routed
*"(unless an exemption is provided)"* to destination 2, `C04-01` routed *"further provided that
amounts owed … are actually paid"* to destination 1 — both defensible, neither citable.

**Marker words do not decide the destination.** Apply in order.

**Branch 1 — would this qualifier, standing alone, be an obligation-bearing clause under §2
and §3.2?** A real deontic undertaking borne by a party — or by an unstated agent under
§3.5.3 — is a **separate obligation**: split under §4.3 and annotate it as its own item, or log
it as a §2 exclusion if it fails eligibility alone. It does **not** go in `conditions`.

*Not branch 1:* a future fact about the agreement (§3.2 — *"the Gas shall be deemed 'dry'"*);
an interpretive or savings provision with a non-party subject (§8.8's class — *"nothing in this
Section shall limit…"*, *"no such severability shall be effective…"*); a conditional clause
using the archaic conditional `shall` (*"if a claim shall be made against the other parties"*).

**Branch 2 — does it state a circumstance under which the duty applies?** (affirmative) →
**one verbatim `conditions` entry** (§3.8). Internal `and`/`or` stays unparsed (§17.2).
— `C04-01`.

**Branch 3 — does it state a circumstance that removes or narrows the duty?** (negative
carve-out) → `conditions` does **not** receive it; `known_gaps` gains
**`exception_unsupported`**; the full carve-out is recorded verbatim in `annotator_notes`; the
span still contains it per §3.1. — `C14-01`.

**Branch 1 is tested first.** A qualifier carrying its own obligation is an obligation whatever
marker introduced it, and misfiling one as a condition loses an entire item — the loss §8.4
already refuses to accept for mutual obligations.

**Why branch 1 delegates rather than applying its own test (F3, §20.4).** Two earlier drafts
failed. *"Has its own subject and modal"* has a measured **63.3% false-positive rate**
(hand-classified seeded sample, n=30: 11 genuine against 19 interpretive/definitional).
*"Predicates a deontic modal of a party subject"* wrongly rejects agentless passives that
§3.5.3 explicitly admits as obligations. Delegating to §2, §3.2, §3.5.3 and §8.8 — which
already decide what counts as an obligation-bearing clause — survives both cases and adds no
fourth independent judgment.

**Why branch 3 drops rather than absorbs.** `packages/ir-spec/SPEC.md` §6: an `UNLESS`
*"must never be silently dropped, and never silently absorbed into `condition` as if it had
been an `IF` clause. Silently discarding a legal carve-out is a correctness bug with real
stakes for a compliance tool."* Gold honours that — the carve-out is neither absorbed nor lost,
it is tagged and recorded. **The compiler currently does not**; see §8.2.

**Measured, with the limits of the measurement stated.**

| marker | segments | % of pool | occurrences | modal in tail | genuine branch 1 |
| :--- | --: | --: | --: | --: | :--- |
| `provided (that / , / , however)` | 159 | **10.3%** | 171 | 128 (74.3%) | **~47 (~27%)**, 95% CI [21.9%, 54.5%] |
| `unless` | 103 | 6.7% | 109 | 36 (33.0%) | **unmeasured** |
| `except that / as / for / to the extent` | 119 | **7.7%** | 137 | 62 (45.3%) | **unmeasured** |
| `subject to` | 175 | 11.3% | 198 | 90 (45.5%) | **unmeasured** |

**Only `provided that` was hand-classified.** The 63.3% false-positive correction is measured
for that row alone; the other three rows' modal-in-tail figures are **upper bounds, not
branch-1 estimates**, and must not be quoted as shares. What holds regardless: non-`unless`
carve-out markers outnumber `unless` roughly **1.85 : 1** by segment across 19–21 of the 28
documents, and §8.2 covered none of them.

**Marker equivalence for branch 3 (v0.40 — REVIEWER-RULED).** Branch 3's own test — *"does it
state a circumstance that removes or narrows the duty?"* — was already written marker-agnostic;
nothing in it names the word `unless`. What was missing was a **reviewer-ruled confirmation**
that a non-`unless` marker actually routes there in practice, not just in the abstract, plus a
citable list so future annotators recognize the semantic class rather than pattern-matching on
one literal word.

**Motivating case** — `C10-016`: *"...except to the extent the liability arises as a result of
the wilful misconduct of the Distributor."* This narrows the Supplier's indemnification duty
under a stated circumstance — the identical shape as `C14-01`'s *"unless an exemption is
provided"* — headed by `except to the extent` instead of `unless`. Reviewer-ruled: routes
through branch 3 exactly like `unless` does. `known_gaps` gains `exception_unsupported`; the
carve-out is not absorbed into `conditions`; the full text is recorded verbatim in
`annotator_notes`, matching `C14-01`'s and `E01-01`'s treatment exactly.

**The underlying principle, stated so the next instance is decided by citation rather than
re-litigated: this was never about the word "unless."** It is about a **semantic category** — a
carve-out that narrows or removes an otherwise-stated duty under a stated circumstance — which
`packages/ir-spec/SPEC.md` §6's frozen no-exception-construct decision makes unrepresentable in
IR v1 regardless of which English marker introduces it.

**The test IS the rule; the list below is citation convenience, not a whitelist (made
explicit v0.41, after `except where` became a fifth confirmed marker at `C02-045` without
needing its own fresh re-litigation).** Membership in branch 3 is decided by branch 3's own
test — *does this phrase state a circumstance that removes or narrows the duty?* — applied to
whatever English marker introduces it. A marker matching the *shape* of an entry already on the
list below is not required for branch 3 to apply, and a marker's mere absence from the list is
not grounds to re-derive the test from scratch or to demand a fresh reviewer-ruled instance
before applying it — that demand was reasonable exactly once, to confirm the test actually
holds in practice beyond `unless` (§20.4/`C10-016`), and the confirmation generalizes. The list
exists so a future annotator recognizes the pattern quickly by example, not so every new
preposition needs to join it by ceremony. A small, non-exhaustive set of markers known to carry
this class, named here for quick recognition rather than as an exhaustive test: **`unless`,
`except to the extent`, `save where`, `other than in cases where`, `except where`** (the fifth,
confirmed at `C02-045`: *"Except where AMAG is required by Applicable Law to account for any
VAT..., Antares shall be solely responsible for..."* — narrows Antares's payment duty under the
stated AMAG-accounts-for-it-instead circumstance, the identical shape as the other four). The
`except that / as / for / to the extent` row in the table above is already a
measured pool pattern at 7.7% (119 segments) — this ruling is what confirms its branch-3
disposition; `save where` and `other than in cases where` are not yet measured in this corpus
and are recorded by citation only, the same posture §4.3.2 and §3.2.1 took at their own
precedent-setting instances.

**Note on the tag name, since §8.2's own "Rule" paragraph is stale and this is not the place to
silently edit it.** §8.2 still literally reads `known_gaps gains "unless_unsupported"`. That was
superseded by the tag rename already approved at the original consolidation pass (2026-08-22,
§20.4 decision 5 — *"the class is semantic, not lexical"* — `E01-01` and `C14-01` re-stamped to
`exception_unsupported` at the time). §8.2's prose was never updated to match its own approved
rename. `exception_unsupported` is the tag in actual use — by both locked items and by
`evals/harness/report.py`'s `GAP_DIRECTION` map — and is the one this section uses throughout.
Left as a note here rather than an edit to §8.2's original text, per this document's own
corrections-are-new-text discipline.

### 3.8.3 Belt-and-suspenders redundant condition restatements (v0.41 — REVIEWER-RULED)

**A different shape from both §3.8.2 rules, and from §4.3.1's restatement rule.** §3.8.2 Rule B
splits **adjacent, distinct** circumstances into separate entries; §4.3.1 handles a whole
**obligation** stated twice in one segment. Neither covers a single condition — one real-world
circumstance — stated **twice, non-adjacently**, sandwiching the obligation's verb and object,
common in drafting that tracks a statutory formula and then adds a belt-and-suspenders echo.

**Motivating case** — `C06-016`: *"the designee...shall be required, **if requested by the
applicable counterparty**, to provide adequate assurance of future performance with respect to
such Lease or Contract **if the applicable counterparty so requests**;"* Both bracketed phrases
state the identical triggering fact (the counterparty's request); the second is an anaphoric
echo of the first ("so requests" refers back to the same request already named), not an
independent circumstance the removal test (§3.8.2) would find non-redundant if deleted only
once — deleting *either* phrase still leaves the condition stated once, whereas deleting a
genuine §3.8.2 Rule B pair (`C11-094`'s two distinct circumstances) removes information both
times.

**Applicability gate, checked before any tiebreak is needed.** This section fires **only** when
every candidate occurrence states the identical real-world circumstance with **no
informational difference** between them — the removal test (§3.8.2) applied to *each*
occurrence independently must find the *other(s)* redundant, not merely similar. If one
occurrence carries any detail the other lacks (a sub-condition, a qualifier, a deadline, a
narrower scope), they are **not** a belt-and-suspenders pair: this section does not apply, and
the two are either two genuine §3.8.2 Rule B entries (if both independently gate the duty) or
the single more-detailed phrasing is simply the one true `conditions` entry, with the vaguer
phrasing noted in `annotator_notes` as imprecise but not entered as a second condition. This
gate is what makes the tiebreak below purely mechanical: **because §3.8.3 only ever compares
occurrences that are informationally identical by its own admission criterion, "which one is
more complete" can never be a live question inside this section** — there is nothing left to
compare on except position.

**Rule — collapses to one `conditions` entry, chosen by a hard positional tiebreak.** Quote the
occurrence **structurally closest to the clause's own governing modal verb** (the verb recorded
in `modality`, §3.2) — measured as the shorter character distance from the end of the modal
phrase to the start of each candidate occurrence in `span_text`. This is not a default or a
usual case: it is the rule, unconditionally, for every occurrence count. With three or more
redundant occurrences, the same measurement picks one winner (the modal-nearest) and every
other occurrence — not just the runner-up — goes into `conditions_accept_set[i]` together. In
the vanishingly unlikely case of an exact tie in modal-distance, the occurrence with the
earlier character offset in `span_text` wins, so the outcome is always deterministic and never
depends on annotator taste. Apply §3.8.2 Rule A's quote-extent convention to whichever
occurrence wins. Record every non-winning occurrence verbatim in `annotator_notes`, exactly as
§4.3.1 records a restated obligation's redundant span — **not scored, not silently dropped.**
Do not record more than one occurrence as a `conditions` entry: they are one real-world
circumstance, and recording more than one would assert an implicit-AND over a single fact
rather than count multiple circumstances, which is what count-sensitive clause 7 exists to
measure.

**Why modal-distance and not, say, clause order or length.** Clause order was considered and
rejected: in `C06-016` the modal-nearest occurrence also happens to be the earlier one, but
nothing guarantees that in general (a differently-ordered sentence could easily place the
modal-nearest phrase second). Length/"completeness" was considered and rejected for the reason
the applicability gate above states directly: within this section's own scope, every candidate
is informationally identical, so length differences (if any) reflect phrasing verbosity, not
information content, and are not a principled basis for a choice that must be reproducible by a
different annotator reading the same sentence cold. Modal-distance is chosen because it is the
one property that is always computable directly from the text, never requires a semantic
judgment, and tracks the linguistically natural reading — the occurrence syntactically bound to
the operative clause is the "real" one; a trailing echo is definitionally the more detachable of
the two.

**The scoring risk this creates, and the mechanism that closes it.** A real extraction may
reasonably quote *either* phrasing — nothing about the sentence privileges one occurrence over
the other from a model's perspective, only gold's own quote-extent convention (§3.8.2 Rule A)
does. Scoring gold's chosen phrasing by exact string match alone would fail a correct
extraction that happened to quote the other occurrence, a clause-7 miscount caused by the
document's own redundant drafting rather than by extraction quality — the identical shape of
risk §3.4/§3.6/§3.5.1's accept-sets exist to close for `action`/`object_class`/`obligor`, not
previously needed for `conditions` because no locked item before this one carried a redundant
restatement.

**Mechanism — a new, optional `conditions_accept_set` field, not a rewrite of `conditions`
itself.** `conditions` stays exactly what §3.8 already defines: an ordered list of canonical
verbatim strings, order-insensitive/count-sensitive at scoring. `conditions_accept_set` is a
parallel list of the same length and order; `conditions_accept_set[i]` holds zero or more
**additional** verbatim substrings of `span_text` that are accepted as equivalent phrasings of
`conditions[i]`'s same real-world circumstance — here, `conditions_accept_set[0] = ["the
applicable counterparty so requests"]`. Absent or empty for every existing locked item and for
the overwhelming majority of future ones; this is not a general paraphrase-tolerance mechanism
and must not be used to admit a phrasing that states a genuinely different circumstance —
that stays a straightforward mismatch. **Scoring (clause 7):** a predicted condition string
matches gold entry `i` if it equals (whitespace-normalized) either `conditions[i]` or any
member of `conditions_accept_set[i]`; the **count** that clause 7 checks is still `len(conditions)`,
unaffected by how many accepted phrasings any entry carries.

**Why not treat this as already covered by §3.8.2 Rule A's quote-extent flexibility.** Rule A
governs where a *single* quote's boundary starts (trimming a leading `further`/`and`); it says
nothing about choosing between two textually distinct substrings elsewhere in the sentence that
express the same fact. The two phrases here differ in more than boundary — different words
entirely (`"if requested by..."` vs `"...so requests"`) — so Rule A's mechanism does not reach
this case, and a purpose-built accept-set is the narrower, more honest fix.

**Forward-only.** Governs items annotated from batch 3 onward; restamps no locked item
(none of the 18 carries this shape); no cassette goes stale (an annotation-schema addition,
not a prompt or model change). `§1`'s field table gains `conditions_accept_set` as an
optional field pointing here.

### 3.8.4 Context-setting anaphora is not an independent condition (v0.41 — REVIEWER-RULED)

**A third shape, distinct from both §3.8.2 Rule B (two genuinely independent conditions) and
§3.8.3 (the identical fact stated twice as two condition-shaped phrases).** Here, a phrase
that *looks* like a condition and passes §3.8.2's bare removal test in isolation is actually
parasitic on scope **already fixed elsewhere in the segment by non-condition-shaped text** — a
list-item heading, a topic label, or the sentence's own position inside a labeled block —
rather than adding a genuinely new, independently variable restriction.

**Motivating case** — `C13-01`'s span (`C13-017`): *"**In such a situation**, DD will make
available to MBRK, **upon request**, all of DD's pertinent records on MOXATAG."* — embedded
directly after item `(h) handling all voluntary recalls and market withdrawals of MOXATAG` in
an enumerated list (§2.6). The bare removal test says both bracketed phrases are conditions:
deleting either changes when the duty applies. But `"In such a situation"` restates a scope
item (h)'s own heading **already fixes** for this whole block — delete the phrase and leave the
sentence positioned right after that heading, and a reader still understands the duty as
scoped to recall-handling, because the heading did that work already. `"upon request"` has no
such anchor anywhere else in the segment; it is the only place anything makes DD's
record-sharing conditional on MBRK actually asking.

**Rule — the two-anchor removal test.** Before entering a candidate phrase as its own
`conditions` entry, check whether **some other part of the same segment — not itself a
condition-shaped phrase — already, independently states the identical restriction**
(a heading, a preceding topic sentence, an enumeration label the clause sits under). If yes,
the candidate is anaphoric scene-setting: it is **not** entered as a separate `conditions`
entry, and is recorded in `annotator_notes` instead, same "not scored, not silently dropped"
treatment §3.8.3 and §4.3.1 already give their own non-scored redundant text. If no such
independent anchor exists anywhere in the segment, the candidate is a genuine condition under
the ordinary §3.8.2 test.

**Why this is not §3.8.3.** §3.8.3 fires when **two condition-shaped phrases** state the
identical fact — both readable as candidate `conditions` entries on their own. Here the anchor
(item (h)'s heading) is not condition-shaped at all — it is a list-item label, never itself a
candidate for `conditions` — so §3.8.3's applicability gate (informationally identical
*condition* occurrences) does not fire, and this needed its own test.

**Why this matters for scoring, not just tidiness.** Double-counting a restated-by-position
phrase as an independent condition would make count-sensitive clause 7 fail a correct
extraction that reasonably reads the duty as having one real gate (`"upon request"`), the
identical shape of extraction-quality-unrelated miscount §3.8.3 exists to prevent — reached
here through redundant *structure* rather than redundant *phrasing*.

**Expected to recur wherever §2.6 applies** — an obligation embedded inside a labeled
enumeration item is exactly the shape where a sentence echoes its own heading's scope in
passing. No corpus-wide frequency measured; decided by citation going forward.

### 3.9 `underspecified`

`true` when **any** of:

1. **a party reference `symbols.resolve_party()` cannot match.** This includes `ABSENT`
   (§3.5); any collective or distributive reference (§3.5.1 step 1 branch 2); any relational
   reference (`the other party`, `such parties`); any role description (*"the executor,
   administrator, or personal representative"*); and any alias absent from the scoring
   registry (§21).
2. a `DateRef` that cannot resolve;
3. a `TriggerRef` that cannot resolve;
4. a business-day (`bd`) duration.

**`temporal: null` is never a trigger** (§15.3) — `typecheck.py` returns `None` for an absent
temporal without appending to `missing_fields`, deliberately and by documented design.

**Trigger 1 restates the code; it does not add a rule (v0.28).** `typecheck.py` computes
`underspecified = bool(missing_fields)`, and `_resolve_party` appends whenever
`resolve_party()` returns `None` — not when a party is `ABSENT`. `ABSENT` is one input that
yields `None` among many: **437 of 1,547 pool segments (28.2%) carry a party reference that can
never resolve.** Because §3.9 is scored (§5 clause 8), gold must predict what a correct
extraction actually produces; where this section and `typecheck.py` disagree, **the code is
authoritative and this section is the defect.** The pre-v0.28 wording made `C14-01` and
`C14-02` guaranteed clause-8 failures and left 11 further items undecidable.

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

**Byte-identical gold spans (v0.36 — REVIEWER-RULED).** Two or more gold items in the same
segment occasionally carry **byte-identical span offsets** — the case §4.3.2's flow-down split
produces when the object clause trails and is shared by both coordinated verbs, so neither
item's minimal contiguous span can be made shorter than the other's without either breaking
§3.1 contiguity or dropping a field from its own span. Where this happens, **IoU cannot
discriminate between the tied items for any candidate prediction that reaches the shared span**
— every candidate scores the identical IoU against both, so plain descending-IoU pairing is
silently implementation-order-dependent rather than a real decision.

**Rule: break the tie by content, not geometry.** Match the candidate's `action` against each
tied item's `action_accept_set`:

- Falls in exactly **one** tied item's accept-set → pair there.
- Falls in **more than one**, or in **none** → fall through to a final deterministic tie-break
  by **ascending `item_id`** (lowest first), so the outcome never depends on iteration order.

**Scope: byte-identical spans only.** This does **not** touch the ordinary greedy-descending-IoU
path for different-offset spans, including nested ones — `C14-076`'s shared-subject-split spans
(§8.3.1) already resolve correctly under plain IoU, because an exact match to the shorter span
always scores strictly higher than a match to the longer, containing one. The new rule fires only
where geometry is genuinely uninformative, which by construction is only the identical-span case.

**Why action, not some other field.** `action` is already the field §5's predicate checks by
accept-set membership rather than exact match (§3.4), which is exactly the discrimination this
tie-break needs — the two tied items are designed to differ in which verb's accept-set covers
them (self-performance vs. third-party-compliance, §4.3.2), so the field that already carries
that distinction for scoring is the natural tie-break key, not a new one invented for this case.

**Deterministic in every case, including the realistic single-candidate one.** If the model
emits one merged candidate for the whole sentence (plausible, since this is a hard case for
extraction too), it pairs to whichever tied item's accept-set contains its action; the sibling
item correctly scores `MISSED` — the honest signal that only one of the two independently-
breachable duties was captured, not a scoring artifact.

### 4.3 Multi-obligation sentences (v0.28 — merged with §8.3's test)

*"Vendor shall notify Customer and shall deliver a report within 5 days."*

**Rule: the test is whether the verbs are aspects of one indivisible performance, or
separate performances.** Object identity is *evidence*, never the criterion.

- **Separate performances** → **two items.** §3.1's span rule applies to each; where the
  second span cannot carry the shared subject, §8.3.1 governs.
- **One indivisible performance** → **one item**, primary verb in `action`, the full verb
  phrase verbatim in `annotator_notes`, and §8.3's `compound_action` tag.

**Worked boundary cases:**

| sentence | verdict | why |
| :--- | :--- | :--- |
| *"shall deliver the report and the invoice"* | **one item** | one verb, compound object; both tests agree |
| *"shall promptly notify and remedy any breach"* | **two items** | shared object but **independent** performances — the case v0.1's object test decided wrongly |
| *"provide to AT&T, and keep current, an escalation document"* (`C03-02`) | **one item** | two verbs, one indivisible performance |
| *"shall deduct such taxes … and shall promptly furnish … tax receipts"* (`C14-01`/`C14-02`) | **two items** | separate objects **and** separate performances |

**Why this replaced the v0.1 object test (v0.28).** v0.1 said *"split when the sentence has
two distinct governing verbs with separately identifiable objects"*; §8.3 (v0.15,
reviewer-confirmed) said the discriminating test is *"not 'one object or two' on its own"* and
gave `notify and remedy any breach` as the counter-example. Both were in force and gave
opposite answers on that sentence. The conflict was latent, not academic: **29 pool segments
(1.9%), 12 documents** carry one modal governing two coordinated bare verbs over a shared
object — `manufacture and test all Devices`, `obtain and maintain all necessary licenses`,
`label and package the Products` — where the two tests diverge. Splitting an indivisible
performance manufactures two items that are not separable, the same over-mechanical failure
§17.2 declined for `AND`/`OR` inside one condition.

A gold item that ends up unaligned because the model emitted one merged span is scored
`MISSED`. That is a real recall finding, not an annotation error.

### 4.3.1 Restated obligations within one segment (v0.28 — F9)

A segment may state the same duty twice, typically flagged `For the avoidance of doubt`,
`For clarity`, `it being understood`, or `without limiting the foregoing`.

**Step 1 — is it actually a restatement?** It is one **only if every scored field (§5 clauses
1–8) would be identical**. If **any** differs — a different trigger, a different object
restriction, a different modality — the two clauses are **distinct obligations** and are
annotated as two items under §4.3's ordinary treatment. **The marker word is not the test.**

*Demonstrated on the segment that surfaced this rule.* Probe `C06-113` carries two
`Agent may abandon` clauses, the second flagged *"For the avoidance of doubt"* — and they are
**not** restatements: the triggers differ (`the conclusion of the Sale or the Designation Rights
Period` against `the Sale Termination Date or termination of the Designation Rights Period`) and
so do the objects (`any FF&E **not sold in the Sale**` against `any FF&E **located at a Store
or, Distribution Center**…`). Neither contains the other, so an instruction to "annotate the
more complete one" would have had **no referent** — the same defect §8.4.1 found in §8.4's
*"first-named party"* when the subject was collective. `C06-113` resolves to three distinct
items and never reaches step 2.

**Step 2 — if it is a genuine restatement:**

- Annotate **one** item, on the span stating the obligation most completely.
- Mark the redundant span **`NOT_ANNOTATABLE` (§4.4)**, so a prediction aligning to it counts as
  **neither a correct item nor a false positive**.
- Record it verbatim, with offsets, in `annotator_notes`.

**No new tag** — §4.4 already carries exactly this semantics, and extending its scope is cheaper
than a parallel mechanism.

**Why not the alternatives.** *Annotate both* → a model sensibly emitting one candidate per duty
scores a `MISSED`, a recall loss caused by the contract's redundancy and attributed to
extraction. *Annotate one and drop the other* → a model emitting the other scores `UNEXPECTED`,
a false positive for correctly reading the document. Only §4.4's treatment is neutral in both
directions.

**Measured:** `for the avoidance of doubt` 23 segments (1.5%), `for clarity`/`to be clear` 16
(1.0%), `it being understood/agreed` 8 (0.5%), `without limiting the foregoing` 15 (1.0%) —
**62 segments (4.0%) across 16 of 28 documents.** That is the **marker** population and is an
**upper bound** on step 2's class, not its size: step 1 reclassifies an unknown share as distinct
obligations, as it does for `C06-113`. The surviving share has **not** been measured.

**STATUS OF STEP 2: UNTESTED — no instance has arisen in any material seen so far**, the same
footing §8.3's split branch carried until `C14-076` arrived. Step 1 is demonstrated; step 2 is
logically sound and unexercised, and must not borrow confidence from step 1.

### 4.3.2 Self-performance vs. third-party-compliance flow-down splits (v0.35 — REVIEWER-RULED)

**Motivating case** — `C04-139`: *"Bellicum shall use, and will cause its Subcontractors and
Licensees to use, Miltenyi Products in accordance with all Applicable Laws and all requirements
of Regulatory Authorities applicable to such use."*

**A third shape, distinct from both existing §4.3 worked examples.** *"Provide... and keep
current"* is one continuing duty over one deliverable; *"notify and remedy any breach"* is two
acts by the same party on its own initiative. This sentence is neither: one verb governs the
obligor's **own conduct**, the other governs the obligor's duty to **bind or control a third
party's conduct** — a flow-down clause of the common commercial shape *"X shall do Y, and shall
cause its Subcontractors/Affiliates/Licensees to do Y."*

**Rule: split into two items.** The discriminating test is **locus of accountability, not object
identity**: a duty to perform an act oneself and a duty to ensure a third party performs
(materially) the same act are **independently breachable** — the obligor can satisfy one while
failing the other (Bellicum can itself comply with law while failing to bind or police its
Subcontractors and Licensees, or vice versa) — and a breach of each is attributed differently:
the first is the obligor's own non-performance, the second is a failure of oversight over a party
who is not bound by this obligation at all. That is a stronger form of the independence §4.3
already requires for a split, not a weaker one — the two performances do not even share an actor.

**Item 1 — self-performance.** `action` holds the verb governing the obligor's own conduct
(`USE`, in the motivating case). `obligor` is the named party; `obligee` follows §3.5 normally
(here `ABSENT` — no dative names a beneficiary in the span).

**Item 2 — third-party-compliance.** `action` holds the taxonomy verb nearest to "cause/bind a
third party to perform" — apply §3.4's accept-set discipline rather than hard-coding one verb,
since "cause X to do Y" has no single exact taxonomy match. `obligor` remains the **named party
with the flow-down duty** (Bellicum), never the third party — the third party is not bound by
this obligation at all, only referenced as the target of the obligor's own oversight duty.

**Why this is not §8.3's compound-action case.** §8.3 keeps one item when two verbs are aspects
of one indivisible performance by the **same actor**. Here the two verbs' underlying performers
differ (the obligor itself, versus the obligor's discharge of an oversight duty over a distinct
third party) even though both are grammatically governed by the obligor as sentence subject —
the same distinction that makes a mutual obligation (§8.4) two duties rather than one, applied to
a different pair of roles.

**This pattern is expected to recur.** Flow-down compliance clauses (a party's own performance
plus a parallel duty to bind subcontractors, affiliates, or licensees to the same standard) are
common commercial drafting and are not particular to this document. No corpus-wide frequency has
been measured; recorded as a rule now so the next instance is decided by citation rather than
re-litigated.

**Span mechanics are a separate question, not settled by this rule.** Whether the two items'
spans can be made non-colliding under §3.1/§4.1 when the object clause trails and is shared by
both coordinated verbs (as in the motivating case) is addressed on its own, per-instance basis —
see the adjudication for `C04-139` itself for the shape this took there.

**`object_class` naming convention (v0.37 — RECOMMENDED, not mandatory).** Anchor the
self-performance item's label with a `self_` prefix and the third-party-compliance item's label
with a `third_party_` prefix, over the same compliance/action root — `self_compliant_use` /
`third_party_compliant_use` for the motivating case, rather than two labels with no visible
shared root. This makes the split's own self/third-party structure legible in the accept-set
vocabulary itself, not only in `annotator_notes`, and gives a future annotator hitting another
flow-down clause an obvious pattern to reach for rather than inventing an unrelated pair of
labels each time. Not mandatory because `object_class` accept-sets are always author-time
judgment calls (§3.6); recorded as a recommendation precisely because `C04-139` is this rule's
precedent-setting instance and the naming choice made here is the one future batches will see
first.

**ROOT CONSTRAINT (v0.48 — REVIEWER-RULED, §10.1 F3). The shared root must be chosen so that
neither half's label restates its own item's `action`.** The prefixes are unchanged and stay
recommended; what is constrained is the root.

**Why this rule yielded rather than §3.6.1.** `C04-139`'s own pair was authored as
`self_compliant_use` / `third_party_compliant_use`, and at v0.44 §3.6.1 forbade a label carrying
material already scored by clause 2. `use` **is** `USE`, so the self-performance half violated it
— and the third-party half did not, because `use` is not `ensure`. The collision therefore lands
on **exactly one half of a split pair**: whichever half's own action verb happens to equal the
root. Both rules were live and the item cited both.

**It was ruled as a genuine conflict of rules, and §3.6.1 does not yield.** §3.6.1 is a
categorical correction of an **instrument** defect — a label restating the action makes clauses 2
and 5 co-vary, so one judgment is scored twice — and it is retroactive on that ground. This
section's naming convention is an **author-time recommendation** by its own text above. A
recommendation gives way to a categorical rule; the reverse would put a named exception into the
one rule whose whole force is that it has none, and §3.4's history with exactly that move is on
record. Narrowing §3.6.1 to exempt a §4.3.2 root would not remove the double-scoring, it would
bless it.

**What was NOT ruled, stated so the constraint is not read as wider than it is.** Nothing here
requires the root to avoid the `ACTIONS` list as a *string* — §3.6.1's test is content-relative to
**this item's own field values**, never a blacklist, and its carve-out 1 (a token that appears in
the span as part of the object's own name) applies here unchanged. A pair whose natural root
happens to be a taxonomy verb neither half holds as its `action` is unaffected.

**The two corrected instances (v0.48).**

| item | field | was | now |
| :--- | :--- | :--- | :--- |
| `C04-04` | slot | `self_compliant_use` | `self_regulatory_compliance` |
| `C04-05` | slot | `third_party_compliant_use` | `third_party_regulatory_compliance` |

`regulatory_compliance` was chosen because it was **already an accept-set member of both items**
before this ruling, so the root is defensible **from the span alone** and was authored before any
prediction for `C04-139` could exist — §3.4's justification test, satisfied by construction rather
than by argument. Both new slot values are added to their own accept-sets (the slot ∈ accept-set
invariant holds 32/32 across the locked set), a **monotone widening** permitted by §3.6.1's
widening-only set rule; **no member is removed from either set.**

**`C04-05`'s change is driven by THIS section, not by §3.6.1, and is recorded that way so it is
not later re-read as a second §3.6.1 violation.** Its old slot was already §3.6.1-clean. It moves
only to keep the pair on a shared root once `C04-04` moved — which is this convention's entire
purpose, and the distinction §9.5 of `OBJECT_CLASS_INVESTIGATION.md` measured head-only matching
would destroy.

**A constraint on label choice, stated as a real cost rather than a free fix.** On `C04-139` every
*natural* root collides with one half: `use` restates `C04-04`'s `action`, and `compliance` shares
a root with `COMPLY`, which sits in `C04-04`'s `action_accept_set`. The chosen root is clean under
§3.6.1 **as written**, which tests the `action` **slot value** only — but that it needed checking
at all is the point, and the accept-set question it raises is filed as **§10.1 F12** rather than
decided here.

**Measured, because the honest version of that cost is smaller than it first looked.** The old
label `self_compliant_use` restated `COMPLY` too — via `compliant` — so on the accept-set axis the
item's exposure is **1 before this ruling and 1 after**. The new root **inherits** an existing
hazard rather than introducing one, which is why F3 was ruled without waiting on F12. Stated
plainly because the first measurement of this said *zero before, one after*, which would have made
the new root look worse than the old one; that reading came from a stemmer that could not see
`COMPLY`→`compliance`, and is corrected in §3.6.1's own note.

**One live instance, and the class is nonetheless real.** A validated screen over all 32 locked
items (below) finds `C04-04` to be the only §3.6.1 slot violation in the set, so this is a
one-member class. It is still filed as a rule rather than a bad label because **any future §4.3.2
split whose root is one half's own taxonomy verb reproduces it** — and the set's *other* §4.3.2
application nearly did. `C22-02` is this rule's second live instance (its own notes say so); it
reduces to a single item because §3.2.1 excludes the self-performance half, and `GRANT` **is** a
taxonomy verb, so had that half survived, `self_…_grant` / `third_party_…_grant` would have
collided identically.

**A finding about this convention's own standing, recorded because it is what made the ruling
cheap.** `C22-02` was annotated at `guideline_version v0.38` — *after* this convention was written
at v0.37 — carries `object_class = trademark_license_grant` with **no prefix, no shared root, and
no reference to this convention at all**, and is `reviewer_status: APPROVED`. The one other live
application of §4.3.2 declined the naming convention outright and was approved. That is direct
evidence the convention is optional in practice and not merely on paper, which is what a ruling
making it yield requires.

**Two propagated misstatements, corrected here rather than silently.** §10.1.1 (v0.45) and
`OBJECT_CLASS_INVESTIGATION.md` §11 each state that this section ***requires*** the prefixes over
a shared root. It does not, and never did — the heading above reads *RECOMMENDED, not mandatory*
and its closing sentence says so again. The conflict was real, but it was between §3.6.1 and one
**root choice**, not between two mandates.

### 4.4 `NOT_ANNOTATABLE`
A clause inside an otherwise-good segment that the exclusion rules of §2 would reject on
its own is labelled `NOT_ANNOTATABLE`. A prediction aligning to it counts as **neither**
a correct item **nor** a false positive.

**Scope widened at v0.28 (F9).** This label also covers a clause excluded **not** because §2
would reject it standalone, but because **another span in the same segment already carries the
same obligation** (§4.3.1 step 2). A restatement is a well-formed obligation and §2 would not
reject it on its own, so the original wording did not reach it.

---

## 5. The scoring predicate

An aligned item is `FULLY_CORRECT` iff **all** of the following hold — this is
**conjunctive**, not weighted:

1. `modality` exact
2. `action` ∈ `action_accept_set`
3. `obligor` matches (see the party-comparison rule below)
4. `obligee` matches (see the party-comparison rule below)
5. `object_class` ∈ `object_class_accept_set`, **compared with grammatical number
   normalized on both sides** (v0.33 — see the number rule below)
6. `temporal` form matches, **and** amount/unit/date constituents match exactly
7. `conditions` match as an order-insensitive, count-sensitive set
8. `underspecified` matches

**The party-comparison rule for clauses 3 and 4 (v0.28).**

- Pipeline emits a **`ResolvedParty`** → the clause passes iff gold's verbatim alias resolves,
  through the registry's own `canonical_name`/`aliases` matching, to the **same `party_id`**.
- Pipeline emits an **`UnresolvedParty`** → whitespace-normalized string equality against
  gold's alias.
- `ABSENT` matches `ABSENT`.

**Why not compare against the alias the model itself quoted.** It is not available:
`ast.ResolvedParty` carries only `(party_id, canonical_name)` and discards the span alias, and
`PipelineResult` retains the `LLMCandidate` **only for rejected and quarantined candidates** —
a successfully typechecked obligation, the only kind that can score `FULLY_CORRECT`, carries
neither. Three further reasons, each independently sufficient: clause 3 measures *party
identity*, not surface form, and the registry's `aliases` array is that accept-set already
authored (the same principle §3.4/§3.6 apply to `action`/`object_class`); which of two in-span
mentions a model quotes varies run to run, so path-matching would put §6's sampling
non-determinism inside a scored clause; and registry matching is **monotone** — adding an alias
can only turn a fail into a pass — while path-matching moves with model behaviour.

**The number rule for clause 5 (v0.33).** Grammatical number is normalized on **both** sides
before the membership test: `taxes` matches an accept-set holding `tax`, `retained_samples`
matches `retained_sample`, `agreement_provisions` matches `agreement_provision`.

**Why this is a comparison rule and not an accept-set widening.** It widens no set and is
fitted to no prediction — it applies uniformly to every item, past and future, and **deletes a
distinction neither side was ever asked to make.** `prompts/extraction/v3.yaml` asks only for
*"a short lowercase snake_case label"* and one of its own three worked examples
(`deliverables`) is plural; §3.6 fixes no convention either. So which number an item's
accept-set happens to spell was arbitrary, and clause 5 was enforcing it. §3.4's freeze rule is
untouched: nothing is widened after seeing a prediction.

**Measured before the rule was written** (§8.6's discipline). Across the 37 aligned
`object_class` comparisons in the first scoring run: **25 exact, 7 number-only mismatches, 5
genuinely different labels.** Number-only mismatches hit 3 of the 18 locked items — `C02-01`,
`C14-01`, `E01-01` — and in all three the model follows the **document's own** number (*"such
taxes"*, *"retained repository samples"*, *"No provisions of this Agreement"*) while gold
singularized. **Zero of the 18 accept-sets hedge by carrying both numbers**, so the items that
pass do so only because gold happened to author the same number — `required_quantities` and
`third_party_royalties` both pass as plurals. It was a coin flip, not a measurement.

**Deliberately a narrow number-normaliser, NOT a stemmer.** `-s`, `-es` after a sibilant,
`-ies`→`-y`, and stop. A Porter-class stemmer would conflate `retention`/`retain` and
`provisions`/`provide`, which would make clause 5 nearly vacuous — the opposite failure, and a
worse one, since clause 5 is the only check on an open vocabulary. The normaliser is pinned by
a known-answer test table (Standing Principle 7), including `taxes`→`tax`, which the first
draft of this very analysis got **wrong** by stripping only a trailing `s`.

**Scope: clause 5 only.** Clause 7 (`conditions`) is NOT number-normalized — §3.8 requires
verbatim quotes and normalizing a quotation is a different act from normalizing a label.

**Named, accepted asymmetry:** a *resolved* party is scored leniently (any registered alias
passes) and an *unresolved* one strictly (exact string). This tracks a real epistemic
difference rather than an arbitrary one — a resolved party **is known** to be one entity, while
two unresolved strings are **not known** to corefer, and asserting they do is the inference
§3.5 forbids. Same UNRESOLVED-is-honestly-not-yet-known posture the IR itself takes.

`missing_fields` is **reported but excluded** from the predicate.

Other outcomes: `PARTIAL` (aligned, predicate fails), `MISSED` (no aligned prediction),
`UNEXPECTED` (prediction aligned to no gold item and not `NOT_ANNOTATABLE`).

### 5.1 §5 is the PIPELINE's predicate. Comparing two annotators uses a different one — `A` (v0.45 — REVIEWER-RULED)

**The question, asked and answered.** `RESULTS.md`'s REDESIGN response left one architectural
question open and ordered it ahead of everything else: *is §5 one predicate serving both
pipeline-vs-gold scoring and gold-vs-cold annotator comparison, or two predicates that happen
to share eight clauses?* **Ruled: two predicates, sharing eight clause definitions and §4's
alignment, differing in three comparison rules.** §5 above is **unchanged** and is the pipeline's
predicate. The annotator-comparison predicate is named `A` and is defined here.

**The decisive argument is structural, not a preference.** §5 clause 2 tests
`prediction ∈ gold's accept_set` — **one-sided by construction**. One-sidedness is *coherent*
against a predictor bound by a closed grammar: `grammar/obligation.lark`'s `ACTION` terminal is a
closed set of 34 verbs, so an out-of-vocabulary emission is impossible and the accept-set can do
its real job of absorbing genuine sentence ambiguity. It is *incoherent* against a peer
annotator, for whom an out-of-vocabulary value is **not a competing reading of the sentence but a
malformed annotation**. §7 already half-conceded this in its own wording — *"a **prediction**
inside the accept-set is not a disagreement"* — while describing two annotators.

**Measured, not argued: this is 5 of the 14 disagreements the 2026-08-29 run counted.** The cold
annotator wrote an off-taxonomy `action` slot on exactly five matched items — `C02-03` `INVOICE`,
`C10-02` `INSURE`, `C14-04` `COMPLETE`, `C17-01` `PREVENT`, `C17-02` `OBTAIN` — and those are
**exactly** the five items `comparison.json` marks `2_action`, a 5-of-5 correspondence. Gold
carries **zero** off-taxonomy values across all 32 items. Cold used `action_not_in_taxonomy`
**0 times in 41 items**; gold used it twice, on two of those same five. So on `C10-02` and
`C14-04` **both annotators saw the same thing** — a real verb outside the taxonomy — and encoded
it differently: gold as *(nearest taxonomy verb + tag)* per §8.8, cold as *(true verb, no tag)*.
K saw only the clause-2 half, because `known_gaps` is not one of its clauses. Two of the fourteen
(`C02-03`, `C17-02`) fail on **nothing else at all**.

**The three differences, each forced by something measured.**

**A1 — a conformance gate, applied before comparison, and it is SLOT-ONLY.** A closed-vocabulary
field whose own value falls outside its vocabulary makes the item `NON_CONFORMING`: it leaves
**both** the numerator and the denominator of K and is reported as its own figure. It is **never**
counted as a disagreement. The closed vocabularies are `modality` (4), `action` (34, §8.8),
`temporal.form` (5) and `known_gaps` (§8's tag set).

> **The gate does not reach accept-set members, and that boundary was PROVEN by execution rather
> than argued** (Standing Principle 7). An off-vocabulary *accept-set member* is **inert**: it can
> only ever be compared against a slot value, every legal slot value is in the vocabulary, so it
> can never produce a match in either direction. Measured — stripping all **52** of cold's
> off-taxonomy accept-set members from both sides changes **no clause outcome on any item**.
> Gating on them instead marks **27 of 32** items `NON_CONFORMING` and leaves K over **n=5**,
> which supports no inference whatever. **The instrument is destroyed by a gate one scope too
> wide, and the first draft of this rule had exactly that scope.**

**A2 — accept-set fields are compared symmetrically, by MUTUAL MEMBERSHIP.** Agreement iff gold's
slot ∈ the other's accept-set **or** the other's slot ∈ gold's accept-set — precisely §5's own
test run in both directions and disjoined, not a new rule. Applies to clause 2 (`action`), clause
3 (`obligor`, via `obligor_accept_set`), clause 5 (`object_class`, with §5's number rule) and
clause 7 (via §3.8.3's `conditions_accept_set`).

> **The looser alternative is REJECTED at zero measured cost.** Non-empty *intersection* of the
> two accept-sets — the form `RESULTS.md`'s sensitivity A measured — gives the **identical**
> result under the A1 gate (`K = 7/27` either way), because the only item separating them
> (`C02-03`: both sets hold `REPORT` while neither slot is in the other's set) is gated out for an
> off-taxonomy slot. Intersection therefore buys nothing measurable and would "agree" an item
> whose slot value the field cannot hold. The tighter rule is taken on principle, and the fact
> that it costs nothing is stated so nobody re-opens it expecting a different number.

**A3 — parties are compared as strings; there is no registry branch.** §5's lenient identity
branch fires when the *pipeline* resolved a party; a cold annotation carries an alias and nothing
else, so that branch is not merely unused but **unavailable**. Resolving both annotators' aliases
through the document registry was considered and is **deferred, not adopted**, on two measured
grounds: it changes nothing (of 31 matched pairs, 16 gold obligors and 10 gold obligees resolve,
and **zero** disagreements flip), and registries exist for only **10 of the 15** documents, so
adopting it would make the instrument's strictness vary by document — a silent coverage hazard
bought for an effect measured at zero. Revisit when a cold run puts a genuine
same-party/different-alias pair in front of it.

**Clause 9 — `known_gaps` belongs to `A`, and is still reported separately.** This is the answer
to REDESIGN item 0 stated in its proper place: `known_gaps` is an annotator judgment, so it is
`A`'s ninth clause and has no business in §5, which scores a pipeline that structurally cannot
emit the field. It is nonetheless reported as its own instrument — `G`/`G_swing`,
`GAP_AGREEMENT_DESIGN.md` — and is **never added to, averaged with, or folded into K**. Clauses
1–8 produce K; clause 9 produces G; conformance produces its own rate. **Three figures, always
published together, never combined.** Option (a)'s disqualification stands, and the ground the
design note gave for it — *"§5 is a gold-vs-prediction predicate… this alone settles it"* — is now
a **ruled** fact rather than the assumption it was when written. *(Recorded plainly because the
ordering was wrong: the design note pre-answered this question while `RESULTS.md` was saying it
"has never been asked and should be asked before either fix." The conclusion survives independent
re-derivation from clause 2; the ordering does not, and is logged rather than tidied away.)*

**Verdict bands are DERIVED at `A`'s own `n`, never transcribed.** A1's gate changes the
denominator, and reusing counts fixed for n=32 would silently change the band's evidential
strength. `PREREGISTRATION.md` §4's own method — preserve §7's Wilson₉₅ **lower** bound at each
trigger (0.0279 DIAGNOSE, 0.0807 REDESIGN) — is applied at whatever `n` survives the gate. The
derivation reproduces the published n=32 bands (DIAGNOSE ≥3, REDESIGN ≥6) exactly, which is the
known-answer check that makes it usable at any other `n`.

**The 2026-08-29 run, recomputed under `A`. The published verdict is NOT overturned.**

| | published (§5, one-sided) | under `A` |
| :--- | :--- | :--- |
| K | **14 / 32 = 43.8%**, Wilson₉₅ [28.2%, 60.7%] | **7 / 27 = 25.9%**, Wilson₉₅ [13.2%, 44.7%] |
| conformance failures | not measured | **5 / 32 = 15.6%** — all cold's, all `action` slots |
| bands at that `n` | DIAGNOSE ≥3 / REDESIGN ≥6 | DIAGNOSE ≥3 / REDESIGN ≥5 |
| **verdict** | **REDESIGN** | **REDESIGN** |
| G | 6 / 31 = 19.4% → REDESIGN | **4 / 26 = 15.4% → DIAGNOSE** |
| G_swing | 2 / 31 → BANDED | **1 / 26 → BANDED** |
| `D` band | 15 [15–17] | **14 [14–15]** |

**Read the K row precisely.** The instrument fix moves the number a long way and moves the
**decision** not at all. That is the outcome that makes the fix safe to adopt: it was ruled on
structural grounds before its effect on the verdict was known, and had it flipped the verdict
this section would say so.

**The G row is a substantive finding, not bookkeeping.** Both items `A` removes from G — `C10-02`
(swing) and `C14-04` (disjoint) — were removed for the **same** conformance failure, cold never
once using `action_not_in_taxonomy`. So part of G's own REDESIGN was the artifact A1 exists to
remove, and **`G_disjoint` falls to zero**: `GAP_AGREEMENT_DESIGN.md` §6's deferred *"can §8 tags
legitimately co-apply?"* question had exactly one motivating instance and it was a conformance
artifact. That question is not thereby answered — one instance disappearing is not evidence
either way — but its only evidence is gone, and the §8 tag-vocabulary review should be told so.

**Executable, and preserved.** `evals/harness/annotator_agreement.py`, with
`tests/evals/test_harness_annotator_agreement.py` reproducing the published run **item by item
and clause by clause** in a retained one-sided legacy mode. That reproduction is required rather
than decorative: the original comparison's script was **never preserved** — the defect
`evals/goldens/holdout/audit/README.md` was written about, and the reason `RESULTS.md` Finding
2's counts are not re-derivable at all — and an aggregate-only match is what
`OBJECT_CLASS_INVESTIGATION.md` §0's struck reproduction already proved insufficient.

**What `A` does NOT do.** It does not change §5, does not restamp any item, does not touch any
cassette, and does not alter criterion 1b or criterion 2 — `A` never scores a prediction. It
governs §7 re-runs and any future annotator comparison, and nothing else.

---

## 6. Non-determinism

Temperature 0.0 is **not** a determinism guarantee — the eval pilot reproduced different
extractions for 2 of 10 items across two identical runs.

**The harness runs the full gold set 3× and reports the per-item modal outcome plus a
count of items unstable across runs.** Three, not two: with two you cannot break a tie.
No single-run number is ever published without this caveat attached.

### 6.1 When a third run cannot be recorded (added v0.29; tie rule amended v0.30)

A third run is occasionally **unobtainable**, not merely unrecorded: the provider can
reject the request itself, reproducibly, for one segment. When that happens the rule is
**report the segment on the runs that exist and say so inline** — never silently average
over two, and never alter the request to force a third.

- The stability figure for such a segment is computed over the runs actually recorded,
  and **every place that figure appears must state the run count and the reason on the
  spot**, not in a footnote or a methods section the reader may not reach. "Modal outcome
  over 2 runs (third refused by the provider, see §6.1)" is the shape.
- **Tie-breaking is unavailable at n=2 by construction, and the tie resolves to the WORST
  observed outcome** — `report.py`'s G2 rule, which already governs the no-unique-mode case
  at n=3. The item is always counted unstable. *(Amended at v0.30. As first written at v0.29
  this clause said "reported as unstable with no modal outcome, not resolved by picking one",
  which contradicted G2 — an inconsistency introduced by writing §6.1 without reconciling it
  against the already-built reporter. G2 wins on two grounds: it embodies the same principle
  §6.1 was reaching for — never round in the pipeline's favour, take the conservative reading
  — and "worst observed" is a **defined** status, whereas "no modal outcome" leaves the item's
  standing in criterion 2's numerator undefined and invites some later piece of code to
  improvise a treatment for it. Deferring keeps the item honestly scored and inside criterion
  2's denominator.)*
- **Do not change the completion cap, temperature, prompt, or any other request parameter
  to obtain the missing run.** A cassette recorded under different parameters is not
  comparable with the rest of the set, so forcing one trades a single clean data point for
  a confound spanning every number the set produces. This is a real finding about the
  model, not a gap to be closed by re-rolling.

**The instance that created this rule: `C17-021` run 3, 2026-08-24.** `openai/gpt-oss-120b`
returned HTTP 400 `json_validate_failed` with an **empty** `failed_generation` on three
consecutive attempts, the last as the first call of a cold process, while runs 1 and 2 of the
byte-identical request had recorded cleanly. `C17-021` is the reciprocal-duty segment behind
§8.4's `mutual_obligation` gap. See CLAUDE.md's debt list for the full failure-mode entry.
`C17-021` is therefore scored over **2 runs**, and its 35 sibling cassettes over 3.

---

## 7. Held-out blinding

> **STATUS (v0.42): the prospective mechanism described in this section was NEVER PERFORMED
> and is now established as unperformable for this project's drafting cadence. It ran once,
> on 2026-08-29, in the amended one-sided form described in §7.1 below, and returned
> `K = 14/32` → REDESIGN.** The original text is retained unedited beneath this line, per
> this document's corrections-are-new-text discipline; **§7.1 is the operative process**,
> and the text below is a dated record of the design that was superseded, not instructions
> to follow.

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

> **SUPERSEDED IN PART BY §5.1 (v0.45).** The clause above is the one place this document ever
> stated how two annotators are compared, and it says *"a **prediction** inside the accept-set"* —
> reaching for the pipeline's word while describing two annotators, which is the conflation §5.1
> rules on. **From v0.45, every annotator comparison uses §5.1's predicate `A`, not §5.** Three
> things change: an out-of-vocabulary value is `NON_CONFORMING`, never a disagreement; accept-set
> clauses compare by mutual membership rather than one-sidedly against gold's set; and bands are
> derived at the surviving `n`. The 2026-08-29 run recomputed under `A` gives **K = 7/27**, still
> **REDESIGN** — see §5.1's table.

**Thresholds, fixed in advance:**

| K / 20 | Verdict |
| :--- | :--- |
| 0–1 | **PROCEED** — report K/20 with its Wilson CI; claim no rate below 5% |
| 2–3 | **DIAGNOSE** — clustered (≥2 on one field/rule) → fix rule, re-check across all 100, draw a second disjoint 20, proceed iff K₂ ≤ 1. Diffuse → treat as ≥4 |
| ≥4 | **REDESIGN** — re-annotate all 100 under a revised guideline *and* a changed process |

N=20 catches a ≥15% error rate ~82% of the time, is a coin flip at 10%, and cannot
certify 5%. It is a tripwire, not an estimator, and must be reported as one.

### 7.1 Amendment (v0.42) — what was actually run, and why the design above could not be

**This is a process amendment, not a correction of a typo.** The mechanism above assumes a
*prospective* withhold: items set aside at draw time and never seen by the reviewer until
the check. **That assumption was never satisfied for any batch, and by the time §7 was
attempted it could not be satisfied retroactively.** All 32 locked items had been
individually reviewer-signed-off — 24 carry `adjudicated_by: reviewer`, 2 carry
`reviewer_status: RULED_BY_REVIEWER`, all 32 are `APPROVED` — so there was no item in the
set the reviewer had not already adjudicated, and `gold/holdout/drafts/` had never existed.

**The root cause is a cadence mismatch, and it is worth naming so the next design does not
repeat it.** §7 presumes batches are drawn, annotated, and closed with a subset quarantined
throughout. This project's actual cadence is *iterative and reviewer-coupled*: every item is
escalated, adjudicated, or at minimum signed off item-by-item as it is drafted, and the
guideline is amended from the items as they are annotated. Under that cadence a prospective
withhold is not merely skipped, it is **incompatible** — an unreviewed item cannot be locked,
and §14.4's own rule removes reviewed items from the holdout pool, which at 100% review
coverage empties the pool.

**What was run instead — one-sided blinding.** A fresh cold annotator (never the drafter's
session, and deliberately not a context-inheriting fork) annotates from a field-allowlisted
packet of raw segments plus this guideline. **The cold annotator is blind to the drafts; the
reviewer is blind to nothing.** The result is therefore a **cold second-annotator check**,
not a held-out one, and must be published under that name.

**Consequential differences from the design above, each of which must travel with any
published K:**

1. **Census, not a 2-of-10 sample.** With nothing withheld there is no sample to draw, and
   the leak measurement below caps the uncontaminated subgroup regardless of N. The whole
   locked set is annotated cold. **A census has no sampling error** — K/N is exact for the
   locked set, and the Wilson interval speaks only to extrapolating to future items.
2. **§14.4's holdout-pool filter is suspended**, being inoperative once every item is
   reviewed. One consequence is favourable and is claimed: the sample is **not**
   systematically easier than the gold set, which §14.4's own accepted limitation concedes
   the original design could not avoid.
3. **Verdict bands must be re-derived for the actual N**, by preserving §7's *evidential
   strength* (the Wilson₉₅ lower bound at each trigger) rather than its raw counts. At
   N=32 that gives PROCEED ≤2 / DIAGNOSE 3–5 / REDESIGN ≥6. Bands are fixed **before** the
   comparison and never revised after K is known.
4. **The guideline leaks the answers, and this is now measured rather than suspected.**
   20 of 32 items have their `span_text` quoted verbatim in this document; grading the
   remaining 12 by citation leaves **3** items uncontaminated. K is therefore reported as an
   L0/L1/L2 leak gradient with every N inline — *and* the gradient is confounded with
   difficulty, because this document works through exactly the segments that were hard.
   **A leak-controlled comparison is not available from a corpus the guideline was authored
   from.** The channel that survives is the one this document never states for any segment:
   **item count and exclusion decisions**.
5. **The spot-check's stated purpose does not survive.** §7 justifies it as the reviewer's
   *fresh* eyes on agreements; those eyes are not fresh. It is still run, and on this
   occasion it earned its place — see the `known_gaps` finding below.

**The finding that most matters, and it is about this document, not about an annotator.**
`known_gaps` is **not one of §5's eight clauses**, so no disagreement on it can affect K.
Measured: the two annotators disagree on `known_gaps` for **19.4% of matched items**, and
that disagreement moves §9's in-force criterion-2 denominator (`len(known_gaps) == 0`) from
**15 items to 17** — a ~13% swing in the denominator of this project's headline acceptance
figure, entirely invisible to the instrument meant to be measuring annotation quality.
**Until this is resolved, no K should be trusted, including any K computed to check whether
a REDESIGN response worked.** Whether the fix is a ninth §5 clause or a separately-tracked
and separately-thresholded agreement rate is an **open decision, deliberately not taken
here** — it turns on whether §5 is one predicate serving both pipeline scoring and annotator
comparison, or two predicates sharing eight clauses. Full statement of both options in
`apps/brain/evals/goldens/holdout/RESULTS.md`.

**Full record** — pre-registration, seeds, leak classification, sealed cold annotations,
comparison, and the run log including a failed first attempt — is in
`apps/brain/evals/goldens/holdout/`.

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
| `within N <unit> after/from/following` | `UNMAPPABLE_TEMPORAL` — `_WITHIN_RE` requires the preposition `of` (§8.6) |
| `upon` / `following` / `prior to` / `on` / `at` / `as of` + trigger | `UNMAPPABLE_TEMPORAL` — `_RELATIVE_RE` accepts only `before`/`after`; **133 of 164 trigger-bearing segments rejected** (§8.9) |
| Mutual/reciprocal duty (both parties bound) | Unrepresentable — one `obligor`, one `obligee`, CHECK they differ (§8.4) |
| Compound-action duty (two verbs, one object) | Only the primary verb is representable — `action` holds one verb (§8.3) |
| `UNLESS` / any exception carve-out | **Does NOT fail to parse on the extraction path (v0.28 correction).** The grammar rejects a literal DSL `UNLESS`, but `ir_compile._build_dsl()` quotes every `condition_raws` entry, so a carve-out arriving as extracted text compiles into an `AtomPredicate` verbatim. The failure is **silent** — a clause-7 `PARTIAL`, or a spuriously `FULLY_CORRECT` item whose carve-out was dropped — not a visible compile failure (§8.2, §3.8.1) |
| Redacted value (`**`, `[***]`) | Value withheld in the filing; unresolvable by any pipeline stage (§8.1) |
| Running header/footer spliced mid-sentence | Not a v1 *compiler* gap — a corpus-text gap that lands inside a scored span (§8.7) |

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

**Rule.** Annotate the item. Set the affected field to `null`, name the field in
`missing_fields`, `known_gaps` gains `"redacted_value"`, and record the literal redacted phrase
in the non-scored `redacted_phrase` field.

**`underspecified` is NOT set by this rule (v0.28 — struck).** Through v0.27 this rule said
*"`underspecified = true` with the field named in `missing_fields`"*, which contradicted
**three** other rules at once: §3.9's closed trigger list (a missing temporal is not a trigger),
§14.2's prohibition on using the field for anything outside that list, and §15.3's explicit
argument that *"annotating `underspecified = true` would make **every** such item fail clause 8
of the conjunctive predicate automatically — not because extraction was wrong, but because gold
asserted a capability v1 explicitly declined to build."* `underspecified` follows §3.9 alone,
from the item's parties, dates, triggers and `bd` durations. `missing_fields` is unaffected: §5
excludes it from the predicate, and it is the channel that keeps the withheld-versus-absent
distinction recoverable, which is this rule's actual purpose.

**Why not exclude them.** Excluding redacted segments is the one answer that is clearly
wrong: at 2.5× concentration in the hard stratum it would deplete exactly the documents
§2.2's 25-item floor exists to protect — the same failure mode as the enumeration defect in
§18.6, arriving through an annotation rule instead of a parsing one.

**Why not simply `temporal: null` with no tag.** That conflates *"the contract states no
deadline"* with *"a deadline exists and was withheld from the filing"*. They are different
facts about the document, and untagged they become indistinguishable in criterion 1b and
criterion 2.

### 8.3 Compound-action duties (v0.15 — REVIEWER-CONFIRMED; application ratified 2026-08-22)

**Label discrepancy, recorded rather than quietly reconciled.** This section has carried
*REVIEWER-CONFIRMED* since v0.15, but `C03-02`'s own annotator notes recorded that the ruling
*"was requested three times and not given"* and treated both the tag and the rule as reversible.
The two artifacts disagreed. The reviewer ruled on 2026-08-22 (B1) — one item, confirmed — and
acknowledged the earlier requests had gone unanswered. The rule and its application are now
genuinely confirmed; the discrepancy is left visible because a label that overstated its own
authority for thirteen versions is worth being able to find again.

**The rule, as ruled:** *compound action verbs governing one shared, indivisible object
stay a single item with the full action recorded verbatim; only split when the verbs
govern genuinely separate objects.*

| Shape | Treatment |
| :--- | :--- |
| Two verbs, **one shared indivisible object** — *"provide to AT&T, **and keep current**, an escalation document"* | **One item.** Primary verb in `action`, full verb phrase verbatim in `annotator_notes`, `known_gaps: ["compound_action"]` |
| Two verbs, **genuinely separate objects** — *"responsible for **the installation of new software releases** … **and the distribution of documentation updates**"* | **Two items** (§4.3) |

The discriminating test is **not** "one object or two" on its own: *"shall promptly notify
and remedy any breach"* shares an object yet the performances are independent. The test is
whether the verbs are **aspects of one indivisible performance** or **separate
performances**.

**That test moved to §4.3 at v0.28 and is stated there, once, for both sections.** It was
duplicated here and in §4.3 in contradictory forms — §4.3 tested object identity, this section
tested performance identity — and the two gave opposite answers on this section's own
`notify and remedy` example. §8.3 now governs only the **tag**: when the split decision made
under §4.3 yields one item, what is recorded about the verb that `action` cannot hold.

`known_gaps: ["compound_action"]` is retained on single items even though the annotation is
*correct* under this rule: IR v1's `action` still holds one verb, so the field genuinely
under-records the sentence, and the tag keeps that recoverable from data rather than from
prose.

**The tag records a loss, and fires only where there is one (v0.28 — F2).**

- Dropped verb maps to a **different** taxonomy verb than `action` → **tag**. *"provide … and
  keep current"* → `PROVIDE` + `MAINTAIN` (`C03-02`).
- Both verbs map to the **same** taxonomy verb → **do not tag.** A legal doublet such as
  *"indemnify and hold harmless"* loses nothing — §8.8 names `hold harmless`→`INDEMNIFY` as
  defensibly mappable — and tagging it would assert a v1 limitation that does not exist while
  removing a fully-scoreable item from §9's `len(known_gaps) == 0` denominator. Same objection
  §3.5.1 raises against tagging joint obligors.
- Dropped verb is **outside the taxonomy entirely** (*"label and package"*) → it is genuinely
  lost: tag **`compound_action` and `action_not_in_taxonomy`** (§8.8). Both apply; §9's per-tag
  counts are non-summable and already say so. Settled here rather than left to be discovered.

**Branch 3's determinant is non-membership PLUS non-mappability, not bare non-membership
(v0.47 — REVIEWER-RULED, and this is a correction to how the three branches read together).**
The branches above are stated in terms of what a dropped verb *"maps to"*, which is §8.8's
**defensible-mapping** notion, not raw membership in `ACTIONS`. Read as bare membership, branch 3
fires on branch 2's **own worked example**: `hold harmless` is not in the 34-verb list either, yet
§8.8 names `hold harmless`→`INDEMNIFY` as defensibly mappable and branch 2 exists precisely to say
that doublet loses nothing. So the test is:

> a dropped verb triggers branch 3 iff it is **neither a taxonomy member nor defensibly mappable
> to the verb in `action`**.

Found while ruling §8.3.2 below; recorded here because it governs all three branches, not only the
item that exposed it.

### 8.3.2 Near-synonym chains whose alternatives are all off-taxonomy (v0.47 — REVIEWER-RULED)

**Ruled: branch 3 applies on its letter. The tags are cumulative.** `E01-01` — *"No provisions of
this Agreement shall be deemed **waived, amended, supplemented or modified** by any Party
hereto…"* — takes **three** tags: `compound_action`, `action_not_in_taxonomy` and (for its
separate carve-out) `exception_unsupported`. `WAIVE` is a taxonomy member; **`AMEND`, `SUPPLEMENT`
and `MODIFY` are not**, verified against `compiler/ast.py`'s real `ACTIONS`, and none is defensibly
mappable to `WAIVE` — amending a provision and waiving one are different legal acts, and gold's own
notes claim no mapping, only that *"only WAIVE exists in the 34-verb taxonomy."*

**The rejected alternative, and why.** Branch 2's *spirit* was genuinely arguable here: both
annotators independently described the chain as one act-type — gold *"a compound near-synonymous
action"*, cold *"disjunctive alternatives of one prohibited act-type over one indivisible
object"* — which is the same intuition branch 2 uses to exempt *"indemnify and hold harmless"*.
**Rejected because branch 2 states that intuition as a mechanical mapping test, and extending it
to a "feels like a legal doublet" judgment would trade a checkable boundary for an unfalsifiable
one** — the same preference for precise mechanical tests over vague ones that §2.5.1, §3.8.2 and
§5's number rule each already record. Where a defensible mapping genuinely exists, branch 2 still
fires on its own terms; what is refused is a branch-2 exemption with no mapping behind it.

**Neither annotator's answer is adopted as-is, and cold's near-miss is instructive.** Gold applied
no branch at all — it recorded branch 3's condition in its notes (*"only WAIVE exists…"*) and drew
no tag from it. Cold reached branch 3's **conclusion** through branch 1's **premise**: *"the
dropped verbs map to different taxonomy labels than the primary"* — they map to **none**. A right
answer via a false premise is not adopted, because the premise is what generalises.

**Re-check across all prior batches, per §10.** Every locked item carrying `compound_action` or
`action_not_in_taxonomy` was re-read against the corrected branch test:

| item | dropped verb(s) | status | outcome |
| :--- | :--- | :--- | :--- |
| `C03-02` | *"keep current"* → `MAINTAIN` | a **taxonomy member** | branch 1 — `compound_action` only. **Unchanged** |
| `E01-01` | *amend, supplement, modify* | non-members, **no** defensible mapping | **branch 3 — gains `action_not_in_taxonomy`.** Restamp pending, §10.1 F8 |
| `C10-01` | *defend*, *hold harmless* | `hold harmless`→`INDEMNIFY` is §8.8's own named mapping; **`defend` is neither a member nor mappable (§8.8.2)** | **branch 3 — gains `action_not_in_taxonomy`. RULED and restamped v0.48** |
| `C10-02`, `C14-04` | n/a — single-verb items | carry `action_not_in_taxonomy` on §8.8's own ground | **Unchanged** |

**`C10-01` is deliberately NOT decided here.** Its own notes state branch 3's raw condition —
*"DEFEND and HOLD_HARMLESS are not taxonomy members at all"* — so a bare-membership reading would
restamp it too. Whether **`defend` is defensibly `INDEMNIFY`** is a substantive question (a duty to
defend is conventionally distinct from a duty to indemnify) that was **not** in front of the
reviewer when this ruling was made, and it is not folded in silently. Queued as **§10.1 F11**.

**DECIDED v0.48 — §8.8.2.** `defend` is ruled a genuine gap on corpus evidence (33 sentences use
it with no `indemnify` anywhere in them; `C03` disjoins *"failed to defend or indemnify"*; `C03`
§(c) owes the defence *"whether or not litigation is actually commenced or the allegations are
meritorious"*; `C11` converts a failed defence duty into a payment duty). Branch 3 fires and
`C10-01` is restamped at v0.48. **The parenthetical above — *"a duty to defend is conventionally
distinct from a duty to indemnify"* — was the hypothesis this ruling tested, not an assumption it
rested on, and it held.** Note what the outcome does to this section's own worked reasoning:
`hold harmless` and `defend`, the two non-member verbs of a single triplet, land on **opposite**
sides of the mappability limb — the clearest available demonstration that the limb discriminates
rather than rubber-stamping.


**The full verb phrase goes verbatim in `annotator_notes` in every branch, tagged or not** —
the record of what the sentence said does not depend on whether the tag fires.

**Instances on record:** probe `E05-019` (*"shall be indemnified and held harmless by WHDX and
11i"*) and `C17-066` (*"shall indemnify and hold harmless the other Party and its Affiliates"*),
the latter in a locked item's own source segment and found independently of the probe by M2's
verification sweep. **No corpus-wide rate was measured** — the class's frequency is recoverable
later from `known_gaps` data once the harness runs, and the refinement's correctness does not
depend on it: where nothing is lost, a tag recording a loss is simply wrong.

**Open consequence, recorded not resolved:** for the split case, two items drawn from one
coordinated verb phrase cannot both satisfy §3.1's *minimal contiguous substring*
requirement — "shall … notify … any breach" is not contiguous once "and remedy" is removed.
Overlapping or identical spans then collide under §4.1's IoU alignment. **No split case has
arisen in batch 1** (the one candidate, `E07-010` sentence 3, fails first on its obligor
being "These personnel", not a party), so this is flagged for whichever batch first hits
it rather than solved speculatively.

**Superseded status note:** One sentence can impose two duties on one object
with two verbs — *"Vendor will provide to AT&T, **and keep current**, an escalation
document"* is a one-time `PROVIDE` and an ongoing `MAINTAIN`. IR v1's `action` holds a
single verb, so the sentence cannot be represented whole.

**Rule.** Annotate **one** item on the primary (first) verb, tag
`known_gaps` gains `"compound_action"`, and record the dropped verb(s) verbatim in
`annotator_notes`.

**Why not two items on the same span.** Two gold items with byte-identical spans collide
under §4.1's IoU alignment, which assumes one item per span region — it would create a
scoring defect to record an annotation nuance.

**Why not silence.** Dropping *"keep current"* with only a prose note weakens a continuing
duty into a one-off, the same silent-weakening `ir_compile.py` refuses for temporals (it
raises `UNMAPPABLE_TEMPORAL` rather than quietly emitting `temporal=None`). The tag keeps
the loss recoverable from the data.

**Consequence for §2's clause count:** a compound-action sentence counts as **one**
obligation-bearing clause, not two, for the 1–3 eligibility band.

### 8.7 Corpus artifacts spliced inside a span (v0.18 — REVIEWER-ADJUDICATED)

**Motivating case** — `C04-117`: *"…solely to the extent Miltenyi's exercise of rights
under such licenses is required **27 Miltenyi Biotec-Bellicum Supply Agreement (Execution
Copy, March 27, 2019)** to supply Miltenyi Product to Bellicum…"*

A running page header, bankruptcy docket stamp, `TM` marker or CUAD `Source:` footer is
spliced **mid-sentence** in the source text. Paragraph reconstruction (§18.6) cannot strip
it: the artifact is genuinely inside the sentence in the document, not on a line of its
own. Batch 1 recorded the class (`E07-01`'s notes) and deferred it — that item's span
happened to stop before the artifact. Batch 2's did not, and could not: §3.1's
minimal-*complete*-span rule requires a scope clause that sits on **both sides** of the
splice.

**Measured before the rule was written**, the same discipline §8.6 used:

| | count | note |
| :--- | --: | :--- |
| Pool segments matching the splice pattern | 76 / 1,547 (4.9%) | mechanical match |
| Genuine artifacts after inspection | ~60 (3.9%) | rest are real durations (*"within 30 Days"*) and notice blocks |
| C04 running header | 22 | 12% of that document's segments, **all 22 mid-sentence** |
| C06 docket stamp | 15 | `Case 18-10248-MFW Doc 632-1 Filed 04/18/18 Page 7 of 60` |
| E07 page header · CUAD `Source:` · C22 · E01 · C05 | 7 · 5 · 4 · 2 · 2 | |

**It is document-concentrated, not uniform.** Which documents a batch draws decides how
often it bites, and C04 is a **hard-stratum** document.

**Rule.** Annotate the item. `span_text` and any `conditions` entry carry the artifact
**verbatim**; tag `known_gaps` gains `"corpus_artifact_in_span"`; record the artifact's literal
text and its segment offsets in `annotator_notes`. Criterion 2 is reported with and
without artifact-in-span items, the same paired-reporting shape §9 already applies to
`known_gaps`.

**Why verbatim (Reading A).** `segment_text` must stay byte-identical to what
`run_pipeline()` is handed — §2.3's own rationale, applied to the span instead of to PII.
A gold span that silently cleans the text measures a document the pipeline never sees.

**Why not truncate the span before the artifact (Reading B).** It drops half a scope
clause and one whole `Condition` entry, violating §3.1 and weakening the obligation in
exactly the way §8.3 refuses for dropped verbs.

**Why not exclude artifact-bearing segments (Reading C).** It would remove ~3.9% of the
pool and **12% of C04**, a hard-stratum document — §13's and §18.6's
difficulty-correlated depletion arriving through a third mechanism. Batch 1's measurement
that artifacts overall are *not* difficulty-correlated (hard 1.2%, standard 9.1%) does not
cover this subclass: the mid-sentence splice is concentrated in C04 and C06.

**Two second-order consequences, recorded because both are scored, not cosmetic:**

1. The artifact contaminates `conditions` as well as `span_text` — `C04-01`'s first
   condition entry carries it — so §5's clause 7 is affected, not only span alignment.
2. The C04 artifact **contains a real date** (*March 27, 2019*) inside an item whose
   `temporal` is `null`. That is a live false-positive hazard for date extraction.

**This is not a v1 compiler gap.** Unlike §8.1–§8.6, nothing about IR v1 causes it and no
grammar change fixes it. It is a property of the corpus text, and the tag exists so its
effect on criterion 2 is countable rather than folded silently into extraction quality.

---

### 8.3.1 The split-span case (v0.23 — DEFAULT, PENDING CONFIRMATION)

§8.3 recorded this as an **open consequence** and deferred it explicitly: *"two items drawn
from one coordinated verb phrase cannot both satisfy §3.1's minimal contiguous substring
requirement… No split case has arisen in batch 1, so this is flagged for whichever batch
first hits it rather than solved speculatively."*

**It arrived at `C14-076`:** *"**Each party** shall **deduct** such taxes from the payments
due to the other party hereunder … and shall promptly **furnish** such other party with
appropriate tax receipts."* Two governing verbs, genuinely separate objects (*taxes* vs *tax
receipts*), so §4.3 requires two items — and the shared subject `Each party` sits at the head
of the sentence, governing both.

**The trilemma, stated before the choice:**

| Option | Fails on |
| :--- | :--- |
| Both spans = the whole sentence | Byte-identical spans **collide** under §4.1's IoU ≥ 0.5 alignment — §8.3's own stated wall |
| Second span = subject + second verb phrase, skipping the first | **Non-contiguous**, violating §3.1's byte-exact-substring requirement outright |
| Second span = the contiguous verb phrase alone | `obligor` is then taken from **outside** `span_text` |

**~~Rule (default).~~ SUPERSEDED AT v0.31 — see "Amendment (v0.31)" below.** ~~Take the third
option. The second item's `span_text` is the **contiguous verb phrase without the shared
subject** (*"shall promptly furnish such other party with appropriate tax receipts"*). The
shared `obligor` is annotated from the sentence head, and the item is tagged
**`shared_subject_split`** so the exception is countable rather than silent.~~

**Why.** §3.1's byte-exact contiguity is a *hard* requirement the grounding gate enforces
mechanically; §3.5's positional rule is a *methodological* one guarding against inference
from elsewhere in the **document**. Taking a subject from the same sentence, three words
away, is a far smaller departure than either breaking contiguity or colliding the alignment
— and the two spans stay **disjoint**, which keeps §4.1 sound. The cost is real and is
tagged, not hidden: for these items alone, `obligor` is not verifiable from `span_text`.

### Amendment (v0.31) — the third option is mechanically unreachable, and there is a fourth

**The v0.23 default was wrong, and the first real scoring run proved it.** Its reasoning
turned on a distinction between hard and soft constraints: *"§3.1's byte-exact contiguity is
a **hard** requirement the grounding gate enforces mechanically; §3.5's positional rule is a
**methodological** one."* That is the error. The grounding gate enforces **more than
contiguity**: `ground_candidates()` rejects any candidate whose nested fields — `obligor_alias`
included — are not literal substrings of `span_text`, as `NESTED_FIELD_NOT_IN_SPAN`. So
"obligor taken from outside `span_text`" is **not** a methodological cost. It is a second
mechanical rule of the *same gate* that rules out option 2, and it makes **option 3
unreachable by the pipeline by construction**.

**Measured, not argued.** Scoring the 35 recorded cassettes put `C14-02` at `MISSED` on all
three runs. The model had in fact extracted the duty correctly — run 3 emitted an obligation
with `action = PROVIDE`, matching *furnish* — but with `span_text` spanning `[12:253]`
against gold's `[184:253]`, IoU 0.286. It could not have done otherwise: emitting gold's span
while naming `Each party` as obligor is precisely what the grounding gate refuses.

**The fourth option, absent from the original trilemma.**

| Option | Fails on |
| :--- | :--- |
| 1 · Both spans = the whole sentence | Byte-identical spans collide under §4.1 |
| 2 · Subject + second verb phrase, skipping the first | Non-contiguous; violates §3.1 |
| 3 · Contiguous verb phrase alone *(the v0.23 default)* | **`NESTED_FIELD_NOT_IN_SPAN` — unreachable by the pipeline** |
| **4 · Contiguous, from the shared subject through the END of the second verb phrase** | **Nothing mechanical. Adopted.** |

**Rule (v0.31).** The second item's `span_text` runs **contiguously from the shared subject
through the end of its own verb phrase**, and therefore properly **contains** the first
item's span. For `C14-076` that is `[12:253]` — *"Each party shall deduct … and shall
promptly furnish such other party with appropriate tax receipts"* — against `C14-01`'s
`[12:178]`. Contiguous (§3.1 ✓), `obligor` and `obligee` both inside `span_text` (grounding
gate ✓), and **not** byte-identical to the first span, so §4.1 does not collide. The item
stays tagged **`shared_subject_split`**: the exception is still countable, and what is tagged
has changed from "obligor unverifiable" to "spans are nested".

**The cost, stated rather than buried.** The two spans are **nested**, with IoU 0.689 between
them — above §4.1's 0.5 threshold. Greedy-by-descending-IoU resolves this correctly *when the
model emits both spans*: an exact match to `[12:178]` pairs with `C14-01` at IoU 1.0 before
`[12:253]` is considered, which then pairs with `C14-02`. Run 3 of the recorded set emitted
exactly that pair, so this is observed behaviour, not a hoped-for one. **When the model emits
only ONE span the pairing is genuinely ambiguous** and one of the two items will be `MISSED`.
That is a real, accepted limitation of option 4 — and it is strictly better than option 3,
under which the item could never be scored correctly at all.

**Conforming.** `C14-02` is the only locked item carrying `shared_subject_split` and is the
only item this amendment changes. **It is NOT yet conformed** — doing so restamps it and
collides with two invariants that need their own decision; see §22.

**Why this is not §8.3's one-item case.** §8.3 keeps *one* item when two verbs are aspects of
one indivisible performance. Deducting tax and furnishing a receipt are separate
performances with separate objects, which is exactly the branch §8.3 sends to §4.3 — and
that branch had never been exercised until now.

**Pending confirmation because it sets the span rule for every future split.** If the
reviewer prefers the whole-sentence option, §4.1 needs an accompanying tie-break amendment
for identical spans, which is why that option is not merely a matter of taste.

### 8.8 Out-of-taxonomy action verbs (v0.24 — REVIEWER-RULED)

`compiler/ast.py`'s `ACTIONS` is a **closed 34-verb list**. Real contract verbs routinely fall
outside it with no defensible member to map onto.

**Measured at the granularity that matters.** A seeded random sample of 40 party-subject
obligation clauses (seed `108325`), hand-classified:

| Class | n | Share of annotatable |
| :--- | --: | --: |
| Not an obligation clause at all (copular *"shall not be liable/entitled"*, non-party subject, Agreement-as-subject) | 14 / 40 | — |
| Verb **is** in the taxonomy | 10 | 38% |
| **Defensibly mappable** — `hold harmless`→`INDEMNIFY`, `nominate`/`designate`→`APPOINT`, `arrange`→`PROCURE`, `address and correct`→`CURE`, `continue to maintain`→`MAINTAIN`, `deduct`→`WITHHOLD` | 10 | 38% |
| **Genuine gap** — `resign`, `discontinue`, `perform` ×2, `approve`, `request` | **6** | **23%** |

**23%, 95% Wilson CI [11%, 42%].** An earlier token-weighted estimate of 44% is superseded: it
measured share of verb *tokens* over the head of the distribution, over-weighting a few
frequent verbs, and answers a different question than *"what share of items will have an
untaggable action."*

**Rule.** Applies **only** to the genuine-gap class. A defensibly mappable verb is **not**
tagged — `deduct`→`WITHHOLD` (`C14-01`) is the worked example of a mapping that lands.

- `action` holds the **nearest** taxonomy verb.
- `action_accept_set` holds **that verb alone**, no widening.
- The real verb is recorded **verbatim** in `annotator_notes`.
- `known_gaps` gains **`"action_not_in_taxonomy"`**.

**Why not widen `ACTIONS`.** A v1 IR change against blueprint §21's explicit freeze, and it
would tune the IR to the corpus it is about to be graded on — the identical objection §11
raised against widening `_WITHIN_RE` before measuring.

**Why not generous accept-sets.** A set wide enough to admit `PROCESS` for *"perform the
capsule appearance test"* stops measuring whether extraction identified the action at all,
which is what §3.4 exists to prevent.

**SUB-CHOICE, adopted as default and flagged — v0.24 default, pending confirmation.** The
single-verb accept-set means an extractor scores clause 2 correct only by picking the *same*
near-miss the annotator picked; §14.4's objection to defaults partly applies. The alternative
— an **empty** `action_accept_set`, making every such item an automatic `PARTIAL` — is more
honest that no correct answer exists, but converts a measurement question into a guaranteed
failure for roughly one item in four. Revisit once batch 3 supplies a second rate.

**Consequence, stated rather than discovered later.** At 23% this tag attaches to about one
gold item in four. With batch 1's ~40% structurally-uncompilable finding it is a **second,
independent** arithmetic constraint on criterion 2's ≥80% bar. It is not an extraction-quality
finding and must not be reported as one.

**No locked item carries this tag yet** — `dispose` (`C02-049`) and `analyze` (`C04-118`) both
sit in segments excluded under §2, so the first real instance is still ahead.

**Superseded (v0.48): the paragraph above is a dated record, not live status.** Locked items now
carry this tag — `C10-02` and `C14-04` on this section's own ground, and, from v0.47/v0.48's
rulings, `E01-01` (§8.3.2) and `C10-01` (§8.8.2 below). Left unedited per the corrections-are-new-
text discipline.

#### 8.8.2 `defend` is a GENUINE GAP, not defensibly `INDEMNIFY` (v0.48 — REVIEWER-RULED, §10.1 F11)

**The question, and why it was not answerable by lookup.** §8.3.2's v0.47 re-check left `C10-01`
open: its span reads *"the Supplier shall **indemnify** the Distributor, **defend** and **hold
harmless** against any liability…"*, and §8.3's corrected branch test fires branch 3 iff a dropped
verb is **neither a taxonomy member nor defensibly mappable** to the verb in `action`.
`hold harmless`→`INDEMNIFY` is already this section's own named mapping, so the item turned
**entirely** on `defend`. Whether a duty to defend is conventionally the same duty as a duty to
indemnify is a substantive question about contract drafting, not a taxonomy-lookup question, and
it was put to the corpus rather than asserted.

**Ruled: `defend` is NOT defensibly mappable to `INDEMNIFY`. Branch 3 fires. `C10-01` gains
`action_not_in_taxonomy`**, joining `E01-01` as the set's second three-tag item.
`action_accept_set` already read `['INDEMNIFY']`, which is this section's single-verb requirement,
so **no accept-set change**. Verified against `compiler/ast.py`'s real 34-verb `ACTIONS`: there is
no `DEFEND`, and no member denotes conducting a defence (`RECOVER` and `REPAIR` are the nearest by
appearance and neither is one).

**MEASURED ACROSS THE WHOLE 28-DOCUMENT CORPUS, not argued from outside it.** 187 sentences use an
indemnity-family term. The detector was validated first against two known sentences — `C10`'s own
`C10-016` verb string and `C17`'s *"indemnify and hold harmless"*, the instance §8.3.2 already
cites — before any count was read off it.

| `indemnify` | `defend` | `hold harmless` | sentences |
| :--- | :--- | :--- | --: |
| ✓ | — | — | **86** |
| ✓ | ✓ | — | 30 |
| — | **✓** | — | **30** |
| ✓ | ✓ | ✓ | 28 |
| ✓ | — | ✓ | 9 |
| — | ✓ | ✓ | 3 |
| — | — | ✓ | 1 |

**33 sentences carry `defend`/`defence` with no `indemnify` in them at all.** A synonym is not
used alone 33 times and added 58 times.

**Three passages settle it, and all three are the corpus's own words.**

1. **`C03` — the contract treats them as two obligations that can be failed independently:**
   *"…except in a case where a Party has **failed to defend or indemnify** the other Party where
   it had an obligation to do so pursuant to Sections 3.15 or 3.36…"*
2. **`C03` §(c) — the defence duty is expressly triggered by allegations that may be meritless,
   which no indemnity can be:** *"Vendor shall conduct the defense … at Vendor's expense, against
   any claim … within the scope of Subsection (a) above, **whether or not litigation is actually
   commenced or the allegations are meritorious**…"* Subsection (a) is the indemnity; (c) is a
   separately numbered defence clause. A duty owed on a meritless allegation is a duty owed when
   there is, by definition, no loss to indemnify. This is the black-letter *"the duty to defend is
   broader than the duty to indemnify"* distinction, appearing **in this corpus** rather than
   imported into it.
3. **`C11` — breach of the defence duty *converts into* a payment duty, so they cannot be one
   duty:** *"If Franchisee **fails to assume the defense**, BKC may defend the action … and
   Franchisee **shall pay** to BKC all costs, including attorney's fees, incurred by BKC in
   effecting such defense, **in addition to** any sum which BKC may…"*

Structurally the same: defence carries counsel selection, litigation control, settlement authority
and progress reporting — 11 sentences across 5 documents assign defence *control* to a named
party, 15 across 11 documents tie settlement to it. An indemnity carries none of these.
**`defend` is a duty to *do* something; `indemnify` is a duty to *bear a loss*.** Mapping one onto
the other does not lose a shade of meaning, it loses the entire performance — which is exactly
what §8.8's mappable list never does: every entry there (`hold harmless`→`INDEMNIFY`,
`nominate`→`APPOINT`, `arrange`→`PROCURE`, `deduct`→`WITHHOLD`) maps a verb onto a member
denoting the **same** performance.

**`hold harmless`→`INDEMNIFY` is untouched and stays in the mappable list.** `hold harmless` alone
would have kept `C10-01` on branch 2; it is `defend` alone that moves it. The two halves of the
classic triplet come out on **opposite sides of the same test**, which is the useful result: this
is the first exercise of §8.3's v0.47 non-mappability limb against a verb this section had not
already ruled on, and the limb **discriminates** rather than rubber-stamping.

**Added to this section's genuine-gap class**, alongside `resign`, `discontinue`, `perform`,
`approve` and `request` — and it is the first entry there that is not merely *absent* from
`ACTIONS` but affirmatively **distinct from its nearest member**. Recorded as its own class of
reason so the next mapping question asks *"same performance?"* rather than *"close enough?"*.

**The 23% measured rate is NOT restated upward by this ruling.** That figure came from a seeded
40-clause sample; `defend` did not appear in it, and one adjudicated verb outside the sample does
not move a sample-based rate. The rate stands at 23%, 95% Wilson CI [11%, 42%], unchanged.

#### 8.8.1 Negated entitlement is the same copular class as affirmative entitlement (v0.41 — REVIEWER-RULED)

**The class this section names — *"not an obligation clause at all (copular 'shall not be
liable/entitled', non-party subject, Agreement-as-subject)"* — was stated and measured only in
its affirmative-modal form.** Every worked instance on record (`C04-163`'s *"shall not be
responsible for payments"*, this section's own table row) negates the **verb** (`shall NOT be
liable`) while asserting a status. Left untested was the mirror construction: a clause that
negates the **object of possession** instead (*"shall have **no** right of X"* /
*"shall have any right of X...unless"*) while keeping the verb affirmative. Grammatically these
look different — one has "not" before the copula, the other doesn't — but the test this class
applies was never about where the negation sits.

**Confirming case** — `C11-101`: *"(c) No Principal shall have any right of subrogation,
repayment, reimbursement or indemnity whatsoever, unless and until the Obligations are paid or
performed in full..."* This states a legal status (a Principal does not currently hold
subrogation rights) rather than commanding or forbidding any party's conduct — nobody is being
told to do, or to refrain from doing, an act. That is the identical question `C04-163`'s
already-excluded clause answers the same way, just phrased as "shall have no right" rather than
"shall not be entitled."

**Rule, stated so the next instance is decided by citation.** §8.8's copular "not an obligation
clause at all" class covers a clause asserting a party's legal status, right, or liability
**regardless of which word carries the negation** — `"shall not be liable/entitled to X"` and
`"shall have no right of X"` / `"shall have any right of X...unless"` are the same shape.
Negation placement does not decide the class; what decides it is the removal test this class
has always applied: does the clause command or forbid **conduct**, or does it describe a
**status**? A negated-entitlement clause commanding no conduct fails the same way its
affirmative counterpart does.

**Does not exclude a genuine `MUST_NOT`-on-conduct clause that happens to use "have."**
*"Franchisee shall not have any employee operate machinery without training"* commands
conduct (who may operate what) and is not excluded by this note — the test is what the clause
asserts, not the presence of the verb "have."

### 8.2 `UNLESS`-dependent clauses (v0.10)

IR v1 has **no exception construct at all**, by the deliberate freeze decision recorded in
`packages/ir-spec/SPEC.md` §6. A clause whose operative meaning sits in an `unless` therefore
cannot be represented faithfully.

**Correction (v0.28) — the stated v1 behaviour was wrong, and it was tested rather than
assumed.** Through v0.27 this section said an `UNLESS` *"does not underspecify, it fails to
parse."* That is true only of the **DSL path**, which extraction never takes. Run against the
real pipeline, `condition_raws = ["unless an exemption is provided"]` produces a clean
`Obligation` carrying
`Condition(predicate=AtomPredicate(raw='unless an exemption is provided'))` — because
`ir_compile._build_dsl()` quotes every `condition_raws` entry, so the grammar's `UNLESS`
rejection is never reached. This is exactly what `SPEC.md` §6 forbids — a legal carve-out
silently absorbed into a condition — and it is an **unfixed production defect**, recorded in
CLAUDE.md's debt list and tied there to the Normalizer checkpoint. Its consequence for gold:
`exception_unsupported` items fail **silently**, not loudly, so §15.3's loud-versus-silent
taxonomy files this class on the wrong side of the line.

**Rule.** Annotate the **carve-out-free reading** with `known_gaps` gains
`"exception_unsupported"`, and record the full carve-out verbatim in `annotator_notes`.

**Correction in place, v0.46 — this paragraph named the pre-rename tag `unless_unsupported` for
six versions after the rename was approved, and that is a live rule statement, not a dated
record.** The rename (`unless_unsupported` → `exception_unsupported`, *"the class is semantic,
not lexical"*) was approved at the original consolidation pass on 2026-08-22 (§20.4 decision 5),
which re-stamped `E01-01` and `C14-01` at the time; §8.2's own Rule paragraph was never updated
to match. §3.8.1 and §10's v0.40 changelog entry both **noted** the staleness without editing it,
each on the reading that §8.2's text was a dated record. It is not — §10's own process note draws
exactly this line, and *"annotate X"* in the imperative is the operative instruction an annotator
follows, so it is **corrected in place** and the history is preserved here rather than in the
rule line. Nothing else changes: `exception_unsupported` was already the tag in use by all five
carrying items, by `evals/harness/report.py`'s `GAP_DIRECTION`, and by §3.8.1's branch 3.

**Why this was worth doing ahead of every other tag-vocabulary question (measured, 2026-09-02).**
Both names sat in `annotator_agreement.py`'s `SECTION_8_TAGS`, so a second annotator following
this paragraph **literally** would pass A1's conformance gate and then fail §5.1 clause 9's set
comparison on every carve-out item. Recomputed against the 2026-08-29 cold run with that single
substitution applied: **`G` rises from 4/26 (DIAGNOSE) to 7/26 (REDESIGN), `G_disjoint` from 0 to
5** (`C02-04`, `C10-01`, `C13-02`, `C14-01`, `E01-01`). One stale sentence carried more
`G`-inflation than every disagreement the run actually observed. This is also the **only**
alternative-encoding pair in §8's vocabulary — every other pair was checked and is disjoint by
construction, `within_preposition`/`relative_trigger_preposition` explicitly so under §8.9's own
boundary paragraph — which is why it is a one-line fix rather than a taxonomy problem.

**The cost, stated rather than hidden:** the annotated obligation is *stronger* than the
one the contract imposes — a flat prohibition where the document has a conditional one.
That is deliberate. The alternative, excluding the class, makes v1's single largest
representational gap invisible in the gold set, and §8's standing posture is that a known
gap is annotated honestly and measured, never avoided. Every such item is tagged, so the
overstatement is always recoverable from the data rather than baked silently into a score.

---


### 8.4 Mutual obligations (v0.16 — REVIEWER-CONFIRMED)

*"Provider and Recipient shall **each** use its commercially reasonable efforts to prevent
… into the Systems of the other Party."* Both parties bear the same duty toward each
other. IR v1's `Obligation` holds exactly one `obligor` and one `obligee`, with a CHECK
that they differ, so a reciprocal duty **cannot be represented at all**.

**Rule.** Annotate **one** item, tag `known_gaps` gains `"mutual_obligation"`, and record in
`annotator_notes` that the reciprocal direction is structurally unrepresentable.

**The party *value* is not decided here — §3.5.1 decides it (v0.28).** This section's v0.16
text said *"first-named party as `obligor`"*, a value instruction inside a tag rule. That
instruction had no referent when the subject was a collective reference, which is the defect
§8.4.1 was written to repair; at v0.28 the value logic moved to §3.5.1 and only the tag
remains here. §8.4 answers one question: **is a second, reciprocal duty lost?**

**Why not two items.** The two duties genuinely *are* separable — different obligor,
different obligee — so §8.3's "split when genuinely separate" principle points that way.
But both would carry a byte-identical span and collide under §4.1's IoU alignment, the
same wall §8.3 hit. The tag preserves the fact at no cost to alignment.

**Why not just let it fall into `UNRESOLVED_PARTY`.** Annotating `obligor` as the verbatim
"Provider and Recipient" would resolve to nothing and land in the generic unresolved-party
bucket, hiding a *representational* gap inside what looks like a *resolution* failure.
Mutual obligations are a common real-world contract pattern; that they cannot be expressed
in IR v1 is a diagnostic fact about the IR, and it should be countable.

### 8.4.1 Collective-reference parties — "the Parties" (v0.19 — REVIEWER-ADJUDICATED)

**Motivating case** — `C04-117` sentence 3: *"…then **the Parties** will negotiate in good
faith which Party(ies) is/are responsible for payment of such Third Party royalties…"*

**The defect this fixes.** §8.4 instructs the annotator to put the **first-named party** in
`obligor`. That instruction assumes the span names the parties individually, as its own
motivating case did (*"Provider and Recipient shall each…"*). A span whose subject is the
collective *"the Parties"* names **no** party, so the instruction has no referent, and
every other available value is blocked by a **stronger, more general** rule:

| Option | Blocked by |
| :--- | :--- |
| `obligor: "Bellicum"` (the agreement's first-named party) | §3.5: *"Do not infer a party from elsewhere in the document."* |
| `obligor: ABSENT` | Factually false — a subject **is** stated; `ABSENT` means *not stated*, and misusing it makes the item indistinguishable from a genuine absent-party item |
| §3.5.1's `obligor_accept_set` | No individual names exist in the span to put in the set |

**Rule — moved to §3.5.1 step 1 branch 2 at v0.28.** This section is retained for its
measurement table below and its `ABSENT`-is-false reasoning, both of which §3.5.1 cites;
`C04-02`, `C14-01` and `C14-02` cite `8.4.1` and those citations must resolve. The rule as
originally written, now living in §3.5.1: annotate the slot with the collective reference
**verbatim as it appears**
(`"the Parties"`, `"the parties"`, `"both Parties"`, and the **distributive** `"Each party"`
/ `"Each Party"`), per §3.5's as-it-appears rule. The distributive form was measured
separately at **4.7% of pool segments** and is covered by the identical rationale: it names
no party either, so `obligor` holds it verbatim.
`obligor_accept_set` stays empty — there are no names to accept. §8.4's `known_gaps` entry
`"mutual_obligation"` still applies whenever the duty is reciprocal; the tag, not the
`obligor` value, is what keeps the representational gap countable, which is exactly the
answer §8.4's own *"why not `UNRESOLVED_PARTY`"* objection was asking for.

**Scope of §8.4's original instruction, restated:** *"first-named party"* governs spans
that name the parties individually. It does not govern collective references, which this
section covers.

**Measured frequency, taken before the rule was written** (§8.6's discipline):

| Form | sentences | segments | % of pool | hard-stratum segments |
| :--- | --: | --: | --: | --: |
| Collective `the Parties` + modal | 132 | 114 | **7.4%** | 42 |
| Distributive `Each Party` + modal | 97 | 73 | 4.7% | 25 |
| Named conjunction `X and Y` + modal (§8.4 / §3.5.1's shape) | 54 | 49 | 3.2% | 8 |
| `both Parties` + modal | 3 | 3 | 0.2% | 2 |

Spread across ≥6 documents (C04 24, C05 24, C14 15, C17 11, C02 10, E03 9), so it is a
property of contract drafting, not of one document. Precision on a seeded 12-sentence
sample: 12/12 genuine. Proportionally this is ~7 of the 100 gold items.

**OPEN SUB-QUESTION — RESOLVED v0.47, REVIEWER-RULED. The decision procedure is §8.4.2 below;
the statement of the question is retained unedited because §8.4.2's rule is only legible against
it.** Recorded not resolved from v0.19 to v0.46 — seven versions, and queued nowhere until
§10.1 F7. Only **31 of
132 (23%)** of collective-reference sentences carry any reciprocity marker (`each other`,
`the other Party`, `between the Parties`, `mutually`, `jointly`). For the remaining 77% —
*"The Parties shall cooperate in good faith to resolve such dispute"*, *"The Parties shall
share equally any applicable arbitration fees"* — the span states neither the co-obligor
names nor an obligee, so **§3.5.1's discriminating test (is the co-obligor also the
obligee?) is undecidable at span scope**. That makes 23% a **lower bound** on the mutual
share, not a split, and it means the `mutual_obligation` tag's own count is
systematically under-stated for this form. Batch 3 should either supply a decision
procedure or record that the discrimination is not makeable from the span alone.

### 8.4.2 The `mutual_obligation` trigger — a decision procedure (v0.47 — REVIEWER-RULED)

**This closes §8.4.1's open sub-question with the first of the two answers it permitted — a
decision procedure — rather than the second (record the discrimination as not makeable).** The
ruling adopts **§3.5.1's own discriminating test, *"is the co-obligor also the obligee?"***, as the
definitive trigger, in place of the party-slot **form** that had been triggering it in practice.

**The tag fires iff all three hold. Evaluate in order; the first failure ends it.**

| | test | why it is there |
| :-- | :--- | :--- |
| **(a)** | `modality` is duty-bearing — `MUST`, `MUST_NOT`, `SHOULD`, **never `MAY`** | §8.4's gap is a **lost second duty** (*"one obligor, one obligee, CHECK they differ"*). A symmetric **right** loses nothing when annotated once |
| **(b)** | the obligation **binds two or more parties** — read from the `obligor` slot for the collective and distributive forms (`"the Parties"`, `"Each party"`, `"Either party"`), **or from the span** for the named-conjunction form | §8.4's own *"first-named party"* rule deliberately collapses `"Provider and Recipient shall each"` into a single `obligor` slot, so for that form the slot **cannot** carry the multi-party fact and the span must be read instead |
| **(c)** | the **`obligee` is that same counterparty** — a reciprocal reference (`"the other party"`, `"such other party"`), or the **named** co-obligor | This is §3.5.1's test proper. `obligee: ABSENT` is a **failure**, not a deferral: with no obligee stated the discrimination is undecidable at span scope, which is exactly the 77% §8.4.1 measured |

**Worked, against all four locked items that carry the tag plus the one near-miss.** These are
the known-answer cases the procedure was checked against before it was written down, per
Standing Principle 7 — and the first two drafts of it failed here rather than in review.

| item | (a) | (b) | (c) | tag | note |
| :--- | :-- | :-- | :-- | :-- | :--- |
| `C17-01` | `MUST` | span: *"Provider and Recipient shall **each**"* | `"Recipient"` — the named co-obligor | **fires** | §8.4's original named-conjunction shape; both annotators agreed |
| `C14-01` | `MUST` | `"Each party"` | `"the other party"` | **fires** | gold's reading confirmed |
| `C14-02` | `MUST` | `"Each party"` | `"such other party"` | **fires** | |
| `C04-02` | `MUST` | `"the Parties"` | **`ABSENT`** | **does not fire** | **the item that changes.** Restamp pending — §10.1 F7 |
| `C13-03` | **`MAY`** | `"Either party"` | `"the other party"` | **does not fire** | (b) and (c) both pass; **(a) is the only thing excluding it** |

**`C13-03` is why (a) exists, and it was found by the re-check rather than by the ruling.** Its
slots are structurally identical to `C14-01`'s, so a two-part test on (b)+(c) alone would have
pulled it in and silently contradicted a locked, reasoned annotation — its own notes already
argue the point: *"unlike section 8.4's mutual_obligation gap (which protects against silently
losing an entire SECOND duty when naming only one obligor of a MUST), naming 'Either party'
verbatim already fully communicates the symmetry within the value itself."* (a) is that argument
promoted from one item's notes into the rule.

**A marker regex is NOT the test, and saying so is load-bearing.** §8.4.1's five reciprocity
markers (`each other`, `the other Party`, `between the Parties`, `mutually`, `jointly`) are a
**recognizer for (c)'s reciprocal form only**. Grepping them over the span instead fails in both
directions, measured on this set: it **fires on `C04-02`**, whose span contains *"the Parties
**mutually** agree"* inside the `if`-clause — a marker attached to the **trigger**, not to the
duty — and it **misses `C17-01`** entirely, whose reciprocity is carried by a named conjunction
with no marker word at all. Both are Standing Principle 7's shape: a detector that looks
authoritative while measuring something adjacent to the question.

**Consequence for the tag's own count, stated rather than left implicit.** §8.4.1 called 23% a
lower bound and warned the tag is *"systematically under-stated for this form."* Under this
procedure that is no longer a defect to be corrected — it is the **definition**: the collective
form with no stated obligee does not carry the gap, because the second duty is not demonstrably
there to be lost. The count becomes interpretable at the price of being narrower.

**Re-check across all prior batches, per §10.** Run over all 32 locked items: **exactly one
changes** — `C04-02` loses the tag. `C17-01`, `C14-01` and `C14-02` keep it; `C13-03` stays
untagged; no untagged item gains it. **Not restamped here** — `C04-117` is cassette-backed, so
this is a conforming event with §22's blocker attached, batched into the freeze pass at §10.1 F7.

---

### 8.6 `WITHIN` preposition gap (v0.17)

**Motivating case** — `C17-066`: *"The Company and RGHI will use all commercially
reasonable efforts to obtain **within 24 months following the Commencement Date** … any
needed consent…"*

**This is NOT §8's parenthetical-numeral gap, and NOT scope/location "within".** The
numeral is bare (`24`), so §8's stated cause — *"`_WITHIN_RE` requires a bare digit"* —
does not apply, and both phrasings are duration usages. The failure is the **preposition
following the duration**, verified against the production regex:

| Phrase | `_WITHIN_RE` |
| :--- | :--- |
| `within 24 months of the Commencement Date` | MATCH |
| `within 24 months following the Commencement Date` | **NO MATCH** |
| `within twenty-four (24) months of X` | NO MATCH — the separate §8 gap |

**Measured across the pool**, the word following `within N <unit>`: `of` 40, **`after` 34,
`from` 17, `following` 8**. Only `of` matches — the rejected prepositions outnumber the
accepted one 59 to 40. Restricted to bare numerals, where §8 cannot explain the failure,
there are **7 confirmed instances across 7 documents** (`C09`, `C13`, `C14`, `C17`×2,
`E08`).

**Rule.** `temporal: null`, `known_gaps: ["within_preposition"]`. **`underspecified` per §3.9 —
not set by this rule (v0.28 — struck).** Same defect and same reasoning as §8.1's struck clause.

**Why its own tag rather than §8's row.** Different cause, different fix: this is a
one-word regex widening (`of|after|from|following`), while the parenthetical case is a
genuine numeral-parsing problem. Filing them together would inflate the parenthetical
gap's measured size with cases that are trivially fixable — and §11's scope decision is
being made against that number.

---

### 8.9 `RELATIVE_TO_TRIGGER` preposition gap (v0.28)

**Motivating case** — probe `E05-019` (`apps/brain/evals/probes/E05-019.json`):
*"Escrow Agent shall be indemnified and held harmless by WHDX and 11i **upon demand by the
Escrow Agent**…"*

`ir_compile._RELATIVE_RE` is `^(before|after)\s+(.+)$` — **two prepositions.** Anything else
falls through all five temporal forms and returns `None` → `UNMAPPABLE_TEMPORAL`, which
**rejects the whole candidate**, not merely its temporal. Verified against the production
classifier by execution, not inferred:

| `temporal_raw` | `_classify_temporal` |
| :--- | :--- |
| `after the receipt by the Escrow Agent of notice` | `AFTER "the receipt … of notice"` |
| `after demand` | `AFTER "demand"` |
| `upon demand by the Escrow Agent` | **`None`** |
| `immediately upon the termination` | **`None`** |

**Measured across the pool before the rule was written** (§8.6's discipline), trigger-noun
alternation `receipt|demand|request|termination|expiration|occurrence|delivery|notice|
execution|completion`:

| preposition | `_RELATIVE_RE` accepts | segments | % of pool |
| :--- | :--- | --: | --: |
| **`upon <trigger>`** | **NO** | **92** | **5.9%** |
| `after <trigger>` | YES | 29 | 1.9% |
| `prior to <trigger>` | **NO** | 11 | 0.7% |
| `following <trigger>` | **NO** | 11 | 0.7% |
| `before <trigger>` | YES | 2 | 0.1% |
| `on <trigger>` | **NO** | 0 | 0.0% |
| `at <trigger>` | **NO** | 19 | 1.2% |
| `as of <trigger>` | **NO** | 3 | 0.2% |

**Accepted 31 segments, rejected 133 — a ratio of 4.29 : 1.**

*Data correction (probe pass 3, `C06-113`): the last two rows were missing from the original
table, which reported **111 rejected, 3.58 : 1**. `at the conclusion of the Sale` and
`as of the Sale Termination Date` both return `None` from `_classify_temporal`, confirmed by
execution. **This is a correction to the evidence, not to the rule** — the rule already reads
"the direction the **preposition expresses**", with `upon`/`following`/`on`/`prior to` given as
examples rather than an exhaustive list, so `at` (→ `after`) and `as of` (→ `after`) were always
covered. The undercount was in the measurement, and it understated the gap by 20%.* For scale, §8.6's
`within_preposition` gap, which has its own tag and section, was sized at **7** confirmed
instances. This is the same defect class in the sibling temporal form, an order of magnitude
larger.

*Second data correction (v0.34, from the compile-stage bottleneck investigation — again a
correction to the **evidence**, not to the rule, on the identical ground the probe-pass-3 note
above states). Two rows of the table above are wrong, and both were exposed by real model output
rather than by re-reading the pattern:*

| row | table says | measured v0.34 | note |
| :--- | :--- | :--- | :--- |
| `on <trigger>` | **0 segments, 0.0%** | **5 segments (0.3%)** | not a genuine zero — an undercount |
| `until <trigger>` | **absent entirely** | **7 by the narrow alternation; 72 (4.7%) for `until <anything>`, every one carrying a modal** | never measured |

*The measurement is corroborated against known answers before its two divergent rows are trusted
(Standing Principle 7): re-run over the same 1,547-segment pool it reproduces this table's `upon`
row at **90** against 92 and its `after` row at **29** against 29 exactly. `until` is covered by the
rule as written — it expresses a `before` direction — so no rule text changes; it simply was never
counted. The `on` row's undercount has a identifiable cause: the trigger-noun alternation
(`receipt|demand|request|termination|…`) cannot see the shape that actually occurs, which is
`on the <Defined> Date` — measured separately at **12 segments (0.8%)**, and the exact construction
in locked item `C04-03` (`"on the Delivery Date"`). Together `on the <X> Date` and `until` are
**77 segments (5.0%)**, comparable to `upon`'s 5.8%, so neither is a corner case.*

*Observed in the cassettes, which is how this surfaced: `on <trigger>` 3 times (`C04-087`, all
three runs) and `until <trigger>` 3 times (`C04-117` ×2, `C02-021` ×1). **A consequence worth
stating because it is not obvious from the rule: `C04-03`'s gold answer is unreachable under EITHER
reading.** Gold annotates it `BY` with the alias `the Delivery Date`; under this section's rule the
form is arguably `RELATIVE_TO_TRIGGER(after, …)`. Neither is producible — `BY` requires a literal
`by` and `RELATIVE_TO_TRIGGER` a literal `before`/`after`, and the span says `on`. That is the same
structural class as §8.3.1's v0.31 finding and §15.5's F7, and it means §8.9's "Cost: zero locked
items" line below is true as a statement about **tags** while being misleading as a statement about
**exposure**. No item is restamped and no rule changes; recorded so the next reader of that line
knows what it does and does not claim.*

**Rule.** Annotate `RELATIVE_TO_TRIGGER` with the direction the preposition expresses
(`upon` / `following` / `on` → `after`; `prior to` → `before`) and the trigger verbatim.
`known_gaps` gains **`relative_trigger_preposition`**. `underspecified` per §3.9 — trigger 3
fires regardless, since `symbols.resolve_trigger()` returns `None` throughout v1.

**Expected v1 outcome: `UNMAPPABLE_TEMPORAL`, a loud failure** visible in criterion 1b. This
class sits on §15.3's **loud** side — unlike `exception_unsupported`, which §8.2 records as
failing silently.

**Why its own tag rather than §8.6's.** Different regex, different cause, different fix:
§8.6 is `_WITHIN_RE` requiring the preposition `of` *after a duration*; this is `_RELATIVE_RE`
requiring the phrase to *begin* with `before` or `after`. Filing them together would inflate
§8.6's measured size with a differently-caused class — the identical objection §8.6 itself
raised against folding into §8's parenthetical row.

**It also breaks a rule already in force.** §15.5's `"Immediately upon X"` bullet (v0.4,
still `PENDING CONFIRMATION`, in force since before batch 1) instructs `RELATIVE_TO_TRIGGER`,
a form the compiler cannot produce for `upon`. Every item annotated under that bullet is a
guaranteed `MISSED`, and v0.28's decision 6 extends the bullet's reach across the 92-segment
`upon` class. That is not an argument against decision 6 — it is the reason this gap needs a
tag, so the loss is countable rather than dissolving into an unattributed `MISSED` count.

**Widening `_RELATIVE_RE` is deferred, not rejected** — the same treatment §11 gave
`_WITHIN_RE`, and the third time in this consolidation pass that this reasoning has been
applied (§11's original `_WITHIN_RE` decision; decision 6's rejection of restricting §15.5 to
compiler-friendly prepositions; here). Revisit only once paired criterion-1b numbers exist.
Changing the classifier first would tune the compiler to the corpus it is about to be graded
on and destroy the baseline that makes the widening's value measurable.


## 9. The two criteria have different denominators

- **Criterion 2 (≥80%)** — `FULLY_CORRECT` / 100 gold items.
- **Criterion 1b (≥90%)** — of candidates that survive grounding and reach the compiler,
  the fraction producing a typechecked `Obligation` within ≤2 repairs, over all 28
  documents.

**1b is gameable in isolation**: a prompt emitting fewer, safer candidates scores higher
while extracting less. **1b is therefore always reported paired with the `MISSED` count.**

**1b is also always reported twice (v0.8, §11):** once over all items, once excluding
items carrying **any** `known_gaps` entry. Both are published together; neither is quoted
alone. The split is computed mechanically from the `known_gaps` field, not reconstructed by
hand.

**The exclusion test is membership, never a count (v0.22).** An item is excluded from the
without-gaps denominator when `len(known_gaps) > 0`. A two-tag item is scored **identically**
to a one-tag item: `known_gaps` appears nowhere in §5's conjunctive predicate, so it changes
which denominator an item is reported in, never whether it is `FULLY_CORRECT`.

**Per-tag figures are non-exclusive and MUST NOT be summed (v0.22).** Each is reported as
*"N items carry this tag."* Because one item may carry several, the per-tag counts overlap
and their sum exceeds the number of tagged items. Summing them to obtain a tagged-item total
is a reporting error, and it is named here because a list makes it possible for the first
time. Same "report alongside, never fold in" discipline as §15.4.

Both numbers are reported alongside: the spurious-extraction count over zero-obligation
segments, the share of items correctly `underspecified` (so "compiled faithfully" is not
misread as "resolved"), and the prompt/model/grammar versions in force.

### 9.1 Criterion 2's dual denominator — **IN FORCE as of v0.33 (was RECOMMENDED at v0.26)**

~~**Criterion 2 needs the same dual denominator, and does not yet have it (v0.26 — RECOMMENDED,
NOT YET APPROVED).**~~ **SUPERSEDED AT v0.33 — approved and in force. The v0.26 text is struck
in place rather than deleted, per this document's own corrections-are-new-text discipline; the
reasoning below is what is operative.**

**The rule.** Criterion 2 is reported **twice**, always together, neither quoted alone:

| denominator | scope | standing |
| :--- | :--- | :--- |
| `len(known_gaps) == 0` | items IR v1 can represent faithfully | **PRIMARY** — this is criterion 2 |
| all items | every locked item, tagged or not | **reported alongside**, never as the criterion |

This is the treatment §11 already gave criterion 1b, applied to criterion 2. The split is
computed mechanically from `known_gaps`, by membership never by count (see the v0.22 rule
above). `known_gaps` still appears nowhere in §5's conjunctive predicate: it changes which
denominator an item is reported in, never whether it is `FULLY_CORRECT`.

**Two independent grounds. Either alone is sufficient; they are recorded separately because
they fail differently and a future reader should not think the decision rests on one number.**

**Ground 1 — reachability (v0.26, the original argument).** At the measured
structurally-uncompilable rate (7 of 18 locked items, 38.9%, 95% CI [20.3%, 61.4%]; 9 of 18
if `corpus_artifact_in_span` spans are counted), criterion 2's ceiling over all items is
roughly **39–61%**, so blueprint §21's **≥80% bar is arithmetically unreachable over that
denominator at every point in the measured interval**. Not a sample-size problem; no target
size fixes it. *This ground is contingent: it holds only while the measured gap rate holds,
and its interval is wide.*

**Ground 2 — validity (v0.33, new, and it does NOT depend on the 38.9% rate).** The all-items
denominator can count an IR that is **knowingly not a faithful representation of the
obligation** as `FULLY_CORRECT`. This is not hypothetical and not marginal:

- **It is already happening.** Two of the five items in the first scoring run's numerator carry
  a tag — `C03-02` (`compound_action`, the second verb unrepresented) and `C04-02`
  (`mutual_obligation`, the reciprocal direction lost). Both IRs are **incomplete**: they
  under-report a duty. A monitor built on them misses a real breach.
- **The worse direction is one comparison rule away.** `C14-01` fails today on `object_class`
  alone (`taxes` against an accept-set holding `tax`). Under §5 clause 5's number rule (v0.33)
  it becomes `FULLY_CORRECT` and enters the all-items numerator — measured, 27.8% → 33.3%,
  the entire `+1` being that item. Its IR is **overstated**, not merely incomplete: §8.2's own
  words, *"the annotated obligation is stronger than the one the contract imposes."* A monitor
  built on it flags a breach the contract expressly exempts.

**Why that is a validity failure and not a caveat.** §8.2 defends the carve-out-free annotation
convention on exactly this promise — *"Every such item is tagged, so the overstatement is
always recoverable from the data rather than baked silently into a score."* A denominator that
does not read the tag **is** baking it into the score. The convention was sound; the reporting
layer was not keeping its half of the bargain. Ground 2 closes that, and it would still hold
if the gap rate were 5%.

**What this does NOT do.** It does not change any annotation rule, restamp any item, or alter
§5's predicate. Items keep their `v0.28` stamp, `run_scoring.guideline_version_from_items()`
keeps returning `v0.28`, and **no cassette goes stale** — the same footing as v0.29/v0.30.

**Ceiling.** §9 asks for "the expected all-items ceiling stated in advance." None is stated:
the tag-derived 39–61% figure was shown wrong item by item during the consolidation pass (most
tagged items compile fine), so publishing it would quote a number already known unsound. The
report states tag counts and the observed rate and says explicitly that no per-item
reachability ceiling has been computed (`report.py` G4).

**Inline disclosure is mandatory (v0.33).** Wherever the criterion-2 figures appear, any
numerator item carrying a non-empty `known_gaps` is named **on the spot**, split into
*overstating* gaps (`exception_unsupported` — the IR claims more than the contract) and
*incompleteness* gaps (`compound_action`, `mutual_obligation` — the IR claims less). Not a
footnote: the same on-the-spot discipline §6.1 already requires for a short run, for the same
reason — a reader who does not reach the methods section still gets the caveat. Implemented as
`report.py` G6.

### 9.2 The v0.48 freeze-pass batch MOVES THE IN-FORCE DENOMINATOR: 8 → 9 (§10.1 F7)

**Stated at the top of §9 rather than in a note, because it changes this phase's own headline
acceptance figure.** F7's ruling (§8.4.2) removes `mutual_obligation` from `C04-02`, leaving its
`known_gaps` **empty**. §9.1's in-force criterion-2 denominator is `len(known_gaps) == 0`, so the
item **enters** it.

| | before v0.48 | after v0.48 |
| :--- | :--- | :--- |
| in-force denominator (over `run_scoring`'s single-stamp v0.28 set) | **8** | **9** |
| in-force criterion 2 | `3/8 = 37.5%` | **`3/9 = 33.3%` — RESOLVED v0.49** |

**RESOLVED v0.49.** `C04-117` was re-recorded live (the narrow §10.1-precondition-2 path, not a
full §10 conform — see the v0.49 changelog entry above) and scored by pure replay: `C04-02`'s
three runs are `PARTIAL`/`MISSED`/`MISSED`, modal `MISSED`, never `FULLY_CORRECT` on any run.
**The numerator holds at 3. In-force criterion 2 is `3/9 = 33.3%`; `4/9 = 44.4%` is closed, not
merely undecided.** The 8 → 9 move itself is arithmetic over the locked items and was computed,
not estimated: the clean items were `C03-01`, `C03-03`, `C11-01`, `C22-01`, `E07-01`, `C02-01`,
`C02-02`, `C02-03`, and `C04-02` joins them. **Do not quote `3/8 = 37.5%` anywhere after v0.48** —
it understates the denominator of the very criterion §21 grades this phase on — **and do not
quote `4/9 = 44.4%`** — that branch is now measured shut, not open. This figure still carries the
mixed-stamp caveat stated in the v0.49 changelog entry: it is computed over a genuinely
guideline-mixed 18-item set (`v0.28×16`/`v0.48×2`), not the single-stamp population a full §10
conform would produce.

**Direction of the change, stated so it is not read as bad news or good.** The denominator grew
because an item stopped claiming a v1 gap it could not demonstrate — the instrument got *more*
honest, and a larger denominator on the same numerator reads as a *lower* percentage. That is the
correct behaviour of a dual denominator, not a regression. §9.1's ground 2 says so in terms: a
denominator that does not read the tag bakes the gap into the score; one that reads a tag which
should never have fired does the same thing in reverse.

**The other three entries in the batch leave the denominator untouched, checked rather than
assumed.** `E01-01` (F8) already carried `exception_unsupported`, so `len(known_gaps)` was already
non-zero; `C10-01` (F11) already carried two tags; `C04-04`/`C04-05` (F3) are batch-3 items outside
the single-stamp scoreable set entirely, and their `known_gaps` stay `[]` either way.

**Inline-disclosure consequence, and it is why F10 was folded into this batch.** F8 and F11 each
add `action_not_in_taxonomy`, which `report.py`'s `GAP_DIRECTION` did **not** classify — so the
mandatory on-the-spot split above would have reported the set's two three-tag items as
`UNCLASSIFIED` at exactly the moment they became numerator-relevant. It is now classified
**INCOMPLETENESS**, on the same ground as `compound_action`: §8.8 puts the *nearest* verb in
`action` and the real verb is lost, so the IR claims less than the document. Five tags remain
deliberately unclassified and `report.py` now names them and says why — they turn on **F9**'s open
`kind`-axis question, which this batch does not decide.

See §19.5 for why the 100-item target is a working figure rather than a derived one, and
CLAUDE.md's debt list for the compile-stage loud-path fix (`ir_compile` routing a carve-out to
`compile_quarantine` instead of `IF`) that would make the spec-compliant behaviour reachable at
all — tracked against the **Normalizer checkpoint**, deliberately not built as part of this
amendment.

---

## 10. Versioning and freeze

**PROCESS NOTE — close-out consistency check (added 2026-08-23).** Any session that edits
this document runs a **header/changelog consistency check before it ends**: re-read the
`**Version:**` line, the `**Status:**` line, and the newest changelog entry, and confirm each
still describes the document as it now stands. Mid-pass wording ("in progress", "no rule
adopted yet", "no items have been annotated") is accurate when written and becomes false the
moment the pass completes — and nothing in the normal editing flow revisits it.

**This document has carried a false header claim three times.** §19.3 records the first two;
the third was `v0.28`'s own header and changelog still reading *"no v0.28 rule is adopted"*
and *"none has been written into a rule section"* after all 16 proposals had been ruled and
written into live sections — contradicted by §20's own status line and by §3.5.1, §3.8.1 and
§8.9 sitting in the file. It was caught by the *next* session's verification step, which is
one session too late.

The check costs a minute. **Live status statements are corrected in place; dated records are
struck with a superseded marker and kept** — §19.3's distinction, which is what makes this a
mechanical check rather than a judgment call.



- v0.1 → amended freely during batches 1–3.
- **Freeze after batch 3 (30 items).** Batches 1–3 are conformed to the frozen version.
- Post-freeze amendments require a logged re-check of the amended rule across all prior
  batches, recorded in the manifest.
- Every item stamps its `guideline_version`. If held-out disagreements cluster in
  pre-freeze batches, that is diagnostic — the freeze worked.
- **Consolidation pass inserted before batch 3 (v0.26).** The conforming step above is run
  **now, at 18 items**, rather than being deferred to the freeze. Measured debt: **154
  outstanding item × rule re-checks** (§19.3), of which 139 clear mechanically (§19.7).
  Deferring to the freeze would face an estimated ~390 in one tangle. The freeze itself stays after batch 3, unchanged: at the
  measured discovery rate (§19.2) freezing earlier would put ~82 items on the post-freeze
  path, where every amendment requires a logged re-check across all prior batches.

### 10.1 The freeze-pass queue (added v0.45) — one list, so nothing is tracked only in a session record

**Why this exists.** Work deferred to the freeze pass has been accumulating in five different
places — §3.4's bounded exception, §22.1's decision, CLAUDE.md's debt list, `RESULTS.md`, and
`OBJECT_CLASS_INVESTIGATION.md`'s ruling log — with no single list. Two of the entries below were
found in one afternoon by an invariant that had never been run, which is direct evidence that
"it is mentioned somewhere" is not tracking. **This table is the queue. An item deferred to the
freeze pass is added here, or it is not deferred, it is dropped.**

| # | item(s) | what has to be decided or done | cassette-backed? | source |
| :-- | :--- | :--- | :--- | :--- |
| **F1** | `C02-03`, `C11-01`, `C02-01` | **accept-set widenings**, already approved in principle under §3.4's bounded exception; all three keep scoring as failures until the pass | yes | §3.4 |
| **F2** | `C10-02` | **`obligor`/`obligee` are not verbatim against their own span** — gold has `"the Supplier"`/`"the Distributor"` where the span reads `"The Supplier"`/`"the distributor"`, in *opposite* directions. A §3.5 violation and an instance of the exact §21 R2 case-sensitivity trap. Restamp both slots | no | v0.45 re-validation; `RESULTS.md`'s 2026-09-01 correction |
| **F3** | `C04-04`, `C04-05` | **EXECUTED v0.48 — §4.3.2's ROOT CONSTRAINT.** §3.6.1 does not yield; §4.3.2's *root choice* does, and §4.3.2 now forbids a root that restates either half's own `action`. One premise of the conflict was false: §4.3.2 **recommends** its convention, it does not require it (§10.1.1 and `OBJECT_CLASS_INVESTIGATION.md` §11 both misstated this; corrected). Both halves restamped to `self_`/`third_party_regulatory_compliance`, both accept-sets widened monotonically. **F12 filed, not decided.** **DONE** | **NO — see the cassette correction below** | v0.45 re-validation |
| **F4** | `C14-02` | §22.1's **deliberately-retained** non-conformance under the superseded §8.3.1 v0.23 rule. Revisit only if §22's forcing function (a second independent conforming instance) has arrived — **F2 and F3 are candidates, and whether either counts is itself part of this item** | yes | §22.1 |
| **F5** | whole set | the **systematic accept-set breadth audit** (§3.6, v0.45), expanding F1 from three queued widenings. Carries §3.6's two hazards: monotone widening must not straddle a criterion-2 baseline, and every widening must be defensible from the span alone | mixed | §3.6, `OBJECT_CLASS_INVESTIGATION.md` Ruling 3 |
| **F6** | `C06-01`, `C13-01`, `C14-01` | the **depth convention** (§3.6, v0.45) — annotator-predicate scope only, **and blocked on a precondition**: §9.4's missing anchor field means any depth rule is unverifiable after authoring. Decide the precondition before the rule | no | §3.6, Ruling 4 |
| **F7** | `C04-02` | **EXECUTED v0.48, RE-RECORDED AND SCORED v0.49.** Ruled v0.47 (§8.4.2); restamp applied at v0.48. `C04-02` loses `mutual_obligation` (obligee `ABSENT`, so the discrimination is undecidable at span scope). **MOVES §9's IN-FORCE DENOMINATOR 8 → 9** — its `known_gaps` is now empty, so it enters the criterion-2 denominator; see **§9.2**. `C04-117` re-recorded live at v0.49 (3 runs, 4 calls) and scored: `C04-02` modal `MISSED` (`PARTIAL`/`MISSED`/`MISSED`), never `FULLY_CORRECT`. **Numerator resolved at 3 — criterion 2 is `3/9 = 33.3%`. DONE, fully closed.** | **yes** (`C04-117`, 3 runs — re-recorded v0.49, now stale against `C04-01` instead; see §22.3) | §8.4.2; v0.46 §8 review |
| **F8** | `E01-01` | **EXECUTED v0.48.** Ruled v0.47 (§8.3.2); restamp applied here. **The row as originally written understated the work: `E01-01` carried only `exception_unsupported` — `compound_action` had never been applied to it either — so the restamp adds TWO tags, not one**, reaching the three §8.3.2 requires. **DONE** | **yes** (`E01-047`, 3 runs — now stale) | §8.3.2; v0.46 §8 review |
| **F9** | whole set | **§8's tag vocabulary carries at least three different KINDS of thing under one flat set** — IR-representational gaps, corpus-text defects (`corpus_artifact_in_span`, which §8's own table says is *"not a v1 compiler gap"*), annotation-convention exceptions (`shared_subject_split`) and scoreability removals (`redacted_clause`) — and §9's `len(known_gaps) == 0` denominator treats all of them identically. Decide whether the vocabulary needs a `kind` axis before it gains more tags | mixed | v0.46 §8 tag-vocabulary review |
| **F10** | n/a — reporting layer | **PARTIALLY EXECUTED v0.48, scoped deliberately.** `action_not_in_taxonomy` is now classified **INCOMPLETENESS** — added in this batch *because* F8 and F11 apply that tag, so shipping them alone would have widened the gap while claiming to close a taxonomy one. **The remaining five live-use tags stay `UNCLASSIFIED` and `report.py` now names each and says why** (`corpus_artifact_in_span`, `shared_subject_split`, `redacted_value`, `within_preposition`, `relative_trigger_preposition`): each turns on **F9**'s `kind`-axis question, and assigning a direction now would be the very masquerade the reviewer filed F10 separately to prevent. **STILL OPEN for those five** | no | v0.46; §9.1, `report.py` G6 |
| **F12** | whole set | **§3.6.1 tests the `action` SLOT VALUE only, not `action_accept_set`** — its v0.44 screen swept `action`, `obligor`, `obligee` and `obligor_accept_set`, and the action accept-set was never in it. The co-variance argument that makes §3.6.1 a *correction* runs through the accept-sets, since §5 clause 2 tests **membership**, not slot equality. **Measured at v0.48: exactly ONE instance across the 32, and it is the same item before and after F3** — `C04-04`'s old slot `self_compliant_use` restated its accept-set member `COMPLY` (via `compliant`) just as its new slot does (via `compliance`), so exposure was **1 → 1** and F3 inherited the hazard rather than creating it. **A first pass reported zero; that was a stemmer miss (`complyance` ≠ `compliance`), the third nominalisation miss by that screen in one session.** Decide whether §3.6.1 extends to accept-sets. Retroactive reach, so it is a rule change, not a screen fix | mixed | v0.48 F3 ruling; §3.6.1 |
| **F11** | `C10-01` | **EXECUTED v0.48 — §8.8.2.** `defend` is ruled **NOT** defensibly mappable to `INDEMNIFY`, on corpus evidence: 33 sentences use it with no `indemnify`; `C03` disjoins *"failed to defend or indemnify"*; `C03` §(c) owes the defence *"whether or not … the allegations are meritorious"*; `C11` converts a failed defence duty into a payment duty. Branch 3 fires; `C10-01` restamped to three tags. `hold harmless`→`INDEMNIFY` untouched — **the two non-member verbs of one triplet land on opposite sides of the limb**, which is the first real exercise of §8.3's v0.47 non-mappability test. **DONE** | **NO — see the cassette correction below** | §8.3.2's re-check |
| **F13** | whole set (1 locked item today: `C17-02`) | **§8.6 and §8.9 give OPPOSITE instructions for the same structural problem, and §3.7's general rule sides against §8.6.** Both gaps are *a preposition the production regex does not accept* — §8.6 is `_WITHIN_RE` wanting `of`, §8.9 is `_RELATIVE_RE` wanting `before`/`after` — yet §8.6 rules **`temporal: null`** while §8.9 rules **annotate the form + trigger verbatim**, and §3.7 says *"Known-gap forms (§8) are annotated **normally**. Do not avoid them."* §8.6 is the outlier against both. It also makes gold assert `temporal: null` where the text plainly carries a timing phrase, which §3.7 permits *"only when the obligation genuinely carries no timing phrase"*. **The inconsistency is in the GUIDELINE, not in the annotation** — measured, both annotators follow each section literally and consistently: `within_preposition` → `null` (gold `C17-02`; cold `C17-066`, `C11-094`) and `relative_trigger_preposition` → the form (gold `C13-03`, `C22-02`; cold ×5). §8.9 (v0.28) was written explicitly as §8.6's sibling (*"Why its own tag rather than §8.6's"*) and never reconciled it. **Exposure: §8.6's own measurement — the word after `within N <unit>` is `of` 40 vs `after` 34 / `from` 17 / `following` 8, so 59 pool-wide occurrences sit on the rejected side.** Decide which treatment governs; if §8.9's, §8.6's rule line and `C17-02` both move. **NOT a prerequisite for any escalation** — surfaced by the cold annotator, who flagged the tension in `C11-094` item 2's notes, resolved it per §8.6 as literally written, and applied that resolution to `C17-066` too for consistency | yes (`C17-066`, `C11-094` both cassette-covered) | 2026-09-05 escalation re-read; `holdout/C14_076_INVESTIGATION.md` §7.4 |
| **F14** | whole set (13 locked items carry an `ABSENT` slot today: **2 on the obligor slot** — `C04-03`, `C14-05` — and 11 on the obligee slot) | **THE PROMPT NEVER STATES THAT AN EMPTY ALIAS IS PERMITTED, AND §5 CLAUSE 3 IS MEASURING THAT OMISSION RATHER THAN EXTRACTION QUALITY.** §5 encodes "this party is absent" as an `UnresolvedParty` carrying an empty alias (`score.py`'s ABSENT branch requires `norm(pred.alias) == ""`), but `prompts/extraction/v3.yaml` states **no rule permitting an empty alias anywhere**. Its only signal is one worked example carrying `"obligee_alias": ""`, with **no obligor counterpart** — and the emission split follows exactly: across all 81 candidates in the 35 gold cassettes, `obligee_alias` is empty **40/81 (49.4%)** and `obligor_alias` is empty **0/81 (0.0%)**, Wilson₉₅ upper bound **4.53%**. §3.5 already called the empty-obligee behaviour *"undesigned behavior, not a chosen rule"*; the measurement shows the undesign is **one-sided**. **Not a capability gap — verified by execution:** a both-`ABSENT` candidate grounds (`_is_grounded_substring` returns `True` on an empty needle, by design), compiles to `MUST "" PAY "" …`, and parses to `UnresolvedParty(alias='')` on both slots, so the ABSENT branch is reachable and the 0/81 is **behavioural**. Decide whether the prompt gains an explicit empty-alias instruction and an obligor worked example. **Tier C — a `prompt_version` bump stales all 35 gold cassettes at once and `C17-021` run 3 is unobtainable (§6.1) — so it is bundled with the already-approved-and-never-run `v4` `condition_raws` probe rather than taken alone**; whether the wording moves the 0/81 is a fact about `openai/gpt-oss-120b`, settleable only live. **NOT a prerequisite for `C14-076`'s band-eligibility ruling, nor for candidate 2's field assignment**, which §3.5.3's rule text decides regardless of how this resolves | yes (all 35 stale on any bump) | 2026-09-05 §5 both-`ABSENT` investigation; `holdout/C14_076_INVESTIGATION.md` §8.2 |
| **F15** | whole set | **§5 EXCLUDES `missing_fields` FROM THE PREDICATE WHILE SCORING `underspecified`, WHICH §3.9 STATES *IS* `bool(missing_fields)`.** §5's own closing line reads *"`missing_fields` is **reported but excluded** from the predicate"*, and §3.9 states *"`typecheck.py` computes `underspecified = bool(missing_fields)`"* — so clause 8 scores the boolean of the field clause-by-clause scoring deliberately drops. **Measured, not argued: across the 24 locked items whose documents carry a committed §21 R3 registry, `underspecified` is predicted with ZERO mismatches by *NOT(obligor resolves AND obligee resolves AND temporal is null)*.** Clause 8 is a **function of clauses 3/4/6's inputs**, not an independent eighth check. **Sharpest on a partyless span, where it is not merely dependent but GUARANTEED:** grounding requires each alias to be a substring of the span, no substring of a partyless span can resolve, so `underspecified` is `True` whatever the model emits and clause 8 passes **for any prediction, including a wholly wrong one** — verified against the real `C14` registry. Reaches the **62 partyless agentless performance passives (3.1% of modal-bearing sentences)** measured over the 10 registry-backed documents, and weakly the 19 currently-`underspecified` locked items. **TWO CANDIDATE RESOLUTIONS, NEITHER DECIDED HERE: (i)** keep clause 8 scored and disclose the guarantee at the point of use, the way §9 already discloses the dual denominator — cheapest, changes no number, but leaves a clause that cannot fail on a whole structural class; **(ii)** move clause 8 to reported-not-scored alongside `missing_fields`, making §5 seven scored clauses — internally consistent, but it is a **retroactive change to what `FULLY_CORRECT` means** and would move criterion 2's numerator, so it cannot be taken casually and interacts with §9's in-force denominator. **A first draft of the measuring script tested `ABSENT`-ness instead of resolvability and reported 4 spurious mismatches (`C14-01`, `C14-02`, `C02-04`, `C06-01` — every one a named but unresolvable party under §3.9 trigger 1); the looser predicate was the defect, not the data**, and the correction is preserved in the script rather than only in this row (Standing Principle 7). **NOT a prerequisite for `C14-076`'s band-eligibility ruling** | mixed | 2026-09-05 §5 both-`ABSENT` investigation; `holdout/C14_076_INVESTIGATION.md` §8.4; §5, §3.9 |

**Ordering note — SUPERSEDED v0.48, and its factual error is corrected below rather than edited
away.** It read: *"F3 is the only entry that is both cassette-backed and a rule conflict rather
than an item fix… F3, F7, F8 and F11 form one cassette-backed freeze-pass batch — their items
(`C04-139`, `C04-117`, `E01-047`, `C10-016`) restamp on any outcome that changes a field or a tag,
so §22's blocker attaches to each."* **Two of those four segments were never recorded.** It also
correctly noted that F7 and F8 were RULED (v0.47) with only the restamp outstanding while F3 and
F11 were not ruled at all — that distinction was right, and all four are now ruled and executed.

#### CASSETTE-BACKED TABLE CORRECTION (v0.48) — checked against the directory, not against this table

`apps/brain/evals/cassettes/gold/` holds **12 segments**: `C02-021`, `C03-192`, `C04-087`,
`C04-117`, `C11-094`, `C14-076`, `C17-021`, `C17-066`, `C22-048`, `E01-047`, `E03-005`, `E07-010`.
These are **exactly the 12 segments of the 18 v0.28 batch-1/batch-2 items**. **No batch-3 item has
a cassette.**

| entry | item(s) | segment | table said | actually |
| :--- | :--- | :--- | :--- | :--- |
| **F3** | `C04-04`, `C04-05` | `C04-139` | cassette-backed **yes** | **NO** — never recorded |
| **F7** | `C04-02` | `C04-117` | yes | **yes** ✓ |
| **F8** | `E01-01` | `E01-047` | yes | **yes** ✓ |
| **F11** | `C10-01` | `C10-016` | cassette-backed **yes** | **NO** — never recorded |

**This table contradicted a live rule section for two versions.** §3.6.1's own v0.44 text already
says, in terms, *"For `C10-01` and `C10-02` there is no prediction in existence — `C10-016` was
never recorded."* The queue was written from the session record rather than from the artifact, and
the artifact was right. **Consequence for how the batch was executed: §22's conforming blocker
attaches to F7 and F8 ONLY.** F3 and F11 were free — the same footing as F2 and F6 — and were run
first for that reason, so that the two genuinely blocked entries were the only ones staling
anything.

**A general lesson worth more than the correction, and it is Standing Principle 7's shape applied
to a document rather than to a detector.** §10.1 exists because *"it is mentioned somewhere"* is
not tracking — and this table, the fix for that, then carried a wrong fact about its own items for
two versions because nobody listed the directory. **Whenever a queue row asserts a property of an
artifact (`cassette-backed?`, run counts, stamps), that property is re-derived from the artifact at
execution time, never trusted from the row.** Both corrections in this batch — this one and F8's
two-tags-not-one — were found that way and by no other means.

**Execution order used (v0.48): F3 → F11 (free) → F8 → F7 (cassette-backed).** F10's
`action_not_in_taxonomy` classification landed with F8/F11 rather than after them, so that the two
rulings applying that tag never shipped into an unclassified reporting slot.

**Why F7–F10 exist as queue entries at all (added v0.46).** The §8 tag-vocabulary review was
triggered by `GAP_AGREEMENT_DESIGN.md` §4's `G = 6/31 → REDESIGN` band. **That trigger no longer
holds**: §5.1's two-predicate ruling recomputed `G` at **4/26 → DIAGNOSE**, so the review runs at
DIAGNOSE strength — *"§8's tag vocabulary needs review"* — and not at the REDESIGN strength it was
scoped under. The de-escalation is recorded rather than assumed, and it is the band that moved,
not the appetite. The review's one immediately-actionable finding is already closed in §8.2 above;
what remains is queued here instead of being decided in the same pass, because F7 and F8 are
reviewer rulings on genuinely two-sided criteria and F9 is a design question about the vocabulary
as a whole.

#### 10.1.1 F3 — §3.6.1 conflicts with §4.3.2's shared-root naming convention (found 2026-09-01, NOT resolved)

**The conflict, stated as a contradiction rather than as a defect in either rule.** `C04-04`
holds `action = USE` and `object_class = self_compliant_use`.

- **§3.6.1 (v0.44, RETROACTIVE)** forbids `object_class` carrying material whose content is
  already the value of clause 2. `use` is `USE`. The label violates it.
- **§4.3.2 (v0.37)** *requires* the `self_` / `third_party_` prefixes over a **shared root** so
  flow-down splits land on visibly parallel labels, and `OBJECT_CLASS_INVESTIGATION.md` §9.5
  leans on this very pair as the distinction head-only matching would destroy.

Both are live rules, both are cited by the item, and they cannot both be satisfied.

**It is asymmetric, and that is the diagnostic detail rather than a curiosity.** The sibling
`C04-05` holds `action = ENSURE` against `third_party_compliant_use` and is clean, because `use`
is not `ensure`. So §4.3.2's shared root collides with §3.6.1 on **exactly one half of a split
pair** — whichever half's own action verb happens to equal the root. **This is not specific to
`C04-04`: any future §4.3.2 split whose root is a taxonomy verb reproduces it**, which is why
this is filed as a rule conflict rather than as one item's label.

**Why the v0.44 §10 re-check did not catch it, consistent with its own caveat.** That screen
already carries a Standing Principle 7 note calling itself *"a lower bound, not a census"* after
missing `C10-02`'s `_listing`. This is a **second** miss by a different mechanism: the screen
looked for *restated material*, and `self_compliant_use` reads as a purpose-built §4.3.2 label
rather than as a restatement. Two independent misses by one screen is the stronger signal — the
screen's stated limitation is real and should not be relied on for the freeze pass.

**Three options, none pre-selected, and their costs differ enough that the choice is real.**

1. **Narrow §3.6.1 to exempt a root that §4.3.2 mandates.** Cheapest — no item changes, no
   cassette stales. But it puts a named exception into a rule whose whole force is that it is
   categorical, and §3.4's history with exactly that move is on record.
2. **Amend §4.3.2 to require a root that is not a taxonomy verb.** Keeps §3.6.1 categorical and
   fixes the class rather than the instance, but it is a **forward** rule that leaves `C04-04`
   needing a restamp anyway, and it constrains label choice on a field §3.6 otherwise leaves open.
3. **Restamp `C04-04` alone.** Treats it as one bad label — but the asymmetry argument above says
   it is not, so this is the option most likely to be re-litigated at the next flow-down split.

**Do not resolve this outside the freeze pass.** `C04-139` **is** cassette-backed, so an item
change here is a conforming event with §22's blocker attached.

#### RESOLVED v0.48 — ruled as option 2, with option 3 subsumed; and TWO factual errors above are corrected

**Ruling: §3.6.1 does not yield. §4.3.2's root choice does.** The amendment, both restamps and the
full reasoning live in **§4.3.2**, because what changed is that section's naming convention and
not §3.6.1. In short: §3.6.1 is a categorical correction of an *instrument* defect and stays
categorical — option 1 was refused because exempting the split half would bless the double-scoring
rather than remove it, and §3.4's history with named exceptions is on record. Option 3 is
subsumed: this section already observed that option 2 *"leaves `C04-04` needing a restamp anyway."*

**Error 1 — §4.3.2 does not *require* the shared root; it RECOMMENDS it.** The paragraph above
says *"§4.3.2 (v0.37) **requires** the `self_` / `third_party_` prefixes over a **shared root**"*.
§4.3.2's own heading reads *RECOMMENDED, not mandatory*, and its closing sentence repeats it.
`OBJECT_CLASS_INVESTIGATION.md` §11 carries the identical misstatement. **A recommendation cannot
contradict a categorical rule — it yields by construction — so the conflict was never between two
mandates**, but between §3.6.1 and one *root choice*. The substance survived the correction; the
framing did not.

**Error 2 — the option costs were stated against a false premise about cassettes.** *"`C04-139` is
cassette-backed"* is **wrong**: the segment was never recorded (see the cassette-backed table
correction in §10.1). F3 was therefore free, and was executed before the two genuinely
cassette-backed entries for exactly that reason.

**The asymmetry argument above is CONFIRMED, not weakened, and the class stays real at one
member.** A screen over all 32 locked items — validated against 12 known answers first, and
corrected twice before it was trusted — finds `C04-04` to be the **only** §3.6.1 slot violation in
the set. But the set's *other* live §4.3.2 application very nearly reproduced it: `C22-02` reduces
to one item only because §3.2.1 excludes its self-performance half, and `GRANT` **is** a taxonomy
verb, so had that half survived, `self_…_grant` / `third_party_…_grant` would have collided
identically. Filed as a rule, on one instance, for that reason.

**And a finding that made the ruling cheap.** `C22-02` was annotated at `v0.38` — *after* the v0.37
convention — with **no prefix, no shared root, and no citation of the convention at all** — and is
`reviewer_status: APPROVED`. The one other application of §4.3.2 declined its naming convention
outright and passed review. That is direct evidence the convention is optional in practice, which
is what a ruling making it yield needs.

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
- Every such item is tagged `known_gaps: ["within_parenthetical"]` so the two denominators
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

#### 15.3.1 The last paragraph above is FALSIFIED by measurement (v0.34)

~~This is **not** the §8 pattern… A vague-temporal mismatch would fail *silently* as a
`PARTIAL` in criterion 2 with no attribution.~~ **SUPERSEDED — struck in place per §19.3's
corrections-are-new-text discipline. The class fails LOUDLY, exactly like §8's.**

**What was measured.** Across the 35 recorded gold cassettes, whenever the model quotes the
vague qualifier into `temporal_raw` — which it does — `ir_compile._classify_temporal` returns
`None` and `UNMAPPABLE_TEMPORAL` **rejects the whole candidate**, so the item scores `MISSED`,
not `PARTIAL`. Five instances reached the classifier and **all five failed**:

| `temporal_raw` the model emitted | segment | outcome |
| :--- | :--- | :--- |
| `promptly` | `C14-076` run 2 | quarantined |
| `as soon as practicable` | `C17-021` run 1 | quarantined |
| `within a reasonable time after the Principal's death or mental incapacity` | `C11-094`, all 3 runs | failed first-pass; **rescued by the repair loop** |

*A sixth, `at reasonable intervals` (`C02-021` run 1), never reached the classifier — it was lost
at schema validation, so it is excluded from the five rather than counted.*

**SCOPED PRECISELY: §15.2's RULE IS UNAFFECTED. Only this section's CLASS PLACEMENT is wrong.**
The load-bearing argument for `underspecified = false` — §3.9's trigger list is closed,
`typecheck.py` returns `None` for an absent temporal without appending to `missing_fields`, and
annotating `true` would fail clause 8 on every such item — is untouched and still correct. The
two paragraphs above it stand. What is falsified is the separate claim about **which side of the
loud-versus-silent line this class sits on**, and therefore **what kind of loss it causes**: the
class costs **recall, loudly** (a `MISSED`, visible in criterion 1b) rather than **precision,
silently** (a `PARTIAL` with no attribution).

**Why that distinction is worth correcting rather than noting in passing.** §15.4 reports this
class as a headline count *alongside* criterion 2, on the premise that its cost is an
unattributed `PARTIAL`. If the real cost is a quarantined candidate, then §15.4's count does not
capture it, and the class is already visible in criterion 1b where §15.3 said it would not be.
§15.1 sizes the class at **12% of pool segments — roughly 8 of the 100 gold items** — so this is
not a corner case. §15.4 is **not amended here**: what to do about it is a decision, and this
section records the fact.

**No rule changed, no item restamped, no cassette stale.** Same footing as §8.9's two data
corrections: the evidence was wrong, not the instruction. Full investigation record in CLAUDE.md's
compile-stage bottleneck entry, including the finding this sits inside — that the temporal
classifier accepted **0 of 25** timing phrases that reached it on first pass, and that every
temporal in a typechecked obligation came from the repair loop.

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
- **Vague quantity + an explicit trigger → the trigger decides the form (v0.28).** Where a
  vague qualifier is immediately followed by a named triggering event, annotate
  `RELATIVE_TO_TRIGGER` with that direction and trigger, **and** record the vague word in
  `vague_temporal_phrase`. The timing *is* specified relative to an event; only its offset is
  vague.
  - *"within a reasonable time after the Principal's death or mental incapacity"* (`C11-01`)
    → `RELATIVE_TO_TRIGGER(after, "the Principal's death or mental incapacity")`,
    `vague_temporal_phrase: "within a reasonable time"`.
  - *"Promptly after the receipt … of notice"* → `RELATIVE_TO_TRIGGER(after, "the receipt …
    of notice")`, `vague_temporal_phrase: "Promptly"`.
  - *"Immediately upon X"* → `RELATIVE_TO_TRIGGER(after, "X")`,
    `vague_temporal_phrase: "Immediately"`.
- **"within a reasonable time"**, with **no** trigger → vague. `temporal = null`, §15.2
  applies, unchanged.

**This generalizes the v0.4 `"Immediately upon X"` bullet rather than competing with it.**
Through v0.27 that bullet and the `"within a reasonable time"` bullet decided the *same*
sentence differently, and `C11-01`'s own temporal is both — a vague quantity **and** an explicit
trigger — so the item was resolved by whichever bullet the annotator read first. Measured:
vague-qualifier-plus-trigger occurs in **22 pool segments (1.4%) across 12 documents**,
excluding `immediately upon`.

**One consequence of generalizing, stated rather than slipped in:** the v0.4 bullet said *"do
not set `vague_temporal_phrase`"* for `"Immediately upon X"`. That is now reversed — the
qualifier is recorded in every branch. `vague_temporal_phrase` is **excluded from the scoring
predicate** (§15.4), so this changes no score; it makes §15.4's headline count complete rather
than silently omitting the trigger-bearing cases.

**ACCEPTED RISK (F7, §20.4): the gold answer here is model-quoting-dependent.**
`ir_compile._WITHIN_RE`/`_RELATIVE_RE` are anchored — `_RELATIVE_RE` is
`^(before|after)\s+(.+)$` — so what the extractor chooses to quote into `temporal_raw` decides
whether the correct form is reachable at all. Verified against the production classifier:

| `temporal_raw` the model emits | `_classify_temporal` |
| :--- | :--- |
| `after the receipt by the Escrow Agent of notice` | `AFTER "the receipt … of notice"` |
| `Promptly after the receipt of notice` | **`None`** — `UNMAPPABLE_TEMPORAL` |
| `within a reasonable time after the death` | **`None`** — `UNMAPPABLE_TEMPORAL` |

Both `"Promptly after…"` and `"after…"` are literal substrings of the span, so the grounding
gate permits either and the gold answer is reachable **only** if the quote starts at the
preposition. This is **not** a reason to annotate `null` — §8's standing posture and §11's
`_WITHIN_RE` decision both hold that a known gap is annotated honestly and measured, never
avoided — but it must be reported, not discovered in a scoring run.

**This is the second independent instance of a real risk class, not a one-off:** *does the
extractor's quote start early enough — or late enough — to satisfy a downstream regex or
grammar anchor?* The first was the leading-subordinate-clause grounding bug (CLAUDE.md's own
checkpoint: the model drew `span_text` at the main clause while quoting a fronted clause's
content into `temporal_raw`, and `ground_candidates()` correctly rejected it). Both are
quote-boundary decisions made by the model that determine whether deterministic downstream code
can accept the result at all, and neither is detectable by any property test over pure code —
only by sampling real model output. Standing Principle 6's own limit, arrived at from a second
direction.

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

---

## 19. Recalibration (v0.26) — measured cost, measured discovery rate

Added 2026-08-21, after batch 2 was paused at 8 of 10 items. **No annotation rule changes
here.** This section records what the first 18 items actually cost and what that does and
does not license, separating measured quantities from judgment. Every figure below marked
*measured* is reproducible from the artifacts named; every figure marked *assumption* is
not.

### 19.1 The cost of batches 1 and 2 — measured

Source: session transcript message timestamps (`1fb27e05` for batch 2, the corresponding
window of `788ae2d2` for batch 1), plus `annotated_at`/`logged_at` in the item and exclusion
files. Overnight idle is excluded; "active elapsed" is wall-clock minus gaps in which
neither party was working.

| | batch 1 | batch 2 (8 items) |
| :--- | ---: | ---: |
| raw wall-clock span | 836.1 min | 1,028.4 min |
| overnight idle removed | 693.1 min | 807.4 min |
| **active elapsed** | **143.0 min** | **221.0 min** |
| **min/item** | **14.3** | **27.6** |
| drafter working time | 74.1 min (52%) | 57.7 min (26%) |
| reviewer turnaround | 68.8 min (48%) | 163.4 min (74%) |
| blocking adjudication gaps (≥5 min) | 4 | 9 |
| mean reviewer time per gap | 17.2 min | 18.2 min |
| segment-level acceptance | 38% (8/21) | 29% (4/14) |

**The throughput limiter is reviewer adjudication latency, not annotation.** Drafter working
time *fell* between batches while producing the same number of rules over fewer items; the
entire 78-minute increase is reviewer turnaround, and reviewer time per decision is
essentially constant. What changed is the number of decisions requiring adjudication.

**Two corrections to figures previously on record**, both of which quoted raw wall-clock
including overnight idle and overstate real cost by 4–6×: batch 1 was recorded as *"814
minutes wall-clock, ≈90 min/item"* and batch 2's in-session close-out reported *"1,028 min ·
17.1 h → 128 min/item."* The real figures are 143.0 min / 14.3 min/item and 221.0 min /
27.6 min/item.

**Reviewer-error correction cycles cost 14.6 min of batch 2's 221.0 — 6.6%** (the `18%`
figure exchange, 18:17:25–18:22:55; the phantom-item-7 exchange, 09:33:04–09:42:09).
Error-adjusted rate: 25.8 min/item. Both cycles produced a real corpus measurement as a
byproduct (§2.4's OCR class; the efforts-qualifier frequency). **Reviewer error is not a
material cost driver and correcting for it does not change any planning number.**

### 19.2 Rule-discovery rate — measured, and NOT tapering

Bumps per item, in annotation order, item 1 as baseline:
`[1,0,0,1,0,1,1,1,0, 1,1,2,2,0,2,0,0]` — 13 bumps over 17 scoreable positions.

| | batch 1 | batch 2 | ratio | exact p | 95% CI on ratio |
| :--- | ---: | ---: | ---: | ---: | :--- |
| item-stamped bumps (v0.12→v0.17 / v0.17→v0.25) | 5/10 = 0.50 | 8/8 = 1.00 | 2.00 | 0.168 | [0.65, 6.11] |
| incl. batch-1 draw-walk rules (v0.10, v0.11) | 7/10 = 0.70 | 8/8 = 1.00 | 1.43 | 0.330 | [0.52, 3.94] |

Poisson regression of bumps on item index: slope **+0.0322/item** (multiplier 1.033×), 95%
profile-likelihood CI on the multiplier **[0.924, 1.159]**, LR χ² = 0.321 (1 df), **p >
0.05**. First 6 items: 3 bumps. Last 6: 6 bumps.

**There is no evidence of tapering. Both point estimates increase; neither is significant;
the interval is compatible with anything from a 7.6% decline to a 15.9% rise per item.** All
planning below therefore assumes the **non-tapered** batch-2 rate. A taper would be a welcome
surprise, never a premise.

**A document-saturation model was proposed and falsified on this data**, recorded so it is
not re-proposed: batch 1 drew from 7 documents and produced 5 bumps (0.71/doc); batch 2 drew
from **3** and produced **8** (2.67/doc) — fewer documents, more rules. Within-document
position does not rescue it (first-in-document items: 0.50 bumps in batch 1, 1.67 in batch
2). The surviving hypothesis — consistent with the data, **not** established at n=18 — is
that discovery tracks which drafting patterns a given draw happens to surface, which implies
high batch-to-batch variance and means no single batch's rate is a reliable estimator.

### 19.3 Conforming debt, and four false claims corrected

**154 outstanding item × rule re-checks** *(corrected at v0.27; v0.26 said 127, having
counted version bumps rather than rules — v0.16, v0.17 and v0.21 each introduced two)*.
Fifteen of the 18 locked items were annotated against a ruleset that has since changed — `E01-01` has never been checked against 13 later
rule versions, `E03-01`/`C22-01`/`C03-01` against 12, down to 0 for the `C02` trio. §10's
conforming pass is mandatory before the freeze regardless; §10 now runs it at 18 items. Of
the 154, **139 clear mechanically and 15 need reviewer judgment** — see §19.7.

Three claims in this document were false and are corrected at v0.26:

1. The header read **"No items have been annotated against this document yet"** from v0.1
   through v0.25. Eighteen have, since 2026-08-19.
2. The **v0.15** changelog entry claimed "v0.15 is the version batch 1 is annotated under."
3. The **v0.17** entry claimed the same thing for v0.17, contradicting (2).

Batch 1's items in fact stamp **six** versions (v0.12 ×1, v0.13 ×3, v0.14 ×2, v0.15 ×1,
v0.16 ×1, v0.17 ×2), monotonically increasing with annotation time. The per-item stamps are
the honest artifact and §10's rule was followed correctly; the summary claims overstated.
`apps/brain/evals/goldens/batch01/SUMMARY.md` carries the same defect ("Guideline version:
v0.17") and is **not** corrected here — it is consolidation-pass work.

**A fourth false claim, corrected at v0.29 — and the first caught by §10's own close-out
consistency check rather than by a later session.** The Status line read, from v0.26 through
v0.28, that the consolidation pass was *"in progress, not complete"*, that *"Items stamp
guideline versions v0.12–v0.25"*, and that *"the §10 conforming pass has **not** run."* All
three were false the moment the pass completed: v0.28's own changelog entry says every
proposal was ruled and all 18 items conformed, and reading the items directly shows **all 18
now stamp `v0.28`** — a single version, which is what conforming means. The mechanism is the
one §10 predicts exactly: mid-pass wording is accurate when written and becomes false on
completion, and nothing in the normal editing flow revisits it. What is new is that the
check caught it **in the session that made it stale**, which is the whole point of adding it.
*(Also, and separately: the count in §10's own prose — "This document has carried a false
header claim three times" — is now four. It is left as written, being a dated record of what
was true when §10 was added; this entry is the correction.)*

### 19.4 Batch 2 is paused at 8 of 10

Two items remain undrawn. They are **not** being drawn until the consolidation pass
completes. The reason is not that the items are expensive (~55 min at the measured rate) but
that they cannot answer anything: adding 2 items to a 17-item sequence narrows §19.2's
interval by roughly 5%.

The consolidation pass closes, in one sitting: the **seven open decisions** — five rules at
`DEFAULT, PENDING CONFIRMATION` (§15 v0.4, §16 v0.5, §17 v0.6, §8.3.1 v0.23, §8.8 v0.24) and
two items at `DRAFTER_JUDGMENT_PENDING_REVIEW` (`C03-02`, `C11-01`) — three of which have
been open since **before batch 1 existed**, 18 items and 15 rule versions ago; the 154
re-checks (139 already cleared, §19.7); `SUMMARY.md`'s version claim; and a §7 amendment for a held-out draw against an
8-item batch 2. **Estimated ~6 h in v0.26; the §19.7 sweep cuts the re-check component
from 154 reviewer judgments to 15, so the realistic figure is now ~2.5–3 h.** The remaining
per-judgment cost still rests on the unmeasured 18.2 min-per-adjudication figure.

### 19.5 Target size: 100 is a working figure, NOT an analytically justified one

**Stated plainly because the analysis does not support the confidence a bare number implies.**

What *is* established, across the whole measured interval and independent of any unmeasured
parameter: **criterion 2 at ≥80% over all items is unreachable** (§9). That conclusion is
solid.

What is **not** established is the item count. The argument that 100 is near-minimal depends
on three things that do not bear the weight:

1. **An unmeasured true fully-correct rate.** The required scoreable N is 25 at a true 95%,
   54 at 90%, 87 at 88%, and 230 at 85%. No fully-correct rate has ever been computed for
   this pipeline. The choice of 90% is plausible, not evidenced.
2. **A gap-rate interval too wide to discriminate.** 7/18 = 38.9%, CI [20.3%, 61.4%] — from
   100 annotated items that is anywhere from **39 to 80 scoreable**, straddling the 54
   threshold entirely.
3. **An independence assumption the data violates.** Wilson intervals assume independent
   items; these cluster by segment (batch 2's 8 items came from 4 segments, 3 from
   `C02-021` alone). Clustering widens the true interval, so every required-N figure above
   is an **underestimate**.

**100 therefore stands as the working target because it is the existing specification and
nothing yet justifies changing it — not because it was derived.** The decision is deferred to
after the scoring harness runs against the 18 already-locked items, which is the cheapest
available way to learn which column of the required-N table this project is actually in and
requires no further annotation.

### 19.6 Planning figures — and their status

**Assumption, not measurement:** `min/item = (adjudications/item × 18.2) + 7`. This is a
**two-parameter model fitted to two data points — zero residual degrees of freedom, so it
cannot fail to fit.** It is a structural story about where time goes, not a validated law.

| | adj/item | min/item | remaining 82 items |
| :--- | ---: | ---: | ---: |
| batch-1 rate — taper, **not assumed** | 0.40 | 14.3 | 19.5 h |
| **batch-2 measured rate — the plan** | **1.13** | **27.6** | **37.7 h** |
| +50% | 1.70 | 37.9 | 51.9 h |
| contingency ceiling | 1.82 | 40.1 | 54.8 h |

**Plan on 38 h; hold contingency to 55 h.** Total to a scored criterion-2 number ≈ **62–73 h**
(consolidation 6 · harness build and run 4–8 · 82 items 38 · freeze-time conforming 6 · §7
held-out 8–15), of which the harness, held-out and re-check components are **guesses with no
measured basis**. An unquantified `K ≥ 4 → REDESIGN` branch in §7 would reset most of it.

**Tripwire.** Record adjudications per item per batch — currently recoverable only by mining
transcripts. If batch 3 produces **≥15 bumps over 10 items** (adj/item ≥ 1.50), the 38 h plan
is broken and target size re-opens. Because discovery is draw-dependent and high-variance
(§19.2), evaluate against the cumulative rate across batches 2–3, never batch 3 alone.

### 19.7 Consolidation sweep — 139 of 154 re-checks cleared mechanically

Run 2026-08-21 as the first step of the consolidation pass. For each of §19.3's 154 item ×
rule pairs, a detector asks whether the later rule could apply to that item at all. A pair
clears only when no detector fires; every fired pair goes to the reviewer.

**Result: 139 cleared (90%), 15 need a reviewer look.**

| item | stamped | unchecked | flagged | rules to look at |
| :--- | :--- | ---: | ---: | :--- |
| `E01-01` | v0.12 | 16 | 5 | §8.3 compound, §8.3 split rule, §8.4 mutual, §3.5.3 passive, §8.3.1 split-span |
| `E03-01` | v0.13 | 15 | 1 | §8.4 mutual |
| `C22-01` | v0.13 | 15 | 1 | §8.4 mutual |
| `C03-01` | v0.13 | 15 | 3 | §8.3 compound, §8.3 split rule, §8.3.1 split-span |
| `C03-02` | v0.14 | 14 | 2 | §8.3 split rule, §8.3.1 split-span |
| `C11-01` | v0.17 | 9 | 1 | §3.5.1.1 disjunctive obligors |
| `C04-01` | v0.18 | 8 | 1 | §8.3.1 split-span |
| `C04-02` | v0.19 | 7 | 1 | §3.5.2 beneficiary purpose |
| `C03-03`, `E07-01`, `C17-01`, `C17-02`, `C04-03`, `C14-01`, `C14-02`, `C02-01/02/03` | — | 71 | 0 | fully cleared |

**The detectors are deliberately high-recall, low-precision, and that is the correct bias
here** — a false positive costs reviewer minutes, a false negative silently leaves a
conformance gap. The §8.3/§8.3.1 compound-and-split detectors in particular over-fire on noun
conjunctions; they are a screen, not a verdict.

**A detector bug found and fixed during the sweep, recorded because it is the same class of
error §18 exists to catch.** The §2.4 OCR detector was first written `[a-hj-z]`, intending to
exclude the real one-letter words *a* and *I* — but that class still contains `a`, so it
matched "in a", "of a", "to a" and fired on **11 of 18 items across 8 documents, at a 100%
false-positive rate with zero true positives**. §2.4's own measured ground truth — 6 segments,
all in `C11`, zero elsewhere — is what exposed it. Corrected to `[b-hj-z]`, after which it
fires on nothing, correctly: no locked item's segment carries the split-word signature, and
`C11-01` was already verified clean when §2.4 was written.


---

## 20. Pending adjudication (v0.28) — PROPOSED, NOT ADOPTED

**STATUS AT CLOSE (2026-08-22): all 16 items in this section are ruled — 7 consolidation
decisions and 9 probe findings. Every approved rule has been written into its own rule section
above; §20.1/§20.2's rows are struck with their rulings, and §20.4 carries the full adjudication
log with rejected alternatives.** Items may now be stamped `v0.28` once the conforming pass
(§10) has run against the six affected locked items.

*(Original framing, retained: nothing in this section was in force while it was being
adjudicated; no rule section was modified until its proposal was individually approved.)* Each entry is adjudicated
individually and, only if approved, written into its own rule section — at which point it is
struck from here with the ruling recorded. This mirrors §10's discipline: a version string must
denote exactly one ruleset, so proposals are quarantined rather than mixed into live text.

Two sources feed this list: the consolidation sweep (§19.7) and the `E05-019` probe, which was
run against the proposals *before* any were adopted, precisely to find out whether they compose.

### 20.1 Seven proposed amendments (from the consolidation pass)

| # | proposal | touches | status |
| :-- | :--- | :--- | :--- |
| M1 | ~~Merge §3.5.1 + §3.5.1.1 + §8.4.1's value half into one slot-neutral party-slot rule~~ **ADOPTED — now §3.5.1** | §3.5.1, §3.5.1.1, §8.4, §8.4.1 | **RULED — approved as written** |
| M2 | ~~Merge §4.3's and §8.3's splitting tests into one performance-identity test~~ **ADOPTED — now §4.3** | §4.3, §8.3 | **RULED — approved as written** |
| M3 | ~~Restate §3.9's first trigger …~~ **ADOPTED — §3.9, §5, §21** | §3.9, §3.5, §5, §21 | **RULED — approved, both halves** |
| 4 | ~~Strike the `underspecified: true` instruction from §8.1 and §8.6~~ **ADOPTED — also §3.7.1, a third instance found on write-in** | §3.7.1, §8.1, §8.6 | **RULED — approved** |
| 5 | ~~New §3.8.1 — route a trailing qualifier by structure, not by marker word~~ **ADOPTED — §3.8.1, plus §8 table and §8.2 corrected** | §3.8.1, §8, §8.2, §4.3 | **RULED — approved, with (i) and (ii)** |
| 6 | ~~§15.5 — vague quantity + explicit trigger resolves to `RELATIVE_TO_TRIGGER`~~ **ADOPTED — option (a)** | §15.5 | **RULED — approved (a), F7 recorded** |
| 7 | ~~Pair A precedence — `on behalf of` governs over §3.5.3's obligee promotion~~ **ADOPTED — one sentence in §3.5.3** | §3.5.2, §3.5.3 | **RULED — approved** |

### 20.2 Seven probe findings (from `E05-019`)

| # | finding | kind | status |
| :-- | :--- | :--- | :--- |
| F1 | ~~`RELATIVE_TO_TRIGGER` preposition gap~~ **ADOPTED as §8.9, tag `relative_trigger_preposition`** | new corpus class | **RULED — approved** |
| F2 | ~~§8.3's `compound_action` tag over-fires on a same-taxonomy-verb doublet~~ **ADOPTED — §8.3 refined, three branches** | defect in an adopted rule | **RULED — (a)** |
| F3 | ~~Proposed §3.8.1 branch 1 false-positives on `if a claim shall be made`~~ **CONFIRMED — 63.3% FP rate measured; fix (c) delegates to §2/§3.2/§3.5.3/§8.8** | defect in proposal 5 | **RULED — (c)** |
| F4 | ~~M1 as first drafted is slot-asymmetric — no rule for a collective **obligee** (`such parties`)~~ **Claim partly falsified on test — see §20.4** | defect in proposal M1 | **RULED — (c)** |
| F5 | ~~M3 leaves `underspecified` undecidable at annotation time~~ **CONFIRMED — registry defined in §21** | defect in proposal M3 | **RULED — (b)** |
| F6 | ~~§2's cross-reference exclusion does not address a cross-reference inside a dropped carve-out~~ **ADOPTED — §2's row restated as scored-field dependence** | unstated boundary | **RULED — (a)** |
| F7 | ~~Proposal 6's correctness is model-quoting-dependent~~ **RECORDED as accepted risk in §15.5; second instance of the quote-boundary risk class** | accepted risk in proposal 6 | **RULED — recorded** |
| F8 | ~~Object-scope post-modifier vs `conditions` entry — no rule decided it~~ **ADOPTED — removal test added to §3.8** | unstated boundary | **RULED — approved** |
| F9 | **Surfaced by probe pass 3 (`C06-113`, fresh draw).** ~~No rule for an obligation restated within one segment~~ **ADOPTED — §4.3.1; §4.4's scope widened** | new corpus class | **RULED — approved** |

### 20.4 Adjudication log

Each entry is written when the reviewer rules, before the corresponding rule text is drafted.

**F4 — RULED (c), 2026-08-22.** *Slot-neutral prose, no new scored field; alternatives for a
joint or disjunctive `obligee` are recorded in `annotator_notes`.*

**The finding's original statement was falsified while being tested, and the correction is the
substantive part of this entry.** F4 first claimed that no rule in adopted v0.27 covered a
collective **obligee**. That is wrong: §3.5's rule is already slot-neutral — *"Annotate the
party alias exactly as it appears inside `span_text`"* — and its `ABSENT` branch is scoped to
*"a party genuinely not stated in the span."* `"such parties"` **is** stated and **is** in the
span, so §3.5 alone yields `obligee: "such parties"` with no amendment. §8.4.1 exists for the
obligor slot **only because §8.4 issued a competing instruction** (*"first-named party"*) that
had no referent for a collective subject; no rule issues a competing instruction for the obligee
slot, so there was nothing to disambiguate.

**The residual asymmetry is real but small:** the accept-set machinery is obligor-only
(`obligor_accept_set` is a §1 field; there is no `obligee_accept_set`, and §3.5.1/§3.5.1.1 write
only the obligor's). Measured over the 1,547-segment pool, obligee position after a dative verb:
**joint obligee 0 segments; disjunctive obligee 3 (0.2%); collective/relational 9 by the narrow
dative match.** **Zero of the 18 locked items has a multi-party obligee**, checked mechanically.

**Rejected alternatives, recorded so they are not relitigated.** *(b) full symmetry* — adding
`obligee_accept_set` to §1 and §5 clause 4 — was rejected as disproportionate at 0.2% and
because it would deepen an existing schema gap (9 of 10 batch-1 items already lack the
`obligor_accept_set` key entirely). *(a) reject outright* was rejected because the slot-neutrality
of the **test** was genuinely arbitrary even though the field asymmetry is now justified.
The reviewer's stated ground: this is the symmetric application of the principle §3.5.1 already
established for joint obligors — *"Tagging it would assert a v1 limitation that does not exist"* —
here, declining to assert a scoring need the corpus does not show.

**Consequence for M1:** step 1 is written slot-neutrally, with the accept-set branch scoped to
the `obligor` slot and `annotator_notes` carrying the rare obligee case. `E05-P2`'s annotation is
unchanged under any of the three options.

**M1 — APPROVED as written, 2026-08-22.** *Merged into a new §3.5.1, "The party slot."*

Three sections answered one question — *what string goes in the party slot?* — selected by one
binary test: **does the span name the individual parties filling this slot?** §3.5.1.1 derived
itself from §3.5.1 in its own text (*"§3.5.1's own test decides it"*) and gave an identical
instruction; §8.4.1 was the other branch of the same test, and existed only because §8.4 carried
a value instruction (*"first-named party"*) with no referent for a collective subject.

**Evidence the split misdirected annotation:** four locked items of the same family cite four
different rule sets — `C17-01` §8.4 only, `C17-02` §3.5.1 only, `C02-01` §3.5.1 + §3.5.1.1,
`C14-01` §8.4 + §8.4.1 + §8.3.1. `C17-01` and `C17-02` are the same named-conjunction shape
citing disjoint rules.

**Cost verified, not assumed: zero field values change.** All 18 locked items were checked
mechanically; every existing party value is already what the merged rule produces. Four items'
`rules_cited` normalize to `3.5.1`.

**§3.5.1.1 and §8.4.1 are retained as pointers, not deleted** — `C02-01` cites `3.5.1.1`, and
`C04-02`/`C14-01`/`C14-02` cite `8.4.1`; a citation must resolve. §8.4.1 keeps its measurement
table (collective 7.4%, distributive 4.7%, named conjunction 3.2%, `both Parties` 0.2%) and its
`ABSENT`-is-false reasoning, both cited by the merged §3.5.1. §8.4 keeps only its tag semantics.

**Rejected alternatives.** *Merge §8.4 in too* — rejected as orthogonal, and §8.4.1's own
measurement establishes the independence: only **31 of 132 (23%)** collective-reference sentences
carry a reciprocity marker, where a shared predicate would sit near 0% or 100%. *Keep §3.5.1.1
separate for the `and`/`or` semantics* — the distinction is real but produces no different
annotator action; retained as a note inside branch 1.

**M2 — APPROVED as written, 2026-08-22.** *§4.3 and §8.3's splitting tests merged into one
performance-identity test, stated once in §4.3.*

**The two rules genuinely conflicted.** §4.3 (v0.1) tested object identity; §8.3 (v0.15,
reviewer-confirmed) explicitly repudiated that test — *"not 'one object or two' on its own"* —
and gave *"shall promptly notify and remedy any breach"* as its counter-example. Run that
sentence through §4.3 and it is one item; through §8.3, two. Both were in force.

**Measured exposure: 29 pool segments (1.9%), 12 documents** carry the divergent shape
(`manufacture and test all Devices`, `obtain and maintain all necessary licenses`,
`label and package the Products`), concentrated in `C02` and `C03` — two documents that
between them already supplied 6 of the 18 locked items.

**Verification method, stated precisely because the reviewer required it and because the
condition as originally stated could not be met.** A fully automated comparison of the two
tests is **impossible**: §8.3's performance-identity test is irreducibly semantic — no detector
decides whether `label and package` is one performance. What was done instead:

1. *Mechanical, reproducible:* four high-recall coordination detectors run over the **full
   text of all 12 distinct source segments** behind the 18 locked items. **8 occurrences
   flagged across 6 segments; 6 segments clear.**
2. *Manual, shown in full:* each of the 8 classified as inside-an-annotated-clause or not,
   then both tests applied by hand to those that are.

**Result: exactly 2 of 8 occurrences sit inside an annotated clause — `C03-192`→`C03-02`
(both tests: one item) and `C14-076`→`C14-01`/`C14-02` (both tests: two items). Both agree.
Zero locked items require re-annotation.** The other 6 are in clauses no item was drawn from:
four with non-party or copular subjects, two in undrawn sentences.

**A detector recall gap, disclosed rather than quietly corrected.** The real `C14-076`
splitting sentence — *"Each party shall deduct such taxes … **and shall** promptly furnish …"* —
was **missed** by the two-modal detector: the text between the two modals is ~148 characters
against a `{0,140}` window. `C14-076` appears in the flagged list only because a *different*
coordination in the same segment was caught. Found by checking flagged context against the known
sentence, then covered manually. Same class as §19.7's `[a-hj-z]` bug: a pattern that passes
inspection while missing the real case. **An earlier presentation of M2 asserted `C14-01`/
`C14-02` were verified-agreeing; that conclusion was correct but had been reached by reading,
and the detector meant to back it had missed that very sentence.**

**F2 corroborated independently of the probe.** Occurrence 5 of the sweep is
*"shall indemnify and hold harmless the other Party"* in `C17-066` — the **same doublet** as the
probe's `E05-P1`, in a locked item's own source segment. F2's class (a coordinated pair whose
verbs collapse to a single taxonomy verb) therefore recurs in the corpus and is not an artifact
of the one probe segment. Carried forward to F2's adjudication.

**F5 — RULED (b), 2026-08-22.** *The scoring registry contains every party the source
document's preamble defines — proper names and defined roles alike — and never collectives,
distributives, relational references, or unnamed third parties. Written into §21 R3.*

**Unlike F4, the claim survived testing.** A grep of the whole guideline for any annotation-time
rule about what resolves returns only four passing uses of the adjective *"registry-resolvable"*
inside §3.5.1 — all assuming the concept, none defining membership. `underspecified` is scored
(§5 clause 8) and must be written at annotation time, so the gap was real.

**The rule was derived from the locked set, not invented.** Nine items assert
`underspecified: false`, and each is a constraint that *every* alias in it resolves. That set is
`AT&T, TIBCO, AMAG, Antares, Bellicum, Miltenyi` (proper names) **and**
`Vendor, Client, Provider, Recipient` (defined roles) — so the locked annotations already
presuppose that defined roles resolve. Option (c) proper-names-only would flip four further
items (`C03-01`, `C03-02`, `C17-01`, `E07-01`); option (a) an empty registry would contradict
all nine and make §9's "share correctly underspecified" 100% by construction.

**Testing F5 surfaced a larger, separate problem, now also resolved.** `ast.ResolvedParty`
carries `(party_id, canonical_name)` and **discards the span alias**, and `PipelineResult`
retains the `LLMCandidate` only for rejected/quarantined candidates. So the registry decision
does not only determine clause 8 — it determines whether **clauses 3 and 4 are evaluable at
all**, in the opposite direction: every party registered removes an item's alias from the
comparison. §5 had no rule for this. The party-comparison rule now in §5 closes it; the reasons
it matches against the registry rather than the model's own resolution path are recorded there.

**M3 — APPROVED, both halves, 2026-08-22.** *§3.9 trigger 1 restated to match
`typecheck.py`; registry definition and harness requirements in §21; §5 party-comparison rule.*

`typecheck.py` computes `underspecified = bool(missing_fields)` and `_resolve_party` appends on
`resolve_party() is None`, not on `ABSENT`. **437 of 1,547 pool segments (28.2%)** carry a party
reference that can never resolve. Consequences on locked items, checked individually:
`C14-01` and `C14-02` were **guaranteed clause-8 failures** (`false` where the pipeline emits
`true`); `E03-01` is guaranteed-wrong in the intended configuration (see decision 4);
`C11-01`/`C22-01`/`E01-01`/`C04-02` have the right value but understate the reason in
non-scored `missing_fields`; and **11 further items were undecidable** without a registry rule.

**Rejected alternatives.** *Change the code to match §3.9* — would require `resolve_party` to
treat an unresolvable-but-stated alias as resolved, inventing a party identity; forbidden by
Standing Principle 2 and §3.5's positional discipline. *Leave §3.9 and accept the mismatches* —
three guaranteed failures and eleven undecidable items out of 18. *Drop `underspecified` from
§5's predicate* — it is the field distinguishing "compiled faithfully" from "resolved", which
§9 requires precisely because the headline number is misread without it.

**Decision 4 — APPROVED, 2026-08-22.** *The `underspecified: true` instruction struck from
§8.1, §8.6 **and §3.7.1**.*

**A third instance was found while writing the approved change in.** The decision was put to the
reviewer as §8.1 and §8.6; a grep for every instruction setting the field showed §3.7.1 carries a
verbatim copy of §8.1's clause. Same defect, same fix, struck at the same time and recorded here
rather than left for a later grep to rediscover. The three *correct* uses of the field — §3.5's
`ABSENT`-party rule, §3.5.3's passive-obligor rule, §3.9's own explanatory paragraph — were
checked and left untouched.

**The contradiction was three-way, and §15.3 had already argued it in advance:** *"annotating
`underspecified = true` would therefore make **every** such item fail clause 8 … not because
extraction was wrong, but because gold asserted a capability v1 explicitly declined to build."*
§3.9's trigger list is closed; §14.2 forbids use outside it; `typecheck.py:153` returns `None`
for an absent temporal without appending to `missing_fields`.

**Live instance: `E03-01`.** Both parties (`Kissei`, `Rigel`) are preamble-defined proper names
that resolve under §21 R3, and `temporal: null` is never flagged — so the pipeline emits
`underspecified: false` for a perfect extraction while gold asserted `true`. A guaranteed
clause-8 failure manufactured entirely by the rule. **`C17-02` carried the same §8.6 instruction
but was masked**: it is `underspecified: true` anyway via its `ABSENT` obligee, so the defect was
live on two items and visible on one.

**Rejected alternative: widen §3.9 to flag `temporal: null`.** It contradicts `typecheck.py`'s
deliberate design, §15.3 rejected it in writing, and it would additionally fail clause 8 on every
vague-temporal item — §15's measured **12% of segments** — converting a scope decision into a
silent defect across a far larger class than the two gap rules. The fix stays the size of the
defect.

**Cost: one scored field changes.** `E03-01` `underspecified` `true` → `false`; it keeps
`missing_fields: ["temporal"]`, `redacted_phrase`, and its `redacted_value` tag. `C17-02` stays
`true`, now correctly derived from §3.9 trigger 1 rather than from §8.6.

**Together with M3 this closes all three of M3's flagged clause-8 failures** — `C14-01` and
`C14-02` by M3's trigger restatement, `E03-01` here.

**F3 — RULED (c), 2026-08-22.** *Branch 1 asks whether the qualifier would stand alone as an
obligation-bearing clause under §2 and §3.2, delegating to existing rules rather than applying a
fourth independent test.*

**Confirmed, and not a one-off.** The probe's case — *"if a claim in respect thereof **shall be
made** against the other parties hereto"* — has a subject and a modal but is a condition:
non-party subject, archaic conditional `shall`. Conditional subordinator + non-party subject +
`<modal> be` occurs in **13 pool segments (0.8%)**.

**The figure that originally sized branch 1 was measuring the wrong thing, and is corrected
here.** *"74.3% of `provided that` occurrences have a modal in the tail"* counts modals, not
obligations. Hand-classified seeded sample (seed `20260822`, n=30, §8.8's methodology), asking
of each *"would this clause, standing alone, be an obligation-bearing clause?"*: **11 genuine
branch-1 against 19 false positives — 36.7%, 95% Wilson CI [21.9%, 54.5%]**. Applied to the
128-occurrence modal-in-tail population: **~47 genuine, not 128**; as a share of all 171
`provided that` occurrences, **~27%, not 74.3%.** The v1 test's false-positive rate is **63.3%**.
The dominant false-positive class is the interpretive provision — *"nothing in this Section shall
inhibit…"*, *"no such severability shall be effective…"*, *"the foregoing shall not limit…"*.

**A second-order defect in the drafter's own first replacement, found while classifying the
sample and recorded rather than quietly dropped.** The proposed fix *"predicates a deontic modal
of a party subject"* fails on *"provided that such display, hanging signs, and interior banners
**shall be professionally produced and hung**"* — an agentless passive with a non-party subject,
which **§3.5.3 explicitly admits** as a real obligation with `obligor: ABSENT`. That fix would
route a genuine obligation into `conditions`, the same error F3 identifies, pointing the other
way. Option (c) survives both cases because it introduces no new test: it delegates to §2, §3.2,
§3.5.3 and §8.8, which already decide what counts as an obligation-bearing clause.

**No locked item is affected** — §3.8.1 did not exist when this was ruled; the ruling determines
the text decision 5 is presented with.

**Decision 5 — APPROVED, 2026-08-22, together with (i) and (ii).** *§3.8.1 added; §8's gap
table and §8.2's opening corrected to state measured compile behaviour; the underlying
production defect recorded in CLAUDE.md.*

**The routing gap was real and the locked set had already papered over it twice.** `C14-01`
sent a negative carve-out to destination 2 citing §8.2; `C04-01` sent an affirmative proviso to
destination 1 citing §3.8/§17. Both correct, neither citable to a rule that names the test.
§8.2 covered one marker word; non-`unless` carve-out markers outnumber `unless` **1.85 : 1** by
segment across 19–21 of the 28 documents.

**Branch 1 delegates to §2/§3.2/§3.5.3/§8.8 rather than applying its own test** — see F3's
entry for the two drafts that failed and why.

**Tag renamed `unless_unsupported` → `exception_unsupported`**: the class is semantic, not
lexical. `E01-01` and `C14-01` are re-stamped; no field value changes on either. §8.2 is
retained as a pointer — both items cite it.

**(i) §8's table row and §8.2's opening corrected.** Both asserted *"fails to parse."* Tested
against the real pipeline: a carve-out arriving as a `condition_raws` entry compiles cleanly
into an `AtomPredicate`. The claim was true of the DSL path only, which extraction never takes.

**(ii) The production defect is recorded in CLAUDE.md's debt list**, tied to the Normalizer
checkpoint, as an unfixed contradiction of `SPEC.md` §6's frozen never-silently-absorb
principle and the third instance of that pattern. Not gold-set work; recorded so it does not
live only in a conversation.

**Cost: zero scored fields change.** `E01-01` and `C14-01` re-stamped for the tag rename;
`C04-01`'s existing condition entry is confirmed and now citable to branch 2.

**Decision 6 — APPROVED, option (a), 2026-08-22.** *Vague quantity + explicit trigger resolves
to `RELATIVE_TO_TRIGGER`; F7 recorded in §15.5 as an accepted risk.*

**The collision was live in a locked item.** §15.5's `"Immediately upon X"` bullet and its
`"within a reasonable time"` bullet decided the same sentence differently, and `C11-01`'s
temporal — *"within a reasonable time after the Principal's death or mental incapacity"* — is
both. Measured at **22 pool segments (1.4%), 12 documents**, excluding `immediately upon`.

**Option (b) — restrict the rule to prepositions `_RELATIVE_RE` can actually accept — was
rejected on a principle this guideline has now applied twice.** §11 rejected widening
`_WITHIN_RE` before measuring, on the ground that it would tune the compiler to the corpus it is
about to be graded on; §8's standing posture is that a known gap is *"annotated honestly and
measured, never avoided."* Annotating `temporal: null` because the compiler cannot swallow
`upon` would hide F1's gap inside a field that looks correct. The principle was applied
consistently rather than relitigated.

**A consequence recorded rather than slipped in:** generalizing reverses the v0.4 bullet's
*"do not set `vague_temporal_phrase`"* instruction for `"Immediately upon X"`. The field is
excluded from §5's predicate (§15.4), so no score changes; §15.4's headline count becomes
complete instead of silently omitting trigger-bearing cases.

**F7 — RECORDED as an accepted risk, 2026-08-22.** The gold answer is reachable only if the
extractor quotes `temporal_raw` from the preposition: `after the receipt …` classifies,
`Promptly after the receipt …` returns `None`. Both are substrings of the span, so the grounding
gate permits either.

**F7 establishes a risk class, which is why it is recorded rather than merely noted.** It is the
**second independent instance** of *"does the extractor's quote start early enough to satisfy a
downstream anchor?"* — the first being the leading-subordinate-clause grounding bug already on
record in CLAUDE.md. Both are model quote-boundary decisions that determine whether
deterministic downstream code can accept the output at all; neither is reachable by any property
test over pure code, only by sampling real model output. That is Standing Principle 6's own
stated limit, arrived at from a second direction.

**Cost: one locked item changes a scored field.** `C11-01` gains
`temporal: RELATIVE_TO_TRIGGER(after, "the Principal's death or mental incapacity")` in place of
`null`, keeping its `vague_temporal_phrase`.

**F1 — APPROVED as §8.9, 2026-08-22.** *New gap class and tag `relative_trigger_preposition`;
`_RELATIVE_RE` widening deferred, not rejected.*

**The largest single finding of the consolidation pass.** `_RELATIVE_RE` accepts two
prepositions; `upon`, `following`, `prior to` and `on` fall through to `UNMAPPABLE_TEMPORAL`,
rejecting the whole candidate. Measured against the real classifier: **111 of 142 trigger-bearing
segments rejected, 3.58 : 1** — against §8.6's 7 confirmed instances for the sibling defect in
`_WITHIN_RE`.

**Kept separate from §8.6 rather than folded in**: different regex, different cause, different
fix. Folding would inflate §8.6's measured size with a differently-caused class — §8.6's own
objection to being folded into §8's parenthetical row.

**Third consistent application of §11's measure-before-changing principle.** §11 deferred
widening `_WITHIN_RE`; decision 6 rejected restricting §15.5 to prepositions the compiler can
already swallow; §8.9 defers widening `_RELATIVE_RE`. The reviewer's note on the record: three
consistent applications is evidence of a real, stable design principle rather than an ad hoc
call made once and reused loosely. The one-line widening
(`before|after|upon|following|prior to|on`) is queued as a named candidate for after criterion
1b has produced a baseline, not rejected.

**Cost: zero locked items.** No locked item carries an `upon`/`following`/`prior to` trigger
temporal; probe `E05-P1` already carries the tag provisionally.

**Decision 7 — APPROVED, 2026-08-22.** *One-sentence precedence clarification in §3.5.3:
`on behalf of` governs, and that party is never promoted to `obligee`.*

**The drafter's earlier estimate of this class was too high and is corrected here.** The party-
family walkthrough reported *"12 co-occurrences → 6 survive inspection → single-digit, ≤5."*
That excluded definitions and copular constructions but never checked whether the two
constructions sit in the **same clause**. Measuring the character gap between them leaves
**exactly one genuine instance in 1,547 pool segments (0.06%)** — `C14-148`. The other eleven:
three definitions, three copular, two with an explicit by-agent (so §3.5.3 never fires), three
99–691 characters apart in different clauses.

**Approved at n=1 on cost asymmetry, not frequency, and the distinction is the reviewer's
stated ground:** this is not new machinery — no field, no tag, no schema change — it closes an
ambiguity between **two rules that already exist**, which would otherwise force a full
re-derivation of the §3.5.2/§3.5.3 boundary the next time anyone hits it. That is a different
cost category from F4's rejected option (b) (a new scored field plus a migration across 18
items at 0.2%), and from the low-frequency cases rejected elsewhere in this pass.

**The measurement is stated inline in §3.5.3** so the class is never later cited as common.

**Cost: zero locked items; the probe is unaffected** (`E05-P1` has an explicit by-agent, so
§3.5.3 never fires on it).

---

**All seven original consolidation decisions are now ruled: M1, M2, M3, the §8.1/§8.6/§3.7.1
strike, §3.8.1, §15.5, and this.** Probe findings F1, F3, F4, F5 and F7 are ruled. **F2 and F6
remain open**, followed by the re-run of probe `E05-019` against adopted v0.28.

**F2 — APPROVED (a), 2026-08-22.** *§8.3's `compound_action` tag fires only where a verb is
actually lost; class-3 co-occurrence with `action_not_in_taxonomy` settled at the same time.*

**Approved without first sizing the class, deliberately.** The reviewer's stated ground: this is
a correctness fix to an existing tag's false-positive rate, not new scoring infrastructure, so
the argument — *same taxonomy verb → nothing lost → the tag firing is simply wrong* — does not
depend on frequency, unlike the earlier low-frequency cases where the rate genuinely decided
whether new machinery was worth building. The rate is recoverable later from `known_gaps` data.

**A corpus-wide rate was attempted and discarded** — the classifier was defective; see the
standing note in CLAUDE.md (Standing Principle 7). Two real instances stand on their own: the
probe's, and `C17-066` in a locked item's own source segment, found independently by M2's sweep.

**Cost: zero locked items.** `C03-02` is `provide`+`keep current` → `PROVIDE`+`MAINTAIN`, two
different taxonomy verbs, so its tag stays.

**F6 — APPROVED (a), 2026-08-22.** *§2's cross-reference exclusion restated: the test is whether
a **scored field** depends on resolving the reference, not whether a reference is present.*

**This writes down existing practice; it was verified against the logs, not assumed.** All six
exclusions citing cross-reference dependence are genuine dependence cases — `C04-018` (scope,
three places), `E03-005` (temporal), `C04-118` (object/amount), `C05-043` (the primary duty
qualified), `C15-046` (the action's manner), `C11-079` (the operative proviso). Every one
survives the narrower test unchanged, so no exclusion is overturned.

**The gap it closes:** **424 of 1,547 pool segments (27.4%)** contain a cross-reference token
while only 6 of 27 exclusions cite one — so a presence-based reading was never actually being
applied, but nothing said so, and it left `E05-P1`'s case (a reference inside a §3.8.1 branch-3
carve-out that reaches no scored field) undecided.

**A self-raised depletion concern, tested and not reproduced.** Because §2.2's hard stratum is
*defined* by cross-reference density (`xref_pct ≥ 20`), cross-reference exclusions could
preferentially deplete the documents the 25-item floor protects — §13's and §18.6's failure mode
through a third mechanism. Measured: cross-reference exclusions split **3 hard / 3 standard**
against an all-exclusions split of 14/13, and the locked set stands at **6 of 18 hard (33%)**,
above §2.2's 25% floor. **No depletion at n=18.** Recorded rather than dropped, and flagged for
**re-check at batch 3** — the floor is a per-100 figure and 18 items is a small sample. If
anything the amendment cuts against depletion, since it admits segments the ambiguous reading
might have excluded.

**F8 — APPROVED, 2026-08-22.** *Removal test added to §3.8: a condition states a circumstance
under which the duty applies; a phrase restricting which instances of the object are covered is
object scope.*

**Surfaced by the v0.28 re-run, not by the first probe pass** — the first pass produced one new
class and five defects in the proposed amendments; the second produced this, and no defects.

**Smaller than it first appeared, because the extraction prompt already implies the answer.**
`prompts/extraction/v2.yaml` defines `object_raw_text` as *"the phrase naming that object"* and
`condition_raws` as *"'if'-type conditional phrases that this obligation depends on."* A scope
modifier on the object is neither, so a correct extraction emits it nowhere, and gold annotating
it as a condition would score a correct extraction wrong on §5's count-sensitive clause 7. The
rule was never written down because the prompt made it unnecessary — until a segment appeared
where the phrase was long enough to look like a condition.

**Verified: all 8 `conditions` entries across the 18 locked items pass the removal test as
conditions; none is an object-scope phrase.** Nothing is overturned. Class size: **93 pool
segments (6.0%)**, larger than several classes that earned their own rules in this pass.

**Why it needed a rule at all rather than being left to judgment:** `conditions` count is an
exact-match field, so §14.3 routes any ambiguity to **escalation**, not to an accept-set. At 6.0%
of segments that is roughly 1–2 items per batch of 10 against §14.4's budget of ≤2 per batch —
the ambiguity alone would have consumed the escalation budget.

**A residual is tracked in CLAUDE.md's debt list rather than resolved here:** gold's existing
conditions use several non-`if` markers (`upon`, `As requested by`, `solely to the extent`,
`provided that`) while the prompt says *"if"-type*. Whether the model actually emits
`condition_raws` for those markers is unverified against real output and is only checkable by a
live run.

**F9 — APPROVED, 2026-08-22.** *§4.3.1 added; §4.4's scope widened to cover a span excluded as a
restatement rather than by §2.*

**Surfaced by probe pass 3** — a seeded random draw (`20260822`) from the 309 eligible segments
in the 11 never-touched documents, screened against §2 with five rejections logged. Selection
method was deliberately changed from pass 1's open-rule-coverage scoring, which biases toward
finding issues adjacent to rules already known.

**The reviewer's proposed treatment was tested against the motivating case and half of it did
not survive.** *"Annotate the more complete restatement"* presupposes one clause contains the
other; `C06-113`'s two `may abandon` clauses differ on **two scored fields** (trigger text and
object restriction) and neither contains the other. Step 1 — the actual-identity test — was added
in front of the treatment and does the real work: it reclassifies `C06-113` as **three distinct
obligations**, so the segment that produced this rule never reaches its step 2.

**§4.4 reused rather than a new tag invented.** Annotating both restatements costs a `MISSED`;
dropping one costs an `UNEXPECTED`; §4.4's "neither correct nor a false positive" is the only
neutral treatment, and it already existed.

**Step 2 is recorded as UNTESTED.** No instance has arisen in any material seen — the same
footing §8.3's split branch held until `C14-076`. Its logical soundness must not borrow
confidence from step 1's demonstration.

**Cost: zero locked items** — no locked segment carries a restatement marker.

### 20.3 What this section does NOT claim

- **Not** that no merges were found. Three were identified (M1, M2, M3); the party-resolution
  comparison in the consolidation pass is the reasoning for M1 and against merging §3.5.2/§3.5.3
  and §8.4/§8.4.1.
- **Not** that discovery is finished. **Three independent probe passes produced three new
  classes** — F1 (pass 1, `E05-019` against the proposals), F8 (pass 2, `E05-019` against adopted
  v0.28), F9 (pass 3, `C06-113`, a fresh seeded draw from a never-touched document). The new-class
  rate did not fall across the three.
- **What the passes do establish**, and it is the narrower claim: the **defect** rate against the
  adopted ruleset went **5 → 0 → 0**. Pass 1 broke five of the six proposals it exercised
  (F2–F5, F7); passes 2 and 3 found none. The fixes hold, including on unseen material from a
  document type neither earlier pass touched. **"Composes correctly under test" is therefore
  supported; "complete" is not.**
- **Not** that the consolidation pass is complete. Seven pre-existing decisions remain open —
  five rules at `DEFAULT, PENDING CONFIRMATION` (§15 v0.4, §16 v0.5, §17 v0.6, §8.3.1 v0.23,
  §8.8 v0.24) and two items at `DRAFTER_JUDGMENT_PENDING_REVIEW` (`C03-02`, `C11-01`) — alongside
  15 of §19.3's 154 re-checks and `SUMMARY.md`'s uncorrected version claim.
- **Not** that discovery is slowing. §19.2's measurement is unchanged: no evidence of tapering.

---

## 21. Scoring-harness build requirements (v0.28)

**These are build requirements, not notes.** Each was derived from real corpus or real code
during the consolidation pass, and each has a failure mode that would be attributed to
extraction quality if it were missed. R5 exists so that R1–R3 cannot be silently violated.

### R1 — one `parties` registry per source document, torn down between documents

`symbols.resolve_party()` returns `None` when its query matches more than one row
(`len(rows) != 1` — a deliberate *"an ambiguous match is still UNRESOLVED, not a guess"*
decision). Measured across the 28-document corpus: **`Client` is a defined party role in both
E02 and E07; `Provider` and `Recipient` in both C17 and E01.** A single shared org registry
would therefore resolve those three aliases to nothing, flipping locked items **`E07-01`** and
**`C17-01`** from `underspecified: false` to `true` and failing §5 clause 8 on both — a scoring
failure caused entirely by harness setup. Mirrors what the eval-harness pilot already did for
its 2 synthetic parties.

### R2 — alias entries MUST be registered with exact span casing

The production query is:

```sql
SELECT id, canonical_name FROM parties
 WHERE lower(canonical_name) = lower(:alias) OR :alias = ANY(aliases)
```

`canonical_name` is matched **case-insensitively**; the `aliases` array is matched
**case-sensitively**. Gold stores party aliases verbatim from the span (§3.5), capitalization
included, so an alias registered in the wrong case silently fails to resolve.

**Concrete failing case:** gold `obligor: "Vendor"`; registry row
`canonical_name = 'Vendor Inc.'`, `aliases = ['vendor']`. Neither branch matches —
`lower('Vendor Inc.') ≠ lower('Vendor')`, and `'Vendor' = ANY(['vendor'])` is false — so
`resolve_party` returns `None`, the item flips to `underspecified: true`, and §5 clause 8 fails
on an item whose extraction was perfect. Registering `aliases = ['Vendor']` fixes it.

**This affects the `aliases` array only.** An alias that happens to equal `canonical_name` is
matched case-insensitively and is not exposed to this.

### R3 — registry contents are committed with the harness and published with every number

Per §3.9 trigger 1 and §20.4 (F5, option (b)): the registry holds every party the source
document's own preamble defines — proper names **and** defined roles — and never collectives,
distributives, relational references, or unnamed third parties. Whether an item is
`underspecified` is a function of this fixture, so a published criterion-2 number without its
registry is not reproducible.

### R4 — clause 3/4 comparison is by `party_id`, not by string, for resolved parties

Implement §5's party-comparison rule exactly. The model's own alias is **not** recoverable from
`PipelineResult` for a successfully typechecked obligation; do not build a scorer that assumes
it is.

### R6 — `UNEXPECTED` is a KNOWN OVER-COUNT until §4.4 spans are annotated (v0.28)

**Every report MUST carry this caveat verbatim until the underlying data exists:**

> *`UNEXPECTED` counts in gold-set scoring reports are a known over-count until
> `NOT_ANNOTATABLE` spans are annotated for all 12 gold segments (real judgment work, same
> review discipline as gold items, not yet scheduled).*

**The gap.** §4.4 says a prediction aligning to a `NOT_ANNOTATABLE` span *"counts as **neither**
a correct item **nor** a false positive"*, and §4.3.1 step 2 relies on that mechanism for
restatements. But **the item schema has no field for it.** `NOT_ANNOTATABLE` is a *segment*-level
fact and gold items are stored *item*-level, so there is nowhere to record the excluded clauses.
Consequently a prediction on any un-annotated clause inside a gold segment scores `UNEXPECTED` —
a false positive charged to extraction for correctly reading a clause §2 excludes.

**The eventual data shape, decided now so adding it later is additive rather than a rewrite:** a
per-segment file `goldens/batchNN/segments/<segment_id>.json` carrying
`[{span_char_start, span_char_end, reason}]`. Segment-level, because the fact is. The scorer
accepts this input from the outset and simply receives an empty list until it is populated.

**Why the interim state is honest rather than convenient.** The alternatives were to fabricate
precision (suppress `UNEXPECTED` and report nothing) or to defer scoring entirely. Reporting the
count with a stated direction of error preserves the signal and names its bias. **It is a
measured over-count, not an unknown one: the error is one-directional and can only shrink.**

**The exclusion logs are a PARTIAL SOURCE for this data, which reduces the work and makes the
over-count triageable rather than merely acknowledged (v0.28, G1).** `E03-005` yields one gold
item, and the batch-1 exclusion log already names two further obligation-bearing clauses in that
same segment, with reasons: **`E03-005#itemize`** (*"For clarity, each Order Forecast shall
itemize…"* — logged `NOT AN ITEM (drafter's judgment, reviewer did not rule -- reversible at
batch review)`) and **`E03-005#discuss`** (cross-reference-dependent). A correct extraction of
either scores `UNEXPECTED` today. So populating §4.4 data is **partly transcription from the
exclusion logs**, not wholly fresh judgment — and every `UNEXPECTED` the harness emits carries
its **span text and offsets** so it can be triaged against the log rather than counted blind.

**`E03-005#itemize` is additionally tracked as a `DRAFTER_JUDGMENT_PENDING_REVIEW` item** — the
log records that the reviewer never ruled on it and that it is reversible.

**Scheduling, stated so this does not quietly become permanent.** Populating it is annotation
work over **12 segments**, requiring the same per-item adjudication every gold item received.
Until it is done, R6's caveat travels with every published `UNEXPECTED` figure, and no precision
or false-positive claim may be made from gold-set scoring.

**SCHEDULED at v0.50 — §2.7 rules that this data is a by-product of drafting, and the paragraph
above is corrected on two points rather than merely satisfied.** (1) *"requiring the same
per-item adjudication every gold item received"* is **not** what §2.7 requires: a disposition
carries offsets, verbatim text, one of four outcome labels, a rule citation and one sentence of
reason — no `action`, no `object_class`, no accept-set, no field-level adjudication. That
narrowing is the whole cost control. (2) The measured retrofit is **39 spans over 22 segments**
(12 of them cassette-covered), of which roughly half already have prose to transcribe and 13 are
one-line class entries — not 12 segments of fresh per-item work.

**R6's verbatim caveat above still travels, and MUST, because §2.7 narrows it rather than
retiring it.** Measured across all 35 gold cassettes: **19 of the 24** grounded candidates that
score `UNEXPECTED` today are retired by populating this data (79%); the residual **5** are
sub-sentence spans falling *inside* sentences that already carry a gold item, which §2.7's
sentence-level unit does not reach. Delete the caveat only when the sub-sentence class is
addressed too. See `evals/goldens/holdout/SPLITTING_EXCLUSION_INVESTIGATION.md` §11 and
`splitting/disposition_cost.py`.

**§6.3 of that investigation corrected R6's *"partly transcription from the exclusion logs"*
claim downward to ~11%, and that correction is itself scoped**: it was measured over the 9
surplus clauses, a subsample selected for annotator disagreement. Over the 21 sentences §2.7
actually reaches, 10 already carry a genuine disposition. Both figures are right for their own
denominator; use the second when estimating this work.

### R5 — startup self-check, so R1–R3 cannot fail silently

Before scoring any item, the harness MUST assert, for every locked gold item in scope, that
**each of its `obligor`/`obligee` values resolves iff the item's annotated `underspecified`
value requires it to.** A mismatch is a **hard startup failure naming the item and the alias**,
never a scored result. Without R5 every fixture defect in R1–R3 surfaces as a clause-8 failure
indistinguishable from an extraction error — which is precisely how a harness measures its own
setup and reports it as model quality.

---

## 22. The conforming blocker (v0.31) — OPEN DECISION, nothing changed

§8.3.1's v0.31 amendment changes exactly one locked item, `C14-02` (span `[184:253]` →
`[12:253]`, the only item tagged `shared_subject_split`). Conforming it is a two-line edit.
**It has not been made**, because restamping that item collides with two invariants that
each deserve an explicit decision rather than a convenient reading.

**Invariant A — one guideline stamp per scored set.** `run_scoring.guideline_version_from_items()`
raises when the 18 items stamp more than one version, on the ground that scoring items
annotated under different rulesets silently mixes two questions. Conforming `C14-02` alone
yields `{v0.28 ×17, v0.31 ×1}` and the scorer refuses to run. §10 permits mixed stamps
pre-freeze — batch 1 legitimately spanned six versions — so this invariant is **stricter than
§10 requires**, and may simply be wrong.

**Invariant B — `guideline_version` is a cassette-staleness dimension.** `Cassette.verify()`
treats a `guideline_version` mismatch as `StaleCassette`. Restamping all 18 items to `v0.31`
(the genuine conforming pass: the other 17 carry no `shared_subject_split` and conform
already) therefore invalidates **all 35 recorded cassettes** and demands a full re-record —
live model calls, and `C17-021` run 3 is known to be unobtainable at all.

**Why B looks like a real design defect rather than an inconvenience.** The guideline never
enters the model request. `prompts/` supplies the prompt; the corpus supplies the segment
text; the guideline governs only how the *answer is scored*, downstream and offline.
`cassette.py`'s own docstring justifies staleness in terms of *"the segment text, the prompt
version, or the model id"* — it does **not** argue for `guideline_version`, which was checked
anyway. Under the current rule the gold set can never be amended without re-spending model
calls, which inverts the purpose of recording cassettes and creates a standing incentive not
to correct a rule once found wrong — the exact failure this session has spent its time
undoing elsewhere.

### 22.1 Decision (v0.32): neither fix is adopted, and this is deferred on purpose

Two fixes were put forward — drop `guideline_version` from `Cassette.verify()`'s staleness
test while keeping it as provenance, and relax invariant A to permit mixed stamps pre-freeze.
**Both are REJECTED for now, and this is a decision, not an open recommendation.** A later
reader must not treat §22 as a to-do list.

**`C14-02` stays annotated under the superseded §8.3.1 v0.23 rule and continues to score
`MISSED`.** That is a known wrong number carrying an honest label — a tracked conforming gap
— and it is strictly better than the alternative on offer: a system in which correcting a
genuinely broken rule costs more than leaving it broken. Weakening either invariant so one
item becomes conformable would buy a marginally better score by making the harness
permanently less strict, which is the wrong trade in the wrong direction.

**REINFORCED, not re-litigated, by §7's cold second-annotator run (v0.43, 2026-08-29).**
`C14-02` is the single item the cold annotator did not match at all — exactly the predicted
consequence of staying unconformed, occurring independently rather than being re-argued here.
Nothing about this decision changes: `C14-02` still stays annotated under the superseded
§8.3.1 v0.23 rule, and whether this counts toward the "forcing function" described below is
left to that later session, not decided here.

**Why defer rather than solve it now.** The real question — how to handle a mid-flight
guideline correction against already-recorded cassettes — is a general one, and solving it in
the abstract against a sample of exactly one item invites a design fitted to that item rather
than to the problem. **The forcing function to wait for is a `v0.32`-or-later correction that
ALSO requires conforming**, i.e. a second, independent instance. At that point the question
has real shape, more than one case to generalise from, and a genuine cost to leaving it
unsolved. Until then this stays exactly as written: visible, tracked, and not quietly fixed.

**What must NOT happen in the meantime:** conforming `C14-02` alone (it yields mixed stamps
and the scorer will refuse to run), restamping all 18 items (it invalidates all 35 cassettes
and `C17-021` run 3 cannot be re-recorded at all), or relaxing a staleness dimension to route
around either.

### 22.2 Is v0.33 the second instance? **NOT DECIDED — deliberately held (v0.33)**

v0.33 queues three locked items for accept-set widening at the §10 freeze pass (`C02-03`,
`C11-01`, `C02-01` — §3.4's bounded exception). Those widenings **would** require conforming,
so the question arises immediately: does this satisfy §22.1's forcing function?

**The decision is to NOT decide yet, and the reason is the same one §22.1 itself gives.**
§22.1 declined to design against a sample of one. Ruling *now* that three queued
accept-set widenings constitute the second instance would repeat that error from the other
side — settling the general question against a scope estimated **in advance** of the pass that
determines it. The freeze pass conforms everything at once: `C14-02`'s §8.3.1 amendment, these
three widenings, and whatever batch 3 adds. **Its real, combined scope is knowable then and
only guessable now.**

**So the trigger is re-armed, not fired.** Re-evaluate at the freeze pass, against what is
actually on the table. Nothing in v0.33 is blocked by leaving this open: every v0.33 change is
forward-only or comparison-only, restamps nothing, and the three queued items keep scoring as
failures in the meantime — a stated understatement, which §9's inline disclosure reports.

### 22.3 Invariant B's real cost, measured for the first time (v0.49): staleness does not
disappear when a shared-segment item is restamped, it moves to the sibling

§22's invariant B was argued in the abstract — restamping an item invalidates its cassette,
demanding a live re-record. The v0.49 `C04-117` re-record (§10.1 F7's resolution, §9.2) is the
first time that cost was actually paid on a segment two gold items share, and it surfaced a
sharper shape than the abstract argument states.

`C04-117` backs **two** locked items, `C04-01` (stays `v0.28`) and `C04-02` (restamped `v0.48`
at the freeze pass, §10.1 F7). One cassette, one `guideline_version` field, two items with
different stamps sharing it — `Cassette.verify()` can only agree with one of them at a time.
Before this session, the cassette was recorded at `v0.28`: valid for `C04-01`, stale against
`C04-02`. Re-recording it at `v0.48` to unblock `C04-02`'s criterion-2 score flips this exactly:
now valid for `C04-02`, stale against `C04-01`. **The cassette did not go from stale to clean —
it went from stale-for-one-sibling to stale-for-the-other.** Nothing was gained for `C04-01`,
and nothing was lost for it either, beyond what was already true of the pre-v0.49 state read
the other way.

**Why this is worth a citable record of its own, separate from the v0.49 changelog entry that
disclosed it inline.** It is a **general property of a single-`guideline_version`-per-cassette
scheme**, not a fact about `C04-117` specifically: any segment backing two-or-more items whose
restamp history diverges will exhibit it, and the next occurrence should be recognised as an
instance of this rather than re-derived. It also sharpens §22's own framing — the abstract
argument treats "restamping invalidates the cassette" as if there is a clean before/after; the
real mechanism, now measured, is a **transfer of validity between the items that share the
recording**, not a simple gain or loss. `C04-01` is unaffected in practice today only because it
was never in criterion 2's denominator to begin with (its `known_gaps` question was never at
issue) — a future segment shared by two denominator-relevant items would make this transfer
directly costly rather than incidental, which is the case this record exists to make findable
before it happens.
