"""Acquires, verifies, and profiles the 28-document Tier-2 gold-set corpus.

`docs/eval/corpus_manifest.json` records 28 documents with their SHA-256
hashes and a set of per-document density statistics, and
`docs/eval/GOLD_SET_GUIDELINE.md` reasons from those statistics in four
separate places (its selection-bias audit in section 13, and the
vague-temporal, efforts-qualifier, and internal-boolean rules in sections
15-17). Both files were committed. The corpus they describe was not, and
neither was the code that produced any of those numbers -- the documents
lived only in a session scratchpad, which is deleted between sessions.

The consequence, found when this script was written: the hashes could be
checked against a re-download, but every derived statistic in both files
was unreproducible. There was no script to re-run and no written
definition of what "a modal sentence" or "a fronted clause" even meant, so
a reader could neither confirm the numbers nor recompute them after a
corpus change.

This script closes that gap in both directions. `fetch` and `verify`
re-acquire the exact 28 documents from their archival sources and check
every byte against the manifest. `profile` recomputes every derived
statistic from an explicit, readable definition -- the definitions in
`METRICS` below are now the specification, where previously there was
none.

Deliberately stdlib-only apart from importing this repo's own compiler.
CLAUDE.md requires asking before adding a dependency, and nothing here
needs one: EDGAR's HTML is stripped with `html.parser` rather than
BeautifulSoup, which is not a current dependency of apps/brain.

On the authority of these numbers, stated plainly rather than implied.
The metric definitions here are a *reconstruction*. The original
definitions were never written down, so where a recomputed number differs
from the manifest's, that difference is genuinely ambiguous between "the
manifest was wrong" and "this script defines the metric differently" --
`profile --compare` reports the delta and does not adjudicate it. Only the
hash verification is unambiguous. The one statistic that is better than a
reconstruction is the WITHIN classification, which is measured against
`ir_compile._WITHIN_RE` itself -- the real production regex, imported, not
a proxy for it -- so `within_parenthetical` is a direct measurement of
what the compiler actually rejects rather than an estimate of it.

Usage:

    uv run --project apps/brain python apps/brain/evals/corpus.py fetch
    uv run --project apps/brain python apps/brain/evals/corpus.py verify
    uv run --project apps/brain python apps/brain/evals/corpus.py profile --compare

`fetch` writes to `--dest` (default `.corpus/`, gitignored). The CUAD
download is a 106 MB zip; it is cached and not re-downloaded when the
cached copy already matches `CUAD_ZIP_SHA256`.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import statistics
import sys
import time
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "docs" / "eval" / "corpus_manifest.json"
DEFAULT_DEST = REPO_ROOT / ".corpus"

sys.path.insert(0, str(REPO_ROOT / "apps" / "brain" / "src"))

# The real production regex, imported rather than reimplemented. This is
# what makes `within_bare`/`within_parenthetical` a measurement of the
# compiler's actual behaviour instead of a hand-written approximation of
# it: a WITHIN phrase counts as "bare" here if and only if the classifier
# that runs in `run_pipeline()` would accept its numeral.
from obligo_brain.compiler.ir_compile import _UNIT_ALTERNATION, _WITHIN_RE  # noqa: E402

# CUAD v1, The Atticus Project. Zenodo DOI 10.5281/zenodo.4595826.
# License verified against the Zenodo record's own metadata on 2026-08-18:
# `"license": {"id": "cc-by-4.0"}`. CC BY 4.0 permits redistribution with
# attribution, which is what `docs/eval/GOLD_SET_GUIDELINE.md` section 12
# records and what any published eval number must carry.
CUAD_ZENODO_URL = "https://zenodo.org/api/records/4595826/files/CUAD_v1.zip/content"
CUAD_ZIP_SHA256 = "88b694d99007d39777fa44cd72daf8297773d285dc3eab0091ba32078888d18e"
CUAD_ZIP_BYTES = 105883672

# SEC requires a User-Agent identifying the requester, and rate-limits to
# 10 requests/second. Six documents at 0.4s apart is far inside that.
EDGAR_USER_AGENT = "Obligo Research rajitagrawal2005@gmail.com"
EDGAR_DELAY_SECONDS = 0.4


# --------------------------------------------------------------------------
# Metric definitions
# --------------------------------------------------------------------------
#
# These are the specification. Every number in `corpus_manifest.json` and
# every frequency the guideline cites is produced by exactly this code.
#
# Everything is counted over *modal sentences*, not all sentences: a
# contract's recitals, definitions, and signature blocks carry no
# obligations, and including them would deflate every density figure by a
# factor that varies with how definition-heavy a given contract is.

_MODAL_RE = re.compile(r"\b(?:shall|must|will|may|should)\b", re.IGNORECASE)

# A deadline expression, not merely any mention of time. "The Term begins
# on January 1" is a date reference; it is not an obligation deadline, and
# counting it would make `temporal` a measure of how often contracts
# mention dates rather than how often obligations carry deadlines.
_TEMPORAL_RE = re.compile(
    r"\bwithin\s+[^,;.]{1,40}?\b(?:" + _UNIT_ALTERNATION + r")\b"
    r"|\bno\s+later\s+than\b"
    r"|\bnot\s+later\s+than\b"
    r"|\bon\s+or\s+before\b"
    r"|\bprior\s+to\s+the\s+\w+\s+(?:date|deadline)\b"
    r"|\bevery\s+[^,;.]{1,30}?\b(?:" + _UNIT_ALTERNATION + r")\b"
    r"|\bby\s+(?:no\s+later\s+than\s+)?\d{4}-\d{2}-\d{2}\b"
    r"|\bby\s+the\s+\w+\s+(?:anniversary|day|date)\b",
    re.IGNORECASE,
)

# A subordinate clause fronting the main clause -- the exact shape that
# produced the grounding bug fixed by `prompts/extraction/v2.yaml`. The
# comma requirement is what distinguishes a genuinely fronted clause
# ("If X occurs, Vendor shall...") from a sentence that merely opens with
# one of these words ("Notwithstanding anything herein Vendor shall...").
_FRONTED_RE = re.compile(
    r"^\s*(?:if|when|whenever|while|where|unless|until|upon|during|after|before|"
    r"following|subject\s+to|notwithstanding|in\s+the\s+event|provided\s+that|"
    r"except|to\s+the\s+extent|as\s+soon\s+as|prior\s+to|should)\b[^,]{0,200},",
    re.IGNORECASE,
)

# A cross-reference out of the segment. Guideline section 2 excludes
# cross-reference-dependent segments as unannotatable at segment scope, so
# this rate predicts how much of a document is unusable for gold items --
# which is precisely why section 13's bias audit turns on it.
_XREF_RE = re.compile(
    r"\b(?:section|article|exhibit|schedule|appendix|annex|clause)\s+"
    r"(?:\d+|[ivxlc]+\b|[A-Z]\b)"
    r"|\bset\s+forth\s+in\b"
    r"|\bas\s+(?:described|defined|provided|referred\s+to)\s+in\b",
    re.IGNORECASE,
)

# Every WITHIN deadline, however its numeral is written. Classification
# into bare/parenthetical is then delegated to the real `_WITHIN_RE`.
_WITHIN_PHRASE_RE = re.compile(
    r"\bwithin\s+([^,;.]{1,60}?)\s*\b(" + _UNIT_ALTERNATION + r")\b",
    re.IGNORECASE,
)

# Guideline section 15. Counted over modal sentences that carry no
# quantified deadline at all, since a sentence with both a vague qualifier
# and a real deadline is not the case that rule governs.
_VAGUE_TEMPORAL_RE = re.compile(
    r"\b(?:promptly|immediately|timely|as\s+soon\s+as\s+(?:practicable|possible)|"
    r"without\s+(?:undue\s+)?delay|expeditiously|forthwith)\b",
    re.IGNORECASE,
)

# Guideline section 16. The form that matched two rows of the v0.4
# modality table at once.
_EFFORTS_RE = re.compile(
    r"\b(?:reasonable|best|commercially\s+reasonable|good\s+faith)\s+efforts\b",
    re.IGNORECASE,
)

METRICS = (
    "modal_sentences",
    "temporal",
    "fronted_clause",
    "xref_pct",
    "p90_len",
    "paren",
    "bare",
)

# Sentence-splitting guards. A period after any of these is an
# abbreviation, not a sentence boundary -- "Acme Corp. shall deliver" is
# one sentence, and splitting it would both inflate the sentence count and
# truncate the obligation.
_ABBREVIATIONS = frozenset(
    """inc llc ltd corp co plc lp llp no nos art sec secs cf eg ie vs etc al
    mr mrs ms dr jr sr st approx dept est fig ref vol pp ch para u.s u.k""".split()
)


def split_sentences(text: str) -> list[str]:
    """Splits into sentences, guarding the abbreviations legal text is full of.

    Deliberately conservative: it is better to under-split (leaving two
    sentences joined) than to over-split, because a truncated sentence
    loses the modal or the deadline that the metrics count.
    """
    text = re.sub(r"\s+", " ", text)
    out: list[str] = []
    start = 0
    for match in re.finditer(r"[.!?][\"')\]]?\s+", text):
        head = text[start : match.start()]
        last = re.search(r"(\S+)$", head)
        if last:
            token = last.group(1).lower().strip("([\"'")
            if token in _ABBREVIATIONS:
                continue
            # A single initial ("J. Smith") or a numbered heading
            # ("Section 12.") -- neither ends a sentence.
            if re.fullmatch(r"[a-z]", token) or re.fullmatch(r"\d+(?:\.\d+)*", token):
                continue
        sentence = text[start : match.end()].strip()
        if sentence:
            out.append(sentence)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def classify_within(sentence: str) -> tuple[int, int]:
    """Returns (bare, parenthetical) WITHIN-deadline counts for one sentence.

    "Bare" means `_WITHIN_RE` -- the actual classifier in
    `compiler/ir_compile.py` -- accepts the numeral. "Parenthetical" means
    it does not, which in this corpus is overwhelmingly the
    `within thirty (30) days` form the guideline's section 8 names as a
    known v1 gap. Measuring against the imported regex rather than a
    lookalike is what makes this number decision-grade: it is what the
    compiler does, not what this script thinks the compiler does.
    """
    bare = parenthetical = 0
    for match in _WITHIN_PHRASE_RE.finditer(sentence):
        numeral, unit = match.group(1).strip(), match.group(2)
        # `_WITHIN_RE` is anchored and requires a trailing "of <trigger>";
        # the deadline phrases counted here are extracted mid-sentence, so
        # a minimal well-formed probe is reconstructed to ask the real
        # regex the one question that matters: does it accept this numeral?
        if _WITHIN_RE.match(f"within {numeral} {unit} of X"):
            bare += 1
        else:
            parenthetical += 1
    return bare, parenthetical


def profile_text(text: str) -> dict[str, object]:
    """Computes every manifest statistic for one document's extracted text."""
    sentences = split_sentences(text)
    modal = [s for s in sentences if _MODAL_RE.search(s)]

    temporal = sum(1 for s in modal if _TEMPORAL_RE.search(s))
    fronted = sum(1 for s in modal if _FRONTED_RE.search(s))
    xref = sum(1 for s in modal if _XREF_RE.search(s))

    bare = parenthetical = 0
    for sentence in modal:
        b, p = classify_within(sentence)
        bare += b
        parenthetical += p

    vague = sum(
        1
        for s in modal
        if _VAGUE_TEMPORAL_RE.search(s) and not _TEMPORAL_RE.search(s)
    )
    efforts = sum(1 for s in modal if _EFFORTS_RE.search(s))

    lengths = sorted(len(s) for s in modal)
    p90 = (
        int(statistics.quantiles(lengths, n=10)[-1]) if len(lengths) >= 10 else (lengths[-1] if lengths else 0)
    )

    return {
        "sentences": len(sentences),
        "modal_sentences": len(modal),
        "temporal": temporal,
        "fronted_clause": fronted,
        "xref_pct": round(100 * xref / len(modal)) if modal else 0,
        "p90_len": p90,
        "paren": parenthetical,
        "bare": bare,
        "vague_temporal": vague,
        "efforts": efforts,
    }


