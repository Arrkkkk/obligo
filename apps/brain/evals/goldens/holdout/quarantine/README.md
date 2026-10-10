# What rejects the three `EXTRACTED_THEN_QUARANTINED` in-force items

Investigation ordered 2026-10-10, after §10.4.1 established that **8 of the 12 non-numerator
in-force items fail before a single clause is scored**, and that 3 of those 8 are quarantines
rather than extraction or alignment failures:

| item | segment | IoU of the best candidate | runs quarantined |
| :-- | :-- | --: | :-- |
| `C04-03` | `C04-087` | 0.988 | 3 of 3 |
| `C04-15` | `C04-017` | 0.941 (r1), 1.000 (r3) | 2 of 3 |
| `C17-03` | `C17-006` | **1.000** | 3 of 3 |

**Method: replay only, zero spend.** `run_scoring.replay_segment` was wrapped so the real
`PipelineResult.quarantined` and `.rejected` records were captured for these three segments while
the rest of the pass ran untouched. **GATE (Standing Principle 7): the instrumented run had to
reproduce the published in-force `6/18` before anything below was read.** It did.

---

## 1. There is ONE cause, not three — and the loop stops the SAME way every time

**`UNMAPPABLE_TEMPORAL` in 9 of 9 quarantine events.** No other `failure_reason` appears for any
of the three items on any run. And `QuarantineCause` is **`REPAIR_MADE_NO_PROGRESS` in 9 of 9** —
never `REPAIR_BUDGET_EXHAUSTED`, never `NO_ACTIONABLE_HINT`.

Every quarantined candidate grounded at **tier `EXACT`**, so every `temporal_raw` below is
**verbatim contract text**, not a paraphrase — the grounding gate guarantees it, which is why no
separate check of the source was needed for that claim.

## 2. The one cause splits into TWO mechanisms, and only one of them is fixable in the classifier

### 2a. `C04-03` — REACHABILITY. Gold's own form is representable; ONE PREPOSITION blocks it.

| run | `temporal_raw`, verbatim |
| --: | :-- |
| 1 | `on the Delivery Date ("Delivery")` |
| 2 | `on the Delivery Date` |
| 3 | `on the Delivery Date` |

Gold's temporal is `BY` + alias `"the Delivery Date"`. Verified by execution through the
production `_classify_temporal()`, with a known accept and a known reject gated first:

```
by the Delivery Date               -> BY "the Delivery Date"      <-- gold's own form
on the Delivery Date               -> None
on the Delivery Date ("Delivery")  -> None
```

**So the IR can hold this obligation exactly as gold annotates it. `_BY_RE` demands the literal
`by`, and the contract writes `on`.** That is §8.6/§8.9/§8.13's family — a surface preposition the
production regex will not accept — and it is the *opposite* kind of failure from 2b.

