# Octokit SDK Reference

## Installation

```bash
# Core packages
npm install @octokit/rest @octokit/auth-app @octokit/webhooks

# Type definitions (included in v19+)
npm install -D @types/node
```

## Authentication

### App Authentication (JWT)

Used for app-level operations like listing installations.

```typescript
import { Octokit } from "@octokit/rest";
import { createAppAuth } from "@octokit/auth-app";

const octokit = new Octokit({
  authStrategy: createAppAuth,
  auth: {
    appId: process.env.GITHUB_APP_ID,
    privateKey: process.env.GITHUB_PRIVATE_KEY,
  },
});

// Get app info
const { data: app } = await octokit.apps.getAuthenticated();

// List installations
const { data: installations } = await octokit.apps.listInstallations();
```

### Installation Authentication

Used for most API operations within a repo.

```typescript
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

async function getInstallationOctokit(installationId: number): Promise<Octokit> {
  const auth = createAppAuth({
    appId: process.env.GITHUB_APP_ID!,
    privateKey: process.env.GITHUB_PRIVATE_KEY!,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}
```

### From Webhook Payload

```typescript
import { Webhooks } from "@octokit/webhooks";

webhooks.on("pull_request.opened", async ({ payload, octokit }) => {
  // octokit is pre-authenticated for this installation
  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Hello!",
  });
});
```

## Pull Requests

### Get PR Details

```typescript
const { data: pr } = await octokit.pulls.get({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
});

console.log(pr.title, pr.state, pr.merged);
```

### List PR Files

```typescript
const { data: files } = await octokit.pulls.listFiles({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  per_page: 100,
});

for (const file of files) {
  console.log(file.filename, file.status, file.additions, file.deletions);
}
```

### Get PR Diff

```typescript
const { data: diff } = await octokit.pulls.get({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  mediaType: { format: "diff" },
});

// diff is a string containing unified diff
```

### Create PR Review

```typescript
// Submit a review
await octokit.pulls.createReview({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  event: "APPROVE", // APPROVE | REQUEST_CHANGES | COMMENT
  body: "Looks good to me!",
});

// Create review with comments
await octokit.pulls.createReview({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  event: "REQUEST_CHANGES",
  body: "Please address these issues.",
  comments: [
    {
      path: "src/index.ts",
      line: 42,
      body: "This could cause a null pointer exception",
    },
  ],
});
```

### Create PR Review Comment

```typescript
await octokit.pulls.createReviewComment({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  body: "Consider using a constant here",
  path: "src/config.ts",
  line: 15,
  side: "RIGHT", // RIGHT (new) or LEFT (old)
});
```

### Merge PR

```typescript
await octokit.pulls.merge({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  merge_method: "squash", // merge | squash | rebase
  commit_title: "feat: add new feature (#123)",
  commit_message: "Detailed description...",
});
```

### Update PR

```typescript
await octokit.pulls.update({
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  title: "New title",
  body: "Updated description",
  state: "closed", // or "open"
});
```

## Issues

### Create Comment

```typescript
await octokit.issues.createComment({
  owner: "owner",
  repo: "repo",
  issue_number: 123, // Works for PRs too
  body: "This is a comment",
});
```

### Add Labels

```typescript
await octokit.issues.addLabels({
  owner: "owner",
  repo: "repo",
  issue_number: 123,
  labels: ["bug", "priority: high"],
});
```

### Remove Label

```typescript
await octokit.issues.removeLabel({
  owner: "owner",
  repo: "repo",
  issue_number: 123,
  name: "bug",
});
```

### Assign Users

```typescript
await octokit.issues.addAssignees({
  owner: "owner",
  repo: "repo",
  issue_number: 123,
  assignees: ["user1", "user2"],
});
```

## Checks

### Create Check Run

```typescript
const { data: checkRun } = await octokit.checks.create({
  owner: "owner",
  repo: "repo",
  name: "My Check",
  head_sha: "abc123",
  status: "in_progress",
  started_at: new Date().toISOString(),
});
```

### Update Check Run

```typescript
await octokit.checks.update({
  owner: "owner",
  repo: "repo",
  check_run_id: checkRun.id,
  status: "completed",
  conclusion: "success", // success | failure | neutral | cancelled | skipped | timed_out
  completed_at: new Date().toISOString(),
  output: {
    title: "Check Passed",
    summary: "All tests passed successfully",
    text: "Detailed results...",
    annotations: [
      {
        path: "src/index.ts",
        start_line: 10,
        end_line: 10,
        annotation_level: "warning", // notice | warning | failure
        message: "Consider adding error handling",
      },
    ],
  },
});
```

### List Check Runs for Ref

