"""PyMuPDF text/layout extraction for born-digital PDFs, plus the per-page
scanned/born-digital decision and dispatch to the Tesseract OCR path
(blueprint §11, §21 Phase 3). `unstructured` semantic section segmentation
and Celery/async wiring are still out of scope here -- see CLAUDE.md's
Phase 3 progress notes for what's deferred versus done. The OCR path itself
lives in obligo_brain.ingestion.loaders.ocr, not in this module -- this
file owns the per-page routing decision and the born-digital extraction
logic only.

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
comparison needs to verify after the fact. ocr.py's OCR path uses the
identical running-string mechanism -- see that module's docstring for the
one thing that changes when OCR is in the mix.

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

**Scanned-page detection.** Per page, not per document -- a "mixed" PDF
(some born-digital pages, some scanned) is a real case blueprint's own
acceptance criteria name, and a per-document decision couldn't handle it.
For each page, page.get_text("text") is called purely to measure how much
extractable text the page's own text layer holds -- this is a length
check only, never a source of offsets, so it doesn't reopen the
str.find()-trap the module docstring above warns about. >100 chars (a
number blueprint's own decision tree gives) means born-digital: run the
block-extraction path below. Otherwise the page is routed to
ocr.extract_ocr_page_segments -- either a true image-only scan, or a page
so text-sparse (a cover page, a stamp) that OCR is a safer default than
trusting a near-empty text layer.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from obligo_brain.ingestion.loaders import ocr as ocr_module
from obligo_brain.ingestion.loaders.segment import ExtractedSegment

__all__ = ["ExtractedSegment", "PdfExtractionError", "SCANNED_PAGE_CHAR_THRESHOLD", "extract_segments"]

SCANNED_PAGE_CHAR_THRESHOLD = 100
"""Blueprint's own number (§11 decision tree): a page whose PyMuPDF text
layer holds this many characters or fewer is treated as scanned/image-only
rather than born-digital, and routed to OCR instead of block extraction."""


class PdfExtractionError(RuntimeError):
    """Raised when PyMuPDF cannot parse the given bytes as a PDF.

    The trust-boundary point for this module: pdf_bytes originates from
    storage but ultimately traces back to an untrusted upload. Native-library
    exceptions from fitz.open() are caught here and re-raised as this typed
    error rather than left to propagate as opaque RuntimeErrors.
    """


def extract_segments(pdf_bytes: bytes) -> list[ExtractedSegment]:
    """Extract layout-aware segments with exact, page-relative character
    offsets from a PDF's raw bytes, routing each page independently to
    either the PyMuPDF text-layer path or the Tesseract OCR path (see
    module docstring's "Scanned-page detection" section).
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

            # Length check only -- never a source of offsets. See module
            # docstring for why this doesn't reopen the str.find() trap.
            text_layer_length = len(page.get_text("text").strip())

            if text_layer_length > SCANNED_PAGE_CHAR_THRESHOLD:
                page_segments, ordinal = _extract_text_layer_page(page, page_number, ordinal)
            else:
                page_segments, ordinal = ocr_module.extract_ocr_page_segments(page, page_number, ordinal)

            segments.extend(page_segments)
    finally:
        doc.close()

    return segments


def _extract_text_layer_page(
    page: fitz.Page, page_number: int, ordinal: int
) -> tuple[list[ExtractedSegment], int]:
    """One segment per non-empty PyMuPDF text block on this page. sort=True
    asks PyMuPDF to order blocks top-to-bottom, then left-to-right, which
    improves reading order for common single-column and simple layouts but
    is not a true multi-column reading-order solver -- see module
    docstring. Returns the page's segments and the ordinal to continue from
    for the next page.
    """
    blocks = page.get_text("blocks", sort=True)

    segments: list[ExtractedSegment] = []
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
                ocr_confidence=None,
            )
        )
        ordinal += 1

    return segments, ordinal
