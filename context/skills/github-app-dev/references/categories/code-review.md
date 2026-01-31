# Code Review GitHub Apps

GitHub Apps that assist with code review: automated suggestions, review assignment, approval workflows, and review analytics.

## Common Use Cases

- **Automated Suggestions** - AI-powered code review comments
- **Review Assignment** - Auto-assign reviewers based on rules
- **Approval Workflows** - Custom approval requirements
- **Review Analytics** - Track review metrics
- **Stale Review Detection** - Notify on outdated reviews
- **Review Templates** - Standardized review checklists

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `pull_request.opened` | Assign reviewers, start analysis |
| `pull_request.ready_for_review` | Draft to ready transition |
| `pull_request.synchronize` | New commits invalidate reviews |
| `pull_request_review.submitted` | Track approvals/changes |
| `pull_request_review_comment.created` | React to review comments |
| `pull_request.review_requested` | Notify requested reviewers |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Pull requests | Write | Create reviews, request reviewers |
| Contents | Read | Access code for review |
| Members | Read | Access team membership for assignment |
| Checks | Write | Report review status |

### Minimal Permission Set
```yaml
permissions:
  pull-requests: write
  contents: read
```

### Full Review Set
```yaml
permissions:
  pull-requests: write
  contents: read
  members: read
  checks: write
```

## Common Patterns

### Auto-Assign Reviewers

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request, repository } = context.payload;

  // Don't assign to self
  const author = pull_request.user.login;

  // Load assignment config
  const config = await context.config("reviewers.yml", {
    reviewers: [],
    teamReviewers: [],
    reviewerCount: 2,
    assignFromTeam: true,
  });

  // Get files changed
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  // Find appropriate reviewers based on file paths
  const reviewers = await selectReviewers({
    files: files.map(f => f.filename),
    author,
    config,
    context,
  });

  if (reviewers.length > 0) {
    await context.octokit.pulls.requestReviewers(
      context.pullRequest({
        reviewers: reviewers.filter(r => !r.startsWith("team:")),
        team_reviewers: reviewers
          .filter(r => r.startsWith("team:"))
          .map(r => r.replace("team:", "")),
      })
    );
  }
});

async function selectReviewers({ files, author, config, context }) {
  const reviewers = new Set<string>();

  // Code owners
  const codeowners = await getCodeowners(context);
  for (const file of files) {
    const owners = codeowners.getOwners(file);
    owners.forEach(o => reviewers.add(o));
  }

  // Remove author
  reviewers.delete(author);

  // Limit to configured count
  return Array.from(reviewers).slice(0, config.reviewerCount);
}
```

### CODEOWNERS Integration

```typescript
interface CodeOwnerRule {
  pattern: string;
  owners: string[];
}

async function getCodeowners(context): Promise<CodeOwnerRule[]> {
  const paths = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"];

  for (const path of paths) {
    try {
      const { data } = await context.octokit.repos.getContent(
        context.repo({ path })
      );

      if ("content" in data) {
        const content = Buffer.from(data.content, "base64").toString();
        return parseCodeowners(content);
      }
    } catch {
      // File doesn't exist
    }
  }

  return [];
}

function parseCodeowners(content: string): CodeOwnerRule[] {
  return content
    .split("\n")
    .filter(line => line.trim() && !line.startsWith("#"))
    .map(line => {
      const parts = line.trim().split(/\s+/);
      const pattern = parts[0];
      const owners = parts.slice(1).map(o => o.replace("@", ""));
      return { pattern, owners };
    });
}
```

### Stale Review Detection

```typescript
app.on("pull_request.synchronize", async (context) => {
  const { pull_request } = context.payload;

  // Get existing reviews
  const { data: reviews } = await context.octokit.pulls.listReviews(
    context.pullRequest()
  );

  // Find reviews that were submitted before the latest push
  const staleReviews = reviews.filter(
    review =>
      review.state === "APPROVED" &&
      new Date(review.submitted_at) < new Date(pull_request.updated_at)
  );

  if (staleReviews.length > 0) {
    const staleReviewers = staleReviews.map(r => r.user.login);

    await context.octokit.issues.createComment(
      context.issue({
        body: `## ⚠️ Stale Reviews Detected

The following reviews were submitted before the latest changes and may need re-review:

${staleReviewers.map(r => `- @${r}`).join("\n")}

Please review the new changes and re-approve if appropriate.`,
      })
    );

    // Add label
    await context.octokit.issues.addLabels(
      context.issue({ labels: ["needs-re-review"] })
    );
  }
});
```

### Review Checklist Enforcement

```typescript
app.on("pull_request_review.submitted", async (context) => {
  const { review, pull_request } = context.payload;

  if (review.state !== "APPROVED") return;

  // Check if PR description has checklist
  const checklist = extractChecklist(pull_request.body);

  if (checklist.length > 0) {
    const unchecked = checklist.filter(item => !item.checked);

    if (unchecked.length > 0) {
      await context.octokit.issues.createComment(
        context.issue({
          body: `@${review.user.login} Approval submitted, but the following checklist items are incomplete:

${unchecked.map(item => `- [ ] ${item.text}`).join("\n")}

Please ensure all items are checked before merging.`,
        })
      );
    }
  }
});

