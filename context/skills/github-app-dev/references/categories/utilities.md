# Utilities GitHub Apps

GitHub Apps that provide general-purpose automation and helper functions: issue management, PR automation, file management, and workflow utilities.

## Common Use Cases

- **Issue Automation** - Auto-labeling, stale issue cleanup
- **PR Helpers** - Title validation, size limits
- **File Management** - Auto-generate files, cleanup
- **Workflow Triggers** - Cross-repo automation
- **Comment Commands** - Slash commands in issues/PRs
- **Repository Maintenance** - Housekeeping automation

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.*` | Issue automation |
| `pull_request.*` | PR utilities |
| `issue_comment.created` | Command handling |
| `push` | File updates |
| `schedule` | Periodic cleanup |
| `repository.*` | Repo setup automation |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Write | Manage issues |
| Pull requests | Write | Manage PRs |
| Contents | Write | File management |
| Metadata | Read | Repository info |

### Utilities Set
```yaml
permissions:
  issues: write
  pull-requests: write
  contents: write
  metadata: read
```

## Common Patterns

### Slash Commands Handler

```typescript
interface Command {
  name: string;
  description: string;
  allowedRoles: ("maintainer" | "collaborator" | "author" | "anyone")[];
  handler: (context: Context, args: string[]) => Promise<void>;
}

const commands: Map<string, Command> = new Map([
  ["assign", {
    name: "assign",
    description: "Assign issue to user(s)",
    allowedRoles: ["maintainer", "collaborator"],
    handler: async (context, args) => {
      const assignees = args.map(a => a.replace("@", ""));
      await context.octokit.issues.addAssignees(
        context.issue({ assignees })
      );
    },
  }],
  ["label", {
    name: "label",
    description: "Add labels to issue",
    allowedRoles: ["maintainer", "collaborator"],
    handler: async (context, args) => {
      await context.octokit.issues.addLabels(
        context.issue({ labels: args })
      );
    },
  }],
  ["close", {
    name: "close",
    description: "Close issue",
    allowedRoles: ["maintainer", "author"],
    handler: async (context, args) => {
      const reason = args[0] === "completed" ? "completed" : "not_planned";
      await context.octokit.issues.update(
        context.issue({ state: "closed", state_reason: reason })
      );
    },
  }],
  ["reopen", {
    name: "reopen",
    description: "Reopen issue",
    allowedRoles: ["maintainer", "author"],
    handler: async (context, args) => {
      await context.octokit.issues.update(
        context.issue({ state: "open" })
      );
    },
  }],
]);

app.on("issue_comment.created", async (context) => {
  const { comment, issue, sender } = context.payload;

  // Parse command
  const match = comment.body.match(/^\/(\w+)(?:\s+(.*))?$/m);
  if (!match) return;

  const [, commandName, argsString] = match;
  const command = commands.get(commandName);

  if (!command) {
    await context.octokit.reactions.createForIssueComment({
      ...context.repo(),
      comment_id: comment.id,
      content: "confused",
    });
    return;
  }

  // Check permissions
  const userRole = await getUserRole(context, sender.login, issue);
  if (!command.allowedRoles.includes(userRole) && !command.allowedRoles.includes("anyone")) {
    await context.octokit.reactions.createForIssueComment({
      ...context.repo(),
      comment_id: comment.id,
      content: "-1",
    });
    return;
  }

  // Execute command
  try {
    const args = argsString ? argsString.split(/\s+/) : [];
    await command.handler(context, args);

    await context.octokit.reactions.createForIssueComment({
      ...context.repo(),
      comment_id: comment.id,
      content: "+1",
    });
  } catch (error) {
    await context.octokit.reactions.createForIssueComment({
      ...context.repo(),
      comment_id: comment.id,
      content: "confused",
    });
  }
});

async function getUserRole(context, username: string, issue): Promise<string> {
  // Check if author
  if (issue.user.login === username) return "author";

  // Check collaborator status
  try {
    const { data } = await context.octokit.repos.getCollaboratorPermissionLevel(
      context.repo({ username })
    );

    if (["admin", "maintain"].includes(data.permission)) return "maintainer";
    if (["write", "triage"].includes(data.permission)) return "collaborator";
  } catch {
    // Not a collaborator
  }

  return "anyone";
}
```

### Stale Issue/PR Cleanup

```typescript
interface StaleConfig {
  daysUntilStale: number;
  daysUntilClose: number;
  staleLabel: string;
  exemptLabels: string[];
  staleMessage: string;
  closeMessage: string;
}

