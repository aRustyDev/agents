# Security GitHub Apps

GitHub Apps focused on security: policy enforcement, access management, secret protection, and security automation.

## Common Use Cases

- **Policy Enforcement** - Branch protection, review requirements
- **Access Management** - Team permissions, token auditing
- **Secret Detection** - Prevent secret exposure
- **Compliance** - SOC2, HIPAA, FedRAMP controls
- **Incident Response** - Security alert automation
- **Vulnerability Management** - CVE tracking and remediation

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Secret scanning, policy checks |
| `pull_request.*` | Security review requirements |
| `member.*` | Access changes |
| `repository.*` | New repo security setup |
| `organization.*` | Org-wide security events |
| `security_advisory.*` | CVE notifications |
| `secret_scanning_alert.*` | Exposed secrets |
| `code_scanning_alert.*` | Vulnerability alerts |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Administration | Write | Manage security settings |
| Security events | Write | Create security alerts |
| Secret scanning alerts | Write | Manage secret alerts |
| Members | Write | Access management |
| Organization administration | Write | Org security settings |

### Security Admin Set
```yaml
permissions:
  administration: write
  security-events: write
  secret-scanning-alerts: write
  members: write
  contents: read
```

## Common Patterns

### Branch Protection Enforcement

```typescript
app.on("repository.created", async (context) => {
  const { repository } = context.payload;

  // Apply standard branch protection
  await context.octokit.repos.updateBranchProtection(
    context.repo({
      branch: repository.default_branch,
      required_status_checks: {
        strict: true,
        contexts: ["ci/tests", "security/scan"],
      },
      enforce_admins: true,
      required_pull_request_reviews: {
        required_approving_review_count: 2,
        dismiss_stale_reviews: true,
        require_code_owner_reviews: true,
      },
      restrictions: null,
      required_linear_history: true,
      allow_force_pushes: false,
      allow_deletions: false,
    })
  );

  // Create security issue
  await context.octokit.issues.create(
    context.repo({
      title: "Security Setup Complete",
      body: `
Branch protection has been automatically configured for \`${repository.default_branch}\`:

- ✅ Required status checks: ci/tests, security/scan
- ✅ Strict mode enabled
- ✅ 2 approving reviews required
- ✅ Stale review dismissal enabled
- ✅ Code owner reviews required
- ✅ Force pushes disabled
- ✅ Branch deletions disabled

Please review and adjust if needed.
      `,
      labels: ["security", "automated"],
    })
  );
});
```

### Secret Scanning Response

```typescript
app.on("secret_scanning_alert.created", async (context) => {
  const { alert, repository, sender } = context.payload;

  // Immediately revoke if possible
  const revoked = await attemptSecretRevocation(alert.secret_type, alert.secret);

  // Create incident
  const { data: issue } = await context.octokit.issues.create(
    context.repo({
      title: `🚨 Secret Exposed: ${alert.secret_type}`,
      body: `
## Security Incident

A secret has been detected in the repository.

| Field | Value |
|-------|-------|
| Type | ${alert.secret_type} |
| Location | ${alert.push_protection_bypassed ? "Push (bypassed)" : "Historical"} |
| Detected At | ${new Date().toISOString()} |
| Auto-Revoked | ${revoked ? "Yes ✅" : "No ❌"} |

### Immediate Actions Required
1. ${revoked ? "✅ Secret has been automatically revoked" : "⚠️ **Manually revoke this secret immediately**"}
2. Rotate any related credentials
3. Audit usage of this secret
4. Review commits for other secrets

### Resolution
Once resolved, close this issue and mark the alert as resolved.

cc: @security-team
      `,
      labels: ["security", "incident", "secret-exposure"],
      assignees: ["security-lead"],
    })
  );

  // Notify security team
  await sendSecurityAlert({
    severity: "critical",
    title: `Secret exposed in ${repository.full_name}`,
    issue: issue.html_url,
    alert,
  });

  // If push protection was bypassed, audit who did it
  if (alert.push_protection_bypassed) {
    await logSecurityEvent({
      type: "push_protection_bypass",
      repository: repository.full_name,
      actor: alert.push_protection_bypassed_by?.login,
      reason: alert.push_protection_bypassed_at,
      secret_type: alert.secret_type,
    });
  }
});

