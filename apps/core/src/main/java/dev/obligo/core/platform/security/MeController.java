package dev.obligo.core.platform.security;

import dev.obligo.core.platform.tenancy.Organization;
import dev.obligo.core.platform.tenancy.OrganizationRepository;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * The capstone proof for this phase: an authenticated request whose
 * org-scoped DB read (via the same OrganizationRepository/RLS mechanism
 * TenantIsolationTest proved) returns exactly the org the token's org_id
 * claim named — nothing else, and nothing missing.
 */
@RestController
public class MeController {

    private final OrganizationRepository organizationRepository;

    public MeController(OrganizationRepository organizationRepository) {
        this.organizationRepository = organizationRepository;
    }

    @GetMapping("/api/v1/me")
    public Map<String, Object> me(Authentication authentication) {
        AccessTokenClaims claims = (AccessTokenClaims) authentication.getPrincipal();

        List<Organization> visibleOrgs = organizationRepository.findAll();
        if (visibleOrgs.size() != 1 || !visibleOrgs.get(0).id().equals(claims.orgId())) {
            throw new IllegalStateException(
                    "TenantContext did not scope to exactly the token's org_id — visible orgs: " + visibleOrgs);
        }

        return Map.of(
                "userId", claims.userId(),
                "orgId", claims.orgId(),
                "role", claims.role(),
                "orgName", visibleOrgs.get(0).name());
    }
}
