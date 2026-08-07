"""Celery application for apps/brain's async segmentation checkpoint (§21
Phase 3). OCR is genuinely slow (Tesseract -- see CLAUDE.md's OCR-checkpoint
notes on observed latency); segmentation moves from a synchronous FastAPI
request to a Celery task queued on Redis (locked-in "Celery on Redis only"
choice).

**Hard rule, not a style preference: nothing in this module, and nothing
that runs in the process BEFORE Celery forks its worker pool, may call
get_engine()/tenant_scope() or otherwise open a network connection.** See
tests/platform/tenancy/test_fork_safety.py's module docstring for why,
verified empirically rather than assumed: opening a connection inside a
forked child, when the parent process already made one, has been observed
to hang (OpenSSL/libpq state) or segfault (macOS's DNS resolver specifically
-- confirmed via process.exitcode == -SIGSEGV). reset_engine_for_forked_process
(wired below via worker_process_init) is necessary defense-in-depth for a
mistake elsewhere, not the primary guarantee -- the primary guarantee is
this module never touching the DB at import/app-construction time, which is
why get_engine() is not called anywhere in this file.

**Broker only, no result backend.** Job state lives in Postgres
(segmentation_jobs, V15) -- a Celery-Redis result backend would be a second,
less tenant-scoped source of truth for "is this job done," and would spend
part of Upstash's free-tier monthly command budget on result storage that
duplicates what Postgres already tracks. task_ignore_result=True reflects
this: nothing in this codebase ever calls .get()/AsyncResult on a task.

**Single queue, not blueprint's full scan/parse/ocr three-stage pipeline.**
Deliberate scope decision for this checkpoint -- reuses blueprint's own
`ocr` queue name (§14) since OCR latency is the actual reason segmentation
needs to be async at all; the fuller multi-stage pipeline is real future
work, not built ahead of an actual need for it.

**Local dev pool: `--pool=solo`, not `--pool=prefork`.** Verified
empirically (test_fork_safety.py) that macOS segfaults inside a forked
child on any new network connection -- a CPython/macOS platform limitation
(Apple's system frameworks, here the DNS resolver, don't survive fork()),
not a bug in this codebase. `celery -A obligo_brain.tasks.celery_app worker
--pool=solo -Q ocr` is what the Makefile's dev target runs locally.
`--pool=prefork` (Celery's own default) is what CI and the real x86 Linux
Hetzner prod target use -- that platform doesn't have this fork hazard, and
is where test_fork_safety.py's skipped-on-darwin test actually runs for
real.
"""

from __future__ import annotations

import os

from celery import Celery
from celery.signals import worker_process_init

from obligo_brain.platform.tenancy.db import reset_engine_for_forked_process

OCR_QUEUE_NAME = "ocr"

DEFAULT_WORKER_CONCURRENCY = 2
"""Matches blueprint's own §14 OCR-queue concurrency number ("ocr | 2
(CPU-bound)"). NOT a verified-safe number against Upstash's actual
max-concurrent-connections ceiling -- checked their docs and troubleshooting
pages directly (not inferred): a real "ERR max concurrent connections
exceeded" error exists, but the tier-specific numeric ceiling is not
published anywhere found, and Upstash's own docs point to contacting
support@upstash.com for it. This is the deliberately conservative fallback
CLAUDE.md's OCR/async-checkpoint notes call for -- documented as unverified,
not assumed safe, same "bounded, not solved" posture as everything else in
this codebase. Revisit if/when the real ceiling is confirmed."""

