# Vercel Deployment

Complete guide for deploying GitHub Apps to Vercel with serverless functions and edge optimization.

## Quick Setup (3 minutes)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Initialize project
vercel init github-app-vercel

# 4. Set environment variables
vercel env add GITHUB_APP_ID production
vercel env add GITHUB_PRIVATE_KEY production
vercel env add GITHUB_WEBHOOK_SECRET production

# 5. Deploy
vercel --prod
```

## Project Structure

```
github-app-vercel/
├── api/
│   └── webhook.ts         # Serverless function
├── lib/
│   ├── github.ts          # GitHub client
│   ├── handlers/          # Event handlers
│   └── utils/             # Utilities
├── vercel.json           # Vercel configuration
├── package.json
├── tsconfig.json
└── .env.example          # Environment template
```

## Configuration Files

### vercel.json
```json
{
  "functions": {
    "api/webhook.ts": {
      "maxDuration": 30
    }
  },
  "env": {
    "NODE_ENV": "production"
  },
  "build": {
    "env": {
      "NODE_ENV": "production"
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/webhook",
      "destination": "/api/webhook",
      "permanent": false
    }
  ]
}
```

### package.json
```json
{
  "name": "github-app-vercel",
  "version": "1.0.0",
  "scripts": {
    "dev": "vercel dev",
    "build": "tsc",
    "deploy": "vercel --prod",
    "deploy:preview": "vercel",
    "test": "jest",
    "type-check": "tsc --noEmit",
    "logs": "vercel logs"
  },
  "dependencies": {
    "@octokit/webhooks": "^12.0.0",
    "@octokit/auth-app": "^6.0.0",
    "@octokit/rest": "^20.0.0",
    "@vercel/kv": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@vercel/node": "^3.0.0",
    "typescript": "^5.0.0",
    "jest": "^29.0.0"
  }
}
```

## Main API Endpoint

### api/webhook.ts
```typescript
import { VercelRequest, VercelResponse } from '@vercel/node';
import { Webhooks } from '@octokit/webhooks';
import { createAppAuth } from '@octokit/auth-app';
import { Octokit } from '@octokit/rest';
import { kv } from '@vercel/kv';
import crypto from 'crypto';

// Environment variables
const {
  GITHUB_APP_ID,
  GITHUB_PRIVATE_KEY,
  GITHUB_WEBHOOK_SECRET,
  VERCEL_ENV,
} = process.env;

// Webhook signature verification
function verifySignature(payload: string, signature: string): boolean {
  if (!GITHUB_WEBHOOK_SECRET) {
    throw new Error('GITHUB_WEBHOOK_SECRET not configured');
  }

  const expectedSignature = crypto
    .createHmac('sha256', GITHUB_WEBHOOK_SECRET)
    .update(payload, 'utf8')
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expectedSignature}`, 'utf8'),
    Buffer.from(signature, 'utf8')
  );
}

// Create installation-scoped Octokit
async function createInstallationOctokit(installationId: number): Promise<Octokit> {
  if (!GITHUB_APP_ID || !GITHUB_PRIVATE_KEY) {
    throw new Error('GitHub App credentials not configured');
  }

  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: GITHUB_APP_ID,
      privateKey: GITHUB_PRIVATE_KEY,
      installationId,
    },
  });
}

// Rate limiting with Vercel KV
async function checkRateLimit(installationId: number): Promise<boolean> {
  const key = `ratelimit:${installationId}:${Math.floor(Date.now() / 60000)}`;
  const current = await kv.incr(key);

  if (current === 1) {
    await kv.expire(key, 60); // Expire in 60 seconds
  }

  return current <= 60; // 60 requests per minute
}

// Webhook handlers
class GitHubAppHandler {
  private octokit: Octokit;

  constructor(octokit: Octokit) {
    this.octokit = octokit;
  }

  async handlePullRequestOpened(payload: any) {
    const { repository, pull_request } = payload;
    const { owner, name: repo } = repository;
    const { number, title, user } = pull_request;

    console.log(`Processing PR #${number} in ${owner.login}/${repo}`);

    try {
      // Check if first-time contributor
      const { data: issues } = await this.octokit.search.issuesAndPullRequests({
        q: `repo:${owner.login}/${repo} author:${user.login}`,
        per_page: 1,
      });

      if (issues.total_count <= 1) {
        await this.octokit.issues.createComment({
          owner: owner.login,
          repo,
          issue_number: number,
          body: `👋 Welcome @${user.login}! Thanks for your first contribution to this project.

Here are some helpful resources:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

A maintainer will review your PR soon. Make sure:
- [ ] Tests pass
- [ ] Documentation is updated if needed
- [ ] PR title follows [conventional commits](https://conventionalcommits.org)`,
        });
      }

      // Auto-label based on title
      const labels = this.extractLabelsFromTitle(title);
      if (labels.length > 0) {
        await this.octokit.issues.addLabels({
          owner: owner.login,
          repo,
          issue_number: number,
          labels,
        });
      }

      return { success: true, labels };
    } catch (error) {
      console.error('Error handling PR:', error);
      throw error;
    }
  }

  async handleIssueOpened(payload: any) {
    const { repository, issue } = payload;
    const { owner, name: repo } = repository;
    const { number } = issue;

    await this.octokit.issues.addLabels({
      owner: owner.login,
      repo,
      issue_number: number,
      labels: ['triage'],
    });

    return { success: true };
  }

  private extractLabelsFromTitle(title: string): string[] {
    const labels: string[] = [];
    if (title.match(/^feat(\(.+\))?:/)) labels.push('enhancement');
    if (title.match(/^fix(\(.+\))?:/)) labels.push('bug');
    if (title.match(/^docs(\(.+\))?:/)) labels.push('documentation');
    if (title.includes('!:') || title.includes('BREAKING CHANGE')) {
      labels.push('breaking-change');
    }
    return labels;
  }
}

