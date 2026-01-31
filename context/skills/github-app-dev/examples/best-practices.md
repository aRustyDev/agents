# GitHub App Best Practices

Comprehensive guide for building secure, maintainable, and performant GitHub Apps.

## Security Best Practices

### ✅ Authentication & Authorization

**Do:**
- Use installation tokens for repository operations (not personal access tokens)
- Request minimal permissions needed for your app's functionality
- Verify webhook signatures on every request
- Store private keys in secure secret management systems
- Rotate secrets regularly and have a key rotation plan

**Don't:**
- Store secrets in environment variables in production
- Request organization or admin permissions unless absolutely necessary
- Use long-lived personal access tokens for automation
- Skip signature verification "for simplicity"
- Log or expose tokens in error messages

```typescript
// ✅ Good: Verify webhook signature
import { verify } from "@octokit/webhooks-methods";

export async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  return await verify(secret, payload, signature);
}

// ❌ Bad: Skip verification
app.post("/webhook", (req, res) => {
  // Process webhook without verification - NEVER DO THIS
  processWebhook(req.body);
});
```

### ✅ Input Validation

**Always validate webhook payloads:**

```typescript
// ✅ Good: Validate critical fields
function validatePullRequestPayload(payload: any) {
  if (!payload.pull_request?.number) {
    throw new Error("Invalid payload: missing PR number");
  }
  if (!payload.repository?.full_name) {
    throw new Error("Invalid payload: missing repository name");
  }
  if (!payload.installation?.id) {
    throw new Error("Invalid payload: missing installation ID");
  }
  return {
    prNumber: payload.pull_request.number,
    repoFullName: payload.repository.full_name,
    installationId: payload.installation.id,
  };
}

// ❌ Bad: Trust payload implicitly
function processWebhook(payload: any) {
  const prNumber = payload.pull_request.number; // Could be undefined
  const repoName = payload.repository.full_name; // Could be undefined
  // ... dangerous operations
}
```

## Performance Best Practices

### ✅ Rate Limit Management

**Implement proactive rate limit handling:**

```typescript
// ✅ Good: Check rate limits before expensive operations
async function withRateLimitCheck<T>(
  octokit: Octokit,
  operation: () => Promise<T>
): Promise<T | null> {
  const { data: rateLimit } = await octokit.rateLimit.get();

  if (rateLimit.resources.core.remaining < 100) {
    console.warn(
      `Rate limit low: ${rateLimit.resources.core.remaining}/5000 remaining`
    );
    // Consider skipping non-critical operations
    return null;
  }

  return await operation();
}

// ❌ Bad: Ignore rate limits until you hit them
async function makeLotsOfCalls(octokit: Octokit, repos: string[]) {
  for (const repo of repos) {
    await octokit.repos.get({ owner: "org", repo }); // Will eventually hit rate limit
  }
}
```

### ✅ Efficient API Usage

**Batch operations and use GraphQL for complex queries:**

```typescript
// ✅ Good: Use GraphQL for complex data fetching
const GET_PR_INFO = `
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        id
        title
        author { login }
        files(first: 50) {
          nodes { path }
        }
        reviews(first: 10, states: [APPROVED, CHANGES_REQUESTED]) {
          nodes {
            author { login }
            state
          }
        }
      }
    }
  }
`;

// ❌ Bad: Multiple REST API calls for same data
async function getPRInfoRest(octokit: Octokit, owner: string, repo: string, prNumber: number) {
  const pr = await octokit.pulls.get({ owner, repo, pull_number: prNumber });
  const files = await octokit.pulls.listFiles({ owner, repo, pull_number: prNumber });
  const reviews = await octokit.pulls.listReviews({ owner, repo, pull_number: prNumber });
  // Multiple API calls for related data
}
```

## Error Handling Best Practices

### ✅ Graceful Degradation

**Handle errors without breaking the entire workflow:**

```typescript
// ✅ Good: Graceful error handling
async function processWebhookWithGracefulHandling(payload: any) {
  const tasks = [
    () => addLabels(payload),
    () => assignReviewers(payload),
    () => sendNotification(payload),
  ];

  const results = await Promise.allSettled(tasks.map(task => task()));

  results.forEach((result, index) => {
    if (result.status === 'rejected') {
      console.error(`Task ${index} failed:`, result.reason);
      // Log error but continue with other tasks
    }
  });
}

// ❌ Bad: All-or-nothing error handling
async function processWebhookRigid(payload: any) {
  await addLabels(payload);      // If this fails, nothing else runs
  await assignReviewers(payload); // If this fails, notification doesn't run
  await sendNotification(payload);
}
```

### ✅ Specific Error Messages

**Provide actionable error information:**

