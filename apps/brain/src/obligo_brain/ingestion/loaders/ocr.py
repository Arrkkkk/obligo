"""Tesseract OCR extraction for scanned/image-only pages (blueprint §11,
§21 Phase 3). pdf.py decides, per page, whether a page is born-digital or
scanned (see that module's "Scanned-page detection" docstring section) and
calls extract_ocr_page_segments here for the scanned ones.

**Engine choice, and why it diverges from blueprint's own §13.3 default:**
blueprint names PaddleOCR (PP-OCRv4) as the default OCR engine, with a
flagged caveat that PaddlePaddle's ARM64 wheels were unreliable and that
non-x86 dev hardware should "fall back to Tesseract." This codebase's local
dev machine is Apple Silicon (arm64) -- see CLAUDE.md's tech-choices table
for the full reasoning, verified live rather than assumed: PaddlePaddle now
ships official macOS arm64 wheels (3.3.1+), so the wheel-availability
problem blueprint flagged is gone, but real, current (2025-2026) GitHub
issues still show PaddleOCR segfaulting/freezing on M1-M3 Macs specifically
-- a native-inference-engine stability class, not a packaging one, that
wheel availability doesn't fix. Tesseract is used here as the dev-only
engine per blueprint's own stated fallback; PaddleOCR remains the plan for
the x86 Hetzner production target, matching how blueprint always said "on
x86 Hetzner, PaddleOCR is fine." Revisit at Phase 9 deployment, same
"decided for the current deployment shape only" framing as the PyMuPDF/AGPL
note elsewhere in CLAUDE.md -- do not read this as a permanent engine
choice.

**The one thing that changes vs. pdf.py's text-layer path, stated as
plainly as that module's own reading-order caveat:** pdf.py's offsets are
exact against the PDF's own embedded text layer -- ground truth, by
definition, because PyMuPDF is reading bytes the PDF itself declares as
text. This module's offsets are exact against Tesseract's OWN RECOGNITION
OUTPUT, not against the physical page. The running-string construction
mechanism is identical (char_start/char_end are read off a running per-page
string's length before/after each block is appended, so `page_text[
char_start:char_end] == text` holds by construction, not by post-hoc
comparison) -- but what "exact" is exact *to* is different. A misread word
is still round-trip exact; it is round-trip exact to the wrong text. This
is why ocr_confidence exists and must be surfaced per segment rather than
trusted the way PyMuPDF text is -- see V14's own migration comment and the
segments.ocr_confidence column comment for the same point stated a third
time, deliberately, where a future reader querying the table will actually
see it.

**Confidence aggregation: MIN across a block's words, not mean.**
Averaging would let one badly-misread word (a date, a party name, a
dollar figure -- exactly the tokens a contradiction-detecting system cares
about) get diluted into a passing score by a few high-confidence words
around it. A single wrong word in a defined term is a real correctness
failure for this project's whole thesis, not noise to be smoothed over --
so the block's reported confidence is its worst word, not its average one.

**Block grouping.** Tesseract's image_to_data returns a flat, five-level
hierarchy (page/block/par/line/word) per recognized element. Segments here
are grouped by Tesseract's own block_num, the closest analog to PyMuPDF's
per-block granularity on the text-layer path. Words within a block are
joined with a single space regardless of which line they were on --
a stated simplification, not an attempt at a full layout reconstruction.
Block order is Tesseract's own array order (first-seen block_num order),
which is a position heuristic, not a true reading-order solver -- the same
caveat pdf.py's module docstring already states for PyMuPDF's sort=True,
now true of this path too, for the same underlying reason (no OCR engine
used here does column-aware reading-order reconstruction).
"""

from __future__ import annotations

import pytesseract
from PIL import Image

import fitz  # PyMuPDF

from obligo_brain.ingestion.loaders.segment import ExtractedSegment

RASTERIZE_DPI = 300
"""Blueprint's own number for the rasterize-then-OCR decision tree."""

