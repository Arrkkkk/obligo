"""Records gold cassettes for the 11 registry-backed batch 5-6 segments.

APPROVED SCOPE (reviewer, 2026-10-09): pass cap 80; sub-caps 38 / 38 / 12;
three sessions in that order; `E02-006` recorded at **v0.64**, so `E02-02`
fails F16's per-item check BY DESIGN and is NOT restamped.

Design notes that matter:

* **PER-SEGMENT STAMPING IS REACHED BY THREE SESSIONS, NOT BY A PARAMETER.**
  `RecordingSession.guideline_version` is a SESSION field and `record_all()`
  takes only `(segment_id, segment_text)` pairs -- verified by reading
  `record.py`, against an instruction that expected a per-segment parameter
  "from C04-117's precedent". That precedent was one session at one version,
  which is a different thing. No code change is needed; the three sessions'
  segment sets are DISJOINT (asserted below), which is the only reason one
  shared gold root is safe.
* **PROMPT `v3` IS THE ACTIVE DEFAULT, SO NOTHING IS INJECTED.** Unlike the
  `v4` probe, this run needs no loader patch; `registry.yaml` is read as
  committed and stays byte-unchanged.
* **THE LIVE ROOT IS THE REAL GOLD ROOT**, so the probe's dry-run hazard is
  strictly worse here: a leaked mock cassette would both corrupt the gold set
  and make every live run report `SKIPPED` while recording nothing. The
  structural mock guard below therefore runs over the GOLD root before any
  live session, keyed on `responses[0].json.id == "dry"` rather than on any
  content marker (the probe's first guard was blind to the artifacts it was
  written for).
* **THE PASS CAP IS ENFORCED ACROSS INVOCATIONS, because `Budget` cannot be.**
  The three sub-caps sum to 88 against a pass cap of 80, and each session is a
  separate process with its own `Budget`. Cumulative spend is persisted to
  `_spend.json` and each session's effective cap is
  `min(sub_cap, 80 - spent_so_far)`, so 80 is a true ceiling on total calls.
  The catalogue check is `GET /v1/models` and costs no tokens, so expected
  total is 69 -- plus the 1 call already burnt by the withdrawn TPM probe
  (see `catalogue_check`), seeded into `_spend.json` as `probe_waste`.
"""
from __future__ import annotations

import argparse
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
RUNS = 3
PASS_CAP = 80
EXPECTED_TPM = 8_000
SPEND_FILE = HERE / "_spend.json"

# (guideline_version, sub_cap, [(segment_id, doc_id), ...]) -- reviewer's order.
# Segments the provider reproducibly refuses. REVIEWER RULING 2026-10-09:
# `C04-144` STAYS AT 1/3 and **run 3 is not attempted**. It is pre-declared here
# rather than left to fail a third time, because a third identical request is
# the loop the ruling forbids -- and it is already evidenced twice:
# HTTP 400 `json_validate_failed` with an EMPTY `failed_generation` on run 2,
# reproduced across two separate sessions on a byte-identical request.
# Mechanism, from its own successful run-1 cassette: completion_tokens 3072
# (the provider default -- `groq.complete()` sends no max_tokens), of which
# reasoning_tokens 2749 = 89.5%, leaving 323 for content. A 10.5% margin that
# run 2's reasoning trace consumed entirely.
KNOWN_FATAL = {
    "C04-144": (
        "runs 2-3 unobtainable -- openai/gpt-oss-120b returns HTTP 400 "
        "json_validate_failed with an empty failed_generation; reproduced on run 2 in "
        "two separate sessions. Run 1 cleared the 3072-token completion default with "
        "only 323 content tokens (reasoning 2749 = 89.5%). No request parameter was "
        "changed to obtain the missing runs (§6.1)"
    ),
}
# Halt the session once this many distinct segments have failed fatally
# (reviewer ruling: "halt only if three segments fail").
MAX_FATAL_SEGMENTS = 3

