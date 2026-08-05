package dev.obligo.core.platform.document;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.HexFormat;
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
     *
     * Package-private, not private: SourceCommitGateway's gatekeep() needs
     * the same value for its own staleness check.
     */
    static final Duration MAX_PENDING_AGE = Duration.ofMinutes(30);

    private final SourceRepository sourceRepository;
    private final SourceCommitGateway sourceCommitGateway;
    private final PdfStructuralValidator pdfStructuralValidator = new PdfStructuralValidator();
    private final ObjectProvider<BlobStore> blobStoreProvider;

    /**
     * ObjectProvider, not a direct BlobStore dependency: BlobStoreConfig's
     * bean is @Conditional on Supabase credentials being present (same
     * pattern as SecurityConfig's ObjectProvider<ClientRegistrationRepository>
     * for Google), so no bean may exist at all. Constructor injection of
     * BlobStore directly would fail bean creation for this whole service --
     * and therefore for every endpoint under /api/v1/sources, including
     * ones that don't touch storage -- the moment Supabase isn't
     * configured. requireBlobStore() below is where that becomes a
     * deliberate, typed, lazy failure instead.
     */
    public SourceUploadService(
            SourceRepository sourceRepository,
            SourceCommitGateway sourceCommitGateway,
            ObjectProvider<BlobStore> blobStoreProvider) {
        this.sourceRepository = sourceRepository;
        this.sourceCommitGateway = sourceCommitGateway;
        this.blobStoreProvider = blobStoreProvider;
    }

    private BlobStore requireBlobStore() {
        BlobStore blobStore = blobStoreProvider.getIfAvailable();
        if (blobStore == null) {
            throw new BlobStoreUnavailableException(
                    "Storage is not configured in this environment (SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY/SUPABASE_STORAGE_BUCKET not set).");
        }
        return blobStore;
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

        BlobStore.SignedUpload signedUpload = requireBlobStore().createSignedUploadUrl(storageKey);

        sourceRepository.insert(sourceId, orgId, uploadedBy, filename, sizeBytes, normalizedSha256, storageKey);

        return new UploadIntentResult.Created(sourceId, signedUpload.uploadUrl(), storageKey);
    }

    /**
     * Three phases, none of which is itself @Transactional -- the two that
     * need a transaction (gatekeep, finalizeVerification) live on
     * SourceCommitGateway, a separate bean, and are called through it
     * rather than as private methods here. See SourceCommitGateway's
     * Javadoc for exactly why that separation is required, not just tidy.
     *
     * Before this design: the whole method was one @Transactional block
     * holding findByIdForUpdate's row lock across a HEAD and a 5-byte
     * range GET -- both sub-second, so holding a pooled connection that
     * long was reasonable, and Postgres's lock fully serialized concurrent
     * commit() calls on the same source for free (the loser blocks, then
     * sees the winner's committed state once unblocked -- no redundant
     * work, no race). Once commit needs a full download (up to 50 MB) and
     * a PDFBox parse (up to PdfStructuralValidator's 10s timeout), holding
     * that same lock for potentially several seconds risks exhausting this
     * app's small Hikari pool (5 connections; 1 in tests) under
     * concurrent large-file commits. Splitting the lock into "gatekeep,
     * release" and "verify unlocked" then "finalize, guarded" trades that
     * held-lock cost for a reopened race window -- two requests could both
     * pass gatekeep() as PENDING and both redundantly do the expensive
     * verification -- which finalizeVerification's WHERE status='PENDING'
     * guard, plus its zero-rows-affected reconciliation read, is the new
     * mitigation for. That race is a consequence of this restructuring,
     * not a bug the restructuring discovered.
     *
     * Idempotent for retries by construction, not via an Idempotency-Key
     * header (see CLAUDE.md's carried-forward debt note on that gap):
     * re-calling this after a source is already UPLOADED re-verifies via
     * headObject but never re-runs markUploaded, so there's no double
     * side effect.
     */
    public CommitResult commit(UUID orgId, UUID sourceId) {
        SourceCommitGateway.GatekeepOutcome outcome = sourceCommitGateway.gatekeep(orgId, sourceId);
        if (outcome instanceof SourceCommitGateway.GatekeepOutcome.Terminal terminal) {
            return terminal.result();
        }
        Source source = ((SourceCommitGateway.GatekeepOutcome.ProceedToVerify) outcome).source();

        VerificationOutcome verification = verify(source);
        if (verification instanceof VerificationOutcome.ObjectNotFound) {
            // No DB write: the row stays PENDING, retryable once the client's
            // PUT actually lands, same as before this restructuring.
            return new CommitResult.ObjectNotFound();
        }

        return sourceCommitGateway.finalizeVerification(orgId, sourceId, verification);
    }

    /**
     * The unlocked, expensive phase -- no transaction, no lock, touches no
     * SQL at all. Operates purely on the in-memory Source snapshot
     * gatekeep() already verified belongs to the caller's org, and on
     * BlobStore calls scoped by that snapshot's storageKey (org_id baked
     * into the path since upload-intent time, never re-derived here).
     */
    private VerificationOutcome verify(Source source) {
        BlobStore blobStore = requireBlobStore();

        Optional<BlobStore.ObjectMetadata> metadata = blobStore.headObject(source.storageKey());
        if (metadata.isEmpty()) {
            return new VerificationOutcome.ObjectNotFound();
        }
        if (metadata.get().sizeBytes() != source.byteSize()) {
            return new VerificationOutcome.Invalid("declared size (%d) does not match the uploaded object's size (%d)"
                    .formatted(source.byteSize(), metadata.get().sizeBytes()));
        }

        byte[] header = blobStore.readRange(source.storageKey(), 0, PDF_SNIFF_BYTES - 1);
        if (!PdfMagicBytes.isPdf(header)) {
            return new VerificationOutcome.Invalid("uploaded object is not a valid PDF (magic-byte check failed)");
        }

        // Only reached after the cheap magic-byte pre-check passes -- avoids
        // paying for a full download on obviously-wrong uploads. Bounded to
        // FileSecurityLimits.MAX_SOURCE_SIZE_BYTES: the size-equality check
        // above already confirmed the object is no larger than the
        // declared size, which upload-intent already capped.
        byte[] fullBytes = blobStore.readObject(source.storageKey());

        String actualSha256 = sha256Hex(fullBytes);
        if (!actualSha256.equals(source.sha256())) {
            return new VerificationOutcome.Invalid(
                    "uploaded object's sha256 does not match the declared value (recomputed server-side)");
        }

        Optional<String> structuralViolation = pdfStructuralValidator.findViolation(fullBytes, source.byteSize());
        if (structuralViolation.isPresent()) {
            return new VerificationOutcome.Invalid(structuralViolation.get());
        }

        return new VerificationOutcome.Valid("application/pdf");
    }

    private static String sha256Hex(byte[] bytes) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(digest.digest(bytes));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }
}
