package dev.obligo.core.platform.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.Signature;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.RSAPublicKeySpec;
import java.time.Instant;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * No Spring context, no DB — pure unit tests of the hand-rolled RS256
 * mint/verify (§10.2/§10.3). The last test is the concrete demonstration of
 * "verify without being able to mint": it reconstructs a public key from
 * nothing but the published JWKS JSON, exactly as brain/mcp would, and uses
 * it to verify a token core signed.
 */
class AccessTokenServiceTest {

    private final JwtKeyManager keyManager = new JwtKeyManager();
    private final AccessTokenService accessTokenService = new AccessTokenService(keyManager, new ObjectMapper());

    @Test
    void issuedTokenRoundTripsToTheSameClaims() {
        UUID userId = UUID.randomUUID();
        UUID orgId = UUID.randomUUID();

        String token = accessTokenService.issue(userId, orgId, "OWNER");
        AccessTokenClaims claims = accessTokenService.verify(token);

        assertThat(claims.userId()).isEqualTo(userId);
        assertThat(claims.orgId()).isEqualTo(orgId);
        assertThat(claims.role()).isEqualTo("OWNER");
        assertThat(claims.expiresAt()).isAfter(Instant.now());
    }

    @Test
    void tamperedPayloadFailsVerificationEvenThoughSignatureLooksWellFormed() {
        String token = accessTokenService.issue(UUID.randomUUID(), UUID.randomUUID(), "OWNER");
        String[] parts = token.split("\\.");

        String decodedPayload = new String(Base64.getUrlDecoder().decode(parts[1]), StandardCharsets.UTF_8);
        String tamperedPayload = decodedPayload.replace("OWNER", "ADMIN");
        String reencodedPayload =
                Base64.getUrlEncoder().withoutPadding().encodeToString(tamperedPayload.getBytes(StandardCharsets.UTF_8));
        String tamperedToken = parts[0] + "." + reencodedPayload + "." + parts[2];

        assertThatThrownBy(() -> accessTokenService.verify(tamperedToken))
                .isInstanceOf(InvalidAccessTokenException.class);
    }

    @Test
    void algNoneIsRejectedRegardlessOfSignature() {
        Base64.Encoder encoder = Base64.getUrlEncoder().withoutPadding();
        String header = encoder.encodeToString("{\"alg\":\"none\",\"typ\":\"JWT\"}".getBytes(StandardCharsets.UTF_8));
        String payload = encoder.encodeToString("{\"sub\":\"attacker\"}".getBytes(StandardCharsets.UTF_8));
        String forgedToken = header + "." + payload + ".";

        assertThatThrownBy(() -> accessTokenService.verify(forgedToken))
                .isInstanceOf(InvalidAccessTokenException.class);
    }

    @Test
    void jwksPublishedKeyAloneCanVerifyATokenButNeverMintOne() throws Exception {
        JwksController jwksController = new JwksController(keyManager);

        @SuppressWarnings("unchecked")
        Map<String, Object> jwk = (Map<String, Object>) ((List<?>) jwksController.jwks().get("keys")).get(0);

        BigInteger modulus = new BigInteger(1, Base64.getUrlDecoder().decode((String) jwk.get("n")));
        BigInteger exponent = new BigInteger(1, Base64.getUrlDecoder().decode((String) jwk.get("e")));
        RSAPublicKey reconstructedPublicKey =
                (RSAPublicKey) KeyFactory.getInstance("RSA").generatePublic(new RSAPublicKeySpec(modulus, exponent));

        assertThat(reconstructedPublicKey).isEqualTo(keyManager.publicKey());

        String token = accessTokenService.issue(UUID.randomUUID(), UUID.randomUUID(), "OWNER");
        String[] parts = token.split("\\.");

        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initVerify(reconstructedPublicKey);
        signature.update((parts[0] + "." + parts[1]).getBytes(StandardCharsets.UTF_8));

        assertThat(signature.verify(Base64.getUrlDecoder().decode(parts[2]))).isTrue();
    }
}
