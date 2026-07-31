package dev.obligo.core.platform.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;
import java.net.URI;

@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource() {
        String databaseUrl = System.getenv("DATABASE_URL");
        if (databaseUrl == null || databaseUrl.isBlank()) {
            throw new IllegalStateException("DATABASE_URL environment variable is not set");
        }

        URI uri = URI.create(databaseUrl);
        String[] userInfo = uri.getUserInfo().split(":", 2);
        String jdbcUrl = "jdbc:postgresql://" + uri.getHost()
                + (uri.getPort() != -1 ? ":" + uri.getPort() : "")
                + uri.getPath()
                + (uri.getQuery() != null ? "?" + uri.getQuery() : "");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(jdbcUrl);
        config.setUsername(userInfo[0]);
        config.setPassword(userInfo[1]);
        config.setMaximumPoolSize(5);
        config.setPoolName("core-hikari");

        return new HikariDataSource(config);
    }
}
