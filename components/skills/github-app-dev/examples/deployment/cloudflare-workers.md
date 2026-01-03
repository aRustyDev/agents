# Cloudflare Workers Deployment

Complete guide for deploying GitHub Apps to Cloudflare Workers with optimal performance and security.

## Quick Setup (5 minutes)

```bash
# 1. Install Wrangler CLI
npm install -g wrangler

# 2. Authenticate with Cloudflare
wrangler login

# 3. Create new project
wrangler init github-app-worker

# 4. Set secrets
wrangler secret put GITHUB_APP_ID
wrangler secret put GITHUB_PRIVATE_KEY
wrangler secret put GITHUB_WEBHOOK_SECRET

# 5. Deploy
wrangler deploy
```

## Project Structure

```
github-app-worker/
├── src/
│   ├── index.ts           # Main worker entry point
│   ├── github.ts          # GitHub client setup
│   ├── handlers/          # Webhook event handlers
│   └── utils/             # Shared utilities
├── wrangler.toml          # Cloudflare configuration
├── package.json
├── tsconfig.json
└── .env.example           # Environment template
```

## Configuration Files

### wrangler.toml
```toml
name = "github-app-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[env.production]
route = { pattern = "app.yourdomain.com/*", zone_name = "yourdomain.com" }

[env.staging]
route = { pattern = "staging-app.yourdomain.com/*", zone_name = "yourdomain.com" }

# Environment variables (non-secret)
[vars]
ENVIRONMENT = "production"
LOG_LEVEL = "info"
WEBHOOK_PATH = "/webhook"

# KV bindings for rate limiting and caching
[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"
preview_id = "your-preview-kv-namespace-id"

# Analytics binding for monitoring
[analytics_engine_datasets]
binding = "ANALYTICS"
dataset = "github_app_metrics"

# Custom domains
[routes]
pattern = "app.yourdomain.com/*"
zone_name = "yourdomain.com"
```

### package.json
```json
{
  "name": "github-app-worker",
  "version": "1.0.0",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "deploy:staging": "wrangler deploy --env staging",
    "logs": "wrangler tail",
    "test": "vitest",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@octokit/webhooks": "^12.0.0",
    "@octokit/auth-app": "^6.0.0",
    "@octokit/rest": "^20.0.0",
    "hono": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "wrangler": "^3.0.0"
  }
}
```

## Main Worker Implementation

### src/index.ts
```typescript
import { Hono } from "hono";
import { WebhookSecurity } from "./security";
import { GitHubAppHandler } from "./handlers";

type Bindings = {
  // Secrets
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;

  // Environment variables
  ENVIRONMENT?: string;
  LOG_LEVEL?: string;
  WEBHOOK_PATH?: string;

  // Bindings
  CACHE: KVNamespace;
  ANALYTICS: AnalyticsEngineDataset;
};

const app = new Hono<{ Bindings: Bindings }>();

// Health check
app.get("/health", (c) => {
  return c.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    environment: c.env.ENVIRONMENT || "unknown",
    version: "1.0.0",
  });
});

// Webhook endpoint with security
app.post("/webhook", async (c) => {
  const security = new WebhookSecurity(c.env.GITHUB_WEBHOOK_SECRET);
  const handler = new GitHubAppHandler(c.env, c.env.CACHE);

  try {
    // Verify webhook signature
    const payload = await c.req.text();
    const signature = c.req.header("X-Hub-Signature-256") || "";

    if (!security.verifySignature(payload, signature)) {
      return c.json({ error: "Invalid signature" }, 401);
    }

    // Process webhook
    const result = await handler.processWebhook(
      JSON.parse(payload),
      c.req.header("X-GitHub-Event") || "",
      c.req.header("X-GitHub-Delivery") || ""
    );

    // Log metrics to Analytics Engine
    c.env.ANALYTICS.writeDataPoint({
      blobs: [
        c.req.header("X-GitHub-Event") || "unknown",
        result.success ? "success" : "error",
      ],
      doubles: [result.processingTime],
      indexes: [result.installationId],
    });

    return c.json({ status: "processed", ...result });
  } catch (error) {
    console.error("Webhook processing error:", error);
    return c.json({ error: "Internal error" }, 500);
  }
});

export default app;
```

## Performance Optimizations

### Edge Caching Strategy
```typescript
// src/cache.ts
export class EdgeCache {
  constructor(private kv: KVNamespace) {}

  async cacheInstallationToken(
    installationId: number,
    token: string,
    expiresAt: Date
  ) {
    const key = `token:${installationId}`;
    const ttl = Math.floor((expiresAt.getTime() - Date.now()) / 1000);

    await this.kv.put(key, token, { expirationTtl: ttl });
  }

  async getInstallationToken(installationId: number): Promise<string | null> {
    const key = `token:${installationId}`;
    return await this.kv.get(key);
  }

  async cacheRateLimit(installationId: number, remaining: number, resetTime: number) {
    const key = `ratelimit:${installationId}`;
    const data = { remaining, resetTime, timestamp: Date.now() };

    await this.kv.put(key, JSON.stringify(data), {
      expirationTtl: Math.floor((resetTime - Date.now()) / 1000),
    });
  }
}
```

