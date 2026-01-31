# Deployment Protection Rules GitHub Apps

GitHub Apps that provide custom deployment protection rules: approval gates, compliance checks, and deployment validators.

## Overview

Deployment protection rules allow GitHub Apps to control when deployments can proceed to protected environments. When a deployment targets a protected environment, GitHub sends a webhook to registered apps, which must approve or reject the deployment.

## Common Use Cases

- **Manual Approvals** - Require human sign-off
- **Change Windows** - Only deploy during allowed times
- **Compliance Checks** - Verify security/audit requirements
- **Integration Tests** - Wait for external test results
- **Canary Validation** - Check metrics before promotion
- **Freeze Periods** - Block deploys during critical times

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `deployment_protection_rule.requested` | Evaluate deployment request |

This is the **only** webhook for deployment protection rules. Your app must respond by approving or rejecting the deployment.

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Deployments | Write | Respond to protection requests |
| Actions | Read | Access workflow context |
| Metadata | Read | Repository info |

### Required Permission Set
```yaml
permissions:
  deployments: write
```

## Common Patterns

### Basic Approval Gate

```typescript
app.on("deployment_protection_rule.requested", async (context) => {
  const { deployment, environment, deployment_callback_url } = context.payload;

  // Get installation token for callback
  const token = await getInstallationToken(context);

  // Example: Auto-approve staging, require manual for production
  if (environment === "staging") {
    await approveDeployment(deployment_callback_url, token, {
      comment: "Auto-approved for staging environment",
    });
  } else {
    // Create issue for manual approval
    const issue = await context.octokit.issues.create(
      context.repo({
        title: `🚀 Deployment approval needed: ${environment}`,
        body: `
## Deployment Request

**Environment**: ${environment}
**Ref**: ${deployment.ref}
**SHA**: ${deployment.sha}
**Triggered by**: ${deployment.creator.login}

### Actions
- Comment \`/approve\` to approve this deployment
- Comment \`/reject <reason>\` to reject

This request will timeout after 30 minutes.
        `,
        labels: ["deployment-approval", environment],
      })
    );

    // Store pending approval
    await storePendingApproval({
      issueNumber: issue.data.number,
      callbackUrl: deployment_callback_url,
      environment,
      deploymentId: deployment.id,
      expiresAt: Date.now() + 30 * 60 * 1000,
    });
  }
});

// Handle approval/rejection comments
app.on("issue_comment.created", async (context) => {
  const { issue, comment } = context.payload;

  if (!issue.labels.some(l => l.name === "deployment-approval")) return;

  const pending = await getPendingApproval(issue.number);
  if (!pending) return;

  const token = await getInstallationToken(context);

  if (comment.body.trim().startsWith("/approve")) {
    await approveDeployment(pending.callbackUrl, token, {
      comment: `Approved by @${comment.user.login}`,
    });

    await context.octokit.issues.update(
      context.issue({ state: "closed" })
    );
  } else if (comment.body.trim().startsWith("/reject")) {
    const reason = comment.body.replace("/reject", "").trim() || "Rejected";

    await rejectDeployment(pending.callbackUrl, token, {
      comment: `Rejected by @${comment.user.login}: ${reason}`,
    });

    await context.octokit.issues.update(
      context.issue({ state: "closed" })
    );
  }
});
```

### Callback Functions

```typescript
async function approveDeployment(
  callbackUrl: string,
  token: string,
  options: { comment?: string; environmentName?: string }
) {
  await fetch(callbackUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      state: "approved",
      comment: options.comment || "Approved by deployment protection app",
      environment_name: options.environmentName,
    }),
  });
}

async function rejectDeployment(
  callbackUrl: string,
  token: string,
  options: { comment: string }
) {
  await fetch(callbackUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      state: "rejected",
      comment: options.comment,
    }),
  });
}
```

### Change Window Enforcement

```typescript
interface ChangeWindow {
  dayOfWeek: number[]; // 0-6, Sunday = 0
  startHour: number;   // 0-23
  endHour: number;     // 0-23
  timezone: string;
}

