package dev.obligo.core.platform.security;

import java.util.Arrays;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * The capability set from blueprint §10.7. Checked as capabilities, not
 * roles: adding a role is a data change to RoleCapabilities, not a change
 * to every @PreAuthorize across the codebase.
 */
public enum Capability {
    OBLIGATION_READ("obligation:read"),
    OBLIGATION_WRITE("obligation:write"),
    OBLIGATION_EDIT_IR("obligation:edit_ir"),
    OBLIGATION_WAIVE("obligation:waive"),
    EVIDENCE_ATTACH("evidence:attach"),
    EVIDENCE_APPROVE("evidence:approve"),
    FINDING_RESOLVE("finding:resolve"),
    SOURCE_UPLOAD("source:upload"),
    SOURCE_READ("source:read"),
    SOURCE_DELETE("source:delete"),
    MEMBER_INVITE("member:invite"),
    MEMBER_MANAGE_ROLES("member:manage_roles"),
    ORG_MANAGE("org:manage"),
    ORG_DELETE("org:delete"),
    AUDIT_READ("audit:read"),
    MCP_INVOKE_WRITE("mcp:invoke_write"),
    EXPORT_CREATE("export:create");

    private static final Map<String, Capability> BY_WIRE_NAME =
            Arrays.stream(values()).collect(Collectors.toMap(Capability::wireName, Function.identity()));

    private final String wireName;

    Capability(String wireName) {
        this.wireName = wireName;
    }

    public String wireName() {
        return wireName;
    }

    public static Capability fromWireName(String wireName) {
        Capability capability = BY_WIRE_NAME.get(wireName);
        if (capability == null) {
            throw new IllegalArgumentException("Unknown capability: " + wireName);
        }
        return capability;
    }
}