const config: StaleConfig = {
  daysUntilStale: 60,
  daysUntilClose: 7,
  staleLabel: "stale",
  exemptLabels: ["pinned", "security", "bug"],
  staleMessage: "This issue has been automatically marked as stale due to inactivity.",
  closeMessage: "This issue has been closed due to continued inactivity.",
};

// Scheduled job for stale processing
async function processStaleItems(context) {
  const now = new Date();

  // Find issues to mark stale
  const staleDate = new Date(now.getTime() - config.daysUntilStale * 86400000);

  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({
      state: "open",
      sort: "updated",
      direction: "asc",
      per_page: 100,
    })
  );

  for (const issue of issues) {
    // Skip exempt labels
    if (issue.labels.some(l => config.exemptLabels.includes(l.name))) continue;

    const lastUpdate = new Date(issue.updated_at);
    const hasStaleLabel = issue.labels.some(l => l.name === config.staleLabel);

    if (!hasStaleLabel && lastUpdate < staleDate) {
      // Mark as stale
      await context.octokit.issues.addLabels(
        context.repo({ issue_number: issue.number, labels: [config.staleLabel] })
      );

      await context.octokit.issues.createComment(
        context.repo({ issue_number: issue.number, body: config.staleMessage })
      );
    } else if (hasStaleLabel) {
      // Check if should close
      const closeDate = new Date(now.getTime() - config.daysUntilClose * 86400000);

      if (lastUpdate < closeDate) {
        await context.octokit.issues.update(
          context.repo({
            issue_number: issue.number,
            state: "closed",
            state_reason: "not_planned",
          })
        );

        await context.octokit.issues.createComment(
          context.repo({ issue_number: issue.number, body: config.closeMessage })
        );
      }
    }
  }
}

// Remove stale label on activity
app.on(["issues.edited", "issue_comment.created"], async (context) => {
  const issue = context.payload.issue;

  const hasStaleLabel = issue.labels.some(l => l.name === config.staleLabel);

  if (hasStaleLabel) {
    await context.octokit.issues.removeLabel(
      context.issue({ name: config.staleLabel })
    );
  }
});
```

### Auto-Labeler

```typescript
interface LabelRule {
  label: string;
  patterns: {
    files?: string[];
    title?: RegExp;
    body?: RegExp;
    branch?: RegExp;
  };
}

const labelRules: LabelRule[] = [
  {
    label: "documentation",
    patterns: {
      files: ["docs/**", "*.md", "README*"],
      title: /\bdocs?\b|\bdocumentation\b/i,
    },
  },
  {
    label: "bug",
    patterns: {
      title: /\bbug\b|\bfix\b|\bissue\b|\berror\b/i,
      branch: /^(bug|fix|hotfix)\//,
    },
  },
  {
    label: "feature",
    patterns: {
      title: /\bfeature\b|\badd\b|\bnew\b/i,
      branch: /^(feature|feat)\//,
    },
  },
  {
    label: "tests",
    patterns: {
      files: ["**/*.test.*", "**/*.spec.*", "**/test/**", "**/tests/**"],
    },
  },
  {
    label: "dependencies",
    patterns: {
      files: ["package.json", "yarn.lock", "Cargo.toml", "go.mod", "requirements.txt"],
    },
  },
  {
    label: "ci",
    patterns: {
      files: [".github/workflows/**", ".gitlab-ci.yml", "Jenkinsfile"],
    },
  },
];

app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;
  const labelsToAdd: string[] = [];

  // Get changed files
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );
  const changedFiles = files.map(f => f.filename);

  for (const rule of labelRules) {
    let matches = false;

    // Check file patterns
    if (rule.patterns.files) {
      matches = changedFiles.some(file =>
        rule.patterns.files!.some(pattern => minimatch(file, pattern))
      );
    }

    // Check title pattern
    if (!matches && rule.patterns.title) {
      matches = rule.patterns.title.test(pull_request.title);
    }

    // Check body pattern
    if (!matches && rule.patterns.body && pull_request.body) {
      matches = rule.patterns.body.test(pull_request.body);
    }

    // Check branch pattern
    if (!matches && rule.patterns.branch) {
      matches = rule.patterns.branch.test(pull_request.head.ref);
    }

    if (matches) {
      labelsToAdd.push(rule.label);
    }
  }

  if (labelsToAdd.length > 0) {
    await context.octokit.issues.addLabels(
      context.issue({ labels: labelsToAdd })
    );
  }
});
```

### PR Size Checker

```typescript
interface SizeConfig {
  small: number;
  medium: number;
  large: number;
  xlarge: number;
}

const sizeConfig: SizeConfig = {
  small: 50,
  medium: 200,
  large: 500,
  xlarge: 1000,
};

