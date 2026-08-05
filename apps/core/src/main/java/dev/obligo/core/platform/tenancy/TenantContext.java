package dev.obligo.core.platform.tenancy;

import java.util.UUID;

/**
 * Holds the active org_id for the current thread. Once auth exists, this is
 * populated from the access token's {@code org_id} claim (§10.4) — never
 * from a header or request body. Callers must always {@link #clear()} in a
 * finally block: on a pooled request thread, a forgotten clear() leaks one
 * tenant's context into whatever request runs next on that thread, which is
 * the same class of hazard as the connection-pooling trap in §10.9, just one
 * layer up.
 *
 * <p><b>Tripwire for future-you:</b> multi-step flows that span more than
 * one {@code @Transactional} call on the same logical operation — e.g.
 * {@code SourceUploadService.commit()}'s gatekeep → verify → finalize split
 * across {@code SourceCommitGateway} — rely on this ThreadLocal staying set
 * across every step. That holds only because every such flow today is
 * synchronous and single-threaded end to end: one HTTP request, one thread,
 * from {@code TenantJwtAuthenticationFilter} setting it to the same filter
 * clearing it in its {@code finally}. If any step in a flow like that ever
 * becomes {@code @Async}, gets dispatched to an executor, or otherwise
 * crosses a thread pool boundary, this will NOT throw — {@link #get()} will
 * silently return {@code null} on the new thread, {@code app.org_id} will
 * never get set for whatever transaction runs there, and RLS will fail
 * closed (empty results, not a crash, not a leak, but a completely broken
 * feature that looks like a data problem). There is no compiler or runtime
 * guard against this; it is a structural assumption, not an enforced one.
 */
public final class TenantContext {

    private static final ThreadLocal<UUID> CURRENT_ORG_ID = new ThreadLocal<>();

    private TenantContext() {}

    public static void set(UUID orgId) {
        CURRENT_ORG_ID.set(orgId);
    }

    public static UUID get() {
        return CURRENT_ORG_ID.get();
    }

    public static void clear() {
        CURRENT_ORG_ID.remove();
    }
}
