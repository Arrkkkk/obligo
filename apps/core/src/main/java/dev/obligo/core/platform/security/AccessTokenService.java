package dev.obligo.core.platform.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.obligo.core.platform.identity.Role;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.Signature;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Hand-rolled RS256 JWT mint/verify (§10.2/§10.3) — deliberately not using a
 * JWT library, since the point of this system is demonstrating the
 * mechanics, not outsourcing them. Access tokens carry exactly one org_id
 * (§10.4); TenantJwtAuthenticationFilter is the only thing that ever reads
 * it back out to populate TenantContext.
 *
 * The "scopes" claim (§10.3: "derived capability list, denormalised for
 * gateway checks") is computed from role once, here, at mint time — not
 * re-derived from role on every request. That's deliberate: a downstream
 * verifier (brain/mcp, or a dumb gateway) can authorize purely off the
 * token's scopes without needing to know the role->capability mapping
 * itself.
 */
@Service
public class AccessTokenService {

    private static final long TTL_MINUTES = 15;
    private static final long CLOCK_SKEW_SECONDS = 60;
    private static final String ISSUER = "obligo-core";
    private static final String AUDIENCE = "obligo";

    private final JwtKeyManager keyManager;
    private final ObjectMapper objectMapper;
    private final Base64.Encoder base64UrlEncoder = Base64.getUrlEncoder().withoutPadding();
    private final Base64.Decoder base64UrlDecoder = Base64.getUrlDecoder();

    public AccessTokenService(JwtKeyManager keyManager, ObjectMapper objectMapper) {
        this.keyManager = keyManager;
        this.objectMapper = objectMapper;
    }

    public String issue(UUID userId, UUID orgId, Role role) {
        try {
            Instant now = Instant.now();
            Instant expiresAt = now.plus(TTL_MINUTES, ChronoUnit.MINUTES);

            Map<String, Object> header = new LinkedHashMap<>();
            header.put("alg", "RS256");
            header.put("typ", "JWT");
            header.put("kid", keyManager.kid());

            List<String> scopes = RoleCapabilities.capabilitiesFor(role).stream()
                    .map(Capability::wireName)
                    .sorted()
                    .collect(Collectors.toList());

            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("sub", userId.toString());
            payload.put("org_id", orgId.toString());
            payload.put("role", role.name());
            payload.put("scopes", scopes);
            payload.put("jti", UUID.randomUUID().toString());
            payload.put("iat", now.getEpochSecond());
            payload.put("exp", expiresAt.getEpochSecond());
            payload.put("iss", ISSUER);
            payload.put("aud", AUDIENCE);

            String encodedHeader = base64UrlEncoder.encodeToString(objectMapper.writeValueAsBytes(header));
            String encodedPayload = base64UrlEncoder.encodeToString(objectMapper.writeValueAsBytes(payload));
            String signingInput = encodedHeader + "." + encodedPayload;

            Signature signature = Signature.getInstance("SHA256withRSA");
            signature.initSign(keyManager.privateKey());
            signature.update(signingInput.getBytes(StandardCharsets.UTF_8));
            String encodedSignature = base64UrlEncoder.encodeToString(signature.sign());

            return signingInput + "." + encodedSignature;
        } catch (Exception e) {
            throw new IllegalStateException("Failed to issue access token", e);
        }
    }

    @SuppressWarnings("unchecked")
    public AccessTokenClaims verify(String token) {
        String[] parts = token.split("\\.", -1);
        if (parts.length != 3) {
            throw new InvalidAccessTokenException("Malformed token");
        }
        String encodedHeader = parts[0];
        String encodedPayload = parts[1];
        String encodedSignature = parts[2];

        try {
            Map<String, Object> header = objectMapper.readValue(base64UrlDecoder.decode(encodedHeader), Map.class);
            // Reject anything but RS256 up front — an "alg":"none" or HS256
            // header is exactly the algorithm-confusion attack RS256 is
            // meant to close off (§10.3's whole point: only core can sign).
            if (!"RS256".equals(header.get("alg"))) {
                throw new InvalidAccessTokenException("Unsupported alg: " + header.get("alg"));
            }

            String signingInput = encodedHeader + "." + encodedPayload;
            Signature signature = Signature.getInstance("SHA256withRSA");
            signature.initVerify(keyManager.publicKey());
            signature.update(signingInput.getBytes(StandardCharsets.UTF_8));
            if (!signature.verify(base64UrlDecoder.decode(encodedSignature))) {
                throw new InvalidAccessTokenException("Signature verification failed");
            }

            Map<String, Object> payload = objectMapper.readValue(base64UrlDecoder.decode(encodedPayload), Map.class);

            Instant now = Instant.now();
            long exp = ((Number) payload.get("exp")).longValue();
            if (now.getEpochSecond() > exp + CLOCK_SKEW_SECONDS) {
                throw new InvalidAccessTokenException("Token expired");
            }
            if (!ISSUER.equals(payload.get("iss")) || !AUDIENCE.equals(payload.get("aud"))) {
                throw new InvalidAccessTokenException("Unexpected issuer/audience");
            }

            List<String> rawScopes = (List<String>) payload.getOrDefault("scopes", List.of());
            Set<Capability> scopes =
                    rawScopes.stream().map(Capability::fromWireName).collect(Collectors.toUnmodifiableSet());

            return new AccessTokenClaims(
                    UUID.fromString((String) payload.get("sub")),
                    UUID.fromString((String) payload.get("org_id")),
                    Role.valueOf((String) payload.get("role")),
                    scopes,
                    (String) payload.get("jti"),
                    Instant.ofEpochSecond(((Number) payload.get("iat")).longValue()),
                    Instant.ofEpochSecond(exp));
        } catch (InvalidAccessTokenException e) {
            throw e;
        } catch (Exception e) {
            throw new InvalidAccessTokenException("Failed to verify token", e);
        }
    }
}
