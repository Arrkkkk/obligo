package dev.obligo.core.platform.document;

import java.util.UUID;

/** Outcomes of SourceUploadService.commit(). Package-private: only SourceController and SourceCommitGateway need it. */
sealed interface CommitResult {

    record Committed(UUID sourceId) implements CommitResult {}

    record NotFound() implements CommitResult {}

    record ObjectNotFound() implements CommitResult {}

    record Invalid(String reason) implements CommitResult {}

    record AlreadyRejected(String reason) implements CommitResult {}

    record Expired(String reason) implements CommitResult {}
}
