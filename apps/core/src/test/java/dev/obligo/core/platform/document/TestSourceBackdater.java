package dev.obligo.core.platform.document;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;

/**
 * Test-only: backdates a source's created_at to simulate an abandoned
 * upload intent, for SourceUploadFlowTest's staleness-check coverage. Has
 * to be a real @Component with a @Transactional method, not a raw
 * JdbcTemplate call from inside the test method itself --
 * TenantConnectionPreparer's AOP only fires around @Transactional
 * (@annotation or @within), and without it app.org_id never gets set, so
 * RLS's fail-closed policy would silently match zero rows instead of
 * erroring, making a bug here easy to miss.
 */
@Component
class TestSourceBackdater {

    private final JdbcTemplate jdbcTemplate;

    TestSourceBackdater(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    void backdateCreatedAt(UUID orgId, UUID sourceId, Instant createdAt) {
        jdbcTemplate.update(
                "UPDATE sources SET created_at = ? WHERE id = ? AND org_id = ?",
                Timestamp.from(createdAt),
                sourceId,
                orgId);
    }
}
