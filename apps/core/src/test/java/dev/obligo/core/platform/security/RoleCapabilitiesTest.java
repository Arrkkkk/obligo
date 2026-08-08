package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.Role;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.EnumSet;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.params.provider.Arguments.arguments;

/**
 * Pure data test, no Spring/DB — every cell of blueprint §10.7's 16x5
 * capability matrix, transcribed directly so a typo in RoleCapabilities
 * fails as one specific (capability, role) cell rather than a vague
 * set-mismatch.
 */
class RoleCapabilitiesTest {

    @ParameterizedTest(name = "{0} x {1} = {2}")
    @MethodSource("matrixCells")
    void matchesBlueprintTableExactly(Capability capability, Role role, boolean expected) {
        assertThat(RoleCapabilities.hasCapability(role, capability)).isEqualTo(expected);
    }

    static Stream<Arguments> matrixCells() {
        return Stream.of(
                // obligation:read — MEMBER's is "scoped¹" in the blueprint
                // (ownership-based row filter); granted as a plain
                // capability here since that predicate doesn't exist yet.
                row(Capability.OBLIGATION_READ, true, true, true, true, true),
                row(Capability.OBLIGATION_WRITE, true, true, true, true, false),
                row(Capability.OBLIGATION_EDIT_IR, true, true, true, false, false),
                row(Capability.OBLIGATION_WAIVE, true, true, true, false, false),
                row(Capability.EVIDENCE_ATTACH, true, true, true, true, false),
                row(Capability.EVIDENCE_APPROVE, true, true, true, false, false),
                row(Capability.FINDING_RESOLVE, true, true, true, false, false),
                row(Capability.SOURCE_UPLOAD, true, true, true, true, false),
                // source:read has no row in blueprint §10.7's own table at
                // all (see RoleCapabilities' class javadoc) — granted to
                // every role, since it's implied by SOURCE_UPLOAD for four
                // of them and by AUDITOR's own stated "read everything"
                // intent for the fifth.
                row(Capability.SOURCE_READ, true, true, true, true, true),
                row(Capability.SOURCE_DELETE, true, true, false, false, false),
                row(Capability.MEMBER_INVITE, true, true, false, false, false),
                row(Capability.MEMBER_MANAGE_ROLES, true, true, false, false, false),
                row(Capability.ORG_MANAGE, true, true, false, false, false),
                row(Capability.ORG_DELETE, true, false, false, false, false),
                row(Capability.AUDIT_READ, true, true, false, false, true),
                row(Capability.MCP_INVOKE_WRITE, true, true, true, false, false),
                row(Capability.EXPORT_CREATE, true, true, true, false, true))
                .flatMap(s -> s);
    }

    /** One matrix row -> 5 (capability, role, expected) argument sets, columns in blueprint order. */
    private static Stream<Arguments> row(
            Capability capability, boolean owner, boolean admin, boolean legalOps, boolean member, boolean auditor) {
        return Stream.of(
                arguments(capability, Role.OWNER, owner),
                arguments(capability, Role.ADMIN, admin),
                arguments(capability, Role.LEGAL_OPS, legalOps),
                arguments(capability, Role.MEMBER, member),
                arguments(capability, Role.AUDITOR, auditor));
    }

    @Test
    void ownerHasEveryCapability() {
        assertThat(RoleCapabilities.capabilitiesFor(Role.OWNER)).isEqualTo(EnumSet.allOf(Capability.class));
    }

    @Test
    void everyRoleCapabilitySetIsExactlyTheUnionImpliedByTheMatrixCells() {
        // Cross-check: capabilitiesFor() and hasCapability() must agree —
        // catches a matrix that answers "false" for a cell that's actually
        // in the role's set, or vice versa.
        for (Role role : Role.values()) {
            for (Capability capability : Capability.values()) {
                assertThat(RoleCapabilities.capabilitiesFor(role).contains(capability))
                        .as("%s x %s", role, capability)
                        .isEqualTo(RoleCapabilities.hasCapability(role, capability));
            }
        }
    }
}
