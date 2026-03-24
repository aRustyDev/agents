---
name: monorepo-strategies
description: Path-based rules:changes, per-service child pipelines, and selective execution patterns
---

# Monorepo Strategies

> **Scope:** Path-based rules:changes, per-service child pipelines, and selective execution patterns
> **GitLab version:** 12.0+
> **Source cards:** NEW-07
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Managing multiple services/packages in a single repository
- Triggering builds only for changed paths (`rules:changes`)
- Structuring per-service child pipelines in a monorepo
- Optimizing pipeline execution to avoid rebuilding unchanged services

## Key Concepts

### Path-Based Triggering

The primary monorepo pattern uses `rules:changes` to run jobs only when relevant files change.

| Keyword | Purpose |
|---|---|
| `rules:changes:paths:` | Match file paths (glob patterns) |
| `rules:changes:compare_to:` | Base branch for diff comparison (16.0+) |

> **Gotcha:** On new branches with no merge request, `changes:` evaluates to **true** (no base to compare). Always pair with `if: $CI_PIPELINE_SOURCE == "merge_request_event"` or `compare_to:` to avoid this.

### Monorepo Strategies

| Strategy | Approach | Best For |
|---|---|---|
| **Path-filtered jobs** | `rules:changes` per job | Simple monorepo (2–5 services) |
| **Per-service child pipelines** | `trigger:include:` per changed path | Complex monorepo (5+ services) |
| **Dynamic child generation** | Script generates child YAML based on changes | Large monorepo with many modules |

### Key Variables

| Variable | Purpose |
|---|---|
| `CI_MERGE_REQUEST_DIFF_BASE_SHA` | Base SHA for MR diff comparison |
| `GIT_DEPTH` | Must be deep enough for diff; `0` for full history |

## Examples

### Path-Filtered Jobs

```yaml
build-frontend:
  stage: build
  script: cd frontend && npm ci && npm run build
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        paths: [frontend/**/*]
        compare_to: $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      changes:
        paths: [frontend/**/*]
```

### Per-Service Child Pipelines

```yaml
trigger-api:
  stage: test
  trigger:
    include: services/api/.gitlab-ci.yml
    strategy: depend
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes: [services/api/**/*]

trigger-web:
  stage: test
  trigger:
    include: services/web/.gitlab-ci.yml
    strategy: depend
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes: [services/web/**/*]
```

### Dynamic Child Generation

```yaml
detect-changes:
  stage: build
  script:
    - python scripts/detect_changes.py > child-pipeline.yml
  artifacts:
    paths: [child-pipeline.yml]

run-changed:
  stage: test
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: detect-changes
    strategy: depend
```

## Common Patterns

- **`rules:changes` + `compare_to:`** for reliable path-based MR filtering
- **Per-service child pipelines** with `trigger:include:` for isolation
- **API trigger with variables** for parameterized per-service rebuilds
- **Shallow cloning with targeted depth** — balance speed vs. diff accuracy

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `changes:` without `compare_to:` or MR guard | Evaluates true on new branches | Add `if: MR event` or `compare_to:` |
| `rules:changes` + `needs:` creating invalid DAG | Optional jobs break `needs:` references | Use `needs:optional: true` (GitLab 16.0+) |
| Shallow clone too shallow for monorepo diff | Changed files not detected | Increase `GIT_DEPTH` or use `0` |
| Storing trigger tokens in code | Security risk | Use CI/CD variables for trigger tokens |

## Practitioner Pain Points

1. **`changes:` on new branches evaluates true** — most frequent monorepo gotcha. Use `compare_to:` or MR pipeline guard.
2. **Terraform monorepo with multiple state directories** — each directory needs isolated plan/apply with path-filtered child pipelines.
3. **`rules:changes` + `needs:` invalid YAML** — when a path-filtered job is skipped, jobs that `need:` it fail. Use `needs:optional: true`.
<!-- TODO: Expand with deeper research on large monorepo patterns (50+ services) -->

## Related Topics

- [downstream.md](downstream.md) — Parent-child pipeline patterns
- [optimization.md](optimization.md) — DAG and parallelism for monorepos
- [../jobs/git-strategies.md](../jobs/git-strategies.md) — GIT_DEPTH for monorepo clones
- [../yaml/rules-patterns.md](../yaml/rules-patterns.md) — `rules:changes:compare_to:` details

## Sources

- [GitLab CI/CD Monorepo Patterns](https://about.gitlab.com/blog/building-a-gitlab-ci-cd-pipeline-for-a-monorepo-the-easy-way/)
- [rules:changes](https://docs.gitlab.com/ci/yaml/#ruleschanges)
