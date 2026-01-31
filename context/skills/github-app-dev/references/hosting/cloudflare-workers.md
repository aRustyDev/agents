# Cloudflare Workers for GitHub Apps

Edge-first serverless platform with zero cold starts. **Recommended for most GitHub Apps.**

## Why Cloudflare Workers?

| Advantage | Details |
|-----------|---------|
| Zero cold starts | Code runs at edge, always warm |
| Global distribution | 300+ locations worldwide |
| Cost effective | Generous free tier (100k req/day) |
| Built-in storage | KV, D1 (SQLite), R2 (S3-compatible) |
| WebSocket support | Via Durable Objects |

## Limitations

- **30s execution limit** (free), 30min (paid)
- **No Node.js APIs** - Web-standard APIs only
- **1MB code size** (free), 10MB (paid)
- **Limited npm compatibility** - Some packages won't work

## Project Setup

```bash
# Create new project
npm create cloudflare@latest my-github-app
# Select "Hello World" TypeScript template

# Or add to existing project
npm install -D wrangler
```

### wrangler.toml

```toml
name = "my-github-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# Environment variables (non-secret)
[vars]
GITHUB_APP_ID = "123456"
LOG_LEVEL = "info"

# KV namespace for caching
[[kv_namespaces]]
binding = "CACHE"
id = "abc123"

# D1 database (optional)
[[d1_databases]]
binding = "DB"
database_name = "github-app-db"
database_id = "def456"

# R2 bucket (optional)
[[r2_buckets]]
binding = "STORAGE"
bucket_name = "github-app-storage"
```

### Environment Types

```typescript
// src/types.ts
export interface Env {
  // Secrets (set via wrangler secret put)
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;

  // KV namespace
  CACHE: KVNamespace;

  // D1 database
  DB: D1Database;

  // R2 bucket
  STORAGE: R2Bucket;
}
```

## Webhook Handler

### Using Hono (Recommended)

```typescript
// src/index.ts
import { Hono } from "hono";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "./auth";
import type { Env } from "./types";

const app = new Hono<{ Bindings: Env }>();

app.post("/webhook", async (c) => {
  const webhooks = new Webhooks({
    secret: c.env.GITHUB_WEBHOOK_SECRET,
  });

  // Register handlers
  webhooks.on("pull_request.opened", async ({ payload }) => {
    const octokit = await createInstallationOctokit(
      c.env,
      payload.installation!.id
    );

    await octokit.issues.createComment({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: payload.pull_request.number,
      body: "Thanks for the PR!",
    });
  });

  // Verify and process
  const signature = c.req.header("x-hub-signature-256") || "";
  const body = await c.req.text();

  try {
    await webhooks.verifyAndReceive({
      id: c.req.header("x-github-delivery") || "",
      name: c.req.header("x-github-event") as any,
      signature,
      payload: body,
    });
    return c.text("OK", 200);
  } catch (error) {
    console.error("Webhook error:", error);
    return c.text("Unauthorized", 401);
  }
});

// Health check
app.get("/health", (c) => c.json({ status: "ok" }));

export default app;
```

### Using Fetch Handler (No Framework)

```typescript
// src/index.ts
import { Webhooks } from "@octokit/webhooks";
import type { Env } from "./types";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/webhook" && request.method === "POST") {
      return handleWebhook(request, env);
    }

    return new Response("Not Found", { status: 404 });
  },
};

async function handleWebhook(request: Request, env: Env): Promise<Response> {
  const webhooks = new Webhooks({ secret: env.GITHUB_WEBHOOK_SECRET });

  webhooks.on("issues.opened", async ({ payload }) => {
    console.log(`Issue #${payload.issue.number} opened`);
  });

  const signature = request.headers.get("x-hub-signature-256") || "";
  const body = await request.text();

  try {
    await webhooks.verifyAndReceive({
      id: request.headers.get("x-github-delivery") || "",
      name: request.headers.get("x-github-event") as any,
      signature,
      payload: body,
    });
    return new Response("OK", { status: 200 });
  } catch {
    return new Response("Unauthorized", { status: 401 });
  }
}
```

## Authentication

```typescript
// src/auth.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";
import type { Env } from "./types";

