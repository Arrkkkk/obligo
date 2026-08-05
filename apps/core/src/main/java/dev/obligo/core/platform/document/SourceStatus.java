package dev.obligo.core.platform.document;

public enum SourceStatus {
    /** Upload-intent issued; the client may or may not have PUT the bytes yet. */
    PENDING,
    /** Commit's server-side verification (existence, size, magic bytes) passed. */
    UPLOADED,
    /** Commit's server-side verification found the object invalid; terminal. */
    REJECTED,
    /** Reserved for §11.7's post-commit drift case (object later found missing) -- not produced by this slice. */
    CORRUPT
}
