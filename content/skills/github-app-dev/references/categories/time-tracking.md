# Time Tracking GitHub Apps

GitHub Apps that track time spent on issues, PRs, and projects: time logging, estimation, and productivity analytics.

## Common Use Cases

- **Time Logging** - Log hours on issues/PRs
- **Estimation Tracking** - Compare estimates to actuals
- **Sprint Analytics** - Team velocity metrics
- **Billing Integration** - Client billing from GitHub
- **Productivity Metrics** - Developer time insights
- **Report Generation** - Timesheet exports

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.*` | Issue lifecycle events |
| `pull_request.*` | PR time tracking |
| `issue_comment.created` | Time logging commands |
| `project_card.*` | Kanban time tracking |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Write | Add time labels/comments |
| Pull requests | Read | Track PR time |
| Metadata | Read | Repository info |
| Projects | Read | Board time tracking |

### Time Tracking Set
```yaml
permissions:
  issues: write
  pull-requests: read
  metadata: read
```

## Common Patterns

### Time Logging via Comments

```typescript
app.on("issue_comment.created", async (context) => {
  const { comment, issue, sender } = context.payload;

  // Parse time logging commands
  // /time 2h 30m
  // /time 1.5h
  // /time 45m
  const timeMatch = comment.body.match(/\/time\s+([\d.]+)\s*(h|hr|hours?|m|min|minutes?)/i);

  if (!timeMatch) return;

  const value = parseFloat(timeMatch[1]);
  const unit = timeMatch[2].toLowerCase();

  let minutes: number;
  if (unit.startsWith("h")) {
    minutes = value * 60;
  } else {
    minutes = value;
  }

  // Store time entry
  await storeTimeEntry({
    repository: context.payload.repository.full_name,
    issue: issue.number,
    user: sender.login,
    minutes,
    timestamp: new Date(),
    comment: comment.id,
  });

  // Get total time
  const totalTime = await getTotalTimeForIssue(
    context.payload.repository.full_name,
    issue.number
  );

  // React to acknowledge
  await context.octokit.reactions.createForIssueComment({
    ...context.repo(),
    comment_id: comment.id,
    content: "+1",
  });

  // Update issue with time info
  await updateTimeLabel(context, issue, totalTime);
});

async function updateTimeLabel(context, issue, totalMinutes: number) {
  // Remove existing time labels
  const existingLabels = issue.labels
    .filter(l => !l.name.startsWith("time:"))
    .map(l => l.name);

  // Add new time label
  const hours = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  const timeLabel = hours > 0 ? `time:${hours}h${mins > 0 ? `${mins}m` : ""}` : `time:${mins}m`;

  await context.octokit.issues.setLabels(
    context.issue({ labels: [...existingLabels, timeLabel] })
  );
}
```

### Estimation vs Actual Tracking

```typescript
interface TimeEstimate {
  issue: number;
  estimatedMinutes: number;
  actualMinutes: number;
  accuracy: number;
}

app.on("issues.closed", async (context) => {
  const { issue } = context.payload;

  // Get estimate from label
  const estimateLabel = issue.labels.find(l => l.name.startsWith("estimate:"));
  if (!estimateLabel) return;

  const estimatedMinutes = parseTimeLabel(estimateLabel.name.replace("estimate:", ""));

  // Get actual time
  const actualMinutes = await getTotalTimeForIssue(
    context.payload.repository.full_name,
    issue.number
  );

  if (actualMinutes === 0) return;

  // Calculate accuracy
  const accuracy = Math.min(estimatedMinutes, actualMinutes) / Math.max(estimatedMinutes, actualMinutes);

  // Store for analytics
  await storeEstimateAccuracy({
    repository: context.payload.repository.full_name,
    issue: issue.number,
    estimated: estimatedMinutes,
    actual: actualMinutes,
    accuracy,
    user: issue.assignee?.login,
  });

  // Comment with summary
  await context.octokit.issues.createComment(
    context.issue({
      body: `
## ⏱️ Time Summary

| Metric | Value |
|--------|-------|
| Estimated | ${formatDuration(estimatedMinutes * 60000)} |
| Actual | ${formatDuration(actualMinutes * 60000)} |
| Accuracy | ${(accuracy * 100).toFixed(0)}% |
| Difference | ${formatDifference(actualMinutes - estimatedMinutes)} |
      `,
    })
  );
});

