package dev.obligo.core.platform.tenancy;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Repository
public class OrganizationRepository {

    private final JdbcTemplate jdbcTemplate;

    public OrganizationRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * The RLS policy's WITH CHECK requires the inserted row's id to equal
     * the caller's app.org_id, so TenantContext must be set to {@code id}
     * (the org creating itself) before calling this.
     */
    @Transactional
    public void insert(UUID id, String name) {
        jdbcTemplate.update("INSERT INTO organizations (id, name) VALUES (?, ?)", id, name);
    }

    @Transactional(readOnly = true)
    public List<Organization> findAll() {
        return jdbcTemplate.query(
                "SELECT id, name, created_at FROM organizations",
                (rs, rowNum) -> new Organization(
                        UUID.fromString(rs.getString("id")),
                        rs.getString("name"),
                        rs.getTimestamp("created_at").toInstant()));
    }

    @Transactional
    public void delete(UUID id) {
        jdbcTemplate.update("DELETE FROM organizations WHERE id = ?", id);
    }

    @Transactional(readOnly = true)
    public long currentBackendPid() {
        Long pid = jdbcTemplate.queryForObject("SELECT pg_backend_pid()", Long.class);
        return pid;
    }
}
