/**
 * OpenTelemetry Tracing Setup for GitHub Apps
 *
 * Complete setup examples for adding observability to your GitHub App
 * with progressive development approach: start simple, add complexity as needed.
 */

import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-otlp-http";
import { trace, context, SpanStatusCode } from "@opentelemetry/api";

// =============================================================================
// Basic Setup - Start Here
// =============================================================================

/**
 * Minimal tracing setup for development
 * Just initialize tracing and add a constant trigger for testing
 */
export function initializeBasicTracing() {
  const traceExporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318/v1/traces",
  });

  const sdk = new NodeSDK({
    traceExporter,
    instrumentations: [getNodeAutoInstrumentations()],
    serviceName: process.env.OTEL_SERVICE_NAME || "github-app",
    serviceVersion: process.env.OTEL_SERVICE_VERSION || "1.0.0",
  });

  sdk.start();
  console.log("✅ OpenTelemetry tracing initialized");
  return sdk;
}

/**
 * Constant trace trigger for testing your tracing setup
 * Call this endpoint to verify traces are being sent correctly
 */
export async function triggerTestTrace(): Promise<void> {
  const tracer = trace.getTracer("github-app-testing");

  const span = tracer.startSpan("debug.test_trace", {
    attributes: {
      "test.trigger": "manual",
      "test.timestamp": Date.now(),
      "environment": process.env.NODE_ENV || "development",
    },
  });

  try {
    span.addEvent("Test trace started");

    // Simulate some processing
    await new Promise(resolve => setTimeout(resolve, 100));
    span.addEvent("Simulated work completed");

    // Add some test attributes
    span.setAttributes({
      "test.operation": "manual_trigger",
      "test.success": true,
    });

    span.setStatus({ code: SpanStatusCode.OK });
    console.log("✅ Test trace completed successfully");
  } catch (error) {
    span.recordException(error as Error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: (error as Error).message,
    });
    console.error("❌ Test trace failed:", error);
  } finally {
    span.end();
  }
}

// =============================================================================
// Advanced Setup - Production Ready
// =============================================================================

/**
 * Production-ready tracing setup with error handling and configuration
 */
export function initializeProductionTracing() {
  try {
    const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
    if (!endpoint) {
      console.warn("OTEL_EXPORTER_OTLP_ENDPOINT not set, tracing disabled");
      return null;
    }

    const headers = process.env.OTEL_EXPORTER_OTLP_HEADERS || "";
    const headerMap = headers
      .split(",")
      .reduce((acc, header) => {
        const [key, value] = header.split("=");
        if (key && value) {
          acc[key.trim()] = value.trim();
        }
        return acc;
      }, {} as Record<string, string>);

    const traceExporter = new OTLPTraceExporter({
      url: endpoint,
      headers: headerMap,
    });

    const sdk = new NodeSDK({
      traceExporter,
      instrumentations: [
        getNodeAutoInstrumentations({
          // Disable file system instrumentation (noisy)
          "@opentelemetry/instrumentation-fs": {
            enabled: false,
          },
          // Customize HTTP instrumentation
          "@opentelemetry/instrumentation-http": {
            requestHook: (span, request) => {
              span.setAttributes({
                "http.request.size": request.headers["content-length"] || 0,
              });
            },
          },
        }),
      ],
      serviceName: process.env.OTEL_SERVICE_NAME || "github-app",
      serviceVersion: process.env.OTEL_SERVICE_VERSION || "1.0.0",
    });

    sdk.start();
    console.log("✅ Production tracing initialized");
    return sdk;
  } catch (error) {
    console.error("❌ Failed to initialize tracing:", error);
    return null;
  }
}

// =============================================================================
// Environment-Specific Configuration
// =============================================================================

/**
 * Environment configuration for different deployment targets
 */
export interface TracingConfig {
  enabled: boolean;
  endpoint: string;
  headers: Record<string, string>;
  sampleRate: number;
  serviceName: string;
}

