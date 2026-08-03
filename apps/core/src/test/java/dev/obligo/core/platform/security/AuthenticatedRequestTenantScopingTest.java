package dev.obligo.core.platform.security;

import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import dev.obligo.core.platform.identity.UserRepository;
import dev.obligo.core.platform.tenancy.OrganizationRepository;
import dev.obligo.core.platform.tenancy.TenantContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.UUID;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * The capstone proof for this phase, driven through the real HTTP layer
 * (no direct TenantContext.set() calls, unlike TenantIsolationTest): sign
 * in provisions a personal org (§10.8), a real RS256 token carries its
 * org_id (§10.4), TenantJwtAuthenticationFilter reads it into
 * TenantContext, and a downstream RLS-protected read via
 * OrganizationRepository — the exact table TenantIsolationTest proved
 * isolation on — comes back scoped to that org and nothing else.
 */
@SpringBootTest(classes = ObligoApplication.class)
@AutoConfigureMockMvc
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class AuthenticatedRequestTenantScopingTest {

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

    private PersonalOrgProvisioningService.SignedInUser userA;
    private PersonalOrgProvisioningService.SignedInUser userB;

    @BeforeEach
    void provisionTwoUsers() {
        userA = provisioningService.findOrProvision("google-sub-" + UUID.randomUUID(), "a-" + UUID.randomUUID() + "@example.com");
        userB = provisioningService.findOrProvision("google-sub-" + UUID.randomUUID(), "b-" + UUID.randomUUID() + "@example.com");
    }

    @AfterEach
    void cleanup() {
        for (PersonalOrgProvisioningService.SignedInUser user : List.of(userA, userB)) {
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

    @Test
    void authenticatedRequestIsScopedToTheTokensOrgOnly() throws Exception {
        String tokenA = accessTokenService.issue(userA.userId(), userA.orgId(), userA.role());

        mockMvc.perform(get("/api/v1/me").header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.userId").value(userA.userId().toString()))
                .andExpect(jsonPath("$.orgId").value(userA.orgId().toString()))
                .andExpect(jsonPath("$.role").value("OWNER"));

        String tokenB = accessTokenService.issue(userB.userId(), userB.orgId(), userB.role());

        mockMvc.perform(get("/api/v1/me").header("Authorization", "Bearer " + tokenB))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.userId").value(userB.userId().toString()))
                .andExpect(jsonPath("$.orgId").value(userB.orgId().toString()));
    }

    @Test
    void requestWithNoTokenIsRejected() throws Exception {
        mockMvc.perform(get("/api/v1/me")).andExpect(status().isUnauthorized());
    }

    @Test
    void requestWithTamperedTokenIsRejected() throws Exception {
        String token = accessTokenService.issue(userA.userId(), userA.orgId(), userA.role());

        mockMvc.perform(get("/api/v1/me").header("Authorization", "Bearer " + token + "x"))
                .andExpect(status().isUnauthorized());
    }
}
