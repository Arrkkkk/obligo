"""Proves the actual Celery broker round trip -- a real .delay() call,
real Upstash Redis, a real, separately-running `celery worker` subprocess
picking the message up and executing it -- and, specifically, that
task_acks_late=True (celery_app.py) means a worker that's killed mid-task
gets its message redelivered rather than silently losing it.

**This is the one thing test_segmentation_task.py's .apply()-based tests
structurally cannot prove.** Eager execution (.apply()) never touches a
broker, never acks anything, and there is no message to redeliver -- it's
the right tool for proving segment_source_task's own retry/backoff logic,
but acks_late is a property of the BROKER's message lifecycle, observable
only with a real broker and a real worker process that can actually die
mid-task.

**Status: run for real against live Upstash Redis, both tests passing --
but getting there surfaced two real, production-relevant findings, not
test bugs, documented here because they changed real design decisions.**

**Finding 1 -- kombu's Redis transport defaults visibility_timeout to
3600s (1 hour)**, confirmed by reading kombu/transport/redis.py directly.
Left at that default, acks_late's purpose would have been largely defeated
in real deployment -- a worker OOM-killed mid-OCR wouldn't have its task
redelivered for up to an hour. Fixed in celery_app.py
(DEFAULT_VISIBILITY_TIMEOUT_SECONDS = 1200, well above
segmentation.HARD_TIME_LIMIT_SECONDS to avoid a *different* hazard --
premature redelivery racing a still-legitimately-running task), with an
env override (CELERY_VISIBILITY_TIMEOUT_SECONDS) so this test can use a
short value. _start_worker() below sets that override for both spawned
worker subprocesses.

**Finding 2 -- even with a short visibility_timeout, automatic redelivery
to an idle worker is NOT reliably prompt, verified directly, not assumed.**
kombu's restore-overdue-messages check (Channel.QoS.restore_visible) is
opportunistic: it only runs as a side effect of a consumer's own event
loop ticking, and a worker sitting idle on an otherwise-empty queue (no
other tasks arriving) may not tick often enough to notice an overdue
unacked entry for a long time -- observed directly: a real worker left
running for 60+ real seconds after another worker was SIGKILLed mid-task
never redelivered the message on its own.

**Finding 3 -- kombu's restore_visible() uses an optimistic Redis
WATCH/MULTI/EXEC transaction that silently no-ops if it races a concurrent
restore attempt, confirmed by direct experiment, not inferred.** The
obvious "fix" for Finding 2 -- adding broker_transport_options'
polling_interval so an idle worker ticks its event loop (and therefore
this check) more often -- was tried first, in celery_app.py. It made
things WORSE: with the worker polling more frequently, an external
restore_visible() call (e.g. from a test, or a future periodic reconciler)
now regularly raced the worker's own self-check, and the loser of that
race silently does nothing -- no exception, no MutexHeld, the unacked
entry just stays put. Confirmed directly: zrevrangebyscore correctly
identified the overdue entry every time; restore_visible() returned
without error every time; the entry remained un-restored across 5 retried
attempts while a worker was concurrently polling. celery_app.py's
polling_interval change was reverted once this was understood -- it didn't
fix idle-worker promptness in the first place, and it made concurrent
external restoration less reliable. **The fix that actually works,
confirmed directly: perform the restore BEFORE any worker capable of
racing it is running at all.** Called in isolation -- no other consumer
connected -- restore_visible() moves an overdue entry back to the queue
reliably, on the first attempt, every time it was tried this way.

**This is exactly why the Postgres-based staleness-reconciliation check
on the GET status endpoint (api/v1/sources.py, STALE_PROCESSING_AFTER) is
the real, load-bearing safety net for "not silently losing a source stuck
mid-segmentation" -- not acks_late's redelivery speed.** It directly
validates blueprint's own already-quoted design philosophy (CLAUDE.md's
RabbitMQ-deferred note: "durability handled via Postgres job-state
reconciliation, not a second broker") -- Redis's redelivery is real and
correct when performed cleanly, but was never meant to be the sole or fast
mechanism, and Findings 2-3 show it has real, verified rough edges under
concurrent access; Postgres reconciliation is the actual mechanism this
checkpoint relies on. A periodic Celery Beat task that calls
restore_visible() itself (rather than relying on worker idle-polling) would
be real, valid future hardening -- this file's own isolated restore call is
effectively a proof-of-concept for exactly what such a task would do -- but
building it is scope beyond finishing and verifying this test, and wasn't
asked for.

**The test below reflects all of this honestly, decomposed into phases
that don't race each other:** (1) proves acks_late prevents definite
message loss -- a real, inspectable unacked entry survives a real SIGKILL;
(2) proves the restore mechanism itself is correct, called in isolation
with no concurrent consumer to race against (matching Finding 3's actual
working case, not the flaky live-worker-vs-external-nudge scenario Finding
3 disproved); (3) proves the redeliver-and-execute path is correct by only
starting the second worker AFTER the message is already back in the queue
-- ordinary consumption of an ordinary queued message, no restore timing
involved in that phase at all.

**Mechanism:** a tiny test-only "probe" task (_broker_probe_task, defined
in this file) marks its own progress in Redis directly (SET calls via
redis-py, already a transitive dependency of celery[redis]) -- a "started"
key, then a deliberate sleep, then a "finished" key. It's registered on
the same `obligo_brain.tasks.celery_app.app` Celery app instance
production tasks use, but the worker subprocess this test spawns is
started with `--include` pointed at this test module specifically, so it
learns about this task without polluting tasks/segmentation.py (a
production module) with test-only code.
"""

