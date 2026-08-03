package dev.obligo.core.platform.identity;

import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

/** No RLS — see V9's migration comment. */
@Repository
public class InvitationRepository {

    private final JdbcTemplate jdbcTemplate;

    public InvitationRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public void insert(
            UUID id, UUID orgId, String email, Role role, String tokenHash, UUID invitedBy, Instant expiresAt) {
        jdbcTemplate.update(
                "INSERT INTO invitations (id, org_id, email, role, token_hash, invited_by, expires_at) "
                        + "VALUES (?, ?, ?, ?, ?, ?, ?)",
                id, orgId, email.toLowerCase(Locale.ROOT), role.name(), tokenHash, invitedBy, Timestamp.from(expiresAt));
    }

    @Transactional(readOnly = true)
    public Optional<Invitation> findByTokenHash(String tokenHash) {
        try {
            return Optional.ofNullable(jdbcTemplate.queryForObject(
                    "SELECT id, org_id, email, role, token_hash, invited_by, created_at, expires_at, accepted_at, revoked_at "
                            + "FROM invitations WHERE token_hash = ?",
                    InvitationRepository::mapRow,
                    tokenHash));
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    /** Not accepted, not revoked, not yet expired — the row a re-invite should rotate rather than duplicate. */
    @Transactional(readOnly = true)
    public Optional<Invitation> findPendingByOrgAndEmail(UUID orgId, String email) {
        try {
            return Optional.ofNullable(jdbcTemplate.queryForObject(
                    "SELECT id, org_id, email, role, token_hash, invited_by, created_at, expires_at, accepted_at, revoked_at "
                            + "FROM invitations WHERE org_id = ? AND email = ? "
                            + "AND accepted_at IS NULL AND revoked_at IS NULL AND expires_at > now()",
                    InvitationRepository::mapRow,
                    orgId, email.toLowerCase(Locale.ROOT)));
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Transactional
    public void markAccepted(UUID id) {
        jdbcTemplate.update("UPDATE invitations SET accepted_at = now() WHERE id = ?", id);
    }

    @Transactional
    public void revoke(UUID id) {
        jdbcTemplate.update("UPDATE invitations SET revoked_at = now() WHERE id = ? AND revoked_at IS NULL", id);
    }

    @Transactional
    public void deleteById(UUID id) {
        jdbcTemplate.update("DELETE FROM invitations WHERE id = ?", id);
    }

    private static Invitation mapRow(java.sql.ResultSet rs, int rowNum) throws java.sql.SQLException {
        return new Invitation(
                UUID.fromString(rs.getString("id")),
                UUID.fromString(rs.getString("org_id")),
                rs.getString("email"),
                Role.valueOf(rs.getString("role")),
                rs.getString("token_hash"),
                UUID.fromString(rs.getString("invited_by")),
                rs.getTimestamp("created_at").toInstant(),
                rs.getTimestamp("expires_at").toInstant(),
                rs.getTimestamp("accepted_at") != null ? rs.getTimestamp("accepted_at").toInstant() : null,
                rs.getTimestamp("revoked_at") != null ? rs.getTimestamp("revoked_at").toInstant() : null);
    }
}
