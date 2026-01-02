---
name: github-app-dev
description: GitHub App development guide for building custom integrations. Use this skill when creating a GitHub App, building webhook handlers, implementing GitHub API integrations, developing PR/Issue automation apps, or deploying GitHub Apps to Cloudflare Workers.
---

# GitHub App Development

Build custom GitHub Apps for automation, integrations, and workflow management.

## Overview

GitHub Apps are first-class integrations that act on their own behalf (unlike OAuth apps which act as users). They receive granular permissions, subscribe to webhooks, and can be installed on specific repositories.

**This skill covers:**
- App registration and configuration
- Authentication (JWT, installation tokens, user tokens)
- Webhook handling and event processing
- Octokit SDK usage
- Probot framework (simplified development)
- Deployment options (Cloudflare Workers preferred)

**This skill does NOT cover:**
- GitHub Actions workflow YAML (see `github-actions-ci` skill)
- Developing custom GitHub Actions (see `github-actions` skill)
- OAuth apps for "Sign in with GitHub"
- Installing/configuring existing apps

## Quick Reference

### App Types

| Type | Acts As | Use Case |
|------|---------|----------|
| GitHub App | Itself or user | Automation, integrations, bots |
| OAuth App | User only | "Sign in with GitHub", user-facing tools |

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub App Auth Flow                      │
├─────────────────────────────────────────────────────────────┤
│  1. Generate JWT (signed with private key)                  │
│     └─► Authenticates the App itself                        │
│                                                             │
│  2. Exchange JWT for Installation Token                     │
│     └─► Scoped to specific installation                     │
│     └─► Used for API calls                                  │
│                                                             │
│  3. (Optional) User Access Token                            │
│     └─► OAuth flow for user-delegated actions               │
└─────────────────────────────────────────────────────────────┘
```

### Permission Categories

| Category | Examples | When to Use |
|----------|----------|-------------|
| Repository | contents, pull_requests, issues | Most apps |
| Organization | members, teams | Org-level automation |

See [references/permissions.md](references/permissions.md) for complete permission matrix.

## Decision Tree: Framework Selection

Choose the right approach based on your requirements:

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub App Framework Selection              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Need simple webhook handling? ────► YES ──► Use Probot     │
│         │                                    - Faster dev  │
│         │                                    - Less setup  │
│         │                                    - Good docs   │
│         │                                                  │
│         NO                                                  │
│         │                                                  │
│         ▼                                                  │
│  Need custom deployment? ──────► YES ──► Raw Octokit       │
│         │                                    - Full control│
│         │                                    - CF Workers  │
│         │                                    - Custom auth │
│         │                                                  │
│         NO                                                  │
│         │                                                  │
│         ▼                                                  │
│  Start with Probot, migrate later if needed                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Framework Comparison

| Criterion | Probot | Raw Octokit | Recommendation |
|-----------|--------|-------------|---------------|
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Start with Probot |
| **Deployment Flexibility** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Complex hosting = Octokit |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Begin with Probot |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | High-traffic = Octokit |
| **Cloudflare Workers** | ❌ | ✅ | Edge deployment = Octokit |

## Error Handling & Rate Limiting

### Essential Error Patterns

```typescript
// Basic error handling with retries
async function safeGitHubCall<T>(call: () => Promise<T>): Promise<T | null> {
  try {
    return await call();
  } catch (error: any) {
    // Handle rate limits
    if (error.status === 403 && error.response?.headers['x-ratelimit-remaining'] === '0') {
      const resetTime = parseInt(error.response.headers['x-ratelimit-reset']) * 1000;
      const waitTime = resetTime - Date.now();
      if (waitTime > 0 && waitTime < 60000) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
        return call(); // Retry once
      }
    }

    // Log error and return null for graceful degradation
    console.error('GitHub API call failed:', error.message);
    return null;
  }
}
```

See [references/error-handling.md](references/error-handling.md) for comprehensive error handling patterns including circuit breakers, adaptive throttling, and monitoring.

**Key error handling:**
- **403 (Rate Limited)**: Wait for reset time
- **5xx (Server Errors)**: Retry with backoff
- **401/403**: Check credentials/permissions
- **400/404**: Fix request or verify resource exists

### Rate Limit Management

Monitor and respect GitHub's rate limits:

```typescript
// Basic rate limit check
const { data } = await octokit.rateLimit.get();
console.log(`Rate limit: ${data.resources.core.remaining}/${data.resources.core.limit}`);