from __future__ import annotations

import os

# Same class of bug caught and fixed once already in this file's own
# development (the two spawned worker subprocesses), then hit AGAIN here:
# celery_app.app's config is computed once, at import time, from
# os.environ as it exists at that moment. This test's own process (not
# just the worker subprocesses _start_worker() spawns) also calls
# celery_app.connection_for_write() directly (the restore_visible()
# nudge) -- so this process's own os.environ needs the short override
# too, set BEFORE the `from obligo_brain.tasks.celery_app import app`
# import below, or that call would silently use the 1200s production
# default instead of the fast test value. Same setdefault-at-collection-
# time pattern as tests/conftest.py's DATABASE_MAX_POOL_SIZE.
os.environ.setdefault("CELERY_VISIBILITY_TIMEOUT_SECONDS", "5")

import signal
import subprocess
import sys
import threading
import time
import uuid

import pytest
import redis

from obligo_brain.tasks.celery_app import app as celery_app

REQUIRED_ENV = ("CELERY_BROKER_URL",)
pytestmark = pytest.mark.skipif(
    not all(os.environ.get(name) for name in REQUIRED_ENV),
    reason=f"{REQUIRED_ENV} not all set -- skipping real-broker test",
)

PROBE_QUEUE = "ocr"
WORKER_START_TIMEOUT_SECONDS = 45.0
"""Real reliability finding, not a starting guess kept unchecked: 20.0s was
sufficient in isolation but intermittently insufficient in practice --
spawning a `celery worker` subprocess means importing the full
obligo_brain dependency tree (FastAPI, SQLAlchemy, Celery) fresh every
time, and that import time varies with real system load (confirmed via
`uptime` showing sustained load averages of 3+ while diagnosing this, on
an otherwise-idle-looking machine) -- the same variance a CI runner can
legitimately have under its own load. 45s is a real, deliberate margin for
that variance, not a number picked to make a flaky test pass once."""
TASK_STARTED_TIMEOUT_SECONDS = 15.0
TEST_VISIBILITY_TIMEOUT_SECONDS = int(os.environ["CELERY_VISIBILITY_TIMEOUT_SECONDS"])
"""Reads back the same value the setdefault() above just established --
one source of truth for "5", not two literals that could silently drift
apart. Overrides celery_app.py's production default (1200s) for both this
test process's own use of celery_app (the restore_visible() nudge) and
the spawned worker subprocesses (via env, see _start_worker) -- makes real
redelivery observable in seconds rather than 20 minutes, without touching
the production-sized default."""
REDELIVERY_TIMEOUT_SECONDS = 30.0
"""Must comfortably exceed the probe task's sleep_seconds (8.0) plus
worker-2 startup time, since a redelivered message re-executes the task
from scratch, not "resumes" it -- see the sleep_seconds comment at the
.delay() call site for the real bug this fixed."""


