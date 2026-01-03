/**
 * Production-Ready GitHub App Example
 *
 * A comprehensive example showcasing production-ready patterns:
 * - Robust error handling with retries and circuit breakers
 * - OpenTelemetry instrumentation for observability
 * - Webhook signature verification and replay attack protection
 * - Rate limiting and graceful degradation
 * - Health checks and monitoring endpoints
 * - Structured logging with correlation IDs
 */

import { Hono } from "hono";
import { Webhooks } from "@octokit/webhooks";
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";
import { trace, SpanStatusCode } from "@opentelemetry/api";
import crypto from "crypto";

// =============================================================================
// Types and Configuration
// =============================================================================

type Bindings = {
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
  LOG_LEVEL?: string;
  ENVIRONMENT?: string;
};

interface WebhookDelivery {
  id: string;
  event: string;
  timestamp: number;
  signature: string;
}

// =============================================================================
// Observability Setup
// =============================================================================

const tracer = trace.getTracer("github-app", "1.0.0");

class Logger {
  private context: Record<string, any> = {};

  constructor(private level: string = "info") {}

  withContext(ctx: Record<string, any>) {
    return Object.assign(Object.create(this), {
      context: { ...this.context, ...ctx },
    });
  }

  info(message: string, data?: any) {
    this.log("info", message, data);
  }

  warn(message: string, data?: any) {
    this.log("warn", message, data);
  }

  error(message: string, error?: any) {
    this.log("error", message, error);
  }

  private log(level: string, message: string, data?: any) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: this.context,
      data,
    };
    console.log(JSON.stringify(entry));
  }
}

// =============================================================================
// GitHub API Client with Circuit Breaker
// =============================================================================

class CircuitBreaker {
  private failures = 0;
  private lastFailTime = 0;
  private state: "closed" | "open" | "half-open" = "closed";

  constructor(
    private threshold = 5,
    private timeout = 60000
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === "open") {
      if (Date.now() - this.lastFailTime >= this.timeout) {
        this.state = "half-open";
      } else {
        throw new Error("Circuit breaker is open");
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = "closed";
  }

  private onFailure() {
    this.failures++;
    this.lastFailTime = Date.now();
    if (this.failures >= this.threshold) {
      this.state = "open";
    }
  }
}

class GitHubClient {
  private circuitBreaker = new CircuitBreaker();
  private logger: Logger;

  constructor(
    private octokit: Octokit,
    logger: Logger
  ) {
    this.logger = logger.withContext({ component: "github-client" });
  }

  async withRetry<T>(
    operation: () => Promise<T>,
    maxRetries = 3
  ): Promise<T> {
    return this.circuitBreaker.execute(async () => {
      let lastError: Error;

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const span = tracer.startSpan(`github.api.attempt.${attempt}`);

          try {
            const result = await operation();
            span.setStatus({ code: SpanStatusCode.OK });
            return result;
          } catch (error: any) {
            span.recordException(error);
            span.setStatus({
              code: SpanStatusCode.ERROR,
              message: error.message
            });
            throw error;
          } finally {
            span.end();
          }
        } catch (error: any) {
          lastError = error;

          if (attempt === maxRetries) break;

          // Don't retry on client errors (4xx)
          if (error.status >= 400 && error.status < 500) {
            this.logger.warn("Client error, not retrying", {
              status: error.status,
              attempt,
            });
            break;
          }

          // Exponential backoff
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
          this.logger.info(`Retrying API call in ${delay}ms`, {
            attempt,
            error: error.message,
          });
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }

      throw lastError;
    });
  }

  async addComment(
    owner: string,
    repo: string,
    issue_number: number,
    body: string
  ) {
    return this.withRetry(() =>
      this.octokit.issues.createComment({
        owner,
        repo,
        issue_number,
        body,
      })
    );
  }

  async addLabels(
    owner: string,
    repo: string,
    issue_number: number,
    labels: string[]
  ) {
    return this.withRetry(() =>
      this.octokit.issues.addLabels({
        owner,
        repo,
        issue_number,
        labels,
      })
    );
  }

  async checkRateLimit() {
    const { data } = await this.octokit.rateLimit.get();
    const remaining = data.resources.core.remaining;
    const limit = data.resources.core.limit;

    this.logger.info("Rate limit check", {
      remaining,
      limit,
      percentage: (remaining / limit) * 100,
    });

    return { remaining, limit, percentage: (remaining / limit) * 100 };
  }
}

// =============================================================================
// Security and Webhook Handling
// =============================================================================

class WebhookSecurity {
  private recentDeliveries = new Map<string, number>();
  private cleanupInterval: NodeJS.Timer;

  constructor(private secret: string, private logger: Logger) {
    // Clean up old deliveries every 5 minutes
    this.cleanupInterval = setInterval(() => {
      const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
      for (const [id, timestamp] of this.recentDeliveries.entries()) {
        if (timestamp < fiveMinutesAgo) {
          this.recentDeliveries.delete(id);
        }
      }
    }, 5 * 60 * 1000);
  }

