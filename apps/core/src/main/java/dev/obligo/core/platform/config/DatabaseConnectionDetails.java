package dev.obligo.core.platform.config;

import java.net.URI;

record DatabaseConnectionDetails(String jdbcUrl, String username, String password) {

    /** The Neon owner role from DATABASE_URL — DDL/GRANT privileges, used only to run Flyway. */
    static DatabaseConnectionDetails ownerFromEnv() {
        return parse(requireEnv("DATABASE_URL"));
    }

    /**
     * The obligo_app role (provisioned by migration V2) that the application
     * actually queries as. Same host/port/database as DATABASE_URL, but a
     * different login — see V2__create_app_role.sql for why.
     */
    static DatabaseConnectionDetails appRoleFromEnv() {
        DatabaseConnectionDetails owner = parse(requireEnv("DATABASE_URL"));
        return new DatabaseConnectionDetails(owner.jdbcUrl(), "obligo_app", requireEnv("APP_DB_PASSWORD"));
    }

    private static DatabaseConnectionDetails parse(String databaseUrl) {
        URI uri = URI.create(databaseUrl);
        String[] userInfo = uri.getUserInfo().split(":", 2);
        String jdbcUrl = "jdbc:postgresql://" + uri.getHost()
                + (uri.getPort() != -1 ? ":" + uri.getPort() : "")
                + uri.getPath()
                + (uri.getQuery() != null ? "?" + uri.getQuery() : "");

        return new DatabaseConnectionDetails(jdbcUrl, userInfo[0], userInfo[1]);
    }

    private static String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(name + " environment variable is not set");
        }
        return value;
    }
}
