package dev.obligo.core.platform.security;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestRedirectFilter;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestCustomizers;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestResolver;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import jakarta.servlet.http.HttpServletResponse;

import java.util.List;

/**
 * Written so the app boots fine with or without Google OAuth2 credentials
 * configured (GOOGLE_CLIENT_ID/SECRET default to empty in application.yml)
 * — Spring Boot's OAuth2 client autoconfiguration backs off entirely with
 * no ClientRegistrationRepository bean when no client is configured, so
 * oauth2Login() is only wired up once real credentials exist.
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final AccessTokenService accessTokenService;
    private final GoogleOAuthSuccessHandler successHandler;
    private final String webAppUrl;

    public SecurityConfig(
            AccessTokenService accessTokenService,
            GoogleOAuthSuccessHandler successHandler,
            @Value("${app.web-url}") String webAppUrl) {
        this.accessTokenService = accessTokenService;
        this.successHandler = successHandler;
        this.webAppUrl = webAppUrl;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http, ObjectProvider<ClientRegistrationRepository> clientRegistrations) throws Exception {
        http.cors(cors -> cors.configurationSource(corsConfigurationSource()))
                // The refresh cookie is SameSite=Strict, which is itself a
                // complete CSRF mitigation for it; everything else here is a
                // stateless JSON API authenticated by a Bearer header, which
                // CSRF tokens don't protect anyway.
                .csrf(AbstractHttpConfigurer::disable)
                // No anonymous principal for a pure API: a missing/invalid
                // token should always be 401, never a 403 "access denied"
                // (Spring's default for an authenticated-but-anonymous user).
                .anonymous(AbstractHttpConfigurer::disable)
                .exceptionHandling(exceptions -> exceptions.authenticationEntryPoint(
                        (request, response, authException) -> response.sendError(HttpServletResponse.SC_UNAUTHORIZED)))
                .authorizeHttpRequests(auth -> auth.requestMatchers(
                                "/healthz",
                                "/.well-known/jwks.json",
                                "/oauth2/**",
                                "/login/**",
                                "/api/v1/auth/refresh",
                                "/api/v1/auth/logout")
                        .permitAll()
                        // Preview only — POST .../accept still requires
                        // authentication via the default rule below.
                        .requestMatchers(HttpMethod.GET, "/api/v1/invitations/*")
                        .permitAll()
                        .anyRequest()
                        .authenticated())
                .addFilterBefore(
                        new TenantJwtAuthenticationFilter(accessTokenService), UsernamePasswordAuthenticationFilter.class);

        ClientRegistrationRepository clientRegistrationRepository = clientRegistrations.getIfAvailable();
        if (clientRegistrationRepository != null) {
            http.oauth2Login(oauth2 -> oauth2
                    .authorizationEndpoint(
                            endpoint -> endpoint.authorizationRequestResolver(pkceResolver(clientRegistrationRepository)))
                    .successHandler(successHandler));
        }

        return http.build();
    }

    private OAuth2AuthorizationRequestResolver pkceResolver(ClientRegistrationRepository clientRegistrationRepository) {
        DefaultOAuth2AuthorizationRequestResolver resolver = new DefaultOAuth2AuthorizationRequestResolver(
                clientRegistrationRepository, OAuth2AuthorizationRequestRedirectFilter.DEFAULT_AUTHORIZATION_REQUEST_BASE_URI);
        resolver.setAuthorizationRequestCustomizer(OAuth2AuthorizationRequestCustomizers.withPkce());
        return resolver;
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of(webAppUrl));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
