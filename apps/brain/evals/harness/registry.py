"""Loads the per-document scoring registries and answers the one question
R5 and the scorer both need: does this alias resolve, and to which party?

Guideline section 21 R1 requires ONE registry per source document, never a
shared org-wide one: symbols.resolve_party() returns None when its query
matches more than one row, and `Client` is a defined party role in both E02
and E07 while `Provider` and `Recipient` are defined in both C17 and E01. A
shared registry would resolve those aliases to nothing and flip locked items
E07-01 and C17-01 to underspecified -- a scoring failure caused entirely by
harness setup and attributed to extraction.

CORRECTION IN PLACE (v0.65) -- THE RULE ABOVE STANDS AND THIS MODULE IMPLEMENTS
IT UNCHANGED; THE EXAMPLES IN THE PARAGRAPH ABOVE DO NOT SURVIVE CHECKING. This
is a SECOND hand-maintained copy of a claim that also lives in guideline section
21 R1 and in CLAUDE.md's debt list -- the same duplicate-copy hazard v0.61
recorded for the tag vocabulary -- and all three are corrected together. Measured
against the corpus while authoring registry/E02.json for batch 5:

  * E02 defines NO bare `Client`. All 22 occurrences of the token are inside
    `Client Facility`, which E02 defines as "the departments and facilities of
    the CBay customer" -- an unnamed third party R3 excludes, so E02's registry
    could never have carried the entry.
  * E01 defines `Service Provider` / `Service Recipient` (78 and 57
    occurrences), never the bare `Provider` / `Recipient` C17 defines.

And the stated CONSEQUENCE was tested by execution rather than argued: a single
registry merged from all committed ones resolves `Client`, `Provider` and
`Recipient` each UNIQUELY, so E07-01 and C17-01 would not flip.

WHY THE RULE IS UNTOUCHED ANYWAY. resolve_party()'s len(rows) != 1 behaviour is
real, this module reproduces it deliberately, and `Provider` against E01's
`Service Provider` is a genuine NEAR-MISS that a different document -- or a
registry authored with E01's own role terms in it -- could turn into an actual
collision. What is falsified is the measurement offered in support, not the
design; same footing as section 8.9's on/until rows and section 2.4's
"6 segments, contained" claim.

Resolution here MIRRORS the production query deliberately, including its
asymmetry (section 21 R2):

    WHERE lower(canonical_name) = lower(:alias) OR :alias = ANY(aliases)

`canonical_name` is matched case-INsensitively; the `aliases` array is
matched case-SENSITIVELY. That asymmetry is a real trap -- an alias
registered in the wrong case silently fails to resolve -- so this module
reproduces it rather than being helpfully lenient. A lenient loader would
pass R5 locally and then fail against the real database, which is the exact
opposite of what R5 exists to do.

Ambiguity is reproduced too: more than one matching party returns None, not
a guess, matching symbols.resolve_party()'s `len(rows) != 1` rule.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REGISTRY_DIR = Path(__file__).resolve().parent.parent / "registry"


@dataclass(frozen=True)
class Party:
    canonical_name: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class DocumentRegistry:
    doc_id: str
    parties: tuple[Party, ...]

    def resolve(self, alias: str) -> Party | None:
        """Returns the single matching party, or None on no match or an
        ambiguous multi-match -- both of which leave a PartyRef UNRESOLVED
        in production."""
        matches = [
            p
            for p in self.parties
            if p.canonical_name.lower() == alias.lower() or alias in p.aliases
        ]
        return matches[0] if len(matches) == 1 else None


def load(doc_id: str) -> DocumentRegistry:
    path = REGISTRY_DIR / f"{doc_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"no scoring registry for document {doc_id!r} at {path}. "
            "Section 21 R3: the registry is an input to the harness and is committed "
            "with it; a published number without its registry is not reproducible."
        )
    raw = json.loads(path.read_text())
    return DocumentRegistry(
        doc_id=raw["doc_id"],
        parties=tuple(
            Party(canonical_name=p["canonical_name"], aliases=tuple(p["aliases"]))
            for p in raw["parties"]
        ),
    )


def load_all() -> dict[str, DocumentRegistry]:
    return {p.stem: load(p.stem) for p in sorted(REGISTRY_DIR.glob("*.json"))}
