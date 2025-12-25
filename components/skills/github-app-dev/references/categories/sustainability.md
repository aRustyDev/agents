# Sustainability GitHub Apps

GitHub Apps focused on software sustainability: carbon footprint tracking, green computing, efficient CI, and environmental impact assessment.

## Common Use Cases

- **Carbon Tracking** - Measure CI/CD carbon footprint
- **Green CI** - Optimize for energy efficiency
- **Idle Resource Detection** - Find unused infrastructure
- **Efficiency Metrics** - Track compute usage
- **Green Badges** - Display sustainability metrics
- **Build Optimization** - Reduce unnecessary builds

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Trigger efficiency analysis |
| `workflow_run.completed` | Track CI carbon usage |
| `pull_request.*` | Efficiency checks |
| `schedule` | Periodic sustainability reports |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Actions | Read | Access workflow data |
| Contents | Read | Analyze codebase |
| Checks | Write | Report metrics |
| Metadata | Read | Repository info |

### Sustainability Set
```yaml
permissions:
  actions: read
  contents: read
  checks: write
```

## Common Patterns

### CI Carbon Footprint Tracking

```typescript
app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository } = context.payload;

  // Get workflow details
  const { data: jobs } = await context.octokit.actions.listJobsForWorkflowRun({
    ...context.repo(),
    run_id: workflow_run.id,
  });

  // Calculate carbon footprint
  const carbonFootprint = calculateCarbonFootprint(jobs, workflow_run);

  // Store metrics
  await storeCarbonMetrics({
    repository: repository.full_name,
    workflow: workflow_run.name,
    runId: workflow_run.id,
    durationMs: workflow_run.run_duration_ms,
    conclusion: workflow_run.conclusion,
    carbonGrams: carbonFootprint.totalGrams,
    region: detectRunnerRegion(jobs),
    timestamp: new Date(),
  });

  // Add summary to workflow
  await context.octokit.actions.createWorkflowRunSummary({
    ...context.repo(),
    run_id: workflow_run.id,
    content: `
## 🌱 Sustainability Report

| Metric | Value |
|--------|-------|
| Carbon Footprint | ${carbonFootprint.totalGrams.toFixed(2)}g CO2 |
| Energy Used | ${carbonFootprint.energyWh.toFixed(2)} Wh |
| Duration | ${formatDuration(workflow_run.run_duration_ms)} |
| Efficiency Score | ${carbonFootprint.efficiencyScore}/100 |

${carbonFootprint.recommendations.length > 0 ? `
### Recommendations
${carbonFootprint.recommendations.map(r => `- ${r}`).join("\n")}
` : ""}
    `,
  });
});

interface CarbonFootprint {
  totalGrams: number;
  energyWh: number;
  efficiencyScore: number;
  recommendations: string[];
}

function calculateCarbonFootprint(jobs, workflowRun): CarbonFootprint {
  const recommendations: string[] = [];

  // Estimate power usage based on runner type
  const powerUsage = jobs.reduce((total, job) => {
    const runnerPower = getRunnerPower(job.runner_name); // Watts
    const durationHours = (
      new Date(job.completed_at).getTime() - new Date(job.started_at).getTime()
    ) / 3600000;

    return total + runnerPower * durationHours;
  }, 0);

  // Convert to CO2 based on grid carbon intensity
  // Average US grid: ~400g CO2/kWh
  const carbonIntensity = 400; // g CO2 / kWh
  const totalGrams = (powerUsage / 1000) * carbonIntensity;

  // Calculate efficiency score
  let efficiencyScore = 100;

  // Penalize long runs
  if (workflowRun.run_duration_ms > 600000) { // > 10 min
    efficiencyScore -= 20;
    recommendations.push("Consider caching dependencies to reduce build time");
  }

  // Penalize failed runs (wasted energy)
  if (workflowRun.conclusion === "failure") {
    efficiencyScore -= 10;
    recommendations.push("Failed runs waste energy - improve test reliability");
  }

  // Check for redundant jobs
  const jobNames = jobs.map(j => j.name);
  const hasDuplicates = jobNames.length !== new Set(jobNames).size;
  if (hasDuplicates) {
    efficiencyScore -= 15;
    recommendations.push("Consolidate duplicate jobs to reduce compute usage");
  }

  return {
    totalGrams,
    energyWh: powerUsage,
    efficiencyScore: Math.max(0, efficiencyScore),
    recommendations,
  };
}

function getRunnerPower(runnerName: string): number {
  // Estimated power consumption in Watts
  if (runnerName?.includes("macos")) return 65;
  if (runnerName?.includes("windows")) return 50;
  if (runnerName?.includes("ubuntu")) return 30;
  return 40; // Default
}
```

