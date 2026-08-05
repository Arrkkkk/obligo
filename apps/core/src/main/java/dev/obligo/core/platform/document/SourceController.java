package dev.obligo.core.platform.document;

import dev.obligo.core.platform.security.AccessTokenClaims;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

/**
 * No org_id ever comes from the client (same discipline as every other
 * controller in this codebase) -- upload-intent and commit both operate on
 * claims.orgId() only. sources also has RLS (V10), so this is
 * belt-and-suspenders on top of the database's own enforcement, not the
 * only thing standing between one org and another org's rows.
 */
@RestController
@RequestMapping("/api/v1/sources")
public class SourceController {

    private final SourceUploadService sourceUploadService;

    public SourceController(SourceUploadService sourceUploadService) {
        this.sourceUploadService = sourceUploadService;
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

    public record UploadIntentRequest(String filename, long sizeBytes, String sha256, String mimeType) {}
}