const CHANGE_WINDOWS: Record<string, ChangeWindow> = {
  production: {
    dayOfWeek: [1, 2, 3, 4, 5], // Monday-Friday
    startHour: 9,
    endHour: 16,
    timezone: "America/New_York",
  },
};

app.on("deployment_protection_rule.requested", async (context) => {
  const { environment, deployment_callback_url } = context.payload;

  const window = CHANGE_WINDOWS[environment];
  if (!window) {
    await approveDeployment(deployment_callback_url, token, {
      comment: "No change window configured",
    });
    return;
  }

  const now = new Date();
  const localTime = new Date(now.toLocaleString("en-US", { timeZone: window.timezone }));

  const isAllowedDay = window.dayOfWeek.includes(localTime.getDay());
  const isAllowedHour = localTime.getHours() >= window.startHour
    && localTime.getHours() < window.endHour;

  if (isAllowedDay && isAllowedHour) {
    await approveDeployment(deployment_callback_url, token, {
      comment: "Within change window",
    });
  } else {
    await rejectDeployment(deployment_callback_url, token, {
      comment: `Outside change window. Allowed: ${window.dayOfWeek.map(d => ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][d]).join(", ")} ${window.startHour}:00-${window.endHour}:00 ${window.timezone}`,
    });
  }
});
```

### Compliance Check Integration

```typescript
app.on("deployment_protection_rule.requested", async (context) => {
  const { deployment, environment, deployment_callback_url } = context.payload;

  const token = await getInstallationToken(context);

  // Run compliance checks
  const checks = await runComplianceChecks({
    ref: deployment.sha,
    environment,
  });

  const failed = checks.filter(c => !c.passed);

  if (failed.length === 0) {
    await approveDeployment(deployment_callback_url, token, {
      comment: "All compliance checks passed",
    });
  } else {
    await rejectDeployment(deployment_callback_url, token, {
      comment: `Compliance checks failed:\n${failed.map(c => `- ${c.name}: ${c.reason}`).join("\n")}`,
    });
  }
});

interface ComplianceCheck {
  name: string;
  check: (context: any) => Promise<{ passed: boolean; reason?: string }>;
}

const COMPLIANCE_CHECKS: ComplianceCheck[] = [
  {
    name: "Security Scan",
    check: async (ctx) => {
      const alerts = await getSecurityAlerts(ctx.ref);
      return {
        passed: alerts.critical === 0,
        reason: alerts.critical > 0 ? `${alerts.critical} critical vulnerabilities` : undefined,
      };
    },
  },
  {
    name: "Test Coverage",
    check: async (ctx) => {
      const coverage = await getTestCoverage(ctx.ref);
      return {
        passed: coverage >= 80,
        reason: coverage < 80 ? `Coverage ${coverage}% < 80%` : undefined,
      };
    },
  },
  {
    name: "Approval Count",
    check: async (ctx) => {
      const approvals = await getPRApprovals(ctx.ref);
      return {
        passed: approvals >= 2,
        reason: approvals < 2 ? `Only ${approvals} approvals` : undefined,
      };
    },
  },
];
```

### External System Integration

```typescript
app.on("deployment_protection_rule.requested", async (context) => {
  const { deployment, environment, deployment_callback_url } = context.payload;

  // Check external change management system
  const changeRequest = await getChangeRequest({
    environment,
    ref: deployment.sha,
  });

  if (!changeRequest) {
    await rejectDeployment(deployment_callback_url, token, {
      comment: "No approved change request found in ServiceNow",
    });
    return;
  }

  if (changeRequest.status !== "approved") {
    await rejectDeployment(deployment_callback_url, token, {
      comment: `Change request ${changeRequest.id} is ${changeRequest.status}`,
    });
    return;
  }

  await approveDeployment(deployment_callback_url, token, {
    comment: `Approved via change request ${changeRequest.id}`,
  });
});
```

### Canary Validation

```typescript
app.on("deployment_protection_rule.requested", async (context) => {
  const { deployment, environment, deployment_callback_url } = context.payload;

  // Only for production promotion
  if (environment !== "production") {
    await approveDeployment(deployment_callback_url, token, {
      comment: "Non-production environment",
    });
    return;
  }

  // Check canary metrics
  const canaryMetrics = await getCanaryMetrics(deployment.sha);

  const healthChecks = [
    { name: "Error Rate", value: canaryMetrics.errorRate, threshold: 0.01 },
    { name: "Latency P99", value: canaryMetrics.latencyP99, threshold: 500 },
    { name: "Success Rate", value: canaryMetrics.successRate, threshold: 0.99, invert: true },
  ];

  const failures = healthChecks.filter(check =>
    check.invert ? check.value < check.threshold : check.value > check.threshold
  );

  if (failures.length === 0) {
    await approveDeployment(deployment_callback_url, token, {
      comment: "Canary metrics healthy",
    });
  } else {
    await rejectDeployment(deployment_callback_url, token, {
      comment: `Canary unhealthy:\n${failures.map(f => `- ${f.name}: ${f.value} (threshold: ${f.threshold})`).join("\n")}`,
    });
  }
});
```

### Freeze Period Enforcement

```typescript
interface FreezePeriod {
  start: Date;
  end: Date;
  reason: string;
  environments: string[];
  exceptions?: string[]; // Users who can bypass
}

