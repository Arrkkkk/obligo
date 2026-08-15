"""Proves ir_hash() hashes a RESOLVED PartyRef by party_id, not by whichever
alias text produced it -- packages/ir-spec/SPEC.md section 10's own stated
requirement -- against a real registered party in the real `parties` table
(apps/core migration V16__create_parties.sql) and a real typecheck() call.
This is the one part of ir_hash's field-by-field rationale that has a real
producer today and so gets proven against real infrastructure rather than by
direct construction; contrast ResolvedDate/ResolvedTrigger, proven in
test_ir_hash.py (ResolvedDate has a real producer too -- the parser itself --
and needs no DB; ResolvedTrigger has no real producer anywhere yet and is
proven by documented direct construction).

Mirrors tests/compiler/test_symbols.py's real-Neon, skip-if-unset,
owner-seeds/obligo_brain-reads pattern exactly, applied to this module
instead.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_hash import ir_hash
from obligo_brain.compiler.parser import parse
from obligo_brain.compiler.typecheck import typecheck
from obligo_brain.platform.tenancy.context import TenantContext

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)

_SEGMENT = "00000000-0000-0000-0000-000000000001"


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


def _dsl(obligor_alias: str) -> str:
    return (
        f"MUST {json.dumps(obligor_alias)} DELIVER \"Customer\" deliverables "
        f'"the Deliverables" {_SEGMENT} 0 10 0.9'
    )


@dataclass
class PartyFixture:
    org_id: uuid.UUID
    acme_id: uuid.UUID


@pytest.fixture
def party_fixture() -> Iterator[PartyFixture]:
    owner_engine = create_engine(_owner_url())
    org_id = uuid.uuid4()
    acme_id = uuid.uuid4()

    try:
        with owner_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO organizations (id, name) VALUES (:id, 'Org IR Hash')"),
                {"id": org_id},
            )
            conn.execute(
                text(
                    "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                    "VALUES (:id, :org_id, 'Acme Corp', ARRAY['Acme', 'Vendor'])"
                ),
                {"id": acme_id, "org_id": org_id},
            )
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"parties table or obligo_brain role not provisioned on this branch yet: {exc}")

    try:
        yield PartyFixture(org_id, acme_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(text("DELETE FROM parties WHERE org_id = :id"), {"id": org_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def test_resolved_party_hashes_by_party_id_not_alias_text(party_fixture: PartyFixture) -> None:
    # Two different real aliases of the same registered party -- canonical
    # name vs. an ARRAY alias -- must resolve to the same party_id and
    # therefore hash identically once typechecked.
    ob_via_canonical_name = parse(_dsl("Acme Corp"))
    ob_via_alias = parse(_dsl("Vendor"))

    TenantContext.set(party_fixture.org_id)
    try:
        typechecked_canonical = typecheck(ob_via_canonical_name)
        typechecked_alias = typecheck(ob_via_alias)
    finally:
        TenantContext.clear()

    assert isinstance(typechecked_canonical.obligor, ast.ResolvedParty)
    assert isinstance(typechecked_alias.obligor, ast.ResolvedParty)
    assert typechecked_canonical.obligor.party_id == typechecked_alias.obligor.party_id
    assert typechecked_canonical.obligor.party_id == str(party_fixture.acme_id)

    assert ir_hash(typechecked_canonical) == ir_hash(typechecked_alias)
    # Sanity: the pre-typecheck (still-alias) obligations really do differ --
    # proving the equal hash above comes from real party resolution
    # collapsing them, not from some other insensitivity.
    assert ir_hash(ob_via_canonical_name) != ir_hash(ob_via_alias)


def test_resolved_party_still_differs_from_a_genuinely_different_party(
    party_fixture: PartyFixture,
) -> None:
    ob_resolved = parse(_dsl("Acme Corp"))
    ob_unresolved = parse(_dsl("Nonexistent Co"))

    TenantContext.set(party_fixture.org_id)
    try:
        typechecked_resolved = typecheck(ob_resolved)
        typechecked_unresolved = typecheck(ob_unresolved)
    finally:
        TenantContext.clear()

    assert isinstance(typechecked_resolved.obligor, ast.ResolvedParty)
    assert isinstance(typechecked_unresolved.obligor, ast.UnresolvedParty)
    assert ir_hash(typechecked_resolved) != ir_hash(typechecked_unresolved)
