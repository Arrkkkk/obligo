"""Tests for the parse-error repair loop (graphs/repair.py).

Layer 1 in blueprint §19.2's sense: no database, no network. The whole
bounded loop -- including every branch and both terminal causes -- runs
against a fake ChatModel, which is possible because repair_candidates()
deliberately does no I/O of its own (run_repair() is the thin DB wrapper).

The properties that actually matter here, and why:

 1. TERMINATION. The loop must never exceed max_repairs model calls, for
    any model behaviour at all -- including a model that keeps returning
    changed-but-still-broken values forever. Proven by a hypothesis
    property, not just by example.
 2. TOTALITY. Every input CompileFailure ends up in exactly one of
    `compiled` or `quarantined`. Nothing is silently dropped, the same
    partition guarantee ground_candidates() and compile_candidates()
    already provide.
 3. NON-FABRICATION. A repair structurally cannot change a span-grounded
    quoted field. This is the one that would be a real correctness bug if
    it regressed, so it is tested adversarially: the fake model tries to
    rewrite span_text, the aliases, object_raw_text, condition_raws and
    confidence, and every one of them must come back unchanged.
"""

from __future__ import annotations

import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_compile import (
    CompileFailure,
    CompileFailureReason,
    compile_candidate,
)
from obligo_brain.graphs import repair as repair_module
from obligo_brain.graphs.repair import (
    MAX_REPAIRS,
    QuarantineCause,
    derive_hints,
    repair_candidates,
    repair_input_hash,
)
from obligo_brain.graphs.state import GroundedCandidate, GroundingTier, LLMCandidate, SegmentRecord
from obligo_brain.models.providers.base import ChatCompletion
from obligo_brain.prompts import registry as prompt_registry

_SEGMENT_ID = "00000000-0000-0000-0000-000000000001"
_SPAN = (
    "If the Customer so requests, Vendor shall register the Deliverables "
    "with the Customer by 2027-01-01."
)
# A genuinely UNMAPPABLE temporal phrase that DOES contain a shorter,
# verbatim, mappable substring -- the over-capture case that is the only
# repairable shape of UNMAPPABLE_TEMPORAL. _EVERY_RE is anchored at the end
# of the string, so the trailing "during the Term" defeats it; "every 30
# days" on its own matches. Picked by checking against the real classifier,
# not assumed: the more obvious-looking "within 30 days of X, as extended"
# actually compiles fine, because WITHIN's trigger capture is `.+`.
_TEMPORAL_SPAN = "Vendor shall report to the Customer every 30 days during the Term."
_OVER_CAPTURED = "every 30 days during the Term"
_SEGMENT = SegmentRecord(
    id=_SEGMENT_ID, text=f"1.1 {_SPAN} 1.2 {_TEMPORAL_SPAN} 1.3 Something else entirely."
)


@pytest.fixture(scope="module")
def repair_prompt():
    return prompt_registry.load("repair")


def _active_repair_version() -> str:
    """The repair version registry.yaml currently points at."""
    import yaml
    from pathlib import Path as _P
    from obligo_brain.prompts import registry as _r
    return yaml.safe_load(
        (_P(_r.__file__).parent / "registry.yaml").read_text()
    )["repair"]["environments"]["default"]


def _candidate(
    *,
    span_text: str = _SPAN,
    modality: str = "MUST",
    obligor_alias: str = "Vendor",
    obligee_alias: str = "Customer",
    action: str = "NOTIFY",
    object_class: str = "deliverables",
    object_raw_text: str = "the Deliverables",
    temporal_raw: str | None = None,
    condition_raws: list[str] | None = None,
    confidence: float = 0.9,
) -> GroundedCandidate:
    start = _SEGMENT.text.index(span_text)
    return GroundedCandidate(
        llm_candidate=LLMCandidate(
            span_text=span_text,
            modality=modality,
            obligor_alias=obligor_alias,
            obligee_alias=obligee_alias,
            action=action,
            object_class=object_class,
            object_raw_text=object_raw_text,
            temporal_raw=temporal_raw,
            condition_raws=condition_raws or [],
            confidence=confidence,
        ),
        source=ast.SourceRef(
            segment_id=_SEGMENT_ID, char_start=start, char_end=start + len(span_text)
        ),
        grounding_tier=GroundingTier.EXACT,
    )


