package dev.obligo.core.platform.security;

import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Timestamp;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/** Identity-plane table, no RLS — see V6's migration comment. */
@Repository
public class RefreshTokenRepository {

    private final JdbcTemplate jdbcTemplate;

    public RefreshTokenRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public void insert(UUID id, UUID familyId, UUID userId, String tokenHash, String userAgent, String ip) {
        jdbcTemplate.update(
                "INSERT INTO refresh_tokens (id, family_id, user_id, token_hash, user_agent, ip) VALUES (?, ?, ?, ?, ?, ?)",
                id, familyId, userId, tokenHash, userAgent, ip);
    }

    /**
     * Locks the row for the duration of the caller's transaction (FOR
     * UPDATE) so two concurrent refresh attempts on the same token can't
     * both observe "unused" and both succeed — the classic TOCTOU race
     * rotation logic has to close.
     */
    @Transactional
    public Optional<RefreshToken> findByHashForUpdate(String tokenHash) {
        try {
            RefreshToken token = jdbcTemplate.queryForObject(
                    "SELECT id, family_id, user_id, token_hash, issued_at, used_at, replaced_by, revoked_at "
                            + "FROM refresh_tokens WHERE token_hash = ? FOR UPDATE",
                    (rs, rowNum) -> new RefreshToken(
                            UUID.fromString(rs.getString("id")),
                            UUID.fromString(rs.getString("family_id")),
                            UUID.fromString(rs.getString("user_id")),
                            rs.getString("token_hash"),
                            rs.getTimestamp("issued_at").toInstant(),
                            rs.getTimestamp("used_at") != null ? rs.getTimestamp("used_at").toInstant() : null,
                            rs.getString("replaced_by") != null ? UUID.fromString(rs.getString("replaced_by")) : null,
                            rs.getTimestamp("revoked_at") != null ? rs.getTimestamp("revoked_at").toInstant() : null),
                    tokenHash);
            return Optional.ofNullable(token);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Transactional
    public void markUsed(UUID id, UUID replacedById) {
        jdbcTemplate.update(
                "UPDATE refresh_tokens SET used_at = now(), replaced_by = ? WHERE id = ?", replacedById, id);
    }

    @Transactional
    public void revokeFamily(UUID familyId) {
        jdbcTemplate.update(
                "UPDATE refresh_tokens SET revoked_at = now() WHERE family_id = ? AND revoked_at IS NULL", familyId);
    }

    @Transactional
    public void deleteByUserId(UUID userId) {
        jdbcTemplate.update("DELETE FROM refresh_tokens WHERE user_id = ?", userId);
    }

    @Transactional(readOnly = true)
    public List<RefreshToken> findByFamilyId(UUID familyId) {
        return jdbcTemplate.query(
                "SELECT id, family_id, user_id, token_hash, issued_at, used_at, replaced_by, revoked_at "
                        + "FROM refresh_tokens WHERE family_id = ?",
                (rs, rowNum) -> new RefreshToken(
                        UUID.fromString(rs.getString("id")),
                        UUID.fromString(rs.getString("family_id")),
                        UUID.fromString(rs.getString("user_id")),
                        rs.getString("token_hash"),
                        rs.getTimestamp("issued_at").toInstant(),
                        rs.getTimestamp("used_at") != null ? rs.getTimestamp("used_at").toInstant() : null,
                        rs.getString("replaced_by") != null ? UUID.fromString(rs.getString("replaced_by")) : null,
                        rs.getTimestamp("revoked_at") != null ? rs.getTimestamp("revoked_at").toInstant() : null),
                familyId);
    }
}
