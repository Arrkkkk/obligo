package dev.obligo.core.platform.document;

import dev.obligo.core.ObligoApplication;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Proves the two independent layers the user asked us to keep in sync
 * actually agree: FileSecurityLimits (app-level) vs. the "sources" bucket's
 * own server-side config (Supabase-level). A drift here -- someone changing
 * the bucket's free-tier cap without updating the constant, or vice versa --
 * would otherwise show up only as a confusing "app accepted it, Supabase
 * silently rejected it" failure at commit time, exactly what this test
 * exists to catch instead.
 */
@SpringBootTest(classes = ObligoApplication.class)
@EnabledIfEnvironmentVariable(named = "SUPABASE_URL", matches = ".+")
class BucketConfigAgreementTest {

    @Autowired
    private SupabaseStorageBlobStore blobStore;

    @Test
    void appLevelLimitsMatchTheBucketsOwnConfigExactly() {
        SupabaseStorageBlobStore.BucketConfig bucketConfig = blobStore.fetchBucketConfig();

        assertThat(bucketConfig.fileSizeLimit())
                .as("FileSecurityLimits.MAX_SOURCE_SIZE_BYTES must not be looser than the bucket's own cap")
                .isEqualTo(FileSecurityLimits.MAX_SOURCE_SIZE_BYTES);

        assertThat(bucketConfig.allowedMimeTypes())
                .as("FileSecurityLimits.ALLOWED_MIME_TYPES must match the bucket's allow-list exactly")
                .containsExactlyInAnyOrderElementsOf(FileSecurityLimits.ALLOWED_MIME_TYPES);
    }
}
