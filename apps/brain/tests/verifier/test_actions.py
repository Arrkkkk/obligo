"""verifier/actions.py -- the antagonism table and gloss function."""

from __future__ import annotations

from obligo_brain.compiler import ast
from obligo_brain.verifier import actions


def test_gloss_is_plain_lowercase_for_every_closed_taxonomy_verb():
    # Pins actions.py's own claim: all 34 verbs are regular enough that
    # plain lowercasing is correct, with no irregular-form table needed. If
    # a future addition to ast.ACTIONS breaks this assumption, this test
    # fails loudly rather than silently misrendering a sentence.
    for action in ast.ACTIONS:
        assert actions.gloss(action) == action.lower()
        assert actions.gloss(action).isalpha()  # no stray punctuation/digits


def test_retain_implies_prohibition_on_delete():
    assert actions.implied_prohibition("RETAIN") == "DELETE"


def test_withhold_implies_prohibition_on_disclose():
    assert actions.implied_prohibition("WITHHOLD") == "DISCLOSE"


def test_antagonism_is_one_directional_not_symmetric():
    # DELETE does not imply a prohibition on RETAIN -- "must delete by
    # March 1" does not forbid retaining beforehand (scoping conversation
    # §2.3's own reasoning).
    assert actions.implied_prohibition("DELETE") is None
    assert actions.implied_prohibition("DISCLOSE") is None


def test_unrelated_actions_have_no_antagonism():
    for action in ast.ACTIONS:
        if action not in actions.IMPLIED_PROHIBITIONS:
            assert actions.implied_prohibition(action) is None


def test_antagonism_table_is_seeded_strictly_with_exactly_two_pairs():
    # Pins the "strictly over loosely" scope decision -- a future session
    # extending this table should do so deliberately, and this test should
    # be updated in the same commit, not silently invalidated.
    assert actions.IMPLIED_PROHIBITIONS == {"RETAIN": "DELETE", "WITHHOLD": "DISCLOSE"}
