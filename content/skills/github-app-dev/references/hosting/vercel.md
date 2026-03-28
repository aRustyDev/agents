# Vercel for GitHub Apps

Modern serverless platform with excellent DX. Great for quick deployments and Next.js integration.

## Why Vercel?

| Advantage | Details |
|-----------|---------|
| Instant deployment | Git push to deploy |
| Edge functions | Global distribution |
| Excellent DX | Great CLI and dashboard |
| Preview deployments | Per-PR environments |
| Zero config | Auto-detects frameworks |

## Limitations

- **10s execution limit** (Hobby), 60s (Pro)
- **No WebSocket support** (serverless functions)
- **Limited cron** - Once per day on Hobby
- **Vendor lock-in** - Vercel-specific APIs

## Project Structure

```
my-github-app/
├── api/
│   └── webhook.ts      # API route for webhooks
├── lib/
│   ├── github.ts       # GitHub client
│   └── webhooks.ts     # Webhook handlers
├── vercel.json
├── package.json
└── .env.local
```

## API Route Handler

```typescript
// api/webhook.ts
import type { VercelRequest, VercelResponse } from "@vercel/node";
import { Webhooks } from "@octokit/webhooks";
import { handlePullRequest, handleIssues } from "../lib/webhooks";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

// Register handlers
webhooks.on("pull_request.opened", handlePullRequest);
webhooks.on("issues.opened", handleIssues);

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== "POST") {
    return res.status(405).send("Method Not Allowed");
  }

  const signature = req.headers["x-hub-signature-256"] as string;
  const body =
    typeof req.body === "string" ? req.body : JSON.stringify(req.body);

  try {
    await webhooks.verifyAndReceive({
      id: req.headers["x-github-delivery"] as string,
      name: req.headers["x-github-event"] as any,
      signature,
      payload: body,
    });

    res.status(200).send("OK");
  } catch (error) {
    console.error("Webhook error:", error);
    res.status(401).send("Unauthorized");
  }
}

// Important: Disable body parsing to get raw body for signature verification
export const config = {
  api: {
    bodyParser: false,
  },
};
```

### Raw Body Handling

```typescript
// api/webhook.ts (with raw body)
import type { VercelRequest, VercelResponse } from "@vercel/node";
import { Webhooks } from "@octokit/webhooks";
import getRawBody from "raw-body";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  const rawBody = await getRawBody(req);
  const body = rawBody.toString("utf8");

  const webhooks = new Webhooks({
    secret: process.env.GITHUB_WEBHOOK_SECRET!,
  });

  // ... rest of handler
}
```

## With Next.js App Router

```typescript
// app/api/webhook/route.ts
import { NextRequest, NextResponse } from "next/server";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "@/lib/github";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(payload.installation!.id);

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Thanks for the PR!",
  });
});

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get("x-hub-signature-256") || "";

  try {
    await webhooks.verifyAndReceive({
      id: request.headers.get("x-github-delivery") || "",
      name: request.headers.get("x-github-event") as any,
      signature,
      payload: body,
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Webhook error:", error);
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
}
```

## Authentication

```typescript
// lib/github.ts
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

## Configuration

### vercel.json

```json
{
  "functions": {
    "api/webhook.ts": {
      "maxDuration": 30
    }
  },
  "crons": [
    {
      "path": "/api/cron/daily",
      "schedule": "0 0 * * *"
    }
  ]
}
```

### Environment Variables

```bash
# .env.local (for local development)
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your-secret
```

## Using Vercel KV (Redis)

```typescript
// lib/cache.ts
import { kv } from "@vercel/kv";

export async function cacheInstallationToken(
  installationId: number,
  token: string,
  expiresIn: number
): Promise<void> {
  await kv.set(`token:${installationId}`, token, {
    ex: expiresIn,
  });
}

export async function getCachedToken(
  installationId: number
): Promise<string | null> {
  return kv.get(`token:${installationId}`);
}
```

## Using Vercel Postgres

```typescript
// lib/db.ts
import { sql } from "@vercel/postgres";

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await sql`
    INSERT INTO installations (id, owner, settings, created_at)
    VALUES (${id}, ${owner}, ${JSON.stringify(settings)}, NOW())
    ON CONFLICT (id) DO UPDATE SET
      settings = ${JSON.stringify(settings)}
  `;
}

export async function getInstallation(id: number) {
  const { rows } = await sql`
    SELECT * FROM installations WHERE id = ${id}
  `;
  return rows[0] || null;
}
```

## Cron Jobs

```typescript
// api/cron/daily.ts
import type { VercelRequest, VercelResponse } from "@vercel/node";

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  // Verify cron secret (recommended)
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).send("Unauthorized");
  }

  // Run daily tasks
  console.log("Running daily cron job");

  // Example: Send digest, cleanup, sync
  await sendDailyDigests();
  await cleanupStaleData();

  res.status(200).json({ success: true });
}
```

## Edge Functions

For lower latency, use Edge Functions:

```typescript
// api/webhook-edge.ts
import { Webhooks } from "@octokit/webhooks";

export const config = {
  runtime: "edge",
};

export default async function handler(request: Request) {
  const body = await request.text();
  const signature = request.headers.get("x-hub-signature-256") || "";

  const webhooks = new Webhooks({
    secret: process.env.GITHUB_WEBHOOK_SECRET!,
  });

  // Note: Edge has limited APIs, some npm packages won't work
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

## Local Development

```bash
# Install Vercel CLI
npm i -g vercel

# Link to project
vercel link

# Pull environment variables
vercel env pull

# Start local dev server
vercel dev

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:3000/api/webhook
```

## Deployment

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Set environment variables
vercel env add GITHUB_APP_ID
vercel env add GITHUB_PRIVATE_KEY
vercel env add GITHUB_WEBHOOK_SECRET
```

### GitHub Integration

1. Connect repo in Vercel dashboard
2. Enable automatic deployments
3. Configure environment variables in Vercel settings
4. Preview deployments created for each PR

## Probot on Vercel

```typescript
// api/github/webhooks.ts
import { createNodeMiddleware, createProbot } from "probot";
import app from "../../lib/app";

const probot = createProbot();

export default createNodeMiddleware(app, {
  probot,
  webhooksPath: "/api/github/webhooks",
});
```

```typescript
// lib/app.ts
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

- [ ] Environment variables set in Vercel dashboard
- [ ] Custom domain configured
- [ ] Preview deployments configured
- [ ] Vercel KV/Postgres provisioned if needed
- [ ] Function timeout increased (Pro plan)
- [ ] Rate limiting configured
- [ ] Error tracking (Sentry, etc.)
- [ ] Webhook URL updated in GitHub App

## See Also

- [Hosting Overview](README.md)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
