package dev.obligo.core.platform.document;

import dev.obligo.core.platform.tenancy.TenantScopedRepository;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * RLS-backed (V10) -- every method here relies on TenantConnectionPreparer
 * having set app.org_id from the caller's token (§10.9 layers 2/3), same
 * mechanism as OrganizationRepository. Unlike OrganizationRepository, these
 * queries also carry an explicit org_id predicate: belt-and-suspenders, not
 * a substitute for RLS (see TenantScopedRepository's Javadoc on what the
 * ArchUnit rules do and don't prove).
 */
@Repository
public class SourceRepository implements TenantScopedRepository {

    private static final String COLUMNS =
            "id, org_id, uploaded_by, filename, byte_size, sha256, mime_type, storage_key, status, rejection_reason, created_at, committed_at";

    private final JdbcTemplate jdbcTemplate;

    public SourceRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public void insert(
            UUID id, UUID orgId, UUID uploadedBy, String filename, long byteSize, String sha256, String storageKey) {
        jdbcTemplate.update(
                "INSERT INTO sources (id, org_id, uploaded_by, filename, byte_size, sha256, storage_key, status) "
                        + "VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')",
                id, orgId, uploadedBy, filename, byteSize, sha256, storageKey);
    }

    /** Dedup lookup (§11.2) -- only a source that actually finished uploading counts as a duplicate. */
    @Transactional(readOnly = true)
    public Optional<Source> findByOrgAndSha256Uploaded(UUID orgId, String sha256) {
        try {
            return Optional.ofNullable(jdbcTemplate.queryForObject(
                    "SELECT " + COLUMNS + " FROM sources WHERE org_id = ? AND sha256 = ? AND status = 'UPLOADED'",
                    SourceRepository::mapRow,
                    orgId, sha256));
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    /**
     * Locks the row for the duration of the enclosing transaction so two
     * concurrent commit calls for the same source can't both observe
     * PENDING and both transition it -- same TOCTOU concern, same fix, as
     * RefreshTokenRepository.findByHashForUpdate. Only used by
     * SourceCommitGateway's short gatekeeper transaction now -- see its
     * Javadoc for why the lock is deliberately NOT held across the
     * expensive verification work anymore.
     */
    @Transactional
    public Optional<Source> findByIdForUpdate(UUID orgId, UUID id) {
        try {
            return Optional.ofNullable(jdbcTemplate.queryForObject(
                    "SELECT " + COLUMNS + " FROM sources WHERE id = ? AND org_id = ? FOR UPDATE",
                    SourceRepository::mapRow,
                    id, orgId));
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    /** Unlocked read, for reconciling state after a guarded write affected zero rows (see SourceCommitGateway). */
    @Transactional(readOnly = true)
    public Optional<Source> findById(UUID orgId, UUID id) {
        try {
            return Optional.ofNullable(jdbcTemplate.queryForObject(
                    "SELECT " + COLUMNS + " FROM sources WHERE id = ? AND org_id = ?",
                    SourceRepository::mapRow,
                    id, orgId));
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    /**
     * Returns whether a row was actually transitioned -- false means a
     * concurrent commit already moved this source out of PENDING first
     * (see SourceCommitGateway.finalizeVerification's reconciliation path).
     */
    @Transactional
    public boolean markUploaded(UUID orgId, UUID id, String mimeType, Instant committedAt) {
        int rowsUpdated = jdbcTemplate.update(
                "UPDATE sources SET status = 'UPLOADED', mime_type = ?, committed_at = ? "
                        + "WHERE id = ? AND org_id = ? AND status = 'PENDING'",
                mimeType, Timestamp.from(committedAt), id, orgId);
        return rowsUpdated == 1;
    }

    /** See markUploaded's Javadoc on the return value. */
    @Transactional
    public boolean markRejected(UUID orgId, UUID id, String reason) {
        int rowsUpdated = jdbcTemplate.update(
                "UPDATE sources SET status = 'REJECTED', rejection_reason = ? "
                        + "WHERE id = ? AND org_id = ? AND status = 'PENDING'",
                reason, id, orgId);
        return rowsUpdated == 1;
    }

    /** Test-cleanup only, same role this method plays on every other repository in this codebase. */
    @Transactional
    public void deleteById(UUID orgId, UUID id) {
        jdbcTemplate.update("DELETE FROM sources WHERE id = ? AND org_id = ?", id, orgId);
    }

    private static Source mapRow(java.sql.ResultSet rs, int rowNum) throws java.sql.SQLException {
        Timestamp committedAt = rs.getTimestamp("committed_at");
        return new Source(
                UUID.fromString(rs.getString("id")),
                UUID.fromString(rs.getString("org_id")),
                UUID.fromString(rs.getString("uploaded_by")),
                rs.getString("filename"),
                rs.getLong("byte_size"),
                rs.getString("sha256"),
                rs.getString("mime_type"),
                rs.getString("storage_key"),
                SourceStatus.valueOf(rs.getString("status")),
                rs.getString("rejection_reason"),
                rs.getTimestamp("created_at").toInstant(),
                committedAt != null ? committedAt.toInstant() : null);
    }
}
