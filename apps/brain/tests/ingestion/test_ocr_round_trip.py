"""The OCR half of the Phase 3 acceptance criterion (blueprint §21): for a
scanned/image-only page, every segment's (page, char_start, char_end) must
still round-trip exactly -- to Tesseract's own recognized text, not to
ground truth; see pdf.py and ocr.py module docstrings for why those are
different guarantees. No infra needed -- pure-unit, like
test_pdf_round_trip.py, which this file mirrors in structure and asserts
the same offset property against.

Fixtures are generated, not hand-written or downloaded from an external
host -- see tests/fixtures/pdfs/build_ocr_fixtures.py's own module
docstring for why (archive.org scans often carry a hidden pre-existing OCR
text layer that would silently defeat the scanned-page detector, and a
generation script keeps this reproducible with no network access at test
time). Re-run that script to regenerate these three PDFs if pdf.py's
rasterization or ocr.py's degradation logic ever changes.

- scanned_irs_1040.pdf -- real IRS form content (the same document as the
  born-digital irs_1040_table_heavy.pdf fixture), rasterized image-only,
  zero embedded text layer. The "genuinely scanned" case.
- scanned_low_quality.pdf -- the same content, deliberately degraded. The
  fixture that exists to drive real Tesseract confidence below
  LOW_OCR_CONFIDENCE_THRESHOLD on some (not all) of its words -- see
  test_low_quality_fixture_produces_real_sub_threshold_confidence for the
  actual numbers observed.
- mixed_born_digital_and_scanned.pdf -- page 1 born-digital (real text
  layer, copied losslessly from public_domain_chart.pdf), page 2 scanned.
  Proves per-page routing, not per-document -- see
  test_mixed_document_routes_each_page_independently.
- scanned_skewed.pdf (added for the 10-varied-PDF volume checkpoint) --
  page 1 of attention_is_all_you_need.pdf, rasterized and rotated 6
  degrees before being embedded image-only. A genuinely different
  degradation mechanism from scanned_low_quality.pdf's blur/contrast/noise
  recipe -- a real, common scanning artifact (a page fed askew) instead of
  a low-quality original. See
  test_skewed_fixture_produces_real_sub_threshold_confidence for the
  actual numbers observed, and build_ocr_fixtures.py's own docstring for
  how 6 degrees was chosen (3 degrees barely degraded anything; 9 degrees
  made Tesseract's layout analysis give up entirely -- not a gradual
  slope).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pytest

from obligo_brain.ingestion.loaders.ocr import LOW_OCR_CONFIDENCE_THRESHOLD, is_low_confidence
from obligo_brain.ingestion.loaders.pdf import extract_segments

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "pdfs"


def _assert_offsets_round_trip(segments) -> None:
    """Same reconstruction test as test_pdf_round_trip.py's -- recomputed
    independently from persisted-shape data (page, char_start, char_end,
    text), not asserted against extract_segments' own return value.
    """
    by_page: dict[int, list] = defaultdict(list)
    for s in segments:
        by_page[s.page].append(s)

    for page, page_segments in by_page.items():
        page_segments.sort(key=lambda s: s.ordinal)
        running_text = ""
        for s in page_segments:
            if running_text:
                running_text += "\n"
            assert len(running_text) == s.char_start, (
                f"page {page} ordinal {s.ordinal}: char_start {s.char_start} "
                f"doesn't match reconstructed offset {len(running_text)}"
            )
            running_text += s.text
            assert len(running_text) == s.char_end
            assert running_text[s.char_start : s.char_end] == s.text


def test_scanned_pdf_produces_segments_with_ocr_confidence_set() -> None:
    pdf_bytes = (FIXTURE_DIR / "scanned_irs_1040.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)

    assert segments, "scanned_irs_1040.pdf: extraction produced zero segments"
    for s in segments:
        assert s.ocr_confidence is not None, (
            f"ordinal {s.ordinal}: OCR segment must carry ocr_confidence, got None"
        )
        assert 0.0 <= s.ocr_confidence <= 100.0


def test_scanned_pdf_offsets_round_trip_exactly_to_tesseracts_own_output() -> None:
    """The OCR-path equivalent of test_pdf_round_trip.py's defining test --
    same property, same construction mechanism, different meaning of
    "exact" (see this file's module docstring)."""
    pdf_bytes = (FIXTURE_DIR / "scanned_irs_1040.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)
    _assert_offsets_round_trip(segments)


def test_scanned_pdf_extraction_is_deterministic() -> None:
    pdf_bytes = (FIXTURE_DIR / "scanned_irs_1040.pdf").read_bytes()
    first = extract_segments(pdf_bytes)
    second = extract_segments(pdf_bytes)
    assert first == second, "OCR extraction is not deterministic"


def test_no_ocr_segment_is_empty() -> None:
    pdf_bytes = (FIXTURE_DIR / "scanned_irs_1040.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)
    for s in segments:
        assert s.char_end > s.char_start
        assert s.text != ""


def test_low_quality_fixture_produces_real_sub_threshold_confidence() -> None:
    """Proves LOW_OCR_CONFIDENCE flagging against real Tesseract output, not
    just asserted in the abstract. Observed when this test was written:
    16 segments, confidences ranging 0-95, 11/16 below the 60.0 threshold
    -- a genuinely degraded scan, not a fabricated confidence value. The
    exact counts aren't pinned (Tesseract isn't guaranteed byte-identical
    across versions/platforms), but the fixture is degraded specifically
    to make "at least one real segment flags low" a safe, non-flaky
    assertion.
    """
    pdf_bytes = (FIXTURE_DIR / "scanned_low_quality.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)

    assert segments, "scanned_low_quality.pdf: extraction produced zero segments"
    low_confidence_segments = [s for s in segments if is_low_confidence(s)]
    assert low_confidence_segments, (
        f"expected at least one segment below LOW_OCR_CONFIDENCE_THRESHOLD "
        f"({LOW_OCR_CONFIDENCE_THRESHOLD}); confidences were "
        f"{[s.ocr_confidence for s in segments]}"
    )

    # And the fixture isn't pure noise either -- at least one segment
    # should still be legible enough to have been recognized with
    # reasonable confidence, or this would just be proving "garbage in,
    # garbage out" rather than a genuinely mixed-quality scan.
    assert any(not is_low_confidence(s) for s in segments), (
        "expected at least one segment above threshold too -- fixture "
        "should be a realistically bad scan, not unrecognizable noise"
    )

    # Offsets still hold exactly even on a badly-misread page -- round-trip
    # correctness doesn't depend on recognition accuracy.
    _assert_offsets_round_trip(segments)


def test_skewed_fixture_produces_real_sub_threshold_confidence() -> None:
    """The rotation-based sibling of
    test_low_quality_fixture_produces_real_sub_threshold_confidence --
    same shape of proof, deliberately different degradation mechanism (see
    this module's own docstring and build_ocr_fixtures.py's for why a
    second, mechanically distinct degraded fixture is worth having, not
    just a second blur/noise variant). Observed when this test was
    written: 13 segments, confidences 0-96, 9/13 below the 60.0 threshold
    -- real skew-induced misreads (e.g. "Attention {s All You Need" for
    "Attention Is All You Need"), not fabricated. Exact counts aren't
    pinned for the same Tesseract-version reason as the low-quality test.
    """
    pdf_bytes = (FIXTURE_DIR / "scanned_skewed.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)

    assert segments, "scanned_skewed.pdf: extraction produced zero segments"
    low_confidence_segments = [s for s in segments if is_low_confidence(s)]
    assert low_confidence_segments, (
        f"expected at least one segment below LOW_OCR_CONFIDENCE_THRESHOLD "
        f"({LOW_OCR_CONFIDENCE_THRESHOLD}); confidences were "
        f"{[s.ocr_confidence for s in segments]}"
    )
    assert any(not is_low_confidence(s) for s in segments), (
        "expected at least one segment above threshold too -- a skewed but "
        "still-legible scan, not unrecognizable noise"
    )

    _assert_offsets_round_trip(segments)


def test_mixed_document_routes_each_page_independently() -> None:
    """The case per-page (not per-document) detection exists for: one
    born-digital page, one scanned page, in the same file. A per-document
    detector could not produce this result at all.
    """
    pdf_bytes = (FIXTURE_DIR / "mixed_born_digital_and_scanned.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)

    page_1_segments = [s for s in segments if s.page == 1]
    page_2_segments = [s for s in segments if s.page == 2]

    assert page_1_segments, "page 1 (born-digital) produced zero segments"
    assert page_2_segments, "page 2 (scanned) produced zero segments"

    assert all(s.ocr_confidence is None for s in page_1_segments), (
        "page 1 is the born-digital page -- every segment must have ocr_confidence None"
    )
    assert all(s.ocr_confidence is not None for s in page_2_segments), (
        "page 2 is the scanned page -- every segment must have ocr_confidence set"
    )

    _assert_offsets_round_trip(segments)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "attention_is_all_you_need.pdf",
        "bert_two_column.pdf",
        "irs_1040_table_heavy.pdf",
        "public_domain_chart.pdf",
        "us_copyright_act_definitions.pdf",
        "federal_register_three_column.pdf",
    ],
)
def test_born_digital_fixtures_never_get_ocr_confidence_set(fixture_name: str) -> None:
    """Regression guard for the per-page routing change in pdf.py: every
    born-digital fixture test_pdf_round_trip.py already proves exact
    round-tripping for must still route entirely through the text-layer
    path -- none of them should accidentally trip the scanned-page
    threshold and get routed to OCR.
    """
    pdf_bytes = (FIXTURE_DIR / fixture_name).read_bytes()
    segments = extract_segments(pdf_bytes)
    assert all(s.ocr_confidence is None for s in segments), (
        f"{fixture_name}: expected every segment to be born-digital (ocr_confidence None), "
        f"but some segment was routed through OCR -- check SCANNED_PAGE_CHAR_THRESHOLD"
    )
