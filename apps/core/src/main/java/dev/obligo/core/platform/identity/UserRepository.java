package dev.obligo.core.platform.identity;

import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

/**
 * Identity-plane table, no tenant scoping (see V4's migration comment) —
 * this runs with no TenantContext set, by design, since it's the lookup
 * that determines which org_id applies in the first place.
 */
@Repository
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    public UserRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional(readOnly = true)
    public Optional<User> findByGoogleSub(String googleSub) {
        try {
            User user = jdbcTemplate.queryForObject(
                    "SELECT id, google_sub, email, created_at FROM users WHERE google_sub = ?",
                    (rs, rowNum) -> new User(
                            UUID.fromString(rs.getString("id")),
                            rs.getString("google_sub"),
                            rs.getString("email"),
                            rs.getTimestamp("created_at").toInstant()),
                    googleSub);
            return Optional.ofNullable(user);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Transactional
    public User insert(String googleSub, String email) {
        UUID id = UUID.randomUUID();
        jdbcTemplate.update("INSERT INTO users (id, google_sub, email) VALUES (?, ?, ?)", id, googleSub, email);
        return findByGoogleSub(googleSub).orElseThrow();
    }

    @Transactional
    public void delete(UUID id) {
        jdbcTemplate.update("DELETE FROM users WHERE id = ?", id);
    }
}
