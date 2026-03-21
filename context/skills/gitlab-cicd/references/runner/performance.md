---
name: runner-performance
description: concurrent, request_concurrency, check_interval, output_limit, and tuning parameters
---

# Runner Performance

> **Scope:** concurrent, request_concurrency, check_interval, output_limit, and tuning parameters
> **GitLab version:** 9.0+
> **Source cards:** RN-5
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult when tuning runner throughput, diagnosing job queue bottlenecks,
or configuring distributed caching for shared runner environments.

## Key Concepts

### Global Performance Parameters

| Parameter | Default | Purpose | Impact |
|-----------|---------|---------|--------|
| `concurrent` | 1 | Max total simultaneous jobs across all runners | Primary throughput control |
| `check_interval` | 3 (sec) | How often runner polls for new jobs | Lower = faster pickup, more API calls |

### Per-Runner Parameters

| Parameter | Default | Purpose |
|-----------|---------|--------|
| `limit` | 0 (unlimited) | Max jobs for this specific runner |
| `request_concurrency` | 1 | Concurrent job request threads | 
| `output_limit` | 4096 (KB) | Max build log size before truncation |

### Key Tuning Rules

- **`concurrent` must be ≥ number of runners** — otherwise workers starve waiting for slots
- **`request_concurrency`** should be increased on high-volume runners to avoid polling bottleneck
- **`check_interval`** affects job pickup latency; 1–3s for interactive, 5–10s for batch
- **`output_limit`** truncates build logs silently — increase for verbose test output

### Distributed Cache Configuration

| Backend | Config Key | Use Case |
|---------|-----------|----------|
| S3 | `[runners.cache.s3]` | AWS or S3-compatible (MinIO) |
| GCS | `[runners.cache.gcs]` | Google Cloud Storage |
| Azure | `[runners.cache.azure]` | Azure Blob Storage |

### Monitoring

- Runner embeds a **Prometheus metrics server** (default port 9252)
- Key metrics: `gitlab_runner_jobs`, `gitlab_runner_concurrent`, `gitlab_runner_request_duration`
- Monitor for queue depth, job wait time, and runner capacity utilization

<!-- TODO: Expand with Prometheus query examples and alerting thresholds -->

## Examples

```toml
# config.toml — high-throughput runner
concurrent = 10
check_interval = 1
listen_address = ":9252"  # Prometheus metrics endpoint

[[runners]]
  name = "docker-high-perf"
  url = "https://gitlab.example.com"
  token = "TOKEN"
  executor = "docker"
  limit = 8
  request_concurrency = 3
  output_limit = 16384    # 16 MB logs
  [runners.docker]
    image = "alpine:latest"
    privileged = false
  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "ci-cache"
      BucketLocation = "us-east-1"
```

```toml
# Multi-runner with different capacities
concurrent = 20

[[runners]]
  name = "build-runner"
  limit = 12
  request_concurrency = 4
  executor = "docker"
  # ... config ...

[[runners]]
  name = "deploy-runner"
  limit = 4
  request_concurrency = 1
  executor = "docker"
  # ... config ...
```

## Common Patterns

- **`concurrent` > number of runners** to prevent worker starvation
- **Increase `request_concurrency`** on high-volume runners (3–5 for busy instances)
- **Distributed S3 cache** for shared runner environments — eliminates cache misses on different runners
- **Prometheus monitoring** via `listen_address` — track queue depth and execution time
- **Separate runner pools** — high `limit` for builds, low `limit` for deploys

## Anti-Patterns

- **`concurrent` < number of runners** — workers sit idle while the slot limit blocks them
- **`request_concurrency: 1` on high-volume runners** — single-threaded polling bottleneck
- **Default `output_limit`** with verbose test frameworks — logs silently truncated
- **Not monitoring runner metrics** — capacity problems go undetected until queue backlog
- **Very low `check_interval`** without need — increases API load on GitLab server

## Related Topics

- [architecture.md](architecture.md) — runner manager model and executor types
- [autoscaling.md](autoscaling.md) — dynamic runner provisioning
- [fleet-management.md](fleet-management.md) — config.toml structure and Prometheus metrics
- [../jobs/caching.md](../jobs/caching.md) — job-level cache configuration

## Sources

- [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- Context card: RN-5
