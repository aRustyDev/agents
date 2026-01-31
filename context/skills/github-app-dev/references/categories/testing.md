# Testing GitHub Apps

GitHub Apps focused on testing automation: test execution, coverage tracking, flaky test detection, and test result reporting.

## Common Use Cases

- **Test Execution** - Run tests on push/PR
- **Coverage Tracking** - Track and enforce coverage
- **Flaky Detection** - Identify unreliable tests
- **Test Reports** - Visualize test results
- **Mutation Testing** - Test quality validation
- **Performance Testing** - Load and stress tests

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Run tests on commit |
| `pull_request.*` | PR test gates |
| `check_suite.requested` | Trigger test runs |
| `check_run.rerequested` | Re-run failed tests |
| `workflow_run.completed` | Process test results |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Checks | Write | Report test results |
| Statuses | Write | Set commit status |
| Contents | Read | Access test files |
| Pull requests | Write | Comment with results |

### Testing Set
```yaml
permissions:
  checks: write
  statuses: write
  contents: read
  pull-requests: write
```

## Common Patterns

### Test Result Reporting

```typescript
app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository } = context.payload;

  // Download test artifacts
  const { data: artifacts } = await context.octokit.actions.listWorkflowRunArtifacts({
    ...context.repo(),
    run_id: workflow_run.id,
  });

  const testArtifact = artifacts.artifacts.find(a => a.name === "test-results");
  if (!testArtifact) return;

  // Download and parse results
  const results = await downloadAndParseTestResults(context, testArtifact);

  // Create check run with results
  await context.octokit.checks.create(
    context.repo({
      name: "Test Results",
      head_sha: workflow_run.head_sha,
      status: "completed",
      conclusion: results.failures > 0 ? "failure" : "success",
      output: {
        title: `${results.passed} passed, ${results.failures} failed`,
        summary: generateTestSummary(results),
        text: generateDetailedResults(results),
        annotations: results.failures > 0 ? generateAnnotations(results) : undefined,
      },
    })
  );
});

interface TestResults {
  total: number;
  passed: number;
  failures: number;
  skipped: number;
  duration: number;
  suites: TestSuite[];
}

function generateTestSummary(results: TestResults): string {
  const passRate = (results.passed / results.total) * 100;

  return `
## Test Summary

| Metric | Value |
|--------|-------|
| Total Tests | ${results.total} |
| Passed | ${results.passed} ✅ |
| Failed | ${results.failures} ❌ |
| Skipped | ${results.skipped} ⏭️ |
| Pass Rate | ${passRate.toFixed(1)}% |
| Duration | ${formatDuration(results.duration)} |

${results.failures > 0 ? `
### Failed Tests
${results.suites
  .flatMap(s => s.tests.filter(t => t.status === "failed"))
  .map(t => `- \`${t.name}\`: ${t.error?.message || "Failed"}`)
  .join("\n")}
` : ""}
  `.trim();
}

function generateAnnotations(results: TestResults) {
  return results.suites
    .flatMap(s => s.tests.filter(t => t.status === "failed"))
    .map(test => ({
      path: test.file || "unknown",
      start_line: test.line || 1,
      end_line: test.line || 1,
      annotation_level: "failure" as const,
      title: test.name,
      message: test.error?.message || "Test failed",
      raw_details: test.error?.stack,
    }));
}
```

### Coverage Tracking

```typescript
app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository } = context.payload;

  // Get coverage artifact
  const coverage = await downloadCoverageReport(context, workflow_run.id);
  if (!coverage) return;

  // Get previous coverage for comparison
  const previousCoverage = await getPreviousCoverage(repository.full_name);

  // Calculate diff
  const diff = {
    lines: coverage.lines - (previousCoverage?.lines || 0),
    branches: coverage.branches - (previousCoverage?.branches || 0),
    functions: coverage.functions - (previousCoverage?.functions || 0),
  };

  // Store new coverage
  await storeCoverage({
    repository: repository.full_name,
    sha: workflow_run.head_sha,
    coverage,
    timestamp: new Date(),
  });

  // Create check run
  const meetsThreshold = coverage.lines >= 80;

  await context.octokit.checks.create(
    context.repo({
      name: "Code Coverage",
      head_sha: workflow_run.head_sha,
      status: "completed",
      conclusion: meetsThreshold ? "success" : "failure",
      output: {
        title: `${coverage.lines.toFixed(1)}% line coverage`,
        summary: `
## Coverage Report

| Metric | Coverage | Change |
|--------|----------|--------|
| Lines | ${coverage.lines.toFixed(1)}% | ${formatChange(diff.lines)} |
| Branches | ${coverage.branches.toFixed(1)}% | ${formatChange(diff.branches)} |
| Functions | ${coverage.functions.toFixed(1)}% | ${formatChange(diff.functions)} |

${!meetsThreshold ? "⚠️ Coverage is below the 80% threshold." : "✅ Coverage meets the threshold."}
        `,
      },
    })
  );

  // Comment on PR with coverage
  if (workflow_run.pull_requests?.length > 0) {
    await commentCoverageOnPR(context, workflow_run.pull_requests[0], coverage, diff);
  }
});