if (data.resources.core.remaining < 100) {
  console.warn('⚠️ Approaching rate limit');
}
```

See [references/error-handling.md](references/error-handling.md) for advanced rate limit management patterns.

## OpenTelemetry Integration

Add distributed tracing to your GitHub App for better observability and debugging.

### Setup OpenTelemetry

```typescript
// src/tracing.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-otlp-http";

export function initializeTracing() {
  const traceExporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318/v1/traces",
  });

  const sdk = new NodeSDK({
    traceExporter,
    instrumentations: [getNodeAutoInstrumentations()],
  });

  sdk.start();
  console.log("OpenTelemetry tracing initialized");
}
```

### Common GitHub App Traces

```typescript
// src/webhooks.ts with tracing
import { trace, context, SpanStatusCode } from "@opentelemetry/api";
import { Webhooks } from "@octokit/webhooks";

const tracer = trace.getTracer("github-app");

export function createWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    const span = tracer.startSpan("webhook.pull_request.opened", {
      attributes: {
        "github.event": "pull_request.opened",
        "github.repository": payload.repository.full_name,
        "github.pr.number": payload.pull_request.number,
        "github.pr.author": payload.pull_request.user.login,
      },
    });

    try {
      // Your webhook logic here
      console.log(`Processing PR #${payload.pull_request.number}`);

      // Example: Add trace for API calls
      await context.with(trace.setSpan(context.active(), span), async () => {
        const apiSpan = tracer.startSpan("github.api.add_labels");
        try {
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 100));
          apiSpan.setStatus({ code: SpanStatusCode.OK });
        } catch (error) {
          apiSpan.recordException(error as Error);
          apiSpan.setStatus({ code: SpanStatusCode.ERROR });
          throw error;
        } finally {
          apiSpan.end();
        }
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
```

### Trace Trigger Configuration

Set up a constant trace trigger for testing and debugging:

```typescript
// src/tracing-trigger.ts
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("github-app-trigger");

// Triggered trace for debugging - can be called via webhook or timer
export async function triggerTestTrace() {
  const span = tracer.startSpan("debug.test_trace", {
    attributes: {
      "test.trigger": "manual",
      "test.timestamp": Date.now(),
    },
  });

  try {
    // Simulate some work
    span.addEvent("Starting test operations");

    await new Promise(resolve => setTimeout(resolve, 200));
    span.addEvent("Simulated API call completed");

    await new Promise(resolve => setTimeout(resolve, 100));
    span.addEvent("Simulated database operation completed");

    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.recordException(error as Error);
    span.setStatus({ code: SpanStatusCode.ERROR });
  } finally {
    span.end();
  }
}

// Add to your webhook handler or create a separate endpoint
// app.post("/debug/trace", async (c) => {
//   await triggerTestTrace();
//   return c.json({ message: "Test trace triggered" });
// });
```

### Environment Configuration

```bash
# .env or Cloudflare Workers secrets
OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io/v1/traces"
OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=YOUR_API_KEY"
OTEL_SERVICE_NAME="my-github-app"
OTEL_SERVICE_VERSION="1.0.0"
```

For Cloudflare Workers, adapt the tracing setup:

```typescript
// For Cloudflare Workers - simplified tracing
import { trace, context } from "@opentelemetry/api";

// Note: Full OpenTelemetry SDK may not work in Workers
// Use fetch-based custom exporter or compatible service
export class SimpleTraceExporter {
  async export(endpoint: string, headers: Record<string, string>, spans: any[]) {
    await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: JSON.stringify(spans),
    });
  }
}
```

## Workflow: Create a New GitHub App

### Step 1: Register the App

1. Go to **Settings → Developer settings → GitHub Apps → New GitHub App**
2. Configure:
   - **Name**: Unique identifier (e.g., `myorg-pr-bot`)
   - **Homepage URL**: Your app's landing page
   - **Webhook URL**: Where GitHub sends events (use smee.io for local dev)
   - **Webhook Secret**: Random string for signature verification
   - **Permissions**: Request minimum necessary
   - **Events**: Subscribe only to needed webhooks

3. After creation:
   - Note the **App ID**
   - Generate and download **Private Key** (.pem file)
   - Note the **Client ID** and **Client Secret** (if using OAuth)

### GitHub App Configuration Settings

After creating your app, you can configure these settings in **Settings → Developer settings → GitHub Apps → [Your App]**:

#### Basic Information
- **Display Name**: Public name shown to users during installation
- **Description**: What your app does (shown in marketplace and installation)
- **Homepage URL**: Link to your app's documentation or website
- **User Authorization Callback URL**: OAuth redirect URL (if using user tokens)
- **Setup URL**: Optional post-installation configuration page
- **Webhook URL**: Endpoint for receiving events
- **Webhook Secret**: Secret for verifying webhook authenticity

#### Installation Settings
- **Public**: Anyone can install your app
- **Only on this account**: Restrict to your personal/organization account
- **Request user authorization (OAuth) during installation**: Enable OAuth flow
- **Expire user authorization tokens**: Automatically expire user tokens
- **Refresh user authorization tokens**: Allow token refresh
- **Device flow enabled**: Support device authorization flow
- **Post installation URL**: Redirect users after installation

#### Marketplace Settings (for public apps)
- **Primary Category**: App category for discovery
- **Listed in GitHub Marketplace**: Make app discoverable
- **Pricing**: Free, flat rate, or per-unit pricing
- **Screenshots**: Up to 5 images showing your app

#### Advanced Settings
- **Transfer ownership**: Move app to different account
- **Danger Zone**: Delete app or make private

#### Example Configuration for PR Bot

```yaml
# Recommended settings for a typical PR automation bot
Display Name: "PR Assistant Bot"
Description: "Automated PR labeling, reviewer assignment, and code quality checks"
Homepage URL: "https://mycompany.com/pr-assistant"
User Authorization Callback URL: "https://mycompany.com/auth/callback"
Setup URL: "https://mycompany.com/setup"
Webhook URL: "https://api.mycompany.com/webhooks/github"

