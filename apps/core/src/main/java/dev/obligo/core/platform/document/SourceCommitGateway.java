package dev.obligo.core.platform.document;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * The two short, locked/guarded transactions in commit()'s three-phase
 * design -- pulled into a SEPARATE bean rather than private methods on
 * SourceUploadService for a specific reason: Spring's @Transactional is
 * proxy-based AOP (same mechanism TenantIsolationArchitectureTest checks
 * for), and a proxy cannot intercept self-invocation. SourceUploadService
 * calling this.gatekeep(...) from within itself would silently skip the
 * proxy entirely -- no exception, just no transaction, no
 * TenantConnectionPreparer GUC set, and RLS failing closed (empty results,
 * not a leak, but a completely broken feature) on every call. Calling
 * through a genuinely separate bean, as here, goes through the proxy
 * correctly, same as every SourceRepository call already does.
 *
 * Why commit() needs two SHORT transactions instead of the one long one it
 * used to be: see SourceUploadService.commit()'s Javadoc for the full
 * before/after reasoning. In short, holding findByIdForUpdate's row lock
 * across a full download + PDFBox parse (up to PdfStructuralValidator's
 * 10s timeout) would tie up a pooled DB connection for that whole window --
 * fine for the old HEAD + 5-byte-range calls, not fine now. Splitting the
 * lock into "gatekeep, release" and "finalize, guarded" reopens a race that
 * the old single-transaction design closed for free (Postgres serialized
 * concurrent commits via the held lock, with the loser blocking then
 * observing the winner's committed state) -- finalizeVerification's
 * WHERE status = 'PENDING' guard plus its zero-rows-affected reconciliation
 * read is the new, deliberate mitigation for that reopened race, not a fix
 * for a bug that existed in the old design.
 *
 * Tenant isolation across both calls: org ownership is established exactly
 * once, here, by findByIdForUpdate's WHERE org_id = ? + RLS. Everything
 * SourceUploadService does in between (the whole unlocked verification
 * phase) runs no SQL at all -- it only touches the in-memory Source
 * snapshot returned below and calls BlobStore with that snapshot's
 * storageKey, which already has org_id baked into its path from
 * upload-intent time and is never re-derived from anything client-supplied.
 * finalizeVerification's UPDATE takes orgId as a plain parameter threaded
 * through from the original call, not re-looked-up -- so there's no point
 * in this flow where org scoping is inferred rather than carried forward as
 * already-verified data. This whole guarantee depends on gatekeep,
 * SourceUploadService.verify, and finalizeVerification running
 * synchronously on the one request thread -- see TenantContext's Javadoc
 * for why that matters and what breaks if it stops being true.
 */
@Component
class SourceCommitGateway {

    private static final Duration MAX_PENDING_AGE = SourceUploadService.MAX_PENDING_AGE;

    private final SourceRepository sourceRepository;
    private final ObjectProvider<BlobStore> blobStoreProvider;

    SourceCommitGateway(SourceRepository sourceRepository, ObjectProvider<BlobStore> blobStoreProvider) {
        this.sourceRepository = sourceRepository;
        this.blobStoreProvider = blobStoreProvider;
    }

    sealed interface GatekeepOutcome {
        record Terminal(CommitResult result) implements GatekeepOutcome {}

        record ProceedToVerify(Source source) implements GatekeepOutcome {}
    }

    /**
     * Locked: findByIdForUpdate holds the row lock for exactly this short
     * method, resolving every terminal state that doesn't need the
     * expensive verification work (not found, already rejected, stale,
     * already-uploaded retry). If none apply, releases the lock (this
     * transaction ends) and hands back a plain in-memory Source snapshot --
     * not a live cursor -- for the caller to verify without holding
     * anything.
     */
    @Transactional
    GatekeepOutcome gatekeep(UUID orgId, UUID sourceId) {
        Optional<Source> maybeSource = sourceRepository.findByIdForUpdate(orgId, sourceId);
        if (maybeSource.isEmpty()) {
            return new GatekeepOutcome.Terminal(new CommitResult.NotFound());
        }
        Source source = maybeSource.get();

        if (source.status() == SourceStatus.UPLOADED) {
            CommitResult result = requireBlobStore().headObject(source.storageKey()).isPresent()
                    ? new CommitResult.Committed(source.id())
                    : new CommitResult.ObjectNotFound();
            return new GatekeepOutcome.Terminal(result);
        }
        if (source.status() == SourceStatus.REJECTED) {
            return new GatekeepOutcome.Terminal(new CommitResult.AlreadyRejected(source.rejectionReason()));
        }
        if (source.createdAt().isBefore(Instant.now().minus(MAX_PENDING_AGE))) {
            String reason = "upload intent expired (older than %d minutes); request a new upload-intent"
                    .formatted(MAX_PENDING_AGE.toMinutes());
            sourceRepository.markRejected(orgId, sourceId, reason);
            return new GatekeepOutcome.Terminal(new CommitResult.Expired(reason));
        }

        return new GatekeepOutcome.ProceedToVerify(source);
    }

    /**
     * Guarded, not locked: the WHERE status = 'PENDING' clause on
     * markUploaded/markRejected is what actually prevents a double-write
     * now that no lock spans the verification work. If it affects zero
     * rows, a concurrent commit already finalized this source while we
     * were downloading/parsing -- reconcile by reading the actual current
     * state and returning that, rather than trusting our own now-stale
     * verdict.
     */
    @Transactional
    CommitResult finalizeVerification(UUID orgId, UUID sourceId, VerificationOutcome verification) {
        boolean updated =
                switch (verification) {
                    case VerificationOutcome.Valid valid -> sourceRepository.markUploaded(
                            orgId, sourceId, valid.mimeType(), Instant.now());
                    case VerificationOutcome.Invalid invalid -> sourceRepository.markRejected(
                            orgId, sourceId, invalid.reason());
                    case VerificationOutcome.ObjectNotFound ignored -> throw new IllegalStateException(
                            "unreachable: ObjectNotFound is handled by the caller before finalizeVerification is invoked");
                };

        if (!updated) {
            return sourceRepository
                    .findById(orgId, sourceId)
                    .map(this::toCommitResult)
                    .orElseGet(CommitResult.NotFound::new);
        }

        return switch (verification) {
            case VerificationOutcome.Valid ignored -> new CommitResult.Committed(sourceId);
            case VerificationOutcome.Invalid invalid -> new CommitResult.Invalid(invalid.reason());
            case VerificationOutcome.ObjectNotFound ignored -> throw new IllegalStateException("unreachable");
        };
    }

    private CommitResult toCommitResult(Source current) {
        return switch (current.status()) {
            case UPLOADED -> new CommitResult.Committed(current.id());
            case REJECTED -> new CommitResult.AlreadyRejected(current.rejectionReason());
            case PENDING, CORRUPT -> new CommitResult.Invalid(
                    "commit could not be finalized due to a concurrent update; please retry");
        };
    }

    private BlobStore requireBlobStore() {
        BlobStore blobStore = blobStoreProvider.getIfAvailable();
        if (blobStore == null) {
            throw new BlobStoreUnavailableException(
                    "Storage is not configured in this environment (SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY/SUPABASE_STORAGE_BUCKET not set).");
        }
        return blobStore;
    }
}
