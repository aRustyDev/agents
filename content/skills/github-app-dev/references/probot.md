# Probot Framework Patterns

Probot is a framework for building GitHub Apps in Node.js. It handles authentication, webhook routing, and provides a simplified API.

## When to Use Probot

| Use Probot | Use Raw Octokit |
|------------|-----------------|
| Simple bots with straightforward logic | Complex apps with custom requirements |
| Quick prototypes | Cloudflare Workers (Probot requires Node.js) |
| Standard hosting (Vercel, Glitch, etc.) | Edge deployment |
| Learning GitHub Apps | Fine-grained control over auth |
| Open source bots | Multi-tenant SaaS apps |

## Installation

```bash
# Create new Probot app
npx create-probot-app my-app

# Or add to existing project
npm install probot
```

## Basic Structure

```typescript
// src/index.ts
import { Probot } from "probot";

export default (app: Probot) => {
  // Event handlers go here
  app.on("issues.opened", async (context) => {
    // Handle event
  });
};
```

## Event Handling

### Single Event

```typescript
app.on("pull_request.opened", async (context) => {
  const pr = context.payload.pull_request;
  console.log(`PR #${pr.number}: ${pr.title}`);
});
```

### Multiple Events

```typescript
app.on(
  ["pull_request.opened", "pull_request.synchronize"],
  async (context) => {
    // Runs for both events
  }
);
```

### Wildcard Events

```typescript
// All pull_request events
app.on("pull_request", async (context) => {
  console.log(`Action: ${context.payload.action}`);
});

// All events (use sparingly)
app.onAny(async (context) => {
  console.log(`Event: ${context.name}`);
});
```

## Context Object

The `context` object provides:

```typescript
app.on("issues.opened", async (context) => {
  // Payload from webhook
  const issue = context.payload.issue;
  const repo = context.payload.repository;
  const sender = context.payload.sender;

  // Pre-authenticated Octokit
  const octokit = context.octokit;

  // Helper for repo/issue context
  const issueParams = context.issue({ body: "Hello!" });
  // Returns: { owner, repo, issue_number, body: "Hello!" }

  const repoParams = context.repo({ path: "README.md" });
  // Returns: { owner, repo, path: "README.md" }

  // Logging
  context.log.info("Processing issue");
  context.log.error("Something went wrong");
});
```

## Common Patterns

### Comment on Issues/PRs

```typescript
app.on("issues.opened", async (context) => {
  const comment = context.issue({
    body: "Thanks for opening this issue!",
  });
  await context.octokit.issues.createComment(comment);
});
```

### Add Labels

```typescript
app.on("pull_request.opened", async (context) => {
  const { title } = context.payload.pull_request;
  const labels: string[] = [];

  if (title.match(/^feat/i)) labels.push("enhancement");
  if (title.match(/^fix/i)) labels.push("bug");
  if (title.match(/^docs/i)) labels.push("documentation");

  if (labels.length > 0) {
    await context.octokit.issues.addLabels(
      context.issue({ labels })
    );
  }
});
```

### Create Check Run

```typescript
app.on("pull_request.opened", async (context) => {
  const { head } = context.payload.pull_request;

  await context.octokit.checks.create(
    context.repo({
      name: "My Check",
      head_sha: head.sha,
      status: "completed",
      conclusion: "success",
      output: {
        title: "Check Passed",
        summary: "All validations passed",
      },
    })
  );
});
```

### Request Reviewers

```typescript
app.on("pull_request.opened", async (context) => {
  const reviewers = ["teammate1", "teammate2"];

  await context.octokit.pulls.requestReviewers(
    context.pullRequest({ reviewers })
  );
});
```

### Read Config File

```typescript
app.on("push", async (context) => {
  // Reads .github/my-app.yml
  const config = await context.config("my-app.yml");

  if (config) {
    console.log("Config:", config);
  } else {
    console.log("No config file found");
  }
});

// With defaults
app.on("push", async (context) => {
  const config = await context.config("my-app.yml", {
    autoLabel: true,
    labels: ["triage"],
  });
});
```

### Read File Contents

```typescript
app.on("pull_request.opened", async (context) => {
  try {
    const { data } = await context.octokit.repos.getContent(
      context.repo({
        path: "package.json",
        ref: context.payload.pull_request.head.ref,
      })
    );

    if ("content" in data) {
      const content = Buffer.from(data.content, "base64").toString();
      const pkg = JSON.parse(content);
      console.log("Package version:", pkg.version);
    }
  } catch (error) {
    // File doesn't exist
  }
});
```

### Get PR Files

```typescript
app.on("pull_request.opened", async (context) => {
  const files = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  for (const file of files.data) {
    console.log(`${file.filename}: +${file.additions} -${file.deletions}`);
  }
});
```

### Merge PR

```typescript
app.on("pull_request_review.submitted", async (context) => {
  const { review, pull_request } = context.payload;

  if (review.state === "approved") {
    // Check if all required approvals met
    const reviews = await context.octokit.pulls.listReviews(
      context.pullRequest()
    );

    const approvals = reviews.data.filter(
      (r) => r.state === "APPROVED"
    ).length;

    if (approvals >= 2) {
      await context.octokit.pulls.merge(
        context.pullRequest({
          merge_method: "squash",
        })
      );
    }
  }
});
```

## Scheduling

Run tasks on a schedule using probot-scheduler:

```typescript
import { Probot } from "probot";
import Scheduler from "probot-scheduler";