def _temporal_candidate(temporal_raw: str = _OVER_CAPTURED) -> GroundedCandidate:
    return _candidate(
        span_text=_TEMPORAL_SPAN,
        action="REPORT",
        object_class="status",
        object_raw_text="the Customer",
        temporal_raw=temporal_raw,
    )


def _failing_temporal(temporal_raw: str = _OVER_CAPTURED) -> CompileFailure:
    result = compile_candidate(_temporal_candidate(temporal_raw))
    assert isinstance(result, CompileFailure)
    assert result.reason is CompileFailureReason.UNMAPPABLE_TEMPORAL
    return result


def _failing(**kwargs) -> CompileFailure:
    """Build a candidate that GENUINELY fails to compile, by running the
    real compiler over it -- never a hand-written CompileFailure. If a value
    that is supposed to be broken stops being broken (say the taxonomy
    grows a verb), this assertion fails loudly instead of the test quietly
    exercising a path that no longer exists.
    """
    candidate = _candidate(**kwargs)
    result = compile_candidate(candidate)
    assert isinstance(result, CompileFailure), f"expected a compile failure, got {result!r}"
    return result


class _FakeModel:
    """A ChatModel whose responses are scripted per call. Records every
    (system, user) pair so tests can assert what was actually sent.
    """

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, *, system: str, user: str, model_id: str, temperature: float = 0.0):
        self.calls.append((system, user))
        content = self._responses.pop(0) if self._responses else '{"repairs": []}'
        return ChatCompletion(
            content=content,
            model_id=model_id,
            input_tokens=100,
            output_tokens=20,
            latency_ms=12.5,
        )


def _run(failures, responses, prompt, **kwargs):
    model = _FakeModel(responses)
    result = repair_candidates(
        _SEGMENT,
        failures,
        chat_model=model,
        prompt=prompt,
        model_id="fake-model",
        **kwargs,
    )
    return result, model


# --- hint derivation ----------------------------------------------------


def test_unknown_action_yields_an_action_hint_carrying_the_closed_taxonomy():
    # REGISTER is one of the verbs the taxonomy checkpoint deliberately
    # excluded (present in the corpus only as a noun), so this is a real
    # out-of-taxonomy value, not an invented one.
    (hint,) = derive_hints(_failing(action="REGISTER"))

    assert hint.field == "action"
    assert hint.bad_value == "REGISTER"
    assert hint.legal_values == ast.ACTIONS


def test_unknown_modality_yields_a_modality_hint():
    (hint,) = derive_hints(_failing(modality="SHALL"))

    assert hint.field == "modality"
    assert hint.legal_values == ast.MODALITIES


def test_object_class_with_a_digit_yields_an_object_class_hint():
    (hint,) = derive_hints(_failing(object_class="section 4 1"))

    assert hint.field == "object_class"
    assert hint.legal_values == ()


def test_several_broken_fields_yield_several_hints():
    hints = derive_hints(_failing(modality="SHALL", action="REGISTER", object_class="Bad Class 9"))

    assert {h.field for h in hints} == {"modality", "action", "object_class"}


def test_modality_spelled_with_a_space_is_not_reported_as_broken():
    """obligation.lark:45 is MUST_NOT: "MUST NOT" | "MUST_NOT", so
    "MUST NOT" compiles fine even though ast.MODALITIES lists only the
    underscore spelling. If the space form were flagged, the hint would
    point at a field that is actually correct and the real cause would go
    unhinted.
    """
    candidate = _candidate(modality="must not")
    assert isinstance(compile_candidate(candidate), ast.Obligation)

    # ...and when something else is broken on the same candidate, modality
    # must not appear among the hints.
    hints = derive_hints(_failing(modality="must not", action="REGISTER"))
    assert {h.field for h in hints} == {"action"}


