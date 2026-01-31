# GitHub App Anti-patterns

Deep dive into common mistakes and how to avoid them when building GitHub Apps.

## Security Anti-patterns

### Over-privileged Permissions

**Problem**: Requesting more permissions than needed "just in case."

```yaml
# ❌ Bad: Kitchen sink permissions
permissions:
  actions: write              # Can modify workflows
  administration: write       # Can change repo settings
  contents: write            # Can modify code
  deployments: write         # Can manage deployments
  environments: write        # Can modify environments
  issues: write              # Can manage issues
  metadata: read             # Actually needed
  pull_requests: write       # Actually needed
  repository_hooks: write    # Can modify webhooks
  statuses: write           # Can set commit statuses
```

```yaml
# ✅ Good: Minimal permissions for PR bot
permissions:
  metadata: read           # Read repo metadata
  pull_requests: write     # Manage PRs
  issues: write           # Add labels (issues API)
```

**Impact**:
- Security risk if app is compromised
- Users reluctant to install over-privileged apps
- Harder to get organization approval

**Fix**: Start with minimal permissions, add only when needed.

### Weak Webhook Signature Verification

**Problem**: Skipping or incorrectly implementing signature verification.

```typescript
// ❌ Bad: No verification
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  processWebhook(req.body);
  res.sendStatus(200);
});

// ❌ Bad: Incorrect verification
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-hub-signature-256'];
  if (signature !== `sha256=${crypto.createHash('sha256').update(req.body).digest('hex')}`) {
    return res.status(401).send('Unauthorized');
  }
  // Wrong: Should use HMAC with secret, not plain hash
});
```

```typescript
// ✅ Good: Proper HMAC verification
import { verify } from "@octokit/webhooks-methods";

app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const signature = req.headers['x-hub-signature-256'];
  const payload = req.body.toString();

  const isValid = await verify(process.env.WEBHOOK_SECRET, payload, signature);
  if (!isValid) {
    return res.status(401).send('Unauthorized');
  }

  processWebhook(JSON.parse(payload));
  res.sendStatus(200);
});
```

### Insecure Secret Management

**Problem**: Storing secrets in easily accessible locations.

```typescript
// ❌ Bad: Hardcoded secrets
const config = {
  appId: 123456,
  privateKey: `-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...`,
  webhookSecret: 'my-super-secret-key'
};

// ❌ Bad: Secrets in environment without protection
const privateKey = process.env.GITHUB_PRIVATE_KEY; // Plain text in env
```

```typescript
// ✅ Good: Secure secret management
import { SecretsManager } from 'aws-sdk';

async function loadSecrets() {
  const secretsManager = new SecretsManager();
  const secret = await secretsManager.getSecretValue({
    SecretId: 'github-app-secrets'
  }).promise();

  return JSON.parse(secret.SecretString);
}

// ✅ Good: Use environment with validation
function requireSecret(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required secret: ${name}`);
  }
  return value;
}
```

## Performance Anti-patterns

### Synchronous Webhook Processing

**Problem**: Blocking webhook responses while performing heavy operations.

```typescript
// ❌ Bad: Synchronous processing
app.post('/webhook', async (req, res) => {
  const payload = req.body;

  // All of these block the webhook response
  await labelPullRequest(payload);
  await assignReviewers(payload);
  await runQualityChecks(payload);
  await sendSlackNotification(payload);

  res.sendStatus(200); // GitHub waited for all operations
});
```

```typescript
// ✅ Good: Async processing with immediate response
app.post('/webhook', async (req, res) => {
  const payload = req.body;

  // Acknowledge webhook immediately
  res.sendStatus(200);

  // Process asynchronously
  setImmediate(async () => {
    try {
      await Promise.allSettled([
        labelPullRequest(payload),
        assignReviewers(payload),
        runQualityChecks(payload),
        sendSlackNotification(payload),
      ]);
    } catch (error) {
      logger.error('Webhook processing failed', { error, payload });
    }
  });
});
```

### Rate Limit Ignorance

**Problem**: Making API calls without considering rate limits.

```typescript
// ❌ Bad: Unbounded API calls
async function processRepositories(repos: Repository[]) {
  for (const repo of repos) {
    // Could easily exceed rate limits
    await octokit.repos.get({ owner: repo.owner, repo: repo.name });
    await octokit.issues.listForRepo({ owner: repo.owner, repo: repo.name });
    await octokit.pulls.list({ owner: repo.owner, repo: repo.name });
  }
}
```

```typescript
// ✅ Good: Rate limit aware processing
import pLimit from 'p-limit';

