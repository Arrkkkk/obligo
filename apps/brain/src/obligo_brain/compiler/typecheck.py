"""The Obligation IR typechecker (blueprint SS6.2's six type rules;
packages/ir-spec/SPEC.md sections 4 and 8).

Entry point: typecheck(obligation: ast.Obligation) -> ast.Obligation. Takes
an already-parsed AST (parser.py's job, not this module's) and returns a
new Obligation with every resolvable PartyRef/DateRef/TriggerRef upgraded
to its RESOLVED state, and `underspecified`/`missing_fields` populated --
the parser always leaves those False/() by construction (ast.py's own
comment), so this is the first and only place that ever sets them.

Nothing this function returns needs a separate result wrapper: SS4's own
convention is that "any field the typechecker is responsible for
resolving" already carries a two-state (UNRESOLVED/RESOLVED) shape in the
AST itself, and `underspecified`/`missing_fields` are already fields on
Obligation. A caller that wants to know "is this obligor unresolved"
inspects `isinstance(result.obligor, ast.UnresolvedParty)` -- that *is*
the UNRESOLVED_PARTY signal (SS6.2 rule 3); there is no separate sentinel
to invent. The routing decision this implies ("unresolved party -> review
queue", blueprint SS6.3 stage 4) belongs to whatever owns the obligations
table and its review-queue UI (Phase 5's domain model), not to this
function -- this function's job stops at producing a correctly-annotated
IR, per packages/ir-spec/SPEC.md section 11's own scope boundary.

Tenant isolation: typecheck() takes no `org_id` parameter. It relies on
the caller having already called TenantContext.set(org_id) -- the same
ambient-context convention every other apps/brain DB access uses
(platform/tenancy/db.py, api/v1/sources.py, tasks/segmentation.py) -- and
opens its own tenant_scope() internally for the party-resolution query.
This is a deliberate consistency choice over an explicit org_id parameter:
threading org_id through typecheck()'s signature would be more overtly
"pure" and arguably easier to unit-test, but it would introduce a second,
different tenant-passing convention alongside the ambient one used
everywhere else in this codebase. Callers (including tests) that need to
typecheck something set TenantContext.set(...) first, same as any other
apps/brain component that touches tenant-scoped data.

Rule-by-rule disposition:

1. `WITHIN` requires an explicit unit -> already enforced by the grammar
   itself (grammar/obligation.lark: `duration: NUMBER UNIT`, UNIT
   mandatory) -- a WITHIN without a unit simply fails to parse and never
   reaches this function. Nothing to check here.
2. `BY` (and, by the same DateRef shape, DURING's start/end) requires a
   resolvable date -> delegates to symbols.resolve_date(), which always
   returns None in this checkpoint (see symbols.py's docstring for why:
   no `sources.effective_date` exists to fold against). An UnresolvedDate
   that fails to resolve marks `underspecified` and records its path in
   `missing_fields`.
3. Every party must resolve in the org symbol table -> symbols.
   resolve_party() against the real `parties` table (V16), via
   tenant_scope(). This is the one rule with real data behind it in this
   checkpoint.
4. `trigger` must be a declared event type or defined term -> delegates
   to symbols.resolve_trigger(), which always returns None in this
   checkpoint for the same reason as resolve_date() (no defined-terms/
   event-type registry exists; building one is extraction-pipeline scope).
5. `ACTION` must be in the closed taxonomy -> already enforced by the
   grammar (the ACTION terminal's own alternation, ast.ACTIONS) at parse
   time. Nothing to check here either.
6. Business-day durations require a jurisdiction -> `sources.jurisdiction`
   doesn't exist and no calendar model exists, so a `bd`-unit Duration is
   *always* flagged underspecified in v1, unconditionally. This is a
   direct presence check on `Duration.unit`, not a resolution attempt.

One case this function deliberately does NOT flag: `temporal is None`
entirely (packages/ir-spec/examples/underspecified-missing-unit.json's
"notify Customer promptly" case). That example's own note says the
mechanism for recognizing a vague temporal phrase as an underspecified
*candidate* -- as opposed to an obligation that simply has no temporal
element at all -- is "a grammar/typechecker design question for the next
checkpoint," i.e. this one. Having read the AST this function receives:
by the time "promptly" has been through candidate extraction and DSL
generation, the word itself is gone -- `temporal: None` is genuinely
indistinguishable from "this obligation has no temporal element and that
is correct" using only the parsed AST. Recovering that distinction needs
the source text or the extraction candidate, neither of which this
function has access to. So: deferred to the extraction/critic stage
(blueprint SS6.3 stage 6, out of this checkpoint's explicit scope), not
guessed at here. Same "documented deferral, not silent skip" discipline
as test_properties.py's property-test table.
"""