Installation:
  - Public: true (if sharing with community)
  - Request OAuth: false (unless need user-specific actions)
  - Post installation URL: "https://mycompany.com/setup/complete"

Permissions:
  Repository:
    - Contents: Read (for file analysis)
    - Issues: Write (for labeling)
    - Pull requests: Write (for reviews/comments)
    - Metadata: Read (for repository info)

  Organization:
    - Members: Read (for reviewer assignment)

Events:
  - Pull request
  - Pull request review
  - Issue comment
```

### Step 2: Set Up Development Environment

Create project structure:

```
my-github-app/
├── src/
│   ├── index.ts          # Entry point
│   ├── webhooks.ts       # Webhook handlers
│   ├── github.ts         # GitHub API client
│   └── auth.ts           # Authentication helpers
├── wrangler.toml         # Cloudflare Workers config
├── package.json
└── .dev.vars             # Local secrets (gitignored)
```

Install dependencies:

```bash
npm install @octokit/rest @octokit/auth-app @octokit/webhooks
npm install -D wrangler typescript @types/node
```

### Step 3: Implement Authentication

```typescript
// src/auth.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

export function createAppOctokit(env: Env): Octokit {
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
    },
  });
}

export async function createInstallationOctokit(
  env: Env,
  installationId: number
): Promise<Octokit> {
  const appOctokit = createAppOctokit(env);

  const { token } = await appOctokit.auth({
    type: "installation",
    installationId,
  }) as { token: string };

  return new Octokit({ auth: token });
}
```

### Step 4: Handle Webhooks

```typescript
// src/webhooks.ts
import { Webhooks } from "@octokit/webhooks";

export function createWebhooks(secret: string): Webhooks {
  const webhooks = new Webhooks({ secret });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    console.log(`PR #${payload.pull_request.number} opened`);
    // Handle event...
  });

  webhooks.on("issues.opened", async ({ payload }) => {
    console.log(`Issue #${payload.issue.number} opened`);
    // Handle event...
  });

  return webhooks;
}
```

### Step 5: Create Entry Point

```typescript
// src/index.ts (Cloudflare Workers)
import { Hono } from "hono";
import { createWebhooks } from "./webhooks";
import { createInstallationOctokit } from "./auth";

