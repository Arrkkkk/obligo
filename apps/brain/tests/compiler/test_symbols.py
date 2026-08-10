"""Proves symbols.resolve_party() against the real `parties` table
(apps/core migration V16__create_parties.sql), including tenant isolation
-- mirrors tests/platform/tenancy/test_tenant_isolation.py's real-Neon,
skip-if-unset, owner-seeds/obligo_brain-reads pattern exactly, applied to
this checkpoint's own table instead of segments.

resolve_date()/resolve_trigger() are not tested here: both are
unconditional `return None` in this checkpoint (symbols.py's own
docstring explains why -- no effective_date/defined-terms data source
exists yet), so there is no real behavior to prove against a database.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.compiler import symbols
from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


@dataclass
class PartiesFixture:
    org_a_id: uuid.UUID
    org_b_id: uuid.UUID
    acme_id: uuid.UUID
    ambiguous_party_1_id: uuid.UUID
    ambiguous_party_2_id: uuid.UUID


@pytest.fixture
def parties_fixture() -> Iterator[PartiesFixture]:
    owner_engine = create_engine(_owner_url())

    org_a_id, org_b_id = uuid.uuid4(), uuid.uuid4()
    acme_id = uuid.uuid4()
    ambiguous_party_1_id, ambiguous_party_2_id = uuid.uuid4(), uuid.uuid4()

    try:
        with owner_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO organizations (id, name) VALUES (:a, 'Org A'), (:b, 'Org B')"),
                {"a": org_a_id, "b": org_b_id},
            )
            # Org A: one cleanly-resolvable party, matchable by canonical
            # name (case-insensitive) or by alias.
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'Acme Corp', ARRAY['Acme', 'Vendor'])"
                ),
                {"id": acme_id, "org_id": org_a_id},
            )
            # Org A: two more parties that both list "Ambiguous Co" as an
            # alias -- resolve_party() must treat >1 match as no match,
            # not guess.
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'First Candidate LLC', ARRAY['Ambiguous Co'])"
                ),
                {"id": ambiguous_party_1_id, "org_id": org_a_id},
            )
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'Second Candidate LLC', ARRAY['Ambiguous Co'])"
                ),
                {"id": ambiguous_party_2_id, "org_id": org_a_id},
            )
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"parties table or obligo_brain role not provisioned on this branch yet: {exc}")

    try:
        yield PartiesFixture(org_a_id, org_b_id, acme_id, ambiguous_party_1_id, ambiguous_party_2_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(
                text("DELETE FROM parties WHERE org_id IN (:a, :b)"), {"a": org_a_id, "b": org_b_id}
            )
            conn.execute(text("DELETE FROM organizations WHERE id IN (:a, :b)"), {"a": org_a_id, "b": org_b_id})
        owner_engine.dispose()


def test_resolve_party_matches_canonical_name_case_insensitively(parties_fixture: PartiesFixture) -> None:
    TenantContext.set(parties_fixture.org_a_id)
    try:
        with tenant_scope() as conn:
            resolved = symbols.resolve_party("acme corp", conn)
    finally:
        TenantContext.clear()

    assert resolved is not None
    assert resolved.party_id == str(parties_fixture.acme_id)
    assert resolved.canonical_name == "Acme Corp"


def test_resolve_party_matches_via_alias(parties_fixture: PartiesFixture) -> None:
    TenantContext.set(parties_fixture.org_a_id)
    try:
        with tenant_scope() as conn:
            resolved = symbols.resolve_party("Vendor", conn)
    finally:
        TenantContext.clear()

    assert resolved is not None
    assert resolved.party_id == str(parties_fixture.acme_id)


def test_resolve_party_returns_none_when_no_match(parties_fixture: PartiesFixture) -> None:
    TenantContext.set(parties_fixture.org_a_id)
    try:
        with tenant_scope() as conn:
            resolved = symbols.resolve_party("Nonexistent Co", conn)
    finally:
        TenantContext.clear()

    assert resolved is None


def test_resolve_party_returns_none_on_ambiguous_match(parties_fixture: PartiesFixture) -> None:
    TenantContext.set(parties_fixture.org_a_id)
    try:
        with tenant_scope() as conn:
            resolved = symbols.resolve_party("Ambiguous Co", conn)
    finally:
        TenantContext.clear()

    assert resolved is None


def test_resolve_party_cannot_see_another_orgs_party(parties_fixture: PartiesFixture) -> None:
    # Org B's own tenant context, querying for a party that only exists in
    # Org A -- RLS (parties_tenant_isolation, V16) must return zero rows,
    # not just "the app happened not to ask for it."
    TenantContext.set(parties_fixture.org_b_id)
    try:
        with tenant_scope() as conn:
            resolved = symbols.resolve_party("Acme Corp", conn)
    finally:
        TenantContext.clear()

    assert resolved is None
