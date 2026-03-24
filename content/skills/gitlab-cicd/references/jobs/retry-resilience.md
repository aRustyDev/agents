---
name: retry-and-resilience
description: retry:when, allow_failure:exit_codes, timeout, interruptible, and failure handling
---

# Retry & Resilience

> **Scope:** retry:when, allow_failure:exit_codes, timeout, interruptible, and failure handling
> **GitLab version:** 9.0+
> **Source cards:** NEW-14
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult when configuring automatic retry strategies, failure tolerance,
timeouts, or job interruptibility for resilient pipelines.

## Key Concepts

### Resilience Keywords

| Keyword | Purpose | Default | Version |
|---------|---------|---------|--------|
| `retry:max` | Max automatic retry attempts | 0 | 9.5+ |
| `retry:when` | Retry only on specific failure types | all failures | 11.4+ |
| `allow_failure` | Job failure doesn't block pipeline | `false` | 9.0+ |
| `allow_failure:exit_codes` | Tolerate only specific exit codes | none | 13.8+ |
| `timeout` | Job-level execution time limit | project default (1h) | 12.3+ |
| `interruptible` | Allow cancellation when newer pipeline starts | `false` | 12.3+ |

### Retry Failure Types

`retry:when` accepts these failure reasons:

| Failure Type | Meaning |
|-------------|--------|
| `always` | Retry on any failure (default if `when` omitted) |
| `unknown_failure` | Unclassified failure |
| `script_failure` | Script returned non-zero exit |
| `api_failure` | GitLab API failure |
| `stuck_or_timeout_failure` | Job stuck or timed out |
| `runner_system_failure` | Runner infrastructure failure |
| `runner_unsupported` | Runner doesn't support feature |
| `stale_schedule` | Scheduled pipeline couldn't run |
| `job_execution_timeout` | Job exceeded timeout |
| `archived_failure` | Job archived before completion |
| `scheduler_failure` | Scheduler couldn't assign runner |
| `data_integrity_failure` | Structural pipeline error |

### Interruptible Behavior

- When `interruptible: true`, running job is cancelled if a newer pipeline starts on the same ref
- Only affects jobs that haven't started the `deploy` stage
- Set on **all non-deployment jobs** to save compute on superseded pipelines
- Interacts with `workflow:auto_cancel:on_new_commit` (16.0+)

<!-- TODO: Expand with allow_failure interaction with needs: and downstream pipelines -->

## Examples

```yaml
# Targeted retry for transient failures
test:
  script: pytest
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
      - scheduler_failure
  timeout: 30m
  interruptible: true
```

```yaml
# Tolerate specific exit codes
lint:
  script: ./run-lint.sh
  allow_failure:
    exit_codes:
      - 2    # warnings-only exit code
      - 137  # OOM killed (investigate but don't block)
```

```yaml
# Combined resilience pattern
deploy_staging:
  script: ./deploy.sh staging
  environment:
    name: staging
  retry:
    max: 1
    when:
      - api_failure
      - runner_system_failure
  timeout: 15m
  allow_failure: false   # deployment must succeed
  interruptible: false   # don't cancel mid-deploy

optional_smoke_test:
  script: ./smoke-test.sh
  allow_failure: true    # informational, doesn't block
  interruptible: true
```

## Common Patterns

- **`retry:max: 2` with targeted `when`** — retry transient infra failures, not script bugs
- **`allow_failure:exit_codes`** — tolerate known warning exit codes without blanket `allow_failure: true`
- **`interruptible: true` on build/test jobs** — cancel stale jobs when new commits push
- **`timeout`** on all jobs — prevent runaway jobs consuming runner capacity
- **Combine retry + timeout** — `retry:when: [stuck_or_timeout_failure]` with `timeout: 10m`

## Anti-Patterns

- **`retry` without `when` clause** — retries all failures including genuine bugs (wastes time)
- **`allow_failure: true` hiding real problems** — use `exit_codes` for specific tolerance instead
- **Not setting `interruptible`** — stale long-running jobs consume compute unnecessarily
- **`retry:max: 2` on deployment jobs** — can cause double deployments or state issues
- **Large `timeout` values** — masks performance regressions; set realistic limits

## Related Topics

- [execution-flow.md](execution-flow.md) — needs, dependencies, and execution ordering
- [testing.md](testing.md) — test job configuration and reporting
- [../pipelines/optimization.md](../pipelines/optimization.md) — pipeline-level optimization
- [../yaml/keyword-reference.md](../yaml/keyword-reference.md) — complete keyword syntax

## Sources

- [GitLab CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/)
- Context card: NEW-14
