"""The action-antagonism table and the action-gloss function (scoping
conversation §2.3/§4) -- both small, deliberate, hand-authored artifacts,
never an LLM call (Standing Principle 2: these determine a finding's
correctness, not a draft).

## Antagonism

DELETE and RETAIN are different actions in the closed 34-verb taxonomy
(ast.ACTIONS), so a literal `MUST RETAIN x` / `MUST_NOT DELETE x` pair is the
only shape z3_lowering.py's plain act-key matching would catch -- but the
product's own headline example ("a retention policy contradicted a deletion
promise", CLAUDE.md's Phase 1 vision) is usually phrased as `MUST RETAIN` /
`MUST DELETE`, with no explicit MUST_NOT anywhere. Without an antagonism
relation, that case never fires.

**The mapping is deliberately one-directional, not a symmetric pair set,**
and that's a real semantic distinction, not an oversight: RETAIN and
WITHHOLD describe a continuous state held throughout a window ("retain the
records during 2027" is true at every instant of 2027), the same shape as a
MUST_NOT's own forbidding window. DELETE and DISCLOSE describe a
point-in-time act performed once within a window ("delete by March 1"
happens at some instant, not throughout). A MUST on the continuous side
genuinely forbids the point-act's antagonist for the whole window it covers
-- "must retain during 2027" really does mean "must not delete at any point
in 2027". The reverse doesn't hold: "must delete by March 1" does not forbid
retaining before March 1 -- you may legitimately retain right up until you
delete. So only RETAIN -> DELETE and WITHHOLD -> DISCLOSE produce an implied
prohibition; DELETE and DISCLOSE never do.

Seeded strictly, matching ir_compile.py's own "strict over loose" posture
(CLAUDE.md's IR-Compiler checkpoint) -- only pairs that are unambiguous by
the dictionary meaning of the verbs are here. Plausible-but-arguable pairs
(TERMINATE/MAINTAIN, TRANSFER/RETAIN, WAIVE/ENSURE) are deliberately left
out rather than guessed at; each one is a real judgment call and belongs in
docs/VERIFIER.md with its own reasoning if it's ever added, not silently
folded into this table.

## Glosses

ast.ACTIONS (compiler/ast.py) is 34 regular English verbs already spelled in
their base form (NOTIFY, DELIVER, PAY, ...) -- every one of them is
grammatically correct as a present-tense verb after plain lowercasing, with
no irregular form requiring a hand-authored table (confirmed by inspection
of all 34; tests/verifier/test_actions.py pins this against the live
ast.ACTIONS tuple so a future addition that breaks the assumption fails
loudly rather than silently misrendering a sentence).
"""

from __future__ import annotations

# action -> the action it implicitly prohibits when asserted as a MUST.
# See module docstring for why this is one-directional.
IMPLIED_PROHIBITIONS: dict[str, str] = {
    "RETAIN": "DELETE",
    "WITHHOLD": "DISCLOSE",
}


def implied_prohibition(action: str) -> str | None:
    """The action this one implicitly prohibits when performed as a MUST
    duty, or None if `action` carries no antagonism relation in v1.
    """
    return IMPLIED_PROHIBITIONS.get(action)


def gloss(action: str) -> str:
    """Present-tense verb phrase for templated finding sentences. See module
    docstring for why plain lowercasing is correct for the entire closed
    taxonomy rather than a hand-authored per-verb table.
    """
    return action.lower()
