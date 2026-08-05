package dev.obligo.core.platform.document;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

/**
 * Reads Supabase credentials straight from the environment, same convention
 * as DataSourceConfig/FlywayConfig -- not application.yml/@Value, since
 * these are infra credentials, not app settings.
 *
 * Returns the concrete SupabaseStorageBlobStore type (not the BlobStore
 * interface) so it's injectable either way: as BlobStore for
 * SourceUploadService, and by its concrete type for
 * BucketConfigAgreementTest, which needs fetchBucketConfig() -- a method
 * deliberately not on the BlobStore port.
 */
@Configuration
public class BlobStoreConfig {

    @Bean
    public SupabaseStorageBlobStore blobStore(RestClient.Builder restClientBuilder) {
        return new SupabaseStorageBlobStore(
                restClientBuilder,
                requireEnv("SUPABASE_URL"),
                requireEnv("SUPABASE_SERVICE_ROLE_KEY"),
                requireEnv("SUPABASE_STORAGE_BUCKET"));
    }

    private static String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(name + " environment variable is not set");
        }
        return value;
    }
}
