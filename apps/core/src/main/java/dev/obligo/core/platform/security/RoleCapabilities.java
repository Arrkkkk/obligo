package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.Role;

import java.util.Collections;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/**
 * The role -> capability matrix from blueprint §10.7, transcribed exactly.
 * This is the only place that should ever change when a role's permissions
 * change or a new role is added — every enforcement point checks a
 * capability (via AccessTokenService baking §10.3's "scopes" claim from
 * this at mint time), never a role name directly.
 *
 * MEMBER's OBLIGATION_READ/OBLIGATION_WRITE are marked "scoped¹" in the
 * blueprint — restricted to obligations the member owns or is assigned to,
 * enforced as a repository-layer predicate. That predicate doesn't exist
 * yet (no obligations table until Phase 3+/5); granting the capability
 * here is correct, but until that predicate lands, a MEMBER with this
 * capability would see all obligations, not just their own.
 *
 * SOURCE_READ (§21 Phase 3 SSE checkpoint) has no row in blueprint §10.7's
 * own capability table at all — that table only names source:upload and
 * source:delete. Granted here to every role that already has SOURCE_UPLOAD
 * (OWNER/ADMIN via their existing catch-all grants, LEGAL_OPS, MEMBER —
 * reading the status of something you can upload is not a new trust
 * boundary), plus AUDITOR on the strength of blueprint §10.7's own stated
 * role intent ("Read everything including the audit log. Write nothing,
 * ever.") even though AUDITOR has no SOURCE_UPLOAD. A real gap-fill, not a
 * guess — documented here since it deviates from a table blueprint
 * otherwise treats as authoritative.
 */
public final class RoleCapabilities {

    private static final Map<Role, Set<Capability>> BY_ROLE = new EnumMap<>(Role.class);

    static {
        BY_ROLE.put(Role.OWNER, EnumSet.allOf(Capability.class));

        BY_ROLE.put(Role.ADMIN, EnumSet.complementOf(EnumSet.of(Capability.ORG_DELETE)));

        BY_ROLE.put(
                Role.LEGAL_OPS,
                EnumSet.of(
                        Capability.OBLIGATION_READ,
                        Capability.OBLIGATION_WRITE,
                        Capability.OBLIGATION_EDIT_IR,
                        Capability.OBLIGATION_WAIVE,
                        Capability.EVIDENCE_ATTACH,
                        Capability.EVIDENCE_APPROVE,
                        Capability.FINDING_RESOLVE,
                        Capability.SOURCE_UPLOAD,
                        Capability.SOURCE_READ,
                        Capability.MCP_INVOKE_WRITE,
                        Capability.EXPORT_CREATE));

        BY_ROLE.put(
                Role.MEMBER,
                EnumSet.of(
                        Capability.OBLIGATION_READ, // scoped¹ — see class javadoc
                        Capability.OBLIGATION_WRITE, // scoped¹ — see class javadoc
                        Capability.EVIDENCE_ATTACH,
                        Capability.SOURCE_UPLOAD,
                        Capability.SOURCE_READ));

        BY_ROLE.put(
                Role.AUDITOR,
                EnumSet.of(
                        Capability.OBLIGATION_READ,
                        Capability.AUDIT_READ,
                        Capability.EXPORT_CREATE,
                        Capability.SOURCE_READ));
    }

    private RoleCapabilities() {}

    public static Set<Capability> capabilitiesFor(Role role) {
        return Collections.unmodifiableSet(BY_ROLE.get(role));
    }

    public static boolean hasCapability(Role role, Capability capability) {
        return BY_ROLE.get(role).contains(capability);
    }
}
