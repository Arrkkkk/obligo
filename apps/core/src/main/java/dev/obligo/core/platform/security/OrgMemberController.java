package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.NoSuchOrgMembershipException;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import dev.obligo.core.platform.identity.Role;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

/**
 * The demonstration capability-checked endpoint for §10.7's RBAC slice:
 * member:manage_roles is ✅ only for OWNER/ADMIN in the blueprint's matrix.
 *
 * Deliberately takes no org_id from the client at all — it always operates
 * on the caller's own org (claims.orgId()), never a path/body-supplied
 * value. org_members has no RLS (see V5), so @PreAuthorize checking the
 * capability is necessary but not sufficient on its own: without this,
 * anyone holding member:manage_roles in *any* org could edit membership
 * rows in every other org too.
 */
@RestController
@RequestMapping("/api/v1/org/members")
public class OrgMemberController {

    private final OrgMembershipRepository orgMembershipRepository;

    public OrgMemberController(OrgMembershipRepository orgMembershipRepository) {
        this.orgMembershipRepository = orgMembershipRepository;
    }

    @PatchMapping("/{userId}/role")
    @PreAuthorize("hasAuthority('member:manage_roles')")
    public ResponseEntity<Void> updateRole(
            Authentication authentication, @PathVariable UUID userId, @RequestBody UpdateRoleRequest request) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();
        try {
            orgMembershipRepository.updateRole(claims.orgId(), userId, request.role());
        } catch (NoSuchOrgMembershipException e) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.noContent().build();
    }

    public record UpdateRoleRequest(Role role) {}
}
