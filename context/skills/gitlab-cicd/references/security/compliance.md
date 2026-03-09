---
name: compliance
description: Compliance frameworks, audit trails, cost governance, and policy enforcement patterns
---

# Compliance

> **Scope:** Compliance frameworks, audit trails, cost governance, and policy enforcement patterns
> **GitLab version:** 14.0+
> **Source cards:** NEW-09
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Implementing compliance frameworks (SOC 2, ISO 27001) in GitLab CI
- Enforcing required pipeline configuration across projects
- Setting up audit trails for deployments and pipeline changes
- Migrating from deprecated compliance pipelines to security policies

## Key Concepts

### Compliance Frameworks

| Feature | Purpose | Tier |
|---|---|---|
| **Framework labels** | Tag projects with compliance requirements | Premium+ |
| **Compliance pipelines** (deprecated 17.0) | Enforced pipeline config per framework | Ultimate |
| **Security policies** (replacement) | Enforce scanning/approval rules | Ultimate |
| **Centralized compliance** | Manage frameworks across groups | Ultimate |

### Framework Labels

Assign compliance labels (**Settings > General > Compliance frameworks**):
- `SOC 2`, `ISO 27001`, `PCI-DSS`, `HIPAA`
- Custom labels for internal compliance requirements
- Labels appear on project cards and compliance dashboard

### Security Policies (17.0+)

Replacement for compliance pipelines:

| Policy Type | Enforces |
|---|---|
| **Scan execution** | Required security scans |
| **Approval** | Required MR approvals for compliance |
| **Pipeline execution** | Required pipeline configuration (future) |

### Audit Trail

| Feature | What It Tracks |
|---|---|
| **Audit events** | Pipeline creation, deployment, variable changes |
| **Compliance dashboard** | MR approvals, framework adherence |
| **Deployment approvals** | Who approved production deployments |
| **Pipeline activity** | Job execution, artifact creation |

### Deployment Gates

| Gate | Configuration |
|---|---|
| **Protected environments** | Restrict who can deploy (users/groups) |
| **Required approvals** | N approvers before deployment (Premium+) |
| **Deploy freezes** | Block deployments during windows |
| **`when: manual` + `allow_failure: false`** | Blocking approval gate |

## Examples

### Enforced Security Scanning

```yaml
# security-policy.yml (managed by security team)
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml

compliance-check:
  stage: test
  script:
    - echo "Compliance gates verified"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Deployment with Audit Trail

```yaml
deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production"
    - deploy_to_production
  environment:
    name: production
  resource_group: production
  when: manual
  allow_failure: false
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Common Patterns

- **`when: manual` + `allow_failure: false`** for blocking compliance gates
- **Environment protection rules** for production deployment restrictions
- **Security policy enforcement** for required scanning (Ultimate)
- **Framework labels** for project categorization and compliance tracking
- **Deploy freezes** during audit periods or change windows

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Compliance pipelines after 17.0 | Deprecated, will be removed | Migrate to security policies |
| No audit trail for deployments | Compliance gap | Use protected environments + deployment approvals |
| Manual compliance checks | Error-prone, doesn't scale | Automate with security policies |
| No deploy freezes during maintenance | Risky changes during windows | Configure deploy freeze schedules |

## Practitioner Pain Points

1. **Compliance pipelines deprecated in 17.0** — migration to security policies required. No direct 1:1 mapping.
2. **Security policies require Ultimate** — Premium teams must use manual gates and protected environments.
3. **Audit event retention** — plan-dependent. Free tier has limited audit event history.
<!-- TODO: Expand with deeper research on security policy migration paths and SOC 2 pipeline patterns -->

## Related Topics

- [../pipelines/security.md](../pipelines/security.md) — Pipeline security controls
- [../pipelines/manual-gates.md](../pipelines/manual-gates.md) — Manual approval gates
- [scanning.md](scanning.md) — Security scanner integration
- [secrets-management.md](secrets-management.md) — Secrets and OIDC authentication

## Sources

- [Compliance frameworks](https://docs.gitlab.com/user/compliance/compliance_frameworks/)
- [Security policies](https://docs.gitlab.com/user/application_security/policies/)
- [Audit events](https://docs.gitlab.com/administration/audit_events/)

