"""ExtractedSegment lives in its own module, not in pdf.py or ocr.py,
specifically to avoid a circular import: pdf.py routes scanned pages to
ocr.py, and ocr.py needs the same segment shape pdf.py's text-layer path
produces -- both modules import it from here instead of one importing it
from the other.
"""

from __future__ import annotations

from dataclasses import dataclass


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
    """Offset into this page's canonical reconstructed text at which this
    segment's text begins. Built identically by pdf.py's text-layer path
    and ocr.py's OCR path -- see both modules' docstrings."""

    char_end: int
    """Offset at which this segment's text ends. char_end > char_start
    always -- empty blocks/words are filtered out before a segment is
    emitted."""

    text: str
    """The segment's exact extracted text. Defining property:
    page_canonical_text[char_start:char_end] == text -- see pdf.py and
    ocr.py module docstrings for what "exact" means differently on the two
    extraction paths."""

    ocr_confidence: float | None
    """None for a PyMuPDF text-layer segment (V14's NULL-means-born-digital
    convention). For an OCR segment, the block's minimum per-word Tesseract
    confidence (0-100) -- min, not mean, so one badly-misread word in an
    otherwise-confident block still surfaces as low confidence rather than
    being averaged out. See ocr.py for why min was chosen over mean."""