### Connection Pooling
```typescript
// src/github.ts
let globalOctokit: Map<number, { octokit: Octokit; expires: number }> | undefined;

export function getInstallationOctokit(
  env: Bindings,
  installationId: number
): Octokit {
  // Connection pooling for better performance
  if (!globalOctokit) {
    globalOctokit = new Map();
  }

  const cached = globalOctokit.get(installationId);
  if (cached && cached.expires > Date.now()) {
    return cached.octokit;
  }

  const octokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
      installationId,
    },
  });

  // Cache for 50 minutes (tokens expire after 1 hour)
  globalOctokit.set(installationId, {
    octokit,
    expires: Date.now() + 50 * 60 * 1000,
  });

  return octokit;
}
```

## Deployment Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Workers

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run test
      - run: npm run type-check

  deploy-staging:
    if: github.event_name == 'pull_request'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npx wrangler deploy --env staging
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}

  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npx wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

## Monitoring and Observability

### Analytics and Metrics
```typescript
// src/analytics.ts
export class WorkerAnalytics {
  constructor(private analytics: AnalyticsEngineDataset) {}

  logWebhookEvent(
    event: string,
    success: boolean,
    processingTime: number,
    installationId: number
  ) {
    this.analytics.writeDataPoint({
      blobs: [event, success ? "success" : "error"],
      doubles: [processingTime],
      indexes: [installationId],
    });
  }

  logApiCall(
    endpoint: string,
    statusCode: number,
    responseTime: number,
    installationId: number
  ) {
    this.analytics.writeDataPoint({
      blobs: [endpoint, statusCode.toString()],
      doubles: [responseTime],
      indexes: [installationId],
    });
  }
}
```

### Error Tracking
```typescript
// Add to your webhook handler
try {
  // Process webhook
} catch (error) {
  // Log structured error for analysis
  console.error("Webhook error", {
    error: error.message,
    stack: error.stack,
    event,
    installationId,
    deliveryId,
    timestamp: new Date().toISOString(),
  });

  // Optional: Send to external error tracking service
  await fetch("https://api.sentry.io/api/...", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: error.message,
      extra: { event, installationId, deliveryId },
    }),
  });
}
```

## Security Best Practices

### 1. Secret Management
```bash
# Use Wrangler for secret management
wrangler secret put GITHUB_APP_ID --env production
wrangler secret put GITHUB_PRIVATE_KEY --env production
wrangler secret put GITHUB_WEBHOOK_SECRET --env production

# Verify secrets
wrangler secret list --env production
```

### 2. Rate Limiting with KV
```typescript
// src/rateLimit.ts
export class WorkerRateLimit {
  constructor(private kv: KVNamespace) {}

  async checkRateLimit(installationId: number): Promise<boolean> {
    const key = `requests:${installationId}:${Math.floor(Date.now() / 60000)}`;

    const count = await this.kv.get(key);
    const currentCount = count ? parseInt(count) : 0;

    if (currentCount >= 60) { // 60 requests per minute
      return false;
    }

    await this.kv.put(key, (currentCount + 1).toString(), {
      expirationTtl: 60,
    });

    return true;
  }
}
```

## Troubleshooting

### Common Issues

1. **Token Caching Problems**
   ```bash
   # Check KV namespace
   wrangler kv:key list --binding CACHE

   # Clear cached tokens
   wrangler kv:key delete "token:123" --binding CACHE
   ```

2. **Memory Limits**
   - Workers have 128MB memory limit
   - Avoid loading large payloads into memory
   - Stream responses when possible

3. **CPU Time Limits**
   - 10ms CPU time for free tier
   - 50ms for paid plans
   - Use async operations efficiently

### Performance Monitoring
```bash
# Monitor real-time logs
wrangler tail --env production

# Check Analytics Engine data
wrangler analytics --env production

# Monitor KV usage
wrangler kv:list --binding CACHE
```

## Cost Optimization

### Usage Patterns
- **Free Tier**: 100,000 requests/day
- **Paid Plans**: $0.50 per million requests
- **KV Operations**: $0.50 per million reads

### Optimization Tips
1. Cache installation tokens (saves 2-3 API calls per webhook)
2. Use Analytics Engine for metrics (cheaper than external services)
3. Implement intelligent rate limiting
4. Bundle multiple GitHub API calls when possible

## Migration from Other Platforms

### From Vercel
1. Copy handler logic from `api/webhook.js`
2. Update imports for Hono instead of Next.js
3. Replace Vercel KV with Cloudflare KV
4. Update deployment configuration

### From AWS Lambda
1. Remove AWS SDK dependencies
2. Replace environment variables with Cloudflare secrets
3. Update cold start optimizations for Workers
4. Migrate monitoring to Analytics Engine

## Advanced Features

### Multi-Region Deployment
```toml
# wrangler.toml
[env.global]
routes = [
  { pattern = "api.yourdomain.com/*", zone_name = "yourdomain.com" }
]

[env.us]
routes = [
  { pattern = "us-api.yourdomain.com/*", zone_name = "yourdomain.com" }
]

[env.eu]
routes = [
  { pattern = "eu-api.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

### Durable Objects for State
```typescript
// For apps requiring persistent state
export class GitHubAppState {
  constructor(private state: DurableObjectState) {}

  async handleWebhook(event: any) {
    // Persistent state across requests
    const lastProcessed = await this.state.storage.get("lastProcessed");

    // Process webhook with state
    await this.state.storage.put("lastProcessed", Date.now());
  }
}
```

This deployment guide provides everything needed to deploy production-ready GitHub Apps to Cloudflare Workers with optimal performance, security, and monitoring.