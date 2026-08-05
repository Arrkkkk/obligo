"""Proves tenant isolation at the database layer from the Python side
(blueprint §10.9), mirroring apps/core's TenantIsolationTest: TenantContext
is set directly, standing in for whatever will eventually derive org_id for
a Python-side request/task (auth-context propagation into apps/brain is not
built yet).

Runs against the real Neon branch in DATABASE_URL/BRAIN_DB_PASSWORD -- no
mocks, per CLAUDE.md. Skipped (not failed) when those aren't set, mirroring
Java's @EnabledIfEnvironmentVariable. Also skipped (not failed) if V11/V12
haven't been applied to that branch yet (obligo_brain role or segments
table missing) -- apps/brain owns no migrations itself (schema ownership is
apps/core's, per the blueprint), so this test's prerequisite is "someone
ran apps/core's Flyway against this branch at least once," not something
this test can create for itself.

Fixture data (organizations/users/sources) is seeded and torn down through
a separate connection using the Neon *owner* role from DATABASE_URL, which
has rolbypassrls=true (see apps/core's V2 migration comment) -- the same
reason apps/core's own Flyway runs as owner but the application never does.
obligo_brain deliberately has no grants on those tables (V12's comment), so
it *can't* seed them itself; only the actual segments reads/writes below go
through the tenant-scoped, obligo_brain-authenticated path under test.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.platform.tenancy.context import TenantContext
from obligo_brain.platform.tenancy.db import tenant_scope

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


@dataclass
class TwoOrgFixture:
    org_a_id: uuid.UUID
    org_b_id: uuid.UUID
    source_a_id: uuid.UUID
    source_b_id: uuid.UUID
    segment_a_id: uuid.UUID
    segment_b_id: uuid.UUID


@pytest.fixture
def two_orgs_with_one_segment_each() -> Iterator[TwoOrgFixture]:
    owner_engine = create_engine(_owner_url())

    org_a_id, org_b_id = uuid.uuid4(), uuid.uuid4()
    user_id = uuid.uuid4()
    source_a_id, source_b_id = uuid.uuid4(), uuid.uuid4()
    segment_a_id, segment_b_id = uuid.uuid4(), uuid.uuid4()

    try:
        with owner_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO organizations (id, name) VALUES (:id, 'Org A'), (:id2, 'Org B')"),
                {"id": org_a_id, "id2": org_b_id},
            )
            conn.execute(
                text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
                {"id": user_id, "sub": f"tenant-isolation-test-{user_id}", "email": f"{user_id}@example.test"},
            )
            for source_id, org_id, digit in ((source_a_id, org_a_id, "0"), (source_b_id, org_b_id, "1")):
                conn.execute(
                    text(
                        "INSERT INTO sources "
                        "(id, org_id, uploaded_by, filename, byte_size, sha256, storage_key, status) "
                        "VALUES (:id, :org_id, :uploaded_by, 'fixture.pdf', 1, :sha, :key, 'UPLOADED')"
                    ),
                    {
                        "id": source_id,
                        "org_id": org_id,
                        "uploaded_by": user_id,
                        "sha": digit * 64,
                        "key": f"{org_id}/{source_id}/v1/fixture.pdf",
                    },
                )
            for segment_id, org_id, source_id, label in (
                (segment_a_id, org_a_id, source_a_id, "seed segment a"),
                (segment_b_id, org_b_id, source_b_id, "seed segment b"),
            ):
                conn.execute(
                    text(
                        "INSERT INTO segments (id, org_id, source_id, text, char_start, char_end) "
                        "VALUES (:id, :org_id, :source_id, :text, 0, :end)"
                    ),
                    {
                        "id": segment_id,
                        "org_id": org_id,
                        "source_id": source_id,
                        "text": label,
                        "end": len(label),
                    },
                )
    except DBAPIError as exc:
        owner_engine.dispose()
        pytest.skip(f"segments table or obligo_brain role not provisioned on this branch yet: {exc}")

    try:
        yield TwoOrgFixture(org_a_id, org_b_id, source_a_id, source_b_id, segment_a_id, segment_b_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(
                text("DELETE FROM segments WHERE id IN (:a, :b)"), {"a": segment_a_id, "b": segment_b_id}
            )
            conn.execute(text("DELETE FROM sources WHERE id IN (:a, :b)"), {"a": source_a_id, "b": source_b_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(
                text("DELETE FROM organizations WHERE id IN (:a, :b)"), {"a": org_a_id, "b": org_b_id}
            )
        owner_engine.dispose()


def test_org_cannot_see_the_other_orgs_segment_even_over_the_same_physical_connection(
    two_orgs_with_one_segment_each: TwoOrgFixture,
) -> None:
    fixture = two_orgs_with_one_segment_each

    TenantContext.set(fixture.org_a_id)
    try:
        with tenant_scope() as conn:
            backend_pid_a = conn.execute(text("SELECT pg_backend_pid()")).scalar_one()
            visible_to_a = conn.execute(text("SELECT id FROM segments")).scalars().all()
    finally:
        TenantContext.clear()

    TenantContext.set(fixture.org_b_id)
    try:
        with tenant_scope() as conn:
            backend_pid_b = conn.execute(text("SELECT pg_backend_pid()")).scalar_one()
            visible_to_b = conn.execute(text("SELECT id FROM segments")).scalars().all()
    finally:
        TenantContext.clear()

    # pytest runs the whole session with DATABASE_MAX_POOL_SIZE=1
    # (conftest.py, mirroring build.gradle.kts's test-JVM pin), and
    # get_engine()'s pool_size + max_overflow=0 makes that a hard cap, so
    # both requests above are guaranteed -- not just likely -- to have been
    # served by the same physical Postgres backend.
    print(
        f"POOLING_TRAP_PROOF: org A request used pg_backend_pid={backend_pid_a}, "
        f"org B request used pg_backend_pid={backend_pid_b} "
        "(same physical connection, different tenant contexts, zero cross-tenant leakage)"
    )
    assert backend_pid_b == backend_pid_a

    assert visible_to_a == [fixture.segment_a_id]
    assert visible_to_b == [fixture.segment_b_id]


def test_request_with_no_tenant_context_sees_no_rows(
    two_orgs_with_one_segment_each: TwoOrgFixture,
) -> None:
    # Fail-closed check, mirrors Java's requestWithNoTenantContextSeesNoRows:
    # with no tenant context, app.org_id is never set for this transaction,
    # NULLIF(current_setting(...), '') is NULL, and org_id = NULL is never
    # true -- an unscoped request sees nothing, not everything, even though
    # two real segment rows exist right now (seeded by the fixture above).
    with tenant_scope() as conn:
        visible = conn.execute(text("SELECT id FROM segments")).scalars().all()

    assert visible == []


def test_org_can_insert_its_own_segment_but_rls_rejects_writing_another_orgs_org_id(
    two_orgs_with_one_segment_each: TwoOrgFixture,
) -> None:
    fixture = two_orgs_with_one_segment_each
    own_segment_id = uuid.uuid4()

    TenantContext.set(fixture.org_a_id)
    try:
        # Positive path: obligo_brain's own INSERT grant, org_id matching
        # the active tenant context, satisfies both USING and WITH CHECK.
        with tenant_scope() as conn:
            conn.execute(
                text(
                    "INSERT INTO segments (id, org_id, source_id, text, char_start, char_end) "
                    "VALUES (:id, :org_id, :source_id, 'org a writing its own segment', 0, 29)"
                ),
                {"id": own_segment_id, "org_id": fixture.org_a_id, "source_id": fixture.source_a_id},
            )

        # Negative path: same tenant context (org A), but the row claims to
        # belong to org B. USING lets the connection through (it's still
        # org A's session), but WITH CHECK evaluates against the row being
        # written, not the session, and rejects it -- an org can't launder
        # a write into another org's data by mismatching org_id from the
        # payload rather than the session, which is exactly the shape of
        # bug FORCE ROW LEVEL SECURITY + WITH CHECK exists to catch.
        with pytest.raises(DBAPIError, match="row-level security"):
            with tenant_scope() as conn:
                conn.execute(
                    text(
                        "INSERT INTO segments (id, org_id, source_id, text, char_start, char_end) "
                        "VALUES (:id, :org_id, :source_id, 'impersonation attempt', 0, 21)"
                    ),
                    {"id": uuid.uuid4(), "org_id": fixture.org_b_id, "source_id": fixture.source_b_id},
                )
    finally:
        TenantContext.clear()

    # Cleanup for the row this test itself inserted -- the fixture's own
    # teardown only knows about its seed rows. obligo_brain deliberately
    # has no DELETE grant on segments (V12's comment), so this goes through
    # the owner role, same as the fixture's teardown does.
    owner_engine = create_engine(_owner_url())
    with owner_engine.begin() as conn:
        conn.execute(text("DELETE FROM segments WHERE id = :id"), {"id": own_segment_id})
    owner_engine.dispose()