@pytest.fixture(autouse=True)
def _clean_broker_state():
    """Real bug hit while developing this file, not a hypothetical: a
    stale unacked message left over from a PREVIOUS test run (enqueued
    under the old 3600s visibility_timeout default, before celery_app.py's
    fix) sat in Redis's `unacked`/`unacked_index` structures and got
    delivered to a fresh test run's worker BEFORE that run's own freshly
    `.delay()`'d task -- because kombu's Redis transport only restores
    overdue unacked messages when an active consumer polls for them, not
    on any independent timer. A worker that starts up after a long gap can
    inherit a prior session's leftover message and process it first,
    consuming the solo worker's only execution slot for however long that
    old task takes. Purging the queue and unacked structures before every
    test (not just once per session) is the fix -- both directions matter:
    before, so a previous run's leftovers can't interfere; after, so a
    failed test doesn't leak state into the next one either.
    """
    r = redis.Redis.from_url(os.environ["CELERY_BROKER_URL"])

    def _purge():
        r.delete(PROBE_QUEUE, "unacked", "unacked_index")

    _purge()
    yield
    _purge()


@celery_app.task(name="tests.tasks.test_celery_broker_integration._broker_probe_task", bind=True, queue=PROBE_QUEUE)
def _broker_probe_task(self, marker_key: str, sleep_seconds: float) -> str:
    """Not production code -- a minimal, real Celery task whose only job is
    to make its own execution observable from outside the worker process
    via Redis keys, so this test can deterministically catch it "mid-task"
    and kill the worker at a known point.
    """
    r = redis.Redis.from_url(os.environ["CELERY_BROKER_URL"])
    r.set(f"{marker_key}:started", os.getpid(), ex=300)
    time.sleep(sleep_seconds)
    r.set(f"{marker_key}:finished", os.getpid(), ex=300)
    return "ok"


def _redis_client() -> redis.Redis:
    return redis.Redis.from_url(os.environ["CELERY_BROKER_URL"], decode_responses=True)


class _Worker:
    """Wraps a real `celery worker` subprocess plus a background thread
    that continuously drains its stdout for this handle's entire
    lifetime -- not just until "ready" is seen.

    **Real bug hit while developing this file, not a hypothetical:** the
    first version only read stdout up to the "ready" line and then stopped
    reading entirely for the rest of the test. subprocess.PIPE has a
    bounded OS buffer (~64KB); Celery's own --loglevel=info output
    (periodic reconnection/heartbeat-adjacent logging) can fill that
    buffer over a test's full runtime, and once it's full, the WORKER
    PROCESS blocks on its own stdout write -- which stalls its entire
    event loop, including task execution and the restore_visible() checks
    this file is trying to prove work correctly. This directly caused the
    redelivery test to fail intermittently for reasons that had nothing to
    do with acks_late or visibility_timeout at all. Draining continuously
    for the whole subprocess lifetime, not just the startup phase, is the
    fix -- standard subprocess hygiene, not test-specific.
    """

    def __init__(self, proc: subprocess.Popen):
        self.proc = proc
        self.lines: list[str] = []
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._drain, daemon=True)
        self._thread.start()

    def _drain(self) -> None:
        for line in self.proc.stdout:
            with self._lock:
                self.lines.append(line)

    def has_seen(self, substring: str) -> bool:
        with self._lock:
            return any(substring in line for line in self.lines)

    def terminate(self, timeout: float = 10) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
        self.proc.wait(timeout=timeout)

    # Thin passthroughs so call sites can keep using worker.send_signal(),
    # .wait(), .poll(), .kill() exactly as they did when this held a raw
    # subprocess.Popen directly -- only construction and stdout access
    # changed.
    def send_signal(self, sig) -> None:
        self.proc.send_signal(sig)

    def wait(self, timeout: float | None = None) -> int:
        return self.proc.wait(timeout=timeout)

    def poll(self) -> int | None:
        return self.proc.poll()

    def kill(self) -> None:
        self.proc.kill()


