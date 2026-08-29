# Cold annotation pass — task packet

You are the **second annotator** for a contract-obligation gold set. You are annotating
**cold**: another annotator has already annotated these same segments, and you must not
see their work. Your annotations will be compared against theirs to measure disagreement.

## Your inputs — these and nothing else

1. `GOLD_SET_GUIDELINE.md` — the annotation guideline. This is authoritative. Follow it.
2. `segments/*.json` — 22 contract segments, each with `segment_id`, `doc_id`, `stratum`
   and `segment_text`.
3. `template.json` — the field schema for one annotated item.

## Hard constraint — do not go looking for the existing annotations

Work **only** inside this directory. Do **not** read, list, search, or `git show` anything
under the `obligo` repository — in particular anything under `evals/goldens/`. Those paths
hold the other annotator's answers; reading them destroys the measurement this pass exists
to produce. If a tool call fails with a permission error on such a path, that is the
safeguard working: do not attempt to work around it, and note it in your report.

At the end, list **every file you read**, by path. This is recorded as your self-report.

## What to produce

For **each** of the 22 segments, decide which obligations in it are annotatable gold items
under the guideline (§2 for eligibility and exclusions, §4.3 / §4.3.1 / §4.3.2 for whether
one sentence yields one item or several), and write one JSON object per item.

**The number of items per segment is deliberately not given to you.** A segment may yield
zero, one, or several. Deciding that is part of the annotation, and it is one of the things
being measured. Do not try to infer it from anything.

If a segment yields **no** annotatable item, still emit a record for it with
`"items": []` and say why in `segment_notes`, citing the § rule that excludes it.

## Output format

Write one file per segment to `out/<rank>_<segment_id>.json`, shaped:

```json
{
  "segment_id": "C22-048",
  "items": [ { ...one object per template.json... } ],
  "segment_notes": "any segment-level reasoning, exclusions and their rules"
}
```

## Field rules that matter most

- `span_text` **must be a verbatim substring** of `segment_text`, and
  `span_char_start`/`span_char_end` must be its real offsets (verify by slicing).
- `modality`, `obligor`, `obligee`, `temporal`, `conditions`, `underspecified` are
  exact-match fields — see §3 and §14.3.
- `action` and `object_class` are accept-set fields. Give your best single value plus any
  further defensible alternates in the `*_accept_set` list.
- `rules_cited` is **mandatory** (§14.5): the § numbers you actually invoked.
- `annotator_confidence` is `CONFIDENT` or `AMBIGUOUS` — never a proxy for
  `underspecified` (§14.2). If you would have escalated to a reviewer under §14.4, mark
  `AMBIGUOUS` and set out both readings in `annotator_notes`. There is no reviewer
  available to you on this pass; record the uncertainty rather than resolving it silently.

Take the guideline's known-gap sections (§8, §15, §16, §17) seriously: annotate what the
document says even where the IR cannot represent it, and tag `known_gaps` accordingly.

Work through the segments in filename order.
