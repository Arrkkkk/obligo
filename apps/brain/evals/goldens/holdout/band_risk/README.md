# `C14-076` band-risk investigation scripts

Preserved for the same reason `splitting/`'s and `audit/`'s are: every count in
`C14_076_INVESTIGATION.md` comes from one of these three, and a number whose script was
not kept cannot later be corrected.

| file | what it produces | known-answer check |
| :-- | :-- | :-- |
| `cold_dispositions.py` | §1's audit — for every non-`ANNOTATED` §2.7 disposition across all 22 retrofitted segments, whether a **cold-side** disposition exists (`COLD_ITEM` / `COLD_NOTE` / `NONE`) | pins six spans read by hand during the investigation: `C14-076`×2 → `COLD_NOTE`, `C11-094`×2 / `C04-117` / `C17-066` → `COLD_ITEM`. Withholds all totals on failure |
| `responsible_for.py` | §2's `be/remain responsible\|liable for` census — the polarity × complement grid, and the 15-instance `BARE_BURDEN` cell | pins all four established dispositions (`C02-045`, `C14-139`, `C14-028` annotated/counted; `C04-163` excluded) plus `C14-076` itself. **Its first draft FAILED this check, and that failure is what produced the investigation's answer** — see the module docstring |
| `partyless.py` | §3's fully-partyless modal-sentence census, broad and narrowed to agentless performance passives | pins candidate 2 as flagged in **both** the broad and narrowed passes, and pins the two locked §3.5.3 items that *do* name a party (`C04-087`, `C14-044`) as **not** flagged — a detector that flags those is measuring the wrong thing |

**Two detector faults were corrected mid-investigation and both corrections live in the
files, not only in the output** — Standing Principle 7 applied to this investigation's own
totals.

1. **`responsible_for.py`** classified `C04-163`'s complement as a *thing* because its ACT
   vocabulary held `payment` and the text says `payments`. Reading the flagged case showed
   the complement **is** an act nominalisation and that `C04-163` was excluded on
   **polarity**, not on complement type — falsifying the complement-type-alone hypothesis
   the script had been written to confirm. The grid is a 2×2 because of that failure.
2. **`cold_dispositions.py`** classified the six-character connective `", and "` as
   `COLD_ITEM` because it sits 100% inside cold's long §8.3.1 span. Containment now
   requires a span of ≥40 characters; bare IoU is unaffected.

A third, milder fault is left **visible rather than suppressed**: `partyless.py`'s narrowed
pass admits a few non-performance participles (`non-binding`, `shall be in addition`). The
class is established by reading the printed list, which is why every member is printed.

Run from anywhere; paths resolve relative to the file. All three import `evals.corpus` and
need the repo venv:

```
/Users/rajitagrawal/obligo/.venv/bin/python holdout/band_risk/cold_dispositions.py
```

---

## Second tranche (2026-09-05) — the §5/§5.1 both-`ABSENT` scoring question

Added when `C14_076_INVESTIGATION.md` §8 answered the question §3.2 raised. Same rule as the
three above: every count in §8 comes from one of these four, and a number whose script was not
kept cannot later be corrected.

| file | what it produces | known-answer check |
| :-- | :-- | :-- |
| `alias_census.py` | §8.2's empty-alias emission census over all 81 candidates in the 35 cassettes — the one-sided `obligee` 40/81 vs `obligor` 0/81 split, with a Wilson₉₅ upper bound on the zero | pins `C02-021` run 1 against the four-candidate list read **by hand** during the investigation, aliases and order included. Withholds all totals on failure |
| `party_alias_check.py` | §8.1's clause-3 / clause-4 pass rates split by whether gold says `ABSENT`. Uses the harness's **own** `align()`/`iou()`, so §4.1's threshold and §4.2's tie-break cannot drift from the scorer's | pins `C04-03` on all three runs: clause 3 **fails** predicting `Miltenyi` (§3.5.3's forbidden possessive-on-a-location) and clause 4 **passes** predicting `Bellicum`. A run that does not reproduce all three is measuring something else |
| `both_absent_exec.py` | §8.2's structural proof — a both-`ABSENT` candidate driven through the **real** `ground_candidates()`, `_build_dsl()` and `parser.parse()` | pins both slots parsing to `UnresolvedParty(alias='')`. Executed rather than read **because every prior instance of this question in this repo was settled wrongly by reading** — the `UNLESS` carve-out, the `AndPredicate`/`OrPredicate` gap, the trailing-period bug |
| `clause8_vacuous.py` | §8.4's clause-8 proof against the real registries, plus the set-wide resolvability check behind §10.1 F15 and §8.5's absence-matched-slot table | pins `C04-03`'s span as naming `Bellicum` **and** `Miltenyi` — without it a detector that only ever answers "no party here" would "prove" the claim for every span |

**A third detector fault was corrected mid-investigation and, like the two above, lives in the
file rather than only in the output.** `clause8_vacuous.py`'s first draft tested
`ABSENT`-ness where the code keys on **resolvability**, and reported 4 spurious mismatches
(`C14-01`, `C14-02`, `C02-04`, `C06-01`). Reading them showed every one is a *named but
unresolvable* party — a collective, distributive or relational reference, all of which §3.9
trigger 1 covers explicitly. The looser predicate was the defect, not the data; the corrected
run is **0 of 24**, and the 8 registry-less items are **skipped rather than counted as
non-resolving**, the same scope restriction `partyless.py` applies.

`both_absent_exec.py` needs `src/` on the path and the repo venv; the other three need only the
venv. All four resolve paths relative to the file and run from anywhere:

```
/Users/rajitagrawal/obligo/.venv/bin/python holdout/band_risk/party_alias_check.py
```
