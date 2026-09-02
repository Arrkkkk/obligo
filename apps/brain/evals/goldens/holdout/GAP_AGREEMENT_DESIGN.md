# `known_gaps` agreement — design note (APPROVED, IMPLEMENTED)

> **v0.48 UPDATE — three figures in this document moved, and this note is the disclosure owed
> with them. Nothing below is edited; the original values are the 2026-08-29 run's and stay
> readable as written.** The §10.1 freeze-pass batch restamped five gold items, three of which
> carry `known_gaps` changes, so every `G`-family figure computed from the live gold set moves:
>
> | figure | 2026-08-29 (as written below) | after v0.48 |
> | :--- | :--- | :--- |
> | `n` | 31 | **31** (unchanged) |
> | `G` | 6/31 → REDESIGN | **6/31 → REDESIGN** (unchanged) |
> | `G_swing` | **2/31** — `C04-02`, `C10-02` | **1/31** — `C10-02` |
> | `D_gold` / `D_int` / `D_uni` | 15 / 15 / 17 | **16 / 16 / 17** |
> | band | (15, 17) | **(16, 17)** |
> | conforming-only `G_swing` / band | 1/26, (14, 15) | **0/26, (15, 15)** |
> | superset items | `C04-03`, `C14-01`, `E01-01` | **+ `C10-01`** |
>
> **All of it is three rulings, itemised rather than aggregated.** F7 removed
> `mutual_obligation` from `C04-02`; cold had never assigned it, so **gold moved onto cold** —
> the item stops swinging and enters `D_gold`. F11 added `action_not_in_taxonomy` to `C10-01`,
> a tag cold does not use at all, making gold a strict superset there. F8 added two tags to
> `E01-01`, already a superset item.
>
> **The substantive result is the conforming-only line: the band collapses to a POINT (15, 15)
> and `G_swing` reaches 0.** Among conforming pairs the two annotators no longer disagree at
> all about which items are scoreable — which is the instrument defect CLAUDE.md's REDESIGN
> entry names as its highest-priority open item. **It does NOT close that item**: the all-pairs
> band is still (16, 17), the five non-conforming pairs are excluded rather than resolved, and
> §6's `kind`-axis question (§10.1 F9) is untouched.
>
> **Neither verdict changed.** `G` is still REDESIGN and `G_swing` still BANDED, so this is a
> real but bounded movement — the same disclosure shape §3.6.1's v0.45 correction established
> for a retroactive edit that moves an `A`-side published measurement: state the effect at its
> true size, neither freeze the computation nor inflate the result. **The direction is toward
> agreement, and it was not sought**: all three rulings were made on their own grounds before
> any `G` was recomputed.


> **STATUS, corrected in place 2026-09-01 (guideline §10 requires live status statements to be
> corrected rather than struck).** The banner below was accurate when written and is now false in
> both its claims. **The design IS implemented** — `evals/harness/gap_agreement.py` and
> `report.py`'s G7, at guideline v0.43 — and a guideline section now exists: **§5.1**, which rules
> the architectural question §1 below leans on. Two amendments follow from that ruling:
>
> 1. **§1's disqualification of option (a) stands, but its stated ground was an assumption at the
>    time, not a ruling.** *"§5 is a gold-vs-prediction predicate… **This alone settles it**"*
>    pre-answered the question `RESULTS.md` was simultaneously recording as *"never asked in this
>    project and [it] should be asked before either fix."* §5.1 has now asked and answered it —
>    **two predicates** — and re-derived the conclusion independently from clause 2 rather than
>    from `known_gaps`. So (a) is correctly dead and §1's other two grounds were always sound;
>    the ordering was wrong and is logged rather than tidied away.
> 2. **`G` is not "beside" K — it is §5.1 clause 9 of the annotator predicate `A`.** Nothing about
>    the metric changes: §2's *"never added, averaged, or reported as one number"* is unchanged and
>    §6's deferrals stand. What changes is that G now has a stated home rather than orbiting a
>    predicate it was explicitly not part of.
>
> **And one measured consequence for §6's deferred question.** Under `A`'s conformance gate,
> `C14-04` leaves the matched set (cold wrote an off-taxonomy `action` slot), taking with it the
> **only** instance of `G_disjoint` — which falls to **zero**, alongside `G = 4/26 → DIAGNOSE`
> (from 6/31 → REDESIGN) and `G_swing = 1/26 → BANDED`. §6 defers *"can §8 tags legitimately
> co-apply?"* to the tag-vocabulary review on the strength of that single case. **The case was a
> conformance artifact, so the question now has no evidence at all — which is not the same as
> being answered**, and the review must not read the empty cell as a result.

