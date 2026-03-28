---
name: execution-flow
description: needs: DAG, dependencies, resource_group, parallel:matrix, and job ordering patterns
---

# Execution Flow

> **Scope:** needs: DAG, dependencies, resource_group, parallel:matrix, and job ordering patterns
> **GitLab version:** 12.2+
> **Source cards:** JB-3
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Controlling job execution order beyond simple stage-based sequencing
- Building DAG pipelines with `needs:` for parallel execution
- Managing deployment concurrency with `resource_group:`
- Understanding `dependencies:` vs `needs:` for artifact control
- Using `parallel:` and `parallel:matrix:` for job multiplication

## Key Concepts

### Execution Keywords

| Keyword | Purpose | Default |
|---|---|---|
| `stage:` | Assign job to a stage | `test` |
| `needs:` | DAG — run when dependencies finish | None (stage-based) |
| `needs:optional: true` | Don't fail if needed job was skipped | `false` |
| `needs:artifacts: false` | DAG edge without artifact download | `true` |
| `dependencies:` | Control which artifacts to download | All from prior stages |
| `resource_group:` | Limit concurrent runs of this job | None |
| `timeout:` | Maximum job duration | Project default (1h) |

### DAG with needs:

`needs:` creates directed acyclic graph (DAG) edges, allowing jobs to start before their stage begins:

```
build ──→ unit-test ──→ deploy
     └──→ lint ──────────┘
```

Without `needs:`, `lint` waits for `build` to complete (stage barrier). With `needs: []`, `lint` starts immediately.

### needs: vs dependencies:

| Feature | `needs:` | `dependencies:` |
|---|---|---|
| Creates DAG edge | Yes | No |
| Controls artifact download | Yes (by default) | Yes |
| Skips stage barrier | Yes | No |
| Can reference cross-pipeline | Yes (`needs:pipeline:job:`) | No |
| Can reference cross-project | Yes (`needs:project:`) | No |

### Resource Groups

Control deployment concurrency:

```yaml
deploy-production:
  resource_group: production
```

| Process Mode | Behavior |
|---|---|
| `unordered` (default) | First available runs |
| `oldest_first` | Queue in order |
| `newest_first` | Skip outdated, run latest |

### Parallel Execution

| Keyword | Purpose |
|---|---|
| `parallel: N` | Run N copies (1–200), `CI_NODE_INDEX`/`CI_NODE_TOTAL` |
| `parallel:matrix:` | Generate jobs from variable combinations |

Matrix-generated job names: `job-name: [VAR1_VALUE, VAR2_VALUE]`

## Examples

### DAG Fan-Out / Fan-In

```yaml
stages: [build, test, deploy]

build:
  stage: build
  script: make build
  artifacts:
    paths: [dist/]

unit-test:
  stage: test
  needs: [build]
  script: make test-unit

lint:
  stage: test
  needs: []  # Starts immediately, no dependencies
  script: make lint

integration-test:
  stage: test
  needs: [build]
  script: make test-integration

deploy:
  stage: deploy
  needs: [unit-test, integration-test, lint]
  script: make deploy
```

### Conditional DAG with Optional Needs

```yaml
build-docs:
  stage: build
  script: mkdocs build
  rules:
    - changes: [docs/**]

deploy:
  stage: deploy
  needs:
    - job: build-app
    - job: build-docs
      optional: true  # Don't fail if build-docs was skipped
  script: make deploy
```

### Resource Group for Serial Deploys

```yaml
deploy-staging:
  stage: deploy
  resource_group: staging
  script: deploy staging
  environment:
    name: staging

deploy-production:
  stage: deploy
  resource_group: production
  script: deploy production
  environment:
    name: production
  when: manual
```

## Common Patterns

- **`needs:` for fan-in/fan-out** — most impactful DAG pattern
- **`needs: []`** (empty) to start immediately, bypass stage order
- **`needs:optional: true`** for conditional jobs in the DAG
- **`dependencies: []`** to skip artifact downloads when not needed
- **`resource_group:`** on all deployment jobs to prevent concurrent deploys
- **`parallel:matrix`** for cross-platform testing

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Only stages when `needs:` would parallelize | Unnecessary serial execution | Add `needs:` references |
| `dependencies: []` not set when artifacts unneeded | Slow artifact downloads | Add `dependencies: []` |
| Complex DAG with 50+ `needs:` edges | Impossible to debug | Simplify with parent-child pipelines |
| `needs:` referencing skipped jobs without `optional:` | Pipeline fails | Add `optional: true` |
| No `resource_group` on production deploy | Concurrent deploy race | Add `resource_group: production` |

## Practitioner Pain Points

1. **`dependencies:` vs `needs:` confusion** — `needs:` = DAG + artifacts, `dependencies:` = artifacts only. Most teams want `needs:`.
2. **Matrix job names in `needs:` references** — must use exact generated name format: `job: [VAR: value]`.
3. **`needs:optional` required for conditional DAG** — if a needed job is skipped by `rules:`, the job fails unless `optional: true`.
<!-- TODO: Expand with deeper research on DAG visualization and debugging strategies -->

## Related Topics

- [../pipelines/optimization.md](../pipelines/optimization.md) — Pipeline-level optimization with DAG
- [../pipelines/downstream.md](../pipelines/downstream.md) — Cross-pipeline `needs:` references
- [artifacts.md](artifacts.md) — Artifact download control with `dependencies:`

## Sources

- [Job control](https://docs.gitlab.com/ci/jobs/job_control/)
- [DAG pipelines](https://docs.gitlab.com/ci/jobs/job_control/#directed-acyclic-graph)
- [Resource groups](https://docs.gitlab.com/ci/resource_groups/)
