# Netlify Functions for GitHub Apps

JAMstack-friendly serverless functions. Great for simple apps with straightforward requirements.

## Why Netlify?

| Advantage | Details |
|-----------|---------|
| Simple deployment | Git push to deploy |
| Edge Functions | Global distribution (Beta) |
| Background Functions | Long-running tasks (up to 15min) |
| Great DX | Excellent CLI and dashboard |
| Preview deploys | Per-branch deployments |

## Limitations

- **10s execution limit** (synchronous), 15min (background)
- **No WebSocket support** in functions
- **Limited customization** compared to containers
- **Vendor-specific** APIs and patterns

## Project Structure

```
my-github-app/
├── netlify/
│   └── functions/
│       ├── webhook.ts
│       └── webhook-background.ts
├── src/
│   ├── github.ts
│   └── handlers.ts
├── netlify.toml
├── package.json
└── .env
```

## Basic Setup

```typescript
// netlify/functions/webhook.ts
import type { Handler, HandlerEvent } from "@netlify/functions";
import { Webhooks } from "@octokit/webhooks";
import { handlePullRequest, handleIssues } from "../../src/handlers";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

webhooks.on("pull_request.opened", handlePullRequest);
webhooks.on("issues.opened", handleIssues);

export const handler: Handler = async (event: HandlerEvent) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const signature = event.headers["x-hub-signature-256"] || "";
  const body = event.body || "";

  try {
    await webhooks.verifyAndReceive({
      id: event.headers["x-github-delivery"] || "",
      name: event.headers["x-github-event"] as any,
      signature,
      payload: body,
    });

    return { statusCode: 200, body: "OK" };
  } catch (error) {
    console.error("Webhook error:", error);
    return { statusCode: 401, body: "Unauthorized" };
  }
};
```

## Background Functions (Long-running)

For operations that exceed 10s, use background functions:

```typescript
// netlify/functions/webhook-background.ts
import type { BackgroundHandler } from "@netlify/functions";
import { analyzeCode, generateReport } from "../../src/analysis";

export const handler: BackgroundHandler = async (event) => {
  const payload = JSON.parse(event.body || "{}");

  console.log("Starting background analysis...");

  // Long-running operations (up to 15 minutes)
  const analysis = await analyzeCode(payload);
  const report = await generateReport(analysis);
  await postComment(payload, report);

  console.log("Background analysis completed");
};
```

Trigger from synchronous function:

```typescript
// netlify/functions/webhook.ts
import fetch from "node-fetch";

export const handler: Handler = async (event) => {
  // ... validate webhook

  // Trigger background function
  const backgroundUrl = `${process.env.URL}/.netlify/functions/webhook-background`;

  await fetch(backgroundUrl, {
    method: "POST",
    body: event.body,
    headers: { "Content-Type": "application/json" },
  });

  return { statusCode: 202, body: "Accepted" };
};
```

## Edge Functions (Low Latency)

```typescript
// netlify/edge-functions/webhook-edge.ts
import { Webhooks } from "@octokit/webhooks";
import type { Context } from "@netlify/edge-functions";

export default async function handler(
  request: Request,
  context: Context
): Promise<Response> {
  const webhooks = new Webhooks({
    secret: Netlify.env.get("GITHUB_WEBHOOK_SECRET")!,
  });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    console.log(`PR #${payload.pull_request.number} opened`);
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

export const config = {
  path: "/webhook-edge",
};
```

## Configuration

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "public"
  functions = "netlify/functions"

[functions]
  node_bundler = "esbuild"
  external_node_modules = ["@octokit/webhooks"]

# Environment variables for specific contexts
[context.production.environment]
  LOG_LEVEL = "info"

[context.deploy-preview.environment]
  LOG_LEVEL = "debug"

# Redirect webhook requests
[[redirects]]
  from = "/api/webhook"
  to = "/.netlify/functions/webhook"
  status = 200
```

## Authentication

