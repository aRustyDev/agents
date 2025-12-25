# GitHub Webhook Events Reference

Complete reference for GitHub webhook events relevant to GitHub App development.

## Event Categories

### Pull Request Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `pull_request` | `opened` | `pull_request` | PR created |
| `pull_request` | `closed` | `pull_request` | PR closed (check `merged` flag) |
| `pull_request` | `reopened` | `pull_request` | Closed PR reopened |
| `pull_request` | `edited` | `pull_request`, `changes` | Title/body modified |
| `pull_request` | `synchronize` | `pull_request` | New commits pushed |
| `pull_request` | `assigned` | `pull_request`, `assignee` | Assignee added |
| `pull_request` | `unassigned` | `pull_request`, `assignee` | Assignee removed |
| `pull_request` | `labeled` | `pull_request`, `label` | Label added |
| `pull_request` | `unlabeled` | `pull_request`, `label` | Label removed |
| `pull_request` | `ready_for_review` | `pull_request` | Draft → Ready |
| `pull_request` | `converted_to_draft` | `pull_request` | Ready → Draft |
| `pull_request` | `review_requested` | `pull_request`, `requested_reviewer` | Review requested |
| `pull_request` | `review_request_removed` | `pull_request`, `requested_reviewer` | Review request removed |

### Pull Request Review Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `pull_request_review` | `submitted` | `review`, `pull_request` | Review submitted |
| `pull_request_review` | `edited` | `review`, `changes` | Review edited |
| `pull_request_review` | `dismissed` | `review` | Review dismissed |

### Pull Request Review Comment Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `pull_request_review_comment` | `created` | `comment`, `pull_request` | Line comment created |
| `pull_request_review_comment` | `edited` | `comment`, `changes` | Comment edited |
| `pull_request_review_comment` | `deleted` | `comment` | Comment deleted |

### Issue Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `issues` | `opened` | `issue` | Issue created |
| `issues` | `closed` | `issue` | Issue closed |
| `issues` | `reopened` | `issue` | Issue reopened |
| `issues` | `edited` | `issue`, `changes` | Title/body modified |
| `issues` | `assigned` | `issue`, `assignee` | Assignee added |
| `issues` | `unassigned` | `issue`, `assignee` | Assignee removed |
| `issues` | `labeled` | `issue`, `label` | Label added |
| `issues` | `unlabeled` | `issue`, `label` | Label removed |
| `issues` | `milestoned` | `issue`, `milestone` | Added to milestone |
| `issues` | `demilestoned` | `issue`, `milestone` | Removed from milestone |

### Issue Comment Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `issue_comment` | `created` | `comment`, `issue` | Comment created |
| `issue_comment` | `edited` | `comment`, `changes` | Comment edited |
| `issue_comment` | `deleted` | `comment` | Comment deleted |

### Check Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `check_run` | `created` | `check_run` | Check created |
| `check_run` | `completed` | `check_run` | Check finished |
| `check_run` | `rerequested` | `check_run` | Re-run requested |
| `check_suite` | `completed` | `check_suite` | All checks in suite done |
| `check_suite` | `requested` | `check_suite` | Suite requested |
| `check_suite` | `rerequested` | `check_suite` | Suite re-run requested |

### Push Events

| Event | Payload Key | Description |
|-------|-------------|-------------|
| `push` | `commits`, `ref`, `before`, `after` | Commits pushed |
| `create` | `ref`, `ref_type` | Branch/tag created |
| `delete` | `ref`, `ref_type` | Branch/tag deleted |

### Repository Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `repository` | `created` | `repository` | Repo created |
| `repository` | `deleted` | `repository` | Repo deleted |
| `repository` | `archived` | `repository` | Repo archived |
| `repository` | `unarchived` | `repository` | Repo unarchived |
| `repository` | `publicized` | `repository` | Made public |
| `repository` | `privatized` | `repository` | Made private |

