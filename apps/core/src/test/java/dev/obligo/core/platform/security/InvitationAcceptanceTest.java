package dev.obligo.core.platform.security;

import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.InvitationRepository;
import dev.obligo.core.platform.identity.OrgMembership;
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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HexFormat;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Email-match enforcement (§10.8) with the same rigor as
 * RefreshTokenReuseTest: this is the check that stands between a leaked
 * invite link and account takeover, so every rejection path is verified
 * both for its HTTP response AND for the DB-observable absence of a side
 * effect (no membership created), not just a status code.
 */
@SpringBootTest(classes = ObligoApplication.class)
@AutoConfigureMockMvc
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class InvitationAcceptanceTest {

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

    @Autowired
    private InvitationRepository invitationRepository;

    private PersonalOrgProvisioningService.SignedInUser inviter;

    @BeforeEach
    void setUp() {
        inviter = provisioningService.findOrProvision(
                "inviter-" + UUID.randomUUID(), "inviter-" + UUID.randomUUID() + "@example.com");
    }

    @AfterEach
    void cleanupInviterOrg() {
        orgMembershipRepository.deleteByUserId(inviter.userId());
        TenantContext.set(inviter.orgId());
        try {
            organizationRepository.delete(inviter.orgId());
        } finally {
            TenantContext.clear();
        }
        userRepository.delete(inviter.userId());
    }

    @Test
    void acceptingWithMatchingEmailSucceedsAndCreatesTheMembership() throws Exception {
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";
        User invitee = createBareUser(invitedEmail);
        UUID invitationId = insertInvitation(invitedEmail, Role.ADMIN, Instant.now().plus(7, ChronoUnit.DAYS));
        String inviteeToken = tokenForBareUser(invitee.id());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + inviteeToken))
                    .andExpect(status().isOk());

            OrgMembership membership = orgMembershipRepository.findByUserId(invitee.id());
            assertThat(membership.orgId()).isEqualTo(inviter.orgId());
            assertThat(membership.role()).isEqualTo(Role.ADMIN);
        } finally {
            orgMembershipRepository.deleteByUserId(invitee.id());
            invitationRepository.deleteById(invitationId);
            userRepository.delete(invitee.id());
        }
    }

    @Test
    void acceptingWithMismatchedEmailIsRejectedAndCreatesNoMembership() throws Exception {
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";
        String actualEmail = "someone-else-" + UUID.randomUUID() + "@example.com";
        User mismatchedUser = createBareUser(actualEmail);
        UUID invitationId = insertInvitation(invitedEmail, Role.ADMIN, Instant.now().plus(7, ChronoUnit.DAYS));
        String userToken = tokenForBareUser(mismatchedUser.id());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + userToken))
                    .andExpect(status().isForbidden());

            assertThat(orgMembershipRepository.existsForUserId(mismatchedUser.id())).isFalse();
        } finally {
            invitationRepository.deleteById(invitationId);
            userRepository.delete(mismatchedUser.id());
        }
    }

    @Test
    void acceptingAnExpiredInvitationIsRejected() throws Exception {
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";
        User invitee = createBareUser(invitedEmail);
        UUID invitationId = insertInvitation(invitedEmail, Role.ADMIN, Instant.now().minus(1, ChronoUnit.DAYS));
        String inviteeToken = tokenForBareUser(invitee.id());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + inviteeToken))
                    .andExpect(status().isNotFound());

            assertThat(orgMembershipRepository.existsForUserId(invitee.id())).isFalse();
        } finally {
            invitationRepository.deleteById(invitationId);
            userRepository.delete(invitee.id());
        }
    }

    @Test
    void acceptingAnAlreadyAcceptedInvitationIsRejectedAndDoesNotDuplicateOrChangeMembership() throws Exception {
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";
        User invitee = createBareUser(invitedEmail);
        UUID invitationId = insertInvitation(invitedEmail, Role.ADMIN, Instant.now().plus(7, ChronoUnit.DAYS));
        String inviteeToken = tokenForBareUser(invitee.id());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + inviteeToken))
                    .andExpect(status().isOk());

            // Replay: the same token, again.
            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + inviteeToken))
                    .andExpect(status().isNotFound());

            OrgMembership membership = orgMembershipRepository.findByUserId(invitee.id());
            assertThat(membership.orgId()).isEqualTo(inviter.orgId());
            assertThat(membership.role()).isEqualTo(Role.ADMIN);
        } finally {
            orgMembershipRepository.deleteByUserId(invitee.id());
            invitationRepository.deleteById(invitationId);
            userRepository.delete(invitee.id());
        }
    }

    @Test
    void acceptingARevokedInvitationIsRejected() throws Exception {
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";
        User invitee = createBareUser(invitedEmail);
        UUID invitationId = insertInvitation(invitedEmail, Role.ADMIN, Instant.now().plus(7, ChronoUnit.DAYS));
        invitationRepository.revoke(invitationId);
        String inviteeToken = tokenForBareUser(invitee.id());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken)
                            .header("Authorization", "Bearer " + inviteeToken))
                    .andExpect(status().isNotFound());

            assertThat(orgMembershipRepository.existsForUserId(invitee.id())).isFalse();
        } finally {
            invitationRepository.deleteById(invitationId);
            userRepository.delete(invitee.id());
        }
    }

    @Test
    void acceptingWhenAlreadyBelongingToAnOrgIsRejectedWithoutTouchingExistingMembership() throws Exception {
        // A real, fully provisioned user — the realistic case, since every
        // signed-in user already has a personal org (§10.8's auto-creation).
        PersonalOrgProvisioningService.SignedInUser existingUser = provisioningService.findOrProvision(
                "existing-" + UUID.randomUUID(), "existing-" + UUID.randomUUID() + "@example.com");
        User existingUserRecord = userRepository.findById(existingUser.userId()).orElseThrow();

        UUID invitationId =
                insertInvitation(existingUserRecord.email(), Role.ADMIN, Instant.now().plus(7, ChronoUnit.DAYS));
        String token = accessTokenService.issue(existingUser.userId(), existingUser.orgId(), existingUser.role());

        try {
            String rawToken = rawTokensByInvitationId.get(invitationId);

            mockMvc.perform(post("/api/v1/invitations/{token}/accept", rawToken).header("Authorization", "Bearer " + token))
                    .andExpect(status().isConflict());

            OrgMembership membership = orgMembershipRepository.findByUserId(existingUser.userId());
            assertThat(membership.orgId()).isEqualTo(existingUser.orgId());
            assertThat(membership.role()).isEqualTo(existingUser.role());
        } finally {
            invitationRepository.deleteById(invitationId);
            orgMembershipRepository.deleteByUserId(existingUser.userId());
            TenantContext.set(existingUser.orgId());
            try {
                organizationRepository.delete(existingUser.orgId());
            } finally {
                TenantContext.clear();
            }
            userRepository.delete(existingUser.userId());
        }
    }

    // --- fixtures ---

    private final java.util.Map<UUID, String> rawTokensByInvitationId = new java.util.HashMap<>();

    private User createBareUser(String email) {
        return userRepository.insert("bare-" + UUID.randomUUID(), email);
    }

    /** org_id/role here are irrelevant to accept() — it only ever reads claims.userId(). */
    private String tokenForBareUser(UUID userId) {
        return accessTokenService.issue(userId, UUID.randomUUID(), Role.MEMBER);
    }

    private UUID insertInvitation(String email, Role role, Instant expiresAt) {
        UUID id = UUID.randomUUID();
        String rawToken = UUID.randomUUID().toString() + UUID.randomUUID();
        invitationRepository.insert(id, inviter.orgId(), email, role, sha256Hex(rawToken), inviter.userId(), expiresAt);
        rawTokensByInvitationId.put(id, rawToken);
        return id;
    }

    private String sha256Hex(String raw) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(digest.digest(raw.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