### Build Skip Detection

```typescript
app.on("push", async (context) => {
  const { commits, after, repository } = context.payload;

  // Analyze what changed
  const changedFiles = commits.flatMap(c => [...c.added, ...c.modified, ...c.removed]);

  // Skip CI for documentation-only changes
  const docOnlyChanges = changedFiles.every(f =>
    f.match(/\.(md|txt|rst)$/) ||
    f.startsWith("docs/") ||
    f === "LICENSE" ||
    f === "CHANGELOG.md"
  );

  if (docOnlyChanges) {
    // Create skipped check run
    await context.octokit.checks.create(
      context.repo({
        name: "CI",
        head_sha: after,
        status: "completed",
        conclusion: "skipped",
        output: {
          title: "Skipped - Documentation only",
          summary: "CI skipped to save energy. Only documentation files were changed.",
        },
      })
    );

    // Track energy saved
    await trackEnergySaved({
      repository: repository.full_name,
      sha: after,
      estimatedMinutesSaved: 10,
      reason: "doc-only-changes",
    });
  }
});
```

### Green Computing Report

```typescript
// Monthly sustainability report
async function generateSustainabilityReport(context, month: Date) {
  const startOfMonth = new Date(month.getFullYear(), month.getMonth(), 1);
  const endOfMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0);

  // Get workflow runs for the month
  const runs = await getWorkflowRunsBetween(
    context.payload.repository.full_name,
    startOfMonth,
    endOfMonth
  );

  const metrics = {
    totalRuns: runs.length,
    totalMinutes: runs.reduce((sum, r) => sum + r.run_duration_ms / 60000, 0),
    totalCarbon: runs.reduce((sum, r) => sum + r.carbonGrams, 0),
    successRate: runs.filter(r => r.conclusion === "success").length / runs.length,
    energySaved: await getEnergySavedForMonth(
      context.payload.repository.full_name,
      startOfMonth,
      endOfMonth
    ),
  };

  // Compare to previous month
  const prevMonth = new Date(month);
  prevMonth.setMonth(prevMonth.getMonth() - 1);
  const prevMetrics = await getMonthMetrics(
    context.payload.repository.full_name,
    prevMonth
  );

  const carbonChange = prevMetrics
    ? ((metrics.totalCarbon - prevMetrics.totalCarbon) / prevMetrics.totalCarbon) * 100
    : 0;

  // Create report issue
  await context.octokit.issues.create(
    context.repo({
      title: `🌍 Sustainability Report - ${month.toLocaleString("default", { month: "long", year: "numeric" })}`,
      body: `
## Monthly Sustainability Summary

| Metric | Value | vs. Last Month |
|--------|-------|----------------|
| Total CI Runs | ${metrics.totalRuns} | ${formatChange(metrics.totalRuns - (prevMetrics?.totalRuns || 0))} |
| Total Runtime | ${formatDuration(metrics.totalMinutes * 60000)} | - |
| Carbon Footprint | ${(metrics.totalCarbon / 1000).toFixed(2)} kg CO2 | ${formatPercentChange(carbonChange)} |
| Energy Saved (skipped builds) | ${metrics.energySaved.toFixed(2)} kWh | - |
| Success Rate | ${(metrics.successRate * 100).toFixed(1)}% | - |

### 🌱 Environmental Impact

Your CI usage this month was equivalent to:
- ${(metrics.totalCarbon / 400).toFixed(1)} miles driven in an average car
- ${(metrics.totalCarbon / 21000).toFixed(2)} trees needed to offset annually

### Recommendations

${generateSustainabilityRecommendations(metrics)}

---
*Powered by Green CI Tracker*
      `,
      labels: ["sustainability", "report"],
    })
  );
}

function generateSustainabilityRecommendations(metrics): string {
  const recs: string[] = [];

  if (metrics.successRate < 0.9) {
    recs.push("- Improve test stability to reduce failed (wasted) runs");
  }

  if (metrics.totalMinutes > 10000) {
    recs.push("- Consider more aggressive caching strategies");
    recs.push("- Use job concurrency limits to reduce parallel waste");
  }

  if (recs.length === 0) {
    return "Great job! Your CI practices are already efficient. 🌟";
  }

  return recs.join("\n");
}
```

