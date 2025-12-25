# Reporting GitHub Apps

GitHub Apps that generate reports and analytics: repository insights, team metrics, audit logs, and compliance reporting.

## Common Use Cases

- **Repository Analytics** - Activity metrics, trends
- **Team Reports** - Contribution statistics
- **Compliance Audits** - Access and change logs
- **PR/Issue Metrics** - Cycle time, throughput
- **Security Reports** - Vulnerability summaries
- **Custom Dashboards** - Tailored visualizations

## Key Webhooks

For reporting, you often need to either:
1. Listen to all relevant events for real-time tracking
2. Use scheduled polling for periodic reports

| Webhook | Use Case |
|---------|----------|
| `push` | Commit activity |
| `pull_request.*` | PR metrics |
| `issues.*` | Issue tracking |
| `workflow_run.*` | CI/CD metrics |
| `member.*` | Team changes |
| `repository.*` | Repo lifecycle |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Metadata | Read | Repository info |
| Contents | Read | Code statistics |
| Issues | Read | Issue metrics |
| Pull requests | Read | PR metrics |
| Actions | Read | CI/CD data |
| Administration | Read | Team/access data |

### Reporting Set
```yaml
permissions:
  metadata: read
  contents: read
  issues: read
  pull-requests: read
  actions: read
```

## Common Patterns

### Weekly Activity Report

```typescript
// Scheduled job for weekly reports
async function generateWeeklyReport(context, repository) {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  // Fetch data in parallel
  const [commits, prs, issues, workflows] = await Promise.all([
    getCommitsSince(context, weekAgo),
    getPRsSince(context, weekAgo),
    getIssuesSince(context, weekAgo),
    getWorkflowRunsSince(context, weekAgo),
  ]);

  const report = {
    period: { start: weekAgo, end: now },
    commits: {
      total: commits.length,
      byAuthor: groupBy(commits, c => c.author.login),
      additions: sum(commits, c => c.stats.additions),
      deletions: sum(commits, c => c.stats.deletions),
    },
    pullRequests: {
      opened: prs.filter(pr => new Date(pr.created_at) >= weekAgo).length,
      merged: prs.filter(pr => pr.merged_at && new Date(pr.merged_at) >= weekAgo).length,
      closed: prs.filter(pr => pr.closed_at && !pr.merged_at).length,
      avgMergeTime: calculateAvgMergeTime(prs),
    },
    issues: {
      opened: issues.filter(i => new Date(i.created_at) >= weekAgo).length,
      closed: issues.filter(i => i.closed_at && new Date(i.closed_at) >= weekAgo).length,
      avgCloseTime: calculateAvgCloseTime(issues),
    },
    ci: {
      runs: workflows.length,
      successRate: (workflows.filter(w => w.conclusion === "success").length / workflows.length) * 100,
      avgDuration: average(workflows, w => w.run_duration_ms),
    },
  };

  return formatReport(report);
}

function formatReport(report: WeeklyReport): string {
  return `
# Weekly Activity Report
**Period**: ${report.period.start.toDateString()} - ${report.period.end.toDateString()}

## Summary
| Metric | Value |
|--------|-------|
| Commits | ${report.commits.total} |
| Lines Added | +${report.commits.additions} |
| Lines Removed | -${report.commits.deletions} |
| PRs Opened | ${report.pullRequests.opened} |
| PRs Merged | ${report.pullRequests.merged} |
| Issues Opened | ${report.issues.opened} |
| Issues Closed | ${report.issues.closed} |
| CI Success Rate | ${report.ci.successRate.toFixed(1)}% |

## Top Contributors
${Object.entries(report.commits.byAuthor)
  .sort((a, b) => b[1].length - a[1].length)
  .slice(0, 5)
  .map(([author, commits]) => `- @${author}: ${commits.length} commits`)
  .join("\n")}

## PR Velocity
- Average time to merge: ${formatDuration(report.pullRequests.avgMergeTime)}
- Average issue close time: ${formatDuration(report.issues.avgCloseTime)}
  `.trim();
}
```

### Contributor Statistics

