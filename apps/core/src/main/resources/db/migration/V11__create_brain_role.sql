-- Phase 3 (§21): apps/brain is the first non-Spring process to read/write
-- tenant-scoped data directly. It does so by running PyMuPDF/PaddleOCR --
-- native-code parsing -- against untrusted, attacker-supplied file bytes,
-- the same risk class as apps/core's own documented, accepted gap
-- (in-process, unsandboxed PDF structural validation), arguably a larger
-- surface here given OCR's heavier native dependencies.
--
-- Rather than reuse obligo_app (V2), which already carries broad grants
-- across the entire identity plane (users, org_members, refresh_tokens,
-- invitations, security_audit_events) plus organizations and sources,
-- apps/brain gets its own role. If the Python process is ever compromised
-- via a malicious upload, the blast radius is capped to exactly what this
-- role can do (see V12 for its grants: read-only on sources, read/write on
-- segments, nothing else) -- not everything obligo_app can do.
--
-- NOBYPASSRLS for the same reason as V2: Neon's owner role (used to run
-- this migration) has rolbypassrls=true, so RLS is a silent no-op for it.
-- The application must connect as a role that doesn't have that attribute.
CREATE ROLE obligo_brain LOGIN PASSWORD '${brain_db_password}' NOBYPASSRLS;

GRANT USAGE ON SCHEMA public TO obligo_brain;
