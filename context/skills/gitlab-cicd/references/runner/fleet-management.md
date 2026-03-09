---
name: fleet-management
description: config.toml structure, auto-reload, Prometheus metrics, health checks, and fleet planning
---

# Fleet Management

> **Scope:** config.toml structure, auto-reload, Prometheus metrics, health checks, and fleet planning
> **GitLab version:** 9.0+
> **Source cards:** RN-6
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You're setting up `config.toml` for a runner fleet
- You need Prometheus metrics for runner monitoring
- You're tuning concurrency, health checks, or log limits
- You need to understand config auto-reload vs manual restart
- You're planning fleet architecture (single vs multi-manager)

**Do NOT use when:**
- You need executor-specific configuration — see [executors.md](executors.md)
- You need autoscaler policy details — see [autoscaling.md](autoscaling.md)

## Key Concepts

### Global config.toml Parameters

| Parameter | Default | Purpose |
|---|---|---|
| `concurrent` | — | **Max jobs across ALL runners combined**; 0 is forbidden (critical error) |
| `check_interval` | `3` | Seconds between polling GitLab for new jobs |
| `log_level` | `info` | Verbosity: `debug`, `info`, `warn`, `error`, `fatal`, `panic` |
| `log_format` | `runner` | Output format: `runner` (colored), `text`, `json` |
| `connection_max_age` | `15m` | Max TLS keepalive lifetime to GitLab; 0=persist indefinitely |
| `listen_address` | — | Prometheus metrics HTTP server bind address (e.g., `0.0.0.0:9252`) |
| `shutdown_timeout` | `30` | Seconds for forceful shutdown before process exits |
| `sentry_dsn` | — | Send system-level errors to Sentry |

### Per-Runner Management Parameters

| Parameter | Default | Purpose |
|---|---|---|
| `limit` | `0` | Max concurrent jobs for this runner; 0=unlimited (bounded by `concurrent`) |
| `request_concurrency` | `1` | Parallel new-job requests to GitLab per runner |
| `strict_check_interval` | `false` | Disable faster-than-check_interval re-poll after job pickup |
| `output_limit` | 4096 KB | Max build log size |
| `unhealthy_requests_limit` | — | Consecutive unhealthy responses before runner worker disabled |
| `unhealthy_interval` | — | Duration worker is disabled after exceeding unhealthy limit |
| `pre_get_sources_script` | — | Commands before git clone |
| `post_get_sources_script` | — | Commands after git clone/submodule update |
| `pre_build_script` | — | Commands before job script |
| `post_build_script` | — | Commands after job script, before `after_script` |

### Config Reload Behavior

- `config.toml` **auto-reloads every 3 seconds** — no restart needed for `[[runners]]` changes
- **Autoscaler section is NOT hot-reloaded** — requires `SIGHUP` or process restart
- Send `SIGHUP` for manual graceful reload
- CLI flags (`--debug`, `--log-level`) take precedence over `config.toml` values

### Fleet Architecture Tiers

| Tier | Description | Use Case |
|---|---|---|
| Basic | One manager, one `[[runners]]`, shell/docker | Small teams, low job volume |
| Intermediate | One manager, multiple `[[runners]]` | Multi-executor support, 10-50 concurrent jobs |
| Autoscaling | 2+ managers, autoscaling executors | Large fleets, 50+ concurrent jobs |

> **Key rule:** Start with minimum 2 runner managers for autoscaling deployments.
> The runner manager itself should NOT execute CI/CD jobs.
> Multiple managers can share the same runner auth token with unique `system_id`.

### Prometheus Metrics (22 exposed)

Key metrics at `listen_address` endpoint:

| Metric | Type | Purpose |
|---|---|---|
| `gitlab_runner_concurrent` | gauge | Current `concurrent` setting value |
| `gitlab_runner_limit` | gauge | Current `limit` setting value |
| `gitlab_runner_jobs` | gauge | Jobs currently executing (with scope labels) |
| `gitlab_runner_jobs_total` | counter | Total jobs executed |
| `gitlab_runner_job_duration_seconds` | histogram | Job duration distribution |
| `gitlab_runner_job_queue_duration_seconds` | histogram | Time spent waiting in queue |
| `gitlab_runner_request_concurrency` | gauge | Current concurrent job requests |
| `gitlab_runner_errors_total` | counter | Caught errors (labels: warning, error) — use `rate()` |
| `gitlab_runner_api_request_statuses_total` | counter | API requests by runner, endpoint, status |
| `gitlab_runner_autoscaling_machine_states` | gauge | Machines per state in autoscaling provider |
| `gitlab_runner_autoscaling_machine_creation_duration_seconds` | histogram | Machine creation time |
| `gitlab_runner_version_info` | gauge | Constant 1, labeled with build stats |

> **Cardinality warning:** `gitlab_runner_job_stage_duration_seconds` creates a label per
> pipeline stage — can overwhelm Prometheus. Use `metric_relabel_configs` to drop or filter.

## Examples

### Fleet Manager with Monitoring

