package dev.obligo.core.platform.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Pins the @Transactional advisor to HIGHEST_PRECEDENCE so it is the
 * outermost advice on any @Transactional method. TenantConnectionPreparer
 * (@Order(10)) then runs nested inside it, after the transaction — and its
 * physical connection — already exist.
 */
@Configuration
@EnableTransactionManagement(order = Ordered.HIGHEST_PRECEDENCE)
public class TransactionManagementConfig {
}
