# §7 cold second-annotator check — result

**Computed 2026-08-29, after the cold output was sealed and committed (`f3f958b`,
rolling SHA-256 `e5d0b42a…d87623`) and after PREREGISTRATION.md was fixed.** Nothing in
the pre-registration was changed after this number was known.

## Verdict

| | |
| :--- | :--- |
| **K** | **14 / 32 = 43.8%**, Wilson₉₅ **[28.2%, 60.7%]** |
| **Pre-registered band** | **≥6 → REDESIGN** |
| **Escalation rule** | **not triggered** (see gradient below) |

**This is a cold second-annotator check, not a held-out one**, and K carries all four
PREREGISTRATION §1 disclosures: correlated model-family error (K is a lower bound), no
reviewer blinding, guideline leakage, and within-pass order-dependence.

## The structural finding, which is larger than K

**41 cold items against 32 drafter items over the same 22 segments** — and yet
**spans agree at IoU ≥ 0.95 on 29 of 32 items**, with 6 exact at 1.000.

The two annotators are finding *the same obligations in the same places*. Essentially all
the disagreement is in **how those obligations are labelled**, plus **how many items one
sentence yields**. Span identification — the thing the compiler's grounding gate protects
and §21 criterion 1a certifies — is not where this set is weak.

## K by leak level (D4 channels 1–3)

| Level | K | rate | Wilson₉₅ | disagreeing items |
| :-- | :-- | ---: | :--- | :--- |
| **L0** | 0/3 | 0.0% | [0.0%, 56.2%] | — |
| **L1** | 1/3 | 33.3% | [6.1%, 79.2%] | `C10-02` |
| **L2** | 13/26 | 50.0% | [32.1%, 67.9%] | `C02-03` `C04-01` `C04-03` `C06-01` `C10-01` `C11-01` `C13-03` `C14-02` `C14-04` `C17-01` `C17-02` `C22-02` `E03-01` |

**The gradient runs the opposite way to the one the escalation rule anticipated**, so the
rule does not fire. Disagreement is *highest* on the most-leaked items, not lowest.

**This must not be read as "leakage improves nothing."** Leak level is **confounded with
difficulty**, and the confound plausibly dominates: the guideline works through exactly
those segments *because they were hard* — they are its motivating cases. L0 items are
uncited precisely because they raised no rule question. With N = 3 / 3 / 26 the gradient
cannot separate the two effects, and no attempt is made here to. **Reported as
uninterpretable in its intended direction**, which is itself the finding: a leak-controlled
comparison is not available from this corpus, because the guideline was authored from it.

## Channel 4 — item-count and exclusion decisions

The channel the guideline never states for any segment, and therefore the one clean
signal that survives on L2 items.

| | |
| :--- | :--- |
| Segments agreeing on item count | **16 / 22 = 72.7%** |
| Segments disagreeing | **6 / 22 = 27.3%**, Wilson₉₅ [13.2%, 48.2%] |
| Surplus cold items | 10 |
| Unmatched gold items | 1 (`C14-02`) |

Disagreeing segments: `C04-117` 2→3 · `C11-094` 1→3 · `C17-021` 1→3 · `C17-066` 1→3 ·
`E03-005` 1→2 · `E08-005` 1→2. **Every disagreement is the cold annotator finding *more*
items than the drafters, never fewer** — a directional signal, not noise, and one that
points at §2's exclusion rules and §4.3's splitting tests rather than at field labelling.

## Clause-level profile — where the disagreements actually are

23 clause failures across the 13 matched disagreements:

| clause | failures |
| :--- | ---: |
| 5 `object_class` | 6 |
| 2 `action` | 5 |
| 3 `obligor` | 3 |
| 4 `obligee` | 3 |
| 6 `temporal` | 2 |
| 7 `conditions` | 2 |
| 8 `underspecified` | 1 |

**The accept-set clauses (2 and 5) carry 11 of 23**, and 5 of the 13 matched disagreements
fail on *nothing else*: `C02-03`, `C10-01`, `C17-02`, `C22-02`, `E03-01`.

