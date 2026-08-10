"""Pure unit tests for extract_candidates()'s response-parsing logic
(_parse_response() in extraction.py) -- specifically the SCHEMA_INVALID
path. No live call, no cassette, no DB: a fake chat_model returns exactly
the content under test, proving OUR OWN parsing code handles a malformed
or wrongly-shaped response correctly, independent of whether any real
model actually produces one.

Written during the same session that attempted to record a real
malformed_json cassette (tests/graphs/test_extraction_cassette.py) and
found llama-3.3-70b-versatile simply didn't produce malformed output on a
single try -- that cassette's real recorded response is clean, valid JSON
(see that file's module docstring). This file exists so the SCHEMA_INVALID
gate has real test coverage regardless of whether any particular model
happens to trip it; before this file, that path had none at all.
"""

from __future__ import annotations

from obligo_brain.graphs.extraction import extract_candidates
from obligo_brain.graphs.state import RejectionReason, SegmentRecord
from obligo_brain.models.providers.base import ChatCompletion
from obligo_brain.prompts import registry as prompt_registry


def _fake_chat_model(content: str):
    def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0) -> ChatCompletion:
        return ChatCompletion(
            content=content, model_id=model_id, input_tokens=1, output_tokens=1, latency_ms=0.0
        )

    return chat_model


def _extract_with(content: str):
    prompt = prompt_registry.load("extraction")
    segment = SegmentRecord(id="seg-1", text="Vendor must notify Customer.")
    return extract_candidates(segment, chat_model=_fake_chat_model(content), prompt=prompt, model_id="fake-model")


def test_non_json_response_is_schema_invalid():
    result = _extract_with("Sorry, I cannot help with that request.")

    assert result.candidates == []
    assert len(result.rejected) == 1
    assert result.rejected[0].reason == RejectionReason.SCHEMA_INVALID


def test_json_missing_obligations_key_is_schema_invalid():
    result = _extract_with('{"result": []}')

    assert result.candidates == []
    assert result.rejected[0].reason == RejectionReason.SCHEMA_INVALID


def test_obligations_not_a_list_is_schema_invalid():
    result = _extract_with('{"obligations": "none"}')

    assert result.candidates == []
    assert result.rejected[0].reason == RejectionReason.SCHEMA_INVALID


def test_item_failing_pydantic_validation_is_schema_invalid_but_does_not_lose_valid_siblings():
    content = (
        '{"obligations": ['
        '{"span_text": "Vendor must notify Customer.", "modality": "MUST", '
        '"obligor_alias": "Vendor", "obligee_alias": "Customer", "action": "NOTIFY", '
        '"object_class": "notice", "object_raw_text": "Customer", "temporal_raw": null, '
        '"condition_raws": [], "confidence": 0.9},'
        '{"modality": "MUST"}'
        "]}"
    )

    result = _extract_with(content)

    assert len(result.candidates) == 1
    assert result.candidates[0].span_text == "Vendor must notify Customer."
    assert len(result.rejected) == 1
    assert result.rejected[0].reason == RejectionReason.SCHEMA_INVALID


def test_empty_obligations_array_is_not_an_error():
    result = _extract_with('{"obligations": []}')

    assert result.candidates == []
    assert result.rejected == []
