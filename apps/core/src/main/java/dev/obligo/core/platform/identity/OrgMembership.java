package dev.obligo.core.platform.identity;

import java.util.UUID;

public record OrgMembership(UUID orgId, UUID userId, Role role) {}
