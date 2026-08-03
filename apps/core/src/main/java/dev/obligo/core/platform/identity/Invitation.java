package dev.obligo.core.platform.identity;

import java.time.Instant;
import java.util.UUID;

public record Invitation(
        UUID id,
        UUID orgId,
        String email,
        Role role,
        String tokenHash,
        UUID invitedBy,
        Instant createdAt,
        Instant expiresAt,
        Instant acceptedAt,
        Instant revokedAt) {

    public boolean isCurrentlyAcceptable() {
        return revokedAt == null && acceptedAt == null && expiresAt.isAfter(Instant.now());
    }
}
