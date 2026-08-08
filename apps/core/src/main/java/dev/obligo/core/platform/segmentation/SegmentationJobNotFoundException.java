package dev.obligo.core.platform.segmentation;

import java.util.UUID;

/** No segmentation job exists yet for this source -- the caller maps this to a 404. */
public class SegmentationJobNotFoundException extends RuntimeException {

    public SegmentationJobNotFoundException(UUID sourceId) {
        super("no segmentation job for source " + sourceId);
    }
}
