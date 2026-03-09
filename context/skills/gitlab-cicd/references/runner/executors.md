---
name: runner-executors
description: Docker, Kubernetes, shell executor configuration, comparison table, and security implications
---

# Runner Executors

> **Scope:** Docker, Kubernetes, shell executor configuration, comparison table, and security implications
> **GitLab version:** 9.0+
> **Source cards:** RN-2
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need to choose an executor for a new runner deployment
- You're configuring Docker or Kubernetes executor parameters in `config.toml`
- You need to understand security implications of each executor type
- You're evaluating privileged mode requirements for container builds

**Do NOT use when:**
- You need autoscaling configuration — see [autoscaling.md](autoscaling.md)
- You need security hardening details — see [security.md](security.md)

## Key Concepts

### Executor Comparison

| Executor | Required Config | Where Jobs Run | Risk Level |
|---|---|---|---|
| `shell` | (none) | Local shell — default executor | HIGH — no isolation |
| `docker` | `[runners.docker]` + Docker Engine | Docker container | MODERATE (non-priv) / CRITICAL (priv) |
| `docker-windows` | `[runners.docker]` + Docker Engine | Windows Docker container | MODERATE |
| `ssh` | `[runners.ssh]` | SSH remotely | HIGH — MITM risk |
| `parallels` | `[runners.parallels]` + `[runners.ssh]` | Parallels VM via SSH | LOW — full VM isolation |
| `virtualbox` | `[runners.virtualbox]` + `[runners.ssh]` | VirtualBox VM via SSH | LOW |
| `docker+machine` | `[runners.docker]` + `[runners.machine]` | Auto-scaled Docker machines (legacy) | MODERATE |
| `kubernetes` | `[runners.kubernetes]` | Kubernetes pods | MODERATE |
| `docker-autoscaler` | `[runners.docker]` + `[runners.autoscaler]` | Autoscaled instances running containers | MODERATE |
| `instance` | `[runners.autoscaler]` | Autoscaled instances — shell on host | HIGH |

### Docker Executor Key Parameters

62 total params in `[runners.docker]`. Most important:

| Parameter | Default | Purpose |
|---|---|---|
| `image` | — | Default container image for jobs (e.g., `"ruby:3.3"`) |
| `privileged` | `false` | Run containers in privileged mode — **INSECURE** |
| `pull_policy` | `["always"]` | Image pull strategy: `never`, `if-not-present`, `always` |
| `allowed_images` | `[]` | Whitelist image globs from `.gitlab-ci.yml` |
| `allowed_services` | `[]` | Whitelist service image globs |
| `volumes` | `[]` | Additional volumes to mount (`-v` flag syntax) |
| `memory` | — | Container memory limit (e.g., `"2g"`) |
| `cpus` | — | CPU count (Docker 1.13+) |
| `cap_add` / `cap_drop` | `[]` | Add/drop Linux capabilities |
| `helper_image` | — | Override default helper image for cloning/artifacts |
| `helper_image_flavor` | `alpine` | Helper OS: `alpine`, `ubi-fips`, `ubuntu` |
| `wait_for_services_timeout` | `30` | Seconds to wait for services; `-1` to disable |
| `network_mode` | — | Add container to custom Docker network |
| `shm_size` | `0` | Shared memory in bytes |

### Kubernetes Executor Key Parameters

| Parameter | Type | Purpose |
|---|---|---|
| `namespace` | string | Namespace for job pods |
| `image` | string | Default container image |
| `privileged` | boolean | Run all containers privileged |
| `node_selector` | table | Key=value pairs to constrain pod scheduling |
| `image_pull_secrets` | array | K8s docker-registry secrets for private registries |
| `service_account` | string | Service account for job pods |
| `allowed_images` | array | Whitelist — same as Docker executor |
| `logs_base_dir` | string | Base dir for build logs (17.2+) |

### Supported Shells

| Shell | Description |
|---|---|
| `bash` | Default for Unix systems |
| `sh` | Fallback for bash on Unix |
| `powershell` | PowerShell Desktop context (Windows) |
| `pwsh` | PowerShell Core — default for Windows |

## Examples

### Docker Executor with Security Hardening

```toml
# config.toml
[[runners]]
  executor = "docker"
  [runners.docker]
    image = "alpine:3.21"
    privileged = false
    pull_policy = ["always"]
    allowed_images = ["ruby:*", "python:*", "node:*", "alpine:*"]
    allowed_services = ["postgres:*", "redis:*", "mysql:*"]
    cap_drop = ["ALL"]
    cap_add = ["NET_BIND_SERVICE"]
    memory = "2g"
    cpus = "2"
    disable_cache = false
```

