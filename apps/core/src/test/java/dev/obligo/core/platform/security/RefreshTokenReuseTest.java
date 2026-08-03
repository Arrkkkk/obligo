package dev.obligo.core.platform.security;

import dev.obligo.core.ObligoApplication;
import dev.obligo.core.platform.identity.User;
import dev.obligo.core.platform.identity.UserRepository;
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
 * Proves refresh rotation with reuse detection at the same rigor as
 * TenantIsolationTest (blueprint §10.5): replaying an already-rotated
 * token must kill the *entire* family, including tokens that were never
 * themselves replayed — not just reject the one bad token.
 */
@SpringBootTest(classes = ObligoApplication.class)
@EnabledIfEnvironmentVariable(named = "DATABASE_URL", matches = ".+")
class RefreshTokenReuseTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RefreshTokenService refreshTokenService;

    @Autowired
    private RefreshTokenRepository refreshTokenRepository;

    @Autowired
    private SecurityAuditEventRepository auditEventRepository;

    private User user;

    @BeforeEach
    void createUser() {
        user = userRepository.insert("google-sub-" + UUID.randomUUID(), "reuse-test@example.com");
    }

    @AfterEach
    void cleanup() {
        auditEventRepository.deleteByUserId(user.id());
        refreshTokenRepository.deleteByUserId(user.id());
        userRepository.delete(user.id());
    }

    @Test
    void replayingAUsedTokenKillsTheEntireFamilyAndAuditsIt() {
        String token1 = refreshTokenService.issue(user.id(), "test-agent", "127.0.0.1");

        RotationResult firstRotation = refreshTokenService.rotate(token1, "test-agent", "127.0.0.1");
        assertThat(firstRotation).isInstanceOf(RotationResult.Rotated.class);
        String token2 = ((RotationResult.Rotated) firstRotation).newRawToken();

        // The attack: token1 gets presented again after it was already
        // rotated away — a stolen cookie or a broken client racing a retry.
        RotationResult replay = refreshTokenService.rotate(token1, "attacker-agent", "10.0.0.1");
        assertThat(replay).isInstanceOf(RotationResult.ReuseDetected.class);
        UUID familyId = ((RotationResult.ReuseDetected) replay).familyId();

        assertThat(auditEventRepository.findEventTypesForFamily(familyId)).contains("SECURITY_TOKEN_REUSE");

        List<RefreshToken> familyRows = refreshTokenRepository.findByFamilyId(familyId);
        assertThat(familyRows).isNotEmpty();
        assertThat(familyRows).allSatisfy(row -> assertThat(row.revokedAt()).isNotNull());

        // The critical assertion: token2 was legitimately rotated and never
        // itself replayed, but it must be dead too — the whole family died,
        // not just the token that got reused.
        RotationResult token2AttemptAfterFamilyKilled = refreshTokenService.rotate(token2, "test-agent", "127.0.0.1");
        assertThat(token2AttemptAfterFamilyKilled).isInstanceOf(RotationResult.ReuseDetected.class);
    }

    @Test
    void rotatingAnUnknownTokenIsInvalidNotReuseDetected() {
        RotationResult result = refreshTokenService.rotate("not-a-real-token", "test-agent", "127.0.0.1");

        assertThat(result).isInstanceOf(RotationResult.Invalid.class);
    }

    @Test
    void legitimateRotationChainWorksAndEachSupersededTokenBecomesUnusable() {
        String token1 = refreshTokenService.issue(user.id(), "test-agent", "127.0.0.1");

        RotationResult rotation1 = refreshTokenService.rotate(token1, "test-agent", "127.0.0.1");
        assertThat(rotation1).isInstanceOf(RotationResult.Rotated.class);
        String token2 = ((RotationResult.Rotated) rotation1).newRawToken();

        RotationResult rotation2 = refreshTokenService.rotate(token2, "test-agent", "127.0.0.1");
        assertThat(rotation2).isInstanceOf(RotationResult.Rotated.class);
        String token3 = ((RotationResult.Rotated) rotation2).newRawToken();

        // token1 is superseded — replaying it is detected as reuse, which
        // kills the whole family as a side effect of this very call.
        assertThat(refreshTokenService.rotate(token1, "test-agent", "127.0.0.1"))
                .isInstanceOf(RotationResult.ReuseDetected.class);

        // token2 and token3 (the legitimate, never-replayed tip) are now
        // both casualties of that family-wide revocation, not just token1.
        assertThat(refreshTokenService.rotate(token2, "test-agent", "127.0.0.1"))
                .isInstanceOf(RotationResult.ReuseDetected.class);
        assertThat(refreshTokenService.rotate(token3, "test-agent", "127.0.0.1"))
                .isInstanceOf(RotationResult.ReuseDetected.class);
    }
}
