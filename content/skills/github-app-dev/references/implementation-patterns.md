# Implementation Patterns

Common development patterns and best practices for GitHub App implementation.

## Essential App Patterns

Core automation patterns that most GitHub Apps implement.

### Auto-labeling
Label PRs and issues based on conventional commit titles, file paths, or content analysis.

```typescript
// Pattern: Conventional commit-based labeling
app.on('pull_request.opened', async (context) => {
  const title = context.payload.pull_request.title;
  const type = extractCommitType(title); // feat, fix, docs, etc.

  if (type) {
    await context.octokit.issues.addLabels({
      ...context.repo,
      issue_number: context.payload.pull_request.number,
      labels: [`type: ${type}`]
    });
  }
});
```

### Reviewer Assignment
Route pull requests to appropriate team members based on file paths or repository configuration.

```typescript
// Pattern: CODEOWNERS-based assignment
app.on('pull_request.opened', async (context) => {
  const files = await getChangedFiles(context);
  const reviewers = await getCodeOwners(files, context.repo);

  if (reviewers.length > 0) {
    await context.octokit.pulls.requestReviewers({
      ...context.repo,
      pull_number: context.payload.pull_request.number,
      reviewers: reviewers.slice(0, 3) // Limit to 3 reviewers
    });
  }
});
```

### Quality Gates
Enforce quality standards and repository policies automatically.

```typescript
// Pattern: Required checks enforcement
app.on('pull_request.opened', async (context) => {
  const config = await getRepoConfig(context.repo);

  // Create required check run
  await context.octokit.checks.create({
    ...context.repo,
    name: 'Quality Gate',
    head_sha: context.payload.pull_request.head.sha,
    status: 'in_progress'
  });

  // Run quality checks
  const results = await runQualityChecks(context.payload.pull_request);

  // Update check with results
  await updateCheckRun(context, results);
});
```

### Welcome Automation
Greet and guide first-time contributors with helpful information.

```typescript
// Pattern: First-time contributor welcome
app.on('pull_request.opened', async (context) => {
  const isFirstContribution = await checkFirstContribution(
    context.payload.pull_request.user.login,
    context.repo
  );

  if (isFirstContribution) {
    await context.octokit.issues.createComment({
      ...context.repo,
      issue_number: context.payload.pull_request.number,
      body: generateWelcomeMessage(context.payload.pull_request.user)
    });
  }
});
```

## Configuration-Driven Patterns

Implement flexible behavior using repository-specific configurations.

### Repository Custom Properties
Use GitHub's custom properties for per-repository configuration.

```typescript
// Pattern: Custom properties configuration
const getRepoConfig = async (repo, octokit) => {
  const { data } = await octokit.repos.get(repo);
  return {
    autoAssign: data.custom_properties?.auto_assign === 'true',
    reviewerTeam: data.custom_properties?.reviewer_team,
    requireTests: data.custom_properties?.require_tests === 'true'
  };
};
```

### Team-Based Routing
Route issues and PRs based on team ownership and expertise.

```typescript
// Pattern: Team-based routing with fallback
const getTeamOwners = async (files, repo, octokit) => {
  const teams = await getTeamsForFiles(files, repo);

  if (teams.length === 0) {
    // Fallback to default team
    return [repo.custom_properties?.default_team || 'maintainers'];
  }

  return teams;
};
```

### Conditional Logic
Implement repository-specific behavior based on metadata and configuration.

```typescript
// Pattern: Environment-aware behavior
app.on('push', async (context) => {
  const branch = context.payload.ref.replace('refs/heads/', '');
  const config = await getRepoConfig(context.repo);

  if (config.production_branches?.includes(branch)) {
    await triggerProductionWorkflow(context);
  } else if (config.staging_branches?.includes(branch)) {
    await triggerStagingWorkflow(context);
  }
});
```

## Event Processing Patterns

Handle webhook events efficiently and reliably.

### Event Filtering
Process only relevant events to reduce noise and improve performance.

```typescript
// Pattern: Smart event filtering
app.on('issues.labeled', async (context) => {
  const relevantLabels = ['bug', 'enhancement', 'help wanted'];
  const hasRelevantLabel = context.payload.issue.labels.some(
    label => relevantLabels.includes(label.name)
  );

  if (hasRelevantLabel) {
    await processRelevantIssue(context);
  }
});
```

### Batch Processing
Group related operations to improve efficiency and reduce API calls.

```typescript
// Pattern: Batch operations
const batchUpdateLabels = async (issues, labels, octokit, repo) => {
  const batchSize = 10;

  for (let i = 0; i < issues.length; i += batchSize) {
    const batch = issues.slice(i, i + batchSize);

    await Promise.all(batch.map(issue =>
      octokit.issues.setLabels({
        ...repo,
        issue_number: issue.number,
        labels
      })
    ));
  }
};
```

### Idempotent Operations
Ensure operations can be safely retried without side effects.

```typescript
// Pattern: Idempotent webhook processing
app.on('pull_request.opened', async (context) => {
  const prNumber = context.payload.pull_request.number;
  const processedKey = `pr-${prNumber}-processed`;

  // Check if already processed
  if (await cache.get(processedKey)) {
    return;
  }

  await processPullRequest(context);

  // Mark as processed
  await cache.set(processedKey, true, { ttl: 86400 }); // 24h TTL
});
```

## State Management Patterns

Handle application state in stateless webhook environments.

### External State Storage
Use databases or caches for persistent state across webhook invocations.

```typescript
// Pattern: Redis-based state management
const saveProcessingState = async (key, data) => {
  await redis.setex(`state:${key}`, 3600, JSON.stringify(data));
};

const getProcessingState = async (key) => {
  const data = await redis.get(`state:${key}`);
  return data ? JSON.parse(data) : null;
};
```

### GitHub as State Store
Leverage GitHub's native features for state persistence.

```typescript
// Pattern: Using PR/Issue comments for state
const saveStateToComment = async (context, state) => {
  const marker = '<!-- APP-STATE:';
  const stateComment = `${marker}${JSON.stringify(state)}-->`;

  await context.octokit.issues.createComment({
    ...context.repo,
    issue_number: context.payload.issue.number,
    body: `Processing update...\n${stateComment}`
  });
};
```

## See Also

- [Integration Patterns](integration-patterns.md) - External system integration
- [Advanced Configuration](advanced-configuration.md) - Enterprise and multi-repo patterns
- [Error Handling](error-handling.md) - Robust error handling strategies
- [Examples](../examples/) - Complete implementation examples
