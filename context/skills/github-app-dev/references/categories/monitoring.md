# Monitoring GitHub Apps

GitHub Apps that provide monitoring and observability: repository health, activity tracking, metrics collection, and alerting.

## Common Use Cases

- **Repository Health** - Track repo activity and health
- **Activity Metrics** - Monitor commits, PRs, issues
- **CI/CD Monitoring** - Track workflow status and duration
- **Alert Integration** - Send alerts to monitoring tools
- **SLA Tracking** - Measure response times
- **Team Metrics** - Developer activity analytics

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `*` (all events) | Comprehensive activity tracking |
| `push` | Commit activity |
| `pull_request.*` | PR lifecycle |
| `workflow_run.*` | CI/CD metrics |
| `check_run.*` | Build status |
| `deployment_status.*` | Deployment metrics |
| `issues.*` | Issue activity |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Metadata | Read | Repository information |
| Checks | Read | CI status |
| Actions | Read | Workflow runs |
| Deployments | Read | Deployment status |
| Issues | Read | Issue metrics |
| Pull requests | Read | PR metrics |

### Minimal Monitoring Set
```yaml
permissions:
  metadata: read
  checks: read
  actions: read
```

### Full Observability Set
```yaml
permissions:
  metadata: read
  checks: read
  actions: read
  deployments: read
  issues: read
  pull-requests: read
  statuses: read
```

## Common Patterns

### Event Metrics Collection

```typescript
import { Counter, Histogram, Gauge } from "prom-client";

// Define metrics
const eventCounter = new Counter({
  name: "github_events_total",
  help: "Total GitHub events received",
  labelNames: ["event", "action", "repository"],
});

const prDuration = new Histogram({
  name: "github_pr_duration_seconds",
  help: "Time from PR open to merge",
  labelNames: ["repository"],
  buckets: [3600, 86400, 259200, 604800, 2592000], // 1h, 1d, 3d, 7d, 30d
});

const openPRs = new Gauge({
  name: "github_open_prs",
  help: "Number of open pull requests",
  labelNames: ["repository"],
});

// Collect metrics from webhooks
app.onAny(async (context) => {
  const repository = context.payload.repository?.full_name || "unknown";

  eventCounter.inc({
    event: context.name,
    action: context.payload.action || "none",
    repository,
  });
});

app.on("pull_request.closed", async (context) => {
  const { pull_request, repository } = context.payload;

  if (pull_request.merged) {
    const duration =
      (new Date(pull_request.merged_at).getTime() -
        new Date(pull_request.created_at).getTime()) /
      1000;

    prDuration.observe({ repository: repository.full_name }, duration);
  }
});

app.on(["pull_request.opened", "pull_request.closed"], async (context) => {
  const { repository } = context.payload;

  // Fetch current open PR count
  const { data } = await context.octokit.pulls.list(
    context.repo({ state: "open", per_page: 1 })
  );

  openPRs.set({ repository: repository.full_name }, data.length);
});
```

### CI/CD Metrics

```typescript
const workflowDuration = new Histogram({
  name: "github_workflow_duration_seconds",
  help: "Workflow run duration",
  labelNames: ["repository", "workflow", "conclusion"],
  buckets: [60, 300, 600, 1800, 3600],
});

const workflowStatus = new Gauge({
  name: "github_workflow_status",
  help: "Latest workflow status (1=success, 0=failure)",
  labelNames: ["repository", "workflow"],
});

app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository, workflow } = context.payload;

  // Record duration
  const duration =
    (new Date(workflow_run.updated_at).getTime() -
      new Date(workflow_run.run_started_at).getTime()) /
    1000;

  workflowDuration.observe(
    {
      repository: repository.full_name,
      workflow: workflow.name,
      conclusion: workflow_run.conclusion,
    },
    duration
  );

  // Update status gauge
  workflowStatus.set(
    {
      repository: repository.full_name,
      workflow: workflow.name,
    },
    workflow_run.conclusion === "success" ? 1 : 0
  );

  // Alert on failure
  if (workflow_run.conclusion === "failure") {
    await sendAlert({
      severity: "warning",
      title: `Workflow failed: ${workflow.name}`,
      repository: repository.full_name,
      url: workflow_run.html_url,
    });
  }
});
```

