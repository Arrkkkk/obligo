package dev.obligo.core.platform.segmentation;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * A real, socket-level stand-in for apps/brain's segment trigger/status
 * endpoints -- not a Mockito mock of BrainClient. This is the "split proof"
 * this checkpoint's design discussion settled on: it proves apps/core's own
 * logic (request shaping, response mapping, SSE polling/heartbeat/close
 * timing, disconnect handling) fast and deterministically, in real HTTP,
 * without needing a live apps/brain + Celery + Redis stack in every CI run.
 * It does NOT re-prove the cross-service wire contract -- that's proven
 * for real by apps/brain's own tests (test_segment_source.py,
 * test_segmentation_task.py) and by this checkpoint's own one-time live
 * manual verification (see CLAUDE.md).
 *
 * Uses the JDK's built-in com.sun.net.httpserver.HttpServer -- no new test
 * dependency.
 */
final class FakeBrainServer implements AutoCloseable {

    record CannedResponse(int status, String body) {}

    private final HttpServer server;
    private final String expectedToken;
    private final List<CannedResponse> postResponses = new CopyOnWriteArrayList<>();
    private final List<CannedResponse> getResponses = new CopyOnWriteArrayList<>();
    private final AtomicInteger postCallCount = new AtomicInteger();
    private final AtomicInteger getCallCount = new AtomicInteger();

    FakeBrainServer(String expectedToken) throws IOException {
        this.expectedToken = expectedToken;
        this.server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        this.server.createContext("/api/v1/sources/", this::handle);
        this.server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        this.server.start();
    }

    String baseUrl() {
        return "http://127.0.0.1:" + server.getAddress().getPort();
    }

    void enqueuePostResponse(int status, String body) {
        postResponses.add(new CannedResponse(status, body));
    }

    void enqueueGetResponse(int status, String body) {
        getResponses.add(new CannedResponse(status, body));
    }

    int postCallCount() {
        return postCallCount.get();
    }

    int getCallCount() {
        return getCallCount.get();
    }

    void reset() {
        postResponses.clear();
        getResponses.clear();
        postCallCount.set(0);
        getCallCount.set(0);
    }

    private void handle(HttpExchange exchange) throws IOException {
        try {
            String token = exchange.getRequestHeaders().getFirst("X-Internal-Service-Token");
            if (!expectedToken.equals(token)) {
                sendJson(exchange, 401, "{\"detail\":\"invalid internal service token\"}");
                return;
            }

            boolean isPost = "POST".equalsIgnoreCase(exchange.getRequestMethod());
            List<CannedResponse> responses = isPost ? postResponses : getResponses;
            int index = isPost ? postCallCount.getAndIncrement() : getCallCount.getAndIncrement();

            if (responses.isEmpty()) {
                sendJson(exchange, 500, "{\"detail\":\"FakeBrainServer has no canned response queued\"}");
                return;
            }
            CannedResponse response = responses.get(Math.min(index, responses.size() - 1));
            sendJson(exchange, response.status(), response.body());
        } finally {
            exchange.close();
        }
    }

    private static void sendJson(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    @Override
    public void close() {
        server.stop(0);
    }
}