def test_unmappable_temporal_yields_a_narrow_your_quote_hint():
    (hint,) = derive_hints(_failing_temporal())
    assert hint.field == "temporal_raw"
    assert "substring" in hint.problem


# --- the no-actionable-hint path: zero model calls ----------------------


def test_unexplainable_parse_error_quarantines_immediately_with_no_model_call(repair_prompt):
    """A PARSE_ERROR none of the three field checks explains must not cost a
    model call. Constructed by hand here precisely because the compiler
    cannot currently produce one -- that is the point: this is the fallback
    for a future failure mode nobody has enumerated yet.
    """
    failure = CompileFailure(
        reason=CompileFailureReason.PARSE_ERROR,
        detail="some future grammar rejection with no field-level explanation",
        candidate=_candidate(),
    )

    result, model = _run([failure], [], repair_prompt)

    assert model.calls == []
    assert result.compiled == []
    assert result.calls == []
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.NO_ACTIONABLE_HINT
    assert item.attempts == 1
    assert item.repair_calls == ()


# --- the happy path -----------------------------------------------------


def test_one_repair_fixes_an_out_of_taxonomy_action(repair_prompt):
    failure = _failing(action="REGISTER")

    result, model = _run(
        [failure], [json.dumps({"repairs": [{"index": 0, "action": "REPORT"}]})], repair_prompt
    )

    assert len(model.calls) == 1
    assert result.quarantined == []
    (obligation,) = result.compiled
    assert obligation.action == "REPORT"
    # The grounded span survived the round trip untouched.
    assert obligation.source.char_start == failure.candidate.source.char_start
    assert obligation.source.char_end == failure.candidate.source.char_end


def test_second_attempt_repairs_what_the_first_left_broken(repair_prompt):
    failure = _failing(modality="SHALL", action="REGISTER")

    result, model = _run(
        [failure],
        [
            json.dumps({"repairs": [{"index": 0, "modality": "MUST"}]}),
            json.dumps({"repairs": [{"index": 0, "action": "REPORT"}]}),
        ],
        repair_prompt,
    )

    assert len(model.calls) == 2
    (obligation,) = result.compiled
    assert obligation.modality == "MUST"
    assert obligation.action == "REPORT"
    assert result.quarantined == []


def test_narrowing_an_over_captured_temporal_quote_repairs_it(repair_prompt):
    """The one genuinely repairable UNMAPPABLE_TEMPORAL case: the model
    over-captured, and a shorter VERBATIM substring of the same span is a
    clean timing phrase on its own.
    """
    result, _ = _run(
        [_failing_temporal()],
        [json.dumps({"repairs": [{"index": 0, "temporal_raw": "every 30 days"}]})],
        repair_prompt,
    )

    (obligation,) = result.compiled
    assert isinstance(obligation.temporal, ast.EveryTemporal)
    assert obligation.temporal.duration == ast.Duration(amount=30.0, unit="d")


# --- non-fabrication: the guarantee that would be a real bug if it broke -


def test_a_repair_cannot_rewrite_any_span_grounded_field(repair_prompt):
    """Adversarial: the model returns wholesale rewrites of every quoted
    field alongside the one legitimate correction. All of them must be
    inert -- not because the prompt asked, but because _apply_repair copies
    the original and overrides only hinted, whitelisted fields.
    """
    original = _candidate(action="REGISTER", condition_raws=["the Customer so requests"])
    failure = compile_candidate(original)
    assert isinstance(failure, CompileFailure)

    result, _ = _run(
        [failure],
        [
            json.dumps(
                {
                    "repairs": [
                        {
                            "index": 0,
                            "action": "REPORT",
                            "span_text": "Vendor shall NOT do anything at all.",
                            "obligor_alias": "Some Other Party",
                            "obligee_alias": "Nobody",
                            "object_raw_text": "an entirely invented object",
                            "condition_raws": ["a condition that appears nowhere"],
                            "confidence": 1.0,
                        }
                    ]
                }
            )
        ],
        repair_prompt,
    )

    (obligation,) = result.compiled
    o = original.llm_candidate
    assert obligation.action == "REPORT"  # the one legitimate change landed
    assert obligation.obligor == ast.UnresolvedParty(alias=o.obligor_alias)
    assert obligation.obligee == ast.UnresolvedParty(alias=o.obligee_alias)
    assert obligation.object.raw_text == o.object_raw_text
    assert [c.predicate.raw for c in obligation.conditions] == o.condition_raws
    assert obligation.confidence == o.confidence


