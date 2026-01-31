# CI (Continuous Integration) GitHub Apps

GitHub Apps that provide continuous integration capabilities: build automation, test execution, and integration with external CI systems.

## Common Use Cases

- **Build Automation** - Compile and build projects
- **Test Execution** - Run automated tests
- **External CI Integration** - Connect Jenkins, CircleCI, etc.
- **Build Status Reporting** - Report CI results to GitHub
- **Artifact Management** - Store build outputs
- **Matrix Builds** - Test across configurations

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Trigger builds on commit |
| `pull_request.opened/synchronize` | Build PRs |
| `workflow_job.queued` | External runner dispatch |
| `workflow_run.completed` | React to workflow completion |
| `check_suite.requested` | Trigger check runs |
| `check_run.rerequested` | Re-run builds |
| `status` | Legacy commit status updates |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Checks | Write | Report build status |
| Statuses | Write | Set commit status |
| Contents | Read | Clone repository |
| Pull requests | Read | Access PR metadata |
| Actions | Write | Trigger workflows |
| Metadata | Read | Repository info |

### Minimal Permission Set
```yaml
permissions:
  checks: write
  contents: read
```

### Full CI Set
```yaml
permissions:
  checks: write
  statuses: write
  contents: read
  pull-requests: read
  actions: write
```

## Common Patterns

### External CI Integration

```typescript
app.on("push", async (context) => {
  const { after, ref, repository, commits } = context.payload;

  // Create pending check
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "External CI",
      head_sha: after,
      status: "queued",
      details_url: `${CI_URL}/builds/new`,
    })
  );

  // Trigger external CI system
  const build = await triggerExternalBuild({
    repoUrl: repository.clone_url,
    sha: after,
    ref,
    checkRunId: check.id,
    callbackUrl: `${APP_URL}/webhook/ci-callback`,
  });

  // Update with external build URL
  await context.octokit.checks.update(
    context.repo({
      check_run_id: check.id,
      status: "in_progress",
      details_url: build.url,
      external_id: build.id,
    })
  );
});

// Callback endpoint for external CI
async function handleCICallback(payload: CICallbackPayload) {
  const { checkRunId, status, conclusion, output, repoOwner, repoName } = payload;

  await octokit.checks.update({
    owner: repoOwner,
    repo: repoName,
    check_run_id: checkRunId,
    status,
    conclusion,
    completed_at: status === "completed" ? new Date().toISOString() : undefined,
    output,
  });
}
```

### Multi-Job Check Suite

```typescript
interface CIJob {
  name: string;
  command: string;
  dependsOn?: string[];
}

const CI_JOBS: CIJob[] = [
  { name: "lint", command: "npm run lint" },
  { name: "test", command: "npm test" },
  { name: "build", command: "npm run build", dependsOn: ["lint", "test"] },
  { name: "e2e", command: "npm run e2e", dependsOn: ["build"] },
];

app.on("check_suite.requested", async (context) => {
  const { check_suite } = context.payload;

  // Create check runs for each job
  const checkRuns = new Map<string, number>();

  for (const job of CI_JOBS) {
    const { data: check } = await context.octokit.checks.create(
      context.repo({
        name: `CI / ${job.name}`,
        head_sha: check_suite.head_sha,
        status: job.dependsOn ? "queued" : "in_progress",
      })
    );
    checkRuns.set(job.name, check.id);
  }

  // Execute jobs respecting dependencies
  await executeJobsWithDependencies(context, CI_JOBS, checkRuns, check_suite.head_sha);
});

async function executeJobsWithDependencies(
  context,
  jobs: CIJob[],
  checkRuns: Map<string, number>,
  sha: string
) {
  const completed = new Map<string, "success" | "failure">();

  while (completed.size < jobs.length) {
    // Find jobs ready to run
    const ready = jobs.filter(job => {
      if (completed.has(job.name)) return false;

      const deps = job.dependsOn || [];
      return deps.every(dep => completed.get(dep) === "success");
    });

    // Check for blocked jobs (dependency failed)
    const blocked = jobs.filter(job => {
      if (completed.has(job.name)) return false;

      const deps = job.dependsOn || [];
      return deps.some(dep => completed.get(dep) === "failure");
    });

    // Mark blocked jobs as skipped
    for (const job of blocked) {
      const checkId = checkRuns.get(job.name)!;
      await context.octokit.checks.update(
        context.repo({
          check_run_id: checkId,
          status: "completed",
          conclusion: "skipped",
          output: {
            title: "Skipped",
            summary: "Dependency failed",
          },
        })
      );
      completed.set(job.name, "failure");
    }

    // Execute ready jobs in parallel
    await Promise.all(
      ready.map(async job => {
        const checkId = checkRuns.get(job.name)!;

        await context.octokit.checks.update(
          context.repo({
            check_run_id: checkId,
            status: "in_progress",
            started_at: new Date().toISOString(),
          })
        );

        const result = await executeJob(job, sha);

        await context.octokit.checks.update(
          context.repo({
            check_run_id: checkId,
            status: "completed",
            conclusion: result.success ? "success" : "failure",
            completed_at: new Date().toISOString(),
            output: {
              title: result.success ? "Passed" : "Failed",
              summary: result.summary,
              text: result.logs,
            },
          })
        );

        completed.set(job.name, result.success ? "success" : "failure");
      })
    );
  }
}
```