type Bindings = {
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.post("/webhook", async (c) => {
  const webhooks = createWebhooks(c.env.GITHUB_WEBHOOK_SECRET);

  const signature = c.req.header("x-hub-signature-256") || "";
  const body = await c.req.text();

  try {
    await webhooks.verifyAndReceive({
      id: c.req.header("x-github-delivery") || "",
      name: c.req.header("x-github-event") as any,
      signature,
      payload: body,
    });
    return c.text("OK");
  } catch (error) {
    return c.text("Unauthorized", 401);
  }
});

export default app;
```

### Step 6: Deploy

**Local Development:**

```bash
# Start smee.io proxy
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8787/webhook

# Start worker
wrangler dev
```

**Production (Cloudflare Workers):**

```bash
# Set secrets
wrangler secret put GITHUB_APP_ID
wrangler secret put GITHUB_PRIVATE_KEY
wrangler secret put GITHUB_WEBHOOK_SECRET

# Deploy
wrangler deploy
```

Update the app's webhook URL to your worker URL.

## Probot Framework

For simpler apps, Probot handles auth and webhook routing automatically.

```typescript
// app.ts
import { Probot } from "probot";

export default (app: Probot) => {
  app.on("pull_request.opened", async (context) => {
    const comment = context.issue({
      body: "Thanks for the PR!",
    });
    await context.octokit.issues.createComment(comment);
  });

  app.on("issues.opened", async (context) => {
    const label = context.issue({
      labels: ["triage"],
    });
    await context.octokit.issues.addLabels(label);
  });
};
```

**Use Probot for:** Simple bots, prototypes, standard hosting
**Use raw Octokit for:** Complex apps, Cloudflare Workers, custom control

## Hosting Options

| Platform | Pros | Cons |
|----------|------|------|
| **Cloudflare Workers** | Edge deployment, cheap, fast | Limited runtime APIs |
| **Vercel/Netlify** | Easy deployment, serverless | Cold starts |
| **AWS Lambda** | Flexible, scalable | More setup |
| **Self-hosted** | Full control | Maintenance overhead |

### Cloudflare Workers (Preferred)

See `cloudflare-workers` skill for detailed patterns.

```toml
# wrangler.toml
name = "my-github-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
GITHUB_APP_ID = "123456"
```

## Common Patterns

### Repository Custom Properties for Configuration

Use repository or organization custom properties to apply different logic based on repository metadata:

```typescript
// Check repository custom properties for configuration
async function getRepoConfig(octokit: Octokit, owner: string, repo: string) {
  try {
    const { data: repoProperties } = await octokit.request(
      "GET /repos/{owner}/{repo}/custom-properties",
      { owner, repo }
    );

    return repoProperties.reduce((config, prop) => {
      config[prop.property_name] = prop.value;
      return config;
    }, {} as Record<string, string>);
  } catch (error) {
    // Fallback if custom properties not available
    return {};
  }
}

// Apply language-specific logic based on custom properties
webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
  const config = await getRepoConfig(
    octokit,
    payload.repository.owner.login,
    payload.repository.name
  );

  const language = config.language || "unknown";
  const labels: string[] = [];

  // Apply language-specific configuration
  switch (language) {
    case "rust":
      labels.push("rust", "performance-critical");
      // Require clippy checks
      await octokit.checks.create({
        owner: payload.repository.owner.login,
        repo: payload.repository.name,
        head_sha: payload.pull_request.head.sha,
        name: "Rust Clippy Required",
        status: "queued",
        output: {
          title: "Clippy check required for Rust projects",
          summary: "Please ensure clippy passes before merging",
        },
      });
      break;

    case "javascript":
      labels.push("javascript", "needs-testing");
      // Require Jest tests
      break;

    case "python":
      labels.push("python", "type-checking");
      // Require mypy validation
      break;

    default:
      labels.push("needs-review");
  }

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: payload.pull_request.number,
      labels,
    });
  }
});
```

### Auto-label PRs

```typescript
webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
  const { title, number } = payload.pull_request;
  const labels: string[] = [];

  if (title.startsWith("feat")) labels.push("enhancement");
  if (title.startsWith("fix")) labels.push("bug");
  if (title.startsWith("docs")) labels.push("documentation");

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: number,
      labels,
    });
  }
});
```

### Auto-assign Reviewers

```typescript
webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
  const reviewers = getReviewersForPath(payload.pull_request.changed_files);

  await octokit.pulls.requestReviewers({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    pull_number: payload.pull_request.number,
    reviewers,
  });
});
```

### Enforce PR Checks

```typescript
webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
  // Validate title format
  const valid = /^(feat|fix|docs|chore)(\(.+\))?: .+/.test(
    payload.pull_request.title
  );

  await octokit.checks.create({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    head_sha: payload.pull_request.head.sha,
    name: "Title Validation",
    status: "completed",
    conclusion: valid ? "success" : "failure",
    output: {
      title: valid ? "Title is valid" : "Title format invalid",
      summary: valid
        ? "PR title follows conventional commit format"
        : "Expected: feat|fix|docs|chore(scope): description",
    },
  });
});
```

## API Reference

### Webhook Events

**Common events:** `pull_request.opened`, `issues.opened`, `issue_comment.created`, `check_run.completed`

See [references/webhooks.md](references/webhooks.md) for complete event reference.

### Octokit Methods

```typescript
// Pull Requests
octokit.pulls.get({ owner, repo, pull_number });
octokit.pulls.listFiles({ owner, repo, pull_number });
octokit.pulls.createReview({ owner, repo, pull_number, event, body });
octokit.pulls.merge({ owner, repo, pull_number, merge_method });