async function checkFreezePeriod(
  environment: string,
  requestor: string
): Promise<FreezePeriod | null> {
  const freezePeriods = await getFreezePeriods();
  const now = new Date();

  for (const period of freezePeriods) {
    if (now >= period.start && now <= period.end) {
      if (period.environments.includes(environment) || period.environments.includes("*")) {
        if (!period.exceptions?.includes(requestor)) {
          return period;
        }
      }
    }
  }

  return null;
}

app.on("deployment_protection_rule.requested", async (context) => {
  const { deployment, environment, deployment_callback_url } = context.payload;

  const freeze = await checkFreezePeriod(environment, deployment.creator.login);

  if (freeze) {
    await rejectDeployment(deployment_callback_url, token, {
      comment: `Deployment frozen until ${freeze.end.toISOString()}: ${freeze.reason}`,
    });
  } else {
    await approveDeployment(deployment_callback_url, token, {
      comment: "No active freeze period",
    });
  }
});
```

## Webhook Payload Structure

```typescript
interface DeploymentProtectionRulePayload {
  action: "requested";
  environment: string;
  event: string;
  deployment_callback_url: string;
  deployment: {
    id: number;
    sha: string;
    ref: string;
    task: string;
    payload: Record<string, any>;
    environment: string;
    creator: {
      login: string;
    };
  };
  repository: Repository;
  installation: Installation;
}
```

## Response Timeout

- Deployment protection rules have a **30 minute timeout**
- If your app doesn't respond, the deployment is **rejected**
- For long-running checks, respond quickly and use webhooks for updates

## Security Considerations

- **Validate callback URL** - Only use URLs from webhook payload
- **Secure token storage** - Don't log or expose tokens
- **Audit all decisions** - Log who approved/rejected what
- **Rate limit** - Prevent approval spam
- **Timeout handling** - Don't leave deployments hanging

## Example Apps in This Category

- **LaunchDarkly** - Feature flag gates
- **PagerDuty** - Incident-aware deployments
- **ServiceNow** - Change management integration

## Related Categories

- [Deployment](deployment.md) - Deployment automation
- [Monitoring](monitoring.md) - Health checks
- [Security](security.md) - Compliance enforcement

## See Also

- [GitHub Deployment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#deployment-protection-rules)
- [Creating Custom Protection Rules](https://docs.github.com/en/actions/deployment/protecting-deployments/creating-custom-deployment-protection-rules)
