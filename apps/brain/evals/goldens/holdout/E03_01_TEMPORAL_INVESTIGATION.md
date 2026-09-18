# `E03-01`'s temporal — F19 investigation

**Ruled 2026-09-18, guideline v0.61 (§8.11).** Question as filed (§10.1 F19): *does `E03-01`
genuinely carry a masked §7 composition gap, as its own `annotator_notes` suggest but never
verify?*

**Answer: it carries a second gap, and the annotator's stated mechanism is wrong.** The tag added
is `lead_time_unrepresentable` (`REPRESENTATIONAL` / `INCOMPLETENESS`), not a composition tag.

Everything below was verified by execution against the production code, after a five-case
known-answer gate on `_classify_temporal` (Standing Principle 7). Nothing here is read off a
regex.

---

## 0. What was claimed

`E03-01`'s `annotator_notes`, written 2026-08-19 and flagged **plausible**:

> Note the temporal would fail even unredacted: the underlying obligation is recurring-with-lead-time,
> plausibly EVERY composed with RELATIVE_TO_TRIGGER, which IR v1 cannot represent (section 7
> composition gap).

Two separable claims: a **conclusion** (it would fail even unredacted) and a **mechanism** (a §7
composition gap between `EVERY` and `RELATIVE_TO_TRIGGER`). They do not stand or fall together,
and F19 was filed because only the first had ever been treated as the interesting one.

The clause, as the filing carries it:

> At least `**` before the `**` of each Calendar Quarter during the Term of this Supply Agreement,
> Kissei shall provide Rigel a rolling forecast …

---

## 1. The conclusion survives

Through the real `compile_candidate()` — not the classifier alone, the whole compile stage:

| `temporal_raw` | result |
| :--- | :--- |
| `At least ** before the ** of each Calendar Quarter during the Term…` (emitted 3 of 3 runs) | `UNMAPPABLE_TEMPORAL` |
| `At least thirty (30) days before the first day of each Calendar Quarter during the Term…` | `UNMAPPABLE_TEMPORAL` |

The redaction is **not** doing the work. The item owes a second gap, and `known_gaps` was
under-reporting why it cannot be scored.

## 2. The mechanism does not

### (a) Neither claimed operand is available for this text

| phrase | classifies as |
| :--- | :--- |
| `each Calendar Quarter` | `None` |
| `every Calendar Quarter` | `None` |
| `every 3 months` | `EVERY 3mo` |

`Duration` is `{amount: float, unit ∈ h/d/bd/w/mo/y}` with **no `UNRESOLVED` alias variant** —
unlike `DateRef` and `TriggerRef`, which both carry the two-state shape `SPEC.md` §4 calls a
deliberate convention. So a recurrence named by a **defined term** has no form at all. `EVERY` is
reachable here only through the paraphrase `every 3 months`, a constant-fold gold never performed
and which the guideline nowhere licenses.

### (b) The load-bearing failure is single-form expressiveness

Mechanical slot check over all five frozen forms:

| form | slots |
| :--- | :--- |
| `ByTemporal` | `datetime` |
| `WithinTemporal` | `duration`, `of` |
| `EveryTemporal` | `duration` |
| `DuringTemporal` | `start`, `end` |
| `RelativeToTriggerTemporal` | `direction`, `trigger` |

- carrying `{duration, direction, trigger}`: **NONE**
- carrying `duration` **and** `direction`: **NONE**

`at least ** before the **` is **one atomic timing element** needing all three. Pinned by
difference rather than asserted:

| phrase | classifies as |
| :--- | :--- |
| `at least 30 days before the first day of each Calendar Quarter` | `None` |
| `30 days before the first day of each Calendar Quarter` | `None` |
| `before the first day of each Calendar Quarter` | `BEFORE "the first day of each Calendar Quarter"` |

The form becomes available **only** once the lead time is stripped — and the lead time is the
content the clause is about.

### (c) The note omits `during the Term`

Which is §7's *actual* named operand. If this were a composition it would be **three-way**, not the
two-way one recorded.

## 3. The decisive test

**Granting free composition of all five v1 forms does NOT rescue this clause.**

Composition joins *whole forms*. No form holds the `{duration, direction}` pair a lead time needs,
so no composition of forms can hold it either. The nearest composable approximation,
`WITHIN 30d OF X` ∧ `BEFORE X`, denotes `X−30d ≤ t < X` — the **complement** of *"at least 30 days
before X"* (`t ≤ X−30d`). v1 cannot build it, and if it could it would state the opposite
constraint.

This is what separates the case from §7. §7's gap is real *because* each operand is an available
form and only their co-occurrence fails — that is why its resolution could be "compile as `EVERY`
alone, and warn." Here there is nothing to compile alone.