async function processRepositoriesWithRateLimit(repos: Repository[]) {
  // Limit concurrent API calls
  const limit = pLimit(5);

  const results = await Promise.allSettled(
    repos.map(repo => limit(async () => {
      // Check rate limit before expensive operations
      const { data: rateLimit } = await octokit.rateLimit.get();

      if (rateLimit.resources.core.remaining < 100) {
        logger.warn('Rate limit low, skipping non-critical operations');
        return null;
      }

      return await octokit.repos.get({
        owner: repo.owner,
        repo: repo.name
      });
    }))
  );

  return results.filter(result =>
    result.status === 'fulfilled' && result.value !== null
  );
}
```

### Memory Leaks in Long-running Apps

**Problem**: Not cleaning up event listeners and cached data.

```typescript
// ❌ Bad: Memory leaks
class WebhookProcessor {
  private handlers = new Map();

  constructor() {
    // Event listeners never removed
    process.on('SIGTERM', this.handleShutdown);
    process.on('SIGINT', this.handleShutdown);
  }

  processWebhook(payload: any) {
    // Cache grows indefinitely
    this.handlers.set(payload.installation.id, new Date());

    // Create new listeners without cleanup
    setTimeout(() => {
      this.doSomething(payload);
    }, 1000);
  }
}
```

```typescript
// ✅ Good: Proper cleanup
class WebhookProcessor {
  private handlers = new Map();
  private timers = new Set<NodeJS.Timeout>();

  constructor() {
    // Bound methods for proper cleanup
    this.handleShutdown = this.handleShutdown.bind(this);
    process.on('SIGTERM', this.handleShutdown);
    process.on('SIGINT', this.handleShutdown);
  }

  processWebhook(payload: any) {
    // Implement cache eviction
    this.cleanupOldHandlers();
    this.handlers.set(payload.installation.id, new Date());

    // Track timers for cleanup
    const timer = setTimeout(() => {
      this.doSomething(payload);
      this.timers.delete(timer);
    }, 1000);
    this.timers.add(timer);
  }

  private cleanupOldHandlers() {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    for (const [id, timestamp] of this.handlers) {
      if (timestamp.getTime() < oneHourAgo) {
        this.handlers.delete(id);
      }
    }
  }

  private handleShutdown() {
    // Clean up all resources
    this.timers.forEach(timer => clearTimeout(timer));
    this.handlers.clear();

    process.removeListener('SIGTERM', this.handleShutdown);
    process.removeListener('SIGINT', this.handleShutdown);
  }
}
```

## Integration Anti-patterns

### Polling Instead of Webhooks

**Problem**: Inefficient API usage by polling for changes instead of using webhooks.

```typescript
// ❌ Bad: Polling for new PRs
setInterval(async () => {
  const repos = await getMonitoredRepositories();

  for (const repo of repos) {
    const prs = await octokit.pulls.list({
      owner: repo.owner,
      repo: repo.name,
      state: 'open',
      sort: 'updated',
      direction: 'desc'
    });

    for (const pr of prs.data) {
      if (isNewPR(pr)) {
        await processPullRequest(pr);
      }
    }
  }
}, 60000); // Check every minute - inefficient!
```

```typescript
// ✅ Good: Webhook-driven processing
app.on('pull_request.opened', async ({ payload }) => {
  await processPullRequest(payload.pull_request);
});

