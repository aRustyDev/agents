# Deployment GitHub Apps

GitHub Apps that automate deployments: environment management, deployment automation, rollbacks, and deployment tracking.

## Common Use Cases

- **Automated Deployments** - Deploy on merge/release
- **Environment Management** - Staging, production, preview
- **Deployment Gates** - Approval workflows
- **Rollback Automation** - Quick recovery
- **Deployment Status** - Track active deployments
- **Preview Environments** - Per-PR deployments

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Deploy on commit |
| `pull_request.*` | Preview deployments |
| `deployment.created` | Start deployment |
| `deployment_status.created` | Track status |
| `release.published` | Production deployment |
| `workflow_run.completed` | Post-build deploy |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Deployments | Write | Create/update deployments |
| Environments | Write | Manage environments |
| Contents | Read | Access deployment configs |
| Statuses | Write | Set commit status |
| Pull requests | Write | Comment with deploy URLs |

### Minimal Permission Set
```yaml
permissions:
  deployments: write
  contents: read
```

### Full Deployment Set
```yaml
permissions:
  deployments: write
  environments: write
  contents: read
  statuses: write
  pull-requests: write
```

## Common Patterns

### Create Deployment on Push

```typescript
app.on("push", async (context) => {
  const { ref, after, repository } = context.payload;

  // Only deploy default branch
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  // Determine environment
  const environment = "production";

  // Create deployment
  const { data: deployment } = await context.octokit.repos.createDeployment(
    context.repo({
      ref: after,
      environment,
      auto_merge: false,
      required_contexts: [], // Skip status checks
      payload: {
        version: after.slice(0, 7),
        deployer: "github-app",
      },
    })
  );

  // Set pending status
  await context.octokit.repos.createDeploymentStatus(
    context.repo({
      deployment_id: deployment.id,
      state: "pending",
      description: "Deployment started",
    })
  );

  try {
    // Perform deployment
    const result = await deploy({
      environment,
      ref: after,
      repository: repository.full_name,
    });

    // Set success status
    await context.octokit.repos.createDeploymentStatus(
      context.repo({
        deployment_id: deployment.id,
        state: "success",
        environment_url: result.url,
        description: "Deployment complete",
      })
    );
  } catch (error) {
    // Set failure status
    await context.octokit.repos.createDeploymentStatus(
      context.repo({
        deployment_id: deployment.id,
        state: "failure",
        description: error.message,
      })
    );
  }
});
```

### Preview Deployments for PRs

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request, repository } = context.payload;

  const environment = `preview-pr-${pull_request.number}`;

  // Create deployment
  const { data: deployment } = await context.octokit.repos.createDeployment(
    context.repo({
      ref: pull_request.head.sha,
      environment,
      transient_environment: true, // Auto-cleanup
      production_environment: false,
      payload: {
        pr: pull_request.number,
        branch: pull_request.head.ref,
      },
    })
  );

  await context.octokit.repos.createDeploymentStatus(
    context.repo({
      deployment_id: deployment.id,
      state: "in_progress",
    })
  );

  try {
    // Deploy to preview environment
    const result = await deployPreview({
      environment,
      ref: pull_request.head.sha,
      prNumber: pull_request.number,
    });

    await context.octokit.repos.createDeploymentStatus(
      context.repo({
        deployment_id: deployment.id,
        state: "success",
        environment_url: result.url,
      })
    );

    // Comment on PR
    await context.octokit.issues.createComment(
      context.issue({
        body: `## 🚀 Preview Deployment

Your preview is ready!

**URL**: ${result.url}
**Environment**: \`${environment}\`

This preview will be automatically deleted when the PR is closed.
        `,
      })
    );
  } catch (error) {
    await context.octokit.repos.createDeploymentStatus(
      context.repo({
        deployment_id: deployment.id,
        state: "failure",
        description: error.message,
      })
    );
  }
});

// Cleanup preview on PR close
app.on("pull_request.closed", async (context) => {
  const { pull_request } = context.payload;
  const environment = `preview-pr-${pull_request.number}`;

  // Delete preview environment
  await deletePreviewEnvironment(environment);

  // Mark deployments as inactive
  const { data: deployments } = await context.octokit.repos.listDeployments(
    context.repo({ environment })
  );

  for (const deployment of deployments) {
    await context.octokit.repos.createDeploymentStatus(
      context.repo({
        deployment_id: deployment.id,
        state: "inactive",
        description: "PR closed, preview deleted",
      })
    );
  }
});
```

### Environment Configuration

```typescript
interface EnvironmentConfig {
  name: string;
  url: string;
  reviewers?: string[];
  waitTimer?: number;
  branches?: string[];
}

const ENVIRONMENTS: EnvironmentConfig[] = [
  {
    name: "development",
    url: "https://dev.example.com",
    branches: ["develop", "feature/*"],
  },
  {
    name: "staging",
    url: "https://staging.example.com",
    branches: ["main"],
    waitTimer: 0,
  },
  {
    name: "production",
    url: "https://example.com",
    branches: ["main"],
    reviewers: ["@org/devops"],
    waitTimer: 300, // 5 minute wait
  },
];