app.on(["pull_request.opened", "pull_request.synchronize"], async (context) => {
  const { pull_request } = context.payload;

  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const totalChanges = files.reduce((sum, f) => sum + f.additions + f.deletions, 0);

  // Determine size label
  let sizeLabel: string;
  let sizeEmoji: string;

  if (totalChanges <= sizeConfig.small) {
    sizeLabel = "size/S";
    sizeEmoji = "🟢";
  } else if (totalChanges <= sizeConfig.medium) {
    sizeLabel = "size/M";
    sizeEmoji = "🟡";
  } else if (totalChanges <= sizeConfig.large) {
    sizeLabel = "size/L";
    sizeEmoji = "🟠";
  } else if (totalChanges <= sizeConfig.xlarge) {
    sizeLabel = "size/XL";
    sizeEmoji = "🔴";
  } else {
    sizeLabel = "size/XXL";
    sizeEmoji = "💥";
  }

  // Remove existing size labels
  const existingLabels = pull_request.labels
    .filter(l => !l.name.startsWith("size/"))
    .map(l => l.name);

  await context.octokit.issues.setLabels(
    context.issue({ labels: [...existingLabels, sizeLabel] })
  );

  // Warn on large PRs
  if (totalChanges > sizeConfig.large) {
    // Check if we already commented
    const { data: comments } = await context.octokit.issues.listComments(
      context.issue()
    );

    const existingWarning = comments.find(c =>
      c.body?.includes("Large PR Warning") && c.user?.type === "Bot"
    );

    if (!existingWarning) {
      await context.octokit.issues.createComment(
        context.issue({
          body: `
## ${sizeEmoji} Large PR Warning

This PR has **${totalChanges}** lines changed across **${files.length}** files.

Large PRs are harder to review and more likely to introduce bugs. Consider:

- Breaking into smaller, focused PRs
- Separating refactoring from feature changes
- Adding detailed descriptions for each section

| Metric | Value |
|--------|-------|
| Files Changed | ${files.length} |
| Additions | +${files.reduce((s, f) => s + f.additions, 0)} |
| Deletions | -${files.reduce((s, f) => s + f.deletions, 0)} |
| Total Changes | ${totalChanges} |
          `,
        })
      );
    }
  }
});
```

### Repository Setup Automation

```typescript
app.on("repository.created", async (context) => {
  const { repository } = context.payload;

  // Create standard labels
  const labels = [
    { name: "bug", color: "d73a4a", description: "Something isn't working" },
    { name: "enhancement", color: "a2eeef", description: "New feature or request" },
    { name: "documentation", color: "0075ca", description: "Improvements to docs" },
    { name: "good first issue", color: "7057ff", description: "Good for newcomers" },
    { name: "help wanted", color: "008672", description: "Extra attention needed" },
    { name: "question", color: "d876e3", description: "Further information requested" },
    { name: "wontfix", color: "ffffff", description: "Will not be worked on" },
    { name: "duplicate", color: "cfd3d7", description: "Already exists" },
    { name: "priority:high", color: "ff0000", description: "High priority" },
    { name: "priority:medium", color: "ffff00", description: "Medium priority" },
    { name: "priority:low", color: "00ff00", description: "Low priority" },
  ];

  for (const label of labels) {
    try {
      await context.octokit.issues.createLabel(
        context.repo({ ...label })
      );
    } catch (error) {
      // Label might already exist
    }
  }

  // Create welcome issue
  await context.octokit.issues.create(
    context.repo({
      title: "Welcome to your new repository!",
      body: `
# Welcome! 👋

Your repository has been set up with:

- ✅ Standard issue labels
- ✅ Branch protection (if enabled)
- ✅ Basic CI workflow (if templates available)

## Next Steps

1. [ ] Add a README.md
2. [ ] Configure branch protection rules
3. [ ] Set up CI/CD workflows
4. [ ] Add contributing guidelines

Feel free to close this issue once you've completed setup!
      `,
      labels: ["documentation"],
    })
  );

  // Create basic files if repo is empty
  if (repository.size === 0) {
    await context.octokit.repos.createOrUpdateFileContents(
      context.repo({
        path: "README.md",
        message: "Initial commit: Add README",
        content: Buffer.from(`# ${repository.name}\n\n${repository.description || ""}\n`).toString("base64"),
      })
    );
  }
});
```

### Cross-Repository Dispatch

```typescript
app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository } = context.payload;

  // Check if this triggers downstream repos
  const config = await getRepoConfig(context);

  if (config.dispatch?.onSuccess && workflow_run.conclusion === "success") {
    for (const target of config.dispatch.onSuccess) {
      const [owner, repo] = target.repo.split("/");

      await context.octokit.repos.createDispatchEvent({
        owner,
        repo,
        event_type: target.event || "upstream-success",
        client_payload: {
          source_repo: repository.full_name,
          source_workflow: workflow_run.name,
          source_sha: workflow_run.head_sha,
          source_branch: workflow_run.head_branch,
        },
      });
    }
  }
});

