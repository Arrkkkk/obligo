"""Tenant context propagation for apps/brain (blueprint §10.9, Python side).

Mirrors dev.obligo.core.platform.tenancy.TenantContext's calling convention
(set/get/clear) exactly, but the underlying primitive has to change, not
just the syntax. Spring/Tomcat is thread-per-request, so a ThreadLocal is a
safe stand-in for "current request's org_id." FastAPI's concurrency model is
asyncio: many concurrent request coroutines can be multiplexed onto one OS
thread, so a threading.local()-based port would leak one request's org_id
into another's mid-await, silently. contextvars.ContextVar is task-scoped
under asyncio and isolates concurrent requests correctly. It also survives
the sync/async boundary: Starlette dispatches `def` (sync) endpoints to a
threadpool via contextvars.copy_context(), which snapshots and propagates
the ContextVar's value into that worker thread -- so this is safe for both
sync and async routes without extra plumbing.

Same tripwire as Java's: callers must always clear() in a finally block.
"""

from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID


class TenantContext:
    _current: ContextVar[UUID | None] = ContextVar("obligo_brain_tenant_org_id", default=None)

    def __init__(self) -> None:
        raise TypeError("TenantContext is not instantiable; use its classmethods")

    @classmethod
    def set(cls, org_id: UUID) -> None:
        cls._current.set(org_id)

    @classmethod
    def get(cls) -> UUID | None:
        return cls._current.get()

    @classmethod
    def clear(cls) -> None:
        cls._current.set(None)
