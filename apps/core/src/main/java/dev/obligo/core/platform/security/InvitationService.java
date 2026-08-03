package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.Invitation;
import dev.obligo.core.platform.identity.InvitationRepository;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.Role;
import dev.obligo.core.platform.identity.User;
import dev.obligo.core.platform.identity.UserRepository;
import dev.obligo.core.platform.tenancy.Organization;
import dev.obligo.core.platform.tenancy.OrganizationRepository;
import dev.obligo.core.platform.tenancy.TenantContext;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

/**
 * Invitations (§10.8). Opaque tokens stored hashed, same pattern as refresh
 * tokens (§10.5) — high-entropy random values, SHA-256 is sufficient.
 *
 * Deliberately does NOT build multi-org support: accept() rejects a user
 * who already has any org membership, rather than silently creating a
 * second one. If we ever want multi-org, that's a deliberate feature with
 * its own session/active-org model — not something to back into here.
 */
@Service
public class InvitationService {

    private static final Duration EXPIRY = Duration.ofDays(7);

    private final InvitationRepository invitationRepository;
    private final OrgMembershipRepository orgMembershipRepository;
    private final UserRepository userRepository;
    private final OrganizationRepository organizationRepository;
    private final AccessTokenService accessTokenService;
    private final SecureRandom secureRandom = new SecureRandom();
    private final Base64.Encoder base64UrlEncoder = Base64.getUrlEncoder().withoutPadding();

    public InvitationService(
            InvitationRepository invitationRepository,
            OrgMembershipRepository orgMembershipRepository,
            UserRepository userRepository,
            OrganizationRepository organizationRepository,
            AccessTokenService accessTokenService) {
        this.invitationRepository = invitationRepository;
        this.orgMembershipRepository = orgMembershipRepository;
        this.userRepository = userRepository;
        this.organizationRepository = organizationRepository;
        this.accessTokenService = accessTokenService;
    }

    public record CreatedInvitation(UUID id, String rawToken, Instant expiresAt) {}

    @Transactional
    public CreatedInvitation invite(UUID orgId, UUID invitedBy, String email, Role role) {
        String normalizedEmail = email.toLowerCase(Locale.ROOT);

        // Re-inviting rotates the token rather than resending the old one
        // (§10.8) — revoke any still-pending invite for this (org, email)
        // before creating the fresh one.
        invitationRepository.findPendingByOrgAndEmail(orgId, normalizedEmail).ifPresent(existing -> invitationRepository.revoke(existing.id()));

        UUID id = UUID.randomUUID();
        String rawToken = generateOpaqueToken();
        Instant expiresAt = Instant.now().plus(EXPIRY);
        invitationRepository.insert(id, orgId, normalizedEmail, role, hash(rawToken), invitedBy, expiresAt);

        return new CreatedInvitation(id, rawToken, expiresAt);
    }

    public record InvitationPreview(String orgName, Role role, String invitedByEmail) {}

    public Optional<InvitationPreview> preview(String rawToken) {
        return invitationRepository
                .findByTokenHash(hash(rawToken))
                .filter(Invitation::isCurrentlyAcceptable)
                .map(invitation -> new InvitationPreview(
                        lookupOrgName(invitation.orgId()),
                        invitation.role(),
                        userRepository.findById(invitation.invitedBy()).map(User::email).orElse("unknown")));
    }

    public sealed interface AcceptResult {
        record Accepted(String accessToken, long expiresInSeconds) implements AcceptResult {}

        record InvitationNotValid() implements AcceptResult {}

        record EmailMismatch() implements AcceptResult {}

        record AlreadyHasOrg() implements AcceptResult {}
    }

    @Transactional
    public AcceptResult accept(String rawToken, UUID acceptingUserId) {
        Optional<Invitation> maybeInvitation = invitationRepository.findByTokenHash(hash(rawToken));
        if (maybeInvitation.isEmpty() || !maybeInvitation.get().isCurrentlyAcceptable()) {
            return new AcceptResult.InvitationNotValid();
        }
        Invitation invitation = maybeInvitation.get();

        User user = userRepository
                .findById(acceptingUserId)
                .orElseThrow(() -> new IllegalStateException("Authenticated user not found: " + acceptingUserId));
        if (!user.email().equalsIgnoreCase(invitation.email())) {
            return new AcceptResult.EmailMismatch();
        }

        // Constrained by design (not a gap): multi-org support doesn't exist
        // yet, so a user who already belongs to an org can't accept a
        // second one. See class javadoc.
        if (orgMembershipRepository.existsForUserId(acceptingUserId)) {
            return new AcceptResult.AlreadyHasOrg();
        }

        orgMembershipRepository.insert(invitation.orgId(), acceptingUserId, invitation.role());
        invitationRepository.markAccepted(invitation.id());

        String accessToken = accessTokenService.issue(acceptingUserId, invitation.orgId(), invitation.role());
        return new AcceptResult.Accepted(accessToken, 900);
    }

    private String lookupOrgName(UUID orgId) {
        // Reads a single, already-known org by its own id — the same
        // pattern PersonalOrgProvisioningService uses for inserts. Not a
        // cross-tenant browse: TenantContext is set to exactly the org the
        // invitation itself names.
        TenantContext.set(orgId);
        try {
            return organizationRepository.findAll().stream()
                    .findFirst()
                    .map(Organization::name)
                    .orElse("Unknown organization");
        } finally {
            TenantContext.clear();
        }
    }

    private String generateOpaqueToken() {
        byte[] randomBytes = new byte[32];
        secureRandom.nextBytes(randomBytes);
        return base64UrlEncoder.encodeToString(randomBytes);
    }

    private String hash(String rawToken) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(rawToken.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hashBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 not available", e);
        }
    }
}
