---
name: runner-security
description: Runner tokens, allowed_images, debug_trace_disabled, privileged mode risks, and hardening
---

# Runner Security

> **Scope:** Runner tokens, allowed_images, debug_trace_disabled, privileged mode risks, and hardening
> **GitLab version:** 9.0+
> **Source cards:** RN-4
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You're hardening a runner for shared or production use
- You need to understand security risks of each executor type
- You're configuring image whitelists, pull policies, or debug restrictions
- You need to manage runner tokens (registration tokens are deprecated)
- You're evaluating Git strategy risks on shared runners

**Do NOT use when:**
- You need executor configuration details — see [executors.md](executors.md)
- You need autoscaling setup — see [autoscaling.md](autoscaling.md)

## Key Concepts

### Security Risk by Executor

| Executor | Risk | Detail | Mitigation |
|---|---|---|---|
| Shell | **HIGH** | Jobs run as runner user; full host access; can steal code | Use only for trusted builds on dedicated hosts |
| Docker (non-priv) | MODERATE | Container isolation; safer with non-root, dropped caps | Use `cap_drop`/`cap_add` for granular permissions |
| Docker (privileged) | **CRITICAL** | Full root on host VM; mount volumes; container breakout | Ephemeral VMs only; `max_use_count=1`; restrict to protected branches |
| SSH | **HIGH** | Susceptible to MITM (no StrictHostKeyChecking) | Avoid for untrusted workloads |
| Parallels | LOW | Full system virtualization; isolated mode blocks peripherals | Safest option for high-security workloads |
| Kubernetes | MODERATE | Pod-level isolation; privileged pods have Docker-priv risks | Use RBAC, network policies, PSP/PSA |

### config.toml Security Parameters

| Parameter | Section | Purpose |
|---|---|---|
| `debug_trace_disabled` | `[[runners]]` | Prevents `CI_DEBUG_TRACE` from exposing secrets even when set to `true` |
| `allowed_images` | `[runners.docker]` / `[runners.kubernetes]` | Whitelist of image globs that `.gitlab-ci.yml` can specify |
| `allowed_privileged_images` | `[runners.docker]` | Subset of `allowed_images` that can run privileged |
| `allowed_services` | `[runners.docker]` / `[runners.kubernetes]` | Whitelist of service image globs |
| `allowed_pull_policies` | `[runners.docker]` | Restricts which pull policies `.gitlab-ci.yml` can request |
| `pull_policy` | `[runners.docker]` | Use `always` on shared runners to prevent cache poisoning |
| `clean_git_config` | `[[runners]]` | Cleans Git config between jobs — prevents credential leakage |
| `output_limit` | `[[runners]]` | Limit build log size (default: 4096 KB) to prevent log-based DoS |

### Pull Policy Security

| Policy | Security | Use Case |
|---|---|---|
| `always` | **SAFE** — always re-pulls and re-authenticates | Shared/instance runners with untrusted users |
| `if-not-present` | **RISKY** — cached images served without re-auth | Dedicated runners for trusted teams only |
| `never` | RESTRICTED — only pre-downloaded images | Locked-down environments with pre-approved image set |

> **Cache poisoning attack:** With `if-not-present`, User A pulls a private image → it's cached
> on the host → User B (no access) gets the cached copy without authentication.

### Git Strategy Risks

- `GIT_STRATEGY: fetch` reuses local working copy — previous job's code may persist
- Users can inject code that executes in other users' pipelines
- Submodule contents accessible via `git reflog` even after cleanup
- **Recommendation:** Use `GIT_STRATEGY: clone` on shared runners

### Network Segmentation

- Configure runner VMs in their own network segment
- Block SSH access from Internet to runner VMs
- Restrict traffic between runner VMs (prevent lateral movement)
- Filter access to cloud metadata endpoints (`169.254.169.254`)

## Examples

### Hardened Shared Runner

```toml
# config.toml — production shared runner
[[runners]]
  name = "shared-secure"
  executor = "docker"
  environment = ["FF_ENABLE_JOB_CLEANUP=true"]
  debug_trace_disabled = true
  output_limit = 4096
  clean_git_config = true
  [runners.docker]
    image = "alpine:3.21"
    privileged = false
    pull_policy = ["always"]
    allowed_images = ["alpine:*", "ruby:*", "python:*", "node:*"]
    allowed_services = ["postgres:*", "redis:*", "mysql:*"]
    cap_drop = ["ALL"]
    cap_add = ["NET_BIND_SERVICE"]
```

### Isolated Privileged Runner for DinD

