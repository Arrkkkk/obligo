"""PyMuPDF text/layout extraction for born-digital PDFs (blueprint §11, §21
Phase 3). OCR (scanned pages), `unstructured` semantic section segmentation,
and Celery/async wiring are all explicitly out of scope for this module --
see CLAUDE.md's Phase 3 progress notes for what's deferred versus done.

Offsets are derived by construction, not by post-hoc comparison. The naive
approach -- call page.get_text("text") for the page's full text, separately
call page.get_text("blocks") for per-block text, then str.find() each
block's text inside the full text -- is a trap: the two extraction modes
aren't guaranteed to concatenate identically, and str.find() silently
returns the *first* match, so a repeated phrase (a defined term, a table
header) can get a wrong offset with no error at all.

Instead, this module builds each page's "canonical text" and every
segment's (char_start, char_end) in a single pass: get_text("blocks") is
called once per page, and as each non-empty text block is appended to a
running per-page string, char_start/char_end are read directly off that
string's length before and after the append. The persisted text *is* what
produced the offsets -- `page_text[char_start:char_end] == segment.text`
holds because of how the values were computed, not as something a
comparison needs to verify after the fact.

Two consequences worth being explicit about:
- (page, char_start, char_end) is page-relative, not document-global --
  matches blueprint's own column layout (page and char_start/end as
  siblings) and avoids ever having to define a cross-page join convention.
- Round-trip correctness (offsets point at the right text) is guaranteed by
  construction. Reading-order correctness (segments appear in visually
  sensible order) is NOT fully guaranteed for genuinely multi-column
  layouts -- PyMuPDF's block ordering (even with sort=True, used below) is
  position-heuristic, and true column-aware reading-order reconstruction is
  an open problem, not something this module solves. A block-ordering
  oddity on a multi-column fixture is an expected, named limitation, not a
  bug -- the offsets for whatever order it does produce are still exact.
"""

from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF


class PdfExtractionError(RuntimeError):
    """Raised when PyMuPDF cannot parse the given bytes as a PDF.

    The trust-boundary point for this module: pdf_bytes originates from
    storage but ultimately traces back to an untrusted upload. Native-library
    exceptions from fitz.open() are caught here and re-raised as this typed
    error rather than left to propagate as opaque RuntimeErrors.
    """


@dataclass(frozen=True)
class ExtractedSegment:
    ordinal: int
    """0-indexed position in document-wide extraction order. Unique per
    source alongside source_id -- matches the segments table's
    UNIQUE (source_id, ordinal) constraint (V13)."""

    page: int
    """1-indexed page number. PyMuPDF's own page.number is 0-indexed;
    converted here so it matches how a human -- or a future citation UI --
    refers to "page 3", not PyMuPDF's internal convention."""

    char_start: int
    """Offset into this page's canonical reconstructed text (see module
    docstring) at which this segment's text begins."""

    char_end: int
    """Offset at which this segment's text ends. char_end > char_start
    always -- empty blocks are filtered out before a segment is emitted."""

    text: str
    """The segment's exact extracted text. Defining property:
    page_canonical_text[char_start:char_end] == text."""


def extract_segments(pdf_bytes: bytes) -> list[ExtractedSegment]:
    """Extract layout-aware segments with exact, page-relative character
    offsets from a born-digital PDF's raw bytes.

    One segment per non-empty PyMuPDF text block. sort=True asks PyMuPDF to
    order blocks top-to-bottom, then left-to-right, which improves reading
    order for common single-column and simple layouts but is not a true
    multi-column reading-order solver -- see module docstring.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:  # fitz raises assorted RuntimeError subclasses
        raise PdfExtractionError(f"PyMuPDF could not open the given bytes as a PDF: {e}") from e

    segments: list[ExtractedSegment] = []
    ordinal = 0
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_number = page_index + 1
            blocks = page.get_text("blocks", sort=True)

            running_page_text = ""
            for block in blocks:
                block_type = block[6]
                if block_type != 0:  # 0 = text block, 1 = image block
                    continue

                block_text = block[4].strip("\n")
                if not block_text:
                    continue

                if running_page_text:
                    running_page_text += "\n"
                char_start = len(running_page_text)
                running_page_text += block_text
                char_end = len(running_page_text)

                segments.append(
                    ExtractedSegment(
                        ordinal=ordinal,
                        page=page_number,
                        char_start=char_start,
                        char_end=char_end,
                        text=block_text,
                    )
                )
                ordinal += 1
    finally:
        doc.close()

    return segments