function extractChecklist(body: string | null) {
  if (!body) return [];

  const checklistRegex = /- \[([ x])\] (.+)/g;
  const items = [];
  let match;

  while ((match = checklistRegex.exec(body)) !== null) {
    items.push({
      checked: match[1] === "x",
      text: match[2],
    });
  }

  return items;
}
```

### Custom Approval Requirements

```typescript
app.on(["pull_request_review.submitted", "pull_request.synchronize"], async (context) => {
  const { pull_request } = context.payload;

  // Get approval config
  const config = await context.config("approval.yml", {
    requiredApprovals: 2,
    requireCodeOwner: true,
    requireTeamLead: false,
    blockedPaths: [],
  });

  // Get reviews
  const { data: reviews } = await context.octokit.pulls.listReviews(
    context.pullRequest()
  );

  // Count valid approvals (latest per user)
  const latestReviews = new Map<string, string>();
  for (const review of reviews.sort((a, b) =>
    new Date(a.submitted_at).getTime() - new Date(b.submitted_at).getTime()
  )) {
    latestReviews.set(review.user.login, review.state);
  }

  const approvalCount = Array.from(latestReviews.values())
    .filter(state => state === "APPROVED")
    .length;

  // Check requirements
  const checks = {
    approvalCount: approvalCount >= config.requiredApprovals,
    codeOwner: !config.requireCodeOwner || await hasCodeOwnerApproval(context),
    teamLead: !config.requireTeamLead || await hasTeamLeadApproval(context),
  };

  const allPassed = Object.values(checks).every(Boolean);

  // Update check status
  await context.octokit.checks.create(
    context.repo({
      name: "Approval Requirements",
      head_sha: pull_request.head.sha,
      status: "completed",
      conclusion: allPassed ? "success" : "failure",
      output: {
        title: allPassed ? "All requirements met" : "Requirements not met",
        summary: `
- Approvals: ${approvalCount}/${config.requiredApprovals} ${checks.approvalCount ? "✅" : "❌"}
- Code Owner: ${checks.codeOwner ? "✅" : "❌"}
- Team Lead: ${checks.teamLead ? "✅" : "❌"}
        `.trim(),
      },
    })
  );
});
```

### AI-Powered Review Suggestions

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Get diff
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const reviewComments = [];

  for (const file of files) {
    if (file.status === "removed" || !file.patch) continue;

    // Parse hunks
    const hunks = parsePatch(file.patch);

    for (const hunk of hunks) {
      // Send to AI for review
      const suggestions = await getAISuggestions({
        filename: file.filename,
        code: hunk.added,
        context: hunk.context,
      });

      for (const suggestion of suggestions) {
        reviewComments.push({
          path: file.filename,
          position: hunk.startLine + suggestion.lineOffset,
          body: `**AI Suggestion**: ${suggestion.message}

${suggestion.code ? `\`\`\`suggestion\n${suggestion.code}\n\`\`\`` : ""}`,
        });
      }
    }
  }

  if (reviewComments.length > 0) {
    await context.octokit.pulls.createReview(
      context.pullRequest({
        event: "COMMENT",
        comments: reviewComments.slice(0, 20),
      })
    );
  }
});
```

## Review Metrics

```typescript
interface ReviewMetrics {
  timeToFirstReview: number; // minutes
  timeToApproval: number;
  reviewIterations: number;
  commentsCount: number;
}

async function trackReviewMetrics(context, pullRequest) {
  const { data: reviews } = await context.octokit.pulls.listReviews(
    context.pullRequest()
  );

  const { data: comments } = await context.octokit.pulls.listReviewComments(
    context.pullRequest({ per_page: 100 })
  );

  const firstReview = reviews[0];
  const firstApproval = reviews.find(r => r.state === "APPROVED");

  const metrics: ReviewMetrics = {
    timeToFirstReview: firstReview
      ? (new Date(firstReview.submitted_at).getTime() - new Date(pullRequest.created_at).getTime()) / 60000
      : -1,
    timeToApproval: firstApproval
      ? (new Date(firstApproval.submitted_at).getTime() - new Date(pullRequest.created_at).getTime()) / 60000
      : -1,
    reviewIterations: new Set(reviews.map(r => r.commit_id)).size,
    commentsCount: comments.length,
  };

  await storeMetrics({
    repo: pullRequest.base.repo.full_name,
    pr: pullRequest.number,
    metrics,
  });
}
```

## Security Considerations

- **Don't auto-merge** - Reviews should gate merges
- **Validate reviewer identity** - Prevent review spoofing
- **Audit review actions** - Log who approved what
- **Protect sensitive paths** - Require specific reviewers
- **Handle dismissed reviews** - Track review history

## Example Apps in This Category

- **Reviewable** - Advanced code review
- **PullApprove** - Approval automation
- **LGTM** - Automated code analysis
- **Graphite** - Stacked PR reviews

## Related Categories

- [Code Quality](code-quality.md) - Automated analysis
- [Testing](testing.md) - Test requirements
- [Security](security.md) - Security-focused review

## See Also

- [GitHub Pull Request Reviews API](https://docs.github.com/en/rest/pulls/reviews)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
