package dev.obligo.core;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Map;

@RestController
public class HealthController {

    private final DataSource dataSource;

    public HealthController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @GetMapping("/healthz")
    public ResponseEntity<Map<String, Object>> healthz() {
        try (Connection connection = dataSource.getConnection()) {
            connection.createStatement().execute("SELECT 1");
            return ResponseEntity.ok(Map.of(
                    "status", "ok",
                    "database", "reachable"
            ));
        } catch (SQLException e) {
            return ResponseEntity.status(503).body(Map.of(
                    "status", "down",
                    "database", "unreachable",
                    "error", e.getMessage()
            ));
        }
    }
}
