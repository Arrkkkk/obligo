package dev.obligo.core.platform.security;

import dev.obligo.core.platform.identity.PersonalOrgProvisioningService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.time.Duration;

/**
 * Runs once Spring Security has already completed the Google OAuth2+PKCE
 * exchange (§10.2). From here on nothing about Google matters anymore —
 * this only ever mints Obligo's own tokens (§10.3) and redirects to a
 * neutral callback page with no token in the URL. The access token is
 * fetched separately by the frontend via POST /auth/refresh (using the
 * HttpOnly cookie set here), so it's never present in any URL or redirect.
 */
@Component
public class GoogleOAuthSuccessHandler implements AuthenticationSuccessHandler {

    private final PersonalOrgProvisioningService provisioningService;
    private final RefreshTokenService refreshTokenService;
    private final String webAppUrl;

    public GoogleOAuthSuccessHandler(
            PersonalOrgProvisioningService provisioningService,
            RefreshTokenService refreshTokenService,
            @Value("${app.web-url}") String webAppUrl) {
        this.provisioningService = provisioningService;
        this.refreshTokenService = refreshTokenService;
        this.webAppUrl = webAppUrl;
    }

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request, HttpServletResponse response, Authentication authentication)
            throws IOException {
        OidcUser oidcUser = (OidcUser) authentication.getPrincipal();
        String googleSub = oidcUser.getSubject();
        String email = oidcUser.getEmail();

        PersonalOrgProvisioningService.SignedInUser signedInUser = provisioningService.findOrProvision(googleSub, email);

        String rawRefreshToken =
                refreshTokenService.issue(signedInUser.userId(), request.getHeader("User-Agent"), request.getRemoteAddr());

        ResponseCookie cookie = ResponseCookie.from("refresh_token", rawRefreshToken)
                .httpOnly(true)
                .secure(true)
                .sameSite("Strict")
                .path("/api/v1/auth")
                .maxAge(Duration.ofDays(30))
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());

        response.sendRedirect(webAppUrl + "/auth/callback");
    }
}