**`C04-03` IS CURRENTLY UNTAGGED FOR THIS**, carrying only `corpus_artifact_in_span`
(`CORPUS_DEFECT`, which *enters* §9.1's denominator). See §4: this raises a conformance question
and this investigation deliberately does not rule it.

### 2b. `C04-15` and `C17-03` — REPRESENTATIONAL. No legal form exists at any wording.

| item | run | `temporal_raw`, verbatim |
| :-- | --: | :-- |
| `C04-15` | 1, 3 | `During the Term of this Agreement` (on BOTH the `SUPPLY` and `PURCHASE` candidates) |
| `C17-03` | 1, 2 | `During the applicable Term of any Service` |
| `C17-03` | 3 | `During the applicable Term` — **after two repair calls narrowed it** |

```
During the Term of this Agreement          -> None
During the applicable Term of any Service  -> None
During the applicable Term                 -> None   <-- the repaired phrase
during 2026-01-01..2026-12-31              -> DURING 2026-01-01 .. 2026-12-31
```

Gold's temporal on both items is **`null`** — the untagged defined-term-period gap §10.1 F25's
cost note prices and which v0.68 deliberately kept apart from F25's own event-bounded class. So
the model quotes a period gold **deliberately omits**, and the whole candidate dies on it.

**`C17-03` run 3 is the sharpest single data point in this investigation: the repair loop DID
spend budget (`attempts=2`, `repair_calls=[1, 2]`), DID narrow the phrase, and still failed** —
because no narrowing of a named period produces a legal `DURING`, which requires a mandatory
two-slot date pair. This is the same unsatisfiable-instruction shape already tracked for the
`within` class (the repair prompt asks for "just the timing phrase" where the grammar has no
production for it), now **attested for `DURING` as well**.

## 3. A third, smaller finding: `NOT_EXTRACTED` conflates two different things

`C04-15` run 2's miss diagnosis is `NOT_EXTRACTED@IoU0.000`, which reads as *"the model emitted
nothing at this span"*. It did not. **It emitted both candidates and both were rejected at
GROUNDING with `SPAN_NOT_FOUND`** — the span text it returned was not a verbatim substring.

So `NOT_EXTRACTED` means *"no typechecked obligation aligned here"* and covers both *nothing was
emitted* and *something was emitted and failed to ground*. That is one level deeper than the
already-tracked finding that a bare `MISSED` reads as an extraction failure when the clause was
in fact extracted and quarantined. **Not fixed here** — the miss-kind taxonomy is part of the
scoring instrument, which is F37's and F40's posture: a diagnosis is not changed inside an
investigation commit.

## 4. OPEN, NOT RULED: `C04-03`'s gold temporal versus §8.9

§8's gap table already names the shape — *`upon` / `following` / `prior to` / `on` / `at` /
`as of` + trigger → `UNMAPPABLE_TEMPORAL`*, tagged `relative_trigger_preposition`, because
`_RELATIVE_RE` accepts only `before`/`after`; and §8.9's rule maps **`on` → `after`**. Gold
instead annotates `BY "the Delivery Date"` with **no tag at all**. Three readings, and this
investigation picks none:

1. **`BY` is right and the gap is unnamed.** *"the Delivery Date"* is a defined **date**, not an
   event trigger, so §8.9 (which is about triggers) does not govern, and what blocks the item is
   an unnamed `_BY_RE` preposition gap — a sibling of `within_preposition`.
2. **§8.9 governs on its literal terms**, gold is non-conforming, and the item owes
   `relative_trigger_preposition`. That tag is `REACHABILITY`, i.e. **excluding**, so the item
   would leave §9.1's denominator: **`6/17 = 35.3%`**, measured, not projected.
3. **Neither, and gold is unfaithful in a third way.** `BY` means *no later than*; the contract
   says *on*. Recording an on-the-date duty as a by-the-date duty **widens** the permitted window,
   which is §9.1 ground 2's shape.

**This is a CONFORMANCE question about an existing tag, not a request to mint a new one**, so it
is compatible with the 2026-10-10 ruling that no tag is minted. Filed as §10.1 **F41**.

## 5. A measured NEGATIVE, recorded because it keeps an existing entry honest

`C04-087` is the segment CLAUDE.md's agentive-`by` entry names as *"one narrowing away"* from the
latent `_BY_RE` defect, on the grounds that `by Bellicum` and `by delivery …` are the only
classifying substrings in its span and the repair loop was asked about it three times.

**It was asked — `repair_calls=[1]` on all three runs — and it did NOT latch onto either.** All
three runs returned no progress with the `on the Delivery Date` phrase intact. So that entry's
**"LATENT, NOT OBSERVED"** status is now backed by evidence on the one segment most exposed to it,
rather than by assumption. One segment at three runs is not a bound on the defect; it is a
negative result on the case that entry itself singles out.

## 6. What this does and does not change

**Nothing is ruled, no tag is minted, no item is restamped, no cassette is staled, and no
published figure moves** — in-force criterion 2 stays `6/18 = 33.3%`, all-items `9/33 = 27.3%`.

It does bear on two already-ruled rows, by supplying mechanism rather than by reopening them:
F25's narrow ruling is reinforced (the two defined-term items fail for a reason that is *not*
F25's event-bounded mechanism, and narrowing is proven not to be a path), and **F34's
pre-registered probe now has its exact target string in hand** — `During the Term of this
Agreement` and `During the applicable Term of any Service` are the phrases whose disappearance
under `v4` would convert a quarantine into a `null == null` clause-6 pass.
