package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.Role;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * No org id ever comes from the client here either (same discipline as
 * OrgMemberController) — invite always operates on claims.orgId(), accept
 * always operates on the invitation's own stored org_id, never anything
 * path/body-supplied.
 */
@RestController
public class InvitationController {

    private final InvitationService invitationService;
    private final String webAppUrl;

    public InvitationController(InvitationService invitationService, @Value("${app.web-url}") String webAppUrl) {
        this.invitationService = invitationService;
        this.webAppUrl = webAppUrl;
    }

    @PostMapping("/api/v1/org/invitations")
    @PreAuthorize("hasAuthority('member:invite')")
    public ResponseEntity<Map<String, Object>> invite(Authentication authentication, @RequestBody InviteRequest request) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        InvitationService.CreatedInvitation created =
                invitationService.invite(claims.orgId(), claims.userId(), request.email(), request.role());

        // No SMTP wiring yet ([PROD] per blueprint) — the raw token and its
        // preview URL are returned directly so the accept flow is testable
        // without an email round trip.
        return ResponseEntity.ok(Map.of(
                "invitationId", created.id(),
                "token", created.rawToken(),
                "expiresAt", created.expiresAt(),
                "previewUrl", webAppUrl + "/invitations/" + created.rawToken()));
    }

    @GetMapping("/api/v1/invitations/{token}")
    public ResponseEntity<Map<String, Object>> preview(@PathVariable String token) {
        return invitationService
                .preview(token)
                .<ResponseEntity<Map<String, Object>>>map(p -> ResponseEntity.ok(Map.of(
                        "orgName", p.orgName(), "role", p.role(), "invitedByEmail", p.invitedByEmail())))
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Invitation not found or no longer valid.")));
    }

    @PostMapping("/api/v1/invitations/{token}/accept")
    public ResponseEntity<Map<String, Object>> accept(Authentication authentication, @PathVariable String token) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        InvitationService.AcceptResult result = invitationService.accept(token, claims.userId());

        return switch (result) {
            case InvitationService.AcceptResult.Accepted accepted -> ResponseEntity.ok(
                    Map.of("access_token", accepted.accessToken(), "expires_in", accepted.expiresInSeconds()));
            case InvitationService.AcceptResult.InvitationNotValid ignored -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "Invitation not found or no longer valid."));
            case InvitationService.AcceptResult.EmailMismatch ignored -> ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "This invitation was sent to a different email address."));
            case InvitationService.AcceptResult.AlreadyHasOrg ignored -> ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(Map.of(
                            "error", "You already belong to an organization; multi-org support isn't available yet."));
        };
    }

    public record InviteRequest(String email, Role role) {}
}