// Issues
octokit.issues.createComment({ owner, repo, issue_number, body });
octokit.issues.addLabels({ owner, repo, issue_number, labels });

// Checks
octokit.checks.create({ owner, repo, head_sha, name, status, conclusion });
octokit.checks.update({ owner, repo, check_run_id, status, conclusion });

// Contents
octokit.repos.getContent({ owner, repo, path, ref });
```

## Security Checklist

- [ ] Verify webhook signatures before processing
- [ ] Request minimum necessary permissions
- [ ] Store private key securely (secrets manager)
- [ ] Never log tokens or private keys
- [ ] Rate limit incoming requests
- [ ] Validate all input from payloads
- [ ] Use HTTPS for all communication

## Troubleshooting

**Common issues:**
- **Bad credentials**: Check private key format (PEM), APP_ID, token expiry
- **Webhook not received**: Verify URL accessibility, secret, event subscriptions
- **Permission denied**: Check app permissions, installation scope

See [references/error-handling.md](references/error-handling.md) for detailed troubleshooting.

## Documentation Strategy

Different contexts require different types of documentation for your GitHub App. Plan your documentation approach based on your audience and distribution method.

### Documentation Types

#### 1. Marketplace Listing Documentation
**Purpose**: Help users discover and understand your app's value proposition
**Audience**: Potential users browsing the GitHub Marketplace
**Content Focus**:
- Clear value proposition and use cases
- Feature highlights with screenshots
- Installation and setup instructions
- Pricing and support information

```markdown
# Example: PR Assistant Bot - Marketplace Description

## Automate Your Pull Request Workflow

Save hours of manual work with intelligent PR labeling, automated reviewer
assignment, and code quality checks.

### Key Features
- 🏷️ **Smart Labeling**: Automatically label PRs based on files changed
- 👥 **Reviewer Assignment**: Route PRs to the right team members
- ✅ **Quality Gates**: Enforce coding standards and best practices
- 📊 **Analytics**: Track PR metrics and team performance

### Setup in 2 Minutes
1. Install the app from the marketplace
2. Configure your team settings
3. Watch the automation begin!

**Pricing**: Free for public repos, $5/month per private repo
```

#### 2. Code Comments and Documentation
**Purpose**: Help developers understand, maintain, and extend your app
**Audience**: Your development team and contributors
**Content Focus**:
- API documentation and type definitions
- Architectural decisions and trade-offs
- Code comments for complex business logic
- Development setup and testing procedures

```typescript
/**
 * Assigns reviewers to a pull request based on CODEOWNERS file
 * and team availability from GitHub's REST API.
 *
 * @param octokit - Authenticated GitHub client
 * @param payload - Pull request webhook payload
 * @param maxReviewers - Maximum number of reviewers to assign (default: 3)
 *
 * @returns Promise<string[]> - Array of assigned reviewer usernames
 *
 * @example
 * ```typescript
 * const reviewers = await assignReviewers(octokit, prPayload, 2);
 * console.log(`Assigned reviewers: ${reviewers.join(', ')}`);
 * ```
 */
