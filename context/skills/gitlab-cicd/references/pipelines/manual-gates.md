---
name: manual-gates-and-approvals
description: when:manual, environment protection rules, deploy freezes, and approval workflows
---

# Manual Gates & Approvals

> **Scope:** when:manual, environment protection rules, deploy freezes, and approval workflows
> **GitLab version:** 11.0+
> **Source cards:** NEW-09
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Requiring human approval before production deployments
- Implementing `when: manual` gates with blocking behavior
- Configuring environment protection rules and deploy freezes
- Building compliance-friendly deployment workflows with audit trails

## Key Concepts

### Manual Jobs

| Configuration | Behavior |
|---|---|
| `when: manual` | Job requires manual trigger; pipeline continues |
| `when: manual` + `allow_failure: false` | **Blocking gate** — pipeline waits for manual action |
| `when: manual` + `allow_failure: true` (default) | Non-blocking — pipeline proceeds without manual action |

### Environment Protection Rules

Configure in **Settings > CI/CD > Protected environments**:

| Rule | Purpose | Tier |
|---|---|---|
| **Allowed to deploy** | Restrict to specific users/groups | Premium+ |
| **Required approvals** (N approvers) | Require N different users to approve | Premium+ |
| **Deploy freezes** | Block deployments during maintenance windows | Free |

### Manual Pipeline with Prefilled Variables

```yaml
variables:
  DEPLOY_TARGET:
    value: staging
    description: "Target environment"
    options:
      - staging
      - production
```

Users see a dropdown in the "Run pipeline" UI.

### Deployment Approval Flow (Premium+)

1. Pipeline reaches manual gate job
2. Job shows "Pending approval" status
3. Configured approvers approve/reject via UI or API
4. Approved → job runs; Rejected → job fails

### Deploy Freezes

- **Settings > CI/CD > Deploy freezes** — define date ranges
- During freeze, manual deployment jobs are blocked
- Scheduled/automatic jobs still run (only manual gates are frozen)
- `$CI_DEPLOY_FREEZE` variable is `true` during freeze windows

### Compliance Framework (Ultimate)

- **Compliance pipelines** (deprecated in 17.0) → replaced by **Security policies**
- **Compliance framework labels** enforce required pipeline configuration
- Centralized compliance management across groups

## Examples

### Blocking Manual Gate

```yaml
deploy-staging:
  stage: staging
  script: deploy staging
  environment:
    name: staging

approve-production:
  stage: gate
  script: echo "Approved for production"
  when: manual
  allow_failure: false  # Blocks pipeline

deploy-production:
  stage: production
  script: deploy production
  environment:
    name: production
  needs: [approve-production]
```

### Deploy Freeze Guard

```yaml
deploy:
  stage: deploy
  script: deploy production
  rules:
    - if: $CI_DEPLOY_FREEZE
      when: manual  # Allow override during freeze
    - when: on_success
  environment:
    name: production
```

### Parameterized Manual Deployment

```yaml
variables:
  ENVIRONMENT:
    value: staging
    description: "Deploy target"
    options: [staging, production, canary]
  VERSION:
    description: "Version to deploy (e.g., v1.2.3)"

deploy:
  stage: deploy
  script: deploy --env $ENVIRONMENT --version $VERSION
  when: manual
  environment:
    name: $ENVIRONMENT
```

## Common Patterns

- **`when: manual` + `allow_failure: false`** for required approval gates
- **Environment protection rules** for production deployment restrictions
- **`variables:options`** for dropdown selection in manual pipeline UI
- **Deploy freezes** during maintenance windows (`$CI_DEPLOY_FREEZE`)
- **`resource_group: production`** combined with manual gates for safe deployments

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `when: manual` without `allow_failure` consideration | Default `allow_failure: true` — non-blocking | Set `allow_failure: false` for blocking gates |
| No environment protection on production | Anyone with push access can deploy | Configure protected environments |
| Compliance pipeline without migration plan | Deprecated in 17.0 | Migrate to security policies |
| Manual gates without audit trail | No record of who approved | Use environment deployment approvals (Premium+) |

## Practitioner Pain Points

1. **`allow_failure: true` is the default** for manual jobs — most teams want blocking behavior but forget to set `allow_failure: false`.
2. **Deploy freeze only blocks manual trigger** — automatic/scheduled deployments still run during freeze windows.
3. **Compliance pipelines deprecated** — teams on 17.0+ should migrate to security policies for enforced pipeline configuration.
<!-- TODO: Expand with deeper research on multi-level approval chains and compliance framework integration -->

## Related Topics

- [environments.md](environments.md) — Environment lifecycle and resource groups
- [../security/compliance.md](../security/compliance.md) — Compliance frameworks and audit
- [types-and-triggers.md](types-and-triggers.md) — Pipeline triggering methods

## Sources

- [Manual jobs](https://docs.gitlab.com/ci/jobs/job_control/#create-a-job-that-must-be-run-manually)
- [Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)
- [Deploy freezes](https://docs.gitlab.com/user/project/releases/#deploy-freezes)