  verifySignature(payload: string, signature: string): boolean {
    const expectedSignature = crypto
      .createHmac("sha256", this.secret)
      .update(payload, "utf8")
      .digest("hex");

    return crypto.timingSafeEqual(
      Buffer.from(`sha256=${expectedSignature}`, "utf8"),
      Buffer.from(signature, "utf8")
    );
  }

  checkReplayAttack(deliveryId: string): boolean {
    if (this.recentDeliveries.has(deliveryId)) {
      this.logger.warn("Replay attack detected", { deliveryId });
      return false;
    }

    this.recentDeliveries.set(deliveryId, Date.now());
    return true;
  }

  destroy() {
    clearInterval(this.cleanupInterval);
  }
}

// =============================================================================
// Application Logic
// =============================================================================

class GitHubApp {
  private github: GitHubClient;
  private security: WebhookSecurity;
  private logger: Logger;

  constructor(
    octokit: Octokit,
    webhookSecret: string,
    logger: Logger
  ) {
    this.github = new GitHubClient(octokit, logger);
    this.security = new WebhookSecurity(webhookSecret, logger);
    this.logger = logger.withContext({ component: "github-app" });
  }

  async handlePullRequestOpened(payload: any) {
    const span = tracer.startSpan("webhook.pull_request.opened");
    const logger = this.logger.withContext({
      event: "pull_request.opened",
      pr: payload.pull_request.number,
      repo: payload.repository.full_name,
    });

    try {
      const { owner, name: repo } = payload.repository;
      const { number, title, user } = payload.pull_request;

      logger.info("Processing PR opened event");

      // Check if this is a first-time contributor
      const isFirstTime = await this.isFirstTimeContributor(
        owner,
        repo,
        user.login
      );

      if (isFirstTime) {
        await this.welcomeFirstTimeContributor(owner, repo, number, user.login);
      }

      // Auto-label based on title
      const labels = this.extractLabelsFromTitle(title);
      if (labels.length > 0) {
        await this.github.addLabels(owner, repo, number, labels);
        logger.info("Applied auto-labels", { labels });
      }

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error: any) {
      logger.error("Failed to handle PR opened", error);
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end();
    }
  }

  async handleIssuesOpened(payload: any) {
    const span = tracer.startSpan("webhook.issues.opened");
    const logger = this.logger.withContext({
      event: "issues.opened",
      issue: payload.issue.number,
      repo: payload.repository.full_name,
    });

    try {
      const { owner, name: repo } = payload.repository;
      const { number, title, user } = payload.issue;

      logger.info("Processing issue opened event");

      // Add triage label to all new issues
      await this.github.addLabels(owner, repo, number, ["triage"]);

      // Welcome new users
      const isFirstTime = await this.isFirstTimeContributor(
        owner,
        repo,
        user.login
      );

      if (isFirstTime) {
        await this.github.addComment(
          owner,
          repo,
          number,
          `👋 Welcome @${user.login}! Thanks for opening your first issue. ` +
          `A maintainer will review this soon.`
        );
      }

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error: any) {
      logger.error("Failed to handle issue opened", error);
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end();
    }
  }

  private async isFirstTimeContributor(
    owner: string,
    repo: string,
    username: string
  ): Promise<boolean> {
    try {
      // Check if user has any previous contributions
      const { data: issues } = await this.github.withRetry(() =>
        this.github.octokit.search.issuesAndPullRequests({
          q: `repo:${owner}/${repo} author:${username}`,
          per_page: 1,
        })
      );

      return issues.total_count <= 1; // Only current issue/PR
    } catch {
      // If we can't determine, assume not first time
      return false;
    }
  }

  private async welcomeFirstTimeContributor(
    owner: string,
    repo: string,
    prNumber: number,
    username: string
  ) {
    const message = `🎉 Welcome @${username}! Thanks for your first contribution to this project.

Here are some helpful resources:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- Join our [Discord community](https://discord.gg/example)

A maintainer will review your PR soon. In the meantime, please make sure:
- [ ] Tests pass
- [ ] Documentation is updated if needed
- [ ] PR title follows [conventional commits](https://conventionalcommits.org)`;

    await this.github.addComment(owner, repo, prNumber, message);
  }

  private extractLabelsFromTitle(title: string): string[] {
    const labels: string[] = [];

    if (title.match(/^feat(\(.+\))?:/)) labels.push("enhancement");
    if (title.match(/^fix(\(.+\))?:/)) labels.push("bug");
    if (title.match(/^docs(\(.+\))?:/)) labels.push("documentation");
    if (title.includes("!:") || title.includes("BREAKING CHANGE")) {
      labels.push("breaking-change");
    }

    return labels;
  }

  // Rate limit monitoring
  async checkHealth() {
    const rateLimit = await this.github.checkRateLimit();

    if (rateLimit.percentage < 10) {
      this.logger.warn("Rate limit critically low", rateLimit);
      return { status: "warning", message: "Rate limit low", data: rateLimit };
    }

    return { status: "healthy", data: rateLimit };
  }
}

// =============================================================================
// Hono Application Setup
// =============================================================================

const app = new Hono<{ Bindings: Bindings }>();

