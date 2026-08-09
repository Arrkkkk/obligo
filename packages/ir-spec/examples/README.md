# Worked examples

Each file (except `not-supported/`) has the shape `{ source_text, notes, ir }`. Only the `ir` key is validated against `../schema/obligation-ir.schema.json` — the wrapper (`source_text`, `notes`) exists for human/test readability and is not part of the schema.

| File | Demonstrates |
| :--- | :--- |
| `must-by.json` | `MUST` + `BY`, both parties `UNRESOLVED` |
| `must-not-no-temporal.json` | `MUST_NOT`, `temporal: null`, both parties `RESOLVED` |
| `should-within.json` | `SHOULD` + `WITHIN...OF` |
| `may-relative-to-trigger.json` | `MAY` + `RELATIVE_TO_TRIGGER(AFTER)` |
| `must-every.json` | `MUST` + `EVERY` (recurring) |
| `must-during.json` | `MUST` + `DURING`, resolved interval bounds |
| `must-if-condition.json` | A compound (`AND`) predicate inside one `IF` condition |
| `underspecified-missing-unit.json` | `temporal: null` + `underspecified: true` — the blueprint's own "promptly is not a deadline" example |
| `underspecified-missing-anchor.json` | A recognized `BY` shape whose `DateRef` is `UNRESOLVED` — a different underspecification mechanism than the missing-unit case |

Together, these nine cover all four modalities, all five frozen temporal forms, both `PartyRef` states, and both underspecification mechanisms.

## `not-supported/`

A different, deliberately simpler shape: `{ source_text, why_not_representable_in_v1, expected_parser_behavior }`. These are **not** valid against `obligation-ir.schema.json` and are not meant to be — they document real sentences IR v1 cannot represent, and what the next checkpoint's parser must do when it meets one (never silently drop, never silently misrepresent).

| File | Boundary |
| :--- | :--- |
| `exception-unless.json` | Any `UNLESS`/exception clause at all — the basic case |
| `mixed-condition-and-exception.json` | An `IF` and an `UNLESS` on the same obligation — pins down that the rejected "flat exceptions allowed" reading of "conditions only" is in fact rejected |
| `exception-nested-condition.json` | Multi-level nesting (condition containing exception containing exception) — out of scope under either reading |
| `every-during-composition.json` | `EVERY` + `DURING` composed on one obligation — a compositional gap distinct from the conditions/exceptions boundary; each form exists individually but they can't combine |