Hence a tag of its own. Kind `REPRESENTATIONAL` on §8.6.1's test (the IR has no form; this is not a
surface pattern rejecting input the IR could hold). Direction **`INCOMPLETENESS`**, reached
independently of the note: the IR drops the lead-time duration and keeps at most the bare
direction, so a monitor never checks the advance-notice period and misses a real breach.
`OVERSTATING` was considered and rejected on the semantics above — `WITHIN` would be a
*misstatement*, not an overstatement, and is unbuildable regardless.

## 4. The two annotators' agreement is not corroboration

Cold's `known_gaps` for this item is `["redacted_value"]` — **identical to gold**. At a glance that
reads as two independent annotators confirming one another.

They do not. Cold **explicitly considered and declined** the composed reading, and identified the
composed element as **`during the Term` (`DURING`)**:

> Also noted and not annotated: 'during the Term of this Supply Agreement' is a second, composed
> timing signal — §8's gap table records 'during the Term' as UNMAPPABLE_TEMPORAL … and an
> EVERY+DURING composition as EVERY-only-with-warning — so no reading of it changes temporal from
> null here.

Gold says `EVERY` ∘ `RELATIVE_TO_TRIGGER`; cold says the `DURING` limb. Two mutually inconsistent
characterisations of one clause, converging on one tag. **Set equality on `known_gaps` is agreement
about a tag, never about the mechanism behind it** — the same blind spot §7.1 already names for
`K`, reached one level down.

## 5. A guideline error that had already propagated

Cold's reasoning above rests on §8's gap-table row:

> `EVERY` + `DURING` composed | `EVERY` only, with a composition warning

That row states the **grammar** path. On the **extraction** path it is false:

| path | input | behaviour |
| :--- | :--- | :--- |
| extraction (`_classify_temporal`) | `every 30 days during 2026-01-01 .. 2026-12-31` | `None` → `UNMAPPABLE_TEMPORAL`, whole candidate rejected |
| extraction | `every 30 days during the Term` | `None` → `UNMAPPABLE_TEMPORAL` |
| grammar (`parse()` on a hand-built DSL) | `… EVERY 30d DURING 2026-01-01 .. 2026-12-31 …` | `EveryTemporal(30d)` + `ObligationCompositionWarning` |

`_EVERY_RE` is `$`-anchored after the unit, so a trailing `DURING` cannot survive classification.
The warn-and-degrade guarantee is **real** and **unreachable from extraction** — confirmed in both
directions rather than assumed.

**This is the fourth tracked instance of a guarantee proven at the grammar/DSL layer that the real
extraction path bypasses**, after (1) `UNLESS` absorption, (2) `ir_compile.py` never building an
`AndPredicate`/`OrPredicate` despite AST and grammar support (§17.3), and (3) the IR-Compiler
trailing-period bug. The signature is constant: the guarantee is real where it was tested, the
extraction path never reaches that layer, and **every instance was found by testing rather than by
reading**.

Unlike the first three, this one is also a **documentation** defect — and not an inert one. The row
was cited by an annotator as a reason not to tag, so a layer confusion in a reference table
propagated into the gold set itself. §8's row is corrected rather than merely annotated.

## 6. Cost, measured before and after by a real `run_scoring.run()`

| | in-force criterion 2 | all-items | cassette-unscoreable |
| :--- | :--- | :--- | :--- |
| baseline | `3/10 = 30.0%` | `5/15 = 33.3%` | 21 |
| **ruled (tag, no restamp)** | **`3/10 = 30.0%`** | **`5/15 = 33.3%`** | **21** |
| rejected alternative (tag + restamp) | `3/10 = 30.0%` | `5/14 = 35.7%` | 22 |

