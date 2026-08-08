package dev.obligo.core.platform.security;

import dev.obligo.core.platform.tenancy.TenantContext;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

/**
 * The only place org_id ever enters TenantContext for an authenticated
 * request — read from a verified access token's org_id claim, never from a
 * header or body field (§10.9 Layer 2). One org per token (§10.4) is what
 * makes this unconditional: there is no "which org do you mean" ambiguity
 * for this filter to get wrong, because the token only ever carries one.
 */
public class TenantJwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String BEARER_PREFIX = "Bearer ";

    private final AccessTokenService accessTokenService;

    public TenantJwtAuthenticationFilter(AccessTokenService accessTokenService) {
        this.accessTokenService = accessTokenService;
    }

    /**
     * Real finding from the §21 Phase 3 SSE checkpoint, not a defensive
     * guess: OncePerRequestFilter.shouldNotFilterAsyncDispatch() defaults to
     * true, which is fine for every endpoint that existed before an
     * SseEmitter-returning one did. An SseEmitter completing (terminal
     * status, max-duration close, or a client disconnect) makes Tomcat
     * perform an internal ASYNC dispatch back through the *entire* filter
     * chain to finalize the response -- including Spring Security's own
     * AuthorizationFilter, which runs on every dispatch type regardless.
     * With this filter skipping itself on that second pass (the default),
     * SecurityContextHolder is empty by the time AuthorizationFilter checks
     * it, and the completion dispatch fails with
     * AuthenticationCredentialsNotFoundException -- confirmed by a real
     * failing SegmentationFlowTest run, not predicted from documentation.
     * Overriding this to false makes the filter re-verify the same Bearer
     * header (still present on the same underlying HttpServletRequest) on
     * the async-completion dispatch too, exactly as it did on the original
     * request.
     */
    @Override
    protected boolean shouldNotFilterAsyncDispatch() {
        return false;
    }

    /**
     * Same finding, second dispatch type: an abrupt client disconnect mid-
     * stream (a broken pipe on emitter.send()) makes Tomcat perform an
     * ERROR dispatch, not just the plain ASYNC one covered above --
     * confirmed the same way, by a real clientDisconnectStopsServerSidePolling
     * run logging the identical AuthenticationCredentialsNotFoundException
     * on that path. shouldNotFilterErrorDispatch() defaults to true for the
     * same reason shouldNotFilterAsyncDispatch() does; same fix.
     */
    @Override
    protected boolean shouldNotFilterErrorDispatch() {
        return false;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith(BEARER_PREFIX)) {
            try {
                AccessTokenClaims claims = accessTokenService.verify(header.substring(BEARER_PREFIX.length()));
                TenantContext.set(claims.orgId());

                // Authorities come straight from the token's own "scopes"
                // claim (baked in at mint time from role, §10.3) — never
                // re-derived from role here, and never from anything
                // client-supplied.
                List<GrantedAuthority> authorities = claims.scopes().stream()
                        .map(Capability::wireName)
                        .<GrantedAuthority>map(SimpleGrantedAuthority::new)
                        .toList();
                SecurityContextHolder.getContext()
                        .setAuthentication(new UsernamePasswordAuthenticationToken(claims, null, authorities));
            } catch (InvalidAccessTokenException e) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                return;
            }
        }

        try {
            filterChain.doFilter(request, response);
        } finally {
            // Mandatory: this thread returns to the servlet container's
            // pool after this request. A forgotten clear() here is the
            // same class of leak as the connection-pooling trap in §10.9,
            // just one layer up — TenantContext's own javadoc says so.
            TenantContext.clear();
        }
    }
}
