"""Builds and tears down the real-database fixture one scored run needs.

`run_pipeline(segment_id, org_id)` reads `SELECT id, text FROM segments
WHERE id = :id` keyed by UUID, but gold items carry a corpus identifier
("C03-192"). So a scored run must materialise the whole chain the schema
requires -- organizations -> users -> sources -> segments, plus parties --
and hold the corpus-id -> UUID mapping.

ONE ORG PER SOURCE DOCUMENT (guideline section 21 R1), not one shared org.
symbols.resolve_party() returns None when its query matches more than one
row, and `Client` is a defined party role in both E02 and E07 while
`Provider` and `Recipient` are defined in both C17 and E01. A shared
registry would resolve those to nothing and flip locked items E07-01 and
C17-01 to underspecified -- a scoring failure caused entirely by harness
setup and charged to extraction. Per-document orgs make that impossible by
construction rather than by careful ordering, and RLS gives the isolation
for free.

Seeding uses the OWNER connection while the pipeline reads through the
`obligo_brain` role -- the same owner-seeds/brain-reads split
tests/compiler/test_symbols.py established, because RLS is FORCEd and the
brain role cannot insert its own fixtures.

Teardown is unconditional and ordered against the foreign keys. It also
removes `agent_runs` and `compile_quarantine` rows, which a real scored run
genuinely writes: the harness deliberately exercises the production path
rather than a leaner one that could silently diverge from it.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator, Sequence

from sqlalchemy import create_engine, text

from evals.harness import registry as registry_mod

_MARK = "eval-harness"


def _owner_engine():
    url = os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url, pool_pre_ping=True)


@dataclass
class DocumentFixture:
    doc_id: str
    org_id: str
    user_id: str
    source_id: str
    segment_uuids: dict[str, str] = field(default_factory=dict)   # corpus id -> uuid
    party_ids: dict[str, str] = field(default_factory=dict)       # canonical -> uuid


def _seed_document(conn, doc_id: str, segments: Sequence[tuple[str, str]]) -> DocumentFixture:
    run_tag = uuid.uuid4().hex[:8]
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    source_id = str(uuid.uuid4())

    conn.execute(
        text("INSERT INTO organizations (id, name) VALUES (:id, :name)"),
        {"id": org_id, "name": f"{_MARK} {doc_id} {run_tag}"},
    )
    conn.execute(
        text("INSERT INTO users (id, google_sub, email) VALUES (:id, :sub, :email)"),
        {"id": user_id, "sub": f"{_MARK}-{run_tag}", "email": f"{_MARK}-{run_tag}@invalid.test"},
    )
    conn.execute(
        text(
            "INSERT INTO sources (id, org_id, uploaded_by, filename, byte_size, sha256, storage_key) "
            "VALUES (:id, :org, :user, :fn, :size, :sha, :key)"
        ),
        {
            "id": source_id, "org": org_id, "user": user_id,
            "fn": f"{doc_id}.txt", "size": sum(len(t) for _, t in segments),
            # a REAL digest of the seeded text: `sources` carries a
            # sources_sha256_check constraint requiring 64 hex characters, and a
            # marker string is rejected by it. Digesting the content also makes the
            # row honest -- it is the sha256 of exactly what was seeded.
            "sha": hashlib.sha256(
                "".join(body for _, body in segments).encode()
            ).hexdigest(),
            "key": f"{_MARK}/{doc_id}/{run_tag}/v1",
        },
    )

    fx = DocumentFixture(doc_id=doc_id, org_id=org_id, user_id=user_id, source_id=source_id)
    # `ordinal` and `page` are NOT NULL with no default -- added by
    # V13__segments_layout_columns, AFTER V12 created the table. Read the LIVE
    # schema, never the creating migration: this fixture was first written
    # against V12 alone and failed on both columns.
    for ordinal, (corpus_id, body) in enumerate(segments, start=1):
        seg_id = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO segments "
                "(id, org_id, source_id, text, char_start, char_end, ordinal, page) "
                "VALUES (:id, :org, :src, :txt, 0, :end, :ord, 1)"
            ),
            {"id": seg_id, "org": org_id, "src": source_id, "txt": body,
             "end": len(body), "ord": ordinal},
        )
        fx.segment_uuids[corpus_id] = seg_id

    reg = registry_mod.load(doc_id)
    for party in reg.parties:
        pid = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO parties (id, org_id, canonical_name, aliases) "
                "VALUES (:id, :org, :name, :aliases)"
            ),
            # aliases are inserted VERBATIM: section 21 R2 -- the production query
            # matches this array case-SENSITIVELY, so normalising case here would
            # make the fixture pass locally and fail in production.
            {"id": pid, "org": org_id, "name": party.canonical_name,
             "aliases": list(party.aliases)},
        )
        fx.party_ids[party.canonical_name] = pid
    return fx


def _teardown(conn, fixtures: Sequence[DocumentFixture]) -> dict[str, int]:
    removed = {t: 0 for t in
               ("compile_quarantine", "agent_runs", "segments", "sources", "parties", "users", "organizations")}
    for fx in fixtures:
        for table in ("compile_quarantine", "agent_runs", "segments", "sources", "parties"):
            r = conn.execute(text(f"DELETE FROM {table} WHERE org_id = :o"), {"o": fx.org_id})
            removed[table] += r.rowcount or 0
        r = conn.execute(text("DELETE FROM users WHERE id = :u"), {"u": fx.user_id})
        removed["users"] += r.rowcount or 0
        r = conn.execute(text("DELETE FROM organizations WHERE id = :o"), {"o": fx.org_id})
        removed["organizations"] += r.rowcount or 0
    return removed


@contextmanager
def document_fixtures(
    per_document: dict[str, Sequence[tuple[str, str]]]
) -> Iterator[dict[str, DocumentFixture]]:
    """Seeds one org per document, yields the fixtures, and always tears down.

    Teardown runs in a `finally` so a failed or interrupted scoring run does
    not leave orphaned orgs on the shared CI branch -- the harness must never
    be the reason the next run's registry is ambiguous.
    """
    engine = _owner_engine()
    built: list[DocumentFixture] = []
    try:
        with engine.begin() as conn:
            for doc_id, segments in sorted(per_document.items()):
                built.append(_seed_document(conn, doc_id, segments))
        yield {fx.doc_id: fx for fx in built}
    finally:
        with engine.begin() as conn:
            removed = _teardown(conn, built)
        print(f"  teardown removed: {removed}")


def residue_count(engine=None) -> dict[str, int]:
    """Counts anything this harness has ever left behind, by its marker.
    A non-zero result after a run means teardown is incomplete."""
    engine = engine or _owner_engine()
    with engine.connect() as conn:
        orgs = conn.execute(
            text("SELECT count(*) FROM organizations WHERE name LIKE :m"), {"m": f"{_MARK}%"}
        ).scalar()
        users = conn.execute(
            text("SELECT count(*) FROM users WHERE google_sub LIKE :m"), {"m": f"{_MARK}%"}
        ).scalar()
    return {"organizations": int(orgs or 0), "users": int(users or 0)}