app.on('pull_request.synchronize', async ({ payload }) => {
  await processPullRequestUpdate(payload.pull_request);
});
```

### Not Handling App Uninstalls

**Problem**: Continuing to process events after app is uninstalled.

```typescript
// ❌ Bad: No uninstall handling
app.on('pull_request.opened', async ({ payload }) => {
  // Process without checking if app is still installed
  await processNewPR(payload);
});
```

```typescript
// ✅ Good: Handle installation lifecycle
const installedApps = new Set<number>();

app.on('installation.created', ({ payload }) => {
  installedApps.add(payload.installation.id);
  logger.info('App installed', { installationId: payload.installation.id });
});

app.on('installation.deleted', ({ payload }) => {
  installedApps.delete(payload.installation.id);
  logger.info('App uninstalled', { installationId: payload.installation.id });

  // Clean up any stored data for this installation
  cleanupInstallationData(payload.installation.id);
});

app.on('pull_request.opened', async ({ payload }) => {
  if (!installedApps.has(payload.installation.id)) {
    logger.warn('Received webhook for uninstalled app', {
      installationId: payload.installation.id
    });
    return;
  }

  await processNewPR(payload);
});
```

### Assuming Webhook Order

**Problem**: Expecting webhooks to arrive in chronological order.

```typescript
// ❌ Bad: Assuming order
let lastProcessedPR: number = 0;

app.on('pull_request', async ({ payload }) => {
  if (payload.pull_request.number <= lastProcessedPR) {
    // Wrong assumption - webhooks may arrive out of order
    return;
  }

  lastProcessedPR = payload.pull_request.number;
  await processPR(payload);
});
```

```typescript
// ✅ Good: Idempotent processing
const processedEvents = new Map<string, Date>();

app.on('pull_request', async ({ payload }) => {
  const eventKey = `${payload.repository.id}:${payload.pull_request.number}:${payload.action}`;
  const eventTime = new Date(payload.pull_request.updated_at);

  // Check if we've already processed a newer event
  const lastProcessed = processedEvents.get(eventKey);
  if (lastProcessed && lastProcessed >= eventTime) {
    logger.debug('Skipping older event', { eventKey, eventTime, lastProcessed });
    return;
  }

  processedEvents.set(eventKey, eventTime);
  await processPR(payload);
});
```

## Architecture Anti-patterns

### Monolithic Webhook Handlers

**Problem**: Single handler processing all webhook events.

```typescript
// ❌ Bad: Monolithic handler
app.on('*', async ({ name, payload }) => {
  if (name === 'pull_request.opened') {
    // Handle PR opened
    if (payload.pull_request.title.startsWith('feat:')) {
      // Add enhancement label
    }
    if (payload.pull_request.changed_files > 10) {
      // Request additional review
    }
    // ... more logic
  } else if (name === 'issues.opened') {
    // Handle issue opened
    if (payload.issue.title.includes('bug')) {
      // Add bug label
    }
    // ... more logic
  }
  // ... dozens more conditions
});
```

```typescript
// ✅ Good: Modular handlers
import { PullRequestService } from './services/pull-request';
import { IssueService } from './services/issue';

const prService = new PullRequestService();
const issueService = new IssueService();

app.on('pull_request.opened', prService.handleOpened.bind(prService));
app.on('pull_request.edited', prService.handleEdited.bind(prService));
app.on('issues.opened', issueService.handleOpened.bind(issueService));
app.on('issues.labeled', issueService.handleLabeled.bind(issueService));
```

### Direct Database Access in Webhooks

**Problem**: Making database calls directly in webhook handlers.

```typescript
// ❌ Bad: Direct database access
app.on('pull_request.opened', async ({ payload }) => {
  // Database operations in webhook handler
  const user = await db.users.findOne({ githubId: payload.sender.id });
  if (!user) {
    await db.users.create({
      githubId: payload.sender.id,
      username: payload.sender.login
    });
  }

  await db.pullRequests.create({
    number: payload.pull_request.number,
    repository: payload.repository.full_name,
    userId: user.id
  });

  // More database operations...
});
```

```typescript
// ✅ Good: Queue-based processing
import { Queue } from 'bull';

const webhookQueue = new Queue('webhook processing');

