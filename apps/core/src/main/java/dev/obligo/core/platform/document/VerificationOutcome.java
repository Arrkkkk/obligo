package dev.obligo.core.platform.document;

/** The result of commit()'s unlocked, expensive verification phase (see SourceCommitGateway's Javadoc). */
sealed interface VerificationOutcome {

    record Valid(String mimeType) implements VerificationOutcome {}

    record Invalid(String reason) implements VerificationOutcome {}

    record ObjectNotFound() implements VerificationOutcome {}
}