LOW_OCR_CONFIDENCE_THRESHOLD = 60.0
"""A documented judgment call, not a validated number -- Tesseract's
confidence scale is 0-100 with no universal "safe" cutoff; 60 is a common
rule-of-thumb floor in OCR pipelines generally. Revisit once real OCR
output volume exists to calibrate against, the same "decided now, revisit
with evidence" posture as this project's other placeholder thresholds.
Segments below this are not excluded from persistence -- they are
persisted with their real (low) confidence and left for a consumer to
filter, matching blueprint's "flagged ... and excluded from binding
extraction, surfaced to the user, not silently used." Nothing in this
phase yet does "binding extraction" (that's Phase 4's compiler) -- so
is_low_confidence() below is the flagging primitive a future consumer
calls, not a persisted boolean or a filter applied here."""


class OcrExtractionError(RuntimeError):
    """Raised when Tesseract cannot be invoked or fails unexpectedly on a
    rasterized page. Distinct from PdfExtractionError (pdf.py) -- this is a
    failure of the OCR engine/binary, not of PyMuPDF's own PDF parsing.
    """


def is_low_confidence(segment: ExtractedSegment) -> bool:
    """True for an OCR segment whose (min-of-block) confidence falls below
    LOW_OCR_CONFIDENCE_THRESHOLD. Always False for a PyMuPDF text-layer
    segment (ocr_confidence is None there) -- confidence flagging only
    applies to hypotheses, and text-layer segments aren't hypotheses.
    """
    return segment.ocr_confidence is not None and segment.ocr_confidence < LOW_OCR_CONFIDENCE_THRESHOLD


def extract_ocr_page_segments(
    page: fitz.Page, page_number: int, ordinal: int, dpi: int = RASTERIZE_DPI
) -> tuple[list[ExtractedSegment], int]:
    """OCR a single page and return its segments plus the ordinal to
    continue from for the next page -- same (segments, next_ordinal)
    contract as pdf.py's _extract_text_layer_page, so pdf.py's per-page
    loop can call either path interchangeably.
    """
    image = _rasterize_page(page, dpi)

    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractError as e:
        raise OcrExtractionError(f"Tesseract failed to process page {page_number}: {e}") from e
    except pytesseract.TesseractNotFoundError as e:
        raise OcrExtractionError(
            "Tesseract binary not found -- install via `brew install tesseract` for local dev"
        ) from e

    # Group word-level entries (level 5) by block_num, preserving first-seen
    # order (a plain dict's insertion order) -- this is Tesseract's own
    # array order, i.e. its own position-heuristic reading order. Level 5
    # words carry the real per-word text and confidence; levels 1-4 are
    # structural (page/block/par/line) markers with conf == -1, not real
    # recognition confidences, and are skipped entirely.
    word_indices_by_block: dict[int, list[int]] = {}
    for i, level in enumerate(data["level"]):
        if level != 5:
            continue
        word_text = data["text"][i].strip()
        if not word_text:
            continue
        block_num = data["block_num"][i]
        word_indices_by_block.setdefault(block_num, []).append(i)

    segments: list[ExtractedSegment] = []
    running_page_text = ""
    for indices in word_indices_by_block.values():
        words = [data["text"][i].strip() for i in indices]
        block_text = " ".join(w for w in words if w)
        if not block_text:
            continue

        word_confidences = [float(data["conf"][i]) for i in indices if float(data["conf"][i]) >= 0]
        block_confidence = min(word_confidences) if word_confidences else 0.0

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
                ocr_confidence=block_confidence,
            )
        )
        ordinal += 1

    return segments, ordinal


def _rasterize_page(page: fitz.Page, dpi: int) -> Image.Image:
    """Render via PyMuPDF's own get_pixmap rather than adding a second
    rasterization dependency (pdf2image/poppler) -- PyMuPDF is already a
    dependency of this codebase and this is the only rasterization this
    project needs.
    """
    pix = page.get_pixmap(dpi=dpi)
    if pix.colorspace is None or pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