export default (app: Probot) => {
  Scheduler(app, {
    delay: false, // Run immediately on startup
    interval: 24 * 60 * 60 * 1000, // Daily
  });

  app.on("schedule.repository", async (context) => {
    // Runs for each installed repository
    const staleIssues = await findStaleIssues(context);
    await closeStaleIssues(context, staleIssues);
  });
};
```

## Error Handling

```typescript
app.on("issues.opened", async (context) => {
  try {
    await context.octokit.issues.createComment(
      context.issue({ body: "Hello!" })
    );
  } catch (error) {
    context.log.error("Failed to comment:", error);

    // Re-throw to signal failure to GitHub
    throw error;
  }
});

// Global error handler
app.onError(async (error) => {
  console.error("Unhandled error:", error);
});
```

## Testing

### Unit Tests

```typescript
import nock from "nock";
import { Probot, ProbotOctokit } from "probot";
import myApp from "../src";

describe("My App", () => {
  let probot: Probot;

  beforeEach(() => {
    nock.disableNetConnect();
    probot = new Probot({
      appId: 123,
      privateKey: "test-private-key",
      Octokit: ProbotOctokit.defaults({
        retry: { enabled: false },
        throttle: { enabled: false },
      }),
    });
    probot.load(myApp);
  });

  afterEach(() => {
    nock.cleanAll();
    nock.enableNetConnect();
  });

  test("creates a comment on new issues", async () => {
    const mock = nock("https://api.github.com")
      .post("/repos/owner/repo/issues/1/comments", (body) => {
        expect(body.body).toContain("Thanks");
        return true;
      })
      .reply(201);

    await probot.receive({
      name: "issues",
      payload: {
        action: "opened",
        issue: { number: 1 },
        repository: {
          owner: { login: "owner" },
          name: "repo",
        },
      },
    });

    expect(mock.isDone()).toBe(true);
  });
});
```

### Integration Tests

```typescript
import { createProbot } from "probot";
import myApp from "../src";

describe("Integration", () => {
  test("handles real webhook", async () => {
    const probot = createProbot({
      overrides: {
        appId: process.env.APP_ID,
        privateKey: process.env.PRIVATE_KEY,
      },
    });

    await probot.load(myApp);

    // Trigger with real payload
    const payload = require("./fixtures/issues.opened.json");
    await probot.receive({ name: "issues", payload });
  });
});
```

## Deployment

### Environment Variables

```bash
# Required
APP_ID=12345
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
WEBHOOK_SECRET=your-secret

# Optional
LOG_LEVEL=debug
NODE_ENV=production
```

### Vercel

```json
// vercel.json
{
  "builds": [{ "src": "src/index.ts", "use": "@vercel/node" }],
  "routes": [{ "src": "/(.*)", "dest": "src/index.ts" }]
}
```

```typescript
// api/github/webhooks.ts
import { createNodeMiddleware, createProbot } from "probot";
import app from "../../src";

export default createNodeMiddleware(app, {
  probot: createProbot(),
  webhooksPath: "/api/github/webhooks",
});
```

### Glitch

```json
// package.json
{
  "scripts": {
    "start": "probot run ./src/index.js"
  }
}
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
CMD ["npm", "start"]
```

## Extensions

### probot-commands

Handle slash commands in comments:

```typescript
import commands from "probot-commands";

export default (app: Probot) => {
  // Responds to "/close" in comments
  commands(app, "close", async (context, command) => {
    await context.octokit.issues.update(
      context.issue({ state: "closed" })
    );
  });

  // "/label bug priority:high"
  commands(app, "label", async (context, command) => {
    const labels = command.arguments.split(/\s+/);
    await context.octokit.issues.addLabels(
      context.issue({ labels })
    );
  });
};
```

### probot-metadata

Store metadata in issue/PR body:

```typescript
import metadata from "probot-metadata";

export default (app: Probot) => {
  app.on("issues.opened", async (context) => {
    // Store metadata
    await metadata(context).set("reviewed", false);
    await metadata(context).set("assignedAt", new Date().toISOString());
  });

  app.on("issue_comment.created", async (context) => {
    // Read metadata
    const reviewed = await metadata(context).get("reviewed");
    if (!reviewed) {
      // First review
    }
  });
};
```

## Comparison: Probot vs Raw Octokit

| Feature | Probot | Raw Octokit |
|---------|--------|-------------|
| Auth handling | Automatic | Manual JWT/token management |
| Webhook routing | Built-in | Manual with @octokit/webhooks |
| Context helpers | `context.issue()`, `context.repo()` | Build params manually |
| Config loading | `context.config()` | Manual file fetch |
| Logging | Built-in structured logging | BYO logging |
| Testing | Fixtures and mocks | More setup required |
| Deployment | Many integrations | More flexible |
| Runtime | Node.js only | Any JavaScript runtime |
| Bundle size | Larger | Smaller, tree-shakeable |

## See Also

- [Probot Documentation](https://probot.github.io/docs/)
- [Probot Extensions](https://probot.github.io/docs/extensions/)
- [Example Apps](https://github.com/probot/probot/tree/master/docs/examples)