```toml
# config.toml — fleet manager with Prometheus
concurrent = 50
check_interval = 3
log_level = "info"
log_format = "json"
listen_address = "0.0.0.0:9252"    # Prometheus metrics
shutdown_timeout = 60
connection_max_age = "15m"

[[runners]]
  name = "fleet-docker"
  executor = "docker-autoscaler"
  limit = 30
  request_concurrency = 5
  output_limit = 8192              # 8 MB log limit
  unhealthy_requests_limit = 10
  unhealthy_interval = "5m"
  [runners.docker]
    image = "alpine:3.21"

[[runners]]
  name = "fleet-k8s"
  executor = "kubernetes"
  limit = 20
  request_concurrency = 3
  [runners.kubernetes]
    namespace = "ci"
```

### Health Check and Recovery Tuning

```toml
# config.toml — tuned for resilience
[[runners]]
  name = "resilient-runner"
  executor = "docker"
  unhealthy_requests_limit = 5     # Disable after 5 failures
  unhealthy_interval = "2m"        # Re-enable after 2 min
  job_status_final_update_retry_limit = 5
  strict_check_interval = false    # Fast re-poll after job pickup
```

## Common Patterns

- **Prometheus metrics endpoint** for fleet monitoring (`listen_address`)
- **`unhealthy_interval` tuning** for fast recovery after GitLab upgrades
- **Multiple `[[runners]]` in single config** for multi-project/multi-executor support
- **`SIGHUP`** for zero-downtime config updates (especially autoscaler changes)
- **`log_format = "json"`** for structured log aggregation
- **`connection_max_age = "15m"`** to cycle TLS connections after GitLab upgrades

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Restarting runner for config changes | Unnecessary — `config.toml` auto-reloads every 3s | Just edit the file; use SIGHUP for autoscaler changes |
| Not monitoring runner health metrics | Blind to fleet degradation, queue buildup | Enable `listen_address` and scrape with Prometheus |
| Single runner config for all environments | No isolation between sensitive and non-sensitive workloads | Use separate `[[runners]]` sections with different security profiles |
| `concurrent=0` | Causes critical error — runner won't start | Set to at least 1 |
| Not setting `output_limit` | Massive logs can overwhelm storage and UI | Set appropriate limit (default 4096 KB is reasonable) |

## Practitioner Pain Points

1. **Runners go idle during GitLab upgrades, slow to recover** — GitLab API returns errors during upgrade; `unhealthy_interval` can be too long. **Fix:** Tune `unhealthy_interval` to 2-5m; monitor `gitlab_runner_errors_total` for rate spikes.

2. **Autoscaler config changes don't hot-reload** — Auto-reload (every 3s) covers `[[runners]]` but NOT the autoscaler section. **Fix:** Use `SIGHUP` for graceful restart; plan changes during low-traffic windows.

3. **No built-in fleet management dashboard** — GitLab provides Prometheus metrics but not out-of-box Grafana dashboards. **Fix:** Use [GitLab.com runbooks repo](https://gitlab.com/gitlab-com/runbooks) for dashboard JSON templates.

4. **High cardinality metrics overwhelm Prometheus** — `gitlab_runner_job_stage_duration_seconds` creates a label per pipeline stage. **Fix:** Use `metric_relabel_configs` to drop or keep only relevant stages.

## Version Notes

| Version | Change |
|---|---|
| 9.0+ | Prometheus metrics endpoint via `listen_address` |
| 14.8+ | `unhealthy_requests_limit` and `unhealthy_interval` for worker health |
| 15.1+ | `strict_check_interval` option |
| 16.x | `system_id` for runner instance deduplication |
| 17.5+ | `job_stage_duration_seconds` metric (high cardinality warning) |

## Decision Guide

| Scenario | Recommendation | Monitoring |
|---|---|---|
| Small team, < 10 concurrent jobs | Single manager, shell/docker, `concurrent=10` | Basic — `listen_address` for Prometheus |
| Medium team, 10-50 concurrent | Single manager, multiple `[[runners]]`, docker | Grafana dashboards for queue and duration |
| Large fleet, 50+ concurrent | 2+ managers, `docker-autoscaler`, time-based policies | Full Grafana stack; alert on queue, errors, machine states |
| GitLab upgrade resilience | `unhealthy_interval=5m`, `connection_max_age=15m` | Alert on `gitlab_runner_errors_total` rate increase |
| Cost optimization | Monitor `autoscaling_machine_states` for right-sizing `idle_count` | Track machine creation latency vs job queue duration |

## Related Topics

- [executors.md](executors.md) — Executor types configured within `[[runners]]` sections
- [autoscaling.md](autoscaling.md) — `[runners.autoscaler]` config (not hot-reloaded)
- [security.md](security.md) — Security parameters within `[[runners]]` and `[runners.docker]`
- [../pipelines/optimization.md](../pipelines/optimization.md) — Pipeline-level changes that affect fleet sizing

## Sources

- [GitLab Runner Advanced Configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- [GitLab Runner Fleet Scaling](https://docs.gitlab.com/runner/fleet_scaling/)
- [GitLab.com Runbooks (Grafana Dashboards)](https://gitlab.com/gitlab-com/runbooks)

