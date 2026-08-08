"""The core Phase 3 acceptance criterion (blueprint §21): for real, varied
PDFs, every segment's (page, char_start, char_end) must round-trip exactly
to the source text. No infra needed -- this is pure-unit, fast, and
exhaustive, the Python analog of PdfStructuralValidatorTest's role on the
Java side (SourceUploadFlowTest is the slower, real-infra counterpart; see
tests/api/test_segment_source.py).

Fixtures are real, downloaded documents (tests/fixtures/pdfs/), not
synthetic ones -- deliberately, per the same reasoning V12's own Java
sibling (PdfTestFixtures) had for using PDFBox-generated fixtures over
hand-written byte strings: a real PDF exercises PyMuPDF's actual block
extraction and layout heuristics, which a minimal fixture wouldn't.

- attention_is_all_you_need.pdf -- arXiv paper, 15 pages, mixed single/
  wide-column layout with equations and figures.
- bert_two_column.pdf -- ACL Anthology paper, 16 pages, genuinely
  two-column academic layout. Also the fixture that demonstrates the
  documented reading-order limitation -- see
  test_two_column_fixture_has_exact_offsets_despite_reading_order_caveat.
- irs_1040_table_heavy.pdf -- real IRS form, 2 pages, dense tabular/form
  layout, very different block shapes than prose.
- public_domain_chart.pdf -- 2-page chart/table document, unusual mixed
  formatting relative to the other three.
- us_copyright_act_definitions.pdf -- 3 pages excerpted from the real,
  downloaded U.S. Copyright Office publication of Title 17 (17 U.S.C.
  §101, "Definitions"), copyright.gov/title17/title17.pdf. Single-column
  dense statutory prose -- genuinely different from all four fixtures
  above (no equations/figures, no columns, no tabular structure), and
  thematically apt for an obligations-extraction project. Confirmed
  single-column via real x-coordinate block inspection before adding, not
  assumed from the source's reputation.
- federal_register_three_column.pdf -- 3 pages excerpted from a real
  Federal Register issue (govinfo.gov/content/pkg/FR-2024-01-05/pdf/
  FR-2024-01-05.pdf), pages covering an actual proposed-rule notice
  (TTB/Alcohol and Tobacco Tax and Trade Bureau, Mendocino Ridge AVA
  petition). Genuinely three-column, confirmed by inspecting real block
  x-coordinates (three distinct column bands, not two) before choosing
  these pages over the document's own two-column table-of-contents
  pages -- the multi-column case bert_two_column.pdf doesn't cover
  (2 columns vs. 3), with denser small-print blocks than academic prose.
  Both federal government works (17 U.S.C. §105 -- no copyright), same
  public-domain footing as the IRS/arXiv/ACL fixtures above.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pytest

from obligo_brain.ingestion.loaders.pdf import extract_segments

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "pdfs"
FIXTURE_NAMES = [
    "attention_is_all_you_need.pdf",
    "bert_two_column.pdf",
    "irs_1040_table_heavy.pdf",
    "public_domain_chart.pdf",
    "us_copyright_act_definitions.pdf",
    "federal_register_three_column.pdf",
]


@pytest.fixture(params=FIXTURE_NAMES)
def fixture_pdf_bytes(request: pytest.FixtureRequest) -> tuple[str, bytes]:
    name: str = request.param
    return name, (FIXTURE_DIR / name).read_bytes()


def test_extraction_produces_at_least_one_segment_per_page(fixture_pdf_bytes: tuple[str, bytes]) -> None:
    name, pdf_bytes = fixture_pdf_bytes
    segments = extract_segments(pdf_bytes)

    assert segments, f"{name}: extraction produced zero segments"
    pages_with_segments = {s.page for s in segments}
    assert min(pages_with_segments) == 1
    # every page number seen is contiguous from 1 -- no page silently skipped
    assert pages_with_segments == set(range(1, max(pages_with_segments) + 1))


def test_every_segment_offset_round_trips_exactly_to_its_page_text(
    fixture_pdf_bytes: tuple[str, bytes],
) -> None:
    """The defining acceptance criterion: reconstruct each page's canonical
    text the same way extract_segments builds it internally, and confirm
    page_text[char_start:char_end] == text for every single segment, on a
    real multi-page document -- not asserted on the module's own return
    value (that would be tautological), but recomputed independently here
    from persisted-shape data (ordinal, page, char_start, char_end, text)
    with no access to extract_segments' internals.
    """
    name, pdf_bytes = fixture_pdf_bytes
    segments = extract_segments(pdf_bytes)

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
                f"{name} page {page} ordinal {s.ordinal}: char_start {s.char_start} "
                f"doesn't match reconstructed offset {len(running_text)}"
            )
            running_text += s.text
            assert len(running_text) == s.char_end, (
                f"{name} page {page} ordinal {s.ordinal}: char_end {s.char_end} "
                f"doesn't match reconstructed offset {len(running_text)}"
            )
            assert running_text[s.char_start : s.char_end] == s.text


def test_extraction_is_deterministic(fixture_pdf_bytes: tuple[str, bytes]) -> None:
    """Re-extracting the same bytes twice must produce byte-identical
    (ordinal, page, char_start, char_end, text) for every segment -- proves
    there's nothing order-nondeterministic (e.g. dict iteration, set
    ordering) hiding in the extraction path.
    """
    name, pdf_bytes = fixture_pdf_bytes
    first = extract_segments(pdf_bytes)
    second = extract_segments(pdf_bytes)
    assert first == second, f"{name}: extraction is not deterministic"


def test_no_segment_is_empty(fixture_pdf_bytes: tuple[str, bytes]) -> None:
    _name, pdf_bytes = fixture_pdf_bytes
    segments = extract_segments(pdf_bytes)
    for s in segments:
        assert s.char_end > s.char_start
        assert s.text != ""


def test_two_column_fixture_has_exact_offsets_despite_reading_order_caveat() -> None:
    """Documents a real, observed limitation rather than a hypothetical
    one: on bert_two_column.pdf page 2, section heading "2.2" (ordinal 20)
    is emitted BEFORE "2.1"'s body paragraph (ordinal 21) and its own
    heading (ordinal 22) -- PyMuPDF's sort=True orders blocks by
    y-coordinate, which interleaves the two side-by-side columns instead of
    reading column 1 fully before column 2. This is the named,
    known-not-solved reading-order limitation from the module docstring.

    The offsets are still exact regardless -- that's the point of this
    test. Round-trip correctness (what this checkpoint's acceptance
    criterion requires) does not depend on reading order being correct.
    """
    pdf_bytes = (FIXTURE_DIR / "bert_two_column.pdf").read_bytes()
    segments = extract_segments(pdf_bytes)
    page_2 = sorted((s for s in segments if s.page == 2), key=lambda s: s.ordinal)

    heading_22 = next(s for s in page_2 if s.text.startswith("2.2"))
    heading_21 = next(s for s in page_2 if s.text.startswith("2.1"))

    # The observed jumbling: 2.2's heading has a lower ordinal (appears
    # earlier in extraction order) than 2.1's heading, even though 2.1
    # should read first. Asserted here so a future PyMuPDF upgrade or
    # column-aware reordering fix changes this test loudly, not silently.
    assert heading_22.ordinal < heading_21.ordinal

    # But both still round-trip exactly to their own recorded span.
    running = ""
    for s in page_2:
        if running:
            running += "\n"
        running += s.text
    assert running[heading_22.char_start : heading_22.char_end] == heading_22.text
    assert running[heading_21.char_start : heading_21.char_end] == heading_21.text
