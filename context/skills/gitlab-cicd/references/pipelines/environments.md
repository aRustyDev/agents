---
name: environments-and-deployment-tiers
description: Environment types, deployment tiers, auto_stop_in, on_stop, and dotenv artifact URLs
---

# Environments & Deployment Tiers

> **Scope:** Environment types, deployment tiers, auto_stop_in, on_stop, and dotenv artifact URLs
> **GitLab version:** 9.0+
> **Source cards:** PL-4, WF-4
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Modeling deployment targets (production, staging, review apps)
- Implementing deployment tiers with protection rules
- Creating dynamic review app environments per MR
- Configuring auto-cleanup for temporary environments
- Using `resource_group` to prevent concurrent deployments

## Key Concepts

### Environment Types

| Type | Example | Lifecycle |
|---|---|---|
| **Static** | `production`, `staging` | Permanent, manually managed |
| **Dynamic** | `review/$CI_MERGE_REQUEST_IID` | Created per MR, auto-stopped |

### Deployment Tiers

| Tier | Default Environments | Protection |
|---|---|---|
| `production` | `production`, `prod` | Highest — approval required |
| `staging` | `staging`, `stage`, `model` | Medium — optional approval |
| `testing` | `testing`, `test`, `qa` | Low |
| `development` | `development`, `dev` | None |
| `other` | All others | None |

Tiers determine **deployment order** in the Environments dashboard and **default protection rules**.

### Environment Lifecycle

| Keyword | Purpose |
|---|---|
| `environment:name:` | Environment name (supports variables) |
| `environment:url:` | Deployed application URL |
| `environment:action: start` | Deploy (default) |
| `environment:action: stop` | Tear down environment |
| `environment:auto_stop_in:` | Duration before auto-stop (e.g., `2 days`) |
| `environment:on_stop:` | Job to run when stopping environment |

### Dynamic URLs via dotenv

```yaml
deploy-review:
  script:
    - URL=$(deploy_review_app)
    - echo "REVIEW_URL=$URL" >> deploy.env
  artifacts:
    reports:
      dotenv: deploy.env
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: $REVIEW_URL
    on_stop: stop-review
    auto_stop_in: 2 days
```

### Resource Groups

Prevent concurrent deployments to the same environment:

```yaml
deploy-production:
  resource_group: production  # Only one job at a time
```

| `process_mode` | Behavior |
|---|---|
| `unordered` (default) | First-come-first-served |
| `oldest_first` | Queue order, deploy in sequence |
| `newest_first` | Skip outdated, deploy latest |

### Environment-Scoped Variables

Variables can be scoped to specific environments via **Settings > CI/CD > Variables**:
- Set `Environment scope` to `production`, `staging`, or wildcard `review/*`
- Scoped variables override unscoped variables in matching environment jobs

## Examples

### Review App with Auto-Stop

```yaml
deploy-review:
  stage: deploy
  script:
    - deploy_to review-$CI_MERGE_REQUEST_IID
    - echo "DYNAMIC_URL=https://review-${CI_MERGE_REQUEST_IID}.example.com" >> deploy.env
  artifacts:
    reports:
      dotenv: deploy.env
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: $DYNAMIC_URL
    on_stop: stop-review
    auto_stop_in: 2 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-review:
  stage: deploy
  script: destroy_review review-$CI_MERGE_REQUEST_IID
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    action: stop
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual
```

### Staged Deployment with Approvals

```yaml
deploy-staging:
  stage: staging
  script: deploy_to staging
  environment:
    name: staging
    url: https://staging.example.com

deploy-production:
  stage: production
  script: deploy_to production
  environment:
    name: production
    url: https://example.com
  resource_group: production
  when: manual
  allow_failure: false  # Blocking manual gate
```

## Common Patterns

- **Deploy to staging → manual approval → production** flow
- **`resource_group: production`** for single-flight deployments
- **Dynamic review apps** with `auto_stop_in: 2 days` + `on_stop:` cleanup
- **`dotenv` artifacts** to expose dynamic URLs in MR widgets
- **Environment-scoped variables** for per-target secrets/config
- **Deployment tiers** for ordered progression and protection rules

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No `auto_stop_in` on dynamic environments | Resource leak — environments accumulate | Set `auto_stop_in: 2 days` (or appropriate) |
| Missing `on_stop` for environments with resources | Infrastructure not cleaned up | Define teardown job with `action: stop` |
| No `resource_group` on production | Race condition — concurrent deploys | Add `resource_group: production` |
| Not using deployment tiers | No protection rule defaults | Set tier via `deployment_tier:` or naming convention |

## Practitioner Pain Points

1. **`on_stop` job must be in same stage or later** — common misconfiguration causes "stop job not found" errors.
2. **`auto_stop_in` timer resets on redeploy** — re-running the deploy job restarts the timer.
3. **Environment-scoped variables + wildcard matching** — `review/*` scope matches all review apps, but more specific scopes take precedence.
<!-- TODO: Expand with deeper research on auto-rollback (Ultimate) and deployment approval workflows -->

## Related Topics

- [manual-gates.md](manual-gates.md) — Manual approvals and deploy freezes
- [../deployment/strategies.md](../deployment/strategies.md) — Blue-green, canary, rolling strategies
- [../deployment/environments.md](../deployment/environments.md) — Dynamic environment management
- [../variables/precedence.md](../variables/precedence.md) — Environment-scoped variable precedence

## Sources

- [Environments and deployments](https://docs.gitlab.com/ci/environments/)
- [Resource groups](https://docs.gitlab.com/ci/resource_groups/)