### Build Configuration Detection

```typescript
const BUILD_CONFIGS = [
  {
    file: ".github/workflows/*.yml",
    type: "github-actions",
    command: "Handled by GitHub Actions",
  },
  {
    file: ".travis.yml",
    type: "travis",
    parser: parseTravisConfig,
  },
  {
    file: "Jenkinsfile",
    type: "jenkins",
    parser: parseJenkinsfile,
  },
  {
    file: ".circleci/config.yml",
    type: "circleci",
    parser: parseCircleCIConfig,
  },
  {
    file: "package.json",
    type: "npm",
    getCommands: (pkg) => ({
      test: pkg.scripts?.test,
      build: pkg.scripts?.build,
      lint: pkg.scripts?.lint,
    }),
  },
];

async function detectBuildConfig(context, sha: string) {
  for (const config of BUILD_CONFIGS) {
    if (config.file.includes("*")) {
      // Glob pattern
      const files = await findFiles(context, config.file, sha);
      if (files.length > 0) {
        return { type: config.type, files };
      }
    } else {
      try {
        const content = await getFileContent(context, config.file, sha);
        if (content) {
          return {
            type: config.type,
            config: config.parser ? config.parser(content) : content,
          };
        }
      } catch {
        // File doesn't exist
      }
    }
  }

  return null;
}
```

### Build Caching

```typescript
interface CacheKey {
  os: string;
  nodeVersion: string;
  lockfileHash: string;
}

async function getCacheKey(context, sha: string): Promise<CacheKey> {
  const lockfile = await getFileContent(context, "package-lock.json", sha)
    || await getFileContent(context, "yarn.lock", sha)
    || await getFileContent(context, "pnpm-lock.yaml", sha);

  const lockfileHash = lockfile ? crypto.createHash("sha256").update(lockfile).digest("hex").slice(0, 16) : "no-lockfile";

  return {
    os: "ubuntu-latest",
    nodeVersion: "18",
    lockfileHash,
  };
}

async function restoreCache(cacheKey: CacheKey): Promise<boolean> {
  const key = `node-modules-${cacheKey.os}-${cacheKey.nodeVersion}-${cacheKey.lockfileHash}`;

  const cached = await cacheStore.get(key);
  if (cached) {
    await extractCache(cached, "node_modules");
    return true;
  }

  return false;
}

async function saveCache(cacheKey: CacheKey): Promise<void> {
  const key = `node-modules-${cacheKey.os}-${cacheKey.nodeVersion}-${cacheKey.lockfileHash}`;

  const archive = await createArchive("node_modules");
  await cacheStore.set(key, archive);
}
```

### Matrix Build Support