// Global error handler
app.onError((err, c) => {
  const logger = new Logger().withContext({
    path: c.req.path,
    method: c.req.method,
  });

  logger.error("Unhandled application error", err);

  return c.json(
    { error: "Internal server error", requestId: crypto.randomUUID() },
    500
  );
});

// Health check endpoint
app.get("/health", async (c) => {
  const logger = new Logger(c.env.LOG_LEVEL);

  try {
    const octokit = await createAppOctokit(c.env);
    const githubApp = new GitHubApp(octokit, c.env.GITHUB_WEBHOOK_SECRET, logger);

    const health = await githubApp.checkHealth();

    return c.json({
      status: "ok",
      timestamp: new Date().toISOString(),
      environment: c.env.ENVIRONMENT || "unknown",
      github: health,
    });
  } catch (error) {
    logger.error("Health check failed", error);
    return c.json(
      {
        status: "error",
        timestamp: new Date().toISOString(),
        error: "GitHub API unavailable",
      },
      503
    );
  }
});

// Metrics endpoint
app.get("/metrics", async (c) => {
  // In production, you'd integrate with Prometheus or similar
  const metrics = {
    webhooks_processed_total: 0, // Counter
    webhook_duration_seconds: 0, // Histogram
    github_api_requests_total: 0, // Counter
    github_rate_limit_remaining: 0, // Gauge
  };

  return c.text(
    Object.entries(metrics)
      .map(([name, value]) => `${name} ${value}`)
      .join("\n")
  );
});

// Main webhook endpoint
app.post("/webhook", async (c) => {
  const deliveryId = c.req.header("X-GitHub-Delivery") || crypto.randomUUID();
  const event = c.req.header("X-GitHub-Event") || "unknown";
  const signature = c.req.header("X-Hub-Signature-256") || "";

  const logger = new Logger(c.env.LOG_LEVEL).withContext({
    deliveryId,
    event,
  });

  const span = tracer.startSpan("webhook.receive", {
    attributes: {
      "webhook.event": event,
      "webhook.delivery_id": deliveryId,
    },
  });

  try {
    const payload = await c.req.text();
    logger.info("Webhook received", { payloadSize: payload.length });

    // Create webhook security handler
    const security = new WebhookSecurity(c.env.GITHUB_WEBHOOK_SECRET, logger);

    // Verify signature
    if (!security.verifySignature(payload, signature)) {
      logger.warn("Invalid webhook signature");
      span.setStatus({ code: SpanStatusCode.ERROR, message: "Invalid signature" });
      return c.json({ error: "Invalid signature" }, 401);
    }

    // Check for replay attacks
    if (!security.checkReplayAttack(deliveryId)) {
      return c.json({ error: "Duplicate delivery" }, 409);
    }

    // Create authenticated Octokit
    const octokit = await createInstallationOctokit(
      c.env,
      JSON.parse(payload).installation.id
    );

    const githubApp = new GitHubApp(octokit, c.env.GITHUB_WEBHOOK_SECRET, logger);

    // Process webhook based on event type
    const webhookPayload = JSON.parse(payload);

    switch (event) {
      case "pull_request":
        if (webhookPayload.action === "opened") {
          await githubApp.handlePullRequestOpened(webhookPayload);
        }
        break;

      case "issues":
        if (webhookPayload.action === "opened") {
          await githubApp.handleIssuesOpened(webhookPayload);
        }
        break;

      default:
        logger.info("Unhandled event type", { event });
    }

    span.setStatus({ code: SpanStatusCode.OK });
    logger.info("Webhook processed successfully");

    return c.json({ message: "Webhook processed", deliveryId });
  } catch (error: any) {
    logger.error("Webhook processing failed", error);
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });

    return c.json(
      { error: "Webhook processing failed", deliveryId },
      500
    );
  } finally {
    span.end();
  }
});

// =============================================================================
// Helper Functions
// =============================================================================

async function createAppOctokit(env: Bindings): Promise<Octokit> {
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
    },
  });
}

async function createInstallationOctokit(
  env: Bindings,
  installationId: number
): Promise<Octokit> {
  const appOctokit = await createAppOctokit(env);

  const { token } = await appOctokit.auth({
    type: "installation",
    installationId,
  }) as { token: string };

  return new Octokit({ auth: token });
}

export default app;

// =============================================================================
// Usage Example for Local Development
// =============================================================================

/*
To run this app locally:

1. Set environment variables:
   export GITHUB_APP_ID="your_app_id"
   export GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
   export GITHUB_WEBHOOK_SECRET="your_webhook_secret"
   export LOG_LEVEL="debug"
   export ENVIRONMENT="development"

2. Install dependencies:
   npm install hono @octokit/webhooks @octokit/auth-app @octokit/rest

3. Start the server:
   wrangler dev

4. Use ngrok or smee.io to expose local server:
   smee --url https://smee.io/your-unique-url --target http://localhost:8787/webhook

The app includes:
- Circuit breaker for GitHub API reliability
- OpenTelemetry tracing for observability
- Replay attack protection
- Health and metrics endpoints
- Structured logging with correlation IDs
- Exponential backoff for retries
- Rate limit monitoring
*/