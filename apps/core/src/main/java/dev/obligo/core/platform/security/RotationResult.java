package dev.obligo.core.platform.security;

import java.util.UUID;

public sealed interface RotationResult {

    record Rotated(String newRawToken, UUID userId) implements RotationResult {}

    /** Either the replayed token itself, or any other token from a family already killed by a prior replay. */
    record ReuseDetected(UUID userId, UUID familyId) implements RotationResult {}

    /** Unknown token, or a token past its 30-day idle expiry (§10.6). */
    record Invalid() implements RotationResult {}
}
