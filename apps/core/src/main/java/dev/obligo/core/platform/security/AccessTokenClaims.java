package dev.obligo.core.platform.security;

import java.time.Instant;
import java.util.UUID;

public record AccessTokenClaims(
        UUID userId,
        UUID orgId,
        String role,
        String jti,
        Instant issuedAt,
        Instant expiresAt) {}
