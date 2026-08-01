-- Neon's connection-string owner role (used above to run this migration)
-- has rolbypassrls=true, which makes every RLS policy a no-op for it
-- regardless of FORCE ROW LEVEL SECURITY. The application must connect as
-- a role that does not have that attribute, per blueprint §10.9 ("app
-- connects as non-superuser role") — NOBYPASSRLS below makes that
-- explicit rather than relying on it being the (currently correct)
-- default.
CREATE ROLE obligo_app LOGIN PASSWORD '${app_db_password}' NOBYPASSRLS;

GRANT USAGE ON SCHEMA public TO obligo_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON organizations TO obligo_app;