// Handle incoming dispatches
app.on("repository_dispatch", async (context) => {
  const { action, client_payload } = context.payload;

  if (action === "upstream-success") {
    // Trigger downstream workflow
    await context.octokit.actions.createWorkflowDispatch({
      ...context.repo(),
      workflow_id: "downstream.yml",
      ref: "main",
      inputs: {
        upstream_repo: client_payload.source_repo,
        upstream_sha: client_payload.source_sha,
      },
    });
  }
});
```

### File Auto-Generation

```typescript
app.on("push", async (context) => {
  const { commits, ref, repository } = context.payload;

  // Only on default branch
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  const changedFiles = commits.flatMap(c => [...c.added, ...c.modified]);

  // Regenerate table of contents
  if (changedFiles.some(f => f.startsWith("docs/"))) {
    await regenerateTableOfContents(context);
  }

  // Update contributors file
  if (changedFiles.length > 0) {
    await updateContributorsFile(context);
  }
});

async function regenerateTableOfContents(context) {
  // Get all docs
  const { data: tree } = await context.octokit.git.getTree(
    context.repo({ tree_sha: "HEAD", recursive: "true" })
  );

  const docs = tree.tree
    .filter(t => t.path?.startsWith("docs/") && t.path.endsWith(".md"))
    .sort((a, b) => (a.path || "").localeCompare(b.path || ""));

  let toc = "# Documentation\n\n";

  for (const doc of docs) {
    const depth = (doc.path?.match(/\//g) || []).length - 1;
    const indent = "  ".repeat(depth);
    const name = doc.path?.split("/").pop()?.replace(".md", "") || "";

    toc += `${indent}- [${name}](${doc.path})\n`;
  }

  // Update TOC file
  const { data: existing } = await context.octokit.repos.getContent(
    context.repo({ path: "docs/README.md" })
  ).catch(() => ({ data: null }));

  await context.octokit.repos.createOrUpdateFileContents(
    context.repo({
      path: "docs/README.md",
      message: "docs: Update table of contents",
      content: Buffer.from(toc).toString("base64"),
      sha: existing?.sha,
    })
  );
}

async function updateContributorsFile(context) {
  // Get contributors
  const { data: contributors } = await context.octokit.repos.listContributors(
    context.repo({ per_page: 100 })
  );

  let content = "# Contributors\n\nThanks to all our contributors!\n\n";

  for (const contributor of contributors) {
    content += `- [@${contributor.login}](${contributor.html_url}) - ${contributor.contributions} contributions\n`;
  }

  const { data: existing } = await context.octokit.repos.getContent(
    context.repo({ path: "CONTRIBUTORS.md" })
  ).catch(() => ({ data: null }));

  await context.octokit.repos.createOrUpdateFileContents(
    context.repo({
      path: "CONTRIBUTORS.md",
      message: "docs: Update contributors list",
      content: Buffer.from(content).toString("base64"),
      sha: existing?.sha,
    })
  );
}
```

## Common Commands

| Command | Description |
|---------|-------------|
| `/assign @user` | Assign issue to user |
| `/label bug` | Add label |
| `/unlabel bug` | Remove label |
| `/close` | Close issue |
| `/reopen` | Reopen issue |
| `/cc @user` | Mention user |
| `/approve` | Approve (custom) |
| `/help` | Show commands |

## Security Considerations

- **Validate command permissions** - Check user roles
- **Rate limit commands** - Prevent abuse
- **Sanitize inputs** - Escape user-provided values
- **Audit actions** - Log all automated changes
- **Limit file access** - Don't expose sensitive files

## Example Apps in This Category

- **Probot Stale** - Stale issue management
- **Probot Auto-assign** - PR/issue assignment
- **Probot Settings** - Repo configuration
- **Mergify** - PR automation
- **Kodiak** - Auto-merge

## Related Categories

- [Open Source Management](open-source-management.md) - Community tools
- [Project Management](project-management.md) - Issue tracking
- [Code Review](code-review.md) - PR helpers

## See Also

- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work)
- [Saved Replies](https://docs.github.com/en/get-started/writing-on-github/working-with-saved-replies)
- [Repository Dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch)
