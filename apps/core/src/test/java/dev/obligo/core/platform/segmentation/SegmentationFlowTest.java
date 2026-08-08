package dev.obligo.core.platform.segmentation;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import dev.obligo.core.platform.security.AccessTokenService;
import dev.obligo.core.platform.identity.UserRepository;
import dev.obligo.core.platform.tenancy.OrganizationRepository;
import dev.obligo.core.platform.tenancy.TenantContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Real, socket-level integration test for the §21 Phase 3 SSE checkpoint's
 * proxy/stream endpoints, run against a real embedded Tomcat (RANDOM_PORT)
 * and FakeBrainServer standing in for apps/brain (see FakeBrainServer's own
 * javadoc for exactly what this does and doesn't prove). Real JWTs, real
 * Neon-backed user/org provisioning -- only the brain-side HTTP boundary is
 * faked, deliberately, per this checkpoint's own test-strategy decision.
 *
 * poll/heartbeat/max-duration are overridden to small values via
 * @DynamicPropertySource purely so this test suite runs in seconds, not
 * minutes -- production defaults (application.yml) are untouched.
 */
@SpringBootTest(classes = ObligoApplication.class, webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
@EnabledIfEnvironmentVariable(named = "BRAIN_SERVICE_TOKEN", matches = ".+")
class SegmentationFlowTest {

    private static FakeBrainServer fakeBrainServer;

    @DynamicPropertySource
    static void overrideBrainAndTiming(DynamicPropertyRegistry registry) throws IOException {
        fakeBrainServer = new FakeBrainServer(System.getenv("BRAIN_SERVICE_TOKEN"));
        registry.add("brain.url", fakeBrainServer::baseUrl);
        registry.add("segmentation.poll-interval-ms", () -> "200");
        registry.add("segmentation.heartbeat-interval-ms", () -> "500");
        registry.add("segmentation.max-stream-duration-seconds", () -> "3");
    }

    @AfterAll
    static void stopFakeBrainServer() {
        if (fakeBrainServer != null) {
            fakeBrainServer.close();
        }
    }

    @LocalServerPort
    private int port;

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

    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();

    private PersonalOrgProvisioningService.SignedInUser owner;
    private String token;
    private UUID sourceId;

    @BeforeEach
    void setUp() {
        fakeBrainServer.reset();
        owner = provisioningService.findOrProvision(
                "seg-owner-" + UUID.randomUUID(), "seg-owner-" + UUID.randomUUID() + "@example.com");
        token = accessTokenService.issue(owner.userId(), owner.orgId(), owner.role());
        sourceId = UUID.randomUUID();
    }

    @AfterEach
    void tearDown() {
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
    void triggerReturns202AndForwardsBrainsAcceptedResponse() throws Exception {
        fakeBrainServer.enqueuePostResponse(202, "{\"source_id\":\"" + sourceId + "\",\"status\":\"QUEUED\"}");

        HttpResponse<String> response = postSegment();

        assertThat(response.statusCode()).isEqualTo(202);
        JsonNode body = objectMapper.readTree(response.body());
        assertThat(body.get("sourceId").asText()).isEqualTo(sourceId.toString());
        assertThat(body.get("status").asText()).isEqualTo("QUEUED");
        assertThat(fakeBrainServer.postCallCount()).isEqualTo(1);
    }

    @Test
    void triggerReturns404WhenBrainSaysSourceNotFound() throws Exception {
        fakeBrainServer.enqueuePostResponse(404, "{\"detail\":\"source not found\"}");

        HttpResponse<String> response = postSegment();

        assertThat(response.statusCode()).isEqualTo(404);
    }

    @Test
    void triggerReturns409AndForwardsBrainsConflictDetail() throws Exception {
        fakeBrainServer.enqueuePostResponse(409, "{\"detail\":\"source already has a segmentation job\"}");

        HttpResponse<String> response = postSegment();

        assertThat(response.statusCode()).isEqualTo(409);
        JsonNode body = objectMapper.readTree(response.body());
        assertThat(body.get("error").asText()).isEqualTo("source already has a segmentation job");
    }

    @Test
    void triggerReturns503AndForwardsBrainsQueueUnavailableDetail() throws Exception {
        fakeBrainServer.enqueuePostResponse(503, "{\"detail\":\"failed to enqueue: broker unreachable\"}");

        HttpResponse<String> response = postSegment();

        assertThat(response.statusCode()).isEqualTo(503);
        JsonNode body = objectMapper.readTree(response.body());
        assertThat(body.get("error").asText()).isEqualTo("failed to enqueue: broker unreachable");
    }

    @Test
    @Timeout(10)
    void streamEmitsOneStatusEventPerRealChangeThenClosesOnTerminal() throws Exception {
        fakeBrainServer.enqueueGetResponse(200, statusJson("QUEUED", 0, null, null));
        fakeBrainServer.enqueueGetResponse(200, statusJson("PROCESSING", 0, null, null));
        fakeBrainServer.enqueueGetResponse(200, statusJson("SUCCEEDED", 0, 12, null));

        List<String> lines = openStreamAndReadAllLines();

        List<String> statusPayloads = extractEventData(lines, "status");
        assertThat(statusPayloads).hasSize(3);
        assertThat(statusPayloads.get(0)).contains("\"status\":\"QUEUED\"");
        assertThat(statusPayloads.get(1)).contains("\"status\":\"PROCESSING\"");
        assertThat(statusPayloads.get(2)).contains("\"status\":\"SUCCEEDED\"").contains("\"segmentCount\":12");

        // Exactly one GET per real transition, not once per poll tick --
        // FakeBrainServer clamps at the last enqueued response, so a fourth
        // call would silently return SUCCEEDED again; the loop must not
        // have made one, since it should have completed the stream on
        // the third.
        assertThat(fakeBrainServer.getCallCount()).isEqualTo(3);
    }

    @Test
    @Timeout(10)
    void streamSendsHeartbeatsAndClosesAfterMaxDurationWhenJobNeverTerminates() throws Exception {
        // A single QUEUED response, clamped and repeated for every poll --
        // the job never reaches a terminal state within this test.
        fakeBrainServer.enqueueGetResponse(200, statusJson("QUEUED", 0, null, null));

        long startNanos = System.nanoTime();
        List<String> lines = openStreamAndReadAllLines();
        Duration elapsed = Duration.ofNanos(System.nanoTime() - startNanos);

        long heartbeatCount = lines.stream().filter(l -> l.startsWith(":") && l.contains("ping")).count();
        assertThat(heartbeatCount).isGreaterThan(0);

        List<String> timeoutPayloads = extractEventData(lines, "timeout");
        assertThat(timeoutPayloads).hasSize(1);

        // max-stream-duration is overridden to 3s; the stream must close at
        // roughly that bound, not immediately and not indefinitely.
        assertThat(elapsed).isGreaterThanOrEqualTo(Duration.ofSeconds(3));
        assertThat(elapsed).isLessThan(Duration.ofSeconds(8));
    }

    @Test
    @Timeout(10)
    void clientDisconnectStopsServerSidePolling() throws Exception {
        fakeBrainServer.enqueueGetResponse(200, statusJson("QUEUED", 0, null, null));

        HttpClient disconnectableClient = HttpClient.newHttpClient();
        try {
            HttpRequest request = HttpRequest.newBuilder(streamUri())
                    .header("Authorization", "Bearer " + token)
                    .GET()
                    .build();
            HttpResponse<Stream<String>> response =
                    disconnectableClient.send(request, HttpResponse.BodyHandlers.ofLines());
            assertThat(response.statusCode()).isEqualTo(200);

            // Consume the first line to confirm the stream is genuinely live,
            // then abort the connection from the client side rather than
            // reading to completion. close() (JDK 21) does a *graceful*
            // shutdown -- it waits for in-flight exchanges to finish on
            // their own, which this one never will, so it hangs for this
            // still-open stream. shutdownNow() forcibly tears down the
            // in-flight connection instead, which is the actual disconnect
            // this test needs to simulate.
            response.body().findFirst();
            disconnectableClient.shutdownNow();

            // A broken pipe only surfaces on the next write attempt -- with
            // status unchanged, the loop wouldn't try to write again until
            // the next heartbeat is due, which makes detection timing
            // depend on heartbeat cadence. Queuing a real status change
            // forces the very next poll iteration to attempt a send(),
            // making detection fast and deterministic instead of tied to
            // the heartbeat interval.
            fakeBrainServer.enqueueGetResponse(200, statusJson("PROCESSING", 0, null, null));

            Thread.sleep(1000); // let the next poll cycle's failed send land
            int firstSample = fakeBrainServer.getCallCount();
            Thread.sleep(800);
            int secondSample = fakeBrainServer.getCallCount();

            assertThat(secondSample)
                    .as("polling must stop once the client disconnects, not continue until max-stream-duration")
                    .isEqualTo(firstSample);
        } finally {
            disconnectableClient.shutdownNow();
        }
    }

    private HttpResponse<String> postSegment() throws Exception {
        HttpRequest request = HttpRequest.newBuilder(URI.create("http://localhost:" + port + "/api/v1/sources/"
                        + sourceId + "/segment"))
                .header("Authorization", "Bearer " + token)
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    }

    private URI streamUri() {
        return URI.create("http://localhost:" + port + "/api/v1/sources/" + sourceId + "/segment/stream");
    }

    private List<String> openStreamAndReadAllLines() throws Exception {
        HttpRequest request = HttpRequest.newBuilder(streamUri())
                .header("Authorization", "Bearer " + token)
                .GET()
                .build();
        HttpResponse<Stream<String>> response = httpClient.send(request, HttpResponse.BodyHandlers.ofLines());
        assertThat(response.statusCode()).isEqualTo(200);
        return response.body().collect(Collectors.toList());
    }

    /** SSE "data: <payload>" lines for a given named event, in order, payload only. */
    private static List<String> extractEventData(List<String> lines, String eventName) {
        List<String> result = new java.util.ArrayList<>();
        boolean inTargetEvent = false;
        for (String line : lines) {
            if (line.startsWith("event:")) {
                inTargetEvent = line.substring("event:".length()).trim().equals(eventName);
            } else if (inTargetEvent && line.startsWith("data:")) {
                result.add(line.substring("data:".length()).trim());
                inTargetEvent = false;
            } else if (line.isEmpty()) {
                inTargetEvent = false;
            }
        }
        return result;
    }

    private static String statusJson(String status, int attemptCount, Integer segmentCount, String lastError) {
        return "{\"source_id\":\"" + UUID.randomUUID() + "\",\"status\":\"" + status + "\",\"attempt_count\":"
                + attemptCount + ",\"segment_count\":" + (segmentCount == null ? "null" : segmentCount)
                + ",\"last_error\":" + (lastError == null ? "null" : "\"" + lastError + "\"") + "}";
    }
}
