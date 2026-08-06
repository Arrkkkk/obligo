-- Phase 3 (§21/§11): supersedes V12's deliberate placeholder now that real
-- PyMuPDF text/layout extraction exists. V12's own comment said the real
-- columns "arrive with the actual PyMuPDF/PaddleOCR segmentation logic in a
-- later slice" -- this is that slice, for the PyMuPDF (born-digital) path
-- only. ALTERs the existing table rather than dropping/recreating it: no
-- environment has real segment rows yet (the feature didn't exist before
-- this checkpoint), but expand-in-place is the right discipline regardless,
-- per CLAUDE.md's migrations-are-immutable / expand-contract rule.
--
-- `ordinal`: 0-indexed position in document-wide extraction order, per
-- blueprint's own segments row (line 1477: "U (source_id, ordinal)").
-- `page`: 1-indexed page number (PyMuPDF's own page.number is 0-indexed;
-- stored 1-indexed here to match how a human -- or a future citation UI --
-- refers to "page 3", not PyMuPDF's internal convention).
ALTER TABLE segments
    ADD COLUMN ordinal INT NOT NULL,
    ADD COLUMN page INT NOT NULL CHECK (page >= 1);

ALTER TABLE segments ADD CONSTRAINT segments_source_id_ordinal_uidx UNIQUE (source_id, ordinal);

-- Tightened from >= to >: an empty segment (char_end == char_start) isn't a
-- meaningful unit of text and is filtered out at extraction time, so the
-- constraint should reject it rather than silently allow it. V12's CHECK
-- referenced two columns (char_end >= char_start), so Postgres named it as
-- a table-level constraint (`segments_check`), not a column-level one
-- (`segments_char_end_check`) -- confirmed against pg_constraint on the
-- real dev branch, not assumed from naming convention.
ALTER TABLE segments DROP CONSTRAINT segments_check;
ALTER TABLE segments ADD CONSTRAINT segments_char_end_gt_char_start_check CHECK (char_end > char_start);

-- Deliberately NOT added yet, matching V12's own "later slice" framing and
-- CLAUDE.md's "don't build for hypothetical future requirements" rule:
-- `layout jsonb` (bbox) -- no consumer until the page-rendering/highlighting
-- checkpoint; `ocr_confidence` -- meaningless for born-digital text, arrives
-- with the OCR checkpoint; `ts_start/end_ms`, `speaker` -- audio/transcript
-- only, Phase 6. Blueprint's full segments row (line 1477) names all of
-- these; this migration intentionally implements a subset.
