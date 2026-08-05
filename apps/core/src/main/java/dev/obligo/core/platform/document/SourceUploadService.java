package dev.obligo.core.platform.document;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.Instant;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;

@Service
public class SourceUploadService {

    private static final Pattern SHA256_HEX = Pattern.compile("^[0-9a-f]{64}$");
    private static final int PDF_SNIFF_BYTES = 5; // "%PDF-"

    /**
     * Supabase's upload-sign endpoint fixes its token at ~2h regardless of
     * what we request (confirmed live, not assumed -- see
     * SupabaseStorageBlobStore's Javadoc), which is wider than blueprint
     * §11.2's 5 min target. Verified separately that a leaked/replayed URL
     * can't do anything once the legitimate upload lands (upsert:false, a
     * path-bound signature, no read scope) -- the only real exposure is a
     * pre-upload race on an *abandoned* intent, for as long as its token
     * stays live. This caps that window at 30 min server-side: comfortably
     * over how long a real upload plus a slow connection takes, but far
     * under the 2h Supabase actually grants, so an abandoned intent can't
     * sit race-able for the full token lifetime.
     */
    private static final Duration MAX_PENDING_AGE = Duration.ofMinutes(30);

    private final SourceRepository sourceRepository;
    private final BlobStore blobStore;

    public SourceUploadService(SourceRepository sourceRepository, BlobStore blobStore) {
        this.sourceRepository = sourceRepository;
        this.blobStore = blobStore;
    }

    public sealed interface UploadIntentResult {
        record Deduplicated(UUID sourceId) implements UploadIntentResult {}

        record Created(UUID sourceId, String uploadUrl, String storageKey) implements UploadIntentResult {}

        record InvalidRequest(String reason) implements UploadIntentResult {}
    }

    /**
     * Deliberately not @Transactional itself: it calls out to Supabase
     * (createSignedUploadUrl) between the dedup read and the row insert,
     * and a DB transaction should never sit open across external I/O --
     * each repository call gets its own short transaction instead. This
     * also gets §11.7's "no orphan DB row" guarantee for free: if
     * createSignedUploadUrl throws, insert() is simply never called.
     */
    public UploadIntentResult requestUploadIntent(
            UUID orgId, UUID uploadedBy, String filename, long sizeBytes, String sha256, String declaredMimeType) {
        if (filename == null || filename.isBlank()) {
            return new UploadIntentResult.InvalidRequest("filename is required.");
        }
        if (!FileSecurityLimits.ALLOWED_MIME_TYPES.contains(declaredMimeType)) {
            return new UploadIntentResult.InvalidRequest("Only application/pdf is supported in this phase.");
        }
        if (sizeBytes <= 0 || sizeBytes > FileSecurityLimits.MAX_SOURCE_SIZE_BYTES) {
            return new UploadIntentResult.InvalidRequest(
                    "File size must be between 1 and " + FileSecurityLimits.MAX_SOURCE_SIZE_BYTES + " bytes.");
        }
        if (sha256 == null || !SHA256_HEX.matcher(sha256.toLowerCase(Locale.ROOT)).matches()) {
            return new UploadIntentResult.InvalidRequest("sha256 must be 64 hex characters.");
        }
        String normalizedSha256 = sha256.toLowerCase(Locale.ROOT);

        Optional<Source> existing = sourceRepository.findByOrgAndSha256Uploaded(orgId, normalizedSha256);
        if (existing.isPresent()) {
            return new UploadIntentResult.Deduplicated(existing.get().id());
        }

        UUID sourceId = UUID.randomUUID();
        // §11.1 path convention: {org_id}/{source_id}/v{n}/{sha256}.{ext}. No
        // source_versions table yet (see V10's comment), so n is always 1.
        String storageKey = "%s/%s/v1/%s.pdf".formatted(orgId, sourceId, normalizedSha256);

        BlobStore.SignedUpload signedUpload = blobStore.createSignedUploadUrl(storageKey);

        sourceRepository.insert(sourceId, orgId, uploadedBy, filename, sizeBytes, normalizedSha256, storageKey);

        return new UploadIntentResult.Created(sourceId, signedUpload.uploadUrl(), storageKey);
    }

    public sealed interface CommitResult {
        record Committed(UUID sourceId) implements CommitResult {}

        record NotFound() implements CommitResult {}

        record ObjectNotFound() implements CommitResult {}

        record Invalid(String reason) implements CommitResult {}

        record AlreadyRejected(String reason) implements CommitResult {}

        record Expired(String reason) implements CommitResult {}
    }

    /**
     * The whole method is @Transactional, holding findByIdForUpdate's row
     * lock across the headObject/readRange calls to Supabase -- a
     * deliberate tradeoff (a DB transaction spanning two small, bounded
     * network calls) rather than the usual "no I/O inside a transaction"
     * rule: this is exactly the operation that needs serialization against
     * a concurrent commit retry, and the calls involved are a HEAD and a
     * 5-byte range GET, not a 50 MB transfer.
     *
     * Idempotent for retries by construction, not via an Idempotency-Key
     * header (see CLAUDE.md's carried-forward debt note on that gap):
     * re-calling this after a source is already UPLOADED re-verifies via
     * headObject but never re-runs markUploaded, so there's no double
     * side effect.
     */
    @Transactional
    public CommitResult commit(UUID orgId, UUID sourceId) {
        Optional<Source> maybeSource = sourceRepository.findByIdForUpdate(orgId, sourceId);
        if (maybeSource.isEmpty()) {
            return new CommitResult.NotFound();
        }
        Source source = maybeSource.get();

        if (source.status() == SourceStatus.UPLOADED) {
            return blobStore.headObject(source.storageKey()).isPresent()
                    ? new CommitResult.Committed(source.id())
                    : new CommitResult.ObjectNotFound();
        }
        if (source.status() == SourceStatus.REJECTED) {
            return new CommitResult.AlreadyRejected(source.rejectionReason());
        }

        if (source.createdAt().isBefore(Instant.now().minus(MAX_PENDING_AGE))) {
            String reason = "upload intent expired (older than %d minutes); request a new upload-intent"
                    .formatted(MAX_PENDING_AGE.toMinutes());
            sourceRepository.markRejected(orgId, sourceId, reason);
            return new CommitResult.Expired(reason);
        }

        Optional<BlobStore.ObjectMetadata> metadata = blobStore.headObject(source.storageKey());
        if (metadata.isEmpty()) {
            return new CommitResult.ObjectNotFound();
        }
        if (metadata.get().sizeBytes() != source.byteSize()) {
            String reason = "declared size (%d) does not match the uploaded object's size (%d)"
                    .formatted(source.byteSize(), metadata.get().sizeBytes());
            sourceRepository.markRejected(orgId, sourceId, reason);
            return new CommitResult.Invalid(reason);
        }

        byte[] header = blobStore.readRange(source.storageKey(), 0, PDF_SNIFF_BYTES - 1);
        if (!PdfMagicBytes.isPdf(header)) {
            String reason = "uploaded object is not a valid PDF (magic-byte check failed)";
            sourceRepository.markRejected(orgId, sourceId, reason);
            return new CommitResult.Invalid(reason);
        }

        sourceRepository.markUploaded(orgId, sourceId, "application/pdf", Instant.now());
        return new CommitResult.Committed(sourceId);
    }
}
