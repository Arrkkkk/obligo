package dev.obligo.core.platform.document;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import dev.obligo.core.platform.identity.Role;
import dev.obligo.core.platform.identity.UserRepository;
import dev.obligo.core.platform.security.AccessTokenService;
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

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Exercises the real presigned-upload flow (§11.2) end to end against real
 * infrastructure: a real Neon branch for sources/RLS, and the real
 * Supabase Storage project the app talks to -- no mocked BlobStore. The PUT
 * to the signed URL is done with a plain JDK HttpClient, standing in for
 * the browser, exactly as it would happen for real (no service-role key
 * involved in that call, only the token embedded in the signed URL).
 */
@SpringBootTest(classes = ObligoApplication.class)
@AutoConfigureMockMvc
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
@EnabledIfEnvironmentVariable(named = "SUPABASE_URL", matches = ".+")
class SourceUploadFlowTest {

    private static final byte[] REAL_PDF_BYTES =
            "%PDF-1.4\n%obligo-test-fixture\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"
                    .getBytes(StandardCharsets.US_ASCII);
    private static final byte[] NOT_A_PDF_BYTES = "this is definitely not a pdf\n".getBytes(StandardCharsets.US_ASCII);

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
    private SourceRepository sourceRepository;

    @Autowired
    private TestSourceBackdater testSourceBackdater;

    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final List<String> storageKeysToDelete = new ArrayList<>();
    // Explicit tracking, not a post-hoc lookup: a source can end this test in
    // PENDING or REJECTED, not just UPLOADED, and the FK from sources to
    // organizations means cleanup must find every one of them regardless of
    // status, or organizationRepository.delete() below fails with a
    // DataIntegrityViolationException.
    private final List<CreatedSource> createdSources = new ArrayList<>();

    private record CreatedSource(UUID orgId, UUID sourceId) {}

    private PersonalOrgProvisioningService.SignedInUser owner;
    private PersonalOrgProvisioningService.SignedInUser otherOrgOwner;

    @BeforeEach
    void setUp() {
        owner = provisioningService.findOrProvision(
                "source-owner-" + UUID.randomUUID(), "owner-" + UUID.randomUUID() + "@example.com");
        otherOrgOwner = provisioningService.findOrProvision(
                "source-other-" + UUID.randomUUID(), "other-" + UUID.randomUUID() + "@example.com");
    }

    @AfterEach
    void cleanup() throws Exception {
        for (String key : storageKeysToDelete) {
            deleteFromStorage(key);
        }
        for (CreatedSource created : createdSources) {
            TenantContext.set(created.orgId());
            try {
                sourceRepository.deleteById(created.orgId(), created.sourceId());
            } finally {
                TenantContext.clear();
            }
        }
        for (PersonalOrgProvisioningService.SignedInUser user : List.of(owner, otherOrgOwner)) {
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
    void realPdfIsUploadedVerifiedAndDeduplicatedOnReupload() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        String sha256 = sha256Hex(REAL_PDF_BYTES);

        Map<String, Object> intent = requestUploadIntent(owner.orgId(), token, "contract.pdf", REAL_PDF_BYTES.length, sha256);
        assertThat(intent.get("deduplicated")).isEqualTo(false);
        String uploadUrl = (String) intent.get("uploadUrl");
        String storageKey = (String) intent.get("storageKey");
        UUID sourceId = UUID.fromString((String) intent.get("sourceId"));
        storageKeysToDelete.add(storageKey);

        putToSignedUrl(uploadUrl, REAL_PDF_BYTES);

        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + token))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.status").value("UPLOADED"));

