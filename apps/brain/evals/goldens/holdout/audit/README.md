# Pairing-ambiguity audit scripts

Preserved deliberately. §0's correction to `OBJECT_CLASS_INVESTIGATION.md` was possible only
because the *numbers* were re-derivable; `RESULTS.md`'s own Finding 2 counts are **not**
reproducible because its script was never kept. These are kept so §10's verdict can be
re-checked rather than trusted.

| file | what it does |
| :-- | :-- |
| `ambig.py` | the four detectors of §10.1 — duplicate spans within gold, within cold, per-item IoU ties, and non-unique max-total-IoU assignment |
| `margin.py` | §10.2's top-1 vs top-2 IoU margin table for all 32 items |
| `inject.py` | §10.3's planted-instance falsification control — proves the detector fires on a known-answer case before its "no other instances" verdict is used |

Run from anywhere; paths are absolute to `apps/brain/evals/goldens`.

**These do not implement §4.2's content tie-break** — they exist to *find* the cases where it is
needed, not to resolve them. The resolution for the one case found is read out of
`comparison.json` and recorded in §10.4.
