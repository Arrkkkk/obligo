package dev.obligo.core.platform.identity;

import java.util.UUID;

/** Thrown when a role-changing operation targets a user who isn't a member of the given org. */
public class NoSuchOrgMembershipException extends RuntimeException {

    public NoSuchOrgMembershipException(UUID orgId, UUID userId) {
        super("No membership found for user " + userId + " in org " + orgId);
    }
}