```typescript
// ✅ Good: Specific error context
class GitHubAppError extends Error {
  constructor(
    message: string,
    public readonly operation: string,
    public readonly githubError?: any
  ) {
    super(message);
    this.name = 'GitHubAppError';
  }
}

async function addLabelsSafely(octokit: Octokit, owner: string, repo: string, prNumber: number, labels: string[]) {
  try {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: prNumber,
      labels,
    });
  } catch (error: any) {
    throw new GitHubAppError(
      `Failed to add labels [${labels.join(', ')}] to PR #${prNumber} in ${owner}/${repo}`,
      'addLabels',
      error
    );
  }
}

// ❌ Bad: Generic error messages
async function addLabels(octokit: Octokit, params: any) {
  try {
    await octokit.issues.addLabels(params);
  } catch (error) {
    throw new Error('Something went wrong'); // Not helpful!
  }
}
```

## Code Organization Best Practices

### ✅ Modular Architecture

**Separate concerns into focused modules:**

```typescript
// ✅ Good: Organized by responsibility
// src/
//   auth/
//     app-auth.ts
//     installation-auth.ts
//   webhooks/
//     handlers/
//       pull-request.ts
//       issues.ts
//     webhook-router.ts
//   services/
//     labeling-service.ts
//     reviewer-service.ts
//   utils/
//     github-client.ts
//     validation.ts

// Example modular service
export class LabelingService {
  constructor(private octokit: Octokit) {}

  async labelPullRequest(payload: PullRequestPayload): Promise<void> {
    const labels = this.determineLabels(payload);
    if (labels.length === 0) return;

    await this.octokit.issues.addLabels({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: payload.pull_request.number,
      labels,
    });
  }

  private determineLabels(payload: PullRequestPayload): string[] {
    // Focused logic for label determination
  }
}
```

### ✅ Configuration Management

**Externalize configuration and make it environment-aware:**

```typescript
// ✅ Good: Centralized configuration
interface AppConfig {
  github: {
    appId: string;
    privateKey: string;
    clientId: string;
    clientSecret: string;
  };
  features: {
    autoLabeling: boolean;
    reviewerAssignment: boolean;
    qualityChecks: boolean;
  };
  limits: {
    maxReviewers: number;
    processingTimeoutMs: number;
  };
}

export function loadConfig(): AppConfig {
  return {
    github: {
      appId: requireEnv('GITHUB_APP_ID'),
      privateKey: requireEnv('GITHUB_PRIVATE_KEY'),
      clientId: requireEnv('GITHUB_CLIENT_ID'),
      clientSecret: requireEnv('GITHUB_CLIENT_SECRET'),
    },
    features: {
      autoLabeling: parseBoolean(process.env.FEATURE_AUTO_LABELING, true),
      reviewerAssignment: parseBoolean(process.env.FEATURE_REVIEWER_ASSIGNMENT, true),
      qualityChecks: parseBoolean(process.env.FEATURE_QUALITY_CHECKS, false),
    },
    limits: {
      maxReviewers: parseInt(process.env.MAX_REVIEWERS || '3'),
      processingTimeoutMs: parseInt(process.env.PROCESSING_TIMEOUT_MS || '30000'),
    },
  };
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}
```

## Testing Best Practices

### ✅ Mock GitHub API Calls

**Test your logic without hitting GitHub's API:**

```typescript
// ✅ Good: Mock API responses for testing
import { jest } from '@jest/globals';

describe('LabelingService', () => {
  let mockOctokit: any;
  let service: LabelingService;

  beforeEach(() => {
    mockOctokit = {
      issues: {
        addLabels: jest.fn().mockResolvedValue({ data: {} }),
      },
    };
    service = new LabelingService(mockOctokit);
  });

  test('adds enhancement label for feat commits', async () => {
    const payload = {
      pull_request: {
        title: 'feat: add user authentication',
        number: 123,
      },
      repository: {
        owner: { login: 'testorg' },
        name: 'testrepo',
      },
    };

    await service.labelPullRequest(payload);

    expect(mockOctokit.issues.addLabels).toHaveBeenCalledWith({
      owner: 'testorg',
      repo: 'testrepo',
      issue_number: 123,
      labels: ['enhancement'],
    });
  });
});
```

### ✅ Integration Testing with Webhooks

**Test webhook handling with realistic payloads:**

```typescript
// ✅ Good: Test with real webhook payloads
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Webhook Integration', () => {
  test('processes pull request opened event', async () => {
    // Use actual GitHub webhook payloads for testing
    const payloadJson = readFileSync(
      join(__dirname, 'fixtures/pull-request-opened.json'),
      'utf8'
    );
    const payload = JSON.parse(payloadJson);

    const result = await processWebhook('pull_request', 'opened', payload);

    expect(result.success).toBe(true);
    expect(result.actions).toContain('labeled');
  });
});
```

## Monitoring & Observability

### ✅ Structured Logging

**Use consistent, searchable log formats:**

```typescript
// ✅ Good: Structured logging with context
import { createLogger } from 'winston';

