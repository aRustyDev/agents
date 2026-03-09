---
name: caching
description: cache:key:files, fallback_keys, distributed cache backends (S3/GCS), and cache policies
---

# Caching

> **Scope:** cache:key:files, fallback_keys, distributed cache backends (S3/GCS), and cache policies
> **GitLab version:** 9.0+
> **Source cards:** JB-2
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Speeding up builds by caching dependencies (npm, pip, bundler, etc.)
- Configuring content-based cache keys with lockfiles
- Setting up distributed caching with S3/GCS for shared runners
- Optimizing cache policy for push-only vs. pull-only jobs

## Key Concepts

### Cache vs Artifacts

| Feature | Cache | Artifacts |
|---|---|---|
| **Purpose** | Speed optimization (dependencies) | Build outputs between stages/pipelines |
| **Reliability** | Best-effort (may be absent) | Guaranteed (uploaded to GitLab) |
| **Scope** | Per-runner (local) or distributed (S3/GCS) | Per-pipeline, per-project |
| **Use for** | `node_modules/`, `.pip-cache/`, `.gradle/` | `dist/`, `build/`, test reports |
| **Max per job** | 4 caches | No limit |

### Cache Key Strategies

| Strategy | Keyword | When to Use |
|---|---|---|
| **Fixed key** | `cache:key: "my-key"` | Stable dependencies, infrequent changes |
| **Branch-based** | `cache:key: $CI_COMMIT_REF_SLUG` | Per-branch isolation |
| **Lockfile-based** | `cache:key:files: [package-lock.json]` | Content-addressed, invalidate on change |
| **Prefix + files** | `cache:key:prefix: $CI_JOB_NAME` | Combine job identity with content hash |

### Fallback Keys

```yaml
cache:
  key:
    files: [package-lock.json]
  fallback_keys:
    - $CI_DEFAULT_BRANCH-npm
    - global-npm
  paths:
    - node_modules/
```

Up to **5 fallback keys** per cache definition + global `CACHE_FALLBACK_KEY` variable.

### Cache Policy

| Policy | Behavior | Use When |
|---|---|---|
| `pull-push` (default) | Download + upload | Jobs that install dependencies |
| `pull` | Download only, no upload | Jobs that only consume cache |
| `push` | Upload only, no download | Cache warming jobs |

### Distributed Caching

Required for **shared runner environments** where jobs run on different machines:

| Backend | Configuration |
|---|---|
| S3 / MinIO | `[runners.cache.s3]` in `config.toml` |
| GCS | `[runners.cache.gcs]` in `config.toml` |
| Azure Blob | `[runners.cache.azure]` in `config.toml` |

> **Gotcha:** Distributed cache requires runner-level configuration — it's not a YAML-only setting.

### Branch Isolation

Cache is separated between protected and non-protected branches **by design**. A job on a feature branch **cannot** use cache from `main` (protected) unless `CACHE_FALLBACK_KEY` is set.

### Compression

`CACHE_COMPRESSION_FORMAT`: `zip` (default) or `tarzstd` (faster for large caches).

## Examples

### Lockfile-Based NPM Cache

```yaml
install:
  stage: build
  cache:
    key:
      files: [package-lock.json]
    paths:
      - node_modules/
    policy: pull-push
  script:
    - npm ci
```

### Split Push/Pull Pattern

```yaml
warm-cache:
  stage: .pre
  cache:
    key: $CI_DEFAULT_BRANCH-deps
    paths: [node_modules/]
    policy: push
  script: npm ci
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  cache:
    key: $CI_DEFAULT_BRANCH-deps
    paths: [node_modules/]
    policy: pull
  script: npm test
```

### Multiple Caches Per Job

```yaml
build:
  cache:
    - key:
        files: [package-lock.json]
      paths: [node_modules/]
    - key:
        files: [Gemfile.lock]
      paths: [vendor/ruby/]
  script:
    - npm ci && bundle install
```

## Common Patterns

- **`cache:key:files`** with lockfile for automatic invalidation on dependency changes
- **Fallback key chain** for partial cache hits when lockfile changes
- **`cache:policy: pull`** in consumer-only jobs to avoid wasteful re-uploads
- **Distributed cache (S3)** for shared runner environments
- **Separate warm-cache job** in `.pre` stage for cache population

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Caching build outputs | Build outputs need guaranteed delivery | Use `artifacts:` for build outputs |
| No fallback keys | Complete cache miss on lockfile change | Add `fallback_keys:` chain |
| `pull-push` in consumer jobs | Wasteful re-upload | Use `policy: pull` |
| More than 4 caches per job | GitLab enforces limit | Consolidate paths |
| Expecting shared cache without S3 | Local cache is per-runner | Configure distributed backend |

## Practitioner Pain Points

1. **Cache not shared across protected/unprotected branches** — by design. Use `CACHE_FALLBACK_KEY` for cross-branch fallback.
2. **"Cache not working" is the #1 SO question** — usually scope/path misconfiguration. Verify with `CI_DEBUG_TRACE`.
3. **Distributed cache requires runner config, not YAML** — `[runners.cache.s3]` in `config.toml`, not in `.gitlab-ci.yml`.
4. **Cache invalidation timing is unpredictable** — on shared runners, cache availability depends on which runner picks the job.
<!-- TODO: Expand with deeper research on MinIO setup and Kubernetes runner cache issues -->

## Related Topics

- [artifacts.md](artifacts.md) — Artifacts for guaranteed inter-stage data
- [../pipelines/optimization.md](../pipelines/optimization.md) — Overall pipeline optimization
- [../runner/fleet-management.md](../runner/fleet-management.md) — Runner cache backend config

## Sources

- [Caching in GitLab CI/CD](https://docs.gitlab.com/ci/caching/)
- [Cache key configuration](https://docs.gitlab.com/ci/caching/#cache-key)

