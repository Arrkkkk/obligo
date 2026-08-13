"""run_pipeline()'s orchestration -- extract -> ground -> compile -> repair
-> typecheck -- proven end to end against real Neon Postgres (parties for
typecheck's party resolution; segments/agent_runs/compile_quarantine for
the stages that already write there) and a fake ChatModel (no live LLM
calls -- the branching logic under test is which bucket a candidate lands
in, not model behavior, which extraction.py's and repair.py's own suites
already cover exhaustively against fakes and cassettes).

Every stage run_pipeline() calls (run_extraction, run_repair, typecheck)
opens its own tenant_scope() internally, so there is no pure, DB-free
"orchestration only" layer to test in isolation the way repair_candidates()
lets repair.py test its loop without a database -- unlike that loop, this
orchestration's branching *is* which DB-touching stage a candidate reaches
next. These are real-Neon integration tests for that reason, not a gap.

Five terminal outcomes, one test each, matching the walkthrough this
checkpoint's proposal was built against:
  1. grounds, compiles, typechecks clean (both parties resolved)
  2. fails grounding (hallucinated span) -- never reaches compile
  3. fails compile, repaired successfully -- ends up typechecked
  4. fails compile, repair exhausted -- ends up quarantined
  5. compiles, typecheck leaves the obligor UNRESOLVED -- still
     typechecked, underspecified=True, not a failure state
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from obligo_brain.compiler import ast
from obligo_brain.graphs.pipeline import run_pipeline
from obligo_brain.graphs.repair import QuarantineCause
from obligo_brain.graphs.state import RejectionReason
from obligo_brain.models.providers.base import ChatCompletion
from obligo_brain.platform.tenancy.context import TenantContext

pytestmark = pytest.mark.skipif(
    not (os.environ.get("DATABASE_URL") and os.environ.get("BRAIN_DB_PASSWORD")),
    reason="DATABASE_URL/BRAIN_DB_PASSWORD not set -- skipping real-database test",
)


def _owner_url() -> str:
    return os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)


@dataclass
class PipelineFixture:
    engine: Engine
    org_id: uuid.UUID
    source_id: uuid.UUID

    def insert_segment(self, seg_text: str) -> uuid.UUID:
        segment_id = uuid.uuid4()
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO segments "
                    "(id, org_id, source_id, text, char_start, char_end, ordinal, page) "
                    "VALUES (:id, :org_id, :source_id, :text, 0, :end, 0, 1)"
                ),
                {
                    "id": segment_id,
                    "org_id": self.org_id,
                    "source_id": self.source_id,
                    "text": seg_text,
                    "end": len(seg_text),
                },
            )
        return segment_id


@pytest.fixture
def pipeline_fixture() -> Iterator[PipelineFixture]:
    owner_engine = create_engine(_owner_url())

    org_id = uuid.uuid4()
    user_id, source_id = uuid.uuid4(), uuid.uuid4()

    with owner_engine.begin() as conn:
        conn.execute(
            text("INSERT INTO organizations (id, name) VALUES (:id, 'Pipeline Test Org')"),
            {"id": org_id},
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
                "org_id": org_id,
                "user_id": user_id,
                "sha": "c" * 64,
                "key": f"test/{source_id}",
            },
        )
        # Both sides of the "clean" obligation resolve; "Acme Widgets Inc"
        # (test 5's obligor alias) deliberately does not match either.
        conn.execute(
            text(
                "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                "VALUES (gen_random_uuid(), :org_id, 'Acme Vendor Corp', ARRAY['Vendor'])"
            ),
            {"org_id": org_id},
        )
        conn.execute(
            text(
                "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                "VALUES (gen_random_uuid(), :org_id, 'Acme Customer Corp', ARRAY['Customer'])"
            ),
            {"org_id": org_id},
        )

    try:
        yield PipelineFixture(engine=owner_engine, org_id=org_id, source_id=source_id)
    finally:
        with owner_engine.begin() as conn:
            conn.execute(text("DELETE FROM compile_quarantine WHERE org_id = :o"), {"o": org_id})
            conn.execute(text("DELETE FROM agent_runs WHERE org_id = :o"), {"o": org_id})
            conn.execute(text("DELETE FROM segments WHERE org_id = :o"), {"o": org_id})
            conn.execute(text("DELETE FROM parties WHERE org_id = :o"), {"o": org_id})
            conn.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        owner_engine.dispose()


def _extraction_response(obligations: list[dict]) -> str:
    return json.dumps({"obligations": obligations})


def _model(*responses: str):
    """Pops canned responses in call order -- extraction call first, then
    one per repair attempt. Defaults to an empty repair payload once
    exhausted, same shape test_repair_db.py's own fake model uses.
    """
    remaining = list(responses)

    def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0):
        content = remaining.pop(0) if remaining else '{"repairs": []}'
        return ChatCompletion(
            content=content, model_id=model_id, input_tokens=7, output_tokens=3, latency_ms=9.0
        )

    return chat_model


def _run(fixture: PipelineFixture, segment_id: uuid.UUID, chat_model):
    TenantContext.set(fixture.org_id)
    try:
        return run_pipeline(str(segment_id), str(fixture.org_id), chat_model=chat_model)
    finally:
        TenantContext.clear()


def test_clean_candidate_grounds_compiles_and_typechecks_fully_resolved(pipeline_fixture):
    """Deliberately no temporal clause at all. Both WITHIN's and RELATIVE's
    trigger is a TriggerRef, and symbols.resolve_trigger() unconditionally
    returns None in this checkpoint (no defined-terms registry exists yet
    -- typecheck.py's own docstring), so any temporal referencing a
    trigger is *always* underspecified by design, never "fully resolved."
    Omitting temporal isolates party resolution as the only thing this
    test needs to prove clean -- typecheck.py's own docstring says
    temporal=None is never flagged, which is exactly the case here.
    """
    seg_text = "1.1 Vendor shall notify Customer of a Security Incident."
    span = "Vendor shall notify Customer of a Security Incident."
    segment_id = pipeline_fixture.insert_segment(seg_text)

    result = _run(
        pipeline_fixture,
        segment_id,
        _model(
            _extraction_response(
                [
                    {
                        "span_text": span,
                        "modality": "MUST",
                        "obligor_alias": "Vendor",
                        "obligee_alias": "Customer",
                        "action": "NOTIFY",
                        "object_class": "security_incident",
                        "object_raw_text": "a Security Incident",
                        "confidence": 0.9,
                    }
                ]
            )
        ),
    )

    assert result.rejected == []
    assert result.quarantined == []
    (obligation,) = result.typechecked
    assert obligation.underspecified is False
    assert obligation.missing_fields == ()
    assert isinstance(obligation.obligor, ast.ResolvedParty)
    assert obligation.obligor.canonical_name == "Acme Vendor Corp"
    assert isinstance(obligation.obligee, ast.ResolvedParty)
    assert obligation.obligee.canonical_name == "Acme Customer Corp"
    # Extraction only -- nothing needed repair, so exactly one agent_runs row.
    assert len(result.agent_run_ids) == 1


def test_hallucinated_span_fails_grounding_and_never_reaches_compile(pipeline_fixture):
    seg_text = "1.1 The parties acknowledge receipt of this Agreement."
    segment_id = pipeline_fixture.insert_segment(seg_text)

    result = _run(
        pipeline_fixture,
        segment_id,
        _model(
            _extraction_response(
                [
                    {
                        "span_text": "Vendor shall pay $1,000,000 immediately.",
                        "modality": "MUST",
                        "obligor_alias": "Vendor",
                        "obligee_alias": "Customer",
                        "action": "PAY",
                        "object_class": "payment",
                        "object_raw_text": "$1,000,000",
                        "confidence": 0.9,
                    }
                ]
            )
        ),
    )

    assert result.typechecked == []
    assert result.quarantined == []
    (rejection,) = result.rejected
    assert rejection.reason == RejectionReason.SPAN_NOT_FOUND
    # Nothing to compile means run_repair short-circuits with no DB write
    # and no model call of its own (its own docstring's guarantee) -- only
    # the extraction call happened.
    assert len(result.agent_run_ids) == 1


def test_unmapped_action_is_repaired_successfully_and_ends_up_typechecked(pipeline_fixture):
    seg_text = "1.1 Vendor shall register the Deliverables with the Customer."
    span = "Vendor shall register the Deliverables with the Customer."
    segment_id = pipeline_fixture.insert_segment(seg_text)

    result = _run(
        pipeline_fixture,
        segment_id,
        _model(
            _extraction_response(
                [
                    {
                        "span_text": span,
                        "modality": "MUST",
                        "obligor_alias": "Vendor",
                        "obligee_alias": "Customer",
                        "action": "REGISTER",  # not in the closed 34-verb taxonomy
                        "object_class": "deliverables",
                        "object_raw_text": "the Deliverables",
                        "confidence": 0.9,
                    }
                ]
            ),
            '{"repairs": [{"index": 0, "action": "NOTIFY"}]}',
        ),
    )

    assert result.rejected == []
    assert result.quarantined == []
    (obligation,) = result.typechecked
    assert obligation.action == "NOTIFY"
    assert obligation.underspecified is False
    # Extraction + exactly one repair call.
    assert len(result.agent_run_ids) == 2


def test_unrepairable_action_exhausts_the_budget_and_is_quarantined(pipeline_fixture):
    seg_text = "1.1 Vendor shall audit the Records maintained by the Customer."
    span = "Vendor shall audit the Records maintained by the Customer."
    segment_id = pipeline_fixture.insert_segment(seg_text)

    result = _run(
        pipeline_fixture,
        segment_id,
        _model(
            _extraction_response(
                [
                    {
                        "span_text": span,
                        "modality": "MUST",
                        "obligor_alias": "Vendor",
                        "obligee_alias": "Customer",
                        "action": "AUDIT",  # not in the closed taxonomy
                        "object_class": "records",
                        "object_raw_text": "the Records",
                        "confidence": 0.9,
                    }
                ]
            ),
            # Both repair attempts "correct" to another out-of-taxonomy verb
            # -- deliberately unrepairable, to exercise REPAIR_BUDGET_EXHAUSTED.
            '{"repairs": [{"index": 0, "action": "CERTIFY"}]}',
            '{"repairs": [{"index": 0, "action": "INVESTIGATE"}]}',
        ),
    )

    assert result.typechecked == []
    assert result.rejected == []
    (item,) = result.quarantined
    assert item.cause is QuarantineCause.REPAIR_BUDGET_EXHAUSTED
    assert item.attempts == 3  # 1 initial + max_repairs=2, §3.9's "fail 3x"
    # Extraction + 2 repair calls.
    assert len(result.agent_run_ids) == 3

    owner_engine = create_engine(_owner_url())
    try:
        with owner_engine.begin() as conn:
            row = conn.execute(
                text("SELECT cause FROM compile_quarantine WHERE segment_id = :sid"),
                {"sid": segment_id},
            ).one()
    finally:
        owner_engine.dispose()
    assert row.cause == "REPAIR_BUDGET_EXHAUSTED"


def test_unresolved_obligor_is_typechecked_underspecified_not_discarded(pipeline_fixture):
    seg_text = "1.1 Acme Widgets Inc shall maintain the Records for the Customer."
    span = "Acme Widgets Inc shall maintain the Records for the Customer."
    segment_id = pipeline_fixture.insert_segment(seg_text)

    result = _run(
        pipeline_fixture,
        segment_id,
        _model(
            _extraction_response(
                [
                    {
                        "span_text": span,
                        "modality": "MUST",
                        "obligor_alias": "Acme Widgets Inc",  # matches no seeded party
                        "obligee_alias": "Customer",
                        "action": "MAINTAIN",
                        "object_class": "records",
                        "object_raw_text": "the Records",
                        "confidence": 0.9,
                    }
                ]
            )
        ),
    )

    assert result.rejected == []
    assert result.quarantined == []
    (obligation,) = result.typechecked
    assert obligation.underspecified is True
    assert "obligor" in obligation.missing_fields
    assert isinstance(obligation.obligor, ast.UnresolvedParty)
    assert obligation.obligor.alias == "Acme Widgets Inc"
    assert isinstance(obligation.obligee, ast.ResolvedParty)
    # Compiled cleanly on the first attempt -- no repair needed.
    assert len(result.agent_run_ids) == 1