### Release Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `release` | `published` | `release` | Release published |
| `release` | `created` | `release` | Release created (draft) |
| `release` | `edited` | `release`, `changes` | Release edited |
| `release` | `deleted` | `release` | Release deleted |

### Workflow Events

| Event | Action | Payload Key | Description |
|-------|--------|-------------|-------------|
| `workflow_run` | `completed` | `workflow_run` | Workflow finished |
| `workflow_run` | `requested` | `workflow_run` | Workflow triggered |
| `workflow_job` | `completed` | `workflow_job` | Job finished |
| `workflow_job` | `in_progress` | `workflow_job` | Job started |

## Payload Structure

### Common Fields

Every webhook payload includes:

```typescript
interface WebhookPayload {
  action?: string;              // Event action (opened, closed, etc.)
  sender: User;                 // User who triggered event
  repository: Repository;       // Repository context
  organization?: Organization;  // Org context (if applicable)
  installation?: Installation;  // App installation info
}
```

### Pull Request Payload

```typescript
interface PullRequestPayload {
  action: string;
  number: number;
  pull_request: {
    id: number;
    number: number;
    state: "open" | "closed";
    title: string;
    body: string | null;
    user: User;
    head: {
      ref: string;       // Branch name
      sha: string;       // Latest commit SHA
      repo: Repository;
    };
    base: {
      ref: string;       // Target branch
      sha: string;
      repo: Repository;
    };
    merged: boolean;
    mergeable: boolean | null;
    mergeable_state: string;
    merged_by: User | null;
    additions: number;
    deletions: number;
    changed_files: number;
    draft: boolean;
    labels: Label[];
    assignees: User[];
    requested_reviewers: User[];
    html_url: string;
  };
  // For 'edited' action
  changes?: {
    title?: { from: string };
    body?: { from: string };
  };
}
```

### Issue Payload

```typescript
interface IssuePayload {
  action: string;
  issue: {
    id: number;
    number: number;
    state: "open" | "closed";
    title: string;
    body: string | null;
    user: User;
    labels: Label[];
    assignees: User[];
    milestone: Milestone | null;
    html_url: string;
    created_at: string;
    updated_at: string;
    closed_at: string | null;
  };
}
```

### Check Run Payload

```typescript
interface CheckRunPayload {
  action: string;
  check_run: {
    id: number;
    name: string;
    status: "queued" | "in_progress" | "completed";
    conclusion: "success" | "failure" | "neutral" | "cancelled" | "skipped" | "timed_out" | "action_required" | null;
    head_sha: string;
    external_id: string;
    url: string;
    html_url: string;
    started_at: string;
    completed_at: string | null;
    output: {
      title: string | null;
      summary: string | null;
      text: string | null;
      annotations_count: number;
      annotations_url: string;
    };
    check_suite: {
      id: number;
      head_sha: string;
    };
    pull_requests: PullRequest[];
  };
}
```

## Webhook Headers

Every webhook request includes these headers:

| Header | Description |
|--------|-------------|
| `X-GitHub-Event` | Event name (e.g., `pull_request`) |
| `X-GitHub-Delivery` | Unique delivery ID (UUID) |
| `X-Hub-Signature-256` | HMAC hex digest of payload |
| `X-GitHub-Hook-ID` | Webhook ID |
| `X-GitHub-Hook-Installation-Target-Type` | `repository`, `organization`, or `app` |
| `X-GitHub-Hook-Installation-Target-ID` | ID of target |

## Signature Verification

Always verify webhook signatures:

```typescript
import { createHmac, timingSafeEqual } from "crypto";

function verifySignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expected = `sha256=${createHmac("sha256", secret)
    .update(payload)
    .digest("hex")}`;

  return timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}
```

## Event Subscription Best Practices

1. **Subscribe only to needed events** - Reduces webhook volume
2. **Handle actions explicitly** - Check `action` field, not just event type
3. **Idempotent handlers** - Webhooks may be delivered multiple times
4. **Respond quickly** - Return 2xx within 10 seconds, process async
5. **Handle failures gracefully** - GitHub retries failed deliveries
