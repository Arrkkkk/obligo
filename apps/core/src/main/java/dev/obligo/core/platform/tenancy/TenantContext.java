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