// Main handler
export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const deliveryId = req.headers['x-github-delivery'] as string;
  const event = req.headers['x-github-event'] as string;
  const signature = req.headers['x-hub-signature-256'] as string;

  console.log(`Webhook received: ${event} (${deliveryId})`);

  try {
    // Get raw body for signature verification
    const payload = JSON.stringify(req.body);

    // Verify webhook signature
    if (!signature || !verifySignature(payload, signature)) {
      console.warn('Invalid signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const webhookPayload = req.body;
    const { installation } = webhookPayload;

    if (!installation) {
      console.warn('No installation in payload');
      return res.status(400).json({ error: 'No installation found' });
    }

    // Rate limiting
    const rateLimitOk = await checkRateLimit(installation.id);
    if (!rateLimitOk) {
      console.warn(`Rate limit exceeded for installation ${installation.id}`);
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }

    // Create authenticated Octokit
    const octokit = await createInstallationOctokit(installation.id);
    const handler = new GitHubAppHandler(octokit);

    let result;
    switch (event) {
      case 'pull_request':
        if (webhookPayload.action === 'opened') {
          result = await handler.handlePullRequestOpened(webhookPayload);
        }
        break;

      case 'issues':
        if (webhookPayload.action === 'opened') {
          result = await handler.handleIssueOpened(webhookPayload);
        }
        break;

      default:
        console.log(`Unhandled event: ${event}`);
        return res.status(200).json({ message: 'Event not handled' });
    }

    // Log successful processing
    await kv.lpush(`logs:${installation.id}`, JSON.stringify({
      timestamp: new Date().toISOString(),
      event,
      deliveryId,
      success: true,
      result,
    }));

    return res.status(200).json({
      message: 'Webhook processed successfully',
      event,
      deliveryId,
      result,
    });

  } catch (error: any) {
    console.error('Webhook processing failed:', error);

    // Log error
    if (req.body?.installation?.id) {
      await kv.lpush(`logs:${req.body.installation.id}`, JSON.stringify({
        timestamp: new Date().toISOString(),
        event,
        deliveryId,
        success: false,
        error: error.message,
      }));
    }

    return res.status(500).json({
      error: 'Internal server error',
      deliveryId,
    });
  }
}
```

## Vercel KV Integration

### lib/cache.ts
```typescript
import { kv } from '@vercel/kv';

export class VercelCache {
  // Cache GitHub installation tokens
  static async cacheToken(installationId: number, token: string, expiresAt: Date) {
    const key = `token:${installationId}`;
    const ttl = Math.floor((expiresAt.getTime() - Date.now()) / 1000);

    await kv.setex(key, ttl, token);
  }

  static async getToken(installationId: number): Promise<string | null> {
    return await kv.get(`token:${installationId}`);
  }

  // Cache rate limit status
  static async cacheRateLimit(
    installationId: number,
    remaining: number,
    resetTime: number
  ) {
    const key = `ratelimit:${installationId}`;
    const data = { remaining, resetTime, timestamp: Date.now() };
    const ttl = Math.floor((resetTime - Date.now()) / 1000);

    await kv.setex(key, ttl, JSON.stringify(data));
  }

  static async getRateLimit(installationId: number) {
    const data = await kv.get(`ratelimit:${installationId}`);
    return data ? JSON.parse(data) : null;
  }

  // Store webhook processing logs
  static async logWebhook(
    installationId: number,
    event: string,
    deliveryId: string,
    success: boolean,
    details?: any
  ) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event,
      deliveryId,
      success,
      details,
    };

    // Keep last 100 log entries per installation
    await kv.lpush(`logs:${installationId}`, JSON.stringify(logEntry));
    await kv.ltrim(`logs:${installationId}`, 0, 99);
  }

  static async getWebhookLogs(installationId: number, limit = 10) {
    const logs = await kv.lrange(`logs:${installationId}`, 0, limit - 1);
    return logs.map(log => JSON.parse(log));
  }
}
```

## Deployment Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

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
          node-version: 18
          cache: npm

      - run: npm ci
      - run: npm run test
      - run: npm run type-check

  deploy-preview:
    if: github.event_name == 'pull_request'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm

      - run: npm ci
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm

      - run: npm ci
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

## Monitoring and Observability

### Health Check API
```typescript
// api/health.ts
import { VercelRequest, VercelResponse } from '@vercel/node';
import { kv } from '@vercel/kv';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    // Test KV connection
    const testKey = `health:${Date.now()}`;
    await kv.set(testKey, 'ok', { ex: 10 });
    const testValue = await kv.get(testKey);

    if (testValue !== 'ok') {
      throw new Error('KV store not accessible');
    }

    // Test GitHub API (app-level auth)
    const appOctokit = new Octokit({
      authStrategy: createAppAuth,
      auth: {
        appId: process.env.GITHUB_APP_ID,
        privateKey: process.env.GITHUB_PRIVATE_KEY,
      },
    });

    await appOctokit.apps.getAuthenticated();

    return res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      environment: process.env.VERCEL_ENV || 'unknown',
      checks: {
        kv: 'ok',
        github: 'ok',
      },
    });
  } catch (error) {
    console.error('Health check failed:', error);
    return res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    });
  }
}
```

### Metrics Collection
```typescript
// api/metrics.ts
import { VercelRequest, VercelResponse } from '@vercel/node';
import { kv } from '@vercel/kv';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Get basic metrics from KV
    const installations = await kv.keys('logs:*');
    const totalInstallations = installations.length;

    // Get recent activity (last 24 hours)
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    let recentWebhooks = 0;
    let successfulWebhooks = 0;

    for (const installationKey of installations.slice(0, 10)) { // Limit to avoid timeout
      const logs = await kv.lrange(installationKey, 0, 100);

      for (const logStr of logs) {
        const log = JSON.parse(logStr);
        if (new Date(log.timestamp).getTime() > oneDayAgo) {
          recentWebhooks++;
          if (log.success) successfulWebhooks++;
        }
      }
    }

    const successRate = recentWebhooks > 0 ? (successfulWebhooks / recentWebhooks) * 100 : 0;

    return res.status(200).json({
      timestamp: new Date().toISOString(),
      metrics: {
        totalInstallations,
        webhooksLast24h: recentWebhooks,
        successRate: Math.round(successRate * 100) / 100,
        version: process.env.VERCEL_GIT_COMMIT_SHA?.slice(0, 7) || 'unknown',
      },
    });
  } catch (error) {
    console.error('Metrics collection failed:', error);
    return res.status(500).json({ error: 'Failed to collect metrics' });
  }
}
```

## Environment Management

### Development Setup
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Link to your Vercel project
vercel link

# 3. Pull environment variables
vercel env pull .env.local

# 4. Start development server
vercel dev
```

