package dev.obligo.core.platform.identity;

import dev.obligo.core.platform.tenancy.OrganizationRepository;
import dev.obligo.core.platform.tenancy.TenantContext;
import org.springframework.stereotype.Service;

import java.util.UUID;

/**
 * First sign-in auto-creates a personal org with the user as OWNER (§10.8) —
 * no invitations, no multi-org membership yet.
 */
@Service
public class PersonalOrgProvisioningService {

    private final UserRepository userRepository;
    private final OrgMembershipRepository orgMembershipRepository;
    private final OrganizationRepository organizationRepository;

    public PersonalOrgProvisioningService(
            UserRepository userRepository,
            OrgMembershipRepository orgMembershipRepository,
            OrganizationRepository organizationRepository) {
        this.userRepository = userRepository;
        this.orgMembershipRepository = orgMembershipRepository;
        this.organizationRepository = organizationRepository;
    }

    public record SignedInUser(UUID userId, UUID orgId, Role role) {}

    public SignedInUser findOrProvision(String googleSub, String email) {
        User user = userRepository.findByGoogleSub(googleSub).orElseGet(() -> provisionNewUser(googleSub, email));
        OrgMembership membership = orgMembershipRepository.findByUserId(user.id());
        return new SignedInUser(user.id(), membership.orgId(), membership.role());
    }

    private User provisionNewUser(String googleSub, String email) {
        User user = userRepository.insert(googleSub, email);

        UUID orgId = UUID.randomUUID();
        // organizations' RLS WITH CHECK requires app.org_id to equal the row
        // being inserted — the org creating itself, same pattern used to
        // seed TenantIsolationTest.
        TenantContext.set(orgId);
        try {
            organizationRepository.insert(orgId, email + "'s Organization");
        } finally {
            TenantContext.clear();
        }

        orgMembershipRepository.insert(orgId, user.id(), Role.OWNER);
        return user;
    }
}
