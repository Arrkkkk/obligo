package dev.obligo.core.platform.tenancy;

import dev.obligo.core.ObligoApplication;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Proves tenant isolation at the database layer (blueprint §10.9), with no
 * auth/HTTP layer involved yet — TenantContext is set directly, standing in
 * for what a JWT filter will do once org_id comes from a token (§10.4).
 *
 * Runs against a real Neon branch (no mocks, per CLAUDE.md) — the local dev
 * branch here, a dedicated CI branch in ci-core.yml. Gated rather than
 * hard-failed when DATABASE_URL isn't set, so it skips gracefully for any
 * contributor who hasn't configured .env yet.
 */
@SpringBootTest(classes = ObligoApplication.class)
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class TenantIsolationTest {

    @Autowired
    private OrganizationRepository organizationRepository;

    private UUID orgAId;
    private UUID orgBId;

    @BeforeEach
    void seedTwoOrganizations() {
        orgAId = UUID.randomUUID();
        orgBId = UUID.randomUUID();

        TenantContext.set(orgAId);
        try {
            organizationRepository.insert(orgAId, "Org A");
        } finally {
            TenantContext.clear();
        }

        TenantContext.set(orgBId);
        try {
            organizationRepository.insert(orgBId, "Org B");
        } finally {
            TenantContext.clear();
        }
    }

    @AfterEach
    void deleteTheTwoOrganizations() {
        TenantContext.set(orgAId);
        try {
            organizationRepository.delete(orgAId);
        } finally {
            TenantContext.clear();
        }

        TenantContext.set(orgBId);
        try {
            organizationRepository.delete(orgBId);
        } finally {
            TenantContext.clear();
        }
    }

    @Test
    void orgCannotSeeTheOtherOrgsRowEvenOverTheSamePhysicalConnection() {
        TenantContext.set(orgAId);
        long backendPidForA;
        List<Organization> visibleToA;
        try {
            backendPidForA = organizationRepository.currentBackendPid();
            visibleToA = organizationRepository.findAll();
        } finally {
            TenantContext.clear();
        }

        TenantContext.set(orgBId);
        long backendPidForB;
        List<Organization> visibleToB;
        try {
            backendPidForB = organizationRepository.currentBackendPid();
            visibleToB = organizationRepository.findAll();
        } finally {
            TenantContext.clear();
        }

        // The test JVM runs with DATABASE_MAX_POOL_SIZE=1 (build.gradle.kts),
        // so both "requests" are guaranteed — not just likely — to have been
        // served by the same physical Postgres backend. Comparing backend
        // PIDs makes that fact observable rather than assumed.
        assertThat(backendPidForB).isEqualTo(backendPidForA);

        assertThat(visibleToA).extracting(Organization::id).containsExactly(orgAId);
        assertThat(visibleToB).extracting(Organization::id).containsExactly(orgBId);
    }

    @Test
    void requestWithNoTenantContextSeesNoRows() {
        // Fail-closed check: with no tenant context, app.org_id resolves to
        // NULL (see V3's NULLIF — a touched-then-reset custom GUC reverts to
        // '', not NULL, which NULLIF folds back), and id = NULL is never
        // true, so an unscoped request sees nothing rather than everything.
        List<Organization> visible = organizationRepository.findAll();

        assertThat(visible).isEmpty();
    }
}