**Nothing moves.** `redacted_value` already excluded the item from the in-force denominator and
membership is by *any* excluding tag (§9's v0.22 rule, untouched).

**The stamp is deliberately unchanged at `v0.28`, and the alternative was measured rather than
argued.** `known_gaps` is not one of §5's eight scored clauses, so this cannot change how the item
scores. Restamping would stale `E03-005`'s three cassettes and move all-items `5/15 = 33.3%` →
`5/14 = 35.7%` **purely by dropping a `PARTIAL` item out of the denominator** — a published figure
improving for no improvement, in the direction §3.6's monotone-widening hazard exists to guard.
Same refusal as `C11-01`'s v0.52 record-only correction, on a measurement rather than a
presumption.

## 7. Effect on F17 — none, and this was the second half of the filed question

F17 is the kind-scoped `gap_agreement` band. Measured on a scratch copy of the goldens:

```
kind-scoped d_* (in_force_scope), 31 matched pairs
  baseline                : d_gold=18 d_cold=18 d_int=17 d_uni=19   band (17,19)
  + lead_time_unrepresentable : d_gold=18 d_cold=18 d_int=17 d_uni=19   band (17,19)
```

Unchanged, and **structurally incapable of changing**: `redacted_value` is `WITHHELD_VALUE`,
already an excluding kind, so `E03-01` is out on both sides before and after — under the legacy
emptiness scope, under the kind scope, and under any sub-population including the conforming band.
F19 is exclusion-neutral for F17 exactly as the entry predicted.

**It is not neutral for `G`, which the entry did not anticipate.** The pair moves from equal-sets
(agreement, uncounted) to `SUPERSET`:

```
G        6/31 -> 7/31   (Wilson95 lower 9.19% -> 11.40%)
G_swing  1/31 -> 1/31   (BANDED, unchanged)
```

**CORRECTION TO THIS RULING'S OWN FIRST PRICING, made before it landed and recorded rather than
quietly fixed: F19 is NOT verdict-neutral.** The pricing above was offered as "verdict `REDESIGN`
both ways", which is true of the **all-pairs** `G` and incomplete. The **conforming-scoped** `G`
(§5.1 clause 9) is a second instrument with its own `n`, and there the tag tips it:

| scope | published run | current set |
| :--- | :--- | :--- |
| all pairs | `G=6/31` `G_swing=2` band `(15,17)` — REDESIGN | `G=7/31` `G_swing=1` band `(16,17)` — REDESIGN |
| conforming only | `G=4/26` `G_swing=1` band `(14,15)` — **DIAGNOSE** | `G=5/26` `G_swing=0` band `(15,15)` — **REDESIGN** |

So v0.48's framing that restricting `G` to conforming pairs *"moves it off its own REDESIGN
trigger"* is **true of the published run and false of the current set**. No headline figure moves
— criterion 2 and `K` are untouched, confirmed by a real run — but *"no verdict moves"* would have
been wrong, and the error was mine rather than the instrument's.

**The part of v0.48's finding that was really about scoreability survives intact**: `G_swing` on
conforming pairs is `0` and the band is the point `(15,15)`, so the two annotators still do not
disagree about which conforming items are **scoreable**. What moved is `G_overall`, which counts
*any* set inequality — including the superset F19 creates. Worth separating, because CLAUDE.md's
REDESIGN entry cites the `(15,15)` point specifically, and that citation is unaffected.

## 8. What this exposed about the `G` reproduction — now fixed, remainder filed as F20

Checking F19's cost against `G` surfaced a defect in how `G` is reproduced. The real-data test read
`known_gaps` **live** from `batch*/items/` while pinning the population as a transcribed 32-id
list.

**Four items have drifted since the seal commit `628f67c`** (measured at that commit, not
reconstructed from the rulings' prose):

| item | sealed `known_gaps` | live |
| :--- | :--- | :--- |
| `C04-02` | `mutual_obligation` | *(empty)* — F7 |
| `C10-01` | `compound_action`, `exception_unsupported` | + `action_not_in_taxonomy` — F11 |
| `E01-01` | `exception_unsupported` | + `compound_action`, `action_not_in_taxonomy` — F8 |
| `E03-01` | `redacted_value` | + `lead_time_unrepresentable` — F19 |

**And the published `G = 6/31` had been surviving those drifts by coincidence, not by stability**:
`C04-02` leaving `swing` and `C10-01` joining `superset` cancelled exactly. Recomputed at the
sealed tags the run really was `G=6/31, G_swing=2/31, band (15,17)`; live today (pre-F19) it was
`G=6/31, G_swing=1/31, band (16,17)`. **The same `G` for different reasons**, and nothing in the
suite could tell those apart. F19 breaks the coincidence.

**Closed here**, mirroring the fix K received at v0.53 for `C11-02`: the population is now derived
from the sealed `comparison.json` (failing loudly if a published item goes missing), a `PRE_TAG`
map holds the four drifted items' sealed tags, and a genuine **historical** reproduction test now
sits alongside the live-set one. A further test asserts the two disagree, so a future coincidence
cannot be misread as stability, and another fails if a `PRE_TAG` entry ever stops overriding
anything.

**Filed as F20, deliberately not taken here:** `comparison.json` seals the population and K's
per-clause fails but **not** `known_gaps` — G did not exist when it was written — so the override
map is the only mechanism available and must be maintained by hand. Whether a future §7 run should
seal `known_gaps` into its artifact, making override maps unnecessary, is a design question about
the next run, not a repair to this one.
