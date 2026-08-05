package dev.obligo.core.platform.document;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

/**
 * Reads Supabase credentials straight from the environment, same convention
 * as DataSourceConfig/FlywayConfig -- not application.yml/@Value, since
 * these are infra credentials, not app settings.
 *
 * @Conditional, not an eager requireEnv() at bean-construction time: the
 * bean method used to call requireEnv() unconditionally, which meant Spring
 * built this bean -- and threw IllegalStateException doing it -- on every
 * context load, for every test, regardless of whether that test touched
 * storage at all. That broke the whole app (25 unrelated test failures
 * observed once in CI, see CLAUDE.md) the moment SUPABASE_URL was unset,
 * which is exactly the failure mode GoogleOAuthClientRegistrationConfig
 * was already written to avoid for Google credentials. Same fix here: no
 * bean at all when credentials are missing, so the app boots fine and
 * SourceUploadService (which now holds an ObjectProvider<BlobStore>) is
 * the thing that fails -- clearly, lazily, only when storage is actually
 * used.
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
    @Conditional(SupabaseCredentialsPresentCondition.class)
    public SupabaseStorageBlobStore blobStore(RestClient.Builder restClientBuilder) {
        return new SupabaseStorageBlobStore(
                restClientBuilder,
                requireEnv("SUPABASE_URL"),
                requireEnv("SUPABASE_SERVICE_ROLE_KEY"),
                requireEnv("SUPABASE_STORAGE_BUCKET"));
    }

    /** The @Conditional above already guarantees these are present; this stays as a defensive re-check, not the primary guard. */
    private static String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(name + " environment variable is not set");
        }
        return value;
    }
}
