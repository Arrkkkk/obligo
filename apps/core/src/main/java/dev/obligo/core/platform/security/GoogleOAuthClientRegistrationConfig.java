package dev.obligo.core.platform.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.ClientAuthenticationMethod;
import org.springframework.security.oauth2.core.oidc.IdTokenClaimNames;

/**
 * Deliberately not declared via spring.security.oauth2.client.registration.*
 * in application.yml: merely having a "google" key present there — even
 * with an empty default — makes Spring Security's OAuth2ClientConfiguration
 * eagerly build and validate the full client-registration machinery at
 * startup, regardless of whether oauth2Login() is ever invoked, which
 * breaks the whole app (and every test) before GOOGLE_CLIENT_ID exists.
 * Registering it here, gated on the raw env vars, means no bean exists
 * until real credentials do — see SecurityConfig's ObjectProvider check.
 *
 * Google's endpoints below are its stable, documented OIDC values —
 * hardcoded rather than resolved via issuer discovery to avoid a network
 * call (and its failure modes) at every app startup.
 */
@Configuration
public class GoogleOAuthClientRegistrationConfig {

    @Bean
    @Conditional(GoogleCredentialsPresentCondition.class)
    public ClientRegistrationRepository clientRegistrationRepository() {
        ClientRegistration google = ClientRegistration.withRegistrationId("google")
                .clientId(System.getenv("GOOGLE_CLIENT_ID"))
                .clientSecret(System.getenv("GOOGLE_CLIENT_SECRET"))
                .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                .scope("openid", "email", "profile")
                .authorizationUri("https://accounts.google.com/o/oauth2/v2/auth")
                .tokenUri("https://oauth2.googleapis.com/token")
                .userInfoUri("https://openidconnect.googleapis.com/v1/userinfo")
                .userNameAttributeName(IdTokenClaimNames.SUB)
                .jwkSetUri("https://www.googleapis.com/oauth2/v3/certs")
                .clientName("Google")
                .build();
        return new InMemoryClientRegistrationRepository(google);
    }
}
