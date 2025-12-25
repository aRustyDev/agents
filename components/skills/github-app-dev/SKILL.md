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
| Account | email, profile | User-facing features |

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

**When to use Probot:**
- Simple bots with straightforward logic
- Quick prototypes
- When you don't need custom hosting

**When to use raw Octokit:**
- Complex apps with custom requirements
- Cloudflare Workers deployment
- Fine-grained control over auth and routing

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

| Event | When Fired |
|-------|------------|
| `pull_request.opened` | PR created |
| `pull_request.synchronize` | New commits pushed |
| `pull_request.closed` | PR merged or closed |
| `pull_request_review.submitted` | Review submitted |
| `issues.opened` | Issue created |
| `issue_comment.created` | Comment added |
| `check_run.completed` | CI check finished |

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

### "Bad credentials" error

- Check private key format (must be PEM)
- Verify APP_ID matches your app
- Ensure installation token is not expired (1 hour limit)

### Webhook not received

- Check webhook URL is accessible
- Verify webhook secret matches
- Check event subscriptions in app settings
- Use smee.io for local development

### Permission denied

- Verify app has required permissions
- Check installation is on correct repo
- Ensure permission was added before installation

## See Also

- [references/webhooks.md](references/webhooks.md) - Complete webhook event reference
- [references/permissions.md](references/permissions.md) - Permission matrix
- [references/octokit.md](references/octokit.md) - Octokit SDK patterns
- `cloudflare-workers` skill - Detailed CF Workers patterns
- `github-actions` skill - Building custom Actions (different from Apps)

## External Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Octokit.js](https://github.com/octokit/octokit.js)
- [Probot](https://probot.github.io/)
- [GitHub Webhooks](https://docs.github.com/en/webhooks)