async function attemptSecretRevocation(secretType: string, secret: string): Promise<boolean> {
  // Attempt to revoke based on secret type
  switch (secretType) {
    case "github_personal_access_token":
      // Can't revoke other users' tokens
      return false;

    case "aws_access_key_id":
      try {
        await revokeAWSKey(secret);
        return true;
      } catch {
        return false;
      }

    case "slack_webhook":
      // Slack webhooks should be rotated
      return false;

    default:
      return false;
  }
}
```

### Access Audit

```typescript
app.on("member.added", async (context) => {
  const { member, repository, sender } = context.payload;

  // Log access grant
  await logAccessChange({
    type: "grant",
    repository: repository.full_name,
    user: member.login,
    grantedBy: sender.login,
    timestamp: new Date(),
  });

  // Check if user is external
  const { data: membership } = await context.octokit.orgs.getMembershipForUser({
    org: repository.owner.login,
    username: member.login,
  }).catch(() => ({ data: null }));

  if (!membership || membership.role === "outside_collaborator") {
    // External user added - require approval
    await context.octokit.issues.create(
      context.repo({
        title: `External collaborator added: @${member.login}`,
        body: `
@${sender.login} added @${member.login} as a collaborator.

**Action Required**: Please confirm this access is approved.

- [ ] Access approved by manager
- [ ] NDA on file (if required)
- [ ] Access duration defined

Reply with \`/approve\` to confirm or \`/deny\` to revoke access.
        `,
        labels: ["security", "access-review"],
        assignees: [sender.login],
      })
    );
  }
});

// Handle access review commands
app.on("issue_comment.created", async (context) => {
  const { comment, issue } = context.payload;

  if (!issue.labels.some((l) => l.name === "access-review")) return;

  if (comment.body.includes("/deny")) {
    const match = issue.title.match(/External collaborator added: @(\w+)/);
    if (match) {
      await context.octokit.repos.removeCollaborator(
        context.repo({ username: match[1] })
      );

      await context.octokit.issues.update(
        context.issue({ state: "closed" })
      );

      await context.octokit.issues.createComment(
        context.issue({
          body: `Access revoked by @${comment.user.login}`,
        })
      );
    }
  }
});
```

### Security Policy Enforcement

```typescript
interface SecurityPolicy {
  requireSignedCommits: boolean;
  requireBranchProtection: boolean;
  requireSecurityScanning: boolean;
  maxStaleVulnerabilityDays: number;
  allowedVisibility: ("public" | "private" | "internal")[];
}

async function enforceSecurityPolicy(context, policy: SecurityPolicy) {
  const { repository } = context.payload;
  const violations: string[] = [];

  // Check visibility
  if (!policy.allowedVisibility.includes(repository.visibility)) {
    violations.push(`Visibility ${repository.visibility} not allowed`);
  }

  // Check branch protection
  if (policy.requireBranchProtection) {
    try {
      await context.octokit.repos.getBranchProtection(
        context.repo({ branch: repository.default_branch })
      );
    } catch {
      violations.push("Branch protection not enabled");
    }
  }

  // Check for security scanning
  if (policy.requireSecurityScanning) {
    const { data: workflows } = await context.octokit.actions.listRepoWorkflows(
      context.repo()
    );

    const hasSecurityWorkflow = workflows.workflows.some(
      (w) => w.name.toLowerCase().includes("security") || w.name.toLowerCase().includes("codeql")
    );

    if (!hasSecurityWorkflow) {
      violations.push("No security scanning workflow detected");
    }
  }

  // Check stale vulnerabilities
  const { data: alerts } = await context.octokit.dependabot.listAlertsForRepo(
    context.repo({ state: "open" })
  );

  const staleAlerts = alerts.filter((a) => {
    const age = (Date.now() - new Date(a.created_at).getTime()) / 86400000;
    return age > policy.maxStaleVulnerabilityDays;
  });

  if (staleAlerts.length > 0) {
    violations.push(`${staleAlerts.length} vulnerability alerts older than ${policy.maxStaleVulnerabilityDays} days`);
  }

  if (violations.length > 0) {
    await createComplianceIssue(context, violations);
  }

  return violations;
}
```

### Token Rotation Reminder

```typescript
// Track GitHub App installation token age
async function checkTokenAge(context) {
  const installations = await getInstallations();

  for (const installation of installations) {
    const tokenAge = Date.now() - installation.tokenCreatedAt;
    const daysOld = tokenAge / 86400000;

    if (daysOld > 60) {
      // Reminder to rotate
      await sendNotification({
        type: "token-rotation",
        installation: installation.id,
        message: `Installation token is ${Math.floor(daysOld)} days old`,
      });
    }
  }
}

