---
name: dynamic-environments
description: Review apps, dynamic environment naming, auto_stop_in, cleanup jobs, and lifecycle management
---

# Dynamic Environments

> **Scope:** Review apps, dynamic environment naming, auto_stop_in, cleanup jobs, and lifecycle management
> **GitLab version:** 12.0+
> **Source cards:** NEW-02
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Setting up dynamic review app environments per MR
- Configuring environment URLs visible in merge request widgets
- Managing environment lifecycle with auto-stop and teardown
- Implementing environment-scoped variables for per-target configuration

## Key Concepts

### Dynamic Environment Naming

```yaml
environment:
  name: review/$CI_COMMIT_REF_SLUG
  url: https://$CI_COMMIT_REF_SLUG.review.example.com
```

- Variables expand in `name:` and `url:`
- `$CI_COMMIT_REF_SLUG` is URL-safe (lowercased, special chars replaced)

### Review App URL in MR

Two methods to expose the deployment URL:

**Static URL:**
```yaml
environment:
  url: https://$CI_COMMIT_REF_SLUG.review.example.com
```

**Dynamic URL via dotenv:**
```yaml
script:
  - echo "REVIEW_URL=$(get_deployed_url)" >> deploy.env
artifacts:
  reports:
    dotenv: deploy.env
environment:
  url: $REVIEW_URL
```

### Environment Lifecycle

| Event | Configuration |
|---|---|
| **Create/update** | `environment:action: start` (default) |
| **Stop** | `environment:action: stop` |
| **Auto-stop** | `auto_stop_in: 2 days` |
| **Manual stop** | MR widget "Stop" button or manual job |

### Environment-Scoped Variables

Variables scoped to specific environments (**Settings > CI/CD > Variables**):

| Scope | Matches |
|---|---|
| `*` | All environments |
| `production` | Exact match |
| `review/*` | Wildcard match for all review apps |
| `staging` | Exact match |

Scoped variables override unscoped variables when the job's `environment:name` matches.

## Examples

### Full Review App Lifecycle

```yaml
deploy-review:
  stage: deploy
  script:
    - deploy_review_app $CI_COMMIT_REF_SLUG
    - echo "DYNAMIC_URL=https://${CI_COMMIT_REF_SLUG}.review.example.com" >> deploy.env
  artifacts:
    reports:
      dotenv: deploy.env
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: $DYNAMIC_URL
    on_stop: stop-review
    auto_stop_in: 2 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-review:
  stage: deploy
  variables:
    GIT_STRATEGY: none
  script: destroy_review_app $CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual
```

### Multi-Environment with Scoped Variables

```yaml
deploy-staging:
  stage: deploy
  script: deploy --env staging --db $DATABASE_URL
  environment:
    name: staging
    url: https://staging.example.com
  # DATABASE_URL scoped to "staging" environment

deploy-production:
  stage: deploy
  script: deploy --env production --db $DATABASE_URL
  environment:
    name: production
    url: https://example.com
  when: manual
  # DATABASE_URL scoped to "production" environment (different value)
```

## Common Patterns

- **Dynamic environment name** from `$CI_COMMIT_REF_SLUG` for per-MR isolation
- **dotenv artifact** for dynamic URL exposure in MR widget
- **`auto_stop_in` + `on_stop:`** for automatic review app cleanup
- **`GIT_STRATEGY: none`** on stop jobs (branch may be deleted)
- **Environment-scoped variables** for per-target secrets/config (wildcard `review/*`)

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No cleanup strategy | Review apps accumulate, waste resources | Set `auto_stop_in:` and `on_stop:` |
| Hardcoded review app URLs | Conflicts between concurrent MRs | Use `$CI_COMMIT_REF_SLUG` in URL |
| `on_stop` without `GIT_STRATEGY: none` | Fails when source branch deleted | Add `GIT_STRATEGY: none` |
| Missing `when: manual` on stop job | Accidental teardown | Add `when: manual` |

## Practitioner Pain Points

1. **`on_stop` job must be in same or later stage** — jobs in earlier stages can't be stop actions.
2. **`auto_stop_in` resets on redeploy** — pushing to the same MR restarts the timer.
3. **Environment-scoped variable precedence** — more specific scopes win over wildcards.
<!-- TODO: Expand with deeper research on review app infrastructure patterns (K8s namespaces, serverless) -->

## Related Topics

- [strategies.md](strategies.md) — Deployment strategies (blue-green, canary)
- [../pipelines/environments.md](../pipelines/environments.md) — Pipeline environment configuration
- [../variables/precedence.md](../variables/precedence.md) — Environment-scoped variable override

## Sources

- [Environments and deployments](https://docs.gitlab.com/ci/environments/)
- [Review apps](https://docs.gitlab.com/ci/review_apps/)
