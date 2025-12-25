# Project Management GitHub Apps

GitHub Apps that integrate with project management tools: issue tracking, sprint planning, roadmaps, and team workflows.

## Common Use Cases

- **External PM Sync** - Sync with Jira, Linear, Asana
- **Sprint Management** - Manage sprints via GitHub
- **Roadmap Tracking** - Link issues to milestones
- **Workflow Automation** - Move cards on boards
- **Estimation** - Story points and sizing
- **Dependencies** - Track blocking issues

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.*` | Track issue lifecycle |
| `pull_request.*` | Link PRs to issues |
| `issue_comment.created` | Commands and updates |
| `project_card.*` | Board automation |
| `milestone.*` | Sprint/release tracking |
| `label.*` | Status changes |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Write | Manage issues |
| Pull requests | Write | Link PRs |
| Projects | Write | Manage project boards |
| Metadata | Read | Repository info |

### Project Management Set
```yaml
permissions:
  issues: write
  pull-requests: write
  projects: write
  metadata: read
```

## Common Patterns

### Sync with External PM Tool

```typescript
// Bi-directional sync with Jira
app.on("issues.opened", async (context) => {
  const { issue, repository } = context.payload;

  // Create corresponding Jira issue
  const jiraIssue = await jiraClient.createIssue({
    project: mapRepoToJiraProject(repository.full_name),
    summary: issue.title,
    description: issue.body,
    issueType: mapLabelsToIssueType(issue.labels),
    customFields: {
      githubUrl: issue.html_url,
      githubNumber: issue.number,
    },
  });

  // Store mapping
  await storeIssueMapping({
    github: { repo: repository.full_name, number: issue.number },
    jira: jiraIssue.key,
  });

  // Add Jira link to GitHub issue
  await context.octokit.issues.createComment(
    context.issue({
      body: `Linked to Jira: [${jiraIssue.key}](${jiraIssue.url})`,
    })
  );
});

// Sync status changes
app.on("issues.closed", async (context) => {
  const mapping = await getIssueMapping(
    context.payload.repository.full_name,
    context.payload.issue.number
  );

  if (mapping) {
    await jiraClient.transitionIssue(mapping.jira, "Done");
  }
});

// Webhook from Jira to GitHub
async function handleJiraWebhook(payload: JiraWebhook) {
  if (payload.webhookEvent === "jira:issue_updated") {
    const mapping = await getIssueMappingByJira(payload.issue.key);
    if (!mapping) return;

    const [owner, repo] = mapping.github.repo.split("/");

    // Sync status back to GitHub
    if (payload.changelog.items.some(i => i.field === "status")) {
      const newStatus = payload.issue.fields.status.name;

      if (newStatus === "Done") {
        await octokit.issues.update({
          owner,
          repo,
          issue_number: mapping.github.number,
          state: "closed",
        });
      }

      // Update labels based on status
      await syncLabelsFromJiraStatus(mapping.github, newStatus);
    }
  }
}
```

### Project Board Automation

```typescript
app.on("issues.labeled", async (context) => {
  const { issue, label, repository } = context.payload;

  const boardConfig = await context.config("project-board.yml", {
    columnMapping: {
      "in-progress": "In Progress",
      "needs-review": "Review",
      "done": "Done",
    },
  });

  const targetColumn = boardConfig.columnMapping[label.name];
  if (!targetColumn) return;

  // Find project board
  const { data: projects } = await context.octokit.projects.listForRepo(
    context.repo()
  );

  for (const project of projects) {
    // Get columns
    const { data: columns } = await context.octokit.projects.listColumns({
      project_id: project.id,
    });

    const column = columns.find((c) => c.name === targetColumn);
    if (!column) continue;

    // Find existing card for this issue
    let existingCard = null;
    for (const col of columns) {
      const { data: cards } = await context.octokit.projects.listCards({
        column_id: col.id,
      });
      existingCard = cards.find((c) => c.content_url?.includes(`/issues/${issue.number}`));
      if (existingCard) break;
    }

    if (existingCard) {
      // Move card
      await context.octokit.projects.moveCard({
        card_id: existingCard.id,
        position: "top",
        column_id: column.id,
      });
    } else {
      // Create card
      await context.octokit.projects.createCard({
        column_id: column.id,
        content_id: issue.id,
        content_type: "Issue",
      });
    }
  }
});
```

### Sprint Management

```typescript
interface Sprint {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  milestone: string;
}

app.on("issue_comment.created", async (context) => {
  const { comment, issue } = context.payload;

  // Handle sprint commands
  if (comment.body.startsWith("/sprint")) {
    const [, command, ...args] = comment.body.split(" ");

    switch (command) {
      case "add":
        await addToSprint(context, issue, args[0]);
        break;
      case "remove":
        await removeFromSprint(context, issue);
        break;
      case "estimate":
        await setEstimate(context, issue, parseInt(args[0]));
        break;
    }
  }
});

