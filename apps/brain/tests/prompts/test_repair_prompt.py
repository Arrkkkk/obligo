"""Drift guards for prompts/repair/v1.yaml.

The repair prompt hardcodes the closed modality and action vocabularies
rather than having them injected at render time. That is deliberate: an
injected taxonomy would let the SAME prompt_hash produce different model
behaviour whenever ast.ACTIONS changes, which breaks the one thing
prompt_hash exists to guarantee -- that (prompt_hash, model_id) alone
answers "did this call use the prompt version we think it did" (NFR-10,
§13.5).

The cost of hardcoding is drift, so it is bought back here: if the taxonomy
changes and this prompt does not, CI fails loudly and forces a version
bump, which is exactly the discipline §13.5 asks for ("changing a prompt
requires a version bump"). Same shape as tests/compiler/test_action_taxonomy.py,
which keeps ast.ACTIONS and the grammar in sync.
"""

from __future__ import annotations

import re

from obligo_brain.compiler import ast
from obligo_brain.prompts import registry


def _listed_actions(system: str) -> list[str]:
    """The verb list in the system prompt, which is written as a single
    prose run between "one word:" and the sentence that follows it.
    """
    body = system.split("exactly one verb from this closed list, upper case, one word:")[1]
    body = body.split("Choose the listed verb")[0]
    return re.findall(r"\b[A-Z]{3,}\b", body)


def test_the_prompt_lists_exactly_the_closed_action_taxonomy():
    prompt = registry.load("repair")

    assert _listed_actions(prompt.system) == list(ast.ACTIONS)


def test_the_prompt_lists_exactly_the_four_modalities():
    prompt = registry.load("repair")
    declared = prompt.system.split("exactly one of ")[1].split(".")[0]

    listed = [m.strip() for m in declared.split(",")]
    assert listed == list(ast.MODALITIES)


def test_the_prompt_pins_a_model_id_and_deterministic_temperature():
    prompt = registry.load("repair")

    assert prompt.model_constraints["provider"] == "groq"
    assert prompt.model_constraints["model_id"]
    assert prompt.model_constraints["temperature"] == 0.0


def test_repair_prompt_hash_is_independent_of_the_extraction_prompt():
    """Both are loaded through the same registry; a bug that returned the
    wrong file would otherwise be invisible.
    """
    assert registry.load("repair").prompt_hash != registry.load("extraction").prompt_hash
