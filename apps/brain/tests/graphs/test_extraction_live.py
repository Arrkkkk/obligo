"""Layer 3: the one deliberate exception to "unit tests never hit a
network" (blueprint §19.2). Opt-in, skipped by default, gated on
OBLIGO_LIVE_LLM=1 + GROQ_API_KEY -- the same skip-if-unset discipline
DATABASE_URL/SUPABASE_*/CELERY_BROKER_URL already use elsewhere in this
repo.

NOT wired into CI (ci-brain.yml). A rate-limited external dependency does
not belong on the merge path; catching model drift over time is the eval
harness's job (§19.7), a separate, not-yet-built deliverable. This test
exists for a human to run by hand -- to sanity-check the whole
Extractor -> Span Grounder path against a real model response before
trusting it, and as the (intentionally simple) mechanism for recording the
"happy_path" cassette: run with OBLIGO_RECORD_CASSETTE=happy_path set and
this test writes its real response into
tests/cassettes/extraction/happy_path.json. The other four cassette cases
(span_not_found, paraphrase, malformed_json, injection_canary) each need
their own segment text chosen to elicit that specific model behavior --
not something this one fixed-segment test can produce on demand -- so
recording those is a separate, manual step per cassette_support.py's
docstring, not automated here.

Because temperature=0.0 does not guarantee a fixed model version stays
byte-identical over time, this test asserts the pipeline's own invariants
(every candidate accounted for; the grounding gate runs) rather than exact
output content.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime

import pytest

from obligo_brain.graphs.extraction import extract_candidates, ground_candidates
from obligo_brain.graphs.state import SegmentRecord
from obligo_brain.models.providers import groq as groq_provider
from obligo_brain.prompts import registry as prompt_registry
from tests.graphs.cassette_support import CASSETTE_DIR

pytestmark = pytest.mark.skipif(
    not (os.environ.get("OBLIGO_LIVE_LLM") == "1" and os.environ.get("GROQ_API_KEY")),
    reason="OBLIGO_LIVE_LLM=1 and GROQ_API_KEY not both set -- skipping real Groq call",
)

_SAMPLE_SEGMENT_TEXT = (
    "Vendor shall notify Customer in writing within five (5) business days "
    "of Vendor's discovery of any Security Incident affecting Customer "
    "Personal Data. Vendor shall not disclose Customer Personal Data to "
    "any third party without Customer's prior written consent."
)
_SAMPLE_SEGMENT_ID = "00000000-0000-0000-0000-000000000001"


def test_live_extraction_against_a_real_segment_produces_grounded_candidates():
    prompt = prompt_registry.load("extraction")
    segment = SegmentRecord(id=_SAMPLE_SEGMENT_ID, text=_SAMPLE_SEGMENT_TEXT)

    call_result = extract_candidates(
        segment,
        chat_model=groq_provider.complete,
        prompt=prompt,
        model_id=prompt.model_constraints["model_id"],
        temperature=float(prompt.model_constraints.get("temperature", 0.0)),
    )
    grounded, rejected = ground_candidates(segment, call_result.candidates)

    # Every schema-valid candidate ends up grounded or rejected --
    # nothing silently dropped between extraction and grounding.
    assert len(grounded) + len(rejected) == len(call_result.candidates)
    # A real 70B model reading a two-sentence, unambiguously
    # obligation-bearing passage should find at least one candidate to
    # propose; if this ever fails, that's a real extraction-quality
    # signal worth looking at by hand, not an assertion to loosen.
    assert len(call_result.candidates) >= 1

    record_case = os.environ.get("OBLIGO_RECORD_CASSETTE")
    if record_case:
        CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
        cassette = {
            "recorded_at": datetime.now(UTC).isoformat(),
            "model_id": call_result.completion.model_id,
            "segment_id": segment.id,
            "segment_text": segment.text,
            "response": {
                "status_code": 200,
                "json": {
                    "model": call_result.completion.model_id,
                    "choices": [{"message": {"content": call_result.completion.content}}],
                    "usage": {
                        "prompt_tokens": call_result.completion.input_tokens,
                        "completion_tokens": call_result.completion.output_tokens,
                    },
                },
            },
        }
        (CASSETTE_DIR / f"{record_case}.json").write_text(json.dumps(cassette, indent=2))
