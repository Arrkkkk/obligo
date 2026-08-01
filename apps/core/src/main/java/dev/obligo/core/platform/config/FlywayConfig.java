package dev.obligo.core.platform.config;

import org.flywaydb.core.Flyway;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Map;

/**
 * Flyway gets its own unpooled connection, separate from the app's Hikari
 * pool (DataSourceConfig). Postgres migrations hold an advisory lock on one
 * connection while executing DDL on another, so running Flyway through a
 * pool capped at size 1 (as tests do, to pin tenant queries to a single
 * physical connection — see build.gradle.kts) deadlocks it against itself.
 * Defining this bean also makes Spring Boot's FlywayAutoConfiguration back
 * off (@ConditionalOnMissingBean(Flyway.class)), so there's only one path
 * that runs migrations.
 */
@Configuration
public class FlywayConfig {

    @Bean(initMethod = "migrate")
    public Flyway flyway() {
        DatabaseConnectionDetails details = DatabaseConnectionDetails.ownerFromEnv();
        String appDbPassword = System.getenv("APP_DB_PASSWORD");
        if (appDbPassword == null || appDbPassword.isBlank()) {
            throw new IllegalStateException("APP_DB_PASSWORD environment variable is not set");
        }
        return Flyway.configure()
                .dataSource(details.jdbcUrl(), details.username(), details.password())
                .placeholders(Map.of("app_db_password", appDbPassword))
                .load();
    }
}
