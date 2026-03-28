# Fly.io for GitHub Apps

Global edge deployment with containers. Low latency worldwide with persistent volumes.

## Why Fly.io?

| Advantage | Details |
|-----------|---------|
| Global deployment | 30+ regions worldwide |
| Low latency | Run close to users |
| Persistent volumes | SQLite, local storage |
| WebSocket support | Full duplex connections |
| Machine scaling | Scale to zero or up |

## Limitations

- **More complex setup** - Requires Dockerfile knowledge
- **Pricing model** - Per-VM pricing
- **Learning curve** - Fly-specific concepts (machines, volumes)
- **Cold starts** - If scaled to zero

## Project Structure

```
my-github-app/
├── src/
│   ├── index.ts
│   ├── webhooks.ts
│   └── github.ts
├── Dockerfile
├── fly.toml
├── package.json
└── .env
```

## Basic Setup

```typescript
// src/index.ts
import Fastify from "fastify";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "./github";

const fastify = Fastify({ logger: true });

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

fastify.post("/webhook", async (request, reply) => {
  const signature = request.headers["x-hub-signature-256"] as string;
  const body =
    typeof request.body === "string"
      ? request.body
      : JSON.stringify(request.body);

  try {
    await webhooks.verifyAndReceive({
      id: request.headers["x-github-delivery"] as string,
      name: request.headers["x-github-event"] as any,
      signature,
      payload: body,
    });
    return { status: "ok" };
  } catch (error) {
    fastify.log.error(error);
    reply.status(401);
    return { error: "Unauthorized" };
  }
});

fastify.get("/health", async () => ({ status: "ok" }));

const start = async () => {
  try {
    await fastify.listen({
      port: Number(process.env.PORT) || 3000,
      host: "0.0.0.0",
    });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
```

## Configuration

### fly.toml

```toml
app = "my-github-app"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  LOG_LEVEL = "info"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "connections"
    hard_limit = 100
    soft_limit = 80

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
  timeout = "5s"

# Multi-region deployment
# [[regions]]
#   name = "ams"
# [[regions]]
#   name = "syd"
```

### Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

## Using SQLite with Volumes

Fly supports persistent volumes for local storage:

```toml
# fly.toml
[mounts]
  source = "data"
  destination = "/data"
```

```typescript
// src/db.ts
import Database from "better-sqlite3";

const db = new Database("/data/github-app.db");

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS installations (
    id INTEGER PRIMARY KEY,
    owner TEXT NOT NULL,
    settings TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  )
`);

export function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): void {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO installations (id, owner, settings)
    VALUES (?, ?, ?)
  `);
  stmt.run(id, owner, JSON.stringify(settings));
}

export function getInstallation(id: number) {
  const stmt = db.prepare("SELECT * FROM installations WHERE id = ?");
  return stmt.get(id);
}
```

## Using Fly Postgres

```bash
# Create Postgres cluster
fly postgres create --name github-app-db

# Attach to app
fly postgres attach github-app-db
```

```typescript
// src/db.ts
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await pool.query(
    `INSERT INTO installations (id, owner, settings)
     VALUES ($1, $2, $3)
     ON CONFLICT (id) DO UPDATE SET settings = $3`,
    [id, owner, JSON.stringify(settings)]
  );
}
```

## Using Upstash Redis

Fly integrates with Upstash for Redis:

```bash
fly redis create
```

```typescript
// src/cache.ts
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export async function cacheToken(
  installationId: number,
  token: string,
  ttl: number
): Promise<void> {
  await redis.setex(`token:${installationId}`, ttl, token);
}

export async function getCachedToken(
  installationId: number
): Promise<string | null> {
  return redis.get(`token:${installationId}`);
}
```

## Multi-Region Deployment

```toml
# fly.toml
primary_region = "sjc"

[http_service]
  # ... other config

# Add more regions
[[regions]]
  name = "ams"  # Amsterdam
[[regions]]
  name = "syd"  # Sydney
[[regions]]
  name = "nrt"  # Tokyo
```

```bash
# Scale to multiple regions
fly scale count 2 --region sjc,ams
```

## Secrets Management

```bash
# Set secrets
fly secrets set GITHUB_APP_ID=123456
fly secrets set GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
fly secrets set GITHUB_WEBHOOK_SECRET=your-secret

# List secrets
fly secrets list

# Unset secret
fly secrets unset OLD_SECRET
```

## Local Development

```bash
# Install Fly CLI
brew install flyctl

# Login
fly auth login

# Run locally (with secrets)
fly dev

# Or use docker-compose
docker-compose up
```

### docker-compose.yml (for local dev)

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - GITHUB_APP_ID=${GITHUB_APP_ID}
      - GITHUB_PRIVATE_KEY=${GITHUB_PRIVATE_KEY}
      - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
    volumes:
      - ./data:/data
```

## Deployment

```bash
# Initial deployment
fly launch

# Subsequent deployments
fly deploy

# Deploy to specific region
fly deploy --region sjc

# Blue-green deployment
fly deploy --strategy bluegreen
```

## Scaling

```bash
# Scale horizontally
fly scale count 3

# Scale vertically
fly scale vm shared-cpu-2x

# Scale to zero (save costs)
fly scale count 0

# Auto-scaling config in fly.toml
```

## Scheduled Tasks

Use Fly Machines for cron-like tasks:

```bash
# Create a machine that runs on schedule
fly machine run . --schedule "0 0 * * *" --command "npm run cron"
```

Or use external scheduler (GitHub Actions, etc.) to call an endpoint:

```typescript
fastify.post("/cron/daily", async (request, reply) => {
  // Verify cron secret
  if (request.headers["x-cron-secret"] !== process.env.CRON_SECRET) {
    reply.status(401);
    return { error: "Unauthorized" };
  }

  await runDailyTasks();
  return { status: "ok" };
});
```

## Monitoring

```bash
# View logs
fly logs

# View metrics
fly dashboard

# SSH into machine
fly ssh console
```

Built-in metrics include:
- Request rate
- Response times
- Memory/CPU usage
- Network traffic

## Production Checklist

- [ ] Secrets configured
- [ ] Health check endpoint working
- [ ] Volume attached (if using SQLite)
- [ ] Postgres/Redis provisioned if needed
- [ ] Custom domain configured
- [ ] TLS configured (automatic with Fly)
- [ ] Multi-region if needed
- [ ] min_machines_running > 0 for no cold starts
- [ ] Monitoring dashboard set up

## Cost Optimization

- Use `auto_stop_machines = true` for low traffic
- Scale down replicas in off-peak regions
- Use shared-cpu VMs for low-traffic apps
- Monitor usage with `fly billing`

```toml
# Cost-optimized config
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0  # Scale to zero
```

## See Also

- [Hosting Overview](README.md)
- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Postgres](https://fly.io/docs/postgres/)
