import { registerOTel } from "@vercel/otel";
import { ConsoleSpanExporter, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-node";

export function register() {
  registerOTel({
    serviceName: "web",
    spanProcessors: [new SimpleSpanProcessor(new ConsoleSpanExporter())],
  });
}