SESSIONS = [
    ("v0.68", 38, [("C03-125", "C03"), ("C04-017", "C04"), ("C04-045", "C04"),
                   ("C14-095", "C14"), ("C17-006", "C17")]),
    ("v0.65", 38, [("C04-033", "C04"), ("C04-144", "C04"), ("C04-174", "C04"),
                   ("E01-004", "E01"), ("E03-022", "E03")]),
    ("v0.64", 12, [("E02-006", "E02")]),
]


def _assert_disjoint() -> None:
    seen: dict[str, str] = {}
    for ver, _, segs in SESSIONS:
        for seg, _doc in segs:
            assert seg not in seen, (
                f"SEGMENT IN TWO SESSIONS: {seg} at {seen[seg]} and {ver}. One gold "
                "root holds one cassette per (segment, run), so two sessions would "
                "overwrite or skip each other's stamp."
            )
            seen[seg] = ver
    print(f"disjointness gate: {len(seen)} segments across {len(SESSIONS)} sessions  PASS")


def pool_segments() -> dict[str, str]:
    import importlib.util
    spec = importlib.util.spec_from_file_location("corpus", ROOT / "apps/brain/evals/corpus.py")
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = c.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)}"
    return {s["segment_id"]: s["text"] for s in pool}


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


def _is_mock(path: pathlib.Path) -> bool:
    try:
        d = json.loads(path.read_text())
        return d["responses"][0]["json"].get("id") == "dry"
    except Exception:
        return False


def guard_gold_root_clean() -> None:
    """A mock cassette in the GOLD root is worse than in a probe root: it both
    corrupts the gold set and makes live runs report SKIPPED while recording
    nothing. Structural key, not a content marker."""
    stray = [p for p in cassette_mod.CASSETTE_DIR.glob("*/run*.json") if _is_mock(p)]
    if stray:
        raise SystemExit(
            f"REFUSING TO START: {len(stray)} dry-run cassette(s) in the GOLD root would be "
            f"SKIPPED as already-good: {[str(p) for p in stray[:3]]}. Delete them first."
        )
    print(f"gold-root mock guard: {cassette_mod.CASSETTE_DIR.name}/ clean  PASS")


def catalogue_check() -> list[str]:
    """MANDATORY pre-spend check, through the project's own httpx path.

    A `urllib` 403 `error code: 1010` is CLOUDFLARE's block on the client
    fingerprint, not a Groq error (Groq returns JSON) -- read as "the key is
    revoked" it would halt the session wrongly. `GET /v1/models` costs no
    tokens.

    TPM IS **NOT** PROBED WITH A SYNTHETIC COMPLETION, AND THE FIRST VERSION OF
    THIS FUNCTION THAT DID COST ONE LIVE CALL FOR NOTHING. `groq.complete()`
    hardcodes `response_format: {"type": "json_object"}`, so a `system="ping",
    user="ping"` probe gives the model no instruction to emit JSON, it answers
    in prose, and Groq's SERVER-SIDE validation rejects the completion with a
    400 `json_validate_failed` -- the exact failure mode already on record for
    `C17-021`, reached by a malformed probe rather than by a hard construct.
    Tokens are consumed before that validation runs, so the call is not free.

    TPM is instead read from `x-ratelimit-limit-tokens` on the FIRST REAL
    recording call, which `TokenWindow.observe_ceiling()` already does for
    every call (`record.py`'s `chat_model`), and asserted immediately after the
    first run by `assert_tpm_or_halt()`. Zero extra calls, same header, same
    mechanism that caught 8,000-not-12,000 at stage 4.
    """
    from obligo_brain.models.providers import groq as groq_provider
    models = groq_provider.list_models()
    print(f"    catalogue: {len(models)} models; {MODEL_ID} "
          f"{'PRESENT' if MODEL_ID in models else '*** ABSENT ***'}")
    if MODEL_ID not in models:
        raise SystemExit(f"HALT: {MODEL_ID} is not in the catalogue. Zero recording calls made.")
    return models