## Attribution — three of the fourteen are already-known gold-side problems

§7 is explicit that K counts *disagreements, not confirmed drafter errors*, so these stay
in the count. But they must be named, because they are not new information:

- **`C02-03` and `C11-01`** are two of the three items CLAUDE.md and §3.4's bounded
  exception **already queue for accept-set widening at the §10 freeze pass**. The cold
  annotator independently produced `INVOICE` and `principal_interest` — i.e. it landed on
  the very labels that widening exists to admit. This is the queued widening being
  independently confirmed as necessary, not a fresh defect.
- **`C14-02`** is the single unmatched gold item, and it is the item §22.1 **deliberately
  retains** un-conformed under the superseded §8.3.1 v0.23 rule, with a documented span
  that is known wrong. Its disagreement here is the predicted consequence of that decision.

## Two disagreements land exactly on a convention that was never validated

**`C04-01`** — gold quotes a condition as *"further provided that…"*, cold as
*"provided that…"*: a **quote-extent** disagreement. **`C13-03`** — gold records one
condition entry, cold splits the same text into two: an **entry-count** disagreement.

These are precisely the two conventions §3.8.2 writes down for gold's side while stating
in terms that **neither is validated against anything and neither may be assumed correct**.
CLAUDE.md carries the matching open item: the Tier-B `v4` probe, *approved and never run*.
This check does not settle those conventions, but it is the first independent evidence that
they are genuinely underdetermined rather than merely unvalidated — and the evidence comes
from a second annotator rather than from the model, which the probe cannot substitute for.

**Two further disagreements (`C04-03`, `C14-04`) are `BY` vs `RELATIVE_TO_TRIGGER`** on
`by <alias>` phrasing — a §3.7 temporal-form ambiguity between two of the five forms, on
which the guideline gives no discriminating test.

## Two sensitivities — explicitly NOT the pre-registered rule

Reported because they bound the result, not to replace it. **The headline stays 14/32.**

**A — accept-sets compared by intersection.** §5 clause 2/5 test the prediction against
*gold's* accept-set. If instead the two annotators' accept-sets merely had to intersect,
4 items flip (`C02-03`, `C17-02`, `C22-02`, `E03-01`) — in each, cold's own accept-set
contains gold's chosen value. **K → 10/32 = 31.2%**, Wilson₉₅ [18.0%, 48.6%]. **Still
REDESIGN.** The interesting part is not the number but what it says: on those four the
annotators *agree the label is uncertain* and differ only on which point of a shared
uncertainty to name.

**B — case-insensitive party comparison.** `C10-02` has gold `the Supplier`/`the
Distributor` against cold `The Supplier`/`the distributor`, differing in case alone; §5's
unresolved-party rule normalizes whitespace but not case. **No item flips** — `C10-02`
fails on `action` and `object_class` regardless. **K unchanged at 14/32.** Recorded because
guideline §21 R2 flags this case-sensitivity trap for the scoring harness, and it is now
measured: it costs nothing here.

## What REDESIGN does and does not mean here

The verdict is reported as the pre-registered bands give it, unsoftened. But the diagnosis
is narrower than the word suggests, and the evidence supports saying so:

- Span identification is **not** implicated (IoU ≥ 0.95 on 29/32).
- The failures concentrate in **accept-set authoring breadth** (§3.4/§3.6, 11 of 23 clause
  failures, with 2 items already queued for widening) and in **splitting/exclusion**
  (channel 4 at 27.3%, all in one direction).
- Two named guideline areas already carrying open, documented questions — §3.8.2's
  conditions conventions and §3.7's temporal-form boundaries — account for four more.

**A caveat on the band itself, which is a caveat and not a licence to move it.** §7's
thresholds were designed for a genuinely held-out sample annotated under a *frozen*
guideline. This set is none of those things: nothing was withheld, the guideline is v0.41
DRAFT and unfrozen, and it was authored from these very items. The bands were nonetheless
fixed in advance and K is reported against them as fixed. **Any argument that the band is
mis-calibrated for this instrument is an argument to be made now, in the open, and applied
to the *next* run — not applied retroactively to this one.**