```typescript
const { data } = await octokit.checks.listForRef({
  owner: "owner",
  repo: "repo",
  ref: "abc123", // SHA or branch name
});

for (const checkRun of data.check_runs) {
  console.log(checkRun.name, checkRun.status, checkRun.conclusion);
}
```

## Repository Contents

### Get File Content

```typescript
const { data } = await octokit.repos.getContent({
  owner: "owner",
  repo: "repo",
  path: "README.md",
  ref: "main", // optional: branch, tag, or SHA
});

if ("content" in data) {
  const content = Buffer.from(data.content, "base64").toString("utf-8");
  console.log(content);
}
```

### Create or Update File

```typescript
await octokit.repos.createOrUpdateFileContents({
  owner: "owner",
  repo: "repo",
  path: "new-file.md",
  message: "Add new file",
  content: Buffer.from("Hello, world!").toString("base64"),
  branch: "main",
  // sha: "..." // Required if updating existing file
});
```

### List Directory

```typescript
const { data } = await octokit.repos.getContent({
  owner: "owner",
  repo: "repo",
  path: "src",
});

if (Array.isArray(data)) {
  for (const item of data) {
    console.log(item.name, item.type); // type: "file" | "dir" | "submodule"
  }
}
```

## Pagination

### Manual Pagination

```typescript
let page = 1;
let allFiles: File[] = [];

while (true) {
  const { data: files } = await octokit.pulls.listFiles({
    owner: "owner",
    repo: "repo",
    pull_number: 123,
    per_page: 100,
    page,
  });

  allFiles = allFiles.concat(files);

  if (files.length < 100) break;
  page++;
}
```

### Using paginate Helper

```typescript
const allFiles = await octokit.paginate(octokit.pulls.listFiles, {
  owner: "owner",
  repo: "repo",
  pull_number: 123,
  per_page: 100,
});
```

### Async Iterator

```typescript
for await (const response of octokit.paginate.iterator(
  octokit.pulls.listFiles,
  {
    owner: "owner",
    repo: "repo",
    pull_number: 123,
    per_page: 100,
  }
)) {
  for (const file of response.data) {
    console.log(file.filename);
  }
}
```

## Error Handling

```typescript
import { RequestError } from "@octokit/request-error";

try {
  await octokit.issues.createComment({...});
} catch (error) {
  if (error instanceof RequestError) {
    switch (error.status) {
      case 401:
        console.error("Authentication failed");
        break;
      case 403:
        console.error("Forbidden - check permissions");
        break;
      case 404:
        console.error("Resource not found");
        break;
      case 422:
        console.error("Validation failed:", error.message);
        break;
      case 429:
        console.error("Rate limited, retry after:", error.response?.headers["retry-after"]);
        break;
      default:
        console.error("GitHub API error:", error.message);
    }
  }
  throw error;
}
```

## Rate Limiting

```typescript
// Check rate limit status
const { data: rateLimit } = await octokit.rateLimit.get();
console.log("Remaining:", rateLimit.rate.remaining);
console.log("Reset at:", new Date(rateLimit.rate.reset * 1000));

// Handle rate limiting in requests
const { data, headers } = await octokit.pulls.get({...});
console.log("Remaining:", headers["x-ratelimit-remaining"]);
```

## Webhooks

### Setup

```typescript
import { Webhooks, createNodeMiddleware } from "@octokit/webhooks";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

// Register handlers
webhooks.on("pull_request.opened", handlePROpened);
webhooks.on("issues.opened", handleIssueOpened);
webhooks.on("error", (error) => console.error(error));

// Express middleware
app.use("/webhook", createNodeMiddleware(webhooks));
```

### Cloudflare Workers

```typescript
import { Webhooks } from "@octokit/webhooks";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const webhooks = new Webhooks({ secret: env.WEBHOOK_SECRET });

    webhooks.on("pull_request.opened", async ({ payload }) => {
      // Handle event
    });

    const signature = request.headers.get("x-hub-signature-256") || "";
    const body = await request.text();

    try {
      await webhooks.verifyAndReceive({
        id: request.headers.get("x-github-delivery") || "",
        name: request.headers.get("x-github-event") as any,
        signature,
        payload: body,
      });
      return new Response("OK", { status: 200 });
    } catch {
      return new Response("Unauthorized", { status: 401 });
    }
  },
};
```

## TypeScript Types

```typescript
import type { Endpoints } from "@octokit/types";

// Extract response types
type PullRequest = Endpoints["GET /repos/{owner}/{repo}/pulls/{pull_number}"]["response"]["data"];
type Issue = Endpoints["GET /repos/{owner}/{repo}/issues/{issue_number}"]["response"]["data"];
type CheckRun = Endpoints["GET /repos/{owner}/{repo}/check-runs/{check_run_id}"]["response"]["data"];

// Use in functions
function processPR(pr: PullRequest): void {
  console.log(pr.title, pr.number);
}
```