export async function createInstallationOctokit(
  env: Env,
  installationId: number
): Promise<Octokit> {
  const auth = createAppAuth({
    appId: env.GITHUB_APP_ID,
    privateKey: env.GITHUB_PRIVATE_KEY,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}

// Cache installation tokens in KV
export async function getInstallationOctokit(
  env: Env,
  installationId: number
): Promise<Octokit> {
  const cacheKey = `token:${installationId}`;
  const cached = await env.CACHE.get(cacheKey);

  if (cached) {
    return new Octokit({ auth: cached });
  }

  const auth = createAppAuth({
    appId: env.GITHUB_APP_ID,
    privateKey: env.GITHUB_PRIVATE_KEY,
    installationId,
  });

  const { token, expiresAt } = await auth({ type: "installation" });

  // Cache for 50 minutes (tokens expire in 1 hour)
  await env.CACHE.put(cacheKey, token, {
    expirationTtl: 3000,
  });

  return new Octokit({ auth: token });
}
```

## Using KV for Caching

```typescript
// Cache PR analysis results
async function getCachedAnalysis(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number,
  headSha: string
): Promise<Analysis | null> {
  const key = `analysis:${owner}/${repo}#${prNumber}:${headSha}`;
  const cached = await env.CACHE.get(key, "json");
  return cached as Analysis | null;
}

async function cacheAnalysis(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number,
  headSha: string,
  analysis: Analysis
): Promise<void> {
  const key = `analysis:${owner}/${repo}#${prNumber}:${headSha}`;
  await env.CACHE.put(key, JSON.stringify(analysis), {
    expirationTtl: 86400, // 24 hours
  });
}
```

## Using D1 for Persistent Storage

```typescript
// src/db.ts
import type { Env } from "./types";

interface Installation {
  id: number;
  owner: string;
  repo: string | null;
  settings: string;
  created_at: string;
}

export async function saveInstallation(
  env: Env,
  installation: Omit<Installation, "created_at">
): Promise<void> {
  await env.DB.prepare(
    `INSERT OR REPLACE INTO installations (id, owner, repo, settings, created_at)
     VALUES (?, ?, ?, ?, datetime('now'))`
  )
    .bind(
      installation.id,
      installation.owner,
      installation.repo,
      installation.settings
    )
    .run();
}

export async function getInstallationSettings(
  env: Env,
  installationId: number
): Promise<Record<string, unknown> | null> {
  const result = await env.DB.prepare(
    `SELECT settings FROM installations WHERE id = ?`
  )
    .bind(installationId)
    .first<{ settings: string }>();

  return result ? JSON.parse(result.settings) : null;
}
```

### D1 Schema Migration

```sql
-- migrations/0001_initial.sql
CREATE TABLE IF NOT EXISTS installations (
  id INTEGER PRIMARY KEY,
  owner TEXT NOT NULL,
  repo TEXT,
  settings TEXT DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE INDEX idx_installations_owner ON installations(owner);
```

```bash
# Apply migrations
wrangler d1 migrations apply github-app-db
```

## Scheduled Tasks (Cron)

```toml
# wrangler.toml
[triggers]
crons = ["0 */6 * * *"]  # Every 6 hours
```

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // ... webhook handling
  },

  async scheduled(
    controller: ScheduledController,
    env: Env,
    ctx: ExecutionContext
  ): Promise<void> {
    console.log("Running scheduled task:", controller.cron);

    // Example: Clean up stale cache entries
    // Example: Send daily digest
    // Example: Sync installation data
  },
};
```

## Local Development

```bash
# Create .dev.vars for local secrets
cat > .dev.vars << 'EOF'
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your-secret
EOF

# Start local dev server
wrangler dev

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8787/webhook
```

## Deployment

```bash
# Set secrets
wrangler secret put GITHUB_APP_ID
wrangler secret put GITHUB_PRIVATE_KEY
wrangler secret put GITHUB_WEBHOOK_SECRET

# Deploy
wrangler deploy

# Deploy to specific environment
wrangler deploy --env production
```

### Environment-Specific Config

```toml
# wrangler.toml
[env.production]
name = "my-github-app-prod"
vars = { LOG_LEVEL = "warn" }

[env.staging]
name = "my-github-app-staging"
vars = { LOG_LEVEL = "debug" }
```

## Testing

```typescript
// test/webhook.test.ts
import { unstable_dev } from "wrangler";
import { describe, it, expect, beforeAll, afterAll } from "vitest";

describe("Webhook Handler", () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    worker = await unstable_dev("src/index.ts", {
      experimental: { disableExperimentalWarning: true },
    });
  });

  afterAll(async () => {
    await worker.stop();
  });

  it("returns 401 for invalid signature", async () => {
    const response = await worker.fetch("/webhook", {
      method: "POST",
      headers: {
        "x-github-event": "ping",
        "x-github-delivery": "test-id",
        "x-hub-signature-256": "invalid",
      },
      body: "{}",
    });
    expect(response.status).toBe(401);
  });
});
```

## Production Checklist

- [ ] Secrets configured via `wrangler secret put`
- [ ] Custom domain configured
- [ ] Rate limiting enabled (via WAF or custom logic)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Logging enabled
- [ ] Cron triggers tested
- [ ] D1/KV namespaces created for production
- [ ] Webhook URL updated in GitHub App settings

## See Also

- [Cloudflare Workers Skill](../../../../cloudflare-workers/SKILL.md) - Detailed CF Workers patterns
- [Hosting Overview](README.md)
