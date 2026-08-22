"""Strict, segment-keyed cassette replay for the gold-set harness.

WHY THIS EXISTS RATHER THAN REUSING tests/graphs/cassette_support.py. That
helper's own docstring is explicit: it "returns the cassette's recorded
response for ANY request... a store of one response per file." Correct for its
purpose, and unusable here for two reasons:

  1. The repair loop makes a SECOND and THIRD model call. One unconditional
     response would silently feed the extraction response back as the repair
     response.
  2. Section 6 requires the set to be run 3x with the per-item modal outcome
     and a count of items unstable across runs. With one recorded response the
     three replay runs are byte-identical, so instability is ALWAYS 0 -- a
     fabricated stability number.

KEYED BY SEGMENT, NOT BY ITEM. run_pipeline() runs per segment, and the 18 gold
items come from 12 segments -- C02-021 alone backs C02-01/02/03 from ONE call
sequence. Item-keying would record the same sequence three times.

STRICT IN BOTH DIRECTIONS. Overflow (more calls than recorded) raises rather
than silently reusing a response. Under-consumption (responses left unread)
also raises: it means the code path diverged from the one that was recorded --
the repair loop stopped firing, or a candidate that used to fail now compiles
-- which invalidates the replay while looking like a clean run.

STALENESS IS A HARD REFUSAL, NEVER A WARNING. A cassette records responses to a
specific input under a specific prompt and model. If the segment text, the
prompt version, or the model id has changed, every recorded response is about a
different question. Same posture as section 21 R5: never produce a number the
recorded evidence does not back.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import httpx

CASSETTE_DIR = Path(__file__).resolve().parent.parent / "cassettes" / "gold"


class CassetteError(RuntimeError):
    """Base for every condition that invalidates a replay."""


class CassetteMissing(CassetteError):
    pass


class CassetteOverflow(CassetteError):
    pass


class CassetteUnderflow(CassetteError):
    pass


class StaleCassette(CassetteError):
    pass


@dataclass(frozen=True)
class Cassette:
    segment_id: str
    run: int
    model_id: str
    prompt_version: str
    segment_sha256: str
    guideline_version: str
    recorded_at: str
    responses: tuple[dict[str, Any], ...]

    def verify(self, *, segment_text: str, model_id: str, prompt_version: str,
               guideline_version: str) -> None:
        """Raises StaleCassette on ANY mismatch. Every dimension is checked and
        all failures are reported together, so a re-record fixes them in one
        pass instead of one error at a time."""
        actual = hashlib.sha256(segment_text.encode()).hexdigest()
        problems = []
        if actual != self.segment_sha256:
            problems.append(
                f"segment text changed: recorded sha256 {self.segment_sha256[:16]}…, "
                f"now {actual[:16]}… -- every recorded response answers a different input"
            )
        if model_id != self.model_id:
            problems.append(f"model_id: recorded {self.model_id!r}, now {model_id!r}")
        if prompt_version != self.prompt_version:
            problems.append(
                f"prompt_version: recorded {self.prompt_version!r}, now {prompt_version!r}"
            )
        if guideline_version != self.guideline_version:
            problems.append(
                f"guideline_version: recorded {self.guideline_version!r}, now "
                f"{guideline_version!r}"
            )
        if problems:
            raise StaleCassette(
                f"cassette {self.segment_id}/run{self.run} is stale and MUST be re-recorded:\n  - "
                + "\n  - ".join(problems)
            )


def path_for(segment_id: str, run: int, root: Path | None = None) -> Path:
    return (root or CASSETTE_DIR) / segment_id / f"run{run}.json"


def load(segment_id: str, run: int, root: Path | None = None) -> Cassette:
    path = path_for(segment_id, run, root)
    if not path.exists():
        raise CassetteMissing(
            f"no cassette at {path}. Replay mode requires all 3 recorded runs "
            "(section 6): a stability number must never be produced from fewer."
        )
    raw = json.loads(path.read_text())
    return Cassette(
        segment_id=raw["segment_id"], run=int(raw["run"]), model_id=raw["model_id"],
        prompt_version=raw["prompt_version"], segment_sha256=raw["segment_sha256"],
        guideline_version=raw["guideline_version"], recorded_at=raw["recorded_at"],
        responses=tuple(raw["responses"]),
    )


class StrictPlayer:
    """Serves a cassette's responses in recorded order, once each."""

    def __init__(self, cassette: Cassette) -> None:
        self.cassette = cassette
        self._index = 0

    @property
    def consumed(self) -> int:
        return self._index

    @property
    def remaining(self) -> int:
        return len(self.cassette.responses) - self._index

    def transport(self) -> httpx.MockTransport:
        def handler(request: httpx.Request) -> httpx.Response:
            if self._index >= len(self.cassette.responses):
                raise CassetteOverflow(
                    f"cassette {self.cassette.segment_id}/run{self.cassette.run} recorded "
                    f"{len(self.cassette.responses)} model call(s); the code under replay "
                    f"made {self._index + 1}. Reusing a recorded response would silently "
                    "feed one call's answer to a different call -- re-record instead."
                )
            recorded = self.cassette.responses[self._index]
            self._index += 1
            return httpx.Response(status_code=recorded["status_code"], json=recorded["json"])

        return httpx.MockTransport(handler)

    def assert_fully_consumed(self) -> None:
        if self.remaining:
            raise CassetteUnderflow(
                f"cassette {self.cassette.segment_id}/run{self.cassette.run} recorded "
                f"{len(self.cassette.responses)} model call(s); the code under replay made "
                f"only {self._index}. The replayed path diverged from the recorded one, so "
                "this run is not a replay of it."
            )


def chat_model_for(player: StrictPlayer):
    """A ChatModel closure over the strict transport, matching the injection seam
    groq_provider.complete() already exposes."""
    # the real module path is models.providers.groq -- an earlier draft of this
    # file guessed `models.groq_provider` and no test caught it, because none of
    # them exercised this closure. Import it at module scope in the caller if you
    # want the failure at import time rather than first call.
    from obligo_brain.models.providers import groq as groq_provider

    transport = player.transport()

    def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0):
        return groq_provider.complete(
            system=system, user=user, model_id=model_id,
            temperature=temperature, transport=transport,
        )

    return chat_model


def write(cassette: Cassette, root: Path | None = None) -> Path:
    path = path_for(cassette.segment_id, cassette.run, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "segment_id": cassette.segment_id, "run": cassette.run,
        "recorded_at": cassette.recorded_at, "model_id": cassette.model_id,
        "prompt_version": cassette.prompt_version,
        "segment_sha256": cassette.segment_sha256,
        "guideline_version": cassette.guideline_version,
        "responses": list(cassette.responses),
    }, indent=2) + "\n")
    return path
