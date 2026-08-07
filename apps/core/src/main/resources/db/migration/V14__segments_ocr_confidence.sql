-- Phase 3 (§21/§11): OCR checkpoint. V13's own comment deferred this
-- column ("meaningless for born-digital text, arrives with the OCR
-- checkpoint") -- this is that checkpoint. NULL for every segment produced
-- by the PyMuPDF text-layer path (apps/brain/.../loaders/pdf.py);
-- populated for every segment produced by the Tesseract OCR path
-- (apps/brain/.../loaders/ocr.py). NULL-ness of this column is itself the
-- signal for which extraction path produced a given row -- no separate
-- "source" enum column is added for that, since NULL vs. non-NULL already
-- carries it without redundancy.
ALTER TABLE segments ADD COLUMN ocr_confidence REAL CHECK (ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 100));

-- Load-bearing distinction, not a formatting nicety -- stated here because
-- a column comment is where a future reader querying this table will
-- actually see it, not just in a conversation or a commit message.
--
-- The Phase 3 acceptance criterion ("segment offsets round-trip exactly to
-- the source text") means two different things depending on which path
-- produced a row, and this column is how you tell which one you're
-- looking at:
--
--   ocr_confidence IS NULL     -> text/char_start/char_end are exact
--   (PyMuPDF path)                against the PDF's own embedded text
--                                  layer -- ground truth. A misread is not
--                                  possible; PyMuPDF is reading bytes the
--                                  PDF itself declares as text.
--
--   ocr_confidence IS NOT NULL -> text/char_start/char_end are exact
--   (Tesseract OCR path)          against Tesseract's own recognition
--                                  output, NOT against the physical page.
--                                  The offsets are still exact by
--                                  construction (same running-string
--                                  mechanism as the PyMuPDF path) -- but
--                                  what they're exact *to* is a hypothesis
--                                  about the page, which can be wrong. A
--                                  low ocr_confidence value is the signal
--                                  that this segment's text may not match
--                                  what the page actually says, even
--                                  though its own offsets are internally
--                                  consistent.
--
-- Do not read "round-trips exactly" on an OCR-derived segment as "matches
-- the source document" -- it means "matches what Tesseract said the source
-- document says." See obligo_brain.ingestion.loaders.ocr's module
-- docstring and CLAUDE.md's Phase 3 progress notes for the same point
-- stated in those two other places, deliberately, so it can't be missed
-- by only reading one of the three.
COMMENT ON COLUMN segments.ocr_confidence IS
    'Tesseract confidence (0-100) for this block, taken as the MIN across the block''s own words -- '
    'not the mean -- so one badly-misread word cannot be averaged away by surrounding high-confidence '
    'words. NULL for PyMuPDF text-layer segments; NULL-ness marks which extraction path produced this '
    'row. See migration V14''s own comment for the full round-trip-exactness distinction this column '
    'exists to carry.';
