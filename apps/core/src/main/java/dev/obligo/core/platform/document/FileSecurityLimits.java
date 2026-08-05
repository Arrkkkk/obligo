package dev.obligo.core.platform.document;

import java.util.Set;

/**
 * App-level PDF-only constraints for this slice (§11.6). Deliberately a
 * second, independent layer on top of -- not derived from -- the Supabase
 * bucket's own server-side config (50 MB size cap, application/pdf MIME
 * allow-list). BucketConfigAgreementTest asserts the two stay in sync, so a
 * drift here can't silently produce "the app accepted it, Supabase then
 * rejected it" as a confusing failure at commit time.
 */
final class FileSecurityLimits {

    /** Must match the "sources" bucket's file_size_limit exactly. */
    static final long MAX_SOURCE_SIZE_BYTES = 52_428_800L; // 50 MiB

    /** Must match the bucket's allowed_mime_types exactly. */
    static final Set<String> ALLOWED_MIME_TYPES = Set.of("application/pdf");

    private FileSecurityLimits() {}
}