```typescript
interface ContributorStats {
  login: string;
  commits: number;
  pullRequests: number;
  issuesOpened: number;
  reviewsGiven: number;
  linesAdded: number;
  linesRemoved: number;
}

async function getContributorStats(context, since: Date): Promise<ContributorStats[]> {
  const stats = new Map<string, ContributorStats>();

  // Get commits
  const commits = await getCommitsSince(context, since);
  for (const commit of commits) {
    const login = commit.author?.login || "unknown";
    const current = stats.get(login) || createEmptyStats(login);
    current.commits++;
    current.linesAdded += commit.stats?.additions || 0;
    current.linesRemoved += commit.stats?.deletions || 0;
    stats.set(login, current);
  }

  // Get PRs
  const prs = await getPRsSince(context, since);
  for (const pr of prs) {
    const login = pr.user.login;
    const current = stats.get(login) || createEmptyStats(login);
    current.pullRequests++;
    stats.set(login, current);
  }

  // Get reviews
  for (const pr of prs) {
    const reviews = await context.octokit.pulls.listReviews(
      context.pullRequest({ pull_number: pr.number })
    );

    for (const review of reviews.data) {
      if (!review.user) continue;
      const login = review.user.login;
      const current = stats.get(login) || createEmptyStats(login);
      current.reviewsGiven++;
      stats.set(login, current);
    }
  }

  // Get issues
  const issues = await getIssuesSince(context, since);
  for (const issue of issues) {
    const login = issue.user.login;
    const current = stats.get(login) || createEmptyStats(login);
    current.issuesOpened++;
    stats.set(login, current);
  }

  return Array.from(stats.values()).sort((a, b) => b.commits - a.commits);
}
```

### Code Frequency Report

```typescript
interface CodeFrequency {
  date: string;
  additions: number;
  deletions: number;
}

async function getCodeFrequency(context): Promise<CodeFrequency[]> {
  const { data } = await context.octokit.repos.getCodeFrequencyStats(context.repo());

  return data.map(([timestamp, additions, deletions]) => ({
    date: new Date(timestamp * 1000).toISOString().split("T")[0],
    additions,
    deletions: Math.abs(deletions),
  }));
}

function generateCodeFrequencyChart(data: CodeFrequency[]): string {
  // Generate ASCII chart or return data for visualization
  const maxAdd = Math.max(...data.map(d => d.additions));
  const scale = 50 / maxAdd;

  return data.slice(-12).map(d => {
    const addBar = "█".repeat(Math.round(d.additions * scale));
    const delBar = "░".repeat(Math.round(d.deletions * scale));
    return `${d.date} +${addBar}${delBar}`;
  }).join("\n");
}
```

### Audit Log Export

```typescript
interface AuditEntry {
  timestamp: Date;
  actor: string;
  action: string;
  target: string;
  metadata: Record<string, any>;
}

// Collect audit events
app.onAny(async (context) => {
  const entry: AuditEntry = {
    timestamp: new Date(),
    actor: context.payload.sender?.login || "system",
    action: `${context.name}.${context.payload.action || "none"}`,
    target: getTarget(context),
    metadata: extractMetadata(context),
  };

  await storeAuditEntry(entry);
});

function getTarget(context): string {
  const payload = context.payload;

  if (payload.pull_request) return `PR #${payload.pull_request.number}`;
  if (payload.issue) return `Issue #${payload.issue.number}`;
  if (payload.repository) return payload.repository.full_name;
  if (payload.member) return `@${payload.member.login}`;

  return "unknown";
}

// Generate audit report
async function generateAuditReport(repository: string, since: Date): Promise<string> {
  const entries = await getAuditEntries(repository, since);

  // Group by action type
  const byAction = groupBy(entries, e => e.action);

  // Group by actor
  const byActor = groupBy(entries, e => e.actor);

  return `
# Audit Report
**Repository**: ${repository}
**Period**: ${since.toISOString()} - ${new Date().toISOString()}

## Summary
- Total events: ${entries.length}
- Unique actors: ${Object.keys(byActor).length}

## Events by Type
${Object.entries(byAction)
  .sort((a, b) => b[1].length - a[1].length)
  .map(([action, events]) => `- ${action}: ${events.length}`)
  .join("\n")}

## Top Actors
${Object.entries(byActor)
  .sort((a, b) => b[1].length - a[1].length)
  .slice(0, 10)
  .map(([actor, events]) => `- @${actor}: ${events.length} actions`)
  .join("\n")}

## Recent Events
${entries.slice(0, 20).map(e =>
  `- ${e.timestamp.toISOString()} | ${e.actor} | ${e.action} | ${e.target}`
).join("\n")}
  `.trim();
}
```

### PR Cycle Time Analysis

```typescript
interface CycleTimeMetrics {
  timeToFirstReview: number; // hours
  timeToMerge: number;
  reviewIterations: number;
  timeInReview: number;
}