### Environment Variables Management
```bash
# Production environment
vercel env add GITHUB_APP_ID production
vercel env add GITHUB_PRIVATE_KEY production
vercel env add GITHUB_WEBHOOK_SECRET production

# Preview environment
vercel env add GITHUB_APP_ID preview
vercel env add GITHUB_PRIVATE_KEY preview
vercel env add GITHUB_WEBHOOK_SECRET preview

# List all environment variables
vercel env ls
```

### .env.example
```bash
# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Vercel Configuration
VERCEL_ENV=development
NODE_ENV=development

# Optional: External Services
SENTRY_DSN=https://...
DATADOG_API_KEY=...
```

## Performance Optimization

### Cold Start Optimization
```typescript
// lib/optimize.ts

// Pre-initialize common dependencies
let cachedOctokit: Map<number, Octokit> | undefined;

export function getOptimizedOctokit(installationId: number): Octokit {
  if (!cachedOctokit) {
    cachedOctokit = new Map();
  }

  const cached = cachedOctokit.get(installationId);
  if (cached) {
    return cached;
  }

  const octokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: process.env.GITHUB_APP_ID!,
      privateKey: process.env.GITHUB_PRIVATE_KEY!,
      installationId,
    },
  });

  cachedOctokit.set(installationId, octokit);
  return octokit;
}

// Connection pooling for KV
const kvPool = new Map<string, Promise<any>>();

export async function getFromCachePool<T>(
  key: string,
  fetcher: () => Promise<T>
): Promise<T> {
  if (kvPool.has(key)) {
    return await kvPool.get(key);
  }

  const promise = fetcher();
  kvPool.set(key, promise);

  // Clean up after completion
  promise.finally(() => kvPool.delete(key));

  return await promise;
}
```

