package dev.obligo.core.platform.segmentation;

import org.junit.jupiter.api.Test;
import org.springframework.web.client.RestClient;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Pure unit test, no Spring context, no DB, no real apps/brain -- just
 * BrainClient's own error-mapping logic. The "apps/brain unreachable"
 * case specifically doesn't need the fuller SegmentationFlowTest harness
 * (real JWT, real Spring context): a genuinely refused connection is
 * enough on its own.
 */
class BrainClientTest {

    @Test
    void triggerSegmentationThrowsWhenBrainIsUnreachable() {
        // Port 1 is a privileged, essentially-never-listening port -- a real,
        // reliably-refused TCP connection, not a mock.
        BrainClient client = new BrainClient(RestClient.builder(), "http://127.0.0.1:1", "irrelevant-token");

        assertThatThrownBy(() -> client.triggerSegmentation(UUID.randomUUID(), UUID.randomUUID()))
                .isInstanceOf(BrainClientUnavailableException.class);
    }

    @Test
    void getSegmentationStatusThrowsWhenBrainIsUnreachable() {
        BrainClient client = new BrainClient(RestClient.builder(), "http://127.0.0.1:1", "irrelevant-token");

        assertThatThrownBy(() -> client.getSegmentationStatus(UUID.randomUUID(), UUID.randomUUID()))
                .isInstanceOf(BrainClientUnavailableException.class);
    }
}
