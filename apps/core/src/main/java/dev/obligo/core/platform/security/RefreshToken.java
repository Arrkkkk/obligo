package dev.obligo.core.platform.security;

import java.time.Instant;
import java.util.UUID;

public record RefreshToken(
        UUID id,
        UUID familyId,
        UUID userId,
        String tokenHash,
        Instant issuedAt,
        Instant usedAt,
        UUID replacedBy,
        Instant revokedAt) {}