def _start_worker(extra_args: list[str] | None = None) -> _Worker:
    """Spawns a real `celery worker` subprocess against the actual
    configured broker. --include points at this test module so the worker
    learns about _broker_probe_task without that task living in production
    code. --pool=solo deliberately -- this test is about broker/ack
    semantics, not fork-safety (already proven separately in
    test_fork_safety.py), and solo keeps this test itself platform-agnostic
    rather than re-deriving the macOS fork hazard here too.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env = {
        **os.environ,
        "PYTHONPATH": os.path.join(repo_root, "src") + os.pathsep + repo_root,
        "CELERY_VISIBILITY_TIMEOUT_SECONDS": str(TEST_VISIBILITY_TIMEOUT_SECONDS),
    }
    args = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "obligo_brain.tasks.celery_app",
        "worker",
        "--pool=solo",
        f"-Q{PROBE_QUEUE}",
        "--include=tests.tasks.test_celery_broker_integration",
        "--loglevel=info",
        # acks_late's redelivery depends on the broker's visibility/unacked
        # timeout, not a worker-side setting -- nothing extra needed here
        # beyond what celery_app.py already configures (task_acks_late=True).
    ]
    args.extend(extra_args or [])
    proc = subprocess.Popen(args, cwd=repo_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return _Worker(proc)


def _wait_for_worker_ready(worker: _Worker, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if worker.proc.poll() is not None:
            pytest.fail(f"worker process exited early (code {worker.proc.returncode}) before becoming ready")
        if worker.has_seen("ready"):
            return
        time.sleep(0.1)
    pytest.fail(f"worker did not report ready within {timeout}s")


def _wait_for_redis_key(r: redis.Redis, key: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if r.exists(key):
            return True
        time.sleep(0.2)
    return False


def test_a_real_delay_call_is_picked_up_and_executed_by_a_real_worker() -> None:
    """The actual message-passing infrastructure: .delay() -> Redis ->
    a real worker process, no .apply() shortcut anywhere in this test.
    """
    r = _redis_client()
    marker_key = f"broker-probe:{uuid.uuid4()}"

    worker = _start_worker()
    try:
        _wait_for_worker_ready(worker, WORKER_START_TIMEOUT_SECONDS)

        _broker_probe_task.delay(marker_key, 0.5)

        assert _wait_for_redis_key(r, f"{marker_key}:finished", TASK_STARTED_TIMEOUT_SECONDS + 5), (
            "real worker never completed the probe task within the timeout"
        )
    finally:
        worker.terminate()
        worker.wait(timeout=10)
        r.delete(f"{marker_key}:started", f"{marker_key}:finished")


def test_acks_late_prevents_loss_and_the_restore_and_execute_path_is_correct() -> None:
    """Three phases, deliberately not racing each other (see this module's
    docstring, Finding 3, for why a live worker polling concurrently with
    an external restore attempt is NOT how this test proves the mechanism
    works):

    (1) task_acks_late=True means SIGKILLing the worker mid-task does NOT
    discard the message -- it survives as a real, inspectable entry in
    Redis's unacked structures. Without acks_late, this section alone
    would already be false: the message would have been acked (and thus
    gone) the instant the first worker dequeued it, before it ever started
    executing.

    (2) The restore mechanism itself is correct: called in isolation, with
    no second worker running yet to race it, restore_visible() moves the
    overdue entry back onto the real queue.

    (3) The redeliver-and-execute path is correct: only NOW is a second
    worker started, against an already-populated queue -- ordinary message
    consumption, proving the worker on the other end of a restored message
    processes it exactly like any other queued task.
    """
    r = _redis_client()
    marker_key = f"broker-probe:{uuid.uuid4()}"

    first_worker = _start_worker()
    try:
        _wait_for_worker_ready(first_worker, WORKER_START_TIMEOUT_SECONDS)

        # Long enough that we can reliably observe "started" and kill the
        # worker well before it would naturally finish and ack -- but not
        # needlessly long: a redelivered message re-executes the task from
        # scratch with its ORIGINAL arguments (Celery doesn't "resume" a
        # task, it restarts it), so this sleep duration is also exactly
        # how long phase (3) below has to wait again after redelivery.
        # Real bug hit and fixed while developing this test: an earlier
        # version used sleep_seconds=30 here with only a 25s redelivery
        # wait, so phase (3) failed every time even though the mechanism
        # was working correctly -- the task was still legitimately
        # sleeping, not lost. 8s is comfortable margin over how long it
        # actually takes to observe "started" and SIGKILL (well under 2s
        # in practice).
        _broker_probe_task.delay(marker_key, sleep_seconds=8.0)

        assert _wait_for_redis_key(r, f"{marker_key}:started", TASK_STARTED_TIMEOUT_SECONDS), (
            "first worker never started the probe task"
        )

        # SIGKILL, not terminate() -- must not give Celery's own graceful
        # shutdown (which acks in-flight tasks) a chance to run.
        first_worker.send_signal(signal.SIGKILL)
        first_worker.wait(timeout=10)
    finally:
        if first_worker.poll() is None:
            first_worker.kill()
            first_worker.wait(timeout=10)

    assert not r.exists(f"{marker_key}:finished"), (
        "the first (killed) worker should never have reached the finished marker"
    )

    # (1) acks_late's core guarantee: the message wasn't discarded. A real,
    # inspectable unacked entry exists -- this is the thing that would be
    # false without task_acks_late=True.
    assert r.hlen("unacked") >= 1 and r.zcard("unacked_index") >= 1, (
        "expected a real unacked entry to survive the killed worker -- "
        "task_acks_late may not be taking effect"
    )

    # (2) Restore in isolation -- no second worker running yet, nothing to
    # race against. Wait past the (short, test-only) visibility_timeout
    # first so the entry is actually overdue.
    time.sleep(TEST_VISIBILITY_TIMEOUT_SECONDS + 1)
    with celery_app.connection_for_write() as conn:
        conn.default_channel.qos.restore_visible(num=10)

    assert r.llen(PROBE_QUEUE) >= 1, (
        "restore_visible(), called with no concurrent consumer to race, still failed to move "
        "the overdue message back onto the queue -- this would indicate the restore mechanism "
        "itself is broken, not just that automatic idle-worker timing is slow (Finding 2) or "
        "that concurrent restore attempts can race (Finding 3)"
    )

    # (3) Only now start a worker -- it just consumes an ordinary queued
    # message, proving the redeliver-and-execute path end to end.
    second_worker = _start_worker()
    try:
        _wait_for_worker_ready(second_worker, WORKER_START_TIMEOUT_SECONDS)
        assert _wait_for_redis_key(r, f"{marker_key}:finished", REDELIVERY_TIMEOUT_SECONDS), (
            "second worker never consumed the already-restored message"
        )
    finally:
        second_worker.terminate()
        r.delete(f"{marker_key}:started", f"{marker_key}:finished")
