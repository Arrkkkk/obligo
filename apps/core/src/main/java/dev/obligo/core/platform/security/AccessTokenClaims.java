package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.Role;

import java.time.Instant;
import java.util.Set;
import java.util.UUID;

public record AccessTokenClaims(
        UUID userId,
        UUID orgId,
        Role role,
        Set<Capability> scopes,
        String jti,
        Instant issuedAt,
        Instant expiresAt) {}
