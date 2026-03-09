---
name: runner-architecture
description: Runner manager model, 10 executor types, version compatibility, and deployment models
---

# Runner Architecture

> **Scope:** Runner manager model, 10 executor types, version compatibility, and deployment models
> **GitLab version:** 9.0+
> **Source cards:** RN-1
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult when designing runner infrastructure, choosing executor types,
or understanding how GitLab Runner processes and routes jobs.

## Key Concepts

### Runner Manager Model

```
GitLab Server
    │
    ├── Runner Manager (config.toml)
    │       ├── [[runners]] section 1 (Docker executor)
    │       ├── [[runners]] section 2 (Kubernetes executor)
    │       └── [[runners]] section 3 (Shell executor)
    │
    └── Job Queue
            ├── Tag-matched routing
            └── Runner picks up jobs
```

- Runner Manager is a single process defined by `config.toml`
- Each `[[runners]]` section defines one registered runner with its executor
- Jobs are routed to runners by **tag matching** — job tags must be a subset of runner tags
- Global `concurrent` setting limits total simultaneous jobs across all `[[runners]]`

### Deployment Models

| Model | Description | Managed By |
|-------|-------------|------------|
| **GitLab-hosted** (SaaS) | GitLab-managed runners on Linux/Windows/macOS | GitLab |
| **Self-managed** | Your infrastructure, your config.toml | You |
| **Hybrid** | GitLab-hosted for general + self-managed for specialized | Mixed |

### Executor Types

| Executor | Isolation | Use Case | Complexity |
|----------|-----------|----------|------------|
| **shell** | None | Simple scripts, legacy | Low |
| **docker** | Container | Standard CI/CD | Low |
| **docker+machine** | Container + auto-provisioned VM | Legacy autoscaling | High |
| **docker-autoscaler** | Container + cloud VM | Modern autoscaling (replacement) | High |
| **kubernetes** | Pod | Cloud-native CI | Medium |
| **instance** | Full VM | Security-sensitive workloads | High |
| **ssh** | Remote machine | Legacy systems | Low |
| **parallels** | macOS VM | macOS/iOS builds | Medium |
| **virtualbox** | Local VM | Local development | Medium |
| **custom** | User-defined | Exotic environments | High |

### Registration & Authentication

- **Runner authentication tokens** (15.10+) — replaces legacy registration tokens
- Created in GitLab UI (project/group/instance level)
- Token stored in `config.toml` under `[[runners]]`
- Runner version should match GitLab major.minor for full compatibility

<!-- TODO: Expand with config.toml structure and registration flow -->

## Examples

```toml
# config.toml — basic Docker executor
concurrent = 4
check_interval = 3

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.example.com"
  token = "RUNNER_AUTH_TOKEN"
  executor = "docker"
  [runners.docker]
    image = "alpine:latest"
    privileged = false
    volumes = ["/cache"]
```

```yaml
# Job tag routing
build:
  tags:
    - docker
    - linux
  script: make build

ios_build:
  tags:
    - macos
    - xcode15
  script: xcodebuild
```

## Common Patterns

- **Docker executor for standard CI/CD** — isolated, reproducible, well-supported
- **Kubernetes executor for cloud-native** — auto-provisions pods per job
- **Tag-based job routing** — specialized runners for GPU, macOS, privileged workloads
- **Runner version sync** — keep runner version aligned with GitLab server major.minor
- **Multiple `[[runners]]` per manager** — different executors on the same host

## Anti-Patterns

- **Shell executor for production CI** — no isolation, leftover state, security risk
- **Outdated runner versions** — new GitLab features require matching runner support
- **No tag routing** — all jobs land on any runner regardless of capability
- **Single runner for all workloads** — no isolation between build types; specialized runners are safer

## Related Topics

- [executors.md](executors.md) — deep dive on executor configuration
- [autoscaling.md](autoscaling.md) — docker-autoscaler and scaling policies
- [security.md](security.md) — runner security hardening
- [fleet-management.md](fleet-management.md) — config.toml, Prometheus metrics
- [performance.md](performance.md) — concurrent, check_interval tuning

## Sources

- [GitLab Runner docs](https://docs.gitlab.com/runner/)
- [CI/CD Runners](https://docs.gitlab.com/ci/runners/)
- Context card: RN-1