const logger = createLogger({
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
});

export function logWebhookEvent(eventType: string, payload: any, action: string) {
  logger.info('Webhook processed', {
    event: eventType,
    action,
    repository: payload.repository?.full_name,
    actor: payload.sender?.login,
    pullRequest: payload.pull_request?.number,
    installation: payload.installation?.id,
    timestamp: new Date().toISOString(),
  });
}

// ❌ Bad: Inconsistent string logging
console.log(`Processing ${eventType} for ${payload.repository?.full_name}`);
console.log(`PR number: ${payload.pull_request?.number}`);
```

### ✅ Metrics Collection

**Track key performance indicators:**

```typescript
// ✅ Good: Metrics tracking
interface AppMetrics {
  webhookCount: Map<string, number>;
  processingTime: Map<string, number[]>;
  errorCount: Map<string, number>;
}

export class MetricsCollector {
  private metrics: AppMetrics = {
    webhookCount: new Map(),
    processingTime: new Map(),
    errorCount: new Map(),
  };

  recordWebhookProcessed(eventType: string, processingTimeMs: number) {
    // Count events
    const currentCount = this.metrics.webhookCount.get(eventType) || 0;
    this.metrics.webhookCount.set(eventType, currentCount + 1);

    // Track processing time
    const times = this.metrics.processingTime.get(eventType) || [];
    times.push(processingTimeMs);
    this.metrics.processingTime.set(eventType, times);
  }

  recordError(eventType: string, error: Error) {
    const currentErrors = this.metrics.errorCount.get(eventType) || 0;
    this.metrics.errorCount.set(eventType, currentErrors + 1);
  }

  getMetricsSummary() {
    return {
      totalWebhooks: Array.from(this.metrics.webhookCount.values()).reduce((a, b) => a + b, 0),
      averageProcessingTime: this.calculateAverageProcessingTime(),
      errorRate: this.calculateErrorRate(),
    };
  }
}
```

## Deployment Best Practices

### ✅ Health Checks

**Implement health endpoints for monitoring:**

```typescript
// ✅ Good: Comprehensive health checks
app.get('/health', async (req, res) => {
  const checks = {
    github_api: await checkGitHubAPIAccess(),
    database: await checkDatabaseConnection(),
    secrets: checkRequiredSecrets(),
    timestamp: new Date().toISOString(),
  };

  const healthy = Object.values(checks).every(check =>
    typeof check === 'boolean' ? check : check.status === 'ok'
  );

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    checks,
  });
});
```

### ✅ Graceful Shutdowns

**Handle shutdown signals properly:**

```typescript
// ✅ Good: Graceful shutdown handling
let server: Server;

function gracefulShutdown(signal: string) {
  console.log(`Received ${signal}, starting graceful shutdown`);

  server.close(() => {
    console.log('HTTP server closed');

    // Clean up resources
    database.disconnect();

    process.exit(0);
  });

  // Force exit if graceful shutdown takes too long
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
```

## Common Anti-patterns to Avoid

### ❌ Over-requesting Permissions

```typescript
// ❌ Bad: Requesting unnecessary permissions
const permissions = {
  actions: 'write',        // Do you really need to modify workflows?
  administration: 'write', // This is very powerful - avoid unless necessary
  contents: 'write',       // Read-only might be sufficient
  metadata: 'read',        // Usually needed
  pull_requests: 'write',  // Necessary for PR bots
};

// ✅ Good: Minimal permissions for PR labeling bot
const permissions = {
  metadata: 'read',
  pull_requests: 'write',
  issues: 'write', // For labels
};
```

### ❌ Synchronous Webhook Processing

```typescript
// ❌ Bad: Blocking webhook processing
app.post('/webhook', (req, res) => {
  processWebhook(req.body); // This might take a long time
  res.send('OK'); // Response delayed by processing
});

// ✅ Good: Asynchronous processing
app.post('/webhook', (req, res) => {
  // Acknowledge webhook immediately
  res.send('OK');

  // Process asynchronously
  processWebhookAsync(req.body).catch(error => {
    logger.error('Webhook processing failed', error);
  });
});
```

### ❌ Hardcoded Configuration

```typescript
// ❌ Bad: Hardcoded values
const MAX_REVIEWERS = 3;
const LABELS = ['needs-review', 'enhancement'];
const WEBHOOK_URL = 'https://myapp.com/webhook';

// ✅ Good: Configurable values
const config = {
  maxReviewers: parseInt(process.env.MAX_REVIEWERS || '3'),
  labels: process.env.DEFAULT_LABELS?.split(',') || ['needs-review'],
  webhookUrl: process.env.WEBHOOK_URL || 'https://myapp.com/webhook',
};
```