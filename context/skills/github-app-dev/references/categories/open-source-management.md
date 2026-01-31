# Open Source Management GitHub Apps

GitHub Apps that help maintain open source projects: community management, contributor workflows, release automation, and project governance.

## Common Use Cases

- **Issue Triage** - Auto-label and categorize issues
- **Contributor Onboarding** - Welcome new contributors
- **Stale Management** - Handle inactive issues/PRs
- **Release Notes** - Generate changelogs
- **CLA Management** - Contributor license agreements
- **Community Health** - Enforce community standards

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.opened` | Triage new issues |
| `pull_request.opened` | Welcome contributors |
| `issue_comment.created` | Bot commands |
| `fork` | Track project spread |
| `star.created` | Community growth |
| `member.added` | Team management |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Write | Label, comment, close |
| Pull requests | Write | Label, comment, merge |
| Contents | Read | Access contribution files |
| Metadata | Read | Repository info |
| Members | Read | Contributor info |

### Open Source Management Set
```yaml
permissions:
  issues: write
  pull-requests: write
  contents: read
  metadata: read
```

## Common Patterns

### Welcome New Contributors

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request, repository, sender } = context.payload;

  // Check if first-time contributor
  const { data: prs } = await context.octokit.pulls.list(
    context.repo({
      creator: sender.login,
      state: "all",
      per_page: 2,
    })
  );

  if (prs.length === 1) {
    // First PR!
    await context.octokit.issues.createComment(
      context.issue({
        body: `
👋 Welcome @${sender.login}!

Thank you for your first contribution to ${repository.name}! 🎉

A maintainer will review your PR soon. In the meantime, please:

- [ ] Make sure all tests pass
- [ ] Sign the [Contributor License Agreement](link-to-cla)
- [ ] Read our [Contributing Guide](link-to-contributing)

If you have questions, feel free to ask in this PR or join our [Discord](link-to-discord).
        `,
      })
    );

    await context.octokit.issues.addLabels(
      context.issue({ labels: ["first-contribution"] })
    );
  }
});
```

### Auto-Label Issues

```typescript
interface LabelRule {
  labels: string[];
  match: (issue: Issue) => boolean;
}

const LABEL_RULES: LabelRule[] = [
  {
    labels: ["bug"],
    match: (issue) =>
      issue.title.toLowerCase().includes("bug") ||
      issue.body?.toLowerCase().includes("steps to reproduce"),
  },
  {
    labels: ["feature-request"],
    match: (issue) =>
      issue.title.toLowerCase().includes("feature") ||
      issue.title.toLowerCase().includes("request"),
  },
  {
    labels: ["documentation"],
    match: (issue) =>
      issue.title.toLowerCase().includes("doc") ||
      issue.body?.toLowerCase().includes("documentation"),
  },
  {
    labels: ["question"],
    match: (issue) =>
      issue.title.includes("?") ||
      issue.title.toLowerCase().includes("how to"),
  },
];

app.on("issues.opened", async (context) => {
  const { issue } = context.payload;
  const labelsToAdd: string[] = [];

  for (const rule of LABEL_RULES) {
    if (rule.match(issue)) {
      labelsToAdd.push(...rule.labels);
    }
  }

  if (labelsToAdd.length > 0) {
    await context.octokit.issues.addLabels(
      context.issue({ labels: [...new Set(labelsToAdd)] })
    );
  }

  // Add needs-triage if no labels matched
  if (labelsToAdd.length === 0) {
    await context.octokit.issues.addLabels(
      context.issue({ labels: ["needs-triage"] })
    );
  }
});
```

### Stale Issue Management