### Bundle Size Optimization
```javascript
// next.config.js
module.exports = {
  experimental: {
    serverComponentsExternalPackages: ['@octokit/rest'],
  },
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Exclude large dependencies from bundle
      config.externals.push({
        '@octokit/rest': 'commonjs @octokit/rest',
        '@octokit/webhooks': 'commonjs @octokit/webhooks',
      });
    }
    return config;
  },
};
```

## Security Configuration

### Vercel Security Headers
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'none'"
        }
      ]
    }
  ]
}
```

### Rate Limiting Enhancement
```typescript
// lib/advancedRateLimit.ts
import { kv } from '@vercel/kv';

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  blockDurationMs: number;
}

export class AdvancedRateLimit {
  private config: RateLimitConfig;

  constructor(config: RateLimitConfig = {
    windowMs: 60000, // 1 minute
    maxRequests: 60,
    blockDurationMs: 300000, // 5 minutes
  }) {
    this.config = config;
  }

  async isAllowed(installationId: number): Promise<boolean> {
    const now = Date.now();
    const window = Math.floor(now / this.config.windowMs);
    const key = `rate:${installationId}:${window}`;

    // Check if currently blocked
    const blockKey = `blocked:${installationId}`;
    const blockedUntil = await kv.get(blockKey);

    if (blockedUntil && now < Number(blockedUntil)) {
      return false;
    }

    // Increment request count
    const count = await kv.incr(key);

    if (count === 1) {
      await kv.expire(key, Math.ceil(this.config.windowMs / 1000));
    }

    // Block if over limit
    if (count > this.config.maxRequests) {
      await kv.setex(
        blockKey,
        Math.ceil(this.config.blockDurationMs / 1000),
        now + this.config.blockDurationMs
      );
      return false;
    }

    return true;
  }
}
```

## Troubleshooting

### Common Issues

1. **Function Timeout**
   ```json
   // Increase timeout in vercel.json
   {
     "functions": {
       "api/webhook.ts": {
         "maxDuration": 30
       }
     }
   }
   ```

2. **Memory Issues**
   - Serverless functions have 1GB memory limit
   - Use streaming for large payloads
   - Avoid loading entire files into memory

3. **Cold Starts**
   - Keep functions warm with periodic health checks
   - Minimize dependencies
   - Use connection pooling

### Debugging
```bash
# View real-time logs
vercel logs --follow

# Check specific deployment logs
vercel logs [deployment-url]

# Debug locally
vercel dev --debug

# Inspect KV data
vercel kv:get "key" --store production
```

### Performance Monitoring
```typescript
// lib/monitoring.ts
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  startTimer(operation: string): () => void {
    const start = Date.now();

    return () => {
      const duration = Date.now() - start;
      const existing = this.metrics.get(operation) || [];
      existing.push(duration);

      // Keep last 100 measurements
      if (existing.length > 100) {
        existing.shift();
      }

      this.metrics.set(operation, existing);
    };
  }

  getStats(operation: string) {
    const times = this.metrics.get(operation) || [];
    if (times.length === 0) return null;

    const sorted = [...times].sort((a, b) => a - b);
    const avg = times.reduce((a, b) => a + b, 0) / times.length;
    const p95 = sorted[Math.floor(sorted.length * 0.95)];

    return {
      count: times.length,
      average: Math.round(avg),
      p95,
      min: Math.min(...times),
      max: Math.max(...times),
    };
  }
}
```

This guide provides a complete Vercel deployment setup with production-ready features including monitoring, security, and performance optimization.
