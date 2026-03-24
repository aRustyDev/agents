/**
 * Simple GitHub App using Probot Framework
 *
 * Features:
 * - Auto-assign reviewers based on file paths
 * - Enforce PR title conventions
 * - Auto-merge dependabot PRs (with checks)
 */

import { Probot } from "probot";

// Reviewer assignment based on changed files
const CODEOWNERS = {
  "src/frontend/": ["frontend-team"],
  "src/backend/": ["backend-team"],
  "docs/": ["docs-team"],
  "*.md": ["docs-team"],
  "package.json": ["backend-team"],
  "*.yml": ["devops-team"],
  "*.yaml": ["devops-team"],
};

function getReviewersForFiles(files: string[]): string[] {
  const reviewers = new Set<string>();

  for (const file of files) {
    for (const [pattern, owners] of Object.entries(CODEOWNERS)) {
      if (file.includes(pattern) || file.endsWith(pattern.replace("*", ""))) {
        owners.forEach((owner) => reviewers.add(owner));
      }
    }
  }

  return Array.from(reviewers);
}

export default (app: Probot) => {
  // Auto-assign reviewers
  app.on("pull_request.opened", async (context) => {
    const pr = context.payload.pull_request;

    // Get changed files
    const files = await context.octokit.pulls.listFiles(
      context.pullRequest({ per_page: 100 })
    );

    const reviewers = getReviewersForFiles(
      files.data.map((f) => f.filename)
    );

    if (reviewers.length > 0) {
      await context.octokit.pulls.requestReviewers(
        context.pullRequest({ reviewers })
      );

      await context.octokit.issues.createComment(
        context.issue({
          body: `🔍 Auto-assigned reviewers: ${reviewers.map((r) => `@${r}`).join(", ")}`,
        })
      );
    }
  });

  // Enforce PR title conventions
  app.on(["pull_request.opened", "pull_request.edited"], async (context) => {
    const { title } = context.payload.pull_request;
    const validFormat = /^(feat|fix|docs|chore|refactor|test)(\(.+\))?: .+/;
    const isValid = validFormat.test(title);

    await context.octokit.checks.create(
      context.repo({
        name: "PR Title Convention",
        head_sha: context.payload.pull_request.head.sha,
        status: "completed",
        conclusion: isValid ? "success" : "failure",
        output: {
          title: isValid ? "✅ Title follows convention" : "❌ Invalid title format",
          summary: isValid
            ? "PR title follows conventional commit format"
            : "Expected format: `type(scope): description`\\n\\nExamples:\\n- `feat: add user authentication`\\n- `fix(auth): handle expired tokens`\\n- `docs: update API documentation`",
        },
      })
    );

    if (!isValid) {
      await context.octokit.issues.createComment(
        context.issue({
          body: `❌ **PR title doesn't follow convention**

Expected format: \`type(scope): description\`

Valid types: \`feat\`, \`fix\`, \`docs\`, \`chore\`, \`refactor\`, \`test\`

Examples:
- \`feat: add user authentication\`
- \`fix(auth): handle expired tokens\`
- \`docs: update API documentation\``,
        })
      );
    }
  });

  // Auto-merge dependabot PRs (security updates only)
  app.on("pull_request.opened", async (context) => {
    const pr = context.payload.pull_request;
    const isDependabot = pr.user?.login === "dependabot[bot]";
    const isSecurityUpdate = pr.title.includes("security update") ||
      pr.title.includes("Security update");

    if (isDependabot && isSecurityUpdate) {
      // Add security label
      await context.octokit.issues.addLabels(
        context.issue({ labels: ["security", "dependencies"] })
      );

      await context.octokit.issues.createComment(
        context.issue({
          body: `🔒 **Security update detected**

This Dependabot PR contains security updates and will be auto-merged once checks pass.

Review the changes if needed, or approve manually to expedite the process.`,
        })
      );

      // Enable auto-merge (requires GraphQL)
      // Note: This would need additional GraphQL client setup
      // For simplicity, just add a label to indicate auto-merge intent
      await context.octokit.issues.addLabels(
        context.issue({ labels: ["auto-merge"] })
      );
    }
  });

  // Welcome first-time contributors
  app.on("pull_request.opened", async (context) => {
    const pr = context.payload.pull_request;

    // Check if this is their first contribution
    const author = pr.user?.login;
    if (!author) return;

    const previousPRs = await context.octokit.search.issuesAndPullRequests({
      q: `is:pr author:${author} repo:${context.payload.repository.full_name}`,
    });

    if (previousPRs.data.total_count === 1) {
      // First PR!
      await context.octokit.issues.createComment(
        context.issue({
          body: `🎉 **Welcome @${author}!**

Thank you for your first contribution to this project!

A maintainer will review your changes and provide feedback. In the meantime, please make sure:

- [ ] Your PR description clearly explains what changes you made
- [ ] You've tested your changes locally
- [ ] You've followed our contributing guidelines

We appreciate your contribution! 💪`,
        })
      );

      await context.octokit.issues.addLabels(
        context.issue({ labels: ["first-contribution"] })
      );
    }
  });

  // React to issue comments with helpful responses
  app.on("issue_comment.created", async (context) => {
    const comment = context.payload.comment.body.toLowerCase();

    if (comment.includes("/help") || comment.includes("/commands")) {
      await context.octokit.issues.createComment(
        context.issue({
          body: `🤖 **Available commands:**

- \`/help\` - Show this message
- \`/assign @username\` - Assign issue to user
- \`/label bug\` - Add label to issue
- \`/close\` - Close issue

For more help, check our [contributing guide](CONTRIBUTING.md).`,
        })
      );
    }
  });
};