class _TextExtractor(HTMLParser):
    """Strips EDGAR HTML to text, preserving block structure.

    EDGAR exhibits are largely `<p>`/`<div>`/table markup around ordinary
    prose. Dropping tags without inserting boundaries would weld the end of
    one paragraph onto the start of the next and manufacture sentences that
    do not exist.
    """

    _BLOCKS = frozenset(
        "p div br tr td th li h1 h2 h3 h4 h5 h6 table blockquote".split()
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self._BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in self._BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)

    def text(self) -> str:
        joined = html.unescape("".join(self.parts))
        joined = joined.replace("\xa0", " ")
        return re.sub(r"\n{2,}", "\n", joined)


def extract_text(raw: bytes, kind: str) -> str:
    """CUAD ships plain text; EDGAR ships HTML that must be stripped first."""
    decoded = raw.decode("utf-8", errors="replace")
    if kind == "edgar":
        parser = _TextExtractor()
        parser.feed(decoded)
        return parser.text()
    return decoded


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download(url: str, headers: dict[str, str] | None = None) -> bytes:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def cmd_fetch(dest: Path) -> int:
    """Re-acquires all 28 documents from Zenodo and SEC EDGAR."""
    manifest = load_manifest()
    (dest / "cuad").mkdir(parents=True, exist_ok=True)
    (dest / "edgar").mkdir(parents=True, exist_ok=True)

    zip_path = dest / "CUAD_v1.zip"
    if zip_path.exists() and _sha256(zip_path.read_bytes()) == CUAD_ZIP_SHA256:
        print(f"fetch: CUAD_v1.zip already cached and verified ({CUAD_ZIP_BYTES} bytes)")
    else:
        print(f"fetch: downloading CUAD_v1.zip ({CUAD_ZIP_BYTES} bytes) from Zenodo...")
        blob = _download(CUAD_ZENODO_URL)
        got = _sha256(blob)
        if got != CUAD_ZIP_SHA256:
            print(f"fetch: FAILED -- CUAD zip hash mismatch\n  got {got}\n  exp {CUAD_ZIP_SHA256}")
            return 1
        zip_path.write_bytes(blob)
        print("fetch: CUAD_v1.zip downloaded and hash-verified")

    with zipfile.ZipFile(zip_path) as archive:
        by_name = {
            Path(n).name: n
            for n in archive.namelist()
            if n.lower().endswith(".txt") and "full_contract_txt" in n
        }
        for doc in manifest["documents"]["cuad"]:
            member = by_name.get(doc["filename"])
            if member is None:
                print(f"fetch: FAILED -- {doc['id']} not in zip: {doc['filename']}")
                return 1
            (dest / "cuad" / f"{doc['id']}.txt").write_bytes(archive.read(member))
    print(f"fetch: extracted {len(manifest['documents']['cuad'])} CUAD documents")

    for doc in manifest["documents"]["edgar"]:
        blob = _download(doc["url"], {"User-Agent": EDGAR_USER_AGENT})
        (dest / "edgar" / f"{doc['id']}.htm").write_bytes(blob)
        time.sleep(EDGAR_DELAY_SECONDS)
    print(f"fetch: downloaded {len(manifest['documents']['edgar'])} EDGAR documents")
    return cmd_verify(dest)


