"""apps/brain's SQLAlchemy engine and the §10.9 pooling-trap mitigation,
Python side. Mirrors DataSourceConfig + DatabaseConnectionDetails +
TenantConnectionPreparer from apps/core -- see those classes' docstrings for
the underlying hazard this also applies to: SQLAlchemy's connection pool
(QueuePool) hands back the same physical connection across unrelated
requests, exactly like HikariCP, so a transaction-scoped GUC has to be
re-applied at the start of *every* transaction, not set once.

apps/brain connects as obligo_brain (V11), not obligo_app: it runs
PyMuPDF/PaddleOCR against untrusted, attacker-supplied file bytes, so it
gets its own minimally-scoped, NOBYPASSRLS role rather than inheriting
obligo_app's much broader identity-plane grants. Schema ownership (the
migrations that create both the role and the tables it can touch) still
lives in apps/core, per the blueprint.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import urlsplit

from sqlalchemy import Connection, Engine, create_engine, event, text

from obligo_brain.platform.tenancy.context import TenantContext


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")
    return value


def _brain_role_url() -> str:
    """Same host/port/database as DATABASE_URL (the Neon owner connection
    string apps/core's Flyway uses to run migrations), but logged in as
    obligo_brain instead -- same host/db, different login, exactly the
    relationship DatabaseConnectionDetails.appRoleFromEnv() has to
    ownerFromEnv() in Java.
    """
    owner = urlsplit(_require_env("DATABASE_URL"))
    password = _require_env("BRAIN_DB_PASSWORD")

    netloc = f"obligo_brain:{password}@{owner.hostname}"
    if owner.port:
        netloc += f":{owner.port}"

    query = f"?{owner.query}" if owner.query else ""
    return f"postgresql+psycopg://{netloc}{owner.path}{query}"


_engine: Engine | None = None


def reset_engine_for_forked_process() -> None:
    """Celery's prefork pool forks worker child processes from a parent.
    psycopg connections are not fork-safe -- if anything in the parent
    process called get_engine() before the fork (opening real TCP
    connections), every forked child would inherit those already-open
    sockets/connection state, silently corrupting them. This is a
    documented SQLAlchemy-under-Celery-prefork failure mode, not
    speculation, and it's tenant-isolation-adjacent, not just a stability
    concern: tenant_scope()'s guarantee rests on "one connection = one
    transaction = one SET LOCAL app.org_id" holding for every checkout, and
    a corrupted post-fork connection can violate that in ways that
    misbehave rather than cleanly crash.

    Wired to Celery's worker_process_init signal (tasks/celery_app.py),
    which fires in each child process immediately after fork, before it
    starts consuming tasks. Dropping the module-level singleton here --
    rather than calling engine.dispose() on it -- means the next
    get_engine() call in that child builds a brand new Engine from scratch,
    never reusing anything (including internal connection-pool state) that
    existed before the fork.
    """
    global _engine
    _engine = None


def get_engine() -> Engine:
    """One engine per process, created lazily on first use -- the Python
    analog of DataSourceConfig's single HikariDataSource bean.

    pool_size defaults to 5 like Hikari's DataSourceConfig; max_overflow=0
    makes it a hard cap rather than SQLAlchemy's default "burst beyond
    pool_size with temporary extra connections" behaviour, matching
    Hikari's maximumPoolSize semantics (which has no separate overflow
    concept -- it blocks, it doesn't open extra connections). This matters
    beyond tidiness: TenantIsolationTest's Java analog proves same-physical-
    connection reuse by pinning DATABASE_MAX_POOL_SIZE=1 for the test JVM;
    without max_overflow=0 here, the equivalent Python test could silently
    get two different physical connections instead and the "same PID"
    assertion would be unreliable rather than guaranteed.
    """
    global _engine
    if _engine is None:
        pool_size = int(os.environ.get("DATABASE_MAX_POOL_SIZE", "5"))
        _engine = create_engine(_brain_role_url(), pool_size=pool_size, max_overflow=0, pool_pre_ping=True)
        _register_tenant_guc_listener(_engine)
    return _engine


def _register_tenant_guc_listener(engine: Engine) -> None:
    """The Python analog of TenantConnectionPreparer. SQLAlchemy's `begin`
    connection event fires exactly at transaction start, on whichever
    physical connection the pool just handed back -- registered on the
    Engine (not a specific Connection), it applies to every connection this
    engine ever produces, the same "every checkout, every time" guarantee
    the AOP-around-@Transactional gives Java.

    set_config(..., true) is SET LOCAL semantics: transaction-scoped,
    automatically cleared at commit/rollback. Only set when a tenant
    context exists; otherwise app.org_id is left unset for this
    transaction, so RLS's NULLIF(current_setting(...), '')::uuid comparison
    is against NULL and every row fails the policy -- fail closed, not
    fail open, matching organizations_tenant_isolation / V3's reasoning.
    """

    @event.listens_for(engine, "begin")
    def _set_tenant_guc(conn: Connection) -> None:
        org_id = TenantContext.get()
        if org_id is not None:
            conn.execute(text("SELECT set_config('app.org_id', :org_id, true)"), {"org_id": str(org_id)})


@contextmanager
def tenant_scope() -> Iterator[Connection]:
    """The one sanctioned way apps/brain acquires a transactional
    connection -- the analog of a @Transactional-annotated repository
    method. Begins a transaction (firing the listener above), commits on
    clean exit, rolls back on exception.

    Unlike Java, there is no ArchUnit-style static check yet proving every
    DB access in apps/brain goes through this rather than a raw
    engine.connect(). That's a real gap relative to
    TenantIsolationArchitectureTest, left as follow-up, not assumed solved.
    """
    with get_engine().begin() as conn:
        yield conn
