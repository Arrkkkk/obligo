"""One-off manual recorder for the leading-subordinate-clause cassette
pair (tests/graphs/test_extraction_cassette.py's
test_leading_temporal_clause_* / test_leading_condition_clauses_*). Same
role as the adjacent record_cassettes.py, split into its own file because
these two cases need TWO recordings each -- one against v1 (the real,
reproducible bug found during the eval-pilot checkpoint; CLAUDE.md's Phase
4 section), one against v2 (prompts/extraction/v2.yaml's fix) -- rather
than record_cassettes.py's one-recording-per-case shape.

Not a pytest module (no test_ prefix, not collected), never run in CI --
same manual-generation-script role as record_cassettes.py and
tests/fixtures/pdfs/build_ocr_fixtures.py.

Deliberately loads whichever prompt version is CURRENTLY ACTIVE in
registry.yaml rather than pinning a version itself, and writes the output
filename as f"{case_name}_{prompt.version}.json" -- so recording the full
pair is: run this script once with registry.yaml pointed at v1, flip
registry.yaml to v2, run it again. No code change between runs, same
"flip registry.yaml, no redeploy" discipline prompts/registry.py's own
docstring describes.

Run manually:
    GROQ_API_KEY=... uv run --project apps/brain python \
        tests/cassettes/record_clause_boundary_cassettes.py

Makes exactly ONE live Groq call per case per run -- no retries, no loop
hunting for a specific outcome. Records and prints the REAL response and
the REAL grounding verdict, honestly, even if a given run's verdict
doesn't match what that prompt version was expected to produce.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from obligo_brain.graphs.extraction import extract_candidates, ground_candidates
from obligo_brain.graphs.state import SegmentRecord
from obligo_brain.models.providers import groq as groq_provider
from obligo_brain.prompts import registry as prompt_registry

CASSETTE_DIR = Path(__file__).parent / "extraction"

_SEGMENT_ID = "00000000-0000-0000-0000-000000000003"

# The exact two real sentences from the eval-pilot checkpoint's synthetic
# pilot (s5, s10) that reproduced the leading-subordinate-clause bug live,
# identically, across two separate pilot runs. Reused verbatim here rather
# than paraphrased, so this cassette pair is a direct, traceable regression
# test for the exact real finding, not a fresh guess at a similar shape.
_CASES: dict[str, str] = {
    "leading_temporal_clause": (
        "During the period from 2027-01-01 to 2027-12-31, Vendor may access "
        "Customer's testing environment for integration purposes."
    ),
    "leading_condition_clauses": (
        "If the Agreement is renewed and if Customer requests it in writing, "
        "Vendor should provide an updated data processing addendum to Customer."
    ),
}


def _record_one(case_name: str, segment_text: str, prompt) -> None:
    segment = SegmentRecord(id=_SEGMENT_ID, text=segment_text)

    call_result = extract_candidates(
        segment,
        chat_model=groq_provider.complete,
        prompt=prompt,
        model_id=prompt.model_constraints["model_id"],
        temperature=float(prompt.model_constraints.get("temperature", 0.0)),
    )
    grounded, rejected = ground_candidates(segment, call_result.candidates)

    CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
    cassette = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "model_id": call_result.completion.model_id,
        "prompt_version": prompt.version,
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
    out_path = CASSETTE_DIR / f"{case_name}_{prompt.version}.json"
    out_path.write_text(json.dumps(cassette, indent=2))

    print(f"=== {case_name} ({prompt.version}) -> {out_path.name} ===")
    print(f"raw content: {call_result.completion.content!r}")
    print(f"schema-valid candidates: {len(call_result.candidates)}")
    for r in call_result.rejected:
        print(f"  SCHEMA_INVALID: {r.detail}")
    print(f"grounded: {len(grounded)}  grounding-rejected: {len(rejected)}")
    for r in rejected:
        print(f"  {r.reason.value}: {r.detail}")
    print()


def main() -> None:
    prompt = prompt_registry.load("extraction")
    print(f"Recording against registry.yaml's currently active version: {prompt.version}\n")
    for case_name, segment_text in _CASES.items():
        _record_one(case_name, segment_text, prompt)


if __name__ == "__main__":
    main()
