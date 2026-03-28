---
name: pipeline-types-and-triggers
description: Pipeline taxonomy, CI_PIPELINE_SOURCE values, subscriptions, and triggering methods
---

# Pipeline Types & Triggers

> **Scope:** Pipeline taxonomy, CI_PIPELINE_SOURCE values, subscriptions, and triggering methods
> **GitLab version:** 9.0+
> **Source cards:** PL-1, NEW-19
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Understanding how different pipeline types are triggered
- Choosing the right pipeline architecture (basic, DAG, parent-child, multi-project)
- Debugging why a pipeline fired (or didn't) using `CI_PIPELINE_SOURCE`
- Setting up cross-project pipeline subscriptions

## Key Concepts

### Pipeline Types

| Type | Trigger | Key Feature |
|---|---|---|
| **Basic (stage-sequential)** | Push, MR, schedule, manual | Jobs run in stage order |
| **DAG** | Same triggers + `needs:` keyword | Jobs run as soon as dependencies finish |
| **Parent-child** | `trigger:include:` in parent job | Same project, max 2 nesting levels |
| **Multi-project** | `trigger:project:` in upstream job | Different projects, independent pipelines |
| **Merge request** | MR create/update | Detached, merged-results, or merge-train |
| **Merged results** | MR with merged_results enabled | Tests on merge result, not source branch |
| **Merge train** | MR added to merge train | Sequential merge testing queue |
| **Scheduled** | Cron schedule | `CI_PIPELINE_SOURCE == "schedule"` |

### CI_PIPELINE_SOURCE Values

| Value | Trigger |
|---|---|
| `push` | Git push to branch |
| `merge_request_event` | MR create/update |
| `schedule` | Scheduled pipeline |
| `web` | "Run pipeline" button in UI |
| `api` | Pipeline API call |
| `trigger` | Trigger token API |
| `pipeline` | Multi-project downstream |
| `parent_pipeline` | Parent-child downstream |
| `chat` | ChatOps `/run` command |

### Pipeline Duration

Pipeline duration = **longest path** through the DAG, not the sum of all job durations. Unnecessary serialization via stages (when `needs:` would parallelize) is the most common performance mistake.

### Parallelism

| Keyword | Purpose |
|---|---|
| `parallel: N` | Run N copies of the same job (1–200) |
| `parallel:matrix:` | Generate jobs from variable combinations |
| `needs:` | DAG — run as soon as dependencies complete |

### Pipeline Subscriptions

Subscribe to another project's pipeline completions to trigger your own pipeline when an upstream dependency delivers a new version.

- Configured in **Settings > CI/CD > Pipeline subscriptions**
- `CI_PIPELINE_SOURCE` = `pipeline` in the triggered pipeline
- **Limit:** 2 upstream subscriptions per project (Free), configurable on Premium+

### Skip Directives

| Directive | Behavior |
|---|---|
| `[ci skip]` / `[skip ci]` | Skip pipeline for this commit |
| `git push -o ci.skip` | Push option to skip pipeline |

> **Warning:** Never use `[skip ci]` in automated commits (e.g., semantic-release) — it suppresses tag pipelines too.

## Examples

### DAG Parallel Testing

```yaml
stages: [build, test, deploy]

build-app:
  stage: build
  script: make build
  artifacts:
    paths: [dist/]

unit-tests:
  stage: test
  needs: [build-app]
  script: make test-unit

integration-tests:
  stage: test
  needs: [build-app]
  script: make test-integration

deploy:
  stage: deploy
  needs: [unit-tests, integration-tests]
  script: make deploy
```

### Parallel Matrix

```yaml
test:
  stage: test
  parallel:
    matrix:
      - PLATFORM: [linux, macos, windows]
        VERSION: ["3.10", "3.11", "3.12"]
  script: tox -e py${VERSION}
```

### Pipeline Subscription Trigger

```yaml
# Triggered when upstream "shared-libs" project completes
downstream-rebuild:
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline"
  script: make rebuild-with-latest-libs
```

## Common Patterns

- **5-stage standard:** `build → test → scan → stage → deploy`
- **`needs:` DAG** for parallel execution across stages
- **Rules-based stage inclusion** for conditional job flows
- **Manual pipelines** with `variables:options` for deployment targets
- **Pipeline subscriptions** for cross-project dependency triggering
- **`parallel:matrix`** for cross-platform / multi-version testing

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `only/except` instead of `rules:` | Deprecated, less powerful | Migrate to `rules:` |
| 10+ stages with serial execution | Slow — duration = longest path | Use `needs:` for DAG parallelism |
| Stage-only when DAG would parallelize | Unnecessary wait times | Add `needs:` to skip stage barriers |
| Over-parallelizing (too many tiny jobs) | Overhead exceeds savings | Batch small tasks into fewer jobs |
| `[skip ci]` in automated commits | Breaks downstream/tag pipelines | Use selective `rules:` instead |

## Practitioner Pain Points

1. **`needs:` vs `stages:` confusion** — `stages:` defines order; `needs:` creates DAG shortcuts. Both can coexist.
2. **Pipeline duration ≠ job sum** — longest path through DAG determines wall-clock time.
3. **`parallel:matrix` + `needs:` invalid YAML** — generated job names include matrix values; reference with `needs: [job-name: [MATRIX_VAR: value]]`.
<!-- TODO: Expand with deeper research on pipeline subscription limits and cross-project patterns -->

## Related Topics

- [merge-request.md](merge-request.md) — MR pipeline types and duplicate prevention
- [downstream.md](downstream.md) — Parent-child and multi-project pipelines
- [optimization.md](optimization.md) — DAG and parallelism strategies
- [../jobs/execution-flow.md](../jobs/execution-flow.md) — `needs:`, `dependencies:`, `resource_group:`

## Sources

- [GitLab CI/CD Pipelines](https://docs.gitlab.com/ci/pipelines/)
- [Pipeline efficiency](https://docs.gitlab.com/ci/pipelines/pipeline_efficiency/)
- [Downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)
