package dev.obligo.core.platform.tenancy;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.datasource.DataSourceUtils;
import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.UUID;

/**
 * Resolves the §10.9 pooling trap: HikariCP hands out physical connections
 * regardless of which tenant's request last used them, and {@code SET LOCAL}
 * is scoped to a transaction, not a connection. This aspect is woven inside
 * the {@code @Transactional} advisor (see TransactionManagementConfig — the
 * transaction advisor is ordered HIGHEST_PRECEDENCE so it stays outermost,
 * and this aspect's @Order(10) places it just inside), so by the time it
 * runs, DataSourceUtils.getConnection returns the connection already bound
 * to the just-opened transaction. Setting app.org_id here means it is
 * re-applied on every transaction, on whatever physical connection Hikari
 * happens to hand back, and it is automatically cleared at commit/rollback
 * because it was set with is_local=true.
 */
@Aspect
@Component
@Order(10)
public class TenantConnectionPreparer {

    private final DataSource dataSource;

    public TenantConnectionPreparer(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Around("@annotation(org.springframework.transaction.annotation.Transactional) "
            + "|| @within(org.springframework.transaction.annotation.Transactional)")
    public Object setTenantGuc(ProceedingJoinPoint joinPoint) throws Throwable {
        UUID orgId = TenantContext.get();
        if (orgId != null && TransactionSynchronizationManager.isActualTransactionActive()) {
            Connection connection = DataSourceUtils.getConnection(dataSource);
            try (PreparedStatement statement = connection.prepareStatement("SELECT set_config('app.org_id', ?, true)")) {
                statement.setString(1, orgId.toString());
                statement.execute();
            } finally {
                DataSourceUtils.releaseConnection(connection, dataSource);
            }
        }
        return joinPoint.proceed();
    }
}