async function assignReviewers(
  octokit: Octokit,
  payload: PullRequestEvent,
  maxReviewers = 3
): Promise<string[]> {
  // Implementation details...
}
```

#### 3. Installation Configuration Pages
**Purpose**: Guide users through app setup and customization
**Audience**: Users who have installed your app
**Content Focus**:
- Step-by-step configuration instructions
- Interactive setup forms and validation
- Troubleshooting common issues
- Feature toggles and customization options

```html
<!-- Example: Post-Installation Setup Page -->
<!DOCTYPE html>
<html>
<head>
  <title>PR Assistant Setup</title>
</head>
<body>
  <h1>Welcome to PR Assistant!</h1>

  <div class="setup-wizard">
    <h2>Step 1: Configure Team Settings</h2>
    <p>Choose which teams should be notified for different types of PRs:</p>

    <form id="team-config">
      <label>
        Frontend Changes (*.tsx, *.css):
        <select name="frontend-team">
          <option value="">Select team...</option>
          <option value="frontend">Frontend Team</option>
          <option value="design">Design Team</option>
        </select>
      </label>

      <label>
        Backend Changes (*.py, *.go):
        <select name="backend-team">
          <option value="">Select team...</option>
          <option value="backend">Backend Team</option>
          <option value="platform">Platform Team</option>
        </select>
      </label>

      <button type="submit">Save Configuration</button>
    </form>
  </div>

  <div class="help-section">
    <h3>Need Help?</h3>
    <ul>
      <li><a href="/docs/troubleshooting">Troubleshooting Guide</a></li>
      <li><a href="mailto:support@example.com">Contact Support</a></li>
    </ul>
  </div>
</body>
</html>
```

### Documentation Best Practices

#### For Marketplace Listings
- **Lead with benefits**, not features
- Use **screenshots and GIFs** to demonstrate functionality
- Include **clear pricing** information
- Provide **support contact** information
- Test your description with potential users

#### For Code Documentation
- Document **why**, not just what
- Include **runnable examples** in comments
- Use **TypeScript types** for API clarity
- Document **error conditions** and recovery strategies
- Keep documentation **close to code** (avoid separate wikis)

#### For Installation Pages
- Use **progressive disclosure** (show complexity gradually)
- Provide **sensible defaults** for all settings
- Include **validation feedback** on forms
- Offer **quick start** and **advanced** configuration paths
- Test with users unfamiliar with your app

### Documentation Maintenance

```typescript
// Example: Automated documentation checks
export const docChecks = {
  // Ensure all public methods have JSDoc comments
  validateJSDoc: true,

  // Check that README examples still work
  validateExamples: true,

  // Ensure setup URLs are still accessible
  validateLinks: true,

  // Check that marketplace description matches current features
  validateFeatureSync: true,
};
```

#### Common Documentation Anti-patterns
- **Outdated screenshots** showing old UI
- **Broken links** to setup or support resources
- **Missing error messages** in troubleshooting guides
- **Developer jargon** in user-facing documentation
- **Installation steps** that only work on specific systems

## See Also

- [examples/README.md](examples/README.md) - Complete starter projects and runnable code samples
- [references/testing.md](references/testing.md) - Comprehensive testing strategies and patterns
- [references/error-handling.md](references/error-handling.md) - Advanced error handling and rate limit management
- [references/webhooks.md](references/webhooks.md) - Complete webhook event reference
- [references/permissions.md](references/permissions.md) - Permission matrix and runtime validation
- [references/octokit.md](references/octokit.md) - Octokit SDK patterns
- `cloudflare-workers` skill - Detailed CF Workers patterns
- `github-actions` skill - Building custom Actions (different from Apps)

## External Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Octokit.js](https://github.com/octokit/octokit.js)
- [Probot](https://probot.github.io/)
- [GitHub Webhooks](https://docs.github.com/en/webhooks)
