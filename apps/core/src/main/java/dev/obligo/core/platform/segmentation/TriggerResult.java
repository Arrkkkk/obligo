package dev.obligo.core.platform.segmentation;

import java.util.UUID;

/**
 * Outcomes of BrainClient.triggerSegmentation(). Public, not package-private
 * like CommitResult -- SourceController (platform.document) is the only
 * consumer, but it lives in a different package than BrainClient
 * (platform.segmentation), a deliberate split since segmentation is a
 * distinct concern from upload/blob storage even though this checkpoint's
 * proxy endpoint happens to live on the same controller class.
 *
 * Conflict carries brain's own "detail" message rather than splitting into
 * two variants for its two real causes (source not UPLOADED yet, source
 * already has a job) -- both collapse to the same 409 at this proxy layer
 * either way, so the extra variant would buy nothing the message itself
 * doesn't already say.
 */
public sealed interface TriggerResult {

    record Accepted(UUID sourceId, String status) implements TriggerResult {}

    record NotFound() implements TriggerResult {}

    record Conflict(String detail) implements TriggerResult {}

    /**
     * Brain's own POST returned 503 -- it already marked the job row FAILED
     * with the enqueue error before responding (see sources.py's module
     * docstring), so this isn't "brain is unreachable" (that's
     * BrainClientUnavailableException) -- it's "brain is reachable and told
     * us its queue isn't." The caller retries the POST itself.
     */
    record QueueUnavailable(String detail) implements TriggerResult {}
}
