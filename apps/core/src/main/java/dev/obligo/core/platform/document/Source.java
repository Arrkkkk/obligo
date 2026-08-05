package dev.obligo.core.platform.document;

import java.time.Instant;
import java.util.UUID;

public record Source(
        UUID id,
        UUID orgId,
        UUID uploadedBy,
        String filename,
        long byteSize,
        String sha256,
        String mimeType,
        String storageKey,
        SourceStatus status,
        String rejectionReason,
        Instant createdAt,
        Instant committedAt) {}
