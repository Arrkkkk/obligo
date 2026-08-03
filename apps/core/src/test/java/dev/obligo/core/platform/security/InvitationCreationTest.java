package dev.obligo.core.platform.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.InvitationRepository;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import dev.obligo.core.platform.identity.Role;
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
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = ObligoApplication.class)
@AutoConfigureMockMvc
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class InvitationCreationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

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

    private PersonalOrgProvisioningService.SignedInUser owner;
    private final List<UUID> createdInvitationIds = new ArrayList<>();

    @BeforeEach
    void setUp() {
        owner = provisioningService.findOrProvision(
                "inviter-" + UUID.randomUUID(), "inviter-" + UUID.randomUUID() + "@example.com");
    }

    @AfterEach
    void cleanup() {
        createdInvitationIds.forEach(invitationRepository::deleteById);

        orgMembershipRepository.deleteByUserId(owner.userId());
        TenantContext.set(owner.orgId());
        try {
            organizationRepository.delete(owner.orgId());
        } finally {
            TenantContext.clear();
        }
        userRepository.delete(owner.userId());
    }

    @Test
    void creatingAnInvitationRequiresMemberInviteCapability() throws Exception {
        String memberToken = accessTokenService.issue(owner.userId(), owner.orgId(), Role.MEMBER);

        mockMvc.perform(post("/api/v1/org/invitations")
                        .header("Authorization", "Bearer " + memberToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"invitee@example.com\",\"role\":\"MEMBER\"}"))
                .andExpect(status().isForbidden());
    }

    @Test
    void ownerCanCreateAnInvitationThatPreviewsCorrectly() throws Exception {
        String actorToken = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";

        String rawToken = createInvitation(actorToken, invitedEmail, "MEMBER");
        String expectedOrgName =
                userRepository.findById(owner.userId()).orElseThrow().email() + "'s Organization";
        String ownerEmail = userRepository.findById(owner.userId()).orElseThrow().email();

        mockMvc.perform(get("/api/v1/invitations/{token}", rawToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.orgName").value(expectedOrgName))
                .andExpect(jsonPath("$.role").value("MEMBER"))
                .andExpect(jsonPath("$.invitedByEmail").value(ownerEmail));
    }

    @Test
    void reInvitingTheSameEmailRotatesTheTokenRatherThanReusingIt() throws Exception {
        String actorToken = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        String invitedEmail = "invitee-" + UUID.randomUUID() + "@example.com";

        String firstToken = createInvitation(actorToken, invitedEmail, "MEMBER");
        String secondToken = createInvitation(actorToken, invitedEmail, "ADMIN");

        mockMvc.perform(get("/api/v1/invitations/{token}", firstToken)).andExpect(status().isNotFound());

        mockMvc.perform(get("/api/v1/invitations/{token}", secondToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.role").value("ADMIN"));
    }

    @Test
    void responseIncludesAPreviewUrlSinceNoEmailIsSentYet() throws Exception {
        String actorToken = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());

        MvcResult result = mockMvc.perform(post("/api/v1/org/invitations")
                        .header("Authorization", "Bearer " + actorToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"invitee-" + UUID.randomUUID() + "@example.com\",\"role\":\"MEMBER\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.previewUrl").value(containsString("/invitations/")))
                .andReturn();

        @SuppressWarnings("unchecked")
        Map<String, Object> body = objectMapper.readValue(result.getResponse().getContentAsString(), Map.class);
        createdInvitationIds.add(UUID.fromString((String) body.get("invitationId")));
    }

    @SuppressWarnings("unchecked")
    private String createInvitation(String actorToken, String email, String role) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/v1/org/invitations")
                        .header("Authorization", "Bearer " + actorToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"role\":\"" + role + "\"}"))
                .andExpect(status().isOk())
                .andReturn();

        Map<String, Object> body = objectMapper.readValue(result.getResponse().getContentAsString(), Map.class);
        createdInvitationIds.add(UUID.fromString((String) body.get("invitationId")));
        return (String) body.get("token");
    }
}
