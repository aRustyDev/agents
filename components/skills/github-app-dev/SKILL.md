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