def assert_tpm_or_halt(window) -> None:
    """Halt unless an x-ratelimit-limit-tokens header was ACTUALLY OBSERVED and
    equals the 8,000 the approved pacing and duration arithmetic assume.

    REVIEWER RULING 2026-10-09: fail loudly if no header was observed, and NEVER
    print the bootstrap value as if it were measured.

    `TokenWindow.ceiling` is pre-seeded to `BOOTSTRAP_TPM` (12,000) and
    `observe_ceiling()` is reached only after `groq.complete()` RETURNS -- so a
    session whose calls all raise leaves `ceiling` at the bootstrap while
    `summary()` prints `ceiling_observed=12000`, which READS AS A MEASUREMENT
    AND IS A GUESS. That is exactly what happened on session 2's resume: the
    catalogue gate passed, no run was recorded, and the session looked fully
    gated when half of it had not run. `ceiling_observations` is the only
    honest discriminator -- an empty list means no header was ever seen.
    """
    seen = list(window.ceiling_observations)
    if not seen:
        raise SystemExit(
            "HALT: no x-ratelimit-limit-tokens header was observed on any call, so TPM "
            f"is UNMEASURED. window.ceiling is {window.ceiling} but that is BOOTSTRAP_TPM, "
            "a pre-read guess, and must not be reported as measured. Cassettes already "
            "written are complete and verify."
        )
    observed = seen[-1]
    print(f"    TPM MEASURED from headers: x-ratelimit-limit-tokens={observed} "
          f"({len(seen)} observation(s))")
    if int(observed) != EXPECTED_TPM:
        raise SystemExit(
            f"HALT AND REPORT, per the approval: measured TPM {observed} != {EXPECTED_TPM}. "
            "The pacing and duration arithmetic were approved against 8,000. Cassettes "
            "already written are complete and verify; resume only on reviewer approval."
        )


def load_spend() -> int:
    if SPEND_FILE.exists():
        return int(json.loads(SPEND_FILE.read_text())["pass_calls_used"])
    return 0


def prior_spend_this_session(n: int) -> int:
    """Calls already charged to THIS session by an earlier, crashed attempt.

    REVIEWER RULING 2026-10-09: a resumed session's sub-cap is NOT refreshed --
    the 11 calls session 2 spent before its 400 count against its 38, leaving
    27. Without this, `min(sub_cap, PASS_CAP - spent)` would have granted a
    full fresh 38 on resume, so the sub-cap would have been per-ATTEMPT rather
    than per-SESSION and the three sub-caps would no longer bound the pass the
    way they were approved to.
    """
    if not SPEND_FILE.exists():
        return 0
    sessions = json.loads(SPEND_FILE.read_text())["sessions"]
    return sum(int(v.get("recording_calls", 0))
               for k, v in sessions.items() if k.startswith(f"session{n}"))