**Status (2026-08-29, superseded — see above): reviewer-approved as a design. No code, no
guideline section, no `report.py` change exists for any of it.** This note is the specification a
future session implements against; it is not a record of something built.

**Why it exists.** §7's cold second-annotator run (`RESULTS.md`) found that `known_gaps` is
not one of §5's eight scored clauses, so no disagreement on it can move K — while the two
annotators disagree on it for **19.4% of matched items**, moving §9's in-force criterion-2
denominator from **15 scoreable items to 17**. The REDESIGN verdict was therefore computed
by an instrument blind to a disagreement class that swings the number it exists to support.
**Until this is implemented, no K is trustworthy — including any K computed to check whether
the REDESIGN response worked.**

---

## 1. Option (a) is disqualified, on three independent grounds

The alternative was a **ninth §5 clause** requiring `known_gaps` to match. It is eliminated
structurally, not by preference. Verified by reading the code, not assumed:

1. **It could not see the problem it was proposed to fix.** §5 is a *gold-vs-prediction*
   predicate. This disagreement is *gold-vs-gold* — two annotators. A ninth §5 clause would
   never fire on the thing that motivated it. **This alone settles it.**
2. **The pipeline structurally cannot emit the field.** `known_gaps` appears **zero times
   anywhere under `src/`**. `ast.Obligation` carries exactly `modality, obligor, action,
   obligee, object, temporal, conditions, source, confidence, underspecified,
   missing_fields`. `evals/harness/report.py:326` reads the field from **gold only**:
   `known_gaps=tuple(gold.get("known_gaps", ()))`.
3. **Its damage would be worse than "unreachable `FULLY_CORRECT`."** Gap-carrying items are
   *already* excluded from the in-force denominator (`len(known_gaps)==0`), so a ninth clause
   would be **vacuous exactly where the criterion is**, and **destructive on the all-items
   figure §9 reports alongside**, where every gap-carrying item would fail it. That collapses
   the all-items numerator into the in-force numerator over a larger denominator, **killing
   §9's diagnostic split** — a silently dead diagnostic, not merely a harsh one.

---

## 2. The metric — `G`

Named distinctly from `K` on purpose: the two are different instruments and must never be
added, averaged, or reported as one number.

**Unit:** item-level set comparison of `known_gaps` between the two annotators.

**Scope: matched pairs only** (n = 31 in the 2026-08-29 run). *Confirmed decision.* An
unmatched gold item carrying a gap tag is arguably a swing, but it is **already counted in
K** (as `UNMATCHED`) and **in channel 4** (as an item-count disagreement); counting it a
third time would conflate three instruments measuring three different things. The exclusion
is stated wherever G is published.

**Decomposition — three classes, because they have different consequences:**

| class | definition | consequence | 2026-08-29 |
| :--- | :--- | :--- | :--- |
| **`G_swing`** | exactly one side's set is empty | **moves the criterion-2 denominator** | **2/31** — `C04-02`, `C10-02` |
| **`G_superset`** | both non-empty, one strictly contains the other | annotators agree the item is gap-carrying, disagree which/how many | 3/31 — `C04-03`, `C14-01`, `E01-01` |
| **`G_disjoint`** | both non-empty, neither contains the other | annotators disagree about *which* gap the item has | 1/31 — `C14-04` |
| **`G`** | any set inequality (the union of the three) | annotation quality of the §8 taxonomy | **6/31 = 19.4%** |

**Two thresholds, not one, and this is load-bearing.** `G_swing` and `G` answer different
questions with different consequences. A single threshold would let five superset
disagreements mask one swing, or a single swing hide inside an otherwise-clean taxonomy.

---

## 3. `G_swing` thresholds — derived from consequence