def _doc_path(dest: Path, kind: str, doc_id: str) -> Path:
    return dest / kind / (f"{doc_id}.txt" if kind == "cuad" else f"{doc_id}.htm")


def _iter_docs(manifest: dict) -> Iterable[tuple[str, dict]]:
    for kind in ("cuad", "edgar"):
        for doc in manifest["documents"][kind]:
            yield kind, doc


def cmd_verify(dest: Path) -> int:
    """Checks all 28 documents byte-for-byte against the manifest's hashes.

    This is the unambiguous half of the script. A pass means the corpus on
    disk is exactly the corpus the manifest describes; there is no
    interpretation involved and no reconstructed definition in play.
    """
    manifest = load_manifest()
    failures = 0
    for kind, doc in _iter_docs(manifest):
        path = _doc_path(dest, kind, doc["id"])
        if not path.exists():
            print(f"verify: {doc['id']}  MISSING ({path}) -- run `fetch` first")
            failures += 1
            continue
        raw = path.read_bytes()
        if _sha256(raw) != doc["sha256"] or len(raw) != doc["bytes"]:
            print(f"verify: {doc['id']}  MISMATCH\n  got {_sha256(raw)} ({len(raw)} bytes)\n  exp {doc['sha256']} ({doc['bytes']} bytes)")
            failures += 1
    total = sum(1 for _ in _iter_docs(manifest))
    if failures:
        print(f"verify: FAILED -- {failures} of {total} documents do not match the manifest")
        return 1
    print(f"verify: {total} documents, all hashes match the manifest.")
    return 0