### Kubernetes Executor with Node Selection

```toml
# config.toml
[[runners]]
  executor = "kubernetes"
  [runners.kubernetes]
    namespace = "gitlab-ci"
    image = "alpine:3.21"
    service_account = "gitlab-runner"
    privileged = false
    [runners.kubernetes.node_selector]
      "node-role" = "ci"
      "gpu" = "true"
    [[runners.kubernetes.image_pull_secrets]]
      name = "registry-creds"
```

### Custom Executor with Lifecycle Hooks

```toml
# config.toml — custom executor
[[runners]]
  executor = "custom"
  [runners.custom]
    config_exec = "/opt/runner/config.sh"
    prepare_exec = "/opt/runner/prepare.sh"
    run_exec = "/opt/runner/run.sh"
    cleanup_exec = "/opt/runner/cleanup.sh"
    cleanup_exec_timeout = 600
    graceful_kill_timeout = 300
```

## Common Patterns

- **Docker with `pull_policy: if-not-present`** for speed on dedicated runners (NOT shared)
- **K8s with `node_selector`** for GPU/specialized workloads
- **`allowed_images` whitelist** for security control on shared runners
- **`helper_image` mirroring** for air-gapped environments
- **`cap_drop: ["ALL"]` + selective `cap_add`** for least-privilege containers

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `privileged: true` without understanding implications | Full root on host VM; container breakout possible | Use ephemeral VMs with `max_use_count=1`; consider kaniko |
| `if-not-present` pull on shared runners | Cache poisoning — cached image served without re-auth | Use `pull_policy: always` on shared runners |
| No resource limits configured | OOM kills, noisy neighbor problems | Set `memory` and `cpus` limits |
| Shell executor in shared environments | No isolation — jobs run as runner user, full host access | Use Docker or K8s executor with container isolation |
| Not configuring `allowed_images` on shared runners | Users can run arbitrary images including malicious ones | Whitelist trusted image patterns |

## Practitioner Pain Points

1. **Docker-in-Docker requires privileged mode** — DinD needs host Docker socket or kernel capabilities. **Workaround:** Use `docker-autoscaler` with ephemeral VMs and `max_use_count=1`, or use kaniko for rootless image builds.

2. **K8s executor pod startup adds 10-30s latency** — Pod creation, image pull, and init containers all add overhead. **Workaround:** Pre-pull images with DaemonSet; use `node_selector` for warm node pools.

3. **`helper_image` version must match runner version** — Protocol contract between runner and helper; mismatch causes artifact upload failures. **Fix:** Pin `helper_image` to the same version as runner; mirror for air-gapped environments.

4. **`if-not-present` pull policy enables cache poisoning** — Cached image from user A served to user B without re-authentication. **Fix:** Always use `pull_policy: always` on shared/instance runners.

## Version Notes

| Version | Change |
|---|---|
| 15.11 | `delete_instances_on_shutdown` added to docker-autoscaler |
| 16.11 | `instance_ready_command` and `update_interval` for autoscaler |
| 17.2 | `logs_base_dir`, `scripts_base_dir` added to K8s executor |
| 17.5 | S3 DualStack, Accelerate, PathStyle options for cache |
| 18.1 | `instance_acquire_timeout`, `log_internal_ip`, `log_external_ip` for autoscaler |
| 18.4 | `deletion_retry_interval`, `shutdown_deletion_interval`, `failure_threshold` |

## Decision Guide

| Scenario | Recommendation | Key Config |
|---|---|---|
| Standard CI/CD with container isolation | Docker executor with `pull_policy: always`, `allowed_images` | `[runners.docker]` |
| Kubernetes-native workloads | K8s executor with namespace, service_account, node_selector | `[runners.kubernetes]` |
| Auto-scaled cloud fleet (new deployments) | `docker-autoscaler` with fleeting plugin | `[runners.autoscaler]` |
| Legacy auto-scaling | `docker+machine` — migrate to `docker-autoscaler` | `[runners.machine]` |
| High-security workloads | Parallels/VirtualBox for full VM isolation | `[runners.parallels]` |

## Related Topics

- [autoscaling.md](autoscaling.md) — `docker-autoscaler` and `docker+machine` scaling configuration
- [security.md](security.md) — Hardening config for each executor type
- [fleet-management.md](fleet-management.md) — Multi-runner config and monitoring
- [../variables/masking-protection.md](../variables/masking-protection.md) — Variable security on shared runners

## Sources

- [GitLab Runner Advanced Configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- [GitLab Runner Security](https://docs.gitlab.com/runner/security/)
- [GitLab Runner Executors](https://docs.gitlab.com/runner/executors/)