`G` has no §7 ancestor to inherit rates from, so the anchor is the **consequence** rather
than a prior band. At `D = 15`, moving the denominator by one moves an 80%-shaped figure by
roughly five percentage points:

| F | D | criterion 2 |
| --: | --: | --: |
| 12 | 14 | 85.7% |
| 12 | **15** | **80.0%** |
| 12 | 16 | 75.0% |
| 12 | 17 | 70.6% |

**A single swing item is already material against §21's ≥80% bar.** The gate is therefore on
the Wilson₉₅ **upper** bound — what the observation rules out, not what it estimates:

| `G_swing` / n | Wilson₉₅ upper | verdict |
| :--- | ---: | :--- |
| **0** | 11.0% | **STABLE** — criterion 2 quotable as a point figure; the band is still displayed |
| **1–2** | 16.2–20.7% | **BANDED** — criterion 2 quoted **only as an interval**, never a point estimate |
| **≥3** | ≥24.9% | **UNREPORTABLE** — fix the tagging rule before quoting any criterion-2 figure |

**Current state: `G_swing = 2/31` → BANDED.**

**Power, stated as a tripwire exactly as §7 requires of K.** A `G_swing ≤ 0` gate detects a
true swing rate of 10% with probability 0.962 at n=31, and 5% with probability 0.796. **It
cannot certify a low rate.** Published `G_swing` figures say so.

---

## 4. `G` (overall) thresholds — Wilson-anchored to K's own targets

`G` measures the same *kind* of thing K does — annotator disagreement on a field — so it
reuses K's evidential-strength anchors rather than inventing new ones: the Wilson₉₅ **lower**
bound at each trigger (0.0279 for DIAGNOSE, 0.0807 for REDESIGN, per `PREREGISTRATION.md` §4).

| `G` / 31 | Wilson₉₅ lower | verdict |
| :--- | ---: | :--- |
| **0–2** | ≤0.0179 | **TAXONOMY OK** |
| **3–5** | 0.0335–0.0709 | **DIAGNOSE** — §8's tag vocabulary needs review |
| **≥6** | ≥0.0919 | **REDESIGN** — §8's tag vocabulary is not fit for scoring |

(3/31 gives lower 0.0335, first to clear 0.0279; 6/31 gives 0.0919, first to clear 0.0807 —
5/31 falls short at 0.0709.)

**Current state: `G = 6/31` → REDESIGN, landing exactly on the trigger.** This is a
**second, independent REDESIGN signal**, and it points at §8's tag vocabulary rather than at
any field rule — a different target from everything K's own verdict implicated.

---

## 5. The denominator-sensitivity band

Three denominators over matched items:

| | definition | 2026-08-29 |
| :--- | :--- | ---: |
| **`D_gold`** | `{i : gold.known_gaps == []}` — the authoritative annotation | **15** |
| **`D_int`** | `D_gold ∩ D_cold` | 15 |
| **`D_uni`** | `D_gold ∪ D_cold` | 17 |

Criterion 2 is recomputed over each; the band is `[min, max]`. The point figure comes from
`D_gold`.

**Mandatory display rule — the same standing as §9's "both numbers published together,
neither presented alone" and G6's inline numerator disclosure. The point figure may never be
printed without the band:**

```
CRITERION 2 (IN FORCE, §9.1 — len(known_gaps)==0):
    <pt>%   [band <lo>%–<hi>%]   over D=15 [15–17]   G_swing=2/31 → BANDED
```

**A directional finding that belongs with the design, not in a footnote.** Every swing runs
the same way: gold tags a gap where cold does not. The set `gold-clean but cold-gappy` is
**empty**. Gold is systematically the more gap-liberal annotator, so its in-force denominator
is **conservative, not inflated** — mildly reassuring for criterion 2's validity. But the
same fact means **gold may be excluding items IR v1 can actually represent**, which
*understates* criterion 2's coverage. That is a different problem from the one this metric
was built for, and it interacts directly with §9.1's own reachability argument. Flagged, not
solved here.

**What is computable today and what is not.** Only the denominator side. The numerator needs
a scorer run, and only 12 of the 22 segments have cassettes — the 32-item set has never been
scored end to end. `D = 15 [15–17]` is real now; the percentages are not.

---

## 6. Explicitly deferred

