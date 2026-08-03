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
 *
 * Because there's no RLS here, updateRole must never trust a client-
 * supplied org_id — every caller in this codebase passes the org_id from
 * the caller's own verified token (see OrgMemberController), the same
 * discipline TenantContext enforces for tenant-scoped tables.
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
                            Role.valueOf(rs.getString("role"))),
                    userId);
        } catch (EmptyResultDataAccessException e) {
            throw new IllegalStateException("No org membership found for user " + userId);
        }
    }

    @Transactional
    public void insert(UUID orgId, UUID userId, Role role) {
        jdbcTemplate.update(
                "INSERT INTO org_members (org_id, user_id, role) VALUES (?, ?, ?)", orgId, userId, role.name());
    }

    /** orgId must come from the caller's own token — never a client-supplied value. */
    @Transactional
    public void updateRole(UUID orgId, UUID userId, Role role) {
        int rowsUpdated = jdbcTemplate.update(
                "UPDATE org_members SET role = ? WHERE org_id = ? AND user_id = ?", role.name(), orgId, userId);
        if (rowsUpdated == 0) {
            throw new NoSuchOrgMembershipException(orgId, userId);
        }
    }

    @Transactional
    public void deleteByUserId(UUID userId) {
        jdbcTemplate.update("DELETE FROM org_members WHERE user_id = ?", userId);
    }
}
