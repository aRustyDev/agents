# GitHub App Testing Guide

Comprehensive testing strategies for GitHub Apps, from local development to production validation.

## Testing Strategy Overview

| Test Type | Purpose | Tools | When to Run |
|-----------|---------|-------|-------------|
| **Unit Tests** | Test individual functions | Jest, Vitest | Every commit |
| **Integration Tests** | Test webhook processing | MSW, Nock | Pre-deployment |
| **End-to-End Tests** | Test full app behavior | GitHub API, Test repos | Release validation |
| **Local Testing** | Development workflow | smee.io, ngrok | During development |

## Local Development Testing

### 1. Webhook Proxy with smee.io

**Setup smee.io channel:**
```bash
# Create a new channel
curl -X POST https://smee.io/new

# Use the returned URL in your GitHub App webhook settings
# Example: https://smee.io/abc123
```

**Start webhook proxy:**
```bash
# Forward to local development server
npx smee -u https://smee.io/abc123 -t http://localhost:3000/webhook

# For Cloudflare Workers development
npx smee -u https://smee.io/abc123 -t http://localhost:8787/webhook
```

### 2. Alternative: ngrok

```bash
# Expose local server
ngrok http 3000

# Use the HTTPS URL for webhook endpoint
# Example: https://abc123.ngrok.io/webhook
```

### 3. Environment Configuration

```bash
# .env.local
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your_webhook_secret
NODE_ENV=development
```

## Unit Testing Patterns

### Testing Authentication

```typescript
// tests/auth.test.ts
import { createAppAuth } from "@octokit/auth-app";
import { createInstallationOctokit } from "../src/auth";

// Mock the auth module
jest.mock("@octokit/auth-app");

describe("Authentication", () => {
  const mockEnv = {
    GITHUB_APP_ID: "123456",
    GITHUB_PRIVATE_KEY: "fake-key",
    GITHUB_WEBHOOK_SECRET: "secret",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("creates installation Octokit with correct auth", async () => {
    const mockAuth = jest.fn().mockResolvedValue({ token: "fake-token" });
    (createAppAuth as jest.Mock).mockReturnValue({ auth: mockAuth });

    const octokit = await createInstallationOctokit(mockEnv, 12345);

    expect(mockAuth).toHaveBeenCalledWith({
      type: "installation",
      installationId: 12345,
    });
  });

  test("handles auth errors gracefully", async () => {
    const mockAuth = jest.fn().mockRejectedValue(new Error("Auth failed"));
    (createAppAuth as jest.Mock).mockReturnValue({ auth: mockAuth });

    await expect(
      createInstallationOctokit(mockEnv, 12345)
    ).rejects.toThrow("Auth failed");
  });
});
```

### Testing Webhook Handlers

```typescript
// tests/webhooks.test.ts
import { Webhooks } from "@octokit/webhooks";
import { createWebhooks } from "../src/webhooks";

// Mock webhook payloads
const mockPRPayload = {
  action: "opened",
  pull_request: {
    number: 123,
    title: "feat: add new feature",
    head: { sha: "abc123" },
  },
  repository: {
    owner: { login: "testorg" },
    name: "testrepo",
  },
  installation: { id: 12345 },
};

describe("Webhook Handlers", () => {
  let webhooks: Webhooks;
  let mockOctokit: any;

  beforeEach(() => {
    mockOctokit = {
      issues: {
        addLabels: jest.fn().mockResolvedValue({}),
        createComment: jest.fn().mockResolvedValue({}),
      },
    };

    webhooks = createWebhooks("test-secret");
  });

  test("labels PR correctly based on title", async () => {
    const handler = jest.fn();
    webhooks.on("pull_request.opened", handler);

    await webhooks.receive({
      id: "123",
      name: "pull_request",
      payload: mockPRPayload,
    });

    expect(handler).toHaveBeenCalledWith(
      expect.objectContaining({
        payload: mockPRPayload,
      })
    );
  });

  test("handles missing installation gracefully", async () => {
    const payloadWithoutInstallation = {
      ...mockPRPayload,
      installation: undefined,
    };

    const handler = jest.fn();
    webhooks.on("pull_request.opened", handler);

    // Should not throw
    await webhooks.receive({
      id: "123",
      name: "pull_request",
      payload: payloadWithoutInstallation,
    });
  });
});
```

## Integration Testing

### Mock GitHub API Responses

