package dev.obligo.core.platform.security;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Repository
public class SecurityAuditEventRepository {

    private final JdbcTemplate jdbcTemplate;

    public SecurityAuditEventRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public void insert(String eventType, UUID userId, UUID familyId) {
        jdbcTemplate.update(
                "INSERT INTO security_audit_events (event_type, user_id, family_id) VALUES (?, ?, ?)",
                eventType, userId, familyId);
    }

    @Transactional(readOnly = true)
    public List<String> findEventTypesForFamily(UUID familyId) {
        return jdbcTemplate.queryForList(
                "SELECT event_type FROM security_audit_events WHERE family_id = ?", String.class, familyId);
    }

    @Transactional
    public void deleteByUserId(UUID userId) {
        jdbcTemplate.update("DELETE FROM security_audit_events WHERE user_id = ?", userId);
    }
}
