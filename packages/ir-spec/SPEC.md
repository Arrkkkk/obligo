# Obligation IR v1 — Specification

This package is the contract between the probabilistic half of Obligo (LLM candidate extraction) and the deterministic half (the typechecker and the Z3 verifier) — blueprint §6.2's own framing for why the IR is versioned as a first-class artifact, not an implementation detail buried in `apps/brain`.

**Status: v1 frozen.** This checkpoint defines the IR's shape only. No parser, no typechecker, no extraction pipeline code exists yet — those are later Phase 4 checkpoints. Nothing in `apps/brain` imports anything in this directory yet.

This directory mirrors `packages/contracts/`'s existing role in this repo (blueprint §22.4): one language-agnostic schema, validated by both runtimes (Java and Python), rather than a Python-only Pydantic model set that Java would have no way to check itself against.

## 1. What's in this directory

| File | Role |
| :--- | :--- |
| `SPEC.md` | This document — the narrative spec and the reasoning behind every scope decision |
| `grammar.lark` | The frozen v1 surface syntax, written in real Lark notation. **Reference only** — not imported by any parser yet |
| `schema/obligation-ir.schema.json` | The canonical, language-agnostic shape both runtimes validate against |
| `examples/*.json` | Worked examples pairing a real sentence with its compiled IR — the shared fixtures both runtimes' test suites will load |
| `examples/not-supported/*.json` | Real sentences IR v1 **cannot** represent, and what a parser must do when it meets one |

## 2. The four modalities

Frozen at exactly these four (blueprint §21's own risk mitigation):

| Modality | Meaning |
| :--- | :--- |
| `MUST` | Mandatory obligation |
| `MUST_NOT` | Mandatory prohibition |
| `SHOULD` | Non-binding expectation — weaker than `MUST`; matters for risk scoring and for what the verifier treats as contradictable |
| `MAY` | A discretionary right or option, not a duty |

## 3. The five temporal forms

Blueprint §6.2's grammar sketch lists **six** temporal alternatives (`BY`, `WITHIN...OF`, `EVERY`, `DURING`, `AFTER`, `BEFORE`), but §21's risk-mitigation text freezes the count at **five**. This is a real discrepancy in the blueprint's own text, confirmed by counting the sketch's alternatives directly, not a phrasing ambiguity to read past. Resolved for v1, deliberately, not by default: **`AFTER` and `BEFORE` are merged into one directional form**, `RELATIVE_TO_TRIGGER(direction, trigger)`. This keeps all six of the sketch's alternatives' expressive power (nothing is dropped) while landing on exactly five named forms, as §21 requires.

| Form | Shape | Example |
| :--- | :--- | :--- |
| `BY` | `{ datetime: DateRef }` | "...by March 1, 2027." |
| `WITHIN` | `{ duration: Duration, of: TriggerRef }` | "...within 5 business days of discovering a Security Incident." |
| `EVERY` | `{ duration: Duration }` | "...every 30 days." |
| `DURING` | `{ interval: { start: DateRef, end: DateRef } }` | "...during the Term." |
| `RELATIVE_TO_TRIGGER` | `{ direction: BEFORE\|AFTER, trigger: TriggerRef }` | "...before terminating this Agreement." / "...after receipt of the returned Product." |

An obligation carries **at most one** temporal node — the grammar's `temporal?` slot is singular, not a list. See section 7 for the real, named consequence of that.

## 4. Party representation

Blueprint §6.2's grammar sketch shows one abstract `party` slot, but §8.2's schema (`obligations.obligor_party_id`, `obligations.obligee_party_id`, a CHECK that they differ) and the verifier's own conflict-candidate-set definition ("at least one party in {obligor, obligee}") are explicit that there are always two distinct roles. The sketch is shorthand for this, not a narrower design — v1's IR has both:

```
PartyRef =
  | { status: UNRESOLVED, alias: string }
  | { status: RESOLVED,   party_id: UUID, canonical_name: string }

Obligation.obligor: PartyRef
Obligation.obligee: PartyRef
```

The parser only ever produces `UNRESOLVED` — the alias exactly as it appeared in text ("Vendor", "the Company", "Acme Corp"). Only the typechecker's symbol-resolution stage (not designed by this checkpoint — that's the next one) ever produces `RESOLVED`, by matching the alias against the org's `parties`/`aliases` table (FR-6), or leaves it `UNRESOLVED` and routes to the review queue (`UNRESOLVED_PARTY`, type rule 3). The IR's shape carries both states from day one so the typechecker has somewhere to write its output without a schema change later.