interface CoverageReport {
  lines: number;
  branches: number;
  functions: number;
  files: FileCoverage[];
}

async function commentCoverageOnPR(context, pr, coverage, diff) {
  // Find or update existing comment
  const { data: comments } = await context.octokit.issues.listComments({
    ...context.repo(),
    issue_number: pr.number,
  });

  const existingComment = comments.find(c =>
    c.body?.includes("## Coverage Report") && c.user?.type === "Bot"
  );

  const body = `
## Coverage Report

| Metric | Coverage | Δ |
|--------|----------|---|
| Lines | ${coverage.lines.toFixed(1)}% | ${formatChange(diff.lines)} |
| Branches | ${coverage.branches.toFixed(1)}% | ${formatChange(diff.branches)} |
| Functions | ${coverage.functions.toFixed(1)}% | ${formatChange(diff.functions)} |

<details>
<summary>Files with coverage changes</summary>

| File | Coverage | Change |
|------|----------|--------|
${coverage.files
  .filter(f => f.change !== 0)
  .map(f => `| ${f.path} | ${f.coverage.toFixed(1)}% | ${formatChange(f.change)} |`)
  .join("\n")}

</details>
  `;

  if (existingComment) {
    await context.octokit.issues.updateComment({
      ...context.repo(),
      comment_id: existingComment.id,
      body,
    });
  } else {
    await context.octokit.issues.createComment({
      ...context.repo(),
      issue_number: pr.number,
      body,
    });
  }
}
```

### Flaky Test Detection

```typescript
interface TestHistory {
  name: string;
  runs: Array<{
    sha: string;
    status: "passed" | "failed" | "skipped";
    duration: number;
    timestamp: Date;
  }>;
}

async function detectFlakyTests(context, repository: string): Promise<string[]> {
  const testHistories = await getTestHistories(repository, 100); // Last 100 runs
  const flakyTests: string[] = [];

  for (const test of testHistories) {
    const recentRuns = test.runs.slice(-20);

    // Calculate flakiness score
    let transitions = 0;
    for (let i = 1; i < recentRuns.length; i++) {
      if (recentRuns[i].status !== recentRuns[i - 1].status) {
        transitions++;
      }
    }

    const flakinessScore = transitions / (recentRuns.length - 1);

    // Flag as flaky if transitions > 20% of runs
    if (flakinessScore > 0.2 && recentRuns.length >= 10) {
      flakyTests.push(test.name);
    }
  }

  return flakyTests;
}

