"""Runs the Tier-B `v4` conditions probe. See PREREGISTRATION.md, committed first.

Design notes that matter:

* **`v4` IS INJECTED, NOT ACTIVATED.** `prompt_registry.load()` reads
  `registry.yaml` and takes no explicit version, so this module patches it for
  the duration of the run. `registry.yaml` stays byte-identical
  (`extraction: default: v3`) and no gold cassette is staled. A registry flip is
  Tier C and waits for the §10 freeze pass.
* **Probe cassettes are written OUTSIDE the gold set**, under this directory, so
  `Cassette.verify()` on the gold set is untouched.
* **The cap is enforced by `record.Budget` in code**, not by counting. Exhaustion
  is checked at the start of each run, so a run already paid for is always
  written (the recorder's guarantee 2).
* **`--dry-run` exercises the whole path with a MockTransport and zero live
  calls.** Run it before spending anything; the live path differs only in the
  transport.
* **A DRY RUN WRITES TO A THROWAWAY ROOT (`_dryrun/`), AND THAT IS NOT
  COSMETIC.** The first version wrote mock cassettes to the REAL output path,
  where `_already_good()` would then verify them against the same segment, model,
  prompt and guideline version and report every live run as `SKIPPED` -- a live
  run that records nothing while looking like a clean success. Found by listing
  the output directory after the dry run rather than by reading the code.
  Standing Principle 7's shape: the dry run is a detector whose own artifacts
  silently defeat the thing it was meant to de-risk.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import pathlib
import sys
from uuid import UUID

import httpx

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "apps/brain"))
sys.path.insert(0, str(ROOT / "apps/brain/src"))

from evals.harness import cassette as cassette_mod  # noqa: E402
from evals.harness import fixtures, ratelimit, record  # noqa: E402
from obligo_brain.prompts import registry as prompt_registry  # noqa: E402

MODEL_ID = "openai/gpt-oss-120b"
GUIDELINE_VERSION = "v0.66"
RUNS = 3
# PREREGISTRATION.md §3's cap. Not a suggestion: `Budget` raises on exhaustion.
MAX_CALLS = 36

# (segment_id, doc_id). Order is PREREGISTRATION.md §3's, chosen so an early
# halt still leaves an interpretable result.
ARMS = [
    ("v4", "C11-094", "C11"),   # 1. achievability on the known-failing case
    ("v3", "E02-010", "E02"),   # 2. hold-out BASELINE -- without it (3) is uninterpretable
    ("v4", "E02-010", "E02"),   # 3. hold-out -- the only generalisation evidence
]


def pool_segments() -> dict[str, str]:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "corpus", ROOT / "apps/brain/evals/corpus.py")
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = c.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)}"
    return {s["segment_id"]: s["text"] for s in pool}


@contextlib.contextmanager
def injected_prompt(version: str):
    """Returns `prompts/extraction/<version>.yaml` for the extraction task, by
    patching the loader rather than the registry file."""
    real_load = prompt_registry.load
    path = ROOT / f"apps/brain/src/obligo_brain/prompts/extraction/{version}.yaml"
    assert path.exists(), f"no such prompt file: {path}"

    def fake_load(task, *, environment="default"):
        if task != "extraction":
            return real_load(task, environment=environment)
        import hashlib
        import yaml
        data = yaml.safe_load(path.read_text())
        system, user_template = data["system"], data["user_template"]
        return prompt_registry.Prompt(
            id=data["id"], version=data["version"], created=data["created"],
            system=system, user_template=user_template,
            model_constraints=data["model_constraints"],
            expected_schema=data.get("expected_schema", ""),
            changelog=tuple(data.get("changelog", [])),
            prompt_hash=hashlib.sha256(
                f"{system}\x00{user_template}".encode()).hexdigest(),
        )

    prompt_registry.load = fake_load
    try:
        loaded = fake_load("extraction")
        assert loaded.version == version, f"injection failed: got {loaded.version}"
        print(f"    prompt injected: extraction {loaded.version} "
              f"(hash {loaded.prompt_hash[:12]}, model "
              f"{loaded.model_constraints['model_id']}, "
              f"temp {loaded.model_constraints['temperature']})")
        yield loaded
    finally:
        prompt_registry.load = real_load


_CANNED = {
    "id": "dry", "object": "chat.completion", "created": 0, "model": MODEL_ID,
    "choices": [{"index": 0, "finish_reason": "stop", "message": {
        "role": "assistant",
        "content": json.dumps({"obligations": [{
            "span_text": "MOCK DRY RUN", "modality": "MUST", "obligor_alias": "",
            "obligee_alias": "", "action": "PROVIDE", "object_class": "x",
            "object_raw_text": "DRY", "temporal_raw": None,
            "condition_raws": [], "confidence": 0.5}]})}}],
    "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
}


def mock_transport_factory():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_CANNED,
                              headers={"x-ratelimit-limit-tokens": "8000"})
    return httpx.MockTransport(handler)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise the whole path with a MockTransport, zero live calls")
    ap.add_argument("--max-calls", type=int, default=MAX_CALLS)
    args = ap.parse_args()

    segments = pool_segments()
    for _, seg, _ in ARMS:
        assert seg in segments, f"{seg} not in the pool"
    print(f"pool gate: 1547 segments; probe segments present  PASS")

    per_doc: dict[str, list[tuple[str, str]]] = {}
    for _, seg, doc in ARMS:
        per_doc.setdefault(doc, [])
        if seg not in [s for s, _ in per_doc[doc]]:
            per_doc[doc].append((seg, segments[seg]))

    if not args.dry_run:
        # STRUCTURAL, not a content marker. A first version keyed on the string
        # "MOCK" in span_text and was BLIND to the nine mock cassettes actually on
        # disk, because they had been written before that marker existed -- a guard
        # that cannot see the artifacts it was written for. `responses[0].json.id`
        # is set by the canned payload and survives any later wording change.
        def _is_mock(path: pathlib.Path) -> bool:
            try:
                d = json.loads(path.read_text())
                return d["responses"][0]["json"].get("id") == "dry"
            except Exception:
                return False

        stray = [p for v in ("v3", "v4")
                 for p in (HERE / v).glob("*/run*.json")]
        existing = [p for p in stray if _is_mock(p)]
        if existing:
            raise SystemExit(
                f"REFUSING TO START: {len(existing)} dry-run cassette(s) are in the live "
                f"root and would be SKIPPED as already-good: {[str(p) for p in existing[:3]]}. "
                "Delete them first."
            )

    budget = record.Budget(max_calls=args.max_calls)
    window = ratelimit.TokenWindow()
    transport_factory = (mock_transport_factory if args.dry_run
                         else (lambda: httpx.HTTPTransport()))

    print(f"\nbudget: {args.max_calls} calls, HARD cap"
          f"{'  [DRY RUN -- no live calls]' if args.dry_run else '  [LIVE]'}")

    halted = None
    with fixtures.document_fixtures(per_doc) as fx:
        for version, seg, doc in ARMS:
            print(f"\n=== arm: {version} x {seg} ({RUNS} runs) "
                  f"[{budget.used}/{budget.max_calls} calls used] ===")
            with injected_prompt(version):
                def invoke(segment_id: str, chat_model):
                    from obligo_brain.graphs.pipeline import run_pipeline
                    from obligo_brain.platform.tenancy.context import TenantContext
                    uuid = fx[doc].segment_uuids[segment_id]
                    org = fx[doc].org_id
                    TenantContext.set(UUID(str(org)))
                    try:
                        return run_pipeline(str(uuid), str(org), chat_model=chat_model)
                    finally:
                        TenantContext.clear()

                session = record.RecordingSession(
                    budget=budget, window=window, invoke=invoke,
                    transport_factory=transport_factory,
                    model_id=MODEL_ID, prompt_version=version,
                    guideline_version=GUIDELINE_VERSION,
                    # A dry run must never write where a live run reads.
                    root=(HERE / "_dryrun" / version) if args.dry_run
                         else (HERE / version),
                )
                for run in range(1, RUNS + 1):
                    try:
                        out = session.record_run(seg, segments[seg], run)
                    except record.BudgetExhausted as exc:
                        print(f"  *** HARD HALT: {exc}")
                        halted = str(exc)
                        break
                    print(f"  run{run}: {out.status} calls={out.calls} "
                          f"attempts={out.attempts} {out.detail}")
            if halted:
                break

    print(f"\n=== spend: {budget.used}/{budget.max_calls} calls ===")
    if halted:
        print("HALTED -- resume only on explicit reviewer approval.")
        return 2
    print("all arms complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
