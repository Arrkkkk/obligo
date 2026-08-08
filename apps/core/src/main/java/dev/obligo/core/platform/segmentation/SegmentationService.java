package dev.obligo.core.platform.segmentation;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * SourceController's collaborator for the segmentation trigger/SSE
 * checkpoint (§21 Phase 3) -- same controller/service split as
 * SourceUploadService for upload-intent/commit, kept separate from that
 * class because segmentation is a distinct concern layered on top of an
 * already-UPLOADED source (same reasoning V15's own migration comment gives
 * for segmentation_jobs living apart from sources.status).
 *
 * Mechanism, decided explicitly rather than defaulted into (see this
 * checkpoint's design discussion): polls apps/brain's existing GET
 * /segment status endpoint on an interval rather than Postgres
 * LISTEN/NOTIFY or a Redis pub/sub channel -- segmentation_jobs only ever
 * changes 2-3 times across a job's whole lifetime (QUEUED -> PROCESSING ->
 * terminal), so a ~2s poll costs nothing latency-wise against jobs that run
 * tens of seconds to a couple of minutes, and it needs zero new
 * infrastructure. This is a state-sync stream, not a durable event-log
 * stream: segmentation_jobs holds current status only, not a transition
 * history, so a reconnect after a drop just gets a fresh snapshot
 * immediately -- there is deliberately no Last-Event-ID/replay mechanism,
 * since there is nothing to replay.
 */
@Service
public class SegmentationService {

    private static final Set<String> TERMINAL_STATUSES = Set.of("SUCCEEDED", "FAILED");

    private final ObjectProvider<BrainClient> brainClientProvider;
    private final Duration pollInterval;
    private final Duration heartbeatInterval;

    /**
     * Defaults to apps/brain's own STALE_PROCESSING_AFTER (sources.py,
     * 900s) deliberately, not coincidentally -- past this bound brain's own
     * GET would itself reconcile a stuck PROCESSING job to FAILED on the
     * very next poll this loop makes, so the stream would already be
     * closing on a terminal status by then anyway. This bound exists as a
     * backstop for the case where it doesn't (a client that never observes
     * a terminal state for some other reason), not as the primary
     * termination path.
     */
    private final Duration maxStreamDuration;

    /**
     * All three intervals are configurable (application.yml's segmentation.*,
     * defaults matching the values reasoned about in this checkpoint's
     * design discussion) rather than hardcoded -- not just for production
     * tunability, but because SegmentationFlowTest needs to drive a full
     * poll/heartbeat/max-duration cycle in seconds, not real minutes, to
     * stay a fast, deterministic test.
     */
    public SegmentationService(
            ObjectProvider<BrainClient> brainClientProvider,
            @Value("${segmentation.poll-interval-ms:2000}") long pollIntervalMs,
            @Value("${segmentation.heartbeat-interval-ms:15000}") long heartbeatIntervalMs,
            @Value("${segmentation.max-stream-duration-seconds:900}") long maxStreamDurationSeconds) {
        this.brainClientProvider = brainClientProvider;
        this.pollInterval = Duration.ofMillis(pollIntervalMs);
        this.heartbeatInterval = Duration.ofMillis(heartbeatIntervalMs);
        this.maxStreamDuration = Duration.ofSeconds(maxStreamDurationSeconds);
    }

    private BrainClient requireBrainClient() {
        BrainClient brainClient = brainClientProvider.getIfAvailable();
        if (brainClient == null) {
            throw new BrainClientUnavailableException(
                    "apps/brain integration is not configured in this environment (BRAIN_SERVICE_TOKEN not set).");
        }
        return brainClient;
    }

    public TriggerResult trigger(UUID orgId, UUID sourceId) {
        return requireBrainClient().triggerSegmentation(sourceId, orgId);
    }