async function addToSprint(context, issue, sprintName: string) {
  const sprint = await getSprintByName(sprintName);
  if (!sprint) {
    await context.octokit.issues.createComment(
      context.issue({ body: `Sprint "${sprintName}" not found.` })
    );
    return;
  }

  // Add milestone
  await context.octokit.issues.update(
    context.issue({ milestone: sprint.milestone })
  );

  // Add sprint label
  await context.octokit.issues.addLabels(
    context.issue({ labels: [`sprint:${sprint.name}`] })
  );

  await context.octokit.reactions.createForIssueComment({
    ...context.issue(),
    comment_id: context.payload.comment.id,
    content: "+1",
  });
}

async function setEstimate(context, issue, points: number) {
  if (![1, 2, 3, 5, 8, 13].includes(points)) {
    await context.octokit.issues.createComment(
      context.issue({ body: "Invalid estimate. Use Fibonacci: 1, 2, 3, 5, 8, 13" })
    );
    return;
  }

  // Store estimate
  await storeEstimate({
    repo: context.payload.repository.full_name,
    issue: issue.number,
    points,
  });

  // Add label
  const existingLabels = issue.labels
    .filter((l) => !l.name.startsWith("points:"))
    .map((l) => l.name);

  await context.octokit.issues.setLabels(
    context.issue({ labels: [...existingLabels, `points:${points}`] })
  );
}
```

### Dependency Tracking

```typescript
app.on("issue_comment.created", async (context) => {
  const { comment, issue } = context.payload;

  // Parse "blocks #123" or "blocked by #456"
  const blocksMatch = comment.body.match(/blocks?\s+#(\d+)/i);
  const blockedByMatch = comment.body.match(/blocked\s+by\s+#(\d+)/i);

  if (blocksMatch) {
    const blockedIssue = parseInt(blocksMatch[1]);
    await addDependency(context, issue.number, blockedIssue, "blocks");

    await context.octokit.issues.createComment({
      ...context.repo(),
      issue_number: blockedIssue,
      body: `This issue is blocked by #${issue.number}`,
    });
  }

  if (blockedByMatch) {
    const blockingIssue = parseInt(blockedByMatch[1]);
    await addDependency(context, blockingIssue, issue.number, "blocks");

    await context.octokit.issues.addLabels(
      context.issue({ labels: ["blocked"] })
    );
  }
});

// Auto-unblock when blocking issue is closed
app.on("issues.closed", async (context) => {
  const { issue } = context.payload;

  const blockedIssues = await getBlockedBy(
    context.payload.repository.full_name,
    issue.number
  );

  for (const blockedIssue of blockedIssues) {
    // Check if still blocked by other issues
    const otherBlockers = await getBlockers(
      context.payload.repository.full_name,
      blockedIssue
    );

    const openBlockers = [];
    for (const blocker of otherBlockers) {
      if (blocker !== issue.number) {
        const { data } = await context.octokit.issues.get({
          ...context.repo(),
          issue_number: blocker,
        });
        if (data.state === "open") {
          openBlockers.push(blocker);
        }
      }
    }

    if (openBlockers.length === 0) {
      // Remove blocked label
      await context.octokit.issues.removeLabel({
        ...context.repo(),
        issue_number: blockedIssue,
        name: "blocked",
      });

      await context.octokit.issues.createComment({
        ...context.repo(),
        issue_number: blockedIssue,
        body: `🎉 This issue is no longer blocked! #${issue.number} has been closed.`,
      });
    }
  }
});
```

### Roadmap Integration

```typescript
interface RoadmapItem {
  id: string;
  title: string;
  quarter: string;
  status: "planned" | "in-progress" | "completed";
  issues: number[];
}

async function updateRoadmapFromMilestone(context, milestone) {
  const roadmapItem = await getRoadmapItemForMilestone(milestone.title);
  if (!roadmapItem) return;

  // Get all issues in milestone
  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({
      milestone: milestone.number,
      state: "all",
    })
  );

  const total = issues.length;
  const closed = issues.filter((i) => i.state === "closed").length;
  const progress = total > 0 ? (closed / total) * 100 : 0;

  // Update roadmap status
  let status: RoadmapItem["status"] = "planned";
  if (progress > 0 && progress < 100) status = "in-progress";
  if (progress === 100) status = "completed";

  await updateRoadmapItem(roadmapItem.id, {
    status,
    progress,
    issues: issues.map((i) => i.number),
  });

  // Update external roadmap tool
  await syncToRoadmapTool(roadmapItem, { progress, status });
}
```

## PM Tool Integrations

| Tool | Sync Pattern |
|------|-------------|
| Jira | REST API + Webhooks |
| Linear | GraphQL API |
| Asana | REST API |
| Monday.com | REST API |
| Notion | REST API |
| Trello | REST API + Webhooks |
| Clubhouse/Shortcut | REST API |

## Security Considerations

- **Validate external webhooks** - Check signatures
- **Limit sync scope** - Don't sync private data to public tools
- **Audit changes** - Log all synced updates
- **Handle rate limits** - Queue sync operations
- **Token rotation** - Refresh external API tokens

## Example Apps in This Category

- **ZenHub** - GitHub-native PM
- **Zube** - Kanban for GitHub
- **Jira GitHub Integration** - Official sync
- **Linear** - Modern issue tracking

## Related Categories

- [Open Source Management](open-source-management.md) - Community workflows
- [Reporting](reporting.md) - Project analytics
- [Support](support.md) - Issue handling

## See Also

- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work)