def test_a_repair_that_rewrites_temporal_raw_instead_of_narrowing_it_is_rejected(repair_prompt):
    """temporal_raw is the one repairable field that is ALSO span-grounded,
    so it is the only place a repair could smuggle in a paraphrase. The
    grounding gate -- re-run in full, not partially re-implemented -- must
    catch it, and the candidate must be quarantined rather than compiled
    from text that is not in the document.
    """
    result, _ = _run(
        [_failing_temporal()],
        # A perfectly well-formed EVERY phrase that appears nowhere in the
        # segment -- exactly the plausible-looking rewrite the rule exists
        # to stop.
        [json.dumps({"repairs": [{"index": 0, "temporal_raw": "every 30d"}]})],
        repair_prompt,
    )

    assert result.compiled == []
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_BROKE_GROUNDING
    assert item.failure_reason == "NESTED_FIELD_NOT_IN_SPAN"


def test_a_null_temporal_raw_is_never_accepted(repair_prompt):
    """Nulling temporal_raw would "fix" the compile by silently turning a
    timed obligation into an untimed, weaker one -- the exact drop
    ir_compile.py refuses to make. It must read as no usable change.
    """
    result, model = _run(
        [_failing_temporal()],
        [json.dumps({"repairs": [{"index": 0, "temporal_raw": None}]})],
        repair_prompt,
    )

    assert result.compiled == []
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_MADE_NO_PROGRESS
    assert len(model.calls) == 1


def test_an_unhinted_field_is_not_taken_even_when_the_model_volunteers_it(repair_prompt):
    """Only fields the compiler objected to are repairable. A model
    volunteering a change to a field that was already right is a chance to
    degrade a correct answer, not to fix a wrong one.
    """
    failure = _failing(action="REGISTER")

    result, _ = _run(
        [failure],
        [json.dumps({"repairs": [{"index": 0, "action": "REPORT", "modality": "MAY"}]})],
        repair_prompt,
    )

    (obligation,) = result.compiled
    assert obligation.modality == "MUST"  # unchanged, not the volunteered MAY


# --- budget, batching and termination -----------------------------------


def test_budget_exhausts_after_exactly_max_repairs_calls(repair_prompt):
    failure = _failing(action="REGISTER")

    # Each response changes the action to a *different* still-invalid verb,
    # so progress is made every time and the loop never short-circuits.
    result, model = _run(
        [failure],
        [
            json.dumps({"repairs": [{"index": 0, "action": "AUDIT"}]}),
            json.dumps({"repairs": [{"index": 0, "action": "CERTIFY"}]}),
            json.dumps({"repairs": [{"index": 0, "action": "SUBMIT"}]}),
        ],
        repair_prompt,
    )

    assert len(model.calls) == MAX_REPAIRS == 2
    assert result.compiled == []
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_BUDGET_EXHAUSTED
    assert item.attempts == 1 + MAX_REPAIRS  # §3.9's "fail 3x"
    assert item.repair_calls == (1, 2)


def test_an_attempt_that_changes_nothing_stops_the_loop_early(repair_prompt):
    """At temperature 0 with an identical pending set, the next payload
    differs only by its nonce, so the response is deterministic. Paying for
    it would be pure waste.
    """
    failure = _failing(action="REGISTER")

    result, model = _run([failure], ['{"repairs": []}', '{"repairs": []}'], repair_prompt)

    assert len(model.calls) == 1
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_MADE_NO_PROGRESS
    assert item.attempts == 1  # no new COMPILE attempt happened
    assert item.repair_calls == (1,)  # but a call was still paid for


