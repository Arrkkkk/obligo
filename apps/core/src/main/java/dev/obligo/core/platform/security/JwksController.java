package dev.obligo.core.platform.security;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigInteger;
import java.security.interfaces.RSAPublicKey;
import java.util.Arrays;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Publishes the public half of the RS256 keypair (§10.3) so brain/mcp can
 * verify tokens without ever holding anything that lets them mint one.
 */
@RestController
public class JwksController {

    private final JwtKeyManager keyManager;
    private final Base64.Encoder base64UrlEncoder = Base64.getUrlEncoder().withoutPadding();

    public JwksController(JwtKeyManager keyManager) {
        this.keyManager = keyManager;
    }

    @GetMapping("/.well-known/jwks.json")
    public Map<String, Object> jwks() {
        RSAPublicKey key = keyManager.publicKey();

        Map<String, Object> jwk = new LinkedHashMap<>();
        jwk.put("kty", "RSA");
        jwk.put("use", "sig");
        jwk.put("alg", "RS256");
        jwk.put("kid", keyManager.kid());
        jwk.put("n", base64UrlEncoder.encodeToString(unsignedBytes(key.getModulus())));
        jwk.put("e", base64UrlEncoder.encodeToString(unsignedBytes(key.getPublicExponent())));

        return Map.of("keys", List.of(jwk));
    }

    private byte[] unsignedBytes(BigInteger value) {
        byte[] bytes = value.toByteArray();
        if (bytes.length > 1 && bytes[0] == 0) {
            return Arrays.copyOfRange(bytes, 1, bytes.length);
        }
        return bytes;
    }
}
