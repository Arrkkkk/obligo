"""Groq chat-completion adapter (blueprint §13.2's primary extraction
model: Llama 3.3 70B on Groq), implemented as module-level functions over
httpx -- the same style as platform/storage/supabase.py, not a class-based
client.

Deliberately NOT the `groq` PyPI package. Groq's REST API is
OpenAI-compatible (POST /openai/v1/chat/completions), httpx is already a
dependency, and CLAUDE.md's "ask first before adding a new dependency"
rule plus §13.1 rule 2 (models sit behind an adapter interface) are both
better served by one thin adapter than a second, differently-shaped SDK
that Gemini's eventual adapter would need its own version of anyway.

Model ID is passed in by the caller (prompts/extraction/v1.yaml's
model_constraints.model_id), never hardcoded here -- §13.8's own rule is
"pin model IDs explicitly... fail fast at boot," and the pin belongs in
the versioned prompt artifact, not this adapter. list_models() exists so
that ID can be verified against Groq's live model list by hand before
being written into the YAML, rather than trusted from training data --
nothing in this checkpoint calls it automatically, and no function in this
module touches the network at import time or during test collection; only
when actually invoked, and only once GROQ_API_KEY is set.
"""

from __future__ import annotations

import os
import time

import httpx

from obligo_brain.models.providers.base import ChatCompletion

_GROQ_API_BASE = "https://api.groq.com/openai/v1"


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")
    return value


def complete(
    *,
    system: str,
    user: str,
    model_id: str,
    temperature: float = 0.0,
    transport: httpx.BaseTransport | None = None,
) -> ChatCompletion:
    """One chat-completion call. `transport` is the cassette-replay seam --
    tests/graphs/test_extraction_cassette.py injects an httpx.MockTransport
    here so no real network call happens under test; production callers
    leave it None and get a real client.

    temperature=0.0 by default, matching §6.10's router policy
    ("deterministic seed/temperature=0 for extraction"). The real model
    router isn't built yet, but this adapter shouldn't need it to be for
    that default to hold.
    """
    api_key = _require_env("GROQ_API_KEY")
    payload = {
        "model": model_id,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    started = time.monotonic()
    with httpx.Client(transport=transport, timeout=60.0) as client:
        response = client.post(
            f"{_GROQ_API_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
    latency_ms = (time.monotonic() - started) * 1000

    response.raise_for_status()
    body = response.json()
    choice_content = body["choices"][0]["message"]["content"]
    usage = body.get("usage", {})

    return ChatCompletion(
        content=choice_content,
        model_id=body.get("model", model_id),
        input_tokens=int(usage.get("prompt_tokens", 0)),
        output_tokens=int(usage.get("completion_tokens", 0)),
        latency_ms=latency_ms,
    )


def list_models(transport: httpx.BaseTransport | None = None) -> list[str]:
    """GET /openai/v1/models -- a manual verification step for confirming a
    model ID is still live before pinning it in
    prompts/extraction/v1.yaml. Not called by any production code path or
    by CI (§13.8: "fail fast at boot with a clear message; pin model IDs
    explicitly" describes a boot-time smoke test for a real deployment,
    which doesn't exist yet at this checkpoint -- this is the one-off,
    by-hand equivalent until it does).
    """
    api_key = _require_env("GROQ_API_KEY")
    with httpx.Client(transport=transport, timeout=30.0) as client:
        response = client.get(
            f"{_GROQ_API_BASE}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
    response.raise_for_status()
    return [item["id"] for item in response.json().get("data", [])]
