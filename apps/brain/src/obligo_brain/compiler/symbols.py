"""Symbol resolution for the Obligation IR typechecker (blueprint SS6.2 type
rules 3, 4; packages/ir-spec/SPEC.md section 4).

Split from typecheck.py the same way parser.py is split from ast.py: this
module owns *how* a reference resolves (the SQL/matching mechanism);
typecheck.py owns *which* type rules fire and how to annotate the AST when
resolution fails.

Party resolution (rule 3) is real: it queries the `parties` table
(apps/core migration V16__create_parties.sql, added alongside this
checkpoint -- SS8.2 named the table but it had never been migrated) via a
connection the caller obtained from tenant_scope(). This module issues no
org_id filter of its own -- RLS (parties_tenant_isolation, V16) is what
actually scopes the query to whichever org TenantContext.set() established
for the caller's transaction, same division of responsibility as every
other tenant-scoped query in this codebase (platform/tenancy/db.py,
api/v1/sources.py).

Date and trigger resolution (rules 2 and 4) are NOT implemented against
real data in this checkpoint, and this is a deliberate, load-bearing
finding, not an oversight:

- Rule 2 (`BY` -> resolvable absolute date "after constant folding against
  effective_date") has no `effective_date` to fold against. Blueprint
  SS8.2's own table inventory names `sources.effective_date` as an existing
  column, and packages/ir-spec/SPEC.md section 7 says the EVERY+DURING
  outer bound is "already tracked on sources" -- but neither
  `effective_date` nor `jurisdiction` was ever actually migrated (checked
  V10__create_sources.sql directly). Adding an unused column with no
  constant-folding logic behind it yet would be dead schema, so it isn't
  added here; resolve_date() always returns None (UNRESOLVED stays
  UNRESOLVED) until that column and a real folding rule exist.
- Rule 4 (`trigger` must be "a declared event type or a defined term in
  the document") has no declared-event-type registry and no defined-terms
  extraction anywhere in the repo. Building either is extraction-pipeline
  work (the LangGraph graph's job), explicitly out of this checkpoint's
  scope. resolve_trigger() always returns None for the same reason.
- Rule 6 (business-day durations require a jurisdiction to resolve a
  calendar) has the identical gap -- no `sources.jurisdiction`, no
  calendar model -- but it isn't a *resolution* function like the two
  above (there's no "resolved duration" shape to produce); it's a
  presence check typecheck.py makes directly against `Duration.unit`,
  so it has no corresponding function here.

Both resolve_date() and resolve_trigger() are still real, callable
functions (not silently omitted) so typecheck.py has one consistent shape
to call for all PartyRef/DateRef/TriggerRef resolutions, and so the day
either data source exists, only this module changes -- typecheck.py's
rule-orchestration doesn't.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection

from obligo_brain.compiler import ast


def resolve_party(alias: str, conn: Connection) -> ast.ResolvedParty | None:
    """Match `alias` against the tenant-scoped `parties` table: exact
    case-insensitive `canonical_name` match, or membership in the
    `aliases` array. Returns None (stays UNRESOLVED) on no match or on an
    ambiguous multi-row match -- an ambiguous match is a different failure
    the review queue should still see as UNRESOLVED, not a guess between
    candidates.
    """
    rows = conn.execute(
        text(
            "SELECT id, canonical_name FROM parties "
            "WHERE lower(canonical_name) = lower(:alias) OR :alias = ANY(aliases)"
        ),
        {"alias": alias},
    ).all()

    if len(rows) != 1:
        return None

    party_id, canonical_name = rows[0]
    return ast.ResolvedParty(party_id=str(party_id), canonical_name=canonical_name)


def resolve_date(date_ref: ast.UnresolvedDate) -> ast.ResolvedDate | None:
    """Always returns None in this checkpoint -- see module docstring.
    Kept as a real function (not inlined into typecheck.py) so this is the
    one place that changes once sources.effective_date and a real
    constant-folding rule exist.
    """
    return None


def resolve_trigger(trigger_ref: ast.UnresolvedTrigger) -> ast.ResolvedTrigger | None:
    """Always returns None in this checkpoint -- see module docstring."""
    return None
