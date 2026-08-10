"""Cassette-replay support for Layer 2 extraction tests (blueprint §19.2:
"every LLM call in unit tests is replayed from a recorded cassette...
unit tests never hit a network"). No `vcrpy` dependency -- httpx already
ships MockTransport, which is all a fixed-response cassette store needs,
and CLAUDE.md's "ask first before adding a new dependency" rule plus
Standing Principle 5 both argue against pulling one in for this.

No cassettes exist in this repo yet. Recording one needs a real Groq call,
and this checkpoint's live call was deliberately deferred to its own
explicitly-confirmed step (a Groq key was provisioned mid-checkpoint, but
"key exists" and "make the call" were kept as two separate decisions --
see this checkpoint's own chat transcript). Every test in
test_extraction_cassette.py skips individually, one case at a time, until
its cassette file exists -- the same skip-if-real-infra-absent discipline
test_symbols.py (DATABASE_URL/BRAIN_DB_PASSWORD) and ci-brain.yml
(SUPABASE_*, CELERY_BROKER_URL) already use.

To record a cassette once a live call is separately approved: call
obligo_brain.models.providers.groq.complete() for real against a real
segment (temperature=0.0, the model_id pinned in
prompts/extraction/v1.yaml -- verified against list_models() first, not
trusted from this file), then write the request/response into
CASSETTE_DIR/<case_name>.json in the shape load_cassette() expects:

{
  "recorded_at": "<ISO date>",
  "model_id": "<the real model_id used>",
  "segment_id": "<a fake UUID -- fine, this is a fixture>",
  "segment_text": "<the real segment text sent>",
  "response": {
    "status_code": 200,
    "json": { ... the real, complete, unedited response body ... }
  }
}

Deliberately want REAL, unedited model output in each cassette, not
hand-fabricated JSON -- the whole point of this layer is proving this
code handles what the model actually said, not what we imagine it might
say. The one exception the checkpoint's design explicitly allows is
"malformed_json" (see test_extraction_cassette.py), where the point is
proving our own parse-failure path -- a genuinely malformed body can still
be a real captured response (models do sometimes emit broken JSON) rather
than needing to be synthesized.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

CASSETTE_DIR = Path(__file__).parent.parent / "cassettes" / "extraction"


def load_cassette(case_name: str) -> dict | None:
    path = CASSETTE_DIR / f"{case_name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def transport_for_cassette(cassette: dict) -> httpx.MockTransport:
    """A transport that returns the cassette's recorded response for any
    request. Deliberately does not inspect the request at all and has no
    fallback path to a real network call -- a cassette-replay client must
    never silently make a live call, and returning the one recorded
    response unconditionally is simpler and just as safe as a "match or
    raise" scheme for a store of one response per file.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        response = cassette["response"]
        return httpx.Response(status_code=response["status_code"], json=response["json"])

    return httpx.MockTransport(handler)
