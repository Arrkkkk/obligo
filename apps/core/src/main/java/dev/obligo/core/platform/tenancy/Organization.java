package dev.obligo.core.platform.tenancy;

import java.time.Instant;
import java.util.UUID;

public record Organization(UUID id, String name, Instant createdAt) {}