> **CLOSED 2026-09-02 — ANSWERED, not withdrawn, and the deferral's own reasoning is corrected.**
> The §8 tag-vocabulary review this section defers to has now run (guideline §8.2 correction,
> §10.1 F7–F10). Three findings, in the order they bear on the text below:
>
> 1. **The question was already settled three times before it was deferred.** Tags **can**
>    co-apply: v0.22's list schema exists *because* they do (`C14-01`'s own notes call it *"the
>    FIRST GENUINE MULTI-GAP ITEM in the gold set, and the item that forced the v0.22 known_gaps
>    list schema"*); §9's v0.22 rules legislate for it directly (*"a two-tag item is scored
>    identically to a one-tag item"*, *"per-tag figures are non-exclusive and MUST NOT be
>    summed… because one item may carry several"*); and §8.3's v0.28 F2 branch 3 rules an explicit
>    instance (*"tag `compound_action` **and** `action_not_in_taxonomy`. **Both apply**… Settled
>    here rather than left to be discovered."*). **3 of the 32 locked items carry two tags today.**
> 2. **The inference below runs backwards, and that is the substantive correction.** *"If tags can
>    legitimately co-apply, plain set inequality is over-strict and `G_disjoint` overcounts"* does
>    not follow. If both tags truly apply the correct set is `{both}`, so an annotator writing only
>    one has **under-tagged** — a real defect that set equality correctly catches. Co-application
>    makes strict set equality **more** correct, not less. Over-strictness would require two tags
>    to be **alternative encodings of one fact**, which is a different property (vocabulary
>    disjointness) that this section never named.
> 3. **That different property was real, was found, and is fixed.** Every pair in the 11-tag
>    vocabulary was checked. Exactly one was an alternative encoding —
>    `unless_unsupported`/`exception_unsupported`, the same tag under two names, both live in
>    `SECTION_8_TAGS` while guideline §8.2's own Rule paragraph still mandated the retired one.
>    Measured: an annotator following that paragraph literally moves **`G` from 4/26 (DIAGNOSE) to
>    7/26 (REDESIGN)** and `G_disjoint` from **0 to 5**. Corrected in place at guideline v0.46.
>    Every other pair is disjoint by construction — `within_preposition` /
>    `relative_trigger_preposition` explicitly so, under §8.9's own boundary paragraph.
>
> **So `G` stays on strict set equality, and the caveat published with it is withdrawn rather than
> carried forward.** The three-way decomposition in §2 is unchanged. What the banner at the top of
> this file warned about — *"the review must not read the empty cell as a result"* — was heeded:
> `G_disjoint = 0` was **not** treated as evidence either way, and the question was closed on the
> guideline's own prior rulings instead.
>
> **What did NOT close.** The two applicability-criterion disagreements the review found in place
> of an equivalence problem — §8.4.1's trigger (`mutual_obligation`, 2 of the 4 surviving `G`
> disagreements) and §8.3's branch 2/3 precedence — are **reviewer rulings**, queued as guideline
> §10.1 **F7** and **F8**. Neither is a defect in this metric.


**Tag equivalence is NOT decided by this metric's definition.** `C14-04`'s disjoint case —
gold `action_not_in_taxonomy` against cold `relative_trigger_preposition` for the same item —
suggests §8's tags may **co-apply** in practice, one annotator naming the action problem and
the other the temporal one for a single item. If tags can legitimately co-apply, plain set
inequality is over-strict and `G_disjoint` overcounts.

~~**This is deferred to the §8 tag-vocabulary review that `G = 6` now demands**, and must not
be settled inside the metric in isolation — defining equivalence to make a number look better
is exactly the post-hoc adjustment this project's pre-registration discipline exists to
prevent. Until that review rules, `G` is computed on strict set equality and the caveat is
published with it.~~ **Superseded — see the CLOSED banner at the head of this section. The
discipline it states was honoured: equivalence was not redefined, and the number moved only
because §5.1's conformance gate removed two items on independent structural grounds. Note also
that `G = 6` no longer holds and so no longer "demands" anything — the review ran at `G = 4/26`,
DIAGNOSE.**

**Per-run, not cumulative.** `G` and `G_swing` are computed per run, consistent with K's own
treatment. *Confirmed decision.*
