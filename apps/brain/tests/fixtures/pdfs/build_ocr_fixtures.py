"""One-off generator for this checkpoint's two new OCR fixtures. Run once
(`uv run python tests/fixtures/pdfs/build_ocr_fixtures.py` from apps/brain)
to (re)produce the committed PDFs below it in this directory -- not
imported by any test, same role PdfTestFixtures plays as a generator on the
Java side, or PDFBox-generated fixtures for the born-digital PdfTestFixtures
suite: a real, reproducible generation script, not a hand-written byte
string.

**scanned_irs_1040.pdf** -- genuinely image-only, zero embedded text layer.
Built by rasterizing the real, already-committed irs_1040_table_heavy.pdf
(both pages) at 300 DPI via PyMuPDF and re-inserting each page as a bare
image into a fresh PDF with no text layer at all. This is "real" in the
sense that matters for this checkpoint: real document content (an actual
IRS form's actual layout, actual tabular structure), rasterized exactly the
way a physical scanner produces output, with a genuinely absent text layer
-- not hand-typed placeholder text, not a synthetic image.

Deliberately NOT sourced from an external host (e.g. archive.org): many
archive.org "PDF" downloads already carry a hidden OCR text layer baked in
by their own ABBYY pipeline, which would silently defeat this checkpoint's
own scanned-page detection heuristic (page.get_text("text") would find
plenty of characters, and the page would never route to OCR at all) without
that being obvious from the file itself. Deriving the fixture from a
PDF already in this repo avoids that risk entirely and needs no network
access at test time.

**scanned_low_quality.pdf** -- the same real page, then deliberately
degraded (downscale/upscale blur, Gaussian blur, contrast reduction, blended
noise) before being embedded image-only. This is the fixture that exists
specifically to drive genuine sub-threshold Tesseract confidence on some of
its words, so LOW_OCR_CONFIDENCE-style flagging (ocr.is_low_confidence) is
proven against real Tesseract output, not asserted in the abstract. The
degradation level was tuned by actually running Tesseract against
candidates, not guessed once and left: the first attempt (1/5-scale
downsample + heavy blur + 25% noise blend) came back as pure unrecognizable
noise -- 0 legible words -- which proves nothing about confidence
*flagging* specifically. Tuned down to 1/3-scale + lighter blur + 12% noise
so the result reads like a genuinely bad fax/photocopy (some words still
correctly recognized at moderate confidence, several badly misread at
confidence 0-40) rather than blank noise. Real confidence numbers achieved
are recorded in tests/ingestion/test_ocr_round_trip.py's own comments, not
just claimed here.

**mixed_born_digital_and_scanned.pdf** -- page 1 is a lossless copy of the
real public_domain_chart.pdf's own page 1 (born-digital, real text layer,
via insert_pdf so nothing is re-rasterized or reconstructed); page 2 is a
rasterized, image-only copy of irs_1040_table_heavy.pdf's page 1. This is
the fixture that actually proves per-page (not per-document) routing --
the acceptance-criteria "mixed" case CLAUDE.md names as still open. A
per-document detector could not produce this file's expected result at
all: page 1 must come back with ocr_confidence None on every segment, page
2 with ocr_confidence set on every segment, from a single extract_segments
call.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter

FIXTURE_DIR = Path(__file__).parent


def _rasterize(page: fitz.Page, dpi: int = 300) -> Image.Image:
    pix = page.get_pixmap(dpi=dpi)
    if pix.colorspace is None or pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def _degrade(image: Image.Image) -> Image.Image:
    """Heavy but not total degradation -- enough to genuinely confuse
    Tesseract on a meaningful fraction of words without erasing the page's
    text entirely (a blank/unrecognizable page would trivially report zero
    words rather than proving the low-*confidence* path specifically).
    """
    w, h = image.size
    tiny = image.resize((max(1, w // 3), max(1, h // 3)), Image.BILINEAR)
    image = tiny.resize((w, h), Image.BILINEAR)
    image = image.filter(ImageFilter.GaussianBlur(radius=1.3))
    image = ImageEnhance.Contrast(image).enhance(0.55)
    image = ImageEnhance.Brightness(image).enhance(1.08)
    noise = Image.effect_noise(image.size, 35).convert("RGB")
    image = Image.blend(image, noise, alpha=0.12)
    return image


def _build_image_only_pdf(images: list[Image.Image]) -> bytes:
    # JPEG, not PNG: a real scanner's output is JPEG-compressed, not
    # lossless -- and PNG at 300 DPI produced ~28 MB fixtures, unfit to
    # commit. quality=85 is a realistic scan-quality tradeoff, not just a
    # size hack.
    out = fitz.open()
    for image in images:
        w, h = image.size
        page = out.new_page(width=w, height=h)
        page.insert_image(page.rect, stream=_jpeg_bytes(image))
    data = out.tobytes(deflate=True)
    out.close()
    return data


def _jpeg_bytes(image: Image.Image, quality: int = 85) -> bytes:
    import io

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def _build_mixed_fixture() -> bytes:
    out = fitz.open()

    born_digital_src = fitz.open(FIXTURE_DIR / "public_domain_chart.pdf")
    out.insert_pdf(born_digital_src, from_page=0, to_page=0)
    born_digital_src.close()

    scan_src = fitz.open(FIXTURE_DIR / "irs_1040_table_heavy.pdf")
    scan_image = _rasterize(scan_src[0])
    scan_src.close()
    w, h = scan_image.size
    page = out.new_page(width=w, height=h)
    page.insert_image(page.rect, stream=_jpeg_bytes(scan_image))

    data = out.tobytes(deflate=True)
    out.close()
    return data


def main() -> None:
    source_path = FIXTURE_DIR / "irs_1040_table_heavy.pdf"
    doc = fitz.open(source_path)
    page_images = [_rasterize(doc[i]) for i in range(len(doc))]
    doc.close()

    scanned_bytes = _build_image_only_pdf(page_images)
    (FIXTURE_DIR / "scanned_irs_1040.pdf").write_bytes(scanned_bytes)
    print(f"wrote scanned_irs_1040.pdf ({len(scanned_bytes)} bytes, {len(page_images)} pages)")

    degraded_images = [_degrade(page_images[0])]
    low_quality_bytes = _build_image_only_pdf(degraded_images)
    (FIXTURE_DIR / "scanned_low_quality.pdf").write_bytes(low_quality_bytes)
    print(f"wrote scanned_low_quality.pdf ({len(low_quality_bytes)} bytes, 1 page)")

    mixed_bytes = _build_mixed_fixture()
    (FIXTURE_DIR / "mixed_born_digital_and_scanned.pdf").write_bytes(mixed_bytes)
    print(f"wrote mixed_born_digital_and_scanned.pdf ({len(mixed_bytes)} bytes, 2 pages)")


if __name__ == "__main__":
    main()
