package dev.obligo.core.platform.identity;

import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * No RLS / TenantContext here either (see V5) — "which org(s) does this
 * user belong to" is a lookup BY user_id across orgs, run before there's a
 * resolved tenant for the request. Only one membership per user exists in
 * this phase (auto-created personal org, §10.8) — multi-org support and
 * org-switching are future work.
 */
@Repository
public class OrgMembershipRepository {

    private final JdbcTemplate jdbcTemplate;

    public OrgMembershipRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional(readOnly = true)
    public OrgMembership findByUserId(UUID userId) {
        try {
            return jdbcTemplate.queryForObject(
                    "SELECT org_id, user_id, role FROM org_members WHERE user_id = ?",
                    (rs, rowNum) -> new OrgMembership(
                            UUID.fromString(rs.getString("org_id")),
                            UUID.fromString(rs.getString("user_id")),
                            rs.getString("role")),
                    userId);
        } catch (EmptyResultDataAccessException e) {
            throw new IllegalStateException("No org membership found for user " + userId);
        }
    }

    @Transactional
    public void insert(UUID orgId, UUID userId, String role) {
        jdbcTemplate.update("INSERT INTO org_members (org_id, user_id, role) VALUES (?, ?, ?)", orgId, userId, role);
    }

    @Transactional
    public void deleteByUserId(UUID userId) {
        jdbcTemplate.update("DELETE FROM org_members WHERE user_id = ?", userId);
    }
}
