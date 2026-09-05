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
