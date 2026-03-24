/**
 * Auto-labeling Pattern for GitHub Apps
 *
 * Automatically assign labels to PRs and issues based on various criteria.
 * This is one of the most common GitHub App patterns.
 */

import { Octokit } from "@octokit/rest";

// =============================================================================
// Basic Title-Based Labeling
// =============================================================================

/**
 * Label PRs based on conventional commit titles
 */
export async function labelPRByTitle(
  octokit: Octokit,
  owner: string,
  repo: string,
  prNumber: number,
  title: string
): Promise<string[]> {
  const labels: string[] = [];

  // Map commit types to labels
  if (title.match(/^feat(\(.+\))?:/)) labels.push("enhancement");
  if (title.match(/^fix(\(.+\))?:/)) labels.push("bug");
  if (title.match(/^docs(\(.+\))?:/)) labels.push("documentation");
  if (title.match(/^test(\(.+\))?:/)) labels.push("testing");
  if (title.match(/^refactor(\(.+\))?:/)) labels.push("refactor");
  if (title.match(/^perf(\(.+\))?:/)) labels.push("performance");
  if (title.match(/^chore(\(.+\))?:/)) labels.push("maintenance");

  // Size indicators
  if (title.includes("!:") || title.includes("BREAKING CHANGE")) {
    labels.push("breaking-change");
  }

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: prNumber,
      labels,
    });
  }

  return labels;
}

// =============================================================================
// File-Based Labeling
// =============================================================================

/**
 * Label PRs based on changed files
 */
export async function labelPRByFiles(
  octokit: Octokit,
  owner: string,
  repo: string,
  prNumber: number
): Promise<string[]> {
  const labels: string[] = [];

  // Get PR files
  const { data: files } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber,
  });

  const filePaths = files.map(file => file.filename);

  // Frontend files
  if (filePaths.some(path =>
    path.includes("/frontend/") ||
    path.endsWith(".tsx") ||
    path.endsWith(".jsx") ||
    path.endsWith(".css") ||
    path.endsWith(".scss")
  )) {
    labels.push("frontend");
  }

  // Backend files
  if (filePaths.some(path =>
    path.includes("/backend/") ||
    path.includes("/api/") ||
    path.endsWith(".py") ||
    path.endsWith(".go") ||
    path.endsWith(".java")
  )) {
    labels.push("backend");
  }

  // Database changes
  if (filePaths.some(path =>
    path.includes("migration") ||
    path.includes(".sql") ||
    path.includes("schema")
  )) {
    labels.push("database");
  }

  // Documentation changes
  if (filePaths.some(path =>
    path.endsWith(".md") ||
    path.includes("/docs/") ||
    path.includes("README")
  )) {
    labels.push("documentation");
  }

  // Configuration changes
  if (filePaths.some(path =>
    path.includes("config") ||
    path.endsWith(".yml") ||
    path.endsWith(".yaml") ||
    path.endsWith(".json") ||
    path.includes(".env")
  )) {
    labels.push("configuration");
  }

  // Test files
  if (filePaths.some(path =>
    path.includes("test") ||
    path.includes("spec") ||
    path.endsWith(".test.ts") ||
    path.endsWith(".spec.ts")
  )) {
    labels.push("testing");
  }

  // CI/CD changes
  if (filePaths.some(path =>
    path.includes(".github/workflows/") ||
    path.includes("Dockerfile") ||
    path.includes("docker-compose")
  )) {
    labels.push("ci/cd");
  }

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: prNumber,
      labels,
    });
  }

  return labels;
}

// =============================================================================
// Size-Based Labeling
// =============================================================================

/**
 * Label PRs based on their size (lines changed)
 */
export async function labelPRBySize(
  octokit: Octokit,
  owner: string,
  repo: string,
  prNumber: number
): Promise<string[]> {
  const labels: string[] = [];

  // Get PR details
  const { data: pr } = await octokit.pulls.get({
    owner,
    repo,
    pull_number: prNumber,
  });

  const additions = pr.additions || 0;
  const deletions = pr.deletions || 0;
  const totalChanges = additions + deletions;

  // Size categories
  if (totalChanges < 10) {
    labels.push("size/xs");
  } else if (totalChanges < 50) {
    labels.push("size/s");
  } else if (totalChanges < 200) {
    labels.push("size/m");
  } else if (totalChanges < 500) {
    labels.push("size/l");
  } else {
    labels.push("size/xl");
  }

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: prNumber,
      labels,
    });
  }

  return labels;
}

// =============================================================================
// Repository Custom Properties-Based Labeling
// =============================================================================

/**
 * Label PRs based on repository configuration
 */
export async function labelPRByRepoConfig(
  octokit: Octokit,
  owner: string,
  repo: string,
  prNumber: number
): Promise<string[]> {
  const labels: string[] = [];

  try {
    // Get repository custom properties
    const { data: repoProperties } = await octokit.request(
      "GET /repos/{owner}/{repo}/custom-properties",
      { owner, repo }
    );

    const config = repoProperties.reduce((acc, prop) => {
      acc[prop.property_name] = prop.value;
      return acc;
    }, {} as Record<string, string>);

    // Language-specific labeling
    const language = config.language || config.primary_language;
    if (language) {
      labels.push(`lang/${language.toLowerCase()}`);

      // Language-specific additional labels
      switch (language.toLowerCase()) {
        case "rust":
          labels.push("performance-critical");
          break;
        case "javascript":
        case "typescript":
          labels.push("needs-testing");
          break;
        case "python":
          labels.push("type-checking");
          break;
        case "go":
          labels.push("concurrent-safe");
          break;
      }
    }

    // Project type-specific labeling
    const projectType = config.project_type;
    if (projectType) {
      switch (projectType.toLowerCase()) {
        case "library":
          labels.push("api-change");
          break;
        case "service":
          labels.push("service-impact");
          break;
        case "cli":
          labels.push("user-facing");
          break;
      }
    }

    // Environment impact
    const environments = config.environments?.split(",") || [];
    if (environments.includes("production")) {
      labels.push("production-impact");
    }

    if (labels.length > 0) {
      await octokit.issues.addLabels({
        owner,
        repo,
        issue_number: prNumber,
        labels,
      });
    }
  } catch (error) {
    // Repository doesn't support custom properties or other error
    console.warn("Could not fetch repository configuration:", error);
  }

  return labels;
}

