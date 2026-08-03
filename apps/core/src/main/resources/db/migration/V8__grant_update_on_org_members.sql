-- OrgMemberController's role-change endpoint needs UPDATE on org_members;
-- V5 only granted SELECT/INSERT (+V7's DELETE for test cleanup).
GRANT UPDATE ON org_members TO obligo_app;
