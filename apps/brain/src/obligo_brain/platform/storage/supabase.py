"""Minimal Supabase Storage read client for apps/brain (blueprint §11.1).

apps/brain never writes to storage -- Spring already owns the presigned
upload + commit flow (SupabaseStorageBlobStore.java) -- so this is
deliberately not a full BlobStore port, just the one read path the
segmentation checkpoint needs: fetch the bytes of an already-committed
source so PyMuPDF can extract from them.

Confirmed against the real Supabase Storage REST API via the Java adapter
this mirrors, not re-guessed from docs:
GET /object/authenticated/{bucket}/{key} with a service-role bearer token
returns the full object; any non-2xx means "not found or unreadable."

Reuses the same three env vars apps/core's BlobStoreConfig already requires
(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_STORAGE_BUCKET) -- one
Supabase project, one set of credentials, both services read them the same
way.
"""

from __future__ import annotations

import os

import httpx


class SupabaseObjectUnavailableError(RuntimeError):
    """Raised when Supabase Storage doesn't return the requested object."""


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")
    return value


def fetch_object(storage_key: str) -> bytes:
    """Fetch the full bytes of an object already committed to Supabase
    Storage. Raises SupabaseObjectUnavailableError on any non-2xx response.
    """
    supabase_url = _require_env("SUPABASE_URL")
    service_role_key = _require_env("SUPABASE_SERVICE_ROLE_KEY")
    bucket = _require_env("SUPABASE_STORAGE_BUCKET")

    url = f"{supabase_url}/storage/v1/object/authenticated/{bucket}/{storage_key}"
    response = httpx.get(url, headers={"Authorization": f"Bearer {service_role_key}"}, timeout=30.0)
    if not response.is_success:
        raise SupabaseObjectUnavailableError(
            f"Supabase Storage returned {response.status_code} for a read of {storage_key}"
        )
    return response.content