### Idle Resource Detection

```typescript
// Scheduled job to find unused resources
async function detectIdleResources(context) {
  const idleItems: IdleResource[] = [];

  // Check for stale branches with no activity
  const { data: branches } = await context.octokit.repos.listBranches(
    context.repo({ per_page: 100 })
  );

  for (const branch of branches) {
    if (branch.name === context.payload.repository.default_branch) continue;

    const { data: commit } = await context.octokit.repos.getCommit(
      context.repo({ ref: branch.name })
    );

    const daysSinceCommit = (Date.now() - new Date(commit.commit.author.date).getTime()) / 86400000;

    if (daysSinceCommit > 90) {
      idleItems.push({
        type: "stale-branch",
        name: branch.name,
        lastActivity: commit.commit.author.date,
        recommendation: "Delete branch or merge to reduce CI overhead",
      });
    }
  }

  // Check for workflows that run on schedule but aren't needed
  const { data: workflows } = await context.octokit.actions.listRepoWorkflows(context.repo());

  for (const workflow of workflows.workflows) {
    if (workflow.state !== "active") continue;

    // Get recent runs
    const { data: runs } = await context.octokit.actions.listWorkflowRuns({
      ...context.repo(),
      workflow_id: workflow.id,
      per_page: 10,
    });

    const allSkippedOrFailed = runs.workflow_runs.every(
      r => r.conclusion === "skipped" || r.conclusion === "failure"
    );

    if (allSkippedOrFailed && runs.workflow_runs.length >= 10) {
      idleItems.push({
        type: "ineffective-workflow",
        name: workflow.name,
        lastActivity: runs.workflow_runs[0]?.created_at,
        recommendation: "Review workflow - all recent runs skipped or failed",
      });
    }
  }

  if (idleItems.length > 0) {
    await context.octokit.issues.create(
      context.repo({
        title: "🔍 Idle Resources Detected",
        body: `
## Resource Cleanup Opportunities

The following resources appear to be idle and may be wasting compute:

${idleItems.map(item => `
### ${item.type}: \`${item.name}\`
- Last activity: ${item.lastActivity}
- Recommendation: ${item.recommendation}
`).join("\n")}

Cleaning up these resources can reduce your carbon footprint and improve CI efficiency.
        `,
        labels: ["sustainability", "cleanup"],
      })
    );
  }
}
```

### Green Badge

```typescript
// Serve sustainability badge
async function getSustainabilityBadge(repo: string): Promise<Badge> {
  const metrics = await getRepoSustainabilityMetrics(repo);

  let color: string;
  let label: string;

  if (metrics.efficiencyScore >= 80) {
    color = "brightgreen";
    label = "A";
  } else if (metrics.efficiencyScore >= 60) {
    color = "green";
    label = "B";
  } else if (metrics.efficiencyScore >= 40) {
    color = "yellow";
    label = "C";
  } else {
    color = "red";
    label = "D";
  }

  return {
    schemaVersion: 1,
    label: "sustainability",
    message: `${label} (${metrics.efficiencyScore}/100)`,
    color,
  };
}
```

## Sustainability Metrics

| Metric | Description |
|--------|-------------|
| Carbon Footprint | grams CO2 per workflow |
| Energy Usage | Wh consumed |
| Efficiency Score | 0-100 based on practices |
| Skip Rate | % of builds intelligently skipped |
| Success Rate | Failed builds = wasted energy |

## Security Considerations

- **Don't expose infrastructure details** - Abstract metrics
- **Aggregate data** - Individual run data less useful
- **Validate inputs** - Prevent metric manipulation
- **Cache computations** - Don't waste energy calculating metrics

## Example Apps in This Category

- **Green Software Foundation** tools
- **Cloud Carbon Footprint**
- **CodeCarbon**

## Related Categories

- [CI](ci.md) - Build optimization
- [Monitoring](monitoring.md) - Metrics tracking
- [Reporting](reporting.md) - Sustainability reports

## See Also

- [Green Software Foundation](https://greensoftware.foundation/)
- [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/)
- [GitHub Actions Sustainability](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)
