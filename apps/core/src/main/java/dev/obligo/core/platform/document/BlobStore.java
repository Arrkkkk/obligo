package dev.obligo.core.platform.document;

import java.util.Optional;

/**
 * Blueprint §11.1's "define a BlobStore port" -- the seam that lets Supabase
 * Storage be swapped for R2 later (§11.1's stated escape hatch at 800 MB)
 * without touching SourceUploadService.
 */
public interface BlobStore {

    /**
     * A signed, single-object upload URL the browser PUTs the file bytes to
     * directly (§11.2) -- never proxied through Spring. The returned URL
     * embeds a scoped, time-limited token; the caller never needs to hand
     * out service credentials to get this far.
     */
    SignedUpload createSignedUploadUrl(String key);

    /** The server-side verification step (§11.2) -- empty if the object doesn't exist. */
    Optional<ObjectMetadata> headObject(String key);

    /**
     * An inclusive byte range, e.g. (0, 4) for the first 5 bytes -- used for
     * magic-byte sniffing, never for pulling a whole file into memory.
     */
    byte[] readRange(String key, int startInclusive, int endInclusive);

    record SignedUpload(String uploadUrl, String key) {}

    record ObjectMetadata(long sizeBytes, String contentType) {}
}