        // Retrying commit must be idempotent (the scoped fix agreed on for this slice): no error,
        // same outcome, no second write.
        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + token))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.status").value("UPLOADED"));

        // Re-requesting an intent for the same (org, sha256) now finds the committed row instead
        // of minting a new signed URL.
        Map<String, Object> secondIntent =
                requestUploadIntent(owner.orgId(), token, "contract-copy.pdf", REAL_PDF_BYTES.length, sha256);
        assertThat(secondIntent.get("deduplicated")).isEqualTo(true);
        assertThat(secondIntent.get("sourceId")).isEqualTo(sourceId.toString());
    }

    @Test
    void commitRejectsAnObjectThatIsNotActuallyAPdf() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        String sha256 = sha256Hex(NOT_A_PDF_BYTES);

        Map<String, Object> intent =
                requestUploadIntent(owner.orgId(), token, "not-a-contract.pdf", NOT_A_PDF_BYTES.length, sha256);
        String uploadUrl = (String) intent.get("uploadUrl");
        String storageKey = (String) intent.get("storageKey");
        UUID sourceId = UUID.fromString((String) intent.get("sourceId"));
        storageKeysToDelete.add(storageKey);

        // The bucket's own MIME allow-list would normally reject this at PUT time (confirmed
        // separately); declare a PDF content-type to get past that so the app-level magic-byte
        // check at commit is what's actually under test here.
        putToSignedUrl(uploadUrl, NOT_A_PDF_BYTES);

        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + token))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("not a valid PDF")));

        TenantContext.set(owner.orgId());
        try {
            assertThat(sourceRepository.findByIdForUpdate(owner.orgId(), sourceId))
                    .hasValueSatisfying(s -> assertThat(s.status()).isEqualTo(SourceStatus.REJECTED));
        } finally {
            TenantContext.clear();
        }
    }

    @Test
    void uploadIntentRejectsAFileLargerThanTheCap() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());

        mockMvc.perform(post("/api/v1/sources/upload-intent")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(new SourceController.UploadIntentRequest(
                                "huge.pdf", FileSecurityLimits.MAX_SOURCE_SIZE_BYTES + 1, sha256Hex(REAL_PDF_BYTES), "application/pdf"))))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("File size")));
    }

    @Test
    void uploadIntentRejectsANonPdfDeclaredMimeType() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());

        mockMvc.perform(post("/api/v1/sources/upload-intent")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(new SourceController.UploadIntentRequest(
                                "spreadsheet.xlsx", 1024, sha256Hex(REAL_PDF_BYTES), "application/vnd.ms-excel"))))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("application/pdf")));
    }

    @Test
    void auditorCannotRequestAnUploadIntent() throws Exception {
        String auditorToken = accessTokenService.issue(owner.userId(), owner.orgId(), Role.AUDITOR);

        mockMvc.perform(post("/api/v1/sources/upload-intent")
                        .header("Authorization", "Bearer " + auditorToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SourceController.UploadIntentRequest("x.pdf", 100, sha256Hex(REAL_PDF_BYTES), "application/pdf"))))
                .andExpect(status().isForbidden());
    }

    @Test
    void commitOnAnotherOrgsSourceIsNotFoundRatherThanLeaked() throws Exception {
        String ownerToken = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        Map<String, Object> intent = requestUploadIntent(
                owner.orgId(), ownerToken, "contract.pdf", REAL_PDF_BYTES.length, sha256Hex(REAL_PDF_BYTES));
        storageKeysToDelete.add((String) intent.get("storageKey"));
        UUID sourceId = UUID.fromString((String) intent.get("sourceId"));

        String otherOrgToken = accessTokenService.issue(otherOrgOwner.userId(), otherOrgOwner.orgId(), otherOrgOwner.role());

        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + otherOrgToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void commitRejectsAPendingSourceOlderThanTheStalenessThreshold() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        Map<String, Object> intent = requestUploadIntent(
                owner.orgId(), token, "abandoned.pdf", REAL_PDF_BYTES.length, sha256Hex(REAL_PDF_BYTES));
        UUID sourceId = UUID.fromString((String) intent.get("sourceId"));
        // No PUT to the signed URL at all -- this is exactly the "abandoned
        // intent" scenario the staleness check exists for (§11.2 gap
        // discussion): the object was never uploaded, and the check must
        // reject on age alone rather than reaching storage at all.

        backdateCreatedAt(owner.orgId(), sourceId, Instant.now().minus(31, java.time.temporal.ChronoUnit.MINUTES));

        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + token))
                .andExpect(status().isGone())
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("expired")));

        TenantContext.set(owner.orgId());
        try {
            assertThat(sourceRepository.findByIdForUpdate(owner.orgId(), sourceId))
                    .hasValueSatisfying(s -> {
                        assertThat(s.status()).isEqualTo(SourceStatus.REJECTED);
                        assertThat(s.rejectionReason()).contains("expired");
                    });
        } finally {
            TenantContext.clear();
        }
    }

    @Test
    void commitStillSucceedsForAPendingSourceUnderTheStalenessThreshold() throws Exception {
        String token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        Map<String, Object> intent = requestUploadIntent(
                owner.orgId(), token, "recent.pdf", REAL_PDF_BYTES.length, sha256Hex(REAL_PDF_BYTES));
        String uploadUrl = (String) intent.get("uploadUrl");
        storageKeysToDelete.add((String) intent.get("storageKey"));
        UUID sourceId = UUID.fromString((String) intent.get("sourceId"));

        // Old, but comfortably inside the 30 min threshold -- proves the
        // check is a real age comparison, not just "reject everything not
        // created this instant."
        backdateCreatedAt(owner.orgId(), sourceId, Instant.now().minus(5, java.time.temporal.ChronoUnit.MINUTES));

        putToSignedUrl(uploadUrl, REAL_PDF_BYTES);

        mockMvc.perform(post("/api/v1/sources/{id}/commit", sourceId).header("Authorization", "Bearer " + token))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.status").value("UPLOADED"));
    }

    private void backdateCreatedAt(UUID orgId, UUID sourceId, Instant createdAt) {
        TenantContext.set(orgId);
        try {
            testSourceBackdater.backdateCreatedAt(orgId, sourceId, createdAt);
        } finally {
            TenantContext.clear();
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> requestUploadIntent(
            UUID orgId, String token, String filename, long sizeBytes, String sha256) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/v1/sources/upload-intent")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SourceController.UploadIntentRequest(filename, sizeBytes, sha256, "application/pdf"))))
                .andExpect(status().isOk())
                .andReturn();
        Map<String, Object> body = objectMapper.readValue(result.getResponse().getContentAsString(), Map.class);
        createdSources.add(new CreatedSource(orgId, UUID.fromString((String) body.get("sourceId"))));
        return body;
    }

    private void putToSignedUrl(String uploadUrl, byte[] bytes) throws Exception {
        HttpRequest request = HttpRequest.newBuilder(URI.create(uploadUrl))
                .header("Content-Type", "application/pdf")
                .PUT(HttpRequest.BodyPublishers.ofByteArray(bytes))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        assertThat(response.statusCode()).as("PUT to signed URL: " + response.body()).isEqualTo(200);
    }

    private void deleteFromStorage(String key) throws Exception {
        String supabaseUrl = System.getenv("SUPABASE_URL");
        String serviceRoleKey = System.getenv("SUPABASE_SERVICE_ROLE_KEY");
        String bucket = System.getenv("SUPABASE_STORAGE_BUCKET");
        HttpRequest request = HttpRequest.newBuilder(URI.create(supabaseUrl + "/storage/v1/object/" + bucket))
                .header("Authorization", "Bearer " + serviceRoleKey)
                .header("Content-Type", "application/json")
                .method("DELETE", HttpRequest.BodyPublishers.ofString("{\"prefixes\":[\"" + key + "\"]}"))
                .build();
        httpClient.send(request, HttpResponse.BodyHandlers.discarding());
    }

    private static String sha256Hex(byte[] bytes) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        return HexFormat.of().formatHex(digest.digest(bytes));
    }
}
