# DigitalOcean for GitHub Apps

Flexible hosting from App Platform to self-managed Droplets. Good for teams wanting more control.

## Hosting Options

| Option | Best For | Complexity |
|--------|----------|------------|
| App Platform | Managed containers | Low |
| Droplets | Self-managed VMs | Medium |
| Kubernetes | Large scale | High |

## App Platform (Recommended)

### Why App Platform?

| Advantage | Details |
|-----------|---------|
| Managed deployment | Git push to deploy |
| Built-in databases | PostgreSQL, MySQL, Redis |
| Auto-scaling | Scale based on traffic |
| Zero DevOps | No server management |

### Project Structure

```
my-github-app/
├── src/
│   ├── index.ts
│   ├── webhooks.ts
│   └── github.ts
├── .do/
│   └── app.yaml       # App spec
├── Dockerfile
├── package.json
└── .env
```

### Basic Setup

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
      port: Number(process.env.PORT) || 8080,
      host: "0.0.0.0",
    });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
```

### App Spec (.do/app.yaml)

```yaml
name: github-app
region: nyc

services:
  - name: web
    github:
      repo: your-org/your-repo
      branch: main
      deploy_on_push: true
    dockerfile_path: Dockerfile
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 8080
    health_check:
      http_path: /health
    envs:
      - key: NODE_ENV
        value: production
      - key: GITHUB_APP_ID
        value: "123456"
      - key: GITHUB_PRIVATE_KEY
        type: SECRET
      - key: GITHUB_WEBHOOK_SECRET
        type: SECRET
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}

databases:
  - name: db
    engine: PG
    production: false
    cluster_name: github-app-db
    db_name: github_app
    db_user: github_app

# Optional: Add workers
workers:
  - name: cron
    github:
      repo: your-org/your-repo
      branch: main
    dockerfile_path: Dockerfile.cron
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}

# Optional: Add jobs
jobs:
  - name: migrate
    github:
      repo: your-org/your-repo
      branch: main
    dockerfile_path: Dockerfile
    kind: PRE_DEPLOY
    run_command: npm run migrate
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
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

EXPOSE 8080

CMD ["node", "dist/index.js"]
```

## Using DO Managed PostgreSQL

```typescript
// src/db.ts
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
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

## Using DO Managed Redis

```yaml
# .do/app.yaml - add to services
services:
  - name: web
    # ... existing config
    envs:
      - key: REDIS_URL
        scope: RUN_TIME
        value: ${redis.DATABASE_URL}

databases:
  - name: redis
    engine: REDIS
    production: false
```

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
```

## Droplets (Self-Managed)

For more control, deploy to a Droplet:

### Setup Script

```bash
#!/bin/bash
# Run on fresh Ubuntu Droplet

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Clone repo
git clone https://github.com/your-org/your-repo.git /app
cd /app

# Install dependencies
npm ci --production

# Build
npm run build

# Configure environment
cat > .env << 'EOF'
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."
GITHUB_WEBHOOK_SECRET=your-secret
PORT=3000
EOF

# Start with PM2
pm2 start dist/index.js --name github-app
pm2 startup
pm2 save
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/github-app
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site and SSL
sudo ln -s /etc/nginx/sites-available/github-app /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

## DO Functions (Serverless)

DigitalOcean also offers Functions (serverless):

```yaml
# project.yml
packages:
  - name: github-app
    functions:
      - name: webhook
        runtime: nodejs:20
        web: true
        main: webhook/index.js
        environment:
          GITHUB_APP_ID: "123456"
```

```javascript
// packages/github-app/webhook/index.js
const { Webhooks } = require("@octokit/webhooks");

async function main(args) {
  const webhooks = new Webhooks({
    secret: process.env.GITHUB_WEBHOOK_SECRET,
  });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    console.log(`PR #${payload.pull_request.number} opened`);
  });

  try {
    await webhooks.verifyAndReceive({
      id: args.__ow_headers["x-github-delivery"],
      name: args.__ow_headers["x-github-event"],
      signature: args.__ow_headers["x-hub-signature-256"],
      payload: JSON.stringify(args),
    });
    return { body: "OK" };
  } catch {
    return { statusCode: 401, body: "Unauthorized" };
  }
}

exports.main = main;
```

## Local Development

```bash
# Run locally
npm run dev

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8080/webhook
```

## Deployment

### App Platform via CLI

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml

# Update app
doctl apps update <app-id> --spec .do/app.yaml

# View logs
doctl apps logs <app-id>
```

### App Platform via Dashboard

1. Go to App Platform in DO console
2. Create App → GitHub
3. Select repo and branch
4. Configure resources and environment
5. Deploy

## Secrets Management

### App Platform

Set secrets in the dashboard or via CLI:

```bash
# Create secret
doctl apps create-deployment <app-id> \
  --env "GITHUB_PRIVATE_KEY=$(cat private-key.pem)"
```

### Droplets

Use DO's encrypted environment variables or external secret management.

## Monitoring

### App Platform

Built-in monitoring includes:
- Request metrics
- CPU/Memory usage
- Deployment history
- Logs

### Droplets

Use DO Monitoring agent:

```bash
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash
```

## Production Checklist

### App Platform

- [ ] App spec configured (.do/app.yaml)
- [ ] Environment variables set
- [ ] Database provisioned
- [ ] Health check endpoint working
- [ ] Custom domain configured
- [ ] Auto-deploy enabled
- [ ] Webhook URL updated in GitHub App

### Droplets

- [ ] Node.js/PM2 installed
- [ ] Nginx configured with SSL
- [ ] Firewall configured (ufw)
- [ ] Automated backups enabled
- [ ] Monitoring agent installed
- [ ] Log rotation configured

## Pricing

### App Platform

| Tier | Price | Specs |
|------|-------|-------|
| Basic | $5/mo | 512MB RAM, 1 vCPU |
| Professional | $12/mo | 1GB RAM, 1 vCPU |
| + Database | $15/mo+ | Managed PostgreSQL |

### Droplets

| Tier | Price | Specs |
|------|-------|-------|
| Basic | $4/mo | 512MB RAM, 1 vCPU |
| Basic | $6/mo | 1GB RAM, 1 vCPU |
| + Managed DB | $15/mo+ | PostgreSQL |

## See Also

- [Hosting Overview](README.md)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean Functions](https://docs.digitalocean.com/products/functions/)
