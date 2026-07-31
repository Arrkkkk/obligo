import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("web");

export async function GET() {
  return tracer.startActiveSpan("web.healthz", async (span) => {
    try {
      const coreUrl = process.env.CORE_URL ?? "http://localhost:8080";
      const res = await fetch(`${coreUrl}/healthz`, { cache: "no-store" });
      const core = await res.json();

      return Response.json(
        { status: res.ok ? "ok" : "down", core },
        { status: res.ok ? 200 : 503 },
      );
    } finally {
      span.end();
    }
  });
}
