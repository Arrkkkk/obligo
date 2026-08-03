package dev.obligo.core.platform.identity;

import java.time.Instant;
import java.util.UUID;

public record User(UUID id, String googleSub, String email, Instant createdAt) {}
