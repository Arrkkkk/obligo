"""F34 temporal-interaction probe — the LIVE arm only.

Everything about this run is fixed by PREREGISTRATION.md, committed and pushed
in `d49378d` (cap revised to 18 in `adabe90`) BEFORE any call. This module
executes it; it decides nothing.

WHAT IS LIVE AND WHAT IS NOT. The `v3` baselines for both targets and the WHOLE
control arm already exist as committed cassettes, so they cost zero calls and
are read by `score_probe.py` rather than recorded here. This module records
exactly `v4 x C17-006 x 3` and `v4 x C04-017 x 3` -- 6 invocations.

* **`v4` IS INJECTED, NOT ACTIVATED.** `registry.yaml` stays byte-unchanged at
  `extraction: default: v3`; the loader is patched for the extraction task only.
* **The cap is enforced by `record.Budget` in code**, not by counting, and at 18
  it is the structural ceiling (6 invocations x max 3 calls) rather than
  headroom -- see PREREGISTRATION.md §6.
* **A 400 is FATAL by design** (`C17-021`/`C04-144`'s precedent): the recorder
  retries 429 only, and a 400 is not a pacing problem.
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

from evals.harness import fixtures, ratelimit, record  # noqa: E402
from obligo_brain.prompts import registry as prompt_registry  # noqa: E402

MODEL_ID = "openai/gpt-oss-120b"
GUIDELINE_VERSION = "v0.68"
RUNS = 3
EXPECTED_TPM = 8_000
# PREREGISTRATION.md §6 as revised 2026-10-19. NOT a suggestion: Budget raises.
MAX_CALLS = 18

# §6's order: C17-006 first -- one gold item, no byte-identical span group, and
# UNMAPPABLE_TEMPORAL on 3 of 3 under v3 -- so an early halt still interprets.
ARMS = [
    ("v4", "C17-006", "C17"),
    ("v4", "C04-017", "C04"),
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
    """Return `prompts/extraction/<version>.yaml`, patching the loader rather
    than the registry file."""
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


def is_mock(path: pathlib.Path) -> bool:
    """STRUCTURAL, not a content marker.

    The conditions probe's first guard keyed on the string "MOCK" in span_text
    and was BLIND to the nine mock cassettes already on disk, printing
    "guard would fire: False" over the very files it existed to catch.
    `responses[0].json.id` is set by the canned payload and survives any later
    wording change.
    """
    try:
        d = json.loads(path.read_text())
        return d["responses"][0]["json"].get("id") == "dry"
    except Exception:
        return False


def refuse_stray_mocks() -> None:
    stray = [p for p in (HERE / "v4").glob("*/run*.json") if is_mock(p)]
    if stray:
        raise SystemExit(
            f"REFUSING TO START: {len(stray)} dry-run cassette(s) sit in the LIVE root and "
            f"would be SKIPPED as already-good: {[str(p) for p in stray[:3]]}. Delete them."
        )


def catalogue_check() -> None:
    """Mandatory pre-spend check (the 2026-08-22 retired-model incident).

    Goes through the project's own httpx path, NOT urllib: the conditions probe
    got HTTP 403 `error code: 1010` from urllib, which is Cloudflare's edge block
    on the client fingerprint and not a Groq error at all. Costs no tokens.
    """
    from obligo_brain.models.providers import groq as groq_provider
    models = groq_provider.list_models()
    print(f"    catalogue: {len(models)} models; {MODEL_ID} "
          f"{'PRESENT' if MODEL_ID in models else '*** ABSENT ***'}")
    if MODEL_ID not in models:
        raise SystemExit(f"HALT: {MODEL_ID} absent from the catalogue.")


def assert_tpm_or_halt(window) -> None:
    """Halt unless an x-ratelimit-limit-tokens header was ACTUALLY OBSERVED and
    equals the 8,000 the approved arithmetic assumes.

    `ceiling` is pre-seeded to BOOTSTRAP_TPM and `observe_ceiling()` is reached
    only after the provider call RETURNS, so a session whose calls all raise
    leaves a GUESS that prints exactly like a measurement. That happened on the
    batches 5-6 resume. `ceiling_observations` is the only honest discriminator.
    """
    seen = list(window.ceiling_observations)
    if not seen:
        raise SystemExit(
            "HALT: no x-ratelimit-limit-tokens header was observed on any call, so TPM is "
            f"UNMEASURED. window.ceiling is {window.ceiling} but that is BOOTSTRAP_TPM, a "
            "pre-read guess, and must not be reported as measured."
        )
    observed = seen[-1]
    print(f"    TPM MEASURED from headers: x-ratelimit-limit-tokens={observed} "
          f"({len(seen)} observation(s))")
    if int(observed) != EXPECTED_TPM:
        raise SystemExit(
            f"HALT AND REPORT, per the approval: measured TPM {observed} != {EXPECTED_TPM}."
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise the whole path with a MockTransport, zero live calls")
    ap.add_argument("--max-calls", type=int, default=MAX_CALLS)
    args = ap.parse_args()

    assert args.max_calls <= MAX_CALLS, (
        f"cap {args.max_calls} exceeds the pre-registered {MAX_CALLS}")

    segments = pool_segments()
    for _, seg, _ in ARMS:
        assert seg in segments, f"{seg} not in the pool"
    print("pool gate: 1547 segments; probe segments present  PASS")

    if not args.dry_run:
        refuse_stray_mocks()
        print("stray-mock gate: live root clean  PASS")
        catalogue_check()

    per_doc: dict[str, list[tuple[str, str]]] = {}
    for _, seg, doc in ARMS:
        per_doc.setdefault(doc, []).append((seg, segments[seg]))

    budget = record.Budget(max_calls=args.max_calls)
    window = ratelimit.TokenWindow()
    transport_factory = (mock_transport_factory if args.dry_run
                         else (lambda: httpx.HTTPTransport()))

    print(f"\nbudget: {args.max_calls} calls, HARD cap"
          f"{'  [DRY RUN -- no live calls]' if args.dry_run else '  [LIVE]'}")

    halted, tpm_checked = None, False
    recorded = skipped = 0
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
                    # A dry run must NEVER write where a live run reads.
                    root=(HERE / "_dryrun" / version) if args.dry_run
                         else (HERE / version),
                )
                for run in range(1, RUNS + 1):
                    try:
                        out = session.record_run(seg, segments[seg], run)
                    except record.BudgetExhausted as exc:
                        print(f"  *** HARD HALT (cap): {exc}")
                        halted = f"cap: {exc}"
                        break
                    except httpx.HTTPStatusError as exc:
                        body = ""
                        with contextlib.suppress(Exception):
                            body = exc.response.text[:400]
                        print(f"  *** HARD HALT (HTTP {exc.response.status_code}): {body}")
                        halted = f"HTTP {exc.response.status_code}: {body}"
                        break
                    print(f"  run{run}: {out.status} calls={out.calls} "
                          f"attempts={out.attempts} {out.detail}")
                    if out.status == "RECORDED":
                        recorded += 1
                        if not tpm_checked:
                            assert_tpm_or_halt(window)
                            tpm_checked = True
                    elif out.status == "SKIPPED":
                        skipped += 1
            if halted:
                break

    print(f"\n=== spend: {budget.used}/{budget.max_calls} calls ===")
    print(f"=== recorded={recorded} skipped={skipped} ===")
    if not tpm_checked and recorded == 0 and not args.dry_run:
        print("NOTE: nothing was recorded, so TPM was never checked. Not reporting a ceiling.")
    if halted:
        print("HALTED -- resume only on explicit reviewer approval.")
        return 2
    print("all arms complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
