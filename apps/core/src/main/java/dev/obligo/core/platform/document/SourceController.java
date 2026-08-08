package dev.obligo.core.platform.document;

import dev.obligo.core.platform.security.AccessTokenClaims;
import dev.obligo.core.platform.segmentation.BrainClientUnavailableException;
import dev.obligo.core.platform.segmentation.SegmentationJobNotFoundException;
import dev.obligo.core.platform.segmentation.SegmentationService;
import dev.obligo.core.platform.segmentation.TriggerResult;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Map;
import java.util.UUID;

/**
 * No org_id ever comes from the client (same discipline as every other
 * controller in this codebase) -- upload-intent and commit both operate on
 * claims.orgId() only. sources also has RLS (V10), so this is
 * belt-and-suspenders on top of the database's own enforcement, not the
 * only thing standing between one org and another org's rows. The
 * segmentation trigger/stream endpoints below carry that same discipline
 * forward into the org_id passed to apps/brain -- it's always
 * claims.orgId(), never anything read from the request.
 */
@RestController
@RequestMapping("/api/v1/sources")
public class SourceController {

    private final SourceUploadService sourceUploadService;
    private final SegmentationService segmentationService;

    public SourceController(SourceUploadService sourceUploadService, SegmentationService segmentationService) {
        this.sourceUploadService = sourceUploadService;
        this.segmentationService = segmentationService;
    }

    @PostMapping("/upload-intent")
    @PreAuthorize("hasAuthority('source:upload')")
    public ResponseEntity<Map<String, Object>> uploadIntent(
            Authentication authentication, @RequestBody UploadIntentRequest request) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        try {
            SourceUploadService.UploadIntentResult result = sourceUploadService.requestUploadIntent(
                    claims.orgId(),
                    claims.userId(),
                    request.filename(),
                    request.sizeBytes(),
                    request.sha256(),
                    request.mimeType());

            return switch (result) {
                case SourceUploadService.UploadIntentResult.Deduplicated d -> ResponseEntity.ok(
                        Map.of("sourceId", d.sourceId(), "deduplicated", true));
                case SourceUploadService.UploadIntentResult.Created c -> ResponseEntity.ok(Map.of(
                        "sourceId", c.sourceId(),
                        "deduplicated", false,
                        "uploadUrl", c.uploadUrl(),
                        "storageKey", c.storageKey()));
                case SourceUploadService.UploadIntentResult.InvalidRequest invalid -> ResponseEntity.badRequest()
                        .body(Map.of("error", invalid.reason()));
            };
        } catch (BlobStoreUnavailableException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Storage is temporarily unavailable; please retry."));
        }
    }

    @PostMapping("/{id}/commit")
    @PreAuthorize("hasAuthority('source:upload')")
    public ResponseEntity<Map<String, Object>> commit(Authentication authentication, @PathVariable UUID id) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        try {
            CommitResult result = sourceUploadService.commit(claims.orgId(), id);

            return switch (result) {
                case CommitResult.Committed c -> ResponseEntity.status(HttpStatus.ACCEPTED)
                        .body(Map.of("sourceId", c.sourceId(), "status", "UPLOADED"));
                case CommitResult.NotFound ignored -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Source not found."));
                case CommitResult.ObjectNotFound ignored -> ResponseEntity.status(HttpStatus.CONFLICT)
                        .body(Map.of(
                                "error",
                                "Uploaded object not found in storage -- the PUT to the signed URL may not have completed yet."));
                case CommitResult.Invalid invalid -> ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                        .body(Map.of("error", invalid.reason()));
                case CommitResult.AlreadyRejected rejected -> ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                        .body(Map.of("error", rejected.reason()));
                case CommitResult.Expired expired -> ResponseEntity.status(HttpStatus.GONE)
                        .body(Map.of("error", expired.reason()));
            };
        } catch (BlobStoreUnavailableException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Storage is temporarily unavailable; please retry."));
        }
    }

    /**
     * Proxies to apps/brain's POST /segment (§21 Phase 3 SSE checkpoint).
     * Gated on source:upload, not a new capability -- triggering
     * segmentation is part of the ingest pipeline the uploader themselves
     * sets in motion, not a new trust boundary distinct from uploading
     * itself.
     */
    @PostMapping("/{id}/segment")
    @PreAuthorize("hasAuthority('source:upload')")
    public ResponseEntity<Map<String, Object>> segment(Authentication authentication, @PathVariable UUID id) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        try {
            TriggerResult result = segmentationService.trigger(claims.orgId(), id);
            return switch (result) {
                case TriggerResult.Accepted accepted -> ResponseEntity.status(HttpStatus.ACCEPTED)
                        .body(Map.of("sourceId", accepted.sourceId(), "status", accepted.status()));
                case TriggerResult.NotFound ignored -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Source not found."));
                case TriggerResult.Conflict conflict -> ResponseEntity.status(HttpStatus.CONFLICT)
                        .body(Map.of("error", conflict.detail()));
                case TriggerResult.QueueUnavailable queueUnavailable -> ResponseEntity.status(
                                HttpStatus.SERVICE_UNAVAILABLE)
                        .body(Map.of("error", queueUnavailable.detail()));
            };
        } catch (BrainClientUnavailableException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Segmentation is temporarily unavailable; please retry."));
        }
    }

    /**
     * SSE status stream (§21 Phase 3, the last unmet Phase 3 acceptance
     * criterion) -- gated on source:read since this is a read of a job's
     * status, not an upload action. Deliberately a plain Bearer-authenticated
     * GET, not native EventSource + a URL-embedded ticket: the frontend
     * connects with fetch() and a normal Authorization header, so this
     * endpoint needs no new auth mechanism beyond what Spring Security
     * already enforces on every other endpoint here.
     */
    @GetMapping(path = "/{id}/segment/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @PreAuthorize("hasAuthority('source:read')")
    public SseEmitter segmentStream(Authentication authentication, @PathVariable UUID id) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        try {
            return segmentationService.streamStatus(claims.orgId(), id);
        } catch (SegmentationJobNotFoundException e) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, e.getMessage());
        } catch (BrainClientUnavailableException e) {
            throw new ResponseStatusException(
                    HttpStatus.SERVICE_UNAVAILABLE, "Segmentation is temporarily unavailable; please retry.");
        }
    }

    public record UploadIntentRequest(String filename, long sizeBytes, String sha256, String mimeType) {}
}