### Repository Health Dashboard

```typescript
interface RepositoryHealth {
  repository: string;
  metrics: {
    openPRs: number;
    stalePRs: number;
    openIssues: number;
    staleIssues: number;
    lastCommit: Date;
    ciPassRate: number;
    avgPRMergeTime: number;
    avgIssueCloseTime: number;
  };
  health: "healthy" | "warning" | "critical";
}

async function calculateRepoHealth(
  context,
  repository: string
): Promise<RepositoryHealth> {
  const [owner, repo] = repository.split("/");

  // Fetch data in parallel
  const [openPRs, openIssues, recentWorkflows, commits] = await Promise.all([
    context.octokit.pulls.list({ owner, repo, state: "open", per_page: 100 }),
    context.octokit.issues.list({ owner, repo, state: "open", per_page: 100 }),
    context.octokit.actions.listWorkflowRunsForRepo({ owner, repo, per_page: 20 }),
    context.octokit.repos.listCommits({ owner, repo, per_page: 1 }),
  ]);

  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  // Calculate stale items (older than 7 days)
  const stalePRs = openPRs.data.filter(
    (pr) => new Date(pr.updated_at) < weekAgo
  ).length;
  const staleIssues = openIssues.data.filter(
    (issue) => new Date(issue.updated_at) < weekAgo
  ).length;

  // Calculate CI pass rate
  const successfulRuns = recentWorkflows.data.workflow_runs.filter(
    (run) => run.conclusion === "success"
  ).length;
  const ciPassRate =
    (successfulRuns / recentWorkflows.data.workflow_runs.length) * 100;

  const metrics = {
    openPRs: openPRs.data.length,
    stalePRs,
    openIssues: openIssues.data.length,
    staleIssues,
    lastCommit: new Date(commits.data[0]?.commit.author.date || 0),
    ciPassRate,
    avgPRMergeTime: await calculateAvgPRMergeTime(context, owner, repo),
    avgIssueCloseTime: await calculateAvgIssueCloseTime(context, owner, repo),
  };

  // Determine health status
  let health: RepositoryHealth["health"] = "healthy";

  if (stalePRs > 5 || staleIssues > 10 || ciPassRate < 80) {
    health = "warning";
  }
  if (stalePRs > 10 || staleIssues > 20 || ciPassRate < 60) {
    health = "critical";
  }

  return { repository, metrics, health };
}
```

### Alert Integration

```typescript
interface Alert {
  severity: "info" | "warning" | "critical";
  title: string;
  message?: string;
  repository: string;
  url?: string;
  metadata?: Record<string, any>;
}

class AlertManager {
  private integrations: AlertIntegration[] = [];

  registerIntegration(integration: AlertIntegration) {
    this.integrations.push(integration);
  }

  async sendAlert(alert: Alert) {
    // Log alert
    console.log(`[${alert.severity.toUpperCase()}] ${alert.title}`);

    // Send to all integrations
    await Promise.all(
      this.integrations.map((integration) => integration.send(alert))
    );
  }
}

// Datadog integration
class DatadogIntegration implements AlertIntegration {
  async send(alert: Alert) {
    await fetch("https://api.datadoghq.com/api/v1/events", {
      method: "POST",
      headers: {
        "DD-API-KEY": process.env.DD_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: alert.title,
        text: alert.message,
        alert_type: mapSeverity(alert.severity),
        source_type_name: "github",
        tags: [
          `repository:${alert.repository}`,
          `severity:${alert.severity}`,
        ],
      }),
    });
  }
}

// PagerDuty integration
class PagerDutyIntegration implements AlertIntegration {
  async send(alert: Alert) {
    if (alert.severity !== "critical") return;

    await fetch("https://events.pagerduty.com/v2/enqueue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        routing_key: process.env.PAGERDUTY_KEY,
        event_action: "trigger",
        payload: {
          summary: alert.title,
          severity: "critical",
          source: alert.repository,
          custom_details: alert.metadata,
        },
        links: alert.url ? [{ href: alert.url, text: "View on GitHub" }] : [],
      }),
    });
  }
}
```