function formatDifference(diffMinutes: number): string {
  if (diffMinutes > 0) {
    return `+${formatDuration(diffMinutes * 60000)} over`;
  } else if (diffMinutes < 0) {
    return `${formatDuration(Math.abs(diffMinutes) * 60000)} under`;
  }
  return "Exact!";
}
```

### Sprint Time Report

```typescript
interface SprintTimeReport {
  sprint: string;
  startDate: Date;
  endDate: Date;
  totalHours: number;
  byUser: Record<string, number>;
  byIssue: Array<{ issue: number; title: string; hours: number }>;
  velocity: number;
}

async function generateSprintTimeReport(
  context,
  milestone: string
): Promise<SprintTimeReport> {
  // Get milestone details
  const { data: milestones } = await context.octokit.issues.listMilestones(
    context.repo()
  );

  const sprint = milestones.find(m => m.title === milestone);
  if (!sprint) throw new Error(`Milestone ${milestone} not found`);

  // Get issues in milestone
  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({
      milestone: sprint.number,
      state: "all",
    })
  );

  const byUser: Record<string, number> = {};
  const byIssue: SprintTimeReport["byIssue"] = [];
  let totalMinutes = 0;

  for (const issue of issues) {
    const entries = await getTimeEntries(
      context.payload.repository.full_name,
      issue.number
    );

    const issueMinutes = entries.reduce((sum, e) => sum + e.minutes, 0);
    totalMinutes += issueMinutes;

    byIssue.push({
      issue: issue.number,
      title: issue.title,
      hours: issueMinutes / 60,
    });

    for (const entry of entries) {
      byUser[entry.user] = (byUser[entry.user] || 0) + entry.minutes;
    }
  }

  // Calculate velocity (points per hour)
  const totalPoints = issues.reduce((sum, issue) => {
    const pointLabel = issue.labels.find(l => l.name.startsWith("points:"));
    return sum + (pointLabel ? parseInt(pointLabel.name.split(":")[1]) : 0);
  }, 0);

  return {
    sprint: milestone,
    startDate: sprint.due_on ? new Date(sprint.due_on) : new Date(),
    endDate: sprint.closed_at ? new Date(sprint.closed_at) : new Date(),
    totalHours: totalMinutes / 60,
    byUser: Object.fromEntries(
      Object.entries(byUser).map(([k, v]) => [k, v / 60])
    ),
    byIssue: byIssue.sort((a, b) => b.hours - a.hours),
    velocity: totalMinutes > 0 ? totalPoints / (totalMinutes / 60) : 0,
  };
}
```

### Automatic Time Tracking

```typescript
// Track time based on label changes (In Progress -> Done)
app.on("issues.labeled", async (context) => {
  const { issue, label, sender } = context.payload;

  if (label.name === "in-progress") {
    // Start timer
    await startTimer({
      repository: context.payload.repository.full_name,
      issue: issue.number,
      user: sender.login,
      startedAt: new Date(),
    });
  }
});

app.on("issues.unlabeled", async (context) => {
  const { issue, label, sender } = context.payload;

  if (label.name === "in-progress") {
    // Stop timer and log time
    const timer = await stopTimer({
      repository: context.payload.repository.full_name,
      issue: issue.number,
      user: sender.login,
    });

    if (timer) {
      const minutes = (Date.now() - timer.startedAt.getTime()) / 60000;

      await storeTimeEntry({
        repository: context.payload.repository.full_name,
        issue: issue.number,
        user: sender.login,
        minutes: Math.round(minutes),
        timestamp: new Date(),
        automatic: true,
      });

      await context.octokit.issues.createComment(
        context.issue({
          body: `⏱️ Automatically logged ${formatDuration(minutes * 60000)} of work time.`,
        })
      );
    }
  }
});
```

### Billing Integration

```typescript
interface BillableEntry {
  date: Date;
  hours: number;
  description: string;
  issue: number;
  user: string;
  rate?: number;
}

