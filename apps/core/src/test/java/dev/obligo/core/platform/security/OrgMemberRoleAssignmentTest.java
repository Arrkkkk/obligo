package dev.obligo.core.platform.security;

import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import dev.obligo.core.platform.identity.Role;
import dev.obligo.core.platform.identity.User;
import dev.obligo.core.platform.identity.UserRepository;
import dev.obligo.core.platform.tenancy.OrganizationRepository;
import dev.obligo.core.platform.tenancy.TenantContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * The demonstration capability-checked endpoint for §10.7's RBAC slice.
 * Same rigor as TenantIsolationTest/RefreshTokenReuseTest: real DB, real
 * HTTP layer, both directions proven for every role, plus the specific
 * cross-tenant property this endpoint has to get right on its own since
 * org_members carries no RLS (see OrgMemberController's javadoc).
 */
@SpringBootTest(classes = ObligoApplication.class)
@AutoConfigureMockMvc
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class OrgMemberRoleAssignmentTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private PersonalOrgProvisioningService provisioningService;

    @Autowired
    private AccessTokenService accessTokenService;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrgMembershipRepository orgMembershipRepository;

    @Autowired
    private OrganizationRepository organizationRepository;

    private PersonalOrgProvisioningService.SignedInUser actor;
    private User target;
    private PersonalOrgProvisioningService.SignedInUser otherOrgActor;

    @BeforeEach
    void setUp() {
        actor = provisioningService.findOrProvision(
                "actor-" + UUID.randomUUID(), "actor-" + UUID.randomUUID() + "@example.com");
        target = userRepository.insert("target-" + UUID.randomUUID(), "target-" + UUID.randomUUID() + "@example.com");
        orgMembershipRepository.insert(actor.orgId(), target.id(), Role.MEMBER);

        otherOrgActor = provisioningService.findOrProvision(
                "other-" + UUID.randomUUID(), "other-" + UUID.randomUUID() + "@example.com");
    }

    @AfterEach
    void cleanup() {
        orgMembershipRepository.deleteByUserId(target.id());
        userRepository.delete(target.id());

        for (PersonalOrgProvisioningService.SignedInUser user : List.of(actor, otherOrgActor)) {
            orgMembershipRepository.deleteByUserId(user.userId());
            TenantContext.set(user.orgId());
            try {
                organizationRepository.delete(user.orgId());
            } finally {
                TenantContext.clear();
            }
            userRepository.delete(user.userId());
        }
    }

    @ParameterizedTest
    @EnumSource(Role.class)
    void endpointIsGatedExactlyByTheMemberManageRolesCapability(Role actingRole) throws Exception {
        orgMembershipRepository.updateRole(actor.orgId(), actor.userId(), actingRole);
        String token = accessTokenService.issue(actor.userId(), actor.orgId(), actingRole);

        ResultActions result = mockMvc.perform(patch("/api/v1/org/members/{userId}/role", target.id())
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"role\":\"ADMIN\"}"));

        boolean shouldSucceed = RoleCapabilities.hasCapability(actingRole, Capability.MEMBER_MANAGE_ROLES);
        if (shouldSucceed) {
            result.andExpect(status().isNoContent());
            assertThat(orgMembershipRepository.findByUserId(target.id()).role()).isEqualTo(Role.ADMIN);
        } else {
            result.andExpect(status().isForbidden());
            assertThat(orgMembershipRepository.findByUserId(target.id()).role()).isEqualTo(Role.MEMBER);
        }
    }

    @Test
    void cannotChangeRolesInAnotherOrgEvenWhileHoldingTheCapabilityInYourOwnOrg() throws Exception {
        // otherOrgActor is OWNER (has member:manage_roles) — but only in
        // their own org. org_members has no RLS, so this property has to
        // come entirely from the endpoint always scoping to claims.orgId().
        String token = accessTokenService.issue(otherOrgActor.userId(), otherOrgActor.orgId(), otherOrgActor.role());

        mockMvc.perform(patch("/api/v1/org/members/{userId}/role", target.id())
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"role\":\"ADMIN\"}"))
                .andExpect(status().isNotFound());

        assertThat(orgMembershipRepository.findByUserId(target.id()).role()).isEqualTo(Role.MEMBER);
    }

    @Test
    void requestWithNoTokenIsRejected() throws Exception {
        mockMvc.perform(patch("/api/v1/org/members/{userId}/role", target.id())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"role\":\"ADMIN\"}"))
                .andExpect(status().isUnauthorized());
    }
}