```typescript
// src/github.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

export async function createInstallationOctokit(
  installationId: number
): Promise<Octokit> {
  const auth = createAppAuth({
    appId: process.env.GITHUB_APP_ID!,
    privateKey: process.env.GITHUB_PRIVATE_KEY!.replace(/\\n/g, "\n"),
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}
```

## Using Netlify Blobs (Storage)

```typescript
// src/storage.ts
import { getStore } from "@netlify/blobs";

const store = getStore("github-app");

export async function saveInstallation(
  id: number,
  data: Record<string, unknown>
): Promise<void> {
  await store.setJSON(`installation:${id}`, data);
}

export async function getInstallation(
  id: number
): Promise<Record<string, unknown> | null> {
  return store.get(`installation:${id}`, { type: "json" });
}

export async function deleteInstallation(id: number): Promise<void> {
  await store.delete(`installation:${id}`);
}
```

## Scheduled Functions

```typescript
// netlify/functions/daily-task.ts
import type { Handler } from "@netlify/functions";
import { schedule } from "@netlify/functions";

const dailyTask: Handler = async () => {
  console.log("Running daily task");

  await syncInstallations();
  await sendDigests();
  await cleanupOldData();

  return { statusCode: 200, body: "OK" };
};

// Run at midnight UTC every day
export const handler = schedule("0 0 * * *", dailyTask);
```

## Local Development

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Link to site
netlify link

# Start local dev server
netlify dev

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8888/.netlify/functions/webhook
```

### .env (local development)

```bash
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your-secret
```

## Deployment

### Via Git

1. Connect repo in Netlify dashboard
2. Configure build settings
3. Set environment variables
4. Push to deploy

### Via CLI

```bash
# Deploy to preview
netlify deploy

# Deploy to production
netlify deploy --prod

# Set environment variables
netlify env:set GITHUB_APP_ID 123456
netlify env:set GITHUB_PRIVATE_KEY "$(cat private-key.pem)"
netlify env:set GITHUB_WEBHOOK_SECRET your-secret
```

## Using External Databases

### With Supabase

```typescript
// src/db.ts
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!
);

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await supabase.from("installations").upsert({
    id,
    owner,
    settings,
    created_at: new Date().toISOString(),
  });
}

export async function getInstallation(id: number) {
  const { data } = await supabase
    .from("installations")
    .select("*")
    .eq("id", id)
    .single();
  return data;
}
```

### With PlanetScale

```typescript
// src/db.ts
import { connect } from "@planetscale/database";

const conn = connect({
  url: process.env.DATABASE_URL,
});

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await conn.execute(
    `INSERT INTO installations (id, owner, settings)
     VALUES (?, ?, ?)
     ON DUPLICATE KEY UPDATE settings = ?`,
    [id, owner, JSON.stringify(settings), JSON.stringify(settings)]
  );
}
```

## Probot on Netlify

```typescript
// netlify/functions/webhook.ts
import { createProbot, createLambdaFunction } from "probot";
import app from "../../src/app";

const probot = createProbot();

export const handler = createLambdaFunction(app, {
  probot,
});
```

```typescript
// src/app.ts
import { Probot } from "probot";

export default (app: Probot) => {
  app.on("pull_request.opened", async (context) => {
    const comment = context.issue({
      body: "Thanks for the PR!",
    });
    await context.octokit.issues.createComment(comment);
  });
};
```

## Production Checklist

- [ ] Environment variables set in Netlify dashboard
- [ ] Custom domain configured
- [ ] Build command and publish directory set
- [ ] Background functions for long-running tasks
- [ ] Netlify Blobs or external DB configured
- [ ] Scheduled functions for cron tasks
- [ ] Deploy previews enabled
- [ ] Webhook URL updated in GitHub App

## Cost Considerations

| Plan | Functions/month | Background Functions | Edge Functions |
|------|-----------------|---------------------|----------------|
| Free | 125k invocations | No | Limited |
| Pro | 125k + overage | Yes (limited) | Yes |
| Business | Custom | Yes | Yes |

## See Also

- [Hosting Overview](README.md)
- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Netlify Edge Functions](https://docs.netlify.com/edge-functions/overview/)