// =============================================================================
// Advanced Pattern: Issue Template-Based Labeling
// =============================================================================

/**
 * Label issues based on issue template used
 */
export async function labelIssueByTemplate(
  octokit: Octokit,
  owner: string,
  repo: string,
  issueNumber: number,
  body: string
): Promise<string[]> {
  const labels: string[] = [];

  // Detect issue template based on body content
  if (body.includes("## Bug Report") || body.includes("### Expected behavior")) {
    labels.push("bug", "triage");
  }

  if (body.includes("## Feature Request") || body.includes("### Describe the solution")) {
    labels.push("enhancement", "needs-discussion");
  }

  if (body.includes("## Question") || body.includes("### What are you trying to do")) {
    labels.push("question", "support");
  }

  if (body.includes("## Documentation") || body.includes("### Documentation issue")) {
    labels.push("documentation", "good-first-issue");
  }

  // Priority indicators
  if (body.toLowerCase().includes("urgent") || body.toLowerCase().includes("critical")) {
    labels.push("priority/high");
  } else if (body.toLowerCase().includes("low priority")) {
    labels.push("priority/low");
  } else {
    labels.push("priority/medium");
  }

  // Complexity estimation
  if (body.toLowerCase().includes("simple") || body.toLowerCase().includes("easy")) {
    labels.push("good-first-issue");
  }

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: issueNumber,
      labels,
    });
  }

  return labels;
}

// =============================================================================
// Complete Auto-Labeling Service
// =============================================================================

export class AutoLabelingService {
  constructor(private octokit: Octokit) {}

  async labelPullRequest(payload: any): Promise<void> {
    const { owner, name: repo } = payload.repository;
    const prNumber = payload.pull_request.number;

    console.log(`Auto-labeling PR #${prNumber} in ${owner}/${repo}`);

    try {
      // Run all labeling strategies
      const labelPromises = [
        this.labelByTitle(owner, repo, prNumber, payload.pull_request.title),
        this.labelByFiles(owner, repo, prNumber),
        this.labelBySize(owner, repo, prNumber),
        this.labelByRepoConfig(owner, repo, prNumber),
      ];

      const labelResults = await Promise.allSettled(labelPromises);
      const allLabels = labelResults
        .filter(result => result.status === "fulfilled")
        .map(result => (result as PromiseFulfilledResult<string[]>).value)
        .flat();

      console.log(`Applied labels: ${allLabels.join(", ")}`);
    } catch (error) {
      console.error("Auto-labeling failed:", error);
      // Don't throw - labeling failures shouldn't break webhook processing
    }
  }

  async labelIssue(payload: any): Promise<void> {
    const { owner, name: repo } = payload.repository;
    const issueNumber = payload.issue.number;
    const body = payload.issue.body || "";

    console.log(`Auto-labeling issue #${issueNumber} in ${owner}/${repo}`);

    try {
      const labels = await this.labelIssueByTemplate(owner, repo, issueNumber, body);
      console.log(`Applied labels: ${labels.join(", ")}`);
    } catch (error) {
      console.error("Issue auto-labeling failed:", error);
    }
  }

  private async labelByTitle(owner: string, repo: string, prNumber: number, title: string) {
    return labelPRByTitle(this.octokit, owner, repo, prNumber, title);
  }

  private async labelByFiles(owner: string, repo: string, prNumber: number) {
    return labelPRByFiles(this.octokit, owner, repo, prNumber);
  }

  private async labelBySize(owner: string, repo: string, prNumber: number) {
    return labelPRBySize(this.octokit, owner, repo, prNumber);
  }

  private async labelByRepoConfig(owner: string, repo: string, prNumber: number) {
    return labelPRByRepoConfig(this.octokit, owner, repo, prNumber);
  }

  private async labelIssueByTemplate(owner: string, repo: string, issueNumber: number, body: string) {
    return labelIssueByTemplate(this.octokit, owner, repo, issueNumber, body);
  }
}

// =============================================================================
// Usage Example
// =============================================================================

export function setupAutoLabelingWebhooks(webhooks: any, octokit: Octokit) {
  const labelingService = new AutoLabelingService(octokit);

  webhooks.on("pull_request.opened", async ({ payload }: any) => {
    await labelingService.labelPullRequest(payload);
  });

  webhooks.on("issues.opened", async ({ payload }: any) => {
    await labelingService.labelIssue(payload);
  });

  // Also handle PR synchronization (new commits)
  webhooks.on("pull_request.synchronize", async ({ payload }: any) => {
    // Re-evaluate size-based labels when PR changes
    const { owner, name: repo } = payload.repository;
    const prNumber = payload.pull_request.number;

    await labelPRBySize(octokit, owner, repo, prNumber);
  });
}
