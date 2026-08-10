"""Proves typecheck.py's six-type-rule orchestration against the real
`parties` table (V16), same real-Neon standard as
tests/platform/tenancy/test_tenant_isolation.py and this checkpoint's own
test_symbols.py -- typecheck() unconditionally opens tenant_scope() for
party resolution, so every case here needs a real database and a real
tenant context, even the cases that are only really exercising temporal
rules.

Obligations are built via parser.parse() on real DSL strings (not
constructed as ast.Obligation(...) directly) so these tests exercise the
same parser -> typecheck() path the real pipeline will use.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.compiler import ast
from obligo_brain.compiler.parser import parse
from obligo_brain.compiler.typecheck import typecheck
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)

_SOURCE_TAIL = "00000000-0000-0000-0000-000000000001 0 10 0.9"


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


@dataclass
class OrgWithPartyFixture:
    org_id: uuid.UUID
    vendor_id: uuid.UUID
    customer_id: uuid.UUID


@pytest.fixture
def org_with_party() -> Iterator[OrgWithPartyFixture]:
    owner_engine = create_engine(_owner_url())
    org_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    customer_id = uuid.uuid4()

    try:
        with owner_engine.begin() as conn:
            conn.execute(text("INSERT INTO organizations (id, name) VALUES (:id, 'Org')"), {"id": org_id})
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'Vendor Inc', ARRAY['Vendor'])"
                ),
                {"id": vendor_id, "org_id": org_id},
            )
            # Registered so obligee resolution never contaminates tests
            # that aren't about rule 3 -- e.g. the "temporal is None isn't
            # flagged" test below needs a fully-resolvable obligation
            # otherwise, not an accidental UNRESOLVED_PARTY on obligee.
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'Customer Ltd', ARRAY['Customer'])"
                ),
                {"id": customer_id, "org_id": org_id},
            )
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"parties table or obligo_brain role not provisioned on this branch yet: {exc}")

    try:
        yield OrgWithPartyFixture(org_id, vendor_id, customer_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(text("DELETE FROM parties WHERE org_id = :id"), {"id": org_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def _typecheck_in_org(dsl: str, org_id: uuid.UUID) -> ast.Obligation:
    obligation = parse(dsl)
    TenantContext.set(org_id)
    try:
        return typecheck(obligation)
    finally:
        TenantContext.clear()


# -- rule 3: party-alias resolution -----------------------------------------


def test_resolved_party_replaces_matching_obligor_alias(org_with_party: OrgWithPartyFixture) -> None:
    dsl = f'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert result.obligor == ast.ResolvedParty(
        party_id=str(org_with_party.vendor_id), canonical_name="Vendor Inc"
    )
    assert "obligor" not in result.missing_fields


def test_unresolvable_obligee_alias_stays_unresolved_and_flags_underspecified(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = f'MUST "Vendor" DELIVER "Nobody Corp" deliverables "the Deliverables" {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert result.obligee == ast.UnresolvedParty(alias="Nobody Corp")
    assert result.underspecified is True
    assert "obligee" in result.missing_fields


def test_party_from_another_org_is_not_visible(org_with_party: OrgWithPartyFixture) -> None:
    # "Vendor" is only registered in org_with_party.org_id -- typechecking
    # under a fresh, unrelated org must not resolve it, proving this rule
    # actually goes through RLS rather than some unscoped lookup.
    other_org_id = uuid.uuid4()
    dsl = f'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, other_org_id)

    assert result.obligor == ast.UnresolvedParty(alias="Vendor")
    assert "obligor" in result.missing_fields


# -- rule 2 / DateRef resolution (always unresolved in v1) -------------------


def test_by_with_literal_date_is_already_resolved_and_not_flagged(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = f'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" BY 2027-03-01 {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert result.temporal == ast.ByTemporal(datetime=ast.ResolvedDate(date="2027-03-01"))
    assert "temporal.datetime" not in result.missing_fields


def test_by_with_undefined_term_stays_unresolved_and_flags_underspecified(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = (
        f'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        f'BY "the Delivery Date" {_SOURCE_TAIL}'
    )
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert result.temporal == ast.ByTemporal(datetime=ast.UnresolvedDate(raw="the Delivery Date"))
    assert result.underspecified is True
    assert "temporal.datetime" in result.missing_fields


def test_during_with_undefined_terms_flags_both_interval_endpoints(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = (
        f'MUST "Vendor" MAINTAIN "Customer" confidentiality "the information" '
        f'DURING "the Term" .. "the Expiration Date" {_SOURCE_TAIL}'
    )
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert "temporal.interval.start" in result.missing_fields
    assert "temporal.interval.end" in result.missing_fields


# -- rule 4 / TriggerRef resolution (always unresolved in v1) ----------------


def test_within_trigger_stays_unresolved_and_flags_underspecified(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = (
        f'MUST "Vendor" NOTIFY "Customer" security_incident "any security incident" '
        f'WITHIN 5 d OF "discovering a Security Incident" {_SOURCE_TAIL}'
    )
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert isinstance(result.temporal, ast.WithinTemporal)
    assert result.temporal.of == ast.UnresolvedTrigger(raw="discovering a Security Incident")
    assert "temporal.of" in result.missing_fields


def test_relative_to_trigger_stays_unresolved_and_flags_underspecified(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = (
        f'MUST "Vendor" TERMINATE "Customer" agreement "this Agreement" '
        f'BEFORE "terminating this Agreement" {_SOURCE_TAIL}'
    )
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert "temporal.trigger" in result.missing_fields


# -- rule 6 / business-day jurisdiction (always underspecified in v1) --------


def test_within_business_day_duration_always_flags_jurisdiction(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = (
        f'MUST "Vendor" NOTIFY "Customer" security_incident "any security incident" '
        f'WITHIN 5 bd OF "discovering a Security Incident" {_SOURCE_TAIL}'
    )
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert "temporal.duration.jurisdiction" in result.missing_fields


def test_every_business_day_duration_always_flags_jurisdiction(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = f'MUST "Vendor" REPORT "Customer" status_report "a status report" EVERY 5 bd {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert "temporal.duration.jurisdiction" in result.missing_fields


def test_every_non_business_day_duration_does_not_flag_jurisdiction(
    org_with_party: OrgWithPartyFixture,
) -> None:
    dsl = f'MUST "Vendor" REPORT "Customer" status_report "a status report" EVERY 30 d {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert "temporal.duration.jurisdiction" not in result.missing_fields


# -- the deliberate non-rule: temporal is None ------------------------------


def test_missing_temporal_entirely_is_not_flagged(org_with_party: OrgWithPartyFixture) -> None:
    # "Vendor should notify Customer promptly" (packages/ir-spec/examples/
    # underspecified-missing-unit.json) has no temporal shape at all by the
    # time it's DSL text -- typecheck.py's own module docstring documents
    # why this is deliberately not decidable here and is deferred to the
    # extraction stage, not silently guessed at.
    dsl = f'SHOULD "Vendor" NOTIFY "Customer" security_incident "any security incident" {_SOURCE_TAIL}'
    result = _typecheck_in_org(dsl, org_with_party.org_id)

    assert result.temporal is None
    assert result.underspecified is False
    assert result.missing_fields == ()
