package dev.obligo.core.platform.segmentation;

/**
 * Mirrors apps/brain's SegmentationJobStatusResponse (sources.py) field for
 * field. status is one of QUEUED/PROCESSING/SUCCEEDED/FAILED -- brain's own
 * CHECK constraint (V15) is the source of truth for that set, not an enum
 * here, since a new status value should be a brain-side migration decision,
 * not something this client needs to be recompiled to recognize.
 */
public record SegmentationJobStatus(String status, int attemptCount, Integer segmentCount, String lastError) {}
