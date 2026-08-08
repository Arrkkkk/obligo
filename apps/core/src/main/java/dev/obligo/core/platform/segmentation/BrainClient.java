package dev.obligo.core.platform.segmentation;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Map;
import java.util.UUID;

/**
 * The apps/core -> apps/brain client for the segmentation trigger/status
 * endpoints (§21 Phase 3 SSE checkpoint). Same RestClient pattern as
 * SupabaseStorageBlobStore: a per-call header (X-Internal-Service-Token
 * here, Authorization there) rather than a client-level default, and
 * exchange() rather than retrieve() wherever more than one non-2xx status
 * is itself a real, documented outcome, not just an error to unwrap.
 *
 * Auth: BRAIN_SERVICE_TOKEN is the same interim shared-secret gate
 * apps/brain's own tests already exercise against it directly -- see
 * CLAUDE.md's debt-list entry on what this does and doesn't prove. This
 * client doesn't widen that gap; it's the first real caller of the
 * mechanism from the Java side, using it exactly as documented.
 */
public class BrainClient {

    private final RestClient restClient;
    private final String serviceToken;

    public BrainClient(RestClient.Builder restClientBuilder, String brainUrl, String serviceToken) {
        this.restClient = restClientBuilder.baseUrl(brainUrl).build();
        this.serviceToken = serviceToken;
    }

    public TriggerResult triggerSegmentation(UUID sourceId, UUID orgId) {
        try {
            return restClient
                    .post()
                    .uri("/api/v1/sources/{id}/segment", sourceId)
                    .header("X-Internal-Service-Token", serviceToken)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("org_id", orgId.toString()))
                    .exchange((request, response) -> {
                        int code = response.getStatusCode().value();
                        return switch (code) {
                            case 202 -> {
                                SegmentTriggerResponse body = response.bodyTo(SegmentTriggerResponse.class);
                                yield new TriggerResult.Accepted(sourceId, body != null ? body.status() : "QUEUED");
                            }
                            case 404 -> new TriggerResult.NotFound();
                            case 409 -> new TriggerResult.Conflict(errorDetail(response));
                            case 503 -> new TriggerResult.QueueUnavailable(errorDetail(response));
                            default -> throw new BrainClientUnavailableException(
                                    "apps/brain returned an undocumented status " + code + " for a segment trigger");
                        };
                    });
        } catch (RestClientException e) {
            throw new BrainClientUnavailableException("apps/brain unreachable while triggering segmentation", e);
        }
    }

    public StatusResult getSegmentationStatus(UUID sourceId, UUID orgId) {
        try {
            return restClient
                    .get()
                    .uri("/api/v1/sources/{id}/segment?org_id={orgId}", sourceId, orgId)
                    .header("X-Internal-Service-Token", serviceToken)
                    .exchange((request, response) -> {
                        int code = response.getStatusCode().value();
                        return switch (code) {
                            case 200 -> {
                                SegmentationStatusResponse body =
                                        response.bodyTo(SegmentationStatusResponse.class);
                                if (body == null) {
                                    throw new BrainClientUnavailableException(
                                            "apps/brain returned an empty 200 body for a segmentation status read");
                                }
                                yield new StatusResult.Found(new SegmentationJobStatus(
                                        body.status(), body.attemptCount(), body.segmentCount(), body.lastError()));
                            }
                            case 404 -> new StatusResult.NotFound();
                            default -> throw new BrainClientUnavailableException(
                                    "apps/brain returned an undocumented status " + code + " for a segmentation status read");
                        };
                    });
        } catch (RestClientException e) {
            throw new BrainClientUnavailableException("apps/brain unreachable while reading segmentation status", e);
        }
    }

    private static String errorDetail(RestClient.RequestHeadersSpec.ConvertibleClientHttpResponse response) {
        try {
            ErrorDetail detail = response.bodyTo(ErrorDetail.class);
            return detail != null && detail.detail() != null ? detail.detail() : "apps/brain returned no error detail";
        } catch (RestClientException e) {
            return "apps/brain returned a non-JSON error body";
        }
    }

    private record SegmentTriggerResponse(@JsonProperty("source_id") String sourceId, String status) {}

    private record SegmentationStatusResponse(
            @JsonProperty("source_id") String sourceId,
            String status,
            @JsonProperty("attempt_count") int attemptCount,
            @JsonProperty("segment_count") Integer segmentCount,
            @JsonProperty("last_error") String lastError) {}

    private record ErrorDetail(String detail) {}
}
