---
name: runner-autoscaling
description: docker-autoscaler, fleeting plugins, scaling policies, idle periods, and legacy migration
---

# Runner Autoscaling

> **Scope:** docker-autoscaler, fleeting plugins, scaling policies, idle periods, and legacy migration
> **GitLab version:** 15.1+
> **Source cards:** RN-3
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need auto-scaled runner infrastructure that grows/shrinks with demand
- You're configuring `docker-autoscaler` or `instance` executors with fleeting plugins
- You're migrating from legacy `docker+machine` to modern autoscaling
- You need time-based scaling policies (high capacity during work hours, low at night)

**Do NOT use when:**
- You need static runner configuration — see [executors.md](executors.md)
- You need security hardening — see [security.md](security.md)

## Key Concepts

### Modern Autoscaler Parameters (`[runners.autoscaler]`)

| Parameter | Default | Purpose |
|---|---|---|
| `plugin` | — | Fleeting plugin name (e.g., `fleeting-plugin-aws`, `fleeting-plugin-googlecompute`) |
| `capacity_per_instance` | `1` | Jobs that can run concurrently on a single instance |
| `max_use_count` | `0` | Max times instance is reused before removal (0=unlimited; `1`=ephemeral) |
| `max_instances` | `0` | Hard cap on total instances (pending+running+deleting); 0=unlimited |
| `delete_instances_on_shutdown` | `false` | Delete all instances when runner shuts down (15.11+) |
| `instance_ready_command` | — | Command run on provisioned instance to verify readiness (16.11+) |
| `instance_acquire_timeout` | `15m` | Max wait to acquire an instance (18.1+) |
| `update_interval` | `1m` | Plugin instance state refresh interval (16.11+) |
| `failure_threshold` | `3` | Consecutive health failures before instance replaced (18.4+) |

### Scaling Policies (`[[runners.autoscaler.policy]]`)

Multiple policy sections enable time-based scaling. Each has:

| Parameter | Default | Purpose |
|---|---|---|
| `periods` | `["* * * * *"]` | Cron strings for when this policy is active |
| `timezone` | system local | Timezone for cron evaluation |
| `idle_count` | — | Target idle instances ready for immediate job pickup |
| `idle_time` | — | Duration an instance can be idle before termination |
| `scale_factor` | `0.0` | Additional idle capacity as fraction of in-use count |
| `scale_factor_limit` | — | Cap on `scale_factor` result (**always set this!**) |
| `preemptive_mode` | — | Request jobs only when instance confirmed available (17.7+) |

### Scale Throttle (`[runners.autoscaler.scale_throttle]`)

| Parameter | Purpose |
|---|---|
| `limit` | Rate limit of new instances per second |
| `burst` | Burst capacity above the limit (burst ≥ limit) |

### Legacy docker+machine (`[runners.machine]`)

> **Migration note:** `docker+machine` still works but is the deprecated direction.
> New deployments should use `docker-autoscaler` with fleeting plugins.

| Parameter | Purpose |
|---|---|
| `IdleCount` | Machines waiting in idle state |
| `IdleScaleFactor` | Idle as factor of in-use (like `scale_factor`) |
| `IdleCountMin` | Min idle machines when using `IdleScaleFactor` (default: 1) |
| `IdleTime` | Seconds before idle machine is removed |
| `MaxGrowthRate` | Max machines added in parallel; 0=unlimited |
| `MaxBuilds` | Job count before machine is destroyed (ephemeral security) |
| `MachineName` | Template with `%s` for unique ID |
| `MachineDriver` | Docker Machine provider (aws, gcp, azure, etc.) |

### Concurrency Model

| Setting | Scope | Purpose |
|---|---|---|
| `concurrent` | Global | Max jobs across ALL `[[runners]]` combined |
| `limit` | Per-runner | Max jobs for this specific runner (0=unlimited) |
| `request_concurrency` | Per-runner | Concurrent requests to GitLab for new jobs (default: 1) |

## Examples

### docker-autoscaler with Time-Based Policies

```toml
# config.toml — modern autoscaling
concurrent = 50
[[runners]]
  executor = "docker-autoscaler"
  limit = 50
  [runners.docker]
    image = "alpine:3.21"
  [runners.autoscaler]
    plugin = "fleeting-plugin-aws"
    capacity_per_instance = 1
    max_use_count = 1          # Ephemeral for security
    max_instances = 50
    delete_instances_on_shutdown = true
    [runners.autoscaler.plugin_config]
      name = "ci-runner"
      region = "us-east-1"
    [runners.autoscaler.scale_throttle]
      limit = 5
      burst = 10
    # Business hours: high idle capacity
    [[runners.autoscaler.policy]]
      periods = ["* 8-18 * * mon-fri *"]
      timezone = "America/New_York"
      idle_count = 10
      idle_time = "30m"
      scale_factor = 0.5
      scale_factor_limit = 20
    # Off hours: minimal capacity
    [[runners.autoscaler.policy]]
      periods = ["* * * * * *"]
      idle_count = 2
      idle_time = "10m"
```