async function exportBillableTime(
  context,
  startDate: Date,
  endDate: Date,
  clientLabel?: string
): Promise<BillableEntry[]> {
  const entries: BillableEntry[] = [];

  // Get all issues in date range
  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({
      since: startDate.toISOString(),
      state: "all",
      labels: clientLabel,
    })
  );

  for (const issue of issues) {
    const timeEntries = await getTimeEntries(
      context.payload.repository.full_name,
      issue.number
    );

    for (const entry of timeEntries) {
      if (entry.timestamp >= startDate && entry.timestamp <= endDate) {
        entries.push({
          date: entry.timestamp,
          hours: entry.minutes / 60,
          description: `#${issue.number}: ${issue.title}`,
          issue: issue.number,
          user: entry.user,
        });
      }
    }
  }

  return entries;
}

// Export as CSV
function exportToCSV(entries: BillableEntry[]): string {
  const headers = "Date,Hours,Description,Issue,User\n";
  const rows = entries.map(e =>
    `${e.date.toISOString().split("T")[0]},${e.hours.toFixed(2)},"${e.description}",${e.issue},${e.user}`
  );

  return headers + rows.join("\n");
}
```

### Weekly Timesheet

```typescript
async function generateWeeklyTimesheet(context, user: string, weekStart: Date) {
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 7);

  const entries = await getTimeEntriesForUser(
    context.payload.repository.owner.login,
    user,
    weekStart,
    weekEnd
  );

  // Group by day
  const byDay: Record<string, number> = {};
  const byIssue: Record<number, { title: string; minutes: number }> = {};

  for (const entry of entries) {
    const day = entry.timestamp.toISOString().split("T")[0];
    byDay[day] = (byDay[day] || 0) + entry.minutes;

    if (!byIssue[entry.issue]) {
      byIssue[entry.issue] = { title: "", minutes: 0 };
    }
    byIssue[entry.issue].minutes += entry.minutes;
  }

  const totalMinutes = Object.values(byDay).reduce((a, b) => a + b, 0);

  return `
## Weekly Timesheet: @${user}
**Week of ${weekStart.toDateString()}**

### Daily Breakdown
| Day | Hours |
|-----|-------|
${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day, i) => {
  const date = new Date(weekStart);
  date.setDate(date.getDate() + i);
  const dateStr = date.toISOString().split("T")[0];
  const hours = (byDay[dateStr] || 0) / 60;
  return `| ${day} ${date.getDate()} | ${hours.toFixed(1)}h |`;
}).join("\n")}
| **Total** | **${(totalMinutes / 60).toFixed(1)}h** |

### By Issue
${Object.entries(byIssue)
  .sort((a, b) => b[1].minutes - a[1].minutes)
  .map(([issue, data]) => `- #${issue}: ${(data.minutes / 60).toFixed(1)}h`)
  .join("\n")}
  `;
}
```

## Time Commands

| Command | Description |
|---------|-------------|
| `/time 2h` | Log 2 hours |
| `/time 30m` | Log 30 minutes |
| `/estimate 4h` | Set estimate |
| `/timesheet` | Show your time |
| `/timer start` | Start timer |
| `/timer stop` | Stop timer |

## Security Considerations

- **Validate time entries** - Prevent unrealistic values
- **Audit time edits** - Track changes to entries
- **Privacy** - Respect individual time data
- **Rate limiting** - Prevent time entry spam
- **Authorization** - Only allow own time entries

## Example Apps in This Category

- **WakaTime** - Automatic time tracking
- **Clockify** - Time tracker
- **Toggl** - Time tracking integration
- **Everhour** - Project time tracking

## Related Categories

- [Project Management](project-management.md) - Sprint tracking
- [Reporting](reporting.md) - Time analytics
- [Utilities](utilities.md) - Automation

## See Also

- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Issue Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work)