`DateRef` and `TriggerRef` follow the identical `UNRESOLVED`/`RESOLVED` pattern, for the same reason — see the schema for their exact shapes. This is a deliberate, consistent convention across the whole IR: **any field the typechecker, not the parser, is responsible for resolving gets this same two-state shape.**

## 5. Object representation

```
ObjectRef = { class: string, raw_text: string }
```

`class` is used by the verifier's conflict-candidate-set matching (blueprint §6.7: two obligations are conflict candidates only if they share an object class). It is an **open vocabulary** for v1 — not a closed enum — same tracked-open-item footing as the action taxonomy (section 12). `raw_text` preserves the literal object phrase for traceability even after a class is assigned.

## 6. What "conditions only, no nested exceptions" excludes

Blueprint §21's exact words: "conditions only, no nested exceptions in v1." Two readings were considered:

1. **No `UNLESS`/exception construct exists in v1's grammar at all** — only `IF`/condition.
2. **Both `IF` and `UNLESS` exist as flat, top-level modifiers; only nesting/recursion between them is excluded.**

**Decision: reading 1.** "Conditions only" is read at face value — "only" already does the work of excluding exceptions, and the parenthetical is clarifying that exclusion, not softening it into "flat exceptions are fine." This is the safer reading for a tool whose entire purpose is catching things a human reader would otherwise miss: a system that silently drops or silently mis-files a legal carve-out is worse than one that visibly refuses to compile it. `grammar.lark` has **no exception rule of any kind** — this is not an oversight, it's load-bearing, and it's verified mechanically, not just asserted in prose (see section 9).

Concrete sentences IR v1 cannot represent, with worked fixtures in `examples/not-supported/`:

- **Any `UNLESS` clause at all** (`exception-unless.json`) — "Vendor must deliver the Deliverables within 30 days, unless delayed by a Force Majeure Event." The exception simply has no production to parse into.
- **An `IF` and an `UNLESS` on the same obligation** (`mixed-condition-and-exception.json`) — pins down that reading 2 above is in fact rejected: this is exactly the sentence reading 2 would have let through.
- **Multi-level nesting** (`exception-nested-condition.json`) — a condition containing an exception containing a further exception. Out of scope under *either* reading; nesting by any definition.

**Required parser behavior, stated now so it isn't improvised later:** a real `UNLESS` in source text must cause a loud, routed parse failure — fed back through the repair loop (blueprint §6.3 stage 3, ≤3 retries) and quarantined for human review if unrepairable. It must **never** be silently dropped, and never silently absorbed into `condition` as if it had been an `IF` clause. Silently discarding a legal carve-out is a correctness bug with real stakes for a compliance tool, not a cosmetic parsing gap.

**Not affected by this decision:** the `Predicate` type's own `AND`/`OR`/`NOT` recursion (blueprint's `predicate := <atom> | predicate (AND|OR) predicate | NOT predicate`) is ordinary boolean logic *within* a single `IF` clause, not exception nesting. `examples/must-if-condition.json` demonstrates this: a compound `AND` predicate, zero exceptions involved.

## 7. A real compositional gap: `EVERY` + `DURING`

