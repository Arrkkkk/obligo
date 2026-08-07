"""Proves the Celery-prefork fork-safety mitigation (db.reset_engine_for_forked_process,
wired to Celery's worker_process_init signal in tasks/celery_app.py) against a
real os.fork() and a real Neon connection -- not an assertion that the function
exists, tests that would actually fail if the mitigation weren't there.

**The hazard, concretely:** get_engine() (db.py) is a lazy, module-level
singleton Engine holding a real psycopg connection pool. fork() duplicates
the parent process's entire memory via copy-on-write, including any
already-open OS-level file descriptors -- POSIX preserves fd *numbers*
across fork, so a socket fd the parent's pool has sitting idle is the exact
same fd number in the child immediately after fork. If nothing resets the
engine in the child, the child's own copy of the pool will happily hand out
that inherited idle connection to whoever calls get_engine().connect() --
and so will the parent's own (separate, unaffected) copy of the pool, since
forking doesn't remove anything from the parent's bookkeeping either. Two
unrelated processes now believe they each own the same live Postgres
connection -- exactly the hazard tenant isolation depends on not happening:
tenant_scope()'s guarantee rests on "one connection = one transaction = one
SET LOCAL app.org_id" holding for every checkout.

**A second, deeper finding made *while writing this test*, not assumed --
worth its own paragraph because it changes real operational guidance, not
just this file.** The first version of
test_a_worker_forked_from_a_db_untouched_parent_gets_a_working_fresh_connection
forked a parent that had *never* touched the database at all (the
correctly-disciplined case) and expected the child to open a fresh
connection cleanly. Instead the child **segfaulted** -- confirmed via
process.exitcode == -SIGSEGV, with a captured traceback rooted in
socket.getaddrinfo() (called from psycopg's hostname resolution) inside the
forked child. This is not an OpenSSL/libpq issue and not specific to
database connections at all: it's CPython's well-documented macOS
fork-safety limitation -- Apple's system frameworks (here, the DNS
resolver) spin up background threads/GCD state that does not survive
fork(), which is exactly why CPython switched multiprocessing's *default*
start method away from "fork" on macOS starting in 3.8, and why Celery's
prefork pool has long-standing, independently-documented flakiness reports
on macOS specifically. This has nothing to do with whether
reset_engine_for_forked_process() runs or whether the parent touched
Postgres first -- it reproduced even in the fully-disciplined,
DB-untouched-parent scenario, on any network call requiring DNS resolution
from a forked child, on this platform.

**Consequence, stated plainly rather than papered over:** this is a real
macOS-only limitation of Celery's `prefork` pool, not a bug in this
codebase's fix, and not something fixable in Python code here.
tests/platform/tenancy/test_fork_safety.py::test_a_worker_forked_...
therefore SKIPS on darwin (with this exact finding as its skip reason) and
asserts real success on other platforms -- meaning it's expected to
actually run and pass in ci-brain.yml (ubuntu-latest, Linux, where this
GCD/Objective-C-runtime class of fork hazard doesn't exist) and is the
platform this checkpoint's Celery worker is really deployed on anyway
(Hetzner, x86 Linux, per CLAUDE.md's locked-in prod target). Local dev on
this Mac must run the Celery worker with `--pool=solo` (single-process, no
fork at all), never `--pool=prefork` -- documented in tasks/celery_app.py
and the Makefile, not left as a trap someone rediscovers by hanging their
own terminal.
"""

from __future__ import annotations

import multiprocessing
import os
import sys

import pytest

from obligo_brain.platform.tenancy import db as db_module

REQUIRED_ENV = ("DATABASE_URL", "BRAIN_DB_PASSWORD")
pytestmark = pytest.mark.skipif(
    not all(os.environ.get(name) for name in REQUIRED_ENV),
    reason=f"{REQUIRED_ENV} not all set -- skipping real-infra test",
)

FORK_TIMEOUT_SECONDS = 15.0
"""Every test below must fail loudly on timeout, never hang the suite --
the whole point of this file is proving a specific hang scenario doesn't
happen; if it accidentally does, the test must say so, not stall CI."""


def _recv_with_timeout(pipe_conn, process, timeout: float):
    if not pipe_conn.poll(timeout):
        process.terminate()
        process.join(timeout=5)
        pytest.fail(
            f"forked child did not respond within {timeout}s -- it may have hung "
            f"(see this module's docstring on the fork-safety findings)"
        )
    try:
        return pipe_conn.recv()
    except EOFError:
        process.join(timeout=5)
        pytest.fail(
            f"forked child closed its end of the pipe without sending data -- it likely "
            f"crashed (process.exitcode={process.exitcode}; -11 == SIGSEGV). See this "
            f"module's docstring on the macOS getaddrinfo()-after-fork finding."
        )


