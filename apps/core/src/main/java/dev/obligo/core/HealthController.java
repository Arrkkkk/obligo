package dev.obligo.core;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
public class HealthController {

    private final DataSource dataSource;
    private final String brainUrl;
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2))
            .build();

    public HealthController(DataSource dataSource, @Value("${brain.url}") String brainUrl) {
        this.dataSource = dataSource;
        this.brainUrl = brainUrl;
    }

    @GetMapping("/healthz")
    public ResponseEntity<Map<String, Object>> healthz() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("status", "ok");

        try (Connection connection = dataSource.getConnection()) {
            connection.createStatement().execute("SELECT 1");
            body.put("database", "reachable");
        } catch (SQLException e) {
            body.put("status", "down");
            body.put("database", "unreachable");
            body.put("databaseError", e.getMessage());
        }

        try {
            HttpRequest request = HttpRequest.newBuilder(URI.create(brainUrl + "/healthz"))
                    .timeout(Duration.ofSeconds(2))
                    .GET()
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            body.put("brain", response.statusCode() == 200 ? "reachable" : "unreachable");
        } catch (Exception e) {
            body.put("status", "down");
            body.put("brain", "unreachable");
            body.put("brainError", e.getMessage());
        }

        int statusCode = "ok".equals(body.get("status")) ? 200 : 503;
        return ResponseEntity.status(statusCode).body(body);
    }
}
