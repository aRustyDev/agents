# Code Quality GitHub Apps

GitHub Apps that enforce code quality standards: linting, formatting, static analysis, complexity metrics, and best practice enforcement.

## Common Use Cases

- **Linting** - Language-specific style enforcement
- **Formatting** - Auto-format code on PR
- **Complexity Analysis** - Cyclomatic complexity, maintainability
- **Best Practices** - Security patterns, anti-pattern detection
- **Documentation** - Missing docs, outdated comments
- **Type Coverage** - TypeScript/Flow coverage tracking

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Analyze on every commit |
| `pull_request.opened` | Initial PR analysis |
| `pull_request.synchronize` | Re-analyze on new commits |
| `check_suite.requested` | Trigger check runs |
| `check_run.rerequested` | Re-run failed checks |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access source code |
| Checks | Write | Report analysis results |
| Pull requests | Write | Comment with suggestions |
| Statuses | Write | Set commit status |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  checks: write
```

### Full Analysis Set
```yaml
permissions:
  contents: read
  checks: write
  pull-requests: write
  statuses: write
```

## Common Patterns

### Create Check Run with Annotations

```typescript
app.on(["check_suite.requested", "check_run.rerequested"], async (context) => {
  const { head_sha } = context.payload.check_suite || context.payload.check_run;

  // Create check run as "in_progress"
  const { data: checkRun } = await context.octokit.checks.create(
    context.repo({
      name: "Code Quality",
      head_sha,
      status: "in_progress",
      started_at: new Date().toISOString(),
    })
  );

  try {
    // Get changed files
    const files = await getChangedFiles(context, head_sha);

    // Run analysis
    const results = await analyzeFiles(context, files, head_sha);

    // Update check run with results
    await context.octokit.checks.update(
      context.repo({
        check_run_id: checkRun.id,
        status: "completed",
        conclusion: results.issues.length > 0 ? "failure" : "success",
        completed_at: new Date().toISOString(),
        output: {
          title: results.issues.length > 0
            ? `${results.issues.length} issues found`
            : "No issues found",
          summary: generateSummary(results),
          annotations: results.issues.slice(0, 50).map(issue => ({
            path: issue.file,
            start_line: issue.line,
            end_line: issue.endLine || issue.line,
            annotation_level: mapSeverity(issue.severity),
            message: issue.message,
            title: issue.rule,
          })),
        },
      })
    );
  } catch (error) {
    // Report failure
    await context.octokit.checks.update(
      context.repo({
        check_run_id: checkRun.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "Analysis failed",
          summary: `Error: ${error.message}`,
        },
      })
    );
  }
});

function mapSeverity(severity: string): "notice" | "warning" | "failure" {
  switch (severity) {
    case "error": return "failure";
    case "warning": return "warning";
    default: return "notice";
  }
}
```

### Suggest Fixes via PR Review

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Get PR diff
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const suggestions = [];

  for (const file of files) {
    if (file.status === "removed") continue;

    // Get file content
    const content = await getFileContent(context, file.filename, pull_request.head.sha);

    // Run linter with fix suggestions
    const fixes = await getLinterFixes(file.filename, content);

    for (const fix of fixes) {
      suggestions.push({
        path: file.filename,
        line: fix.line,
        side: "RIGHT",
        body: `**Suggestion**: ${fix.message}\n\n\`\`\`suggestion\n${fix.suggestion}\n\`\`\``,
      });
    }
  }

  if (suggestions.length > 0) {
    // Create review with suggestions
    await context.octokit.pulls.createReview(
      context.pullRequest({
        event: "COMMENT",
        comments: suggestions.slice(0, 20), // GitHub limits to ~60 comments
      })
    );
  }
});
```

### Track Quality Metrics Over Time

```typescript
app.on("push", async (context) => {
  const { ref, repository, after } = context.payload;

  // Only track default branch
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  // Get all files
  const files = await getAllFiles(context, after);

  // Calculate metrics
  const metrics = await calculateMetrics(context, files, after);

  // Store metrics
  await storeMetrics({
    repo: repository.full_name,
    sha: after,
    timestamp: new Date().toISOString(),
    metrics: {
      totalLines: metrics.totalLines,
      codeLines: metrics.codeLines,
      commentLines: metrics.commentLines,
      complexity: metrics.averageComplexity,
      duplications: metrics.duplicatePercent,
      testCoverage: metrics.testCoverage,
      techDebt: metrics.techDebtMinutes,
    },
  });

  // Check for regressions
  const previousMetrics = await getPreviousMetrics(repository.full_name);

  if (previousMetrics && metrics.techDebtMinutes > previousMetrics.techDebt * 1.1) {
    // Tech debt increased by more than 10%
    await context.octokit.repos.createCommitStatus(
      context.repo({
        sha: after,
        state: "failure",
        context: "quality/tech-debt",
        description: `Tech debt increased by ${Math.round((metrics.techDebtMinutes / previousMetrics.techDebt - 1) * 100)}%`,
      })
    );
  }
});
```

### Language-Specific Analysis

```typescript
const ANALYZERS: Record<string, Analyzer> = {
  javascript: new ESLintAnalyzer(),
  typescript: new ESLintAnalyzer({ parser: "@typescript-eslint/parser" }),
  python: new PylintAnalyzer(),
  go: new GolangCIAnalyzer(),
  rust: new ClippyAnalyzer(),
  ruby: new RubocopAnalyzer(),
};

