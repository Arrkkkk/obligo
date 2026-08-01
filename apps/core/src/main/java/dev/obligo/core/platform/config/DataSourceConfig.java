package dev.obligo.core.platform.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    // Flyway (owner role) must run first — V2 is what creates the obligo_app
    // role this pool authenticates as.
    @Bean
    @DependsOn("flyway")
    public DataSource dataSource() {
        DatabaseConnectionDetails details = DatabaseConnectionDetails.appRoleFromEnv();
        String maxPoolSizeEnv = System.getenv("DATABASE_MAX_POOL_SIZE");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(details.jdbcUrl());
        config.setUsername(details.username());
        config.setPassword(details.password());
        config.setMaximumPoolSize(maxPoolSizeEnv != null ? Integer.parseInt(maxPoolSizeEnv) : 5);
        config.setPoolName("core-hikari");

        return new HikariDataSource(config);
    }
}
