"""R5's own scoping seam (F16, section 10.1): `run(items=...)` lets a caller
check only a pre-scoped item set instead of globbing every committed item,
so a document with no scoring registry yet (batch 3, never spent) doesn't
turn into an R5 failure for a pass that was never going to touch it.
"""

from __future__ import annotations

import json

import pytest

from evals.harness import registry as registry_mod
from evals.harness import selfcheck


def _write_registry(tmp_path, doc_id: str, parties: list[dict]) -> None:
    (tmp_path / f"{doc_id}.json").write_text(
        json.dumps({"doc_id": doc_id, "parties": parties})
    )


def _item(item_id="A-01", doc_id="D1", obligor="Vendor", obligee="Client",
         underspecified=False, temporal=None) -> dict:
    return {
        "item_id": item_id, "doc_id": doc_id, "obligor": obligor, "obligee": obligee,
        "underspecified": underspecified, "temporal": temporal, "missing_fields": [],
    }


def test_run_with_explicit_items_checks_only_those_items(tmp_path, monkeypatch):
    """PLANTED: without scoping, run() globs GOLDENS_DIR and would try to load a
    registry for every committed item's document, including ones this pass was
    never asked about. Passing `items=` must bypass the glob entirely."""
    monkeypatch.setattr(registry_mod, "REGISTRY_DIR", tmp_path)
    _write_registry(tmp_path, "D1", [
        {"canonical_name": "Vendor", "aliases": []},
        {"canonical_name": "Client", "aliases": []},
    ])
    # No registry for D2 exists at all -- if run() globbed real committed
    # items (which include documents this test knows nothing about) instead
    # of respecting `items=`, this would raise FileNotFoundError.
    failures = selfcheck.run(items=[_item(doc_id="D1")])
    assert failures == []


def test_run_with_explicit_items_still_catches_a_real_mismatch(tmp_path, monkeypatch):
    """The scoping must not weaken what R5 actually checks -- a genuine
    registry/item disagreement inside the scoped set still fails loudly."""
    monkeypatch.setattr(registry_mod, "REGISTRY_DIR", tmp_path)
    _write_registry(tmp_path, "D1", [{"canonical_name": "Vendor", "aliases": []}])
    # obligee "Client" does not resolve against this registry, so
    # underspecified=False disagrees with what section 3.9 predicts.
    failures = selfcheck.run(items=[_item(doc_id="D1", underspecified=False)])
    assert len(failures) == 1
    assert failures[0].item_id == "A-01"
    assert "UNDERSPECIFIED MISMATCH" in failures[0].kind


def test_run_without_items_still_globs_goldens_dir_by_default(tmp_path, monkeypatch):
    """The default (no `items=`) behaviour -- glob items_dir -- is unchanged."""
    monkeypatch.setattr(registry_mod, "REGISTRY_DIR", tmp_path)
    _write_registry(tmp_path, "D1", [
        {"canonical_name": "Vendor", "aliases": []},
        {"canonical_name": "Client", "aliases": []},
    ])
    items_dir = tmp_path / "goldens"
    (items_dir / "batch01" / "items").mkdir(parents=True)
    (items_dir / "batch01" / "items" / "A-01.json").write_text(json.dumps(_item()))
    failures = selfcheck.run(items_dir)
    assert failures == []