from __future__ import annotations

import dataclasses

from sqlalchemy.engine import Connection

from obligo_brain.compiler import ast, symbols
from obligo_brain.platform.tenancy.db import tenant_scope


def typecheck(obligation: ast.Obligation) -> ast.Obligation:
    missing_fields: list[str] = []

    with tenant_scope() as conn:
        obligor = _resolve_party(obligation.obligor, "obligor", conn, missing_fields)
        obligee = _resolve_party(obligation.obligee, "obligee", conn, missing_fields)

    temporal = _typecheck_temporal(obligation.temporal, missing_fields)

    return dataclasses.replace(
        obligation,
        obligor=obligor,
        obligee=obligee,
        temporal=temporal,
        underspecified=bool(missing_fields),
        missing_fields=tuple(missing_fields),
    )


def _resolve_party(
    party: ast.PartyRef, path: str, conn: Connection, missing_fields: list[str]
) -> ast.PartyRef:
    if isinstance(party, ast.ResolvedParty):
        return party
    resolved = symbols.resolve_party(party.alias, conn)
    if resolved is not None:
        return resolved
    missing_fields.append(path)  # UNRESOLVED_PARTY, rule 3
    return party


def _resolve_date(date_ref: ast.DateRef, path: str, missing_fields: list[str]) -> ast.DateRef:
    if isinstance(date_ref, ast.ResolvedDate):
        return date_ref
    resolved = symbols.resolve_date(date_ref)
    if resolved is not None:
        return resolved
    missing_fields.append(path)  # rule 2
    return date_ref


def _resolve_trigger(
    trigger_ref: ast.TriggerRef, path: str, missing_fields: list[str]
) -> ast.TriggerRef:
    if isinstance(trigger_ref, ast.ResolvedTrigger):
        return trigger_ref
    resolved = symbols.resolve_trigger(trigger_ref)
    if resolved is not None:
        return resolved
    missing_fields.append(path)  # UNDEFINED_TRIGGER, rule 4
    return trigger_ref


def _check_business_day_jurisdiction(
    duration: ast.Duration, path: str, missing_fields: list[str]
) -> None:
    if duration.unit == "bd":
        missing_fields.append(path)  # rule 6, always fires in v1 -- see module docstring


def _typecheck_temporal(
    temporal: ast.Temporal | None, missing_fields: list[str]
) -> ast.Temporal | None:
    if temporal is None:
        return None  # deliberately not flagged -- see module docstring

    if isinstance(temporal, ast.ByTemporal):
        datetime_ref = _resolve_date(temporal.datetime, "temporal.datetime", missing_fields)
        return dataclasses.replace(temporal, datetime=datetime_ref)

    if isinstance(temporal, ast.WithinTemporal):
        _check_business_day_jurisdiction(
            temporal.duration, "temporal.duration.jurisdiction", missing_fields
        )
        trigger_ref = _resolve_trigger(temporal.of, "temporal.of", missing_fields)
        return dataclasses.replace(temporal, of=trigger_ref)

    if isinstance(temporal, ast.EveryTemporal):
        _check_business_day_jurisdiction(
            temporal.duration, "temporal.duration.jurisdiction", missing_fields
        )
        return temporal

    if isinstance(temporal, ast.DuringTemporal):
        start = _resolve_date(temporal.start, "temporal.interval.start", missing_fields)
        end = _resolve_date(temporal.end, "temporal.interval.end", missing_fields)
        return dataclasses.replace(temporal, start=start, end=end)

    if isinstance(temporal, ast.RelativeToTriggerTemporal):
        trigger_ref = _resolve_trigger(temporal.trigger, "temporal.trigger", missing_fields)
        return dataclasses.replace(temporal, trigger=trigger_ref)

    raise TypeError(f"unhandled Temporal variant: {temporal!r}")
