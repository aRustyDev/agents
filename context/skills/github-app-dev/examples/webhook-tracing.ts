/**
 * Webhook Tracing Patterns for GitHub Apps
 *
 * Examples of adding OpenTelemetry tracing to webhook handlers
 * with practical patterns for debugging and monitoring.
 */

import { trace, context, SpanStatusCode } from "@opentelemetry/api";
import { Webhooks } from "@octokit/webhooks";
import { Octokit } from "@octokit/rest";

// =============================================================================
// Basic Webhook Tracing
// =============================================================================

/**
 * Create webhooks with basic tracing
 * Traces the overall webhook processing time and outcome
 */
export function createTracedWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });
  const tracer = trace.getTracer("github-app-webhooks");

  webhooks.on("pull_request.opened", async ({ payload }) => {
    const span = tracer.startSpan("webhook.pull_request.opened", {
      attributes: {
        "github.event": "pull_request.opened",
        "github.repository": payload.repository.full_name,
        "github.pr.number": payload.pull_request.number,
        "github.pr.author": payload.pull_request.user.login,
        "github.installation.id": payload.installation?.id,
      },
    });

    try {
      console.log(`Processing PR #${payload.pull_request.number} opened`);

      // Your webhook logic here
      await processPullRequestOpened(payload);

      span.setStatus({ code: SpanStatusCode.OK });
      span.addEvent("Pull request processing completed");
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
  });

  return webhooks;
}

// =============================================================================
// Detailed API Call Tracing
// =============================================================================

/**
 * Wrapper for GitHub API calls with automatic tracing
 */
export async function tracedApiCall<T>(
  tracer: trace.Tracer,
  operation: string,
  apiCall: () => Promise<T>
): Promise<T> {
  const span = tracer.startSpan(`github.api.${operation}`);

  try {
    const result = await apiCall();

    span.setAttributes({
      "github.api.success": true,
      "github.api.operation": operation,
    });

    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error: any) {
    span.setAttributes({
      "github.api.success": false,
      "github.api.operation": operation,
      "github.api.status": error.status,
      "github.api.error": error.message,
    });

    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });

    throw error;
  } finally {
    span.end();
  }
}

/**
 * Enhanced webhook handler with detailed API tracing
 */
export function createDetailedTracedWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });
  const tracer = trace.getTracer("github-app-webhooks");

  webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
    const span = tracer.startSpan("webhook.pull_request.opened", {
      attributes: {
        "github.event": "pull_request.opened",
        "github.repository": payload.repository.full_name,
        "github.pr.number": payload.pull_request.number,
        "github.pr.author": payload.pull_request.user.login,
        "github.pr.title": payload.pull_request.title,
        "github.installation.id": payload.installation?.id,
      },
    });

    try {
      // Trace each operation separately
      await context.with(trace.setSpan(context.active(), span), async () => {
        // Add labels with tracing
        const labels = determinePRLabels(payload);
        if (labels.length > 0) {
          await tracedApiCall(tracer, "add_labels", async () => {
            return octokit.issues.addLabels({
              owner: payload.repository.owner.login,
              repo: payload.repository.name,
              issue_number: payload.pull_request.number,
              labels,
            });
          });
        }

        // Assign reviewers with tracing
        const reviewers = await determineReviewers(payload);
        if (reviewers.length > 0) {
          await tracedApiCall(tracer, "request_reviewers", async () => {
            return octokit.pulls.requestReviewers({
              owner: payload.repository.owner.login,
              repo: payload.repository.name,
              pull_number: payload.pull_request.number,
              reviewers,
            });
          });
        }

        // Add welcome comment with tracing
        const isFirstTime = await checkFirstTimeContributor(octokit, payload);
        if (isFirstTime) {
          await tracedApiCall(tracer, "create_welcome_comment", async () => {
            return octokit.issues.createComment({
              owner: payload.repository.owner.login,
              repo: payload.repository.name,
              issue_number: payload.pull_request.number,
              body: "Welcome! Thanks for your first contribution to this project! 🎉",
            });
          });
        }
      });

      span.setAttributes({
        "github.pr.labels_added": labels.length,
        "github.pr.reviewers_assigned": reviewers.length,
        "github.pr.first_time_contributor": isFirstTime,
      });

      span.setStatus({ code: SpanStatusCode.OK });
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
  });

  return webhooks;
}

// =============================================================================
// Performance Monitoring
// =============================================================================

/**
 * Webhook handler with performance monitoring
 */
export function createPerformanceTracedWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });
  const tracer = trace.getTracer("github-app-performance");

  webhooks.on("pull_request", async ({ payload, octokit }) => {
    const startTime = Date.now();
    const span = tracer.startSpan(`webhook.pull_request.${payload.action}`, {
      attributes: {
        "github.event": "pull_request",
        "github.action": payload.action,
        "github.repository": payload.repository.full_name,
        "github.pr.number": payload.pull_request.number,
        "github.installation.id": payload.installation?.id,
      },
    });

    try {
      // Add timing events for different phases
      span.addEvent("Processing started");

      // Phase 1: Validation
      const validationStart = Date.now();
      await validateWebhookPayload(payload);
      span.addEvent("Validation completed", {
        "validation.duration_ms": Date.now() - validationStart,
      });

      // Phase 2: Business logic
      const businessLogicStart = Date.now();
      await processBusinessLogic(payload, octokit);
      span.addEvent("Business logic completed", {
        "business_logic.duration_ms": Date.now() - businessLogicStart,
      });

      // Phase 3: External integrations
      const integrationsStart = Date.now();
      await notifyExternalSystems(payload);
      span.addEvent("External integrations completed", {
        "integrations.duration_ms": Date.now() - integrationsStart,
      });

      const totalDuration = Date.now() - startTime;
      span.setAttributes({
        "webhook.total_duration_ms": totalDuration,
        "webhook.success": true,
      });

      // Alert on slow processing
      if (totalDuration > 5000) {
        span.addEvent("Slow processing detected", {
          "alert.threshold_ms": 5000,
          "alert.actual_ms": totalDuration,
        });
      }

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      const errorDuration = Date.now() - startTime;
      span.setAttributes({
        "webhook.total_duration_ms": errorDuration,
        "webhook.success": false,
        "webhook.error": (error as Error).message,
      });

      span.recordException(error as Error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: (error as Error).message,
      });
      throw error;
    } finally {
      span.end();
    }
  });

  return webhooks;
}

