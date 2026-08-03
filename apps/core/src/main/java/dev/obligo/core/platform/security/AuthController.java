package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.OrgMembership;
import dev.obligo.core.platform.identity.OrgMembershipRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private static final String COOKIE_NAME = "refresh_token";

    private final RefreshTokenService refreshTokenService;
    private final AccessTokenService accessTokenService;
    private final OrgMembershipRepository orgMembershipRepository;

    public AuthController(
            RefreshTokenService refreshTokenService,
            AccessTokenService accessTokenService,
            OrgMembershipRepository orgMembershipRepository) {
        this.refreshTokenService = refreshTokenService;
        this.accessTokenService = accessTokenService;
        this.orgMembershipRepository = orgMembershipRepository;
    }

    @PostMapping("/refresh")
    public ResponseEntity<Map<String, Object>> refresh(
            @CookieValue(value = COOKIE_NAME, required = false) String refreshTokenCookie,
            HttpServletRequest request,
            HttpServletResponse response) {
        if (refreshTokenCookie == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        RotationResult result =
                refreshTokenService.rotate(refreshTokenCookie, request.getHeader("User-Agent"), request.getRemoteAddr());

        if (result instanceof RotationResult.Rotated rotated) {
            OrgMembership membership = orgMembershipRepository.findByUserId(rotated.userId());
            String accessToken = accessTokenService.issue(rotated.userId(), membership.orgId(), membership.role());

            response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie(rotated.newRawToken(), Duration.ofDays(30)).toString());
            return ResponseEntity.ok(Map.of("access_token", accessToken, "expires_in", 900));
        }

        // ReuseDetected or Invalid: fail closed, force re-login (§10.5).
        response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie("", Duration.ZERO).toString());
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(
            @CookieValue(value = COOKIE_NAME, required = false) String refreshTokenCookie, HttpServletResponse response) {
        if (refreshTokenCookie != null) {
            refreshTokenService.revokeFamilyContaining(refreshTokenCookie);
        }
        response.addHeader(HttpHeaders.SET_COOKIE, refreshCookie("", Duration.ZERO).toString());
        return ResponseEntity.noContent().build();
    }

    private ResponseCookie refreshCookie(String value, Duration maxAge) {
        return ResponseCookie.from(COOKIE_NAME, value)
                .httpOnly(true)
                .secure(true)
                .sameSite("Strict")
                .path("/api/v1/auth")
                .maxAge(maxAge)
                .build();
    }
}