def test_all_failing_candidates_from_one_segment_share_one_call(repair_prompt):
    """Batching by segment, not by candidate -- what bounds repair calls at
    2 per segment regardless of how many candidates failed.
    """
    failures = [
        _failing(action="REGISTER"),
        _failing(modality="SHALL"),
        _failing(object_class="Bad Class 9"),
    ]

    result, model = _run(
        [*failures],
        [
            json.dumps(
                {
                    "repairs": [
                        {"index": 0, "action": "REPORT"},
                        {"index": 1, "modality": "MUST"},
                        {"index": 2, "object_class": "bad_class"},
                    ]
                }
            )
        ],
        repair_prompt,
    )

    assert len(model.calls) == 1
    assert len(result.compiled) == 3
    assert result.quarantined == []


def test_a_partially_successful_batch_retries_only_the_stragglers(repair_prompt):
    failures = [_failing(action="REGISTER"), _failing(modality="SHALL")]

    result, model = _run(
        [*failures],
        [
            json.dumps({"repairs": [{"index": 0, "action": "REPORT"}]}),
            json.dumps({"repairs": [{"index": 1, "modality": "MUST"}]}),
        ],
        repair_prompt,
    )

    assert len(result.compiled) == 2
    assert result.quarantined == []
    _, second_user = model.calls[1]
    payload = second_user[second_user.index("<<<FAILURES_") :]
    assert '"index": 1' in payload
    assert '"index": 0' not in payload


def test_a_malformed_repair_response_degrades_to_no_repair_not_an_exception(repair_prompt):
    failure = _failing(action="REGISTER")

    result, _ = _run([failure], ["not json at all", '{"wrong": "shape"}'], repair_prompt)

    assert result.compiled == []
    assert len(result.quarantined) == 1
    assert result.calls[0].node_trace["ignored"]


def test_duplicate_indexes_are_dropped_rather_than_arbitrarily_chosen_between(repair_prompt):
    """Two corrections for one candidate is the model contradicting itself.
    Same precedent as symbols.resolve_party() and the grounder's ambiguous
    match: refuse, never guess.
    """
    failure = _failing(action="REGISTER")

    result, _ = _run(
        [failure],
        [
            json.dumps(
                {"repairs": [{"index": 0, "action": "REPORT"}, {"index": 0, "action": "DELIVER"}]}
            )
        ],
        repair_prompt,
    )

    assert result.compiled == []
    assert len(result.quarantined) == 1


def test_empty_failure_list_is_a_no_op(repair_prompt):
    result, model = _run([], [], repair_prompt)

    assert model.calls == []
    assert result == repair_module.RepairLoopResult()


# --- accounting ---------------------------------------------------------


def test_one_call_record_per_llm_call_carrying_the_prompt_identity(repair_prompt):
    failures = [_failing(action="REGISTER")]

    result, _ = _run(
        [*failures],
        [
            json.dumps({"repairs": [{"index": 0, "action": "AUDIT"}]}),
            json.dumps({"repairs": [{"index": 0, "action": "CERTIFY"}]}),
        ],
        repair_prompt,
    )

    assert [c.attempt for c in result.calls] == [1, 2]
    for call in result.calls:
        assert call.prompt.id == "repair"
        # Active version read from registry.yaml, not hardcoded: this test cares
        # that prompt IDENTITY is recorded per call, never which version happens
        # to be active. Corrected 2026-08-23 -- a literal "v1" here broke on the
        # model-migration bump (repair v1 -> v2) exactly as a hardcode does, the
        # same defect test_registry.py carried.
        assert call.prompt.version == _active_repair_version()
        assert call.provider == "groq"
        assert len(call.input_hash) == 64


def test_repair_input_hash_distinguishes_two_candidates_in_the_same_segment():
    """The real hazard extraction.py's sha256(segment_id, prompt_hash,
    model_id) formula would create here: V17 records input_hash as the key
    for a future response cache, so two different failing candidates from
    one segment colliding would serve one candidate's repair for another's.
    """
    a = repair_input_hash(system="sys", user="candidate A payload", model_id="m")
    b = repair_input_hash(system="sys", user="candidate B payload", model_id="m")

    assert a != b