Section 3 noted an obligation carries one temporal node. A sentence like "Vendor must provide a status report every 30 days during the Term" genuinely wants `EVERY` (the recurrence) *and* `DURING` (the recurrence's outer bound) together — and no single `Temporal` variant can hold both.

**v1's answer:** compile as `EVERY` alone (`examples/must-every.json`). The recurrence's real-world outer bound is left implicit to the *source document's own* `effective_date`/expiration (already tracked on `sources`), not re-encoded per-obligation. This is a deliberate, lossy simplification, worked in full in `examples/not-supported/every-during-composition.json` — including a note on what the next checkpoint's actual grammar should do when it meets a trailing `DURING` phrase it has nowhere to attach (a parser *warning*, most likely — this is not the same failure class as an `UNLESS` clause, since `DURING` is legal grammar, just not composable here).

Real compositional temporal expressions in general are v2 scope, the same footing as nested exceptions: blueprint §21 froze the *count* of temporal forms, not their composability, and treating those as the same freeze would have been a scope decision this checkpoint has no authority to make unilaterally.

## 8. Underspecification

Blueprint §6.2's own design principle: "the checker's failures are product features... this is why underspecified obligations are stored and surfaced rather than discarded." An underspecified obligation is not rejected — it's compiled with `underspecified: true` and a `missing_fields` list, and routed for human attention (exactly blueprint's own "your DPA says you'll notify 'promptly' — that's not a deadline" framing).

Two different underspecification *mechanisms*, both worked as examples since they produce genuinely different IR shapes:

- **No temporal shape recognized at all** (`examples/underspecified-missing-unit.json`) — "notify Customer promptly" has no explicit duration or unit for any of the five forms to hold; `temporal` is `null`, not a malformed `WITHIN` node.
- **A recognized shape with an unresolved sub-reference** (`examples/underspecified-missing-anchor.json`) — "by the Delivery Date" *does* parse as a `BY` shape; it's the `DateRef` inside it that's `UNRESOLVED` because "the Delivery Date" isn't a resolvable defined term.

`missing_fields`' exact path-naming convention (e.g. `"temporal.unit"`) is illustrative in these examples, not frozen by this spec — that's a typechecker-design detail for the next checkpoint.

## 9. Verified, not just asserted

Before this spec was considered done, both machine-checkable artifacts were run for real, not eyeballed:

- `schema/obligation-ir.schema.json` validates as well-formed JSON Schema (2020-12) via `jsonschema.Draft202012Validator.check_schema`.
- `grammar.lark` loads as valid Lark syntax and successfully parses a real sample obligation string (`MUST`, a `BY` temporal, a `source`/`confidence` tail) with no grammar/lexer conflicts.
- **The section 6 design decision was checked mechanically, not just documented:** the same grammar that parses a valid `IF` condition was fed a string containing `UNLESS` and genuinely failed to parse (`UnexpectedCharacters`) — confirming there is no accidental path by which an exception clause could sneak through this grammar's own rules.
- Every example under `examples/*.json` (excluding `not-supported/`) has its `ir` key validated against the schema, and every `alias`/`raw` string referenced anywhere inside it is confirmed to be a literal substring of that example's own `source_text` — the same span-grounding discipline the real pipeline will enforce, applied to these fixtures too, not assumed.

## 10. Versioning

`grammar_version` (semver) is recorded on every compiled obligation. v1 is `1.0.0`. A grammar bump triggers a recompile job over affected obligations (blueprint §6.2) — the IR is never silently reinterpreted under a new grammar version. Adding a temporal form, a modality, or the exception construct this checkpoint deliberately excluded would all be breaking, `2.0.0`-class changes, not patch bumps.

`ir_hash` (the dedupe/idempotency key referenced throughout blueprint §6, e.g. the `obligations(org_id, ir_hash)` unique index and the hash-stability property test) is a **derived** value — a canonicalization-then-hash function over a compiled IR instance — not a field this schema defines directly. One forward-looking note worth recording now rather than rediscovering later: canonicalization must hash the *resolved* form of a `PartyRef` (`party_id`) where one exists, not the raw `alias` — otherwise two obligations that are semantically identical except for which alias of the same party was used in the source text would hash differently, which is exactly the failure the hash-stability property test (§19.3) exists to catch.

## 11. Explicitly out of scope for this spec

`obligation-ir.schema.json` covers the **compiler-produced IR only**: modality, parties, action, object, temporal, conditions, the source citation, confidence, and the typecheck annotations (`underspecified`, `missing_fields`). It deliberately does **not** cover the `obligations` table's lifecycle columns owned by Phase 5's domain model — `status`, `risk_score`, `due_at`, `owner_user_id`, `version`, `deleted_at`, `binding_strength`. Those describe what happens to an obligation *after* it's compiled (its state machine, its risk score, who owns following up on it) — layered on top of a compiled IR, not part of the IR itself. Conflating the two would mean every future obligation-lifecycle change forces a churn through this spec for a concern it was never meant to own.

`prompt_version`/`model_id` (extraction provenance, tracked in `agent_runs` per NFR-10) are similarly out of scope — they describe *how* an IR instance was produced, not *what* it means. `grammar_version` is the one exception: it's kept in-scope because it's the IR's own versioning mechanism, not extraction provenance.

## 12. Open items — tracked, not forgotten

- **The closed action taxonomy (~40 verbs).** Blueprint §6.2 names 10 examples (`NOTIFY`, `DELIVER`, `PAY`, `DELETE`, `RETAIN`, `MAINTAIN`, `INDEMNIFY`, `REPORT`, `PROVIDE`, `CURE`) but never gives the full list. `action` is validated here only for lexical shape (`^[A-Z][A-Z_]*$`), not against a closed enum. **This is a real, deliberate decision to defer, not an oversight** — finalizing the full ~40-verb list belongs to writing `apps/brain/compiler/grammar/obligation.lark` (the next checkpoint), where it can be checked against real extraction candidates rather than invented in the abstract here. Do not silently invent the missing ~30 verbs when that checkpoint starts — decide the list deliberately, the same "tracked, not forgotten" discipline as every debt item in `CLAUDE.md`.
- **The object-class taxonomy**, same shape of open item as the action taxonomy, tied to the same future decision (blueprint §6.7 ties object-class matching to "the action/object taxonomy" as one combined concern).