def save_spend(total: int, detail: dict) -> None:
    """MERGES detail into the existing ledger rather than replacing it.

    The first version passed only the current session's dict and wrote it as
    the whole `sessions` value, so each session ERASED the previous sessions'
    provenance -- including the `probe_waste` note explaining why the pass
    started at 1 rather than 0. The TOTAL stayed correct, which is exactly why
    it would have gone unnoticed: a ledger whose arithmetic is right and whose
    history is gone still reconciles.
    """
    prior = json.loads(SPEND_FILE.read_text())["sessions"] if SPEND_FILE.exists() else {}
    prior.update(detail)
    SPEND_FILE.write_text(json.dumps({"pass_calls_used": total, "sessions": prior}, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise the whole path with a MockTransport, zero live calls")
    args = ap.parse_args()

    ver, sub_cap, segs = SESSIONS[args.session - 1]
    _assert_disjoint()

    segments = pool_segments()
    for seg, _ in segs:
        assert seg in segments, f"{seg} not in the pool"
    print(f"pool gate: 1547 segments; session-{args.session} segments present  PASS")

    active = prompt_registry.load("extraction")
    assert active.version == "v3", f"expected the committed default v3, got {active.version}"
    print(f"prompt: extraction {active.version} (committed default, NOT injected)")

    if not args.dry_run:
        guard_gold_root_clean()

    spent = 0 if args.dry_run else load_spend()
    prior = 0 if args.dry_run else prior_spend_this_session(args.session)
    remaining_sub = sub_cap - prior
    effective = min(remaining_sub, PASS_CAP - spent)
    print(f"\nsession {args.session}: guideline {ver}, {len(segs)} segments x {RUNS} runs")
    print(f"budget: sub-cap {sub_cap} - {prior} already charged to this session "
          f"= {remaining_sub}; pass cap {PASS_CAP} - {spent} spent = {PASS_CAP - spent}"
          f"  -> EFFECTIVE CAP {effective}"
          f"{'  [DRY RUN -- no live calls]' if args.dry_run else '  [LIVE]'}")
    if effective <= 0:
        raise SystemExit("HALT: pass cap reached. Resume only on explicit reviewer approval.")

    if not args.dry_run:
        catalogue_check()                # GET /v1/models -- no tokens, not charged

    budget = record.Budget(max_calls=effective)
    window = ratelimit.TokenWindow()
    transport_factory = (mock_transport_factory if args.dry_run
                         else (lambda: httpx.HTTPTransport()))
    root = (HERE / "_dryrun" / ver) if args.dry_run else None   # None = the real gold root

    per_doc: dict[str, list[tuple[str, str]]] = {}
    for seg, doc in segs:
        per_doc.setdefault(doc, []).append((seg, segments[seg]))

    # A fatal HTTP error is caught IN THE LOOP (below) rather than allowed to
    # propagate, so `save_spend` always runs. The first version let it escape
    # main() and the ledger silently understated real spend by 11 calls.
    halted = None
    with fixtures.document_fixtures(per_doc) as fx:
        def invoke(segment_id: str, chat_model):
            from obligo_brain.graphs.pipeline import run_pipeline
            from obligo_brain.platform.tenancy.context import TenantContext
            doc = next(d for s, d in segs if s == segment_id)
            uuid = fx[doc].segment_uuids[segment_id]
            org = fx[doc].org_id
            TenantContext.set(UUID(str(org)))
            try:
                return run_pipeline(str(uuid), str(org), chat_model=chat_model)
            finally:
                TenantContext.clear()

        session = record.RecordingSession(
            budget=budget, window=window, invoke=invoke,
            transport_factory=transport_factory, model_id=MODEL_ID,
            prompt_version="v3", guideline_version=ver, root=root,
        )
        # Seeded in a DRY RUN TOO: a dry run that skips a different set of
        # segments from the live run is not a model of it.
        dead: dict[str, str] = {s_: why for s_, why in KNOWN_FATAL.items()
                                if s_ in [x for x, _ in segs]}
        for s_, why in dead.items():
            print(f"  {s_}: PRE-DECLARED FATAL, no run attempted -- {why[:90]}...")
        # Deliberately False in a dry run too: the mock transport returns
        # x-ratelimit-limit-tokens=8000, so the dry run EXERCISES this gate
        # rather than skipping the branch it exists to de-risk.
        checked_tpm = False
        for run in range(1, RUNS + 1):
            for seg, _doc in segs:
                if seg in dead:
                    continue
                try:
                    out = session.record_run(seg, segments[seg], run)
                except record.BudgetExhausted as exc:
                    print(f"  *** HARD HALT: {exc}")
                    halted = str(exc)
                    break
                except httpx.HTTPStatusError as exc:   # ISOLATED, not fatal to the session
                    # A non-429 is FATAL BY DESIGN in the recorder (a 400 is not a
                    # pacing problem), and an earlier version let it propagate out
                    # of main() -- which SKIPPED save_spend entirely and left the
                    # ledger understating real spend by every call the session had
                    # made. The body is printed because the status alone does not
                    # name the cause: Groq returns `json_validate_failed` with an
                    # EMPTY `failed_generation` when reasoning tokens exhaust the
                    # completion budget (the C17-021 class), and that is
                    # indistinguishable from any other 400 at the status line.
                    body = ""
                    try:
                        body = exc.response.text[:800]
                    except Exception:
                        pass
                    print(f"  *** FATAL {exc.response.status_code} on {seg} run{run}: {body}")
                    # REVIEWER RULING: isolate the segment, do not stop the session.
                    # An earlier version `break`ed here, so ONE deterministically
                    # failing segment blocked EIGHT invocations that had nothing to
                    # do with it (the loop is run-major).
                    dead[seg] = f"HTTP {exc.response.status_code} run{run}: {body[:200]}"
                    print(f"      -> {seg} ISOLATED; remaining runs will not be attempted. "
                          f"{len(dead)}/{MAX_FATAL_SEGMENTS} fatal segment(s)")
                    if len(dead) >= MAX_FATAL_SEGMENTS:
                        halted = (f"{len(dead)} segments failed fatally "
                                  f"({sorted(dead)}) -- reviewer halt threshold")
                        print(f"  *** HARD HALT: {halted}")
                        break
                    continue
                print(f"  {seg} run{run}: {out.status} calls={out.calls} "
                      f"attempts={out.attempts} {out.detail}")
                if not checked_tpm and out.status == "RECORDED":
                    assert_tpm_or_halt(window)   # halts after ONE invocation, not zero
                    checked_tpm = True
            if halted:
                break

    print(f"\n=== {session.summary()} ===")
    # `summary()` prints window.ceiling, which is BOOTSTRAP until a header is
    # seen. Say plainly which it is rather than letting the number speak.
    if window.ceiling_observations:
        print(f"    (ceiling MEASURED from {len(window.ceiling_observations)} header "
              f"observation(s): {window.ceiling_observations[-1]})")
    else:
        print(f"    (ceiling above is BOOTSTRAP_TPM, NOT measured -- no "
              f"x-ratelimit-limit-tokens header was observed this session)")
        if budget.used > 0:
            raise SystemExit(
                "HALT: calls were made but no rate-limit header was ever observed. "
                "TPM is unmeasured for this session and must not be reported as 8,000."
            )
    if dead:
        print(f"    ISOLATED segments ({len(dead)}): "
              + "; ".join(f"{k} -- {v[:70]}" for k, v in sorted(dead.items())))
    if not args.dry_run:
        total = spent + budget.used
        # ONE KEY PER ATTEMPT. The first fix made `save_spend` merge instead of
        # replace, which stopped sessions erasing each OTHER -- but both resumes
        # of session 2 wrote the same "session2-RESUME" key, so the second
        # overwrote the first and the breakdown lost 1 call while the TOTAL
        # stayed right. Same defect class as the original, one level down: a
        # ledger that reconciles in aggregate and has lost a row. It also
        # UNDERSTATES per-session spend, which is what the sub-cap is computed
        # from, so it would have granted one more call than the sub-cap allows.
        attempt = 1 + sum(1 for k in (json.loads(SPEND_FILE.read_text())["sessions"]
                                      if SPEND_FILE.exists() else {})
                          if k.startswith(f"session{args.session}-attempt"))
        key = f"session{args.session}-attempt{attempt}"
        save_spend(total, {key: {
            "guideline_version": ver, "recording_calls": budget.used,
            # GET /v1/models costs no tokens and is NOT charged. An earlier
            # version recorded `catalogue_calls: 1` here, which wrongly implied
            # it was -- the pass's non-recording `+1` is the withdrawn TPM
            # probe (see `pre-session`), not the catalogue check.
            "catalogue_calls_charged": 0,
            "invocations": len([o for o in session.outcomes if o.status == "RECORDED"]),
            "halted": halted}})
        print(f"pass spend: {total}/{PASS_CAP} calls")
    if halted:
        print("HALTED -- resume only on explicit reviewer approval.")
        return 2
    print("session complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
