"""run_repair()'s persistence paths against real Neon Postgres -- agent_runs
(V17) and compile_quarantine (V18), over real RLS, no mocking.

Mirrors tests/compiler/test_symbols.py's real-Neon, skip-if-unset pattern,
with the roles inverted: there the owner seeds and obligo_brain reads; here
obligo_brain WRITES (it holds INSERT and nothing else on both tables, by
design) and the owner reads back to verify. That inversion is the point --
it proves the minimal grants V17/V18 actually chose are sufficient for the
code that has to live with them, which reading the migration file cannot.

The pure loop is covered exhaustively without a database in test_repair.py.
What can only be proven here: the SQL is well-formed against the real
schema (including the uuid[] lineage column), the NOT NULL/CHECK
constraints accept what this code writes, and RLS is genuinely load-bearing
on the write path rather than app-level filtering.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from obligo_brain.compiler.ir_compile import CompileFailure, compile_candidate
from obligo_brain.compiler import ast
from obligo_brain.graphs.repair import QuarantineCause, run_repair
from obligo_brain.graphs.state import GroundedCandidate, GroundingTier, LLMCandidate, SegmentRecord
from obligo_brain.models.providers.base import ChatCompletion
from obligo_brain.platform.tenancy.context import TenantContext

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)

_SPAN = "Vendor shall register the Deliverables with the Customer."
_SEGMENT_TEXT = f"1.1 {_SPAN}"


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


@dataclass
class SegmentFixture:
    org_a_id: uuid.UUID
    org_b_id: uuid.UUID
    segment_id: uuid.UUID


@pytest.fixture
def segment_fixture() -> Iterator[SegmentFixture]:
    owner_engine = create_engine(_owner_url())

    org_a_id, org_b_id = uuid.uuid4(), uuid.uuid4()
    user_id, source_id, segment_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    try:
        with owner_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO organizations (id, name) VALUES (:a, 'Org A'), (:b, 'Org B')"),
                {"a": org_a_id, "b": org_b_id},
            )
            conn.execute(
                text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
                {"id": user_id, "sub": f"sub-{user_id}", "email": f"{user_id}@example.test"},
            )
            conn.execute(
                text(
                    "INSERT INTO sources "
                    "(id, org_id, uploaded_by, filename, byte_size, sha256, storage_key, status) "
                    "VALUES (:id, :org_id, :user_id, 'f.pdf', 10, :sha, :key, 'UPLOADED')"
                ),
                {
                    "id": source_id,
                    "org_id": org_a_id,
                    "user_id": user_id,
                    "sha": "a" * 64,
                    "key": f"test/{source_id}",
                },
            )
            conn.execute(
                text(
                    "INSERT INTO segments "
                    "(id, org_id, source_id, text, char_start, char_end, ordinal, page) "
                    "VALUES (:id, :org_id, :source_id, :text, 0, :end, 0, 1)"
                ),
                {
                    "id": segment_id,
                    "org_id": org_a_id,
                    "source_id": source_id,
                    "text": _SEGMENT_TEXT,
                    "end": len(_SEGMENT_TEXT),
                },
            )

        yield SegmentFixture(org_a_id=org_a_id, org_b_id=org_b_id, segment_id=segment_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(
                text("DELETE FROM compile_quarantine WHERE org_id IN (:a, :b)"),
                {"a": org_a_id, "b": org_b_id},
            )
            conn.execute(
                text("DELETE FROM agent_runs WHERE org_id IN (:a, :b)"),
                {"a": org_a_id, "b": org_b_id},
            )
            conn.execute(text("DELETE FROM segments WHERE id = :id"), {"id": segment_id})
            conn.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(
                text("DELETE FROM organizations WHERE id IN (:a, :b)"),
                {"a": org_a_id, "b": org_b_id},
            )
        owner_engine.dispose()


def _failing(segment_id: uuid.UUID) -> CompileFailure:
    start = _SEGMENT_TEXT.index(_SPAN)
    candidate = GroundedCandidate(
        llm_candidate=LLMCandidate(
            span_text=_SPAN,
            modality="MUST",
            obligor_alias="Vendor",
            obligee_alias="Customer",
            action="REGISTER",  # deliberately outside the closed 34-verb taxonomy
            object_class="deliverables",
            object_raw_text="the Deliverables",
            confidence=0.9,
        ),
        source=ast.SourceRef(
            segment_id=str(segment_id), char_start=start, char_end=start + len(_SPAN)
        ),
        grounding_tier=GroundingTier.EXACT,
    )
    failure = compile_candidate(candidate)
    assert isinstance(failure, CompileFailure)
    return failure


def _model(*responses: str):
    remaining = list(responses)

    def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0):
        content = remaining.pop(0) if remaining else '{"repairs": []}'
        return ChatCompletion(
            content=content, model_id=model_id, input_tokens=7, output_tokens=3, latency_ms=9.0
        )

    return chat_model


def _segment(fixture: SegmentFixture) -> SegmentRecord:
    return SegmentRecord(id=str(fixture.segment_id), text=_SEGMENT_TEXT)


def test_each_repair_call_writes_its_own_agent_runs_row(segment_fixture):
    """One row per LLM call, never aggregated -- and node='repair', so these
    are distinguishable from the extractor's own rows in the same segment.
    """
    TenantContext.set(segment_fixture.org_a_id)
    try:
        result = run_repair(
            _segment(segment_fixture),
            str(segment_fixture.org_a_id),
            [_failing(segment_fixture.segment_id)],
            chat_model=_model(
                '{"repairs": [{"index": 0, "action": "AUDIT"}]}',
                '{"repairs": [{"index": 0, "action": "CERTIFY"}]}',
            ),
        )
    finally:
        TenantContext.clear()

    assert len(result.agent_run_ids) == 2

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            rows = conn.execute(
                text(
                    "SELECT node, provider, model_id, prompt_id, prompt_version, prompt_hash, "
                    "       input_hash, input_tokens, output_tokens, latency_ms, status "
                    "FROM agent_runs WHERE segment_id = :sid ORDER BY created_at"
                ),
                {"sid": segment_fixture.segment_id},
            ).all()
    finally:
        owner_engine.dispose()

    assert len(rows) == 2
    for row in rows:
        assert row.node == "repair"
        assert row.provider == "groq"
        assert row.prompt_id == "repair"
        assert row.prompt_version == "v1"
        assert row.status == "ok"
        assert len(row.prompt_hash) == 64
    # The real hazard extraction.py's segment_id-based formula would create:
    # two calls on ONE segment must not share a cache key.
    assert rows[0].input_hash != rows[1].input_hash


def test_an_exhausted_candidate_lands_in_compile_quarantine_with_its_lineage(segment_fixture):
    TenantContext.set(segment_fixture.org_a_id)
    try:
        result = run_repair(
            _segment(segment_fixture),
            str(segment_fixture.org_a_id),
            [_failing(segment_fixture.segment_id)],
            chat_model=_model(
                '{"repairs": [{"index": 0, "action": "AUDIT"}]}',
                '{"repairs": [{"index": 0, "action": "CERTIFY"}]}',
            ),
        )
    finally:
        TenantContext.clear()

    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_BUDGET_EXHAUSTED

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT cause, failure_reason, attempts, char_start, char_end, "
                    "       candidate, agent_run_ids "
                    "FROM compile_quarantine WHERE segment_id = :sid"
                ),
                {"sid": segment_fixture.segment_id},
            ).one()
    finally:
        owner_engine.dispose()

    assert row.cause == "REPAIR_BUDGET_EXHAUSTED"
    assert row.failure_reason == "PARSE_ERROR"
    assert row.attempts == 3  # §3.9's "fail 3x": 1 initial + max_repairs=2
    # The span is a mechanically verified fact carried through untouched, so
    # a human can render this row back onto the source page later.
    assert _SEGMENT_TEXT[row.char_start : row.char_end] == _SPAN
    assert row.candidate["llm_candidate"]["span_text"] == _SPAN
    # uuid[] lineage actually round-trips, not just in theory.
    assert len(row.agent_run_ids) == 2
    assert {str(x) for x in row.agent_run_ids} == set(result.agent_run_ids)


def test_a_zero_call_quarantine_writes_no_agent_run_and_an_empty_lineage(segment_fixture):
    """The case that forced compile_quarantine to exist as its own table:
    a candidate quarantined with no actionable hint makes no LLM call at
    all, and agent_runs' model_id/prompt_* columns are all NOT NULL.
    """
    from obligo_brain.compiler.ir_compile import CompileFailureReason

    # Every field of this candidate is valid, so none of derive_hints()'s
    # three checks can explain the failure -- which is the whole point. The
    # CompileFailure is hand-built because the compiler cannot currently
    # produce an unexplainable one; this is the fallback for a future
    # grammar rejection nobody has enumerated yet.
    start = _SEGMENT_TEXT.index(_SPAN)
    valid_candidate = GroundedCandidate(
        llm_candidate=LLMCandidate(
            span_text=_SPAN,
            modality="MUST",
            obligor_alias="Vendor",
            obligee_alias="Customer",
            action="NOTIFY",
            object_class="deliverables",
            object_raw_text="the Deliverables",
            confidence=0.9,
        ),
        source=ast.SourceRef(
            segment_id=str(segment_fixture.segment_id),
            char_start=start,
            char_end=start + len(_SPAN),
        ),
        grounding_tier=GroundingTier.EXACT,
    )
    unexplainable = CompileFailure(
        reason=CompileFailureReason.PARSE_ERROR,
        detail="a grammar rejection with no field-level explanation",
        candidate=valid_candidate,
    )

    TenantContext.set(segment_fixture.org_a_id)
    try:
        result = run_repair(
            _segment(segment_fixture),
            str(segment_fixture.org_a_id),
            [unexplainable],
            chat_model=_model(),
        )
    finally:
        TenantContext.clear()

    assert result.agent_run_ids == []

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            assert (
                conn.execute(
                    text("SELECT count(*) FROM agent_runs WHERE segment_id = :sid"),
                    {"sid": segment_fixture.segment_id},
                ).scalar()
                == 0
            )
            row = conn.execute(
                text(
                    "SELECT cause, attempts, agent_run_ids FROM compile_quarantine "
                    "WHERE segment_id = :sid"
                ),
                {"sid": segment_fixture.segment_id},
            ).one()
    finally:
        owner_engine.dispose()

    assert row.cause == "NO_ACTIONABLE_HINT"
    assert row.attempts == 1
    assert list(row.agent_run_ids) == []  # the empty-uuid[] path really works


def test_quarantine_write_for_another_org_is_refused_by_rls_not_by_app_code(segment_fixture):
    """RLS's WITH CHECK is what stops a wrong org_id from being written, not
    a Python conditional. Proven by asking obligo_brain to write org B's
    org_id while the tenant GUC says org A.
    """
    TenantContext.set(segment_fixture.org_a_id)
    try:
        with pytest.raises(DBAPIError) as excinfo:
            run_repair(
                _segment(segment_fixture),
                str(segment_fixture.org_b_id),  # a tenant this connection may not touch
                [_failing(segment_fixture.segment_id)],
                chat_model=_model(),
            )
    finally:
        TenantContext.clear()

    assert "row-level security" in str(excinfo.value).lower()


def test_run_extraction_can_actually_write_its_agent_runs_row(segment_fixture):
    """Regression test for a REAL bug this checkpoint found in the Extractor
    checkpoint's code, not a hypothetical one.

    extraction.py's _record_agent_run() used `INSERT ... RETURNING id`.
    Postgres requires SELECT privilege on any column a RETURNING clause
    names, and V17 grants obligo_brain INSERT and nothing else -- on
    purpose. So run_extraction() would have failed with "permission denied
    for table agent_runs" on EVERY call against the real database. It
    survived because V17 had never been applied to the Neon branch (this
    checkpoint's migration run applied V17 and V18 together) and because no
    real-database test exercised run_extraction at all.

    It lives in this file rather than its own because it shares the fixture
    and proves the identical property the repair path exposed: that V17's
    deliberately minimal grant is sufficient for the code written against
    it. The lesson generalises -- a table whose grant is INSERT-only cannot
    use RETURNING, and only a real-database test can catch that.
    """
    from obligo_brain.graphs.extraction import run_extraction

    def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0):
        return ChatCompletion(
            content='{"obligations": []}',
            model_id=model_id,
            input_tokens=5,
            output_tokens=2,
            latency_ms=4.0,
        )

    TenantContext.set(segment_fixture.org_a_id)
    try:
        result = run_extraction(
            str(segment_fixture.segment_id),
            str(segment_fixture.org_a_id),
            chat_model=chat_model,
        )
    finally:
        TenantContext.clear()

    assert result.grounded == [] and result.rejected == []

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            row = conn.execute(
                text("SELECT id, node FROM agent_runs WHERE segment_id = :sid"),
                {"sid": segment_fixture.segment_id},
            ).one()
    finally:
        owner_engine.dispose()

    assert row.node == "extractor"
    # The client-generated id is the one actually persisted.
    assert str(row.id) == result.agent_run_id


def test_no_failures_touches_neither_the_model_nor_the_database(segment_fixture):
    def exploding_model(**kwargs):
        raise AssertionError("run_repair called the model with nothing to repair")

    TenantContext.set(segment_fixture.org_a_id)
    try:
        result = run_repair(
            _segment(segment_fixture),
            str(segment_fixture.org_a_id),
            [],
            chat_model=exploding_model,
        )
    finally:
        TenantContext.clear()

    assert result.compiled == [] and result.quarantined == [] and result.agent_run_ids == []

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            assert (
                conn.execute(
                    text("SELECT count(*) FROM compile_quarantine WHERE segment_id = :sid"),
                    {"sid": segment_fixture.segment_id},
                ).scalar()
                == 0
            )
    finally:
        owner_engine.dispose()