```typescript
// tests/integration.test.ts
import nock from "nock";
import { processWebhook } from "../src/app";

describe("Integration Tests", () => {
  afterEach(() => {
    nock.cleanAll();
  });

  test("handles PR opened event end-to-end", async () => {
    // Mock GitHub API responses
    const githubMock = nock("https://api.github.com")
      .post("/app/installations/12345/access_tokens")
      .reply(200, {
        token: "ghs_mock_token",
        expires_at: "2024-01-01T00:00:00Z",
      })
      .post("/repos/testorg/testrepo/issues/123/labels")
      .reply(200, []);

    const webhookPayload = {
      /* mock payload */
    };

    await processWebhook({
      headers: {
        "x-github-event": "pull_request",
        "x-github-delivery": "12345",
        "x-hub-signature-256": "valid-signature",
      },
      body: JSON.stringify(webhookPayload),
    });

    expect(githubMock.isDone()).toBe(true);
  });
});
```

### MSW (Modern Service Worker)

```typescript
// tests/mocks/handlers.ts
import { rest } from "msw";

export const handlers = [
  // Mock installation token endpoint
  rest.post(
    "https://api.github.com/app/installations/:installationId/access_tokens",
    (req, res, ctx) => {
      return res(
        ctx.json({
          token: "ghs_mock_installation_token",
          expires_at: "2024-01-01T00:00:00Z",
        })
      );
    }
  ),

  // Mock adding labels
  rest.post(
    "https://api.github.com/repos/:owner/:repo/issues/:issue_number/labels",
    (req, res, ctx) => {
      return res(ctx.json([]));
    }
  ),

  // Mock creating comments
  rest.post(
    "https://api.github.com/repos/:owner/:repo/issues/:issue_number/comments",
    (req, res, ctx) => {
      return res(
        ctx.json({
          id: 1,
          body: req.body,
          created_at: "2024-01-01T00:00:00Z",
        })
      );
    }
  ),
];
```

## End-to-End Testing

### Test Repository Setup

Create dedicated test repositories:

```bash
# Create test repositories
gh repo create myorg/github-app-test-repo --public
gh repo create myorg/github-app-e2e-tests --private
```

### Automated E2E Tests

```typescript
// tests/e2e/github-app.test.ts
import { Octokit } from "@octokit/rest";

const TEST_REPO = process.env.TEST_REPO || "myorg/github-app-test-repo";
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

describe("GitHub App E2E", () => {
  const octokit = new Octokit({ auth: GITHUB_TOKEN });

  test("app responds to real PR creation", async () => {
    // Create a real PR
    const { data: pr } = await octokit.pulls.create({
      owner: "myorg",
      repo: "github-app-test-repo",
      title: "feat: test PR for E2E testing",
      head: "test-branch",
      base: "main",
      body: "This is a test PR created by automated tests",
    });

    // Wait for webhook processing (app should auto-label)
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Verify the app added labels
    const { data: issue } = await octokit.issues.get({
      owner: "myorg",
      repo: "github-app-test-repo",
      issue_number: pr.number,
    });

    expect(issue.labels.some((l: any) => l.name === "enhancement")).toBe(true);

    // Cleanup
    await octokit.pulls.update({
      owner: "myorg",
      repo: "github-app-test-repo",
      pull_number: pr.number,
      state: "closed",
    });
  });
});
```

## Testing Framework-Specific Patterns

### Testing Probot Apps

```typescript
// tests/probot.test.ts
import { Probot, ProbotOctokit } from "probot";
import app from "../app";

describe("Probot App", () => {
  let probot: Probot;

  beforeEach(() => {
    probot = new Probot({
      githubToken: "test",
      Octokit: ProbotOctokit.defaults({
        retry: { enabled: false },
        throttle: { enabled: false },
      }),
    });

    probot.load(app);
  });

  test("handles pull_request.opened", async () => {
    const mock = jest.fn();

    // Mock GitHub API
    probot.load((app) => {
      app.on("pull_request.opened", mock);
    });

    await probot.receive({
      name: "pull_request",
      id: "123",
      payload: {
        action: "opened",
        // ... payload
      },
    });

    expect(mock).toHaveBeenCalled();
  });
});
```

### Testing Cloudflare Workers

```typescript
// tests/worker.test.ts
import worker from "../src/index";

describe("Cloudflare Worker", () => {
  const env = {
    GITHUB_APP_ID: "123456",
    GITHUB_PRIVATE_KEY: "test-key",
    GITHUB_WEBHOOK_SECRET: "test-secret",
  };

  test("handles webhook requests", async () => {
    const request = new Request("https://example.com/webhook", {
      method: "POST",
      headers: {
        "x-github-event": "pull_request",
        "x-github-delivery": "12345",
        "content-type": "application/json",
      },
      body: JSON.stringify({ action: "opened" }),
    });

    const response = await worker.fetch(request, env);
    expect(response.status).toBe(200);
  });
});
```