```typescript
// Scheduled job for stale management
async function processStaleItems(context, repository) {
  const config = await context.config("stale.yml", {
    daysUntilStale: 60,
    daysUntilClose: 7,
    staleLabel: "stale",
    exemptLabels: ["pinned", "security", "critical"],
    staleMessage: "This issue has been automatically marked as stale.",
    closeMessage: "This issue has been automatically closed due to inactivity.",
  });

  const now = new Date();
  const staleDate = new Date(now.getTime() - config.daysUntilStale * 24 * 60 * 60 * 1000);
  const closeDate = new Date(now.getTime() - (config.daysUntilStale + config.daysUntilClose) * 24 * 60 * 60 * 1000);

  // Find issues to mark stale
  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({
      state: "open",
      per_page: 100,
      sort: "updated",
      direction: "asc",
    })
  );

  for (const issue of issues) {
    // Skip if has exempt label
    if (issue.labels.some(l => config.exemptLabels.includes(l.name))) {
      continue;
    }

    const updatedAt = new Date(issue.updated_at);
    const isStale = issue.labels.some(l => l.name === config.staleLabel);

    if (isStale && updatedAt < closeDate) {
      // Close stale issue
      await context.octokit.issues.update(
        context.repo({
          issue_number: issue.number,
          state: "closed",
          state_reason: "not_planned",
        })
      );

      await context.octokit.issues.createComment(
        context.repo({
          issue_number: issue.number,
          body: config.closeMessage,
        })
      );
    } else if (!isStale && updatedAt < staleDate) {
      // Mark as stale
      await context.octokit.issues.addLabels(
        context.repo({
          issue_number: issue.number,
          labels: [config.staleLabel],
        })
      );

      await context.octokit.issues.createComment(
        context.repo({
          issue_number: issue.number,
          body: config.staleMessage,
        })
      );
    }
  }
}
```

### CLA (Contributor License Agreement)

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request, sender } = context.payload;

  // Check if user has signed CLA
  const hasSigned = await checkCLASignature(sender.login);

  if (!hasSigned) {
    await context.octokit.checks.create(
      context.repo({
        name: "CLA",
        head_sha: pull_request.head.sha,
        status: "completed",
        conclusion: "action_required",
        output: {
          title: "CLA not signed",
          summary: `Please sign the Contributor License Agreement to continue.`,
        },
        actions: [
          {
            label: "Sign CLA",
            description: "Click to sign the CLA",
            identifier: "sign-cla",
          },
        ],
      })
    );

    await context.octokit.issues.createComment(
      context.issue({
        body: `
Thanks for your contribution! Before we can merge this, you need to sign our [Contributor License Agreement](${CLA_URL}).

Once signed, comment \`@bot recheck\` to verify.
        `,
      })
    );
  } else {
    await context.octokit.checks.create(
      context.repo({
        name: "CLA",
        head_sha: pull_request.head.sha,
        status: "completed",
        conclusion: "success",
        output: {
          title: "CLA signed",
          summary: `@${sender.login} has signed the CLA.`,
        },
      })
    );
  }
});