// Audit personal access tokens used
app.onAny(async (context) => {
  // Check if request used PAT vs app token
  const authHeader = context.req?.headers?.authorization;

  if (authHeader?.startsWith("token ")) {
    // Using PAT - log for audit
    await logTokenUsage({
      type: "personal_access_token",
      repository: context.payload.repository?.full_name,
      event: context.name,
      timestamp: new Date(),
    });
  }
});
```

### Vulnerability Tracking

```typescript
app.on("dependabot_alert.created", async (context) => {
  const { alert, repository } = context.payload;

  // Calculate SLA based on severity
  const slaDays = {
    critical: 1,
    high: 7,
    medium: 30,
    low: 90,
  };

  const sla = slaDays[alert.security_vulnerability.severity] || 30;
  const dueDate = new Date(Date.now() + sla * 24 * 60 * 60 * 1000);

  // Create tracking issue
  await context.octokit.issues.create(
    context.repo({
      title: `[${alert.security_vulnerability.severity.toUpperCase()}] ${alert.security_advisory.summary}`,
      body: `
## Vulnerability Alert

| Field | Value |
|-------|-------|
| Package | ${alert.dependency.package.name} |
| Severity | ${alert.security_vulnerability.severity} |
| CVE | ${alert.security_advisory.cve_id || "N/A"} |
| GHSA | ${alert.security_advisory.ghsa_id} |
| SLA Due Date | ${dueDate.toDateString()} |

### Description
${alert.security_advisory.description}

### Remediation
${alert.security_vulnerability.first_patched_version
  ? `Update to version ${alert.security_vulnerability.first_patched_version.identifier}`
  : "No patch available. Consider removing dependency."}

### References
${alert.security_advisory.references.map((r) => `- ${r.url}`).join("\n")}
      `,
      labels: [
        "security",
        "vulnerability",
        alert.security_vulnerability.severity,
      ],
    })
  );
});
```

## Security Event Types

| Event | Description |
|-------|-------------|
| `secret_scanning_alert` | Exposed secrets |
| `code_scanning_alert` | SAST findings |
| `dependabot_alert` | Dependency vulnerabilities |
| `repository_vulnerability_alert` | Security advisories |
| `security_advisory` | GitHub advisories |

## Security Considerations

- **Least privilege** - Request minimal permissions
- **Audit everything** - Log all security operations
- **Secure webhooks** - Validate signatures
- **Rotate secrets** - Regular credential rotation
- **Defense in depth** - Multiple security layers
- **Incident response** - Defined playbooks

## Example Apps in This Category

- **GitHub Advanced Security** - Built-in security features
- **Snyk** - Security platform
- **Bridgecrew** - Policy as code
- **Checkmarx** - Application security

## Related Categories

- [Code Scanning](code-scanning.md) - Vulnerability detection
- [Dependency Management](dependency-management.md) - Dependency security
- [Reporting](reporting.md) - Security reporting

## See Also

- [GitHub Security Features](https://docs.github.com/en/code-security)
- [Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)