    /**
     * Throws SegmentationJobNotFoundException synchronously (before any
     * SseEmitter is created) if no job exists yet -- a real 404 is better
     * client behavior than a 200 whose stream immediately emits one error
     * event and closes.
     */
    public SseEmitter streamStatus(UUID orgId, UUID sourceId) {
        StatusResult initial = requireBrainClient().getSegmentationStatus(sourceId, orgId);
        if (initial instanceof StatusResult.NotFound) {
            throw new SegmentationJobNotFoundException(sourceId);
        }
        SegmentationJobStatus initialStatus = ((StatusResult.Found) initial).status();

        SseEmitter emitter = new SseEmitter(maxStreamDuration.plusSeconds(30).toMillis());
        AtomicBoolean active = new AtomicBoolean(true);
        emitter.onCompletion(() -> active.set(false));
        emitter.onTimeout(() -> active.set(false));
        emitter.onError(e -> active.set(false));

        Thread.ofVirtual()
                .name("sse-segmentation-" + sourceId)
                .start(() -> pollAndStream(emitter, active, orgId, sourceId, initialStatus));

        return emitter;
    }

    private void pollAndStream(
            SseEmitter emitter, AtomicBoolean active, UUID orgId, UUID sourceId, SegmentationJobStatus firstStatus) {
        Instant start = Instant.now();
        Instant lastHeartbeat = Instant.now();
        SegmentationJobStatus lastSent = null;
        SegmentationJobStatus current = firstStatus;

        try {
            while (active.get()) {
                if (!current.equals(lastSent)) {
                    emitter.send(SseEmitter.event().name("status").data(current, MediaType.APPLICATION_JSON));
                    lastSent = current;
                    lastHeartbeat = Instant.now();
                }

                if (TERMINAL_STATUSES.contains(current.status())) {
                    emitter.complete();
                    return;
                }

                if (Duration.between(start, Instant.now()).compareTo(maxStreamDuration) > 0) {
                    emitter.send(SseEmitter.event()
                            .name("timeout")
                            .data(
                                    "stream exceeded max duration; poll GET /api/v1/sources/" + sourceId
                                            + "/segment/stream again to resume watching",
                                    MediaType.TEXT_PLAIN));
                    emitter.complete();
                    return;
                }

                if (Duration.between(lastHeartbeat, Instant.now()).compareTo(heartbeatInterval) >= 0) {
                    emitter.send(SseEmitter.event().comment("ping"));
                    lastHeartbeat = Instant.now();
                }

                Thread.sleep(pollInterval);

                StatusResult result = requireBrainClient().getSegmentationStatus(sourceId, orgId);
                current = switch (result) {
                    case StatusResult.Found found -> found.status();
                    case StatusResult.NotFound ignored -> {
                        // The job existed at connect time; disappearing mid-stream
                        // isn't a real code path today (nothing deletes
                        // segmentation_jobs rows), but fail loudly rather than
                        // looping forever if it ever does.
                        emitter.send(SseEmitter.event()
                                .name("error")
                                .data("segmentation job no longer found", MediaType.TEXT_PLAIN));
                        emitter.complete();
                        yield null;
                    }
                };
                if (current == null) {
                    return;
                }
            }
        } catch (IOException e) {
            // The client disconnected mid-send. Real finding from this
            // checkpoint's own test run, not a defensive guess: Spring's
            // ResponseBodyEmitter machinery already completes the
            // AsyncContext with an error itself the moment send() fails
            // this way (a broken pipe surfaces as
            // AsyncRequestNotUsableException internally) -- calling
            // emitter.completeWithError(e) again here threw
            // IllegalStateException ("A non-container (application) thread
            // attempted to use the AsyncContext after an error had
            // occurred"), since Tomcat forbids touching an already-errored
            // AsyncContext from this virtual thread. Nothing more to do;
            // the onError callback already flipped `active` to false.
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            emitter.completeWithError(e);
        } catch (BrainClientUnavailableException e) {
            try {
                emitter.send(SseEmitter.event().name("error").data(e.getMessage(), MediaType.TEXT_PLAIN));
            } catch (IOException ignored) {
                // Client's already gone; completeWithError below is what matters.
            }
            emitter.completeWithError(e);
        }
    }
}