```typescript
interface MatrixConfig {
  os: string[];
  nodeVersion: string[];
  include?: Array<Record<string, string>>;
  exclude?: Array<Record<string, string>>;
}

function generateMatrixCombinations(matrix: MatrixConfig) {
  let combinations: Array<Record<string, string>> = [{}];

  // Generate all combinations
  for (const [key, values] of Object.entries(matrix)) {
    if (key === "include" || key === "exclude") continue;

    const newCombinations: Array<Record<string, string>> = [];
    for (const combo of combinations) {
      for (const value of values as string[]) {
        newCombinations.push({ ...combo, [key]: value });
      }
    }
    combinations = newCombinations;
  }

  // Apply excludes
  if (matrix.exclude) {
    combinations = combinations.filter(combo =>
      !matrix.exclude!.some(exclude =>
        Object.entries(exclude).every(([k, v]) => combo[k] === v)
      )
    );
  }

  // Apply includes
  if (matrix.include) {
    combinations.push(...matrix.include);
  }

  return combinations;
}

// Example:
// { os: ["ubuntu", "macos"], nodeVersion: ["16", "18"] }
// -> [
//   { os: "ubuntu", nodeVersion: "16" },
//   { os: "ubuntu", nodeVersion: "18" },
//   { os: "macos", nodeVersion: "16" },
//   { os: "macos", nodeVersion: "18" },
// ]
```

### Build Artifact Upload

```typescript
async function uploadArtifact(
  context,
  checkRunId: number,
  name: string,
  content: Buffer
) {
  // Upload to storage
  const url = await storage.upload({
    key: `artifacts/${context.payload.repository.full_name}/${checkRunId}/${name}`,
    content,
  });

  // Update check run with artifact link
  const { data: check } = await context.octokit.checks.get(
    context.repo({ check_run_id: checkRunId })
  );

  const existingOutput = check.output || { title: "", summary: "" };

  await context.octokit.checks.update(
    context.repo({
      check_run_id: checkRunId,
      output: {
        ...existingOutput,
        summary: `${existingOutput.summary}\n\n**Artifacts:**\n- [${name}](${url})`,
      },
    })
  );
}
```

## Build Status Propagation

```typescript
// Roll up multiple check runs to single status
app.on("check_run.completed", async (context) => {
  const { check_run, repository } = context.payload;

  // Get all check runs for this SHA
  const { data: { check_runs } } = await context.octokit.checks.listForRef(
    context.repo({ ref: check_run.head_sha })
  );

  // Filter to our app's checks
  const ourChecks = check_runs.filter(
    cr => cr.app?.id === parseInt(process.env.APP_ID!)
  );

  // Determine overall status
  const allComplete = ourChecks.every(cr => cr.status === "completed");
  const anyFailed = ourChecks.some(cr => cr.conclusion === "failure");
  const allSuccess = ourChecks.every(cr => cr.conclusion === "success");

  if (allComplete) {
    await context.octokit.repos.createCommitStatus(
      context.repo({
        sha: check_run.head_sha,
        state: allSuccess ? "success" : anyFailed ? "failure" : "pending",
        context: "CI / Summary",
        description: allSuccess
          ? `All ${ourChecks.length} checks passed`
          : `${ourChecks.filter(c => c.conclusion === "failure").length} checks failed`,
      })
    );
  }
});
```

## Security Considerations

- **Clone with least privilege** - Read-only tokens for builds
- **Isolate build environments** - Use containers/VMs
- **Don't run untrusted code** - Especially from forks
- **Secure secrets in builds** - Use secret managers
- **Audit build logs** - Redact sensitive output
- **Timeout builds** - Prevent runaway processes

## Example Apps in This Category

- **CircleCI** - Cloud CI/CD platform
- **Travis CI** - Hosted CI service
- **Jenkins** - Self-hosted automation server
- **Buildkite** - Scalable CI/CD
- **Drone** - Container-native CI

## Related Categories

- [Testing](testing.md) - Test execution
- [Deployment](deployment.md) - CD integration
- [Container CI](container-ci.md) - Container builds
- [Mobile CI](mobile-ci.md) - Mobile builds

## See Also

- [GitHub Checks API](https://docs.github.com/en/rest/checks)
- [GitHub Actions](https://docs.github.com/en/actions)