// Handle CLA signing callback
async function handleCLASigned(username: string) {
  await recordCLASignature(username);

  // Re-check all open PRs from this user
  const prs = await getOpenPRsByUser(username);

  for (const pr of prs) {
    await octokit.checks.create({
      owner: pr.owner,
      repo: pr.repo,
      name: "CLA",
      head_sha: pr.sha,
      status: "completed",
      conclusion: "success",
    });
  }
}
```

### Release Notes Generation

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  // Get previous release
  const { data: releases } = await context.octokit.repos.listReleases(
    context.repo({ per_page: 2 })
  );

  const previousRelease = releases[1];
  if (!previousRelease) return;

  // Get commits between releases
  const { data: comparison } = await context.octokit.repos.compareCommits(
    context.repo({
      base: previousRelease.tag_name,
      head: release.tag_name,
    })
  );

  // Get PRs from commits
  const prNumbers = new Set<number>();
  for (const commit of comparison.commits) {
    const match = commit.commit.message.match(/#(\d+)/);
    if (match) {
      prNumbers.add(parseInt(match[1]));
    }
  }

  // Fetch PR details and categorize
  const categories = {
    features: [],
    fixes: [],
    docs: [],
    chores: [],
    breaking: [],
  };

  for (const prNumber of prNumbers) {
    const { data: pr } = await context.octokit.pulls.get(
      context.repo({ pull_number: prNumber })
    );

    const category = categorizePR(pr);
    categories[category].push({
      number: pr.number,
      title: pr.title,
      author: pr.user.login,
    });
  }

  // Generate release notes
  const releaseNotes = formatReleaseNotes(categories);

  // Update release body
  await context.octokit.repos.updateRelease(
    context.repo({
      release_id: release.id,
      body: `${release.body}\n\n${releaseNotes}`,
    })
  );
});

function formatReleaseNotes(categories): string {
  let notes = "";

  if (categories.breaking.length > 0) {
    notes += "## ⚠️ Breaking Changes\n";
    notes += categories.breaking.map(formatPRLine).join("\n") + "\n\n";
  }

  if (categories.features.length > 0) {
    notes += "## ✨ New Features\n";
    notes += categories.features.map(formatPRLine).join("\n") + "\n\n";
  }

  if (categories.fixes.length > 0) {
    notes += "## 🐛 Bug Fixes\n";
    notes += categories.fixes.map(formatPRLine).join("\n") + "\n\n";
  }

  if (categories.docs.length > 0) {
    notes += "## 📚 Documentation\n";
    notes += categories.docs.map(formatPRLine).join("\n") + "\n\n";
  }

  return notes;
}

function formatPRLine(pr): string {
  return `- ${pr.title} (#${pr.number}) @${pr.author}`;
}
```

### Bot Commands

```typescript
const COMMANDS: Record<string, CommandHandler> = {
  "assign me": async (context) => {
    await context.octokit.issues.addAssignees(
      context.issue({ assignees: [context.payload.sender.login] })
    );
  },
  "unassign me": async (context) => {
    await context.octokit.issues.removeAssignees(
      context.issue({ assignees: [context.payload.sender.login] })
    );
  },
  "needs review": async (context) => {
    await context.octokit.issues.addLabels(
      context.issue({ labels: ["needs-review"] })
    );
  },
  recheck: async (context) => {
    // Re-run checks
    await recheckCLA(context);
  },
  "good first issue": async (context, isMaintainer) => {
    if (!isMaintainer) return;
    await context.octokit.issues.addLabels(
      context.issue({ labels: ["good first issue", "help wanted"] })
    );
  },
};

app.on("issue_comment.created", async (context) => {
  const { comment, issue, sender } = context.payload;

  // Check for bot mention
  if (!comment.body.includes("@my-bot")) return;

  const isMaintainer = await checkMaintainer(context, sender.login);

  for (const [command, handler] of Object.entries(COMMANDS)) {
    if (comment.body.toLowerCase().includes(command)) {
      await handler(context, isMaintainer);
    }
  }
});
```

## Community Health Files

| File | Purpose |
|------|---------|
| `CONTRIBUTING.md` | Contribution guidelines |
| `CODE_OF_CONDUCT.md` | Community standards |
| `SECURITY.md` | Security policy |
| `.github/ISSUE_TEMPLATE/` | Issue templates |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |
| `CODEOWNERS` | Review assignment |

## Security Considerations

- **Validate bot commands** - Check permissions before acting
- **Rate limit actions** - Prevent spam/abuse
- **Audit maintainer actions** - Log privileged operations
- **Secure CLA storage** - Protect signature data
- **Prevent DoS** - Handle large repos gracefully

## Example Apps in This Category

- **Probot Stale** - Stale issue management
- **CLA Assistant** - CLA management
- **All Contributors** - Contributor recognition
- **Release Drafter** - Release notes automation

## Related Categories

- [Project Management](project-management.md) - Issue tracking
- [Publishing](publishing.md) - Release automation
- [Support](support.md) - Community support

## See Also

- [GitHub Community Guidelines](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines)
- [Open Source Guides](https://opensource.guide/)
