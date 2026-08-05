package dev.obligo.core.platform.document;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Confirmed against the real Supabase Storage REST API (not guessed from
 * docs) before writing this:
 * - POST /object/upload/sign/{bucket}/{key} returns a relative url that
 *   already carries a scoped, time-limited token -- the browser needs
 *   nothing else, never the service-role key.
 * - That signing endpoint does NOT honor a caller-supplied expiry (an
 *   "expiresIn" body field is silently ignored); the token is always
 *   minted with a fixed ~2h lifetime. Blueprint §11.2 targets 5 min --
 *   this is a real gap against that target, not a config knob we can
 *   tighten from this side. Flagged, not silently "fixed" by inventing a
 *   client-side expiry that Supabase wouldn't enforce anyway.
 * - HEAD /object/authenticated/{bucket}/{key} works for existence + size
 *   (content-length) verification; a nonexistent object returns 400, not
 *   404, so headObject treats any non-2xx as "not found."
 * - GET with a Range header against the same path returns 206 with just
 *   the requested bytes -- used for magic-byte sniffing without pulling a
 *   whole file into memory.
 */
public class SupabaseStorageBlobStore implements BlobStore {

    private final RestClient restClient;
    private final String storageBaseUrl;
    private final String serviceRoleKey;
    private final String bucket;

    public SupabaseStorageBlobStore(
            RestClient.Builder restClientBuilder, String supabaseUrl, String serviceRoleKey, String bucket) {
        this.storageBaseUrl = supabaseUrl + "/storage/v1";
        this.restClient = restClientBuilder.baseUrl(storageBaseUrl).build();
        this.serviceRoleKey = serviceRoleKey;
        this.bucket = bucket;
    }

    @Override
    public SignedUpload createSignedUploadUrl(String key) {
        try {
            SignResponse response = restClient
                    .post()
                    .uri("/object/upload/sign/{bucket}/{key}", bucket, key)
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + serviceRoleKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of())
                    .retrieve()
                    .body(SignResponse.class);
            if (response == null || response.url() == null) {
                throw new BlobStoreUnavailableException("Supabase Storage returned an empty signed-upload response");
            }
            return new SignedUpload(storageBaseUrl + response.url(), key);
        } catch (RestClientException e) {
            throw new BlobStoreUnavailableException("Supabase Storage unreachable while creating a signed upload URL", e);
        }
    }

    @Override
    public Optional<ObjectMetadata> headObject(String key) {
        return restClient
                .method(HttpMethod.HEAD)
                .uri("/object/authenticated/{bucket}/{key}", bucket, key)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + serviceRoleKey)
                .exchange((request, response) -> {
                    if (!response.getStatusCode().is2xxSuccessful()) {
                        return Optional.empty();
                    }
                    HttpHeaders headers = response.getHeaders();
                    return Optional.of(new ObjectMetadata(headers.getContentLength(), headers.getFirst(HttpHeaders.CONTENT_TYPE)));
                });
    }

    @Override
    public byte[] readRange(String key, int startInclusive, int endInclusive) {
        return restClient
                .get()
                .uri("/object/authenticated/{bucket}/{key}", bucket, key)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + serviceRoleKey)
                .header(HttpHeaders.RANGE, "bytes=%d-%d".formatted(startInclusive, endInclusive))
                .exchange((request, response) -> {
                    if (!response.getStatusCode().is2xxSuccessful()) {
                        throw new BlobStoreUnavailableException(
                                "Supabase Storage returned " + response.getStatusCode() + " for a range read of " + key);
                    }
                    try {
                        return StreamUtils.copyToByteArray(response.getBody());
                    } catch (IOException e) {
                        throw new UncheckedIOException(e);
                    }
                });
    }

    @Override
    public byte[] readObject(String key) {
        return restClient
                .get()
                .uri("/object/authenticated/{bucket}/{key}", bucket, key)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + serviceRoleKey)
                .exchange((request, response) -> {
                    if (!response.getStatusCode().is2xxSuccessful()) {
                        throw new BlobStoreUnavailableException(
                                "Supabase Storage returned " + response.getStatusCode() + " for a full read of " + key);
                    }
                    try {
                        return StreamUtils.copyToByteArray(response.getBody());
                    } catch (IOException e) {
                        throw new UncheckedIOException(e);
                    }
                });
    }

    /**
     * Not part of the BlobStore port -- the port is what SourceUploadService
     * needs, and business logic has no business reading bucket config. Used
     * only by BucketConfigAgreementTest to confirm FileSecurityLimits hasn't
     * drifted from what the bucket actually enforces.
     */
    BucketConfig fetchBucketConfig() {
        return restClient
                .get()
                .uri("/bucket/{bucket}", bucket)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + serviceRoleKey)
                .retrieve()
                .body(BucketConfig.class);
    }

    private record SignResponse(String url, String token) {}

    record BucketConfig(
            @JsonProperty("file_size_limit") long fileSizeLimit,
            @JsonProperty("allowed_mime_types") List<String> allowedMimeTypes) {}
}
