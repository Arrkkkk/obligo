# Extraction model bake-off — criteria fixed BEFORE any call

**Status:** criteria pre-committed 2026-08-23. **No bake-off call has been made.**
**Reason this document exists:** the selection must be decided by evidence agreed in
advance, not by post-hoc rationalisation of whichever model happened to look best.
This file is committed before the first call so the criteria cannot move afterwards —
the same discipline `§3.4`'s accept-sets follow ("authored at annotation time and frozen
with the item... never widened after seeing a prediction").

## Why a bake-off at all

`llama-3.3-70b-versatile` returned HTTP 404 on 2026-08-22 and is absent from the
account's model list (see CLAUDE.md's blocking entry). Every prompt in
`prompts/extraction/` and `prompts/repair/` pins it.

## Candidates

Reviewer-ruled 2026-08-23. Three candidates, all 131,072-token context — context is
not a constraint, since one extraction call needs ~1,564 tokens.

| model | max completion tokens |
| :--- | ---: |
| `openai/gpt-oss-120b` | 65,536 |
| `openai/gpt-oss-20b` | 65,536 |
| `qwen/qwen3.6-27b` | 16,384 |

**`groq/compound` and `groq/compound-mini` are EXCLUDED on agentic-risk grounds**
(reviewer-ruled): they are agentic systems with built-in tool use, and a model that can
invoke external tools mid-extraction is a different risk category from a plain chat
completion. This pipeline's design — deterministic core, probabilistic edge, the
grounding gate as the arbiter of truth — assumes the model's output is self-contained.

The other eight available models are excluded on capability grounds, recorded so the
exclusion is auditable rather than assumed: `whisper-large-v3{,-turbo}` (audio
transcription, 448 ctx), `canopylabs/orpheus-*` (speech), `meta-llama/llama-prompt-guard-2-*`
(injection classifiers whose 512-token context cannot even hold this system prompt,
~1,334 tokens), `openai/gpt-oss-safeguard-20b` (safety classifier variant), `allam-2-7b`
(Arabic-specialised, 4,096 ctx).

## THE TEST SET — and why it deliberately avoids the gold segments

**Six segments, none of them gold.**

- **Four fresh corpus segments**, drawn by seed from the pool, **excluding all 12 gold
  segments and every segment in the exclusion logs**.
- **Two pilot segments** with a fronted subordinate clause (the `leading_temporal_clause`
  and `leading_condition_clauses` cases), for the v2-fix check below.

**Selecting a model by its gold-set score would bias criterion 2 upward on that same
gold set.** It is the model-selection analogue of fitting to the test set, and it is
precisely the failure `§3.4`'s freeze rule and `§11`'s "changing the classifier first
would tune the compiler to the corpus it is about to be graded on" both refuse. The
three mechanical dimensions below are model-CAPABILITY properties, measurable without
any gold answer at all.

**18 calls total** (6 segments x 3 models), plus retries. One run each: this measures
capability, not stability.

## DIMENSION 1 — Schema-valid JSON output (GATING)

Measured by the real `graphs/extraction._parse_response`, not a proxy.

`SCHEMA_INVALID` is emitted when the response is not valid JSON, lacks a top-level
`obligations` array, or a candidate fails `LLMCandidate` validation.

| verdict | criterion |
| :--- | :--- |
| **PASS** | **6/6 segments** parse with zero `SCHEMA_INVALID` |
| **FAIL** | any `SCHEMA_INVALID` |

**Gating, and strict on purpose.** `SCHEMA_INVALID` is a *terminal* rejection — the
§13.8 schema-repair loop is not built, so a malformed response is a silently lost
obligation with no retry. A model that cannot reliably emit the schema is unusable
regardless of how well it reads contracts. A FAIL here eliminates the candidate
outright, whatever its other scores.

## DIMENSION 2 — Verbatim quoting (GATING)

The span-grounding premise: every nested field must be a literal substring of the
segment. Measured by the real `ground_candidates()`.

**The metric is the RATE, not the presence of rejections.** A rejection is the gate
working correctly — hallucinated spans are caught by construction. But a model that
paraphrases constantly collapses recall while the gate stays sound, so the rate is what
distinguishes a usable model from an unusable one.

Per candidate emitted, across all six segments:

| verdict | criterion |
| :--- | :--- |
| **PASS** | **>= 80%** of emitted candidates survive grounding |
| **MARGINAL** | 60-79% |
| **FAIL** | < 60%, or any segment where 0 candidates survive |

Rejections are additionally broken down by reason (`SPAN_NOT_FOUND`, `EMPTY_SPAN`,
`AMBIGUOUS_SPAN`, `NESTED_FIELD_NOT_IN_SPAN`) and reported, because the mix is
diagnostic: `NESTED_FIELD_NOT_IN_SPAN` concentrated on fronted-clause segments is the
v2-fix question below, not a general quoting failure.

## DIMENSION 3 — Grounding-gate survival end to end (GATING)

At least one grounded candidate per obligation-bearing segment. All six test segments
contain at least one obligation.

| verdict | criterion |
| :--- | :--- |
| **PASS** | **>= 5 of 6** segments yield >= 1 grounded candidate |
| **FAIL** | <= 4 of 6 |

Distinct from dimension 2: a model could ground 100% of what it emits while emitting
almost nothing. This catches silence; dimension 2 catches paraphrase.

## DIMENSION 4 — The leading-subordinate-clause fix (DIAGNOSTIC, NOT GATING)

`prompts/extraction/v2.yaml` exists solely to fix one failure — the model excluding a
fronted subordinate clause from `span_text` while quoting its content into
`temporal_raw`/`condition_raws`. That fix was validated by live replay against the
retired model, twice. **It is the one prompt change in this repo whose entire
justification is now unreproducible.**

On the two fronted-clause segments, under v2, record for each candidate:

- does `span_text` include the fronted clause?
- is the candidate rejected `NESTED_FIELD_NOT_IN_SPAN`?

| observation | consequence |
| :--- | :--- |
| clause included, grounds cleanly | v2's wording carries over |
| clause excluded, `NESTED_FIELD_NOT_IN_SPAN` | the bug exists on this model too; v2 does not fix it here |
| clause included but v1 also succeeds | v2 may be unnecessary on this model |

**Deliberately NOT gating.** This informs a prompt decision, not the model choice. A
model could be the best extractor available and still need different prompt wording,
and conflating those two questions would let a prompt artefact veto a model.

## THE DECISION RULE, fixed in advance

1. Any candidate FAILING dimension 1, 2 or 3 is **eliminated**.
2. Among survivors, rank by **dimension 2's grounding-survival rate** — the property the
   pipeline's correctness most directly rests on.
3. **Ties (within 5 percentage points) break toward the SMALLER model**, on cost and
   latency: a 46-call recording run and every future eval run pays this repeatedly.
4. If **all three fail**, no model is selected and the failure is reported. The
   remaining options — a different provider, or the unbuilt model router — are a
   separate decision, not something to be forced by a bad bake-off.
5. If exactly one survives, it is selected **and its weaknesses are recorded**, not
   glossed: a sole survivor is not a strong result.

## What this bake-off does NOT decide

- **Temperature-0 non-determinism** (§6's 3x requirement). Reviewer-approved for
  re-measurement, but it needs repeated runs of the same input and is a separate
  exercise from selection.
- **The `PROVIDE`/`REPORT` action ambiguity** behind §3.4's accept-sets. Same reason.
- **The `condition_raws` prompt-alignment question** (CLAUDE.md debt). Answerable only
  against gold, during the harness's first real run — deliberately not here, to keep
  selection off the gold set.