// =============================================================================
// Error Analysis & Debugging
// =============================================================================

/**
 * Webhook handler with comprehensive error tracking
 */
export function createErrorTrackedWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });
  const tracer = trace.getTracer("github-app-errors");

  webhooks.onError((error) => {
    const span = tracer.startSpan("webhook.error", {
      attributes: {
        "error.type": error.name,
        "error.message": error.message,
        "error.stack": error.stack,
      },
    });

    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
    span.end();
  });

  webhooks.on("issue_comment", async ({ payload, octokit }) => {
    const span = tracer.startSpan("webhook.issue_comment.created", {
      attributes: {
        "github.event": "issue_comment",
        "github.action": payload.action,
        "github.repository": payload.repository.full_name,
        "github.issue.number": payload.issue.number,
        "github.comment.author": payload.comment.user.login,
        "github.installation.id": payload.installation?.id,
      },
    });

    try {
      // Add context for debugging
      span.setAttributes({
        "comment.body_length": payload.comment.body.length,
        "comment.is_from_bot": payload.comment.user.type === "Bot",
        "issue.is_pull_request": !!payload.issue.pull_request,
      });

      await processCommentCommand(payload, octokit, span);

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error: any) {
      // Enhanced error context
      span.setAttributes({
        "error.in_phase": getCurrentProcessingPhase(),
        "error.user_input": payload.comment.body.substring(0, 100), // First 100 chars
        "error.permissions_checked": hasCheckedPermissions(),
        "error.api_calls_made": getApiCallCount(),
      });

      span.recordException(error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message,
      });
      throw error;
    } finally {
      span.end();
    }
  });

  return webhooks;
}

// =============================================================================
// Custom Span Extensions
// =============================================================================

/**
 * Extended span with GitHub-specific helpers
 */
export class GitHubSpan {
  constructor(private span: trace.Span) {}

  setGitHubContext(payload: any): void {
    this.span.setAttributes({
      "github.repository": payload.repository?.full_name,
      "github.actor": payload.sender?.login,
      "github.installation.id": payload.installation?.id,
    });
  }

  setPRContext(pr: any): void {
    this.span.setAttributes({
      "github.pr.number": pr.number,
      "github.pr.author": pr.user.login,
      "github.pr.title": pr.title,
      "github.pr.draft": pr.draft,
      "github.pr.mergeable": pr.mergeable,
    });
  }

  setApiCallContext(operation: string, response?: any): void {
    this.span.setAttributes({
      "github.api.operation": operation,
      "github.api.status": response?.status,
      "github.api.headers.ratelimit_remaining": response?.headers["x-ratelimit-remaining"],
    });
  }

  recordBusinessMetric(name: string, value: number | string | boolean): void {
    this.span.setAttributes({
      [`business.${name}`]: value,
    });
  }

  recordPerformanceMetric(phase: string, durationMs: number): void {
    this.span.setAttributes({
      [`perf.${phase}.duration_ms`]: durationMs,
    });
  }
}

/**
 * Create GitHub-specific span wrapper
 */
export function createGitHubSpan(tracer: trace.Tracer, name: string): GitHubSpan {
  const span = tracer.startSpan(name);
  return new GitHubSpan(span);
}

// =============================================================================
// Utility Functions (stubs for examples)
// =============================================================================

async function processPullRequestOpened(payload: any): Promise<void> {
  // Implementation stub
}

function determinePRLabels(payload: any): string[] {
  if (payload.pull_request.title.startsWith("feat")) return ["enhancement"];
  if (payload.pull_request.title.startsWith("fix")) return ["bug"];
  return ["needs-review"];
}

async function determineReviewers(payload: any): Promise<string[]> {
  // Implementation stub - would check CODEOWNERS, team rules, etc.
  return ["team-lead"];
}

async function checkFirstTimeContributor(octokit: Octokit, payload: any): Promise<boolean> {
  // Implementation stub
  return false;
}

async function validateWebhookPayload(payload: any): Promise<void> {
  // Implementation stub
}

async function processBusinessLogic(payload: any, octokit: Octokit): Promise<void> {
  // Implementation stub
}

async function notifyExternalSystems(payload: any): Promise<void> {
  // Implementation stub
}

async function processCommentCommand(payload: any, octokit: Octokit, span: trace.Span): Promise<void> {
  // Implementation stub
}

function getCurrentProcessingPhase(): string {
  return "validation"; // Implementation stub
}

function hasCheckedPermissions(): boolean {
  return true; // Implementation stub
}

function getApiCallCount(): number {
  return 0; // Implementation stub
}