## Mock Webhook Payloads

### Complete Payload Examples

```typescript
// tests/fixtures/webhooks.ts
export const pullRequestOpened = {
  action: "opened",
  number: 1,
  pull_request: {
    id: 1,
    number: 1,
    title: "feat: add new feature",
    body: "This adds a new feature",
    state: "open",
    head: {
      sha: "abc123def456",
      ref: "feature-branch",
      repo: {
        id: 123456,
        name: "testrepo",
        full_name: "testorg/testrepo",
      },
    },
    base: {
      sha: "def456ghi789",
      ref: "main",
      repo: {
        id: 123456,
        name: "testrepo",
        full_name: "testorg/testrepo",
      },
    },
    user: {
      id: 1,
      login: "testuser",
      type: "User",
    },
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  repository: {
    id: 123456,
    name: "testrepo",
    full_name: "testorg/testrepo",
    owner: {
      id: 1,
      login: "testorg",
      type: "Organization",
    },
  },
  installation: {
    id: 12345,
    account: {
      id: 1,
      login: "testorg",
      type: "Organization",
    },
  },
  sender: {
    id: 1,
    login: "testuser",
    type: "User",
  },
};

export const issueOpened = {
  action: "opened",
  issue: {
    id: 1,
    number: 1,
    title: "Test issue",
    body: "This is a test issue",
    state: "open",
    user: {
      id: 1,
      login: "testuser",
      type: "User",
    },
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  repository: {
    id: 123456,
    name: "testrepo",
    full_name: "testorg/testrepo",
    owner: {
      id: 1,
      login: "testorg",
      type: "Organization",
    },
  },
  installation: {
    id: 12345,
  },
  sender: {
    id: 1,
    login: "testuser",
    type: "User",
  },
};
```

## Testing Checklist

### Pre-Deployment Tests

- [ ] **Unit tests** pass for all handlers
- [ ] **Authentication** works with test credentials
- [ ] **Webhook signature verification** prevents unauthorized requests
- [ ] **Error handling** gracefully manages API failures
- [ ] **Rate limiting** respects GitHub API limits
- [ ] **Permissions** are validated before API calls

### Production Validation

- [ ] **Installation** works on test repository
- [ ] **Webhooks** are delivered and processed
- [ ] **Events** trigger expected behaviors
- [ ] **Logs** are captured for debugging
- [ ] **Health checks** respond correctly
- [ ] **Rollback plan** is tested and ready

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test GitHub App

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test

      - name: Run integration tests
        run: npm run test:integration
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Test deployment build
        run: npm run build

  e2e:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        run: npm run deploy:staging
        env:
          CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          GITHUB_TOKEN: ${{ secrets.E2E_GITHUB_TOKEN }}
          TEST_REPO: ${{ vars.E2E_TEST_REPO }}
```

## Troubleshooting Test Issues

### Common Test Failures

| Issue | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid or expired token | Regenerate app credentials |
| `Webhook not received` | Firewall or routing issue | Check smee.io/ngrok configuration |
| `Signature verification failed` | Wrong webhook secret | Verify `GITHUB_WEBHOOK_SECRET` |
| `Installation not found` | App not installed on test repo | Install app on test repository |
| `Permission denied` | Missing permissions | Update app permissions in GitHub |

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
export NODE_DEBUG=octokit:request

# Probot debug mode
export LOG_LEVEL=trace

# GitHub API debugging
export ACTIONS_RUNNER_DEBUG=true
```

## Testing Tools Summary

| Tool | Purpose | Best For |
|------|---------|----------|
| **Jest** | Unit testing framework | Testing individual functions |
| **MSW** | API mocking | Integration tests |
| **Nock** | HTTP request mocking | Legacy integration tests |
| **smee.io** | Webhook proxy | Local development |
| **ngrok** | Tunnel to localhost | Alternative to smee.io |
| **Probot Test Framework** | Probot-specific testing | Testing Probot apps |

## Cross-References

- [../SKILL.md#troubleshooting](../SKILL.md#troubleshooting) - General troubleshooting
- [webhooks.md](webhooks.md) - Webhook event details
- [permissions.md](permissions.md) - Permission testing strategies
- [octokit.md](octokit.md) - API client testing patterns