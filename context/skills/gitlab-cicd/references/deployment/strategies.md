---
name: deployment-strategies
description: Blue-green, canary, rolling deployments, feature flags, and automated rollback patterns
---

# Deployment Strategies

> **Scope:** Blue-green, canary, rolling deployments, feature flags, and automated rollback patterns
> **GitLab version:** 12.0+
> **Source cards:** NEW-01
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Choosing between blue-green, canary, rolling, and feature flag strategies
- Configuring incremental rollouts in GitLab CI
- Implementing automatic rollback on deployment failure
- Setting up review apps with auto-cleanup

## Key Concepts

### Deployment Strategies

| Strategy | Risk | Rollback | Best For |
|---|---|---|---|
| **Blue-green** | Low | Instant (swap) | Stateless applications |
| **Canary** | Low | Remove canary | Traffic-splittable services |
| **Rolling** | Medium | Redeploy previous | Kubernetes / auto-scaling |
| **Feature flags** | Lowest | Toggle off | Gradual feature exposure |
| **Incremental rollout** | Low | Stop at current % | Progressive validation |

### Incremental Rollouts

GitLab supports manual and timed incremental rollouts:

```yaml
deploy-10%:
  environment:
    name: production
  script: deploy --percentage 10
  when: manual

deploy-50%:
  environment:
    name: production
  script: deploy --percentage 50
  when: manual

deploy-100%:
  environment:
    name: production
  script: deploy --percentage 100
  when: manual
```

### Review Apps

Dynamic environments for per-MR deployments:

| Feature | Configuration |
|---|---|
| **Dynamic name** | `environment:name: review/$CI_COMMIT_REF_SLUG` |
| **Auto-stop** | `auto_stop_in: 2 days` |
| **Teardown** | `on_stop: stop-review` job |
| **URL in MR** | `environment:url:` or dotenv artifact |

### Auto-Rollback (Ultimate)

Available on Ultimate tier — automatic rollback to last successful deployment on environment failure.

## Examples

### Review App with Cleanup

```yaml
deploy-review:
  stage: deploy
  script: deploy_review $CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_COMMIT_REF_SLUG.review.example.com
    on_stop: stop-review
    auto_stop_in: 2 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-review:
  stage: deploy
  variables:
    GIT_STRATEGY: none
  script: destroy_review $CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual
```

### Blue-Green Deploy

```yaml
deploy-green:
  stage: deploy
  script:
    - deploy_to green
    - run_smoke_tests green
    - swap_traffic blue green
  environment:
    name: production
  when: manual
```

### Feature Flag Guard

```yaml
deploy:
  script:
    - deploy_with_flags
  environment:
    name: production
  rules:
    - if: $FEATURE_FLAG_ENABLED == "true"
```

## Common Patterns

- **`auto_stop_in: 2 days`** for review app environments
- **`on_stop:` with `GIT_STRATEGY: none`** for cleanup on deleted branches
- **Dynamic environment names** from `$CI_COMMIT_REF_SLUG`
- **Incremental rollout** with manual gates at 10%, 50%, 100%
- **`resource_group:`** to prevent concurrent deployments

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No `auto_stop_in` on review apps | Resource leak | Set `auto_stop_in: 2 days` |
| `on_stop` job without `GIT_STRATEGY: none` | Fails on deleted branches | Add `GIT_STRATEGY: none` |
| Missing `when: manual` on stop jobs | Accidental teardown | Add `when: manual` |
| No rollback strategy | Stuck with broken deployment | Implement manual or auto rollback |

## Practitioner Pain Points

1. **`on_stop` job must use `GIT_STRATEGY: none`** — the source branch may be deleted when MR is merged.
2. **`auto_stop_in` timer resets on each deploy** — redeploying restarts the countdown.
3. **Auto-rollback requires Ultimate tier** — free/premium teams need manual rollback patterns.
<!-- TODO: Expand with deeper research on Kubernetes rolling update integration and canary analysis -->

## Related Topics

- [environments.md](environments.md) — Dynamic environment management
- [../pipelines/environments.md](../pipelines/environments.md) — Environment lifecycle in pipelines
- [../pipelines/manual-gates.md](../pipelines/manual-gates.md) — Manual approval gates

## Sources

- [Environments and deployments](https://docs.gitlab.com/ci/environments/)
- [Review apps](https://docs.gitlab.com/ci/review_apps/)
