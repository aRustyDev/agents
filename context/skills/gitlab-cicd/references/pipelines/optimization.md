---
name: pipeline-optimization
description: DAG with needs:, parallelism, compute minutes optimization, and interruptible jobs
---

# Pipeline Optimization

> **Scope:** DAG with needs:, parallelism, compute minutes optimization, and interruptible jobs
> **GitLab version:** 12.2+
> **Source cards:** NEW-03
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Reducing pipeline wall-clock time (50–80% possible)
- Minimizing compute minutes usage (SaaS cost optimization)
- Choosing between stage-sequential and DAG execution
- Optimizing Docker image size, caching, and artifact management

## Key Concepts

### Execution Models

| Model | Mechanism | Wall Time |
|---|---|---|
| **Stage-sequential** | Jobs wait for all jobs in previous stage | Sum of longest job per stage |
| **DAG (`needs:`)** | Jobs run when their dependencies finish | Longest path through dependency graph |
| **Parent-child** | Parallel sub-pipelines | Parallel children run concurrently |

### Optimization Levers

| Lever | Impact | Effort |
|---|---|---|
| **`needs:` DAG** | High — removes stage wait times | Low — add `needs:` to jobs |
| **Caching** | High — skip repeated downloads | Medium — configure `cache:key:files` |
| **Smaller Docker images** | Medium — reduce pull/extract time | Medium — switch to `-slim` or `-alpine` |
| **`parallel:matrix`** | High — distribute test workload | Low — split test suite |
| **`interruptible: true`** | Medium — cancel outdated pipelines | Low — add to jobs safe to cancel |
| **Artifact expiration** | Low — reduce storage costs | Low — set `expire_in:` |
| **Rules filtering** | High — skip unnecessary jobs | Medium — add `rules:changes` |

### Interruptible Jobs

```yaml
job:
  interruptible: true  # Cancel this job if a newer pipeline starts
```

Combined with `workflow:auto_cancel:on_new_commit: interruptible` (16.0+), outdated pipelines are automatically cancelled.

### Compute Minutes

SaaS cost factors:
- **Cost multiplier** varies by runner type (Linux 1×, macOS 6×, Windows 1×)
- **`parallel: N`** uses N × job minutes
- **`interruptible: true`** saves minutes by cancelling superseded jobs

## Examples

### DAG for Parallel Testing

```yaml
stages: [build, test, scan, deploy]

build:
  stage: build
  script: make build
  artifacts:
    paths: [dist/]

unit-test:
  stage: test
  needs: [build]
  script: make test-unit
  interruptible: true

lint:
  stage: test
  needs: []  # No dependencies — runs immediately
  script: make lint
  interruptible: true

security-scan:
  stage: scan
  needs: [build]
  script: make scan

deploy:
  stage: deploy
  needs: [unit-test, security-scan]
  script: make deploy
```

### Test Splitting with parallel

```yaml
rspec:
  stage: test
  parallel: 4
  script:
    - bundle exec rspec $(scripts/split-tests.sh $CI_NODE_INDEX $CI_NODE_TOTAL)
  artifacts:
    reports:
      junit: rspec-*.xml
```

### Auto-Cancel Outdated Pipelines

```yaml
workflow:
  auto_cancel:
    on_new_commit: interruptible

test:
  interruptible: true
  script: make test

deploy:
  interruptible: false  # Never cancel deployments
  script: make deploy
  when: manual
```

## Common Patterns

- **DAG with `needs:`** for test parallelism — most impactful single optimization
- **`needs: []`** (empty) to start a job immediately, regardless of stage
- **`parallel:matrix`** for cross-platform / multi-version test distribution
- **`interruptible: true`** on test/lint jobs + `auto_cancel` workflow
- **`cache:key:files: [package-lock.json]`** for dependency caching
- **`expire_in: 1 week`** on non-production artifacts

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| All jobs in sequential stages, no DAG | Pipeline duration = sum of stages | Add `needs:` for parallel execution |
| Bloated Docker images (1GB+) | Minutes wasted pulling/extracting | Use `-slim`/`-alpine` variants |
| No `interruptible:` on safe jobs | Outdated pipelines waste minutes | Mark test/lint as `interruptible: true` |
| Caching everything | Cache upload/download overhead | Cache only expensive-to-generate files |
| Missing `expire_in:` on artifacts | Storage costs grow unbounded | Set `expire_in: 1 week` (or appropriate) |

## Practitioner Pain Points

1. **DAG with `needs:` can be confusing** — must reference exact job names, including matrix-generated names.
2. **`parallel: N` + test splitting requires script** — GitLab provides `$CI_NODE_INDEX` and `$CI_NODE_TOTAL` but splitting logic is user's responsibility.
3. **Interruptible doesn't work on running jobs by default** — only cancels pending/waiting jobs unless the runner supports graceful termination.
<!-- TODO: Expand with deeper research on compute minutes optimization strategies and cost modeling -->

## Related Topics

- [types-and-triggers.md](types-and-triggers.md) — Pipeline architecture choices
- [downstream.md](downstream.md) — Parent-child for parallel sub-pipelines
- [../jobs/caching.md](../jobs/caching.md) — Advanced caching strategies
- [../jobs/execution-flow.md](../jobs/execution-flow.md) — `needs:`, DAG, `resource_group:`

## Sources

- [Pipeline efficiency](https://docs.gitlab.com/ci/pipelines/pipeline_efficiency/)
- [GitLab CI optimization tips](https://dev.to/zenika/gitlab-ci-optimization-15-tips-for-faster-pipelines-55al)