async function analyzePRCycleTime(context, prNumber: number): Promise<CycleTimeMetrics> {
  const { data: pr } = await context.octokit.pulls.get(
    context.pullRequest({ pull_number: prNumber })
  );

  const { data: reviews } = await context.octokit.pulls.listReviews(
    context.pullRequest({ pull_number: prNumber })
  );

  const { data: commits } = await context.octokit.pulls.listCommits(
    context.pullRequest({ pull_number: prNumber })
  );

  const createdAt = new Date(pr.created_at);
  const mergedAt = pr.merged_at ? new Date(pr.merged_at) : null;
  const firstReview = reviews[0];

  return {
    timeToFirstReview: firstReview
      ? (new Date(firstReview.submitted_at).getTime() - createdAt.getTime()) / 3600000
      : -1,
    timeToMerge: mergedAt
      ? (mergedAt.getTime() - createdAt.getTime()) / 3600000
      : -1,
    reviewIterations: new Set(reviews.map(r => r.commit_id)).size,
    timeInReview: calculateTimeInReview(reviews, commits),
  };
}

async function generateCycleTimeReport(context, since: Date) {
  const { data: prs } = await context.octokit.pulls.list(
    context.repo({ state: "closed", sort: "updated", direction: "desc", per_page: 100 })
  );

  const mergedPRs = prs.filter(pr => pr.merged_at && new Date(pr.merged_at) >= since);

  const metrics = await Promise.all(
    mergedPRs.map(pr => analyzePRCycleTime(context, pr.number))
  );

  return {
    avgTimeToFirstReview: average(metrics.filter(m => m.timeToFirstReview > 0), m => m.timeToFirstReview),
    avgTimeToMerge: average(metrics.filter(m => m.timeToMerge > 0), m => m.timeToMerge),
    avgReviewIterations: average(metrics, m => m.reviewIterations),
    p50TimeToMerge: percentile(metrics.map(m => m.timeToMerge).filter(t => t > 0), 50),
    p90TimeToMerge: percentile(metrics.map(m => m.timeToMerge).filter(t => t > 0), 90),
  };
}
```

### Compliance Report

```typescript
interface ComplianceReport {
  repository: string;
  timestamp: Date;
  checks: ComplianceCheck[];
  overallStatus: "pass" | "fail" | "warning";
}

interface ComplianceCheck {
  name: string;
  status: "pass" | "fail" | "warning";
  details: string;
}

async function generateComplianceReport(context): Promise<ComplianceReport> {
  const checks: ComplianceCheck[] = [];

  // Branch protection
  const { data: branch } = await context.octokit.repos.getBranchProtection(
    context.repo({ branch: "main" })
  ).catch(() => ({ data: null }));

  checks.push({
    name: "Branch Protection",
    status: branch ? "pass" : "fail",
    details: branch ? "Main branch is protected" : "Main branch is not protected",
  });

  // Required reviews
  checks.push({
    name: "Required Reviews",
    status: branch?.required_pull_request_reviews ? "pass" : "warning",
    details: branch?.required_pull_request_reviews
      ? `Requires ${branch.required_pull_request_reviews.required_approving_review_count} approving reviews`
      : "No review requirements",
  });

  // Security scanning
  const { data: alerts } = await context.octokit.codeScanning.listAlertsForRepo(
    context.repo({ state: "open" })
  ).catch(() => ({ data: [] }));

  checks.push({
    name: "Security Alerts",
    status: alerts.length === 0 ? "pass" : "fail",
    details: `${alerts.length} open security alerts`,
  });

  // Dependency alerts
  const { data: vulnAlerts } = await context.octokit.dependabot.listAlertsForRepo(
    context.repo({ state: "open" })
  ).catch(() => ({ data: [] }));

  checks.push({
    name: "Dependency Vulnerabilities",
    status: vulnAlerts.length === 0 ? "pass" : "warning",
    details: `${vulnAlerts.length} open dependency alerts`,
  });

  const overallStatus = checks.some(c => c.status === "fail")
    ? "fail"
    : checks.some(c => c.status === "warning")
    ? "warning"
    : "pass";

  return {
    repository: context.payload.repository.full_name,
    timestamp: new Date(),
    checks,
    overallStatus,
  };
}
```

## Report Delivery

| Method | Use Case |
|--------|----------|
| Issue/PR Comment | In-repo visibility |
| Email | External stakeholders |
| Slack/Teams | Team channels |
| Dashboard | Real-time visualization |
| S3/GCS | Archive storage |
| Webhook | External systems |

## Security Considerations

- **Anonymize sensitive data** - Don't expose private info
- **Access control** - Limit who can view reports
- **Data retention** - Define retention policies
- **Audit the audits** - Log report generation
- **Encrypt exports** - Protect report files

## Example Apps in This Category

- **GitHub Insights** - Built-in analytics
- **Octolytics** - GitHub analytics
- **GitClear** - Engineering analytics
- **Waydev** - Developer analytics

## Related Categories

- [Monitoring](monitoring.md) - Real-time metrics
- [Project Management](project-management.md) - Sprint metrics
- [Security](security.md) - Security reporting

## See Also

- [GitHub Repository Statistics API](https://docs.github.com/en/rest/metrics/statistics)
- [GitHub Insights](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository)
