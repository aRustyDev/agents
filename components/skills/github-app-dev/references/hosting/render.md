# Render for GitHub Apps

Simple container hosting with automatic deployments. Good balance of simplicity and flexibility.

## Why Render?

| Advantage | Details |
|-----------|---------|
| Simple deployment | Git push to deploy |
| Managed services | PostgreSQL, Redis built-in |
| Preview environments | Per-PR deployments |
| Zero DevOps | No Kubernetes/Docker knowledge needed |
| Free tier | Hobby projects supported |

## Limitations

- **Spin down on free tier** - 15min inactivity (paid plans always-on)
- **Single region** - US/EU only
- **Limited customization** - Less control than raw containers
- **Resource limits** - Memory/CPU caps per tier

## Project Structure

```
my-github-app/
├── src/
│   ├── index.ts
│   ├── webhooks.ts
│   └── github.ts
├── render.yaml       # Infrastructure as code
├── Dockerfile        # Optional
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

webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(payload.installation!.id);

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Thanks for the PR!",
  });
});

app.post("/webhook", express.raw({ type: "application/json" }), async (req, res) => {
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
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

## Configuration

### render.yaml (Blueprint)

```yaml
services:
  - type: web
    name: github-app
    env: node
    region: oregon
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    healthCheckPath: /health
    envVars:
      - key: NODE_ENV
        value: production
      - key: GITHUB_APP_ID
        sync: false  # Manual entry required
      - key: GITHUB_PRIVATE_KEY
        sync: false
      - key: GITHUB_WEBHOOK_SECRET
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: github-app-db
          property: connectionString

databases:
  - name: github-app-db
    plan: starter
    databaseName: github_app
    user: github_app

# Optional Redis
  - type: redis
    name: github-app-redis
    plan: starter
    maxmemoryPolicy: allkeys-lru
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
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "@octokit/auth-app": "^6.0.0",
    "@octokit/rest": "^20.0.0",
    "@octokit/webhooks": "^12.0.0",
    "express": "^4.18.0",
    "pg": "^8.11.0"
  }
}
```

## Using Render PostgreSQL

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

Create migrations and run on deploy:

```typescript
// src/migrate.ts
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

async function migrate() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS installations (
      id INTEGER PRIMARY KEY,
      owner TEXT NOT NULL,
      settings JSONB DEFAULT '{}',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
  `);

  console.log("Migrations completed");
  process.exit(0);
}

migrate().catch((err) => {
  console.error("Migration failed:", err);
  process.exit(1);
});
```

```json
// package.json
{
  "scripts": {
    "migrate": "tsx src/migrate.ts",
    "build": "tsc && npm run migrate"
  }
}
```

## Using Render Redis

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

## Cron Jobs

Use Render's Cron Jobs feature:

```yaml
# render.yaml
services:
  # ... web service

  - type: cron
    name: github-app-daily
    env: node
    schedule: "0 0 * * *"  # Daily at midnight
    buildCommand: npm install && npm run build
    startCommand: npm run cron
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: github-app-db
          property: connectionString
```

```typescript
// src/cron.ts
import { syncInstallations, sendDigests } from "./tasks";

async function main() {
  console.log("Running daily cron job");

  await syncInstallations();
  await sendDigests();

  console.log("Cron job completed");
  process.exit(0);
}

main().catch((err) => {
  console.error("Cron failed:", err);
  process.exit(1);
});
```

## Background Workers

For async task processing:

```yaml
# render.yaml
services:
  # ... web service

  - type: worker
    name: github-app-worker
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm run worker
    envVars:
      - key: REDIS_URL
        fromService:
          name: github-app-redis
          type: redis
          property: connectionString
```

```typescript
// src/worker.ts
import { createClient } from "redis";
import { processTask } from "./tasks";

const redis = createClient({ url: process.env.REDIS_URL });

async function main() {
  await redis.connect();

  while (true) {
    const task = await redis.brPop("task-queue", 0);
    if (task) {
      await processTask(JSON.parse(task.element));
    }
  }
}

main().catch(console.error);
```

## Dockerfile (Optional)

Render auto-detects Node.js, but you can customize:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY dist ./dist

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

## Local Development

```bash
# Run locally
npm run dev

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:3000/webhook
```

## Deployment

### Via Dashboard

1. Connect GitHub repo in Render dashboard
2. Select "Web Service"
3. Configure build and start commands
4. Add environment variables
5. Deploy

### Via Blueprint (render.yaml)

1. Add render.yaml to repo
2. In Render dashboard, click "New" → "Blueprint"
3. Select repo
4. Review and deploy

### Environment Variables

Set in Render dashboard under "Environment":

| Variable | Description |
|----------|-------------|
| `GITHUB_APP_ID` | From GitHub App settings |
| `GITHUB_PRIVATE_KEY` | PEM format (paste directly) |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret |
| `DATABASE_URL` | Auto-set from linked database |
| `REDIS_URL` | Auto-set from linked Redis |

## Preview Environments

Enable in Render dashboard for PR previews:

1. Go to Service settings
2. Enable "Pull Request Previews"
3. Each PR gets isolated environment

## Custom Domains

1. Go to Service settings → "Custom Domain"
2. Add your domain
3. Configure DNS (CNAME to `*.onrender.com`)
4. SSL auto-configured

## Monitoring

Render provides:
- Real-time logs
- Metrics (CPU, memory, requests)
- Deploy history

For structured logging:

```typescript
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
- [ ] Health check endpoint working
- [ ] Custom domain configured
- [ ] Preview environments enabled
- [ ] Cron jobs configured if needed
- [ ] Upgraded from free tier (for always-on)
- [ ] Webhook URL updated in GitHub App

## Pricing

| Plan | Price | Always-on | Specs |
|------|-------|-----------|-------|
| Free | $0 | No (spins down) | 512MB RAM |
| Starter | $7/mo | Yes | 512MB RAM |
| Standard | $25/mo | Yes | 2GB RAM |
| Pro | $85/mo | Yes | 4GB RAM |

## See Also

- [Hosting Overview](README.md)
- [Render Documentation](https://render.com/docs)
