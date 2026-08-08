package dev.obligo.core.platform.segmentation;

/** Outcomes of BrainClient.getSegmentationStatus(). Public -- see TriggerResult's javadoc for why (cross-package consumer). */
public sealed interface StatusResult {

    record Found(SegmentationJobStatus status) implements StatusResult {}

    record NotFound() implements StatusResult {}
}
