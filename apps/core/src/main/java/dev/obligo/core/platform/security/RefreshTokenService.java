package dev.obligo.core.platform.security;

import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Optional;
import java.util.UUID;

/**
 * Refresh rotation with reuse detection (§10.5) — presenting an
 * already-rotated token means a stolen cookie or a broken client, and both
 * warrant killing the whole family, not just the one token.
 */
@Service
public class RefreshTokenService {

    private static final Duration IDLE_EXPIRY = Duration.ofDays(30);

    private final RefreshTokenRepository refreshTokenRepository;
    private final SecurityAuditEventRepository auditEventRepository;
    private final SecureRandom secureRandom = new SecureRandom();
    private final Base64.Encoder base64UrlEncoder = Base64.getUrlEncoder().withoutPadding();

    public RefreshTokenService(
            RefreshTokenRepository refreshTokenRepository, SecurityAuditEventRepository auditEventRepository) {
        this.refreshTokenRepository = refreshTokenRepository;
        this.auditEventRepository = auditEventRepository;
    }

    public String issue(UUID userId, String userAgent, String ip) {
        UUID familyId = UUID.randomUUID();
        return issueWithinFamily(familyId, userId, userAgent, ip).rawToken();
    }

    public RotationResult rotate(String rawToken, String userAgent, String ip) {
        String hash = hash(rawToken);
        Optional<RefreshToken> maybeToken = refreshTokenRepository.findByHashForUpdate(hash);
        if (maybeToken.isEmpty()) {
            return new RotationResult.Invalid();
        }
        RefreshToken token = maybeToken.get();

        if (token.issuedAt().isBefore(Instant.now().minus(IDLE_EXPIRY))) {
            return new RotationResult.Invalid();
        }

        if (token.revokedAt() != null) {
            // Family already dead from a prior replay elsewhere in it —
            // fail closed even though *this* token was never itself reused.
            return new RotationResult.ReuseDetected(token.userId(), token.familyId());
        }

        if (token.usedAt() != null) {
            refreshTokenRepository.revokeFamily(token.familyId());
            auditEventRepository.insert("SECURITY_TOKEN_REUSE", token.userId(), token.familyId());
            return new RotationResult.ReuseDetected(token.userId(), token.familyId());
        }

        NewToken newToken = issueWithinFamily(token.familyId(), token.userId(), userAgent, ip);
        refreshTokenRepository.markUsed(token.id(), newToken.id());
        return new RotationResult.Rotated(newToken.rawToken(), token.userId());
    }

    public void revokeFamilyContaining(String rawToken) {
        refreshTokenRepository.findByHashForUpdate(hash(rawToken))
                .ifPresent(token -> refreshTokenRepository.revokeFamily(token.familyId()));
    }

    private record NewToken(UUID id, String rawToken) {}

    private NewToken issueWithinFamily(UUID familyId, UUID userId, String userAgent, String ip) {
        byte[] randomBytes = new byte[32];
        secureRandom.nextBytes(randomBytes);
        String rawToken = base64UrlEncoder.encodeToString(randomBytes);

        UUID newId = UUID.randomUUID();
        refreshTokenRepository.insert(newId, familyId, userId, hash(rawToken), userAgent, ip);
        return new NewToken(newId, rawToken);
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