def cmd_profile(dest: Path, compare: bool, write: Path | None) -> int:
    """Recomputes every derived statistic, optionally diffing the manifest."""
    manifest = load_manifest()
    results: dict[str, dict] = {}
    pooled: dict[str, int] = {
        "modal_sentences": 0,
        "temporal": 0,
        "fronted_clause": 0,
        "paren": 0,
        "bare": 0,
        "vague_temporal": 0,
        "efforts": 0,
        "xref_sentences": 0,
    }

    for kind, doc in _iter_docs(manifest):
        path = _doc_path(dest, kind, doc["id"])
        if not path.exists():
            print(f"profile: FAILED -- {doc['id']} missing; run `fetch` first")
            return 1
        stats = profile_text(extract_text(path.read_bytes(), kind))
        results[doc["id"]] = stats
        for key in ("modal_sentences", "temporal", "fronted_clause", "paren", "bare", "vague_temporal", "efforts"):
            pooled[key] += int(stats[key])
        pooled["xref_sentences"] += round(int(stats["xref_pct"]) * int(stats["modal_sentences"]) / 100)

    xref_values = sorted(int(s["xref_pct"]) for s in results.values())
    totals = {
        "documents": len(results),
        "modal_sentences": pooled["modal_sentences"],
        "temporal": pooled["temporal"],
        "fronted_clause": pooled["fronted_clause"],
        "median_xref_pct": int(statistics.median(xref_values)),
        "pooled_xref_pct": round(100 * pooled["xref_sentences"] / pooled["modal_sentences"]),
        "within_bare": pooled["bare"],
        "within_parenthetical": pooled["paren"],
        "vague_temporal": pooled["vague_temporal"],
        "efforts": pooled["efforts"],
    }

    within_total = totals["within_bare"] + totals["within_parenthetical"]
    print(f"profile: {len(results)} documents, {totals['modal_sentences']} modal sentences")
    print(f"profile: WITHIN deadlines: {within_total} total, "
          f"{totals['within_parenthetical']} parenthetical "
          f"({round(100 * totals['within_parenthetical'] / within_total) if within_total else 0}%), "
          f"{totals['within_bare']} bare")

    if write:
        write.write_text(json.dumps({"documents": results, "totals": totals}, indent=2) + "\n")
        print(f"profile: wrote {write}")

    if compare:
        print("\nprofile --compare: recomputed vs manifest (per document)")
        print(f"{'doc':<5} " + " ".join(f"{m:>16}" for m in METRICS))
        diffs = 0
        for kind, doc in _iter_docs(manifest):
            stats = results[doc["id"]]
            cells = []
            for metric in METRICS:
                got, exp = int(stats[metric]), int(doc[metric])
                cells.append(f"{got:>7}/{exp:<8}" if got != exp else f"{got:>7} {'=':<8}")
                if got != exp:
                    diffs += 1
            print(f"{doc['id']:<5} " + " ".join(cells))
        print("\n(recomputed/manifest where they differ, '=' where identical)")
        print(f"totals: {json.dumps(totals)}")
        print(f"manifest totals: {json.dumps(manifest['totals'])}")
        print(f"\n{diffs} of {len(results) * len(METRICS)} per-document values differ.")
        print("A difference is NOT by itself evidence the manifest was wrong: the original")
        print("metric definitions were never committed, so a delta is ambiguous between a")
        print("bad prior number and a differing definition here. Only the hash check in")
        print("`verify` is unambiguous.")
    return 0