app.on("workflow_run.completed", async (context) => {
  const { workflow_run, repository } = context.payload;

  // Update test histories
  const results = await downloadAndParseTestResults(context, workflow_run.id);
  await updateTestHistories(repository.full_name, workflow_run.head_sha, results);

  // Check for flaky tests
  const flakyTests = await detectFlakyTests(context, repository.full_name);

  if (flakyTests.length > 0) {
    // Create or update flaky tests issue
    const existingIssue = await findFlakyTestIssue(context);

    const body = `
## Flaky Tests Detected

The following tests have been identified as flaky (inconsistent pass/fail):

${flakyTests.map(t => `- \`${t}\``).join("\n")}

### What makes a test flaky?
A test is considered flaky when it alternates between pass and fail without code changes.

### Recommended Actions
1. Review the test for race conditions
2. Check for external dependencies
3. Consider adding retry logic or skipping temporarily
    `;

    if (existingIssue) {
      await context.octokit.issues.update({
        ...context.repo(),
        issue_number: existingIssue.number,
        body,
      });
    } else {
      await context.octokit.issues.create(
        context.repo({
          title: "🎲 Flaky Tests Detected",
          body,
          labels: ["flaky-tests", "testing"],
        })
      );
    }
  }
});
```

### Test Performance Tracking

```typescript
interface TestPerformance {
  name: string;
  avgDuration: number;
  p95Duration: number;
  trend: "improving" | "degrading" | "stable";
}

async function analyzeTestPerformance(context, repository: string) {
  const testHistories = await getTestHistories(repository, 50);
  const slowTests: TestPerformance[] = [];

  for (const test of testHistories) {
    const durations = test.runs.map(r => r.duration);
    const avgDuration = average(durations);
    const p95Duration = percentile(durations, 95);

    // Check trend
    const recentAvg = average(durations.slice(-10));
    const olderAvg = average(durations.slice(0, 10));
    const trend = recentAvg > olderAvg * 1.2
      ? "degrading"
      : recentAvg < olderAvg * 0.8
      ? "improving"
      : "stable";

    if (avgDuration > 1000) { // > 1 second
      slowTests.push({
        name: test.name,
        avgDuration,
        p95Duration,
        trend,
      });
    }
  }

  return slowTests.sort((a, b) => b.avgDuration - a.avgDuration);
}
```

### Mutation Testing

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Get changed files
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  const sourceFiles = files.filter(f =>
    f.filename.match(/\.(js|ts|py|java)$/) &&
    !f.filename.includes("test")
  );

  if (sourceFiles.length === 0) return;

  // Create in-progress check
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "Mutation Testing",
      head_sha: pull_request.head.sha,
      status: "in_progress",
    })
  );

  // Run mutation testing
  const results = await runMutationTests(context, sourceFiles, pull_request.head.sha);

  // Report results
  await context.octokit.checks.update(
    context.repo({
      check_run_id: check.id,
      status: "completed",
      conclusion: results.score >= 80 ? "success" : "neutral",
      output: {
        title: `Mutation Score: ${results.score.toFixed(1)}%`,
        summary: `
## Mutation Testing Results

| Metric | Value |
|--------|-------|
| Total Mutants | ${results.totalMutants} |
| Killed | ${results.killed} |
| Survived | ${results.survived} |
| Mutation Score | ${results.score.toFixed(1)}% |

${results.score < 80 ? `
### Surviving Mutants
These mutations were not detected by your tests:

${results.survivingMutants.slice(0, 10).map(m =>
  `- \`${m.file}:${m.line}\`: ${m.description}`
).join("\n")}
` : ""}
        `,
      },
    })
  );
});
```

## Test Report Formats

| Format | Use Case |
|--------|----------|
| JUnit XML | Standard CI format |
| TAP | Test Anything Protocol |
| JSON | Custom processing |
| Allure | Rich reporting |
| LCOV | Coverage data |
| Cobertura | Coverage XML |

## Security Considerations

- **Sanitize test output** - Don't expose secrets in logs
- **Limit artifact size** - Large reports can be DoS vector
- **Validate results** - Don't trust untrusted test data
- **Secure coverage data** - Can reveal code structure

## Example Apps in This Category

- **Codecov** - Coverage tracking
- **Coveralls** - Coverage reporting
- **Percy** - Visual testing
- **Sauce Labs** - Cross-browser testing

## Related Categories

- [CI](ci.md) - Build integration
- [Code Quality](code-quality.md) - Quality metrics
- [Reporting](reporting.md) - Test analytics

## See Also

- [GitHub Check Runs](https://docs.github.com/en/rest/checks/runs)
- [JUnit XML Format](https://llg.cubic.org/docs/junit/)