async function analyzeFiles(context, files, sha) {
  const results = { issues: [], metrics: {} };

  // Group files by language
  const byLanguage = groupBy(files, f => detectLanguage(f.filename));

  for (const [language, langFiles] of Object.entries(byLanguage)) {
    const analyzer = ANALYZERS[language];

    if (analyzer) {
      const langResults = await analyzer.analyze(context, langFiles, sha);
      results.issues.push(...langResults.issues);
      Object.assign(results.metrics, langResults.metrics);
    }
  }

  return results;
}

function detectLanguage(filename: string): string {
  const ext = filename.split(".").pop();
  const extToLanguage: Record<string, string> = {
    js: "javascript",
    jsx: "javascript",
    ts: "typescript",
    tsx: "typescript",
    py: "python",
    go: "go",
    rs: "rust",
    rb: "ruby",
  };
  return extToLanguage[ext] || "unknown";
}
```

## Configuration File Detection

```typescript
const CONFIG_FILES: Record<string, string[]> = {
  eslint: [".eslintrc.js", ".eslintrc.json", ".eslintrc.yml", ".eslintrc"],
  prettier: [".prettierrc", ".prettierrc.js", ".prettierrc.json", "prettier.config.js"],
  stylelint: [".stylelintrc", ".stylelintrc.js", ".stylelintrc.json"],
  pylint: [".pylintrc", "pylintrc", "pyproject.toml"],
};

async function findConfig(context, sha, tool: string): Promise<string | null> {
  const possibleFiles = CONFIG_FILES[tool] || [];

  for (const configFile of possibleFiles) {
    try {
      const { data } = await context.octokit.repos.getContent(
        context.repo({ path: configFile, ref: sha })
      );
      if ("content" in data) {
        return Buffer.from(data.content, "base64").toString();
      }
    } catch {
      // File doesn't exist, try next
    }
  }

  return null;
}
```

## Quality Gates

```typescript
interface QualityGate {
  name: string;
  check: (metrics: Metrics) => boolean;
  message: (metrics: Metrics) => string;
}

const QUALITY_GATES: QualityGate[] = [
  {
    name: "coverage",
    check: m => m.testCoverage >= 80,
    message: m => `Coverage ${m.testCoverage}% < 80%`,
  },
  {
    name: "complexity",
    check: m => m.averageComplexity <= 10,
    message: m => `Complexity ${m.averageComplexity} > 10`,
  },
  {
    name: "duplications",
    check: m => m.duplicatePercent <= 3,
    message: m => `Duplications ${m.duplicatePercent}% > 3%`,
  },
];

async function enforceQualityGates(context, sha, metrics) {
  const failures = QUALITY_GATES.filter(gate => !gate.check(metrics));

  for (const gate of QUALITY_GATES) {
    await context.octokit.repos.createCommitStatus(
      context.repo({
        sha,
        state: gate.check(metrics) ? "success" : "failure",
        context: `quality/${gate.name}`,
        description: gate.check(metrics) ? "Passed" : gate.message(metrics),
      })
    );
  }

  return failures.length === 0;
}
```

## Security Considerations

- **Sandbox analysis** - Run untrusted code in isolation
- **Resource limits** - Cap memory/CPU for analysis
- **Timeout handling** - Don't hang on large files
- **Avoid code execution** - Static analysis only
- **Sanitize output** - Don't leak secrets in reports

## Example Apps in This Category

- **SonarCloud** - Comprehensive code analysis
- **Codacy** - Automated code reviews
- **DeepSource** - Static analysis platform
- **Code Climate** - Quality metrics
- **Reviewdog** - Multi-linter aggregator

## Related Categories

- [Code Review](code-review.md) - Human review assistance
- [Testing](testing.md) - Test coverage analysis
- [Security](security.md) - Security-focused analysis

## See Also

- [GitHub Check Runs API](https://docs.github.com/en/rest/checks/runs)
- [Code Annotations](https://docs.github.com/en/rest/checks/runs#create-a-check-run)