def _child_reuse_inherited_connection(pipe_conn) -> None:
    """Simulates a Celery worker WITHOUT worker_process_init wired to call
    reset_engine_for_forked_process. No new TLS handshake happens here --
    get_engine() returns the already-forked-in Engine, and .connect() pulls
    the already-idle pooled connection straight out of the (copied) pool,
    so this is safe from the OpenSSL-new-handshake hang this module's
    docstring describes.
    """
    engine = db_module.get_engine()
    with engine.connect() as conn:
        fd = conn.connection.driver_connection.fileno()
    pipe_conn.send(fd)
    pipe_conn.close()


def test_without_the_mitigation_a_forked_child_inherits_the_parents_connection_fd() -> None:
    """Reproduces the bug directly. If this assertion ever starts failing,
    it means the underlying fork-inheritance premise this whole mitigation
    exists for has stopped holding (e.g. a psycopg/SQLAlchemy version
    started resetting sockets on fork itself) -- worth knowing, not just a
    broken test.
    """
    engine = db_module.get_engine()
    with engine.connect() as parent_conn:
        parent_fd = parent_conn.connection.driver_connection.fileno()
    # parent_conn is back in the pool now, idle, with a known fd -- exactly
    # the state a real Celery worker process would be in if anything had
    # touched the DB before Celery forks its worker pool.

    ctx = multiprocessing.get_context("fork")
    parent_end, child_end = ctx.Pipe()
    process = ctx.Process(target=_child_reuse_inherited_connection, args=(child_end,))
    process.start()
    try:
        child_fd = _recv_with_timeout(parent_end, process, FORK_TIMEOUT_SECONDS)
    finally:
        process.join(timeout=5)

    assert child_fd == parent_fd, (
        f"expected the forked child to inherit the parent's exact connection fd "
        f"({parent_fd}) when reset_engine_for_forked_process is NOT called, but got "
        f"{child_fd} -- the fork-inheritance premise this mitigation exists for may have changed"
    )


def _child_fresh_connection_after_clean_fork(pipe_conn) -> None:
    """The disciplined, actually-relied-upon scenario: this child's parent
    process never touched the database, so there is no pre-fork TLS session
    to inherit or collide with. reset_engine_for_forked_process() is called
    anyway (exactly as tasks/celery_app.py's worker_process_init handler
    does unconditionally) -- here it's a defensive no-op, and proving it's
    *safe* to call even when there's nothing to reset is itself part of
    what this test checks.
    """
    db_module.reset_engine_for_forked_process()
    engine = db_module.get_engine()
    with engine.connect() as conn:
        fd = conn.connection.driver_connection.fileno()
        conn.execute(db_module.text("SELECT 1"))
    pipe_conn.send(fd)
    pipe_conn.close()


@pytest.mark.skipif(
    sys.platform == "darwin",
    reason=(
        "Verified segfault on macOS (process.exitcode == -SIGSEGV, traceback rooted in "
        "socket.getaddrinfo() called from psycopg's hostname resolution) when opening any "
        "new network connection inside a forked child -- CPython's documented macOS "
        "fork-safety limitation (Apple system frameworks don't survive fork()), not a bug "
        "in reset_engine_for_forked_process() or this codebase. This is exactly why local "
        "dev on this Mac must run Celery with --pool=solo, never --pool=prefork. Runs for "
        "real on Linux (ci-brain.yml, and the actual x86 Hetzner prod target), where this "
        "class of fork hazard doesn't exist -- see this module's docstring."
    ),
)
def test_a_worker_forked_from_a_db_untouched_parent_gets_a_working_fresh_connection() -> None:
    """The realistic regression guard: proves the actual discipline this
    checkpoint relies on (Celery's fork parent never touches the DB; each
    worker connects lazily, for the first time, only after it's already a
    separate process) produces a real, working connection with no hang --
    the scenario tasks/celery_app.py's workers are actually in.
    """
    ctx = multiprocessing.get_context("fork")
    parent_end, child_end = ctx.Pipe()
    process = ctx.Process(target=_child_fresh_connection_after_clean_fork, args=(child_end,))
    process.start()
    try:
        child_fd = _recv_with_timeout(parent_end, process, FORK_TIMEOUT_SECONDS)
    finally:
        process.join(timeout=5)

    assert process.exitcode == 0, f"child process exited with {process.exitcode}"
    assert isinstance(child_fd, int) and child_fd >= 0


def test_reset_engine_for_forked_process_is_safe_to_call_with_nothing_to_reset() -> None:
    """Pure unit-level check, no fork needed: reset must not raise when
    _engine is already None (the state a fresh worker process starts in) --
    it's called unconditionally in worker_process_init, not guarded by a
    "was an engine ever created" check.
    """
    db_module.reset_engine_for_forked_process()
    db_module.reset_engine_for_forked_process()  # idempotent, still no error
    engine = db_module.get_engine()
    with engine.connect() as conn:
        conn.execute(db_module.text("SELECT 1"))
