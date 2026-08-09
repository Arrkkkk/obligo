"""ast.ACTIONS (the closed 34-verb taxonomy) and grammar/obligation.lark's
ACTION terminal alternation must list the exact same verbs. There is no
single source of truth between a Lark terminal and a Python tuple, so
nothing else catches a drift between them -- this test is that check.
"""

from __future__ import annotations

import re
from pathlib import Path

from obligo_brain.compiler import ast

_GRAMMAR_PATH = Path(__file__).resolve().parents[2] / "src" / "obligo_brain" / "compiler" / "grammar" / "obligation.lark"


def _actions_in_grammar() -> set[str]:
    text = _GRAMMAR_PATH.read_text()
    match = re.search(r"^ACTION: (.+?)\n\n", text, re.MULTILINE | re.DOTALL)
    assert match, "could not locate the ACTION terminal definition in obligation.lark"
    return set(re.findall(r'"([A-Z_]+)"', match.group(1)))


def test_action_taxonomy_matches_grammar():
    assert _actions_in_grammar() == set(ast.ACTIONS)


def test_action_taxonomy_has_34_verbs_and_blueprints_10():
    blueprint_named = {
        "NOTIFY", "DELIVER", "PAY", "DELETE", "RETAIN",
        "MAINTAIN", "INDEMNIFY", "REPORT", "PROVIDE", "CURE",
    }
    assert blueprint_named <= set(ast.ACTIONS)
    assert len(ast.ACTIONS) == 34
    assert len(set(ast.ACTIONS)) == 34, "no duplicate verbs"
