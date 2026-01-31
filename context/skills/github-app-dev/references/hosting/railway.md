# Railway for GitHub Apps

Container-based platform with simple deployment. Always-on instances with no cold starts.

## Why Railway?

| Advantage | Details |
|-----------|---------|
| No cold starts | Containers always running |
| Simple deployment | Git push or Docker |
| Built-in databases | PostgreSQL, MySQL, Redis, MongoDB |
| WebSocket support | Full duplex connections |
| Preview environments | Per-PR deployments |

## Limitations

- **Cost** - Pay per minute of compute
- **No edge deployment** - Single region
- **Resource limits** - Memory/CPU caps per plan
- **Sleep on inactivity** (free tier) - Requires paid for always-on

## Project Structure

```
my-github-app/
├── src/
│   ├── index.ts        # Entry point
│   ├── webhooks.ts     # Webhook handlers
│   └── github.ts       # GitHub client
├── Dockerfile          # Optional
├── railway.json        # Railway config
├── package.json
└── .env
```

## Basic Setup

```typescript
// src/index.ts
import express from "express";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "./github";

const app = express();
const port = process.env.PORT || 3000;

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

// Register handlers
webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(payload.installation!.id);

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Thanks for the PR!",
  });
});

// Webhook endpoint
app.post(
  "/webhook",
  express.raw({ type: "application/json" }),
  async (req, res) => {
    const signature = req.headers["x-hub-signature-256"] as string;
    const body = req.body.toString();

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
);

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

## Using Hono (Lightweight Alternative)

```typescript
// src/index.ts
import { Hono } from "hono";
import { serve } from "@hono/node-server";
import { Webhooks } from "@octokit/webhooks";

const app = new Hono();

app.post("/webhook", async (c) => {
  const webhooks = new Webhooks({
    secret: process.env.GITHUB_WEBHOOK_SECRET!,
  });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    console.log(`PR #${payload.pull_request.number} opened`);
  });

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
  } catch {
    return c.text("Unauthorized", 401);
  }
});

serve({ fetch: app.fetch, port: Number(process.env.PORT) || 3000 });
```

## Configuration

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm start",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### package.json

```json
{
  "name": "my-github-app",
  "scripts": {
    "start": "node dist/index.js",
    "build": "tsc",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "@octokit/auth-app": "^6.0.0",
    "@octokit/rest": "^20.0.0",
    "@octokit/webhooks": "^12.0.0",
    "express": "^4.18.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0"
  }
}
```

## Using Railway PostgreSQL

```typescript
// src/db.ts
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await pool.query(
    `INSERT INTO installations (id, owner, settings, created_at)
     VALUES ($1, $2, $3, NOW())
     ON CONFLICT (id) DO UPDATE SET settings = $3`,
    [id, owner, JSON.stringify(settings)]
  );
}

export async function getInstallation(id: number) {
  const result = await pool.query(
    "SELECT * FROM installations WHERE id = $1",
    [id]
  );
  return result.rows[0] || null;
}
```

### Database Migration

```sql
-- migrations/001_initial.sql
CREATE TABLE IF NOT EXISTS installations (
  id INTEGER PRIMARY KEY,
  owner TEXT NOT NULL,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_installations_owner ON installations(owner);
```

## Using Railway Redis

```typescript
// src/cache.ts
import { createClient } from "redis";

const redis = createClient({
  url: process.env.REDIS_URL,
});

redis.connect();

export async function cacheToken(
  installationId: number,
  token: string,
  ttl: number
): Promise<void> {
  await redis.setEx(`token:${installationId}`, ttl, token);
}

export async function getCachedToken(
  installationId: number
): Promise<string | null> {
  return redis.get(`token:${installationId}`);
}
```

## Dockerfile (Optional)

Railway auto-detects Node.js projects, but you can use a custom Dockerfile:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY dist ./dist

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

## Cron Jobs with Railway

Railway supports cron jobs as separate services:

```typescript
// src/cron.ts
import { syncInstallations, sendDigests } from "./tasks";

async function main() {
  console.log("Running scheduled tasks...");

  await syncInstallations();
  await sendDigests();

  console.log("Tasks completed");
  process.exit(0);
}

main().catch((error) => {
  console.error("Cron failed:", error);
  process.exit(1);
});
```

Configure in Railway dashboard:
- Create new service from same repo
- Set start command: `npm run cron`
- Configure cron schedule: `0 0 * * *` (daily)

## Local Development

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Pull environment variables
railway env

# Run locally with Railway env
railway run npm run dev
```

## Deployment

### Via Git

1. Connect GitHub repo in Railway dashboard
2. Railway auto-deploys on push to main
3. Configure environment variables in dashboard

### Via CLI

```bash
# Deploy
railway up

# Set environment variables
railway variables set GITHUB_APP_ID=123456
railway variables set GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."
railway variables set GITHUB_WEBHOOK_SECRET=your-secret
```

## Environment Variables

Set in Railway dashboard or CLI:

| Variable | Description |
|----------|-------------|
| `GITHUB_APP_ID` | From GitHub App settings |
| `GITHUB_PRIVATE_KEY` | PEM format (escape newlines) |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret |
| `DATABASE_URL` | Auto-set when PostgreSQL added |
| `REDIS_URL` | Auto-set when Redis added |

## Custom Domains

1. Go to project settings in Railway
2. Add custom domain
3. Configure DNS CNAME to `*.up.railway.app`
4. Update GitHub App webhook URL

## Monitoring

Railway provides built-in:
- Logs (real-time streaming)
- Metrics (CPU, memory, network)
- Deployment history

For more advanced monitoring:

```typescript
// Structured logging
console.log(
  JSON.stringify({
    level: "info",
    event: "pr_opened",
    pr: payload.pull_request.number,
    repo: payload.repository.full_name,
    timestamp: new Date().toISOString(),
  })
);
```

## Production Checklist

- [ ] Environment variables configured
- [ ] PostgreSQL/Redis provisioned if needed
- [ ] Custom domain configured
- [ ] Health check endpoint working
- [ ] Logging configured
- [ ] Restart policy set
- [ ] Upgraded from free tier (for always-on)
- [ ] Webhook URL updated in GitHub App

## Cost Optimization

- Use starter plan for low-traffic apps
- Scale down replicas during off-hours (manual)
- Use Redis TTL for cache expiration
- Monitor usage in Railway dashboard

## See Also

- [Hosting Overview](README.md)
- [Railway Documentation](https://docs.railway.app/)