async function getEnvironmentForRef(ref: string): Promise<EnvironmentConfig | null> {
  const branch = ref.replace("refs/heads/", "");

  for (const env of ENVIRONMENTS) {
    if (!env.branches) continue;

    for (const pattern of env.branches) {
      if (pattern.includes("*")) {
        const regex = new RegExp(`^${pattern.replace("*", ".*")}$`);
        if (regex.test(branch)) return env;
      } else if (pattern === branch) {
        return env;
      }
    }
  }

  return null;
}
```

### Rollback Automation

```typescript
app.on("deployment_status.created", async (context) => {
  const { deployment_status, deployment, repository } = context.payload;

  // Only handle failure in production
  if (deployment_status.state !== "failure") return;
  if (deployment.environment !== "production") return;

  // Get previous successful deployment
  const { data: deployments } = await context.octokit.repos.listDeployments(
    context.repo({
      environment: "production",
      per_page: 10,
    })
  );

  const previousSuccessful = deployments.find(async (d) => {
    const { data: statuses } = await context.octokit.repos.listDeploymentStatuses(
      context.repo({ deployment_id: d.id })
    );
    return statuses[0]?.state === "success";
  });

  if (previousSuccessful) {
    // Create rollback deployment
    const { data: rollback } = await context.octokit.repos.createDeployment(
      context.repo({
        ref: previousSuccessful.ref,
        environment: "production",
        description: `Rollback from ${deployment.ref}`,
        payload: {
          rollback: true,
          from: deployment.ref,
          to: previousSuccessful.ref,
        },
      })
    );

    // Notify
    await createIssue(context, {
      title: `⚠️ Production rollback triggered`,
      body: `
Deployment of \`${deployment.ref}\` failed. Automatic rollback initiated.

**Failed deployment**: ${deployment.sha}
**Rolling back to**: ${previousSuccessful.sha}

Please investigate the failure.
      `,
      labels: ["incident", "deployment"],
    });
  }
});
```

### Blue-Green Deployment

```typescript
interface BlueGreenConfig {
  active: "blue" | "green";
  blue: { url: string; healthCheck: string };
  green: { url: string; healthCheck: string };
}

async function blueGreenDeploy(context, sha: string, config: BlueGreenConfig) {
  const inactive = config.active === "blue" ? "green" : "blue";
  const target = config[inactive];

  // Deploy to inactive slot
  await deployToSlot(inactive, sha);

  // Health check
  const healthy = await checkHealth(target.healthCheck);
  if (!healthy) {
    throw new Error(`Health check failed for ${inactive} slot`);
  }

  // Switch traffic
  await switchTraffic(inactive);

  // Update config
  config.active = inactive;
  await saveConfig(config);

  return { slot: inactive, url: target.url };
}
```

### Canary Deployment

```typescript
interface CanaryConfig {
  initialPercentage: number;
  incrementPercentage: number;
  intervalMinutes: number;
  maxPercentage: number;
}

async function canaryDeploy(
  context,
  sha: string,
  config: CanaryConfig
) {
  let currentPercentage = config.initialPercentage;

  // Initial canary deployment
  await deployCanary(sha, currentPercentage);

  while (currentPercentage < config.maxPercentage) {
    // Wait interval
    await sleep(config.intervalMinutes * 60 * 1000);

    // Check metrics
    const metrics = await getCanaryMetrics();

    if (metrics.errorRate > 0.01) {
      // Rollback canary
      await rollbackCanary();
      throw new Error(`Canary failed: error rate ${metrics.errorRate}`);
    }

    // Increase traffic
    currentPercentage = Math.min(
      currentPercentage + config.incrementPercentage,
      config.maxPercentage
    );
    await updateCanaryPercentage(currentPercentage);

    // Report progress
    await updateDeploymentStatus(context, {
      state: "in_progress",
      description: `Canary at ${currentPercentage}%`,
    });
  }

  // Promote canary to production
  await promoteCanary();
}
```

## Deployment States

| State | Description |
|-------|-------------|
| `pending` | Deployment created, not started |
| `queued` | Waiting for resources |
| `in_progress` | Deployment running |
| `success` | Deployment complete |
| `failure` | Deployment failed |
| `error` | Unexpected error |
| `inactive` | Superseded by new deployment |

## Security Considerations

- **Protect production** - Require approvals for prod
- **Secrets management** - Don't expose deploy keys
- **Audit deployments** - Log who deployed what
- **Rollback access** - Limit who can rollback
- **Environment isolation** - Separate credentials per env

## Platform Integrations

| Platform | Deployment Method |
|----------|-------------------|
| Vercel | API / Git integration |
| Netlify | API / Git integration |
| AWS | CodeDeploy / ECS / Lambda |
| GCP | Cloud Run / GKE |
| Azure | App Service / AKS |
| Kubernetes | kubectl / Helm |
| Cloudflare | Workers API |

## Example Apps in This Category

- **Vercel** - Frontend deployments
- **Netlify** - JAMstack deployments
- **Heroku** - PaaS deployments
- **ArgoCD** - GitOps for Kubernetes

## Related Categories

- [CI](ci.md) - Build pipeline
- [Deployment Protection Rules](deployment-protection-rules.md) - Approval gates
- [Monitoring](monitoring.md) - Deployment health

## See Also

- [GitHub Deployments API](https://docs.github.com/en/rest/deployments)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