export function getTracingConfig(): TracingConfig {
  const env = process.env.NODE_ENV || "development";

  switch (env) {
    case "production":
      return {
        enabled: true,
        endpoint: process.env.OTEL_EXPORTER_OTLP_ENDPOINT!,
        headers: parseOTLPHeaders(process.env.OTEL_EXPORTER_OTLP_HEADERS || ""),
        sampleRate: parseFloat(process.env.OTEL_TRACE_SAMPLE_RATE || "0.1"),
        serviceName: process.env.OTEL_SERVICE_NAME || "github-app",
      };

    case "staging":
      return {
        enabled: true,
        endpoint: process.env.OTEL_EXPORTER_OTLP_ENDPOINT!,
        headers: parseOTLPHeaders(process.env.OTEL_EXPORTER_OTLP_HEADERS || ""),
        sampleRate: parseFloat(process.env.OTEL_TRACE_SAMPLE_RATE || "0.5"),
        serviceName: `${process.env.OTEL_SERVICE_NAME || "github-app"}-staging`,
      };

    default: // development, test
      return {
        enabled: !!process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
        endpoint: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318/v1/traces",
        headers: {},
        sampleRate: 1.0, // Trace everything in development
        serviceName: `${process.env.OTEL_SERVICE_NAME || "github-app"}-dev`,
      };
  }
}

function parseOTLPHeaders(headerString: string): Record<string, string> {
  return headerString
    .split(",")
    .reduce((acc, header) => {
      const [key, value] = header.split("=");
      if (key && value) {
        acc[key.trim()] = value.trim();
      }
      return acc;
    }, {} as Record<string, string>);
}

// =============================================================================
// Cloudflare Workers Adaptation
// =============================================================================

/**
 * Simplified tracing for Cloudflare Workers
 * Full OpenTelemetry SDK doesn't work in Workers runtime
 */
export class WorkersTraceExporter {
  constructor(
    private endpoint: string,
    private headers: Record<string, string> = {}
  ) {}

  async exportSpans(spans: any[]): Promise<void> {
    try {
      const response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...this.headers,
        },
        body: JSON.stringify({
          resourceSpans: [{
            spans: spans.map(span => ({
              traceId: span.traceId,
              spanId: span.spanId,
              name: span.name,
              startTimeUnixNano: span.startTime * 1000000,
              endTimeUnixNano: span.endTime * 1000000,
              attributes: Object.entries(span.attributes).map(([key, value]) => ({
                key,
                value: { stringValue: String(value) },
              })),
              status: span.status,
            })),
          }],
        }),
      });

      if (!response.ok) {
        console.error("Failed to export traces:", response.statusText);
      }
    } catch (error) {
      console.error("Trace export error:", error);
    }
  }
}

/**
 * Simple span implementation for Cloudflare Workers
 */
export class SimpleSpan {
  public readonly traceId: string;
  public readonly spanId: string;
  public readonly startTime: number;
  public endTime?: number;
  public attributes: Record<string, any> = {};
  public status: any = { code: SpanStatusCode.OK };

  constructor(public name: string) {
    this.traceId = generateTraceId();
    this.spanId = generateSpanId();
    this.startTime = Date.now();
  }

  setAttributes(attributes: Record<string, any>): void {
    this.attributes = { ...this.attributes, ...attributes };
  }

  setStatus(status: any): void {
    this.status = status;
  }

  end(): void {
    this.endTime = Date.now();
  }
}

function generateTraceId(): string {
  return Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join("");
}

function generateSpanId(): string {
  return Array.from({ length: 16 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join("");
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Create a tracer with consistent naming
 */
export function getTracer(name?: string): trace.Tracer {
  const serviceName = process.env.OTEL_SERVICE_NAME || "github-app";
  return trace.getTracer(name || serviceName);
}

/**
 * Wrapper for automatic span creation and cleanup
 */
export async function withSpan<T>(
  tracer: trace.Tracer,
  name: string,
  attributes: Record<string, any>,
  fn: (span: trace.Span) => Promise<T>
): Promise<T> {
  const span = tracer.startSpan(name, { attributes });

  try {
    const result = await context.with(trace.setSpan(context.active(), span), () => fn(span));
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error) {
    span.recordException(error as Error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: (error as Error).message,
    });
    throw error;
  } finally {
    span.end();
  }
}

// =============================================================================
// Development Helpers
// =============================================================================

/**
 * Setup tracing with development-friendly defaults
 */
export function initializeDevelopmentTracing() {
  // Check if Jaeger is available locally
  const isJaegerAvailable = process.env.JAEGER_ENDPOINT || false;

  const config = isJaegerAvailable
    ? {
        url: "http://localhost:14268/api/traces",
      }
    : {
        url: "http://localhost:4318/v1/traces", // OTLP collector
      };

  return initializeBasicTracing();
}

/**
 * Health check for tracing setup
 */
export async function checkTracingHealth(): Promise<boolean> {
  try {
    await triggerTestTrace();
    return true;
  } catch (error) {
    console.error("Tracing health check failed:", error);
    return false;
  }
}