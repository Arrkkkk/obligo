package dev.obligo.core.platform.tenancy;

/**
 * Marker for repositories whose table has row-level security enabled (see
 * V1/V3 migrations for {@code organizations}) — i.e. the "tenant-scoped"
 * tables blueprint §10.9/§21 refers to.
 *
 * This does NOT mark "any repository that happens to have an org_id column."
 * Several Phase 2 tables (users, org_members, refresh_tokens, invitations)
 * carry org_id but are deliberately NOT RLS-protected, because they're
 * looked up before a tenant is resolved or by a value (token hash, Google
 * sub) that predates any org context — see each repository's own Javadoc.
 * Those must not implement this interface.
 *
 * Implementing this interface opts a class into the ArchUnit rules in
 * {@code TenantIsolationArchitectureTest}, which check a necessary
 * precondition for isolation — that every method runs inside the
 * {@code @Transactional} boundary {@link TenantConnectionPreparer}'s AOP
 * intercepts, and that no field offers a way to grab a connection outside
 * that boundary. They do NOT verify isolation itself; that guarantee comes
 * from the RLS policy on the table plus TenantConnectionPreparer actually
 * setting {@code app.org_id} correctly, which is proved separately (see
 * TenantIsolationTest, a real-database integration test). A class can
 * satisfy every ArchUnit rule here and still leak data if, say, the RLS
 * policy itself is wrong or missing — static analysis of Java bytecode
 * can't see into the database's policy catalog.
 */
public interface TenantScopedRepository {}
