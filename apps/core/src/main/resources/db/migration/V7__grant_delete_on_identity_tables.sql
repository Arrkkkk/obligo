-- V4-V6 under-granted relative to the organizations precedent (V2 grants
-- DELETE so tests can clean up after themselves). Matching that here.
GRANT DELETE ON users TO obligo_app;
GRANT DELETE ON org_members TO obligo_app;
GRANT DELETE ON refresh_tokens TO obligo_app;
GRANT DELETE ON security_audit_events TO obligo_app;