DEFAULT_VISIBILITY_TIMEOUT_SECONDS = 1200
"""**Found empirically, while running the real broker-integration test, not
assumed:** kombu's Redis transport defaults visibility_timeout to 3600s (1
hour) -- confirmed by reading kombu/transport/redis.py directly
(`visibility_timeout = 3600`). This is the length of time an unacked
message sits invisible-but-undelivered before the broker assumes the
original consumer died and makes it visible for redelivery. Left at the
1-hour default, acks_late's whole purpose here would be undermined: a
worker OOM-killed mid-OCR wouldn't have its task redelivered to another
worker for up to an hour, directly contradicting this checkpoint's own
"not silently losing a source stuck mid-segmentation" goal.

Set to 1200s instead -- deliberately well ABOVE
segmentation.HARD_TIME_LIMIT_SECONDS (600s), not just "shorter than the
default." A visibility_timeout shorter than a task's legitimate maximum
runtime would cause premature redelivery: a SECOND worker could start the
same task while the FIRST worker is still validly processing it, and both
would race to write segmentation_jobs -- the second (redundant) worker's
eventual FAILED write (from a UNIQUE constraint violation on segments) could
clobber a job the first worker had already marked SUCCEEDED. 1200s gives
2x margin over the hard time limit specifically to make that race
structurally impossible, not just unlikely. (segmentation.py's
_mark_job_failed also guards against this defensively -- see its own
WHERE clause.)

Overridable via CELERY_VISIBILITY_TIMEOUT_SECONDS so tests can use a much
shorter value (redelivery in seconds, not 20 minutes) without touching the
production default."""

app = Celery(
    "obligo_brain",
    broker=os.environ.get("CELERY_BROKER_URL"),
    include=["obligo_brain.tasks.segmentation"],
)

app.conf.update(
    task_ignore_result=True,
    task_acks_late=True,
    # acks_late is the single most load-bearing setting here: without it,
    # Celery acks (discards) a task message BEFORE executing it, so a
    # hard-killed worker (OOM -- exactly the risk blueprint itself names
    # Tesseract/PaddleOCR as capable of causing, "the memory hog") loses
    # the task permanently and silently, with no retry. With acks_late, an
    # un-acked message becomes redeliverable to another worker instead --
    # but only after broker_transport_options' visibility_timeout elapses,
    # see DEFAULT_VISIBILITY_TIMEOUT_SECONDS above for why that default
    # needed overriding.
    broker_transport_options={
        "visibility_timeout": int(
            os.environ.get("CELERY_VISIBILITY_TIMEOUT_SECONDS", str(DEFAULT_VISIBILITY_TIMEOUT_SECONDS))
        ),
        # **Deliberately NOT setting polling_interval, after actually
        # testing it, not just leaving it at Celery's default by omission.**
        # An idle worker's own BRPOP polling only triggers kombu's
        # restore-overdue-messages check (Channel.QoS.restore_visible) as a
        # side effect of ticking, so a short polling_interval looked like
        # the fix for idle workers not noticing overdue unacked messages.
        # Tried it -- it didn't fix idle-worker promptness (a worker still
        # didn't self-restore within 60s in direct testing), and it
        # introduced a WORSE, genuinely confirmed problem: restore_visible()
        # uses an optimistic Redis WATCH/MULTI/EXEC transaction that
        # silently no-ops if it races another concurrent restore attempt --
        # with polling_interval set, the worker's own more-frequent
        # self-checks started racing against an external reconciler's
        # restore attempt and made manual/nudged redelivery LESS reliable,
        # not more. Confirmed by removing it again: an isolated
        # restore_visible() call (no worker polling concurrently) reliably
        # moves an overdue message back to the queue on the first attempt.
        # See tests/tasks/test_celery_broker_integration.py's module
        # docstring (Finding 2) for the full investigation and the design
        # conclusion this led to: Postgres-based staleness reconciliation
        # (api/v1/sources.py's STALE_PROCESSING_AFTER), not Redis-level
        # redelivery speed, is the real safety net here.
    },
    task_default_queue=OCR_QUEUE_NAME,
    worker_concurrency=int(os.environ.get("CELERY_WORKER_CONCURRENCY", str(DEFAULT_WORKER_CONCURRENCY))),
)


@worker_process_init.connect
def _reset_engine_on_worker_fork(**kwargs) -> None:
    """Fires in each forked worker child, immediately after fork, before it
    starts consuming tasks. See db.reset_engine_for_forked_process's own
    docstring and test_fork_safety.py for the full reasoning -- this is
    defense-in-depth for a mistake (something touching the DB pre-fork), not
    a substitute for this module's own "never connect before fork" rule.
    """
    reset_engine_for_forked_process()