```toml
# config.toml — restricted privileged runner
[[runners]]
  name = "dind-builder"
  executor = "docker-autoscaler"
  limit = 10
  [runners.docker]
    image = "docker:27"
    privileged = true
    allowed_privileged_images = ["docker:*"]
    pull_policy = ["always"]
  [runners.autoscaler]
    max_use_count = 1          # Ephemeral — destroy after 1 job
    delete_instances_on_shutdown = true
```

### Token/URL via Environment Variables (K8s Secret)

```toml
# config.toml — secrets managed externally
[[runners]]
  url = "${GITLAB_URL}"        # From K8s secret / env
  token = "${RUNNER_TOKEN}"    # From K8s secret / env
  executor = "kubernetes"
  [runners.kubernetes]
    namespace = "ci-jobs"
```

## Common Patterns

- **Protected runner + protected branch** for production deployments
- **`allowed_images` whitelist** to prevent arbitrary image execution
- **`debug_trace_disabled: true`** on all production runners
- **Token/URL via environment variables** for K8s secret mounting
- **`FF_ENABLE_JOB_CLEANUP=true`** on non-ephemeral runners for defense in depth
- **`pull_policy: always`** on any runner serving untrusted users

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Shared runners with `privileged: true` | Any user can escape container to host | Use ephemeral VMs with `max_use_count=1` |
| Not using protected runners for production secrets | Unprotected branches can access deployment credentials | Enable protected runner flag; pair with protected branches |
| Allowing arbitrary images on shared runners | Malicious images can exfiltrate data or attack infrastructure | Configure `allowed_images` whitelist |
| Storing runner tokens in version-controlled config | Tokens exposed to all contributors | Use env vars or K8s secrets for `token` and `url` |
| `GIT_STRATEGY: fetch` on shared runners | Code from previous jobs persists; data leakage risk | Use `clone` strategy; enable `FF_ENABLE_JOB_CLEANUP` |

## Practitioner Pain Points

1. **Registration token to runner token migration** — Every runner must be re-registered; automation scripts break. **Workaround:** Use runner authentication token API; plan batch migration during maintenance window. Registration tokens fully removed in 17.0.

2. **Privileged mode required for legitimate use cases** — DinD and buildah need container runtime access. **Workaround:** Use `docker-autoscaler` with `max_use_count=1` on isolated VMs; or kaniko/buildah rootless.

3. **Balancing security restrictions with developer productivity** — Strict `allowed_images` blocks legitimate images; `pull_policy: always` adds latency. **Workaround:** Use wildcard patterns (`org/*:*`); use a Docker registry proxy for caching.

4. **`GIT_STRATEGY: fetch` leaks data between jobs** — Working directory reuse; git reflog retains submodule contents. **Fix:** Use `clone` on shared runners; enable `FF_ENABLE_JOB_CLEANUP`.

## Version Notes

| Version | Change |
|---|---|
| 15.6+ | Registration tokens deprecated; runner authentication tokens introduced |
| 16.0+ | `FF_ENABLE_JOB_CLEANUP` feature flag available |
| 17.0 | Registration token workflow fully removed |

## Decision Guide

| Scenario | Recommendation | Risk |
|---|---|---|
| Shared runner for untrusted projects | `pull_policy=always`, `allowed_images`, `debug_trace_disabled=true`, `privileged=false` | Must harden |
| Dedicated runner for trusted team | `pull_policy=if-not-present` OK; relax `allowed_images`; still disable debug trace | Medium trust |
| Production deployment runner | Protected runner + protected branch; env vars from K8s secrets; `output_limit` | High value target |
| Docker image build runner (needs priv) | `docker-autoscaler` with `max_use_count=1`; `allowed_privileged_images`; isolated network | Accept risk with mitigations |
| Runner with sensitive env variables | Protected runner; masked+hidden variables; `debug_trace_disabled=true` | Secret exposure risk |

## Related Topics

- [executors.md](executors.md) — Executor types and their inherent isolation levels
- [autoscaling.md](autoscaling.md) — Ephemeral instances with `max_use_count=1` for security
- [fleet-management.md](fleet-management.md) — Monitoring for security events
- [../variables/masking-protection.md](../variables/masking-protection.md) — Variable masking and protection
- [../security/secrets-management.md](../security/secrets-management.md) — External secrets for runner configuration

## Sources

- [GitLab Runner Security](https://docs.gitlab.com/runner/security/)
- [GitLab Runner Advanced Configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- [Runner Authentication Tokens](https://docs.gitlab.com/ci/runners/new_creation_workflow/)