def enumerate_pool(text: str) -> list[str]:
    """Enumerates candidate gold segments per guideline section 2.1's filter.

    Section 2.1 is explicit that this step carries no judgment: the drafter
    "mechanically enumerates every segment meeting the formal criteria --
    length band, modal presence. No judgment, just the filter." Only the
    two mechanical criteria are applied here. The semantic exclusions in
    section 2 (definitions, recitals, cross-reference-dependent, rights
    without a correlative duty) are annotator decisions made per segment
    with a logged reason, and deliberately are NOT guessed at by this code
    -- doing so would quietly move a judgment the guideline assigns to a
    human into an unreviewable regex.

    Blocks are the document's own paragraph structure. A block over the
    2,000-character ceiling is not sentence-chunked into compliant pieces:
    where to cut it is exactly the hand-cutting decision section 2 reserves
    for the annotator.
    """
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\s*\n|\n", text)]
    return [
        b
        for b in blocks
        if 200 <= len(b) <= 2000 and _MODAL_RE.search(b)
    ]


def cmd_pool(dest: Path) -> int:
    """Recomputes the eligible-segment pool and its section 15-17 frequencies.

    The guideline's vague-temporal (section 15), efforts-qualifier
    (section 16), and internal-boolean (section 17) rules each cite a
    frequency over a "960-segment eligible pool" that was never
    reproducible. This rebuilds the pool from section 2.1's stated filter
    and recounts each.
    """
    manifest = load_manifest()
    pool: list[str] = []
    for kind, doc in _iter_docs(manifest):
        path = _doc_path(dest, kind, doc["id"])
        if not path.exists():
            print(f"pool: FAILED -- {doc['id']} missing; run `fetch` first")
            return 1
        pool.extend(enumerate_pool(extract_text(path.read_bytes(), kind)))

    vague = [s for s in pool if _VAGUE_TEMPORAL_RE.search(s)]
    vague_only = [s for s in vague if not _TEMPORAL_RE.search(s)]
    efforts = [s for s in pool if _EFFORTS_RE.search(s)]
    # Section 17: two or more conditions chained inside one clause.
    chained = [
        s
        for s in pool
        if re.search(r"\bif\b[^.]{0,200}\b(?:and\s+if|or\s+if)\b", s, re.IGNORECASE)
    ]

    print(f"pool: {len(pool)} eligible segments (guideline section 2.1 filter: 200-2000 chars, modal present)")
    print(f"pool: vague temporal qualifier            {len(vague)} ({round(100*len(vague)/len(pool))}%)")
    print(f"pool:   ...of which no quantified deadline {len(vague_only)}")
    print(f"pool: efforts qualifier                   {len(efforts)} ({round(100*len(efforts)/len(pool))}%)")
    print(f"pool: chained conditions in one clause    {len(chained)}")
    print()
    print("Guideline claims for comparison -- section 15: 960-segment pool, 111 vague (12%),")
    print("80 with no quantified form; section 16: 28 efforts (3%); section 17: 2 chained (0.2%).")
    print("Same ambiguity as `profile --compare`: the original pool construction was never")
    print("committed, so a delta does not by itself convict either number.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("fetch", "verify", "profile", "pool"))
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--compare", action="store_true", help="profile: diff against the manifest")
    parser.add_argument("--write", type=Path, default=None, help="profile: write recomputed JSON here")
    args = parser.parse_args(argv)

    if args.command == "fetch":
        return cmd_fetch(args.dest)
    if args.command == "verify":
        return cmd_verify(args.dest)
    if args.command == "pool":
        return cmd_pool(args.dest)
    return cmd_profile(args.dest, args.compare, args.write)


if __name__ == "__main__":
    raise SystemExit(main())
