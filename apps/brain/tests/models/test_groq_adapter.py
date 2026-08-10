"""Pure unit tests for the Groq adapter's own HTTP-shape handling --
distinct from tests/graphs/test_extraction_cassette.py, which replays REAL
recorded model responses. These hand-build httpx.MockTransport responses
because they test THIS ADAPTER's request/response handling (correct
payload shape, token/latency parsing, failing closed without an API key),
never what a real model actually says -- see cassette_support.py's
docstring for why that distinction is kept explicit rather than blurred.

No live network call happens anywhere in this file.
"""

from __future__ import annotations

import json

import httpx
import pytest

from obligo_brain.models.providers import groq


def test_complete_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        groq.complete(system="s", user="u", model_id="m")


def test_complete_sends_expected_request_shape_and_parses_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(
            200,
            json={
                "model": "llama-3.3-70b-versatile",
                "choices": [{"message": {"content": '{"obligations": []}'}}],
                "usage": {"prompt_tokens": 42, "completion_tokens": 7},
            },
        )

    transport = httpx.MockTransport(handler)
    result = groq.complete(system="SYS", user="USR", model_id="llama-3.3-70b-versatile", transport=transport)

    assert result.content == '{"obligations": []}'
    assert result.input_tokens == 42
    assert result.output_tokens == 7
    assert result.model_id == "llama-3.3-70b-versatile"
    assert result.latency_ms >= 0

    request = captured["request"]
    assert request.method == "POST"
    assert request.url.path == "/openai/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"
    body = json.loads(request.content)
    assert body["model"] == "llama-3.3-70b-versatile"
    assert body["temperature"] == 0.0
    assert body["response_format"] == {"type": "json_object"}
    assert body["messages"] == [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "USR"},
    ]


def test_complete_raises_on_non_2xx(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(httpx.HTTPStatusError):
        groq.complete(system="s", user="u", model_id="m", transport=transport)


def test_list_models_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        groq.list_models()


def test_list_models_parses_model_ids(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"data": [{"id": "llama-3.3-70b-versatile"}, {"id": "gemma2-9b-it"}]}
        )

    transport = httpx.MockTransport(handler)
    models = groq.list_models(transport=transport)

    assert models == ["llama-3.3-70b-versatile", "gemma2-9b-it"]