### Legacy docker+machine

```toml
# config.toml — legacy (migrate to docker-autoscaler)
concurrent = 20
[[runners]]
  executor = "docker+machine"
  limit = 20
  [runners.docker]
    image = "alpine:3.21"
  [runners.machine]
    IdleCount = 5
    IdleTime = 600
    MaxBuilds = 1              # Ephemeral
    MaxGrowthRate = 3
    MachineName = "runner-%s"
    MachineDriver = "amazonec2"
    MachineOptions = [
      "amazonec2-region=us-east-1",
      "amazonec2-instance-type=m5.large",
      "amazonec2-spot-instance=true"
    ]
```

### Multi-Runner Concurrency Tuning

```toml
# config.toml — multiple runners on one manager
concurrent = 30              # Global cap
check_interval = 3
[[runners]]
  name = "docker-ci"
  executor = "docker"
  limit = 10                 # Max 10 jobs
  request_concurrency = 3
[[runners]]
  name = "k8s-ci"
  executor = "kubernetes"
  limit = 20                 # Max 20 jobs
  request_concurrency = 5
```

## Common Patterns

- **`docker-autoscaler` for all new deployments** — replaces `docker+machine`
- **Time-based policies:** high `idle_count` during work hours, low idle nights/weekends
- **`scale_factor` for proportional scaling** — idle instances scale with demand
- **`max_use_count=1`** for ephemeral security — destroy instance after 1 job
- **`delete_instances_on_shutdown=true`** to prevent orphaned cloud instances
- **Start with 2+ runner managers** for high availability in autoscaling mode

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using `docker+machine` for new deployments | Deprecated direction; fewer updates | Migrate to `docker-autoscaler` with fleeting plugin |
| No `idle_time` setting | Instances never cleaned up — cost spirals | Always set `idle_time` for all policies |
| `scale_factor` without `scale_factor_limit` | Unbounded growth — 0.5 × 100 running = 50 idle | Always set `scale_factor_limit` |
| Not configuring `delete_instances_on_shutdown` | Orphaned instances on runner restart | Set to `true` for ephemeral fleets |
| Runner manager executing CI jobs | Manager resource contention | Manager should NOT run jobs in autoscaling mode |

## Practitioner Pain Points

1. **docker+machine → docker-autoscaler migration** — Different config structure; fleeting plugins replace `MachineDriver`/`MachineOptions`. **Workaround:** Run both in parallel during migration; feature parity exists for most cloud providers.

2. **Autoscaler config changes require runner restart** — Unlike `[[runners]]` section, autoscaler config is NOT hot-reloaded every 3s. **Workaround:** Use SIGHUP for graceful restart; plan changes during low-traffic periods.

3. **Instance provisioning latency adds 30-120s** — VM boot + OS init + `instance_ready_command` execution time. **Workaround:** Maintain `idle_count > 0`; use `preemptive_mode`; pre-bake AMIs/images.

4. **`scale_factor` without `scale_factor_limit` causes cost spirals** — `scale_factor=0.5` with 100 running instances = 50 idle instances. **Fix:** Always set `scale_factor_limit`; monitor `gitlab_runner_autoscaling_machine_states`.

## Version Notes

| Version | Change |
|---|---|
| 15.11 | `delete_instances_on_shutdown` for docker-autoscaler |
| 16.11 | `instance_ready_command` and `update_interval` |
| 17.7 | `preemptive_mode` for autoscaler policies |
| 18.1 | `instance_acquire_timeout`, `log_internal_ip`, `log_external_ip` |
| 18.4 | `deletion_retry_interval`, `shutdown_deletion_interval`, `failure_threshold` |

## Decision Guide

| Scenario | Recommendation | Key Config |
|---|---|---|
| New cloud-based autoscaling | `docker-autoscaler` with fleeting plugin for your cloud | `[runners.autoscaler]` with `[[runners.autoscaler.policy]]` |
| Existing `docker+machine` fleet | Plan migration to `docker-autoscaler` | `[runners.machine]` → `[runners.autoscaler]` |
| Time-of-day cost optimization | Multiple `[[runners.autoscaler.policy]]` with cron periods | `idle_count` + `idle_time` per period |
| High-security ephemeral instances | `max_use_count=1` + `delete_instances_on_shutdown=true` | `[runners.autoscaler]` |
| Fast job start times | `preemptive_mode` + adequate `idle_count` | `[[runners.autoscaler.policy]]` |

## Related Topics

- [executors.md](executors.md) — Executor types that autoscaling applies to
- [security.md](security.md) — Security considerations for ephemeral instances
- [fleet-management.md](fleet-management.md) — Prometheus metrics for monitoring autoscaler performance
- [../pipelines/optimization.md](../pipelines/optimization.md) — Pipeline-level optimizations that reduce runner demand

## Sources

- [GitLab Runner Advanced Configuration — Autoscaler](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- [GitLab Runner Fleet Scaling](https://docs.gitlab.com/runner/fleet_scaling/)
- [Fleeting Plugins](https://gitlab.com/gitlab-org/fleeting/)