app.on('pull_request.opened', async ({ payload }) => {
  // Acknowledge webhook quickly
  await webhookQueue.add('process-pr-opened', payload, {
    attempts: 3,
    backoff: 'exponential'
  });
});

// Separate worker processes database operations
webhookQueue.process('process-pr-opened', async (job) => {
  const payload = job.data;

  // Database operations in background worker
  await userService.ensureUserExists(payload.sender);
  await pullRequestService.create(payload.pull_request);
});
```

## Testing Anti-patterns

### No Webhook Signature Testing

**Problem**: Not testing webhook signature verification.

```typescript
// ❌ Bad: No signature testing
describe('Webhook handler', () => {
  test('processes pull request opened', async () => {
    const payload = { /* webhook payload */ };

    const response = await request(app)
      .post('/webhook')
      .send(payload)
      .expect(200);
  });
});
```

```typescript
// ✅ Good: Test signature verification
import crypto from 'crypto';

describe('Webhook handler', () => {
  const webhookSecret = 'test-secret';

  function signPayload(payload: any): string {
    const body = JSON.stringify(payload);
    return `sha256=${crypto
      .createHmac('sha256', webhookSecret)
      .update(body, 'utf8')
      .digest('hex')}`;
  }

  test('rejects unsigned webhooks', async () => {
    const payload = { /* webhook payload */ };

    await request(app)
      .post('/webhook')
      .send(payload)
      .expect(401);
  });

  test('processes correctly signed webhook', async () => {
    const payload = { /* webhook payload */ };
    const signature = signPayload(payload);

    await request(app)
      .post('/webhook')
      .set('X-Hub-Signature-256', signature)
      .send(payload)
      .expect(200);
  });
});
```

### Not Testing Rate Limit Scenarios

**Problem**: Only testing happy path, ignoring rate limits.

```typescript
// ❌ Bad: Only happy path tests
test('labels pull request', async () => {
  const mockOctokit = {
    issues: {
      addLabels: jest.fn().mockResolvedValue({ data: {} })
    }
  };

  await labelingService.labelPR(mockPayload);
  expect(mockOctokit.issues.addLabels).toHaveBeenCalled();
});
```

```typescript
// ✅ Good: Test error scenarios
describe('LabelingService', () => {
  test('handles rate limit errors gracefully', async () => {
    const rateLimitError = new Error('API rate limit exceeded');
    rateLimitError.status = 403;

    const mockOctokit = {
      issues: {
        addLabels: jest.fn().mockRejectedValue(rateLimitError)
      }
    };

    const result = await labelingService.labelPR(mockPayload);

    expect(result.success).toBe(false);
    expect(result.retryAfter).toBeDefined();
  });

  test('retries on server errors', async () => {
    const serverError = new Error('Internal server error');
    serverError.status = 500;

    const mockOctokit = {
      issues: {
        addLabels: jest.fn()
          .mockRejectedValueOnce(serverError)
          .mockResolvedValue({ data: {} })
      }
    };

    const result = await labelingService.labelPR(mockPayload);

    expect(result.success).toBe(true);
    expect(mockOctokit.issues.addLabels).toHaveBeenCalledTimes(2);
  });
});
```

## Recovery Strategies

### From Security Issues
1. **Immediate**: Regenerate secrets, audit access logs
2. **Short-term**: Review and minimize permissions
3. **Long-term**: Implement automated security scanning

### From Performance Issues
1. **Immediate**: Add circuit breakers, scale infrastructure
2. **Short-term**: Implement proper rate limiting and caching
3. **Long-term**: Redesign for async processing

### From Integration Issues
1. **Immediate**: Add health checks and monitoring
2. **Short-term**: Implement proper error handling
3. **Long-term**: Add end-to-end testing and staging environments

## See Also

- [best-practices.md](../examples/best-practices.md) - Positive patterns and implementation examples
- [error-handling.md](error-handling.md) - Comprehensive error handling strategies
- [testing.md](testing.md) - Testing strategies and frameworks
- [observability.md](observability.md) - Monitoring and alerting best practices