### Activity Tracking

```typescript
interface ActivityEvent {
  timestamp: Date;
  repository: string;
  actor: string;
  event: string;
  action: string;
  target?: string;
  metadata?: Record<string, any>;
}

app.onAny(async (context) => {
  const event: ActivityEvent = {
    timestamp: new Date(),
    repository: context.payload.repository?.full_name || "unknown",
    actor: context.payload.sender?.login || "unknown",
    event: context.name,
    action: context.payload.action || "none",
  };

  // Add target based on event type
  switch (context.name) {
    case "pull_request":
      event.target = `PR #${context.payload.pull_request.number}`;
      event.metadata = {
        title: context.payload.pull_request.title,
        state: context.payload.pull_request.state,
      };
      break;
    case "issues":
      event.target = `Issue #${context.payload.issue.number}`;
      event.metadata = {
        title: context.payload.issue.title,
        state: context.payload.issue.state,
      };
      break;
    case "push":
      event.target = context.payload.ref;
      event.metadata = {
        commits: context.payload.commits.length,
      };
      break;
  }

  // Store in time-series database
  await timeSeriesDB.insert("github_activity", event);
});
```

### SLA Monitoring

```typescript
interface SLAConfig {
  prReviewTime: number; // hours
  issueResponseTime: number; // hours
  ciDuration: number; // minutes
}

const DEFAULT_SLA: SLAConfig = {
  prReviewTime: 24,
  issueResponseTime: 4,
  ciDuration: 30,
};

async function checkSLAViolations(context, repository: string) {
  const violations: SLAViolation[] = [];
  const sla = await getSLAConfig(repository) || DEFAULT_SLA;

  // Check PR review time
  const { data: prs } = await context.octokit.pulls.list({
    owner: repository.split("/")[0],
    repo: repository.split("/")[1],
    state: "open",
  });

  for (const pr of prs) {
    const age = (Date.now() - new Date(pr.created_at).getTime()) / 3600000;

    if (pr.requested_reviewers.length > 0 && age > sla.prReviewTime) {
      violations.push({
        type: "pr_review_time",
        target: `PR #${pr.number}`,
        threshold: sla.prReviewTime,
        actual: age,
        url: pr.html_url,
      });
    }
  }

  return violations;
}
```

## Metrics Export Formats

| Format | Use Case |
|--------|----------|
| Prometheus | Time-series monitoring |
| StatsD | Lightweight metrics |
| OpenTelemetry | Unified observability |
| JSON | Custom dashboards |

## Security Considerations

- **Limit event access** - Only subscribe to needed events
- **Anonymize data** - Don't store sensitive content
- **Secure metrics endpoints** - Authenticate Prometheus scraping
- **Rate limit queries** - Prevent metric endpoint abuse
- **Audit access** - Log who views metrics

## Example Apps in This Category

- **Datadog GitHub Integration** - Full observability
- **New Relic** - Performance monitoring
- **Grafana GitHub Datasource** - Metrics visualization
- **LinearB** - Engineering metrics

## Related Categories

- [Reporting](reporting.md) - Analytics and reports
- [CI](ci.md) - Build monitoring
- [Deployment](deployment.md) - Deployment metrics

## See Also

- [Prometheus](https://prometheus.io/)
- [OpenTelemetry](https://opentelemetry.io/)
- [GitHub Insights](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-insights)