def test_node_trace_records_the_lark_diagnostic_that_is_never_sent_to_the_model(repair_prompt):
    failure = _failing(action="REGISTER")

    result, model = _run([failure], ['{"repairs": []}'], repair_prompt)

    (call,) = result.calls
    (pending,) = call.node_trace["pending"]
    assert pending["compiler_detail"] == failure.detail
    # ...and that same diagnostic never reached the prompt.
    _, user = model.calls[0]
    assert failure.detail not in user


# --- prompt-boundary properties -----------------------------------------


def test_the_segment_and_the_diagnostics_never_reach_the_system_prompt(repair_prompt):
    """Standing Principle 4, applied to the second prompt this codebase has.
    Both untrusted inputs -- the document text and the failure payload,
    which quotes document text -- must be confined to the user message.
    """
    canary_segment = "CANARY_SEGMENT_MUST_NOT_APPEAR_IN_SYSTEM"
    segment = SegmentRecord(id=_SEGMENT_ID, text=canary_segment)

    system, user = prompt_registry.render_repair(
        repair_prompt, segment_text=canary_segment, failures='{"canary": "FAILURES_CANARY"}'
    )

    assert system == repair_prompt.system
    assert canary_segment not in system
    assert "FAILURES_CANARY" not in system
    assert canary_segment in user
    assert "FAILURES_CANARY" in user
    assert segment.text == canary_segment


def test_a_brace_in_the_document_cannot_create_a_new_substitution_point(repair_prompt):
    """str.format only scans the TEMPLATE for placeholders, so braces in the
    substituted values are inert. Asserted rather than assumed, because the
    failure payload is JSON and is therefore full of braces.
    """
    hostile = "{nonce} {segment_text} {failures} {0} {}"

    _, user = prompt_registry.render_repair(
        repair_prompt, segment_text=hostile, failures="[]"
    )

    assert hostile in user


# --- properties ---------------------------------------------------------


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.sampled_from(["AUDIT", "CERTIFY", "SUBMIT", "FILE", "REGISTER", "DEFEND"]),
        min_size=0,
        max_size=8,
    )
)
def test_property_loop_never_exceeds_the_budget_for_any_model_behaviour(replies):
    """Termination, for a model that keeps changing its answer to something
    still invalid indefinitely. The bound must hold on call count, not on
    the model eventually giving up.
    """
    prompt = prompt_registry.load("repair")
    failure = _failing(action="REGISTER")
    responses = [json.dumps({"repairs": [{"index": 0, "action": a}]}) for a in replies]

    result, model = _run([failure], responses, prompt)

    assert len(model.calls) <= MAX_REPAIRS
    assert len(result.calls) == len(model.calls)


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.sampled_from(["REGISTER", "SHALL", "BAD CLASS 9", "OVERCAPTURE", "UNEXPLAINED"]),
        min_size=1,
        max_size=6,
    ),
    st.lists(st.booleans(), min_size=0, max_size=3),
)
def test_property_every_input_lands_in_exactly_one_output_bucket(kinds, will_fix):
    """Totality: nothing is ever silently dropped, whatever mix of failure
    kinds goes in and however the model responds.
    """
    prompt = prompt_registry.load("repair")

    failures = []
    for kind in kinds:
        if kind == "REGISTER":
            failures.append(_failing(action="REGISTER"))
        elif kind == "SHALL":
            failures.append(_failing(modality="SHALL"))
        elif kind == "BAD CLASS 9":
            failures.append(_failing(object_class="Bad Class 9"))
        elif kind == "OVERCAPTURE":
            failures.append(_failing_temporal())
        else:
            failures.append(
                CompileFailure(
                    reason=CompileFailureReason.PARSE_ERROR,
                    detail="unexplainable",
                    candidate=_candidate(),
                )
            )

    responses = []
    for fix in will_fix:
        responses.append(
            json.dumps({"repairs": [{"index": 0, "action": "REPORT"}]})
            if fix
            else '{"repairs": []}'
        )

    result, _ = _run(failures, responses, prompt)

    assert len(result.compiled) + len(result.quarantined) == len(failures)
