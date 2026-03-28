---
name: git-strategies
description: GIT_STRATEGY, GIT_DEPTH, GIT_SUBMODULE_STRATEGY, clean flags, and fetch configuration
---

# Git Strategies

> **Scope:** GIT_STRATEGY, GIT_DEPTH, GIT_SUBMODULE_STRATEGY, clean flags, and fetch configuration
> **GitLab version:** 9.0+
> **Source cards:** NEW-20
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need to optimize clone performance for large repositories
- You're configuring submodule handling in CI
- You need full Git history for semantic-release, changelogs, or `git describe`
- You want to skip cloning entirely for artifact-only jobs
- You need custom checkout workflows (merge base testing)

**Do NOT use when:**
- Default clone behavior works fine for your project (no performance issues)

## Key Concepts

### GIT_STRATEGY

| Value | Behavior | Use Case |
|---|---|---|
| `clone` | Clones from scratch every job. Slowest but pristine. | Default; guaranteed clean state |
| `fetch` | Re-uses existing worktree. `git clean` + `git fetch` + `git checkout`. | Large repos with persistent runners |
| `none` | Skips all Git operations. Working dir may have previous job files. | Jobs using only artifacts |

### GIT_DEPTH

Controls shallow clone depth. Significantly speeds up cloning for repos with large history.

| Context | Default |
|---|---|
| New projects | `20` (automatically set) |
| GitLab.com | `20` |
| Self-managed (no setting) | Full clone (no depth limit) |

> **Gotcha:** `GIT_DEPTH: 1` with queued jobs or retries may fail — the target commit may not be in
> the shallow range. Use `GIT_DEPTH: 20` or higher for safety. `GIT_DEPTH: 0` = full clone.

### Submodule Variables

| Variable | Purpose |
|---|---|
| `GIT_SUBMODULE_STRATEGY` | `none` (default), `normal`, `recursive` |
| `GIT_SUBMODULE_DEPTH` | Depth for submodule clones (overrides `GIT_DEPTH` for submodules) |
| `GIT_SUBMODULE_PATHS` | Space-separated paths; use `:(exclude)path` to skip specific submodules |
| `GIT_SUBMODULE_FORCE_HTTPS` | Rewrites SSH submodule URLs to HTTPS; uses `CI_JOB_TOKEN` for auth |
| `GIT_SUBMODULE_UPDATE_FLAGS` | Extra flags for `git submodule update` |

### Other Git Variables

| Variable | Default | Purpose |
|---|---|---|
| `GIT_CHECKOUT` | `true` | Set `false` to skip checkout (custom checkout in script) |
| `GIT_CLEAN_FLAGS` | `-ffdx` | Controls `git clean` behavior; e.g., `-ffdx -e node_modules/` |
| `GIT_FETCH_EXTRA_FLAGS` | — | Appended after default fetch flags (e.g., `--prune`) |
| `GIT_CLONE_EXTRA_FLAGS` | — | Extra args for native `git clone` (requires `FF_USE_GIT_NATIVE_CLONE`) |

### Advanced Features

| Feature | Type | Purpose |
|---|---|---|
| `pre_get_sources_script` | Runner `config.toml` | Run script before Git operations (LFS, auth setup) |
| `clean_git_config` | Runner `config.toml` | Remove Git config after job (ephemeral state) |
| `FF_USE_GIT_NATIVE_CLONE` | Feature flag | Use native `git clone` instead of runner's built-in logic |

## Examples

### Fastest Clone for Simple Builds

```yaml
build:
  variables:
    GIT_STRATEGY: clone
    GIT_DEPTH: 1
  script:
    - make build
```

### Fetch Strategy with Preserved node_modules

```yaml
test:
  variables:
    GIT_STRATEGY: fetch
    GIT_DEPTH: 20
    GIT_CLEAN_FLAGS: -ffdx -e node_modules/
  script:
    - npm test
```

### Full History for Semantic-Release

```yaml
release:
  variables:
    GIT_STRATEGY: clone
    GIT_DEPTH: 0
  script:
    - npx semantic-release
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Selective Submodule Checkout

```yaml
build-with-submodules:
  variables:
    GIT_SUBMODULE_STRATEGY: recursive
    GIT_SUBMODULE_DEPTH: 1
    GIT_SUBMODULE_PATHS: ":(exclude)docs :(exclude)vendor/large-lib"
  script:
    - make build
```

### Custom Checkout Workflow (Merge Test)

```yaml
merged-test:
  variables:
    GIT_STRATEGY: clone
    GIT_CHECKOUT: "false"
  script:
    - git checkout -B master origin/master
    - git merge $CI_COMMIT_SHA
    - make test
```

### No-Clone Job Using Only Artifacts

```yaml
deploy:
  variables:
    GIT_STRATEGY: none
  dependencies:
    - build
  script:
    - ./deploy.sh dist/
```

## Common Patterns

- **`GIT_DEPTH: 1`** for fastest clone when history not needed (simple builds)
- **`GIT_STRATEGY: fetch`** for large repos with persistent/shell runners
- **`GIT_CLEAN_FLAGS: -ffdx -e cache/`** to preserve local cache directories
- **`GIT_SUBMODULE_FORCE_HTTPS: "true"`** for submodules on same GitLab instance without SSH keys
- **`GIT_SUBMODULE_PATHS` with `:(exclude)`** to skip unneeded submodules
- **`pre_get_sources_script`** for Git LFS or custom auth config

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `GIT_DEPTH: 0` when tags/history not needed | Full clone is slow for large repos | Use `GIT_DEPTH: 1` or `20` |
| `GIT_DEPTH: 1` with job retries or queued jobs | Commit may not be in shallow range — fetch fails | Use `GIT_DEPTH: 20` or higher |
| Shallow submodules when parent references older commits | `GIT_SUBMODULE_DEPTH` limits history; parent may reference outside range | Increase depth or set to `0` |
| `GIT_SUBMODULE_FORCE_HTTPS` with legacy `/ci` URL | Auth failures due to URL pattern mismatch | Update submodule URLs to current format |
| `GIT_STRATEGY: none` without realizing working dir is empty | Scripts expecting source code fail | Use `dependencies:` to get artifacts instead |
| Not setting `GIT_DEPTH` on self-managed (full clone default) | Unnecessary slow clones | Set `GIT_DEPTH: 20` project-wide |

## Practitioner Pain Points

1. **Shallow clone breaks semantic-release and linters** — `GIT_DEPTH` default of 20 is insufficient for tools needing full history. **Fix:** Set `GIT_DEPTH: 0` for release/changelog jobs.

2. **`GIT_DEPTH: 1` with job queue causes failures** — When jobs are queued, newer commits push the target commit outside the shallow range. **Fix:** Use `GIT_DEPTH: 20` or higher as a safety margin.

3. **Shallow submodules fail if parent references commit outside depth** — `GIT_SUBMODULE_DEPTH` limits history; parent may reference older commits. **Fix:** Increase depth or set to `0`.

4. **`GIT_SUBMODULE_FORCE_HTTPS` + legacy `/ci` URL causes auth errors** — Older submodule URLs with `/ci` suffix don't match the HTTPS rewrite pattern. **Fix:** Update submodule URLs to current GitLab format.

## Version Notes

| Version | Change |
|---|---|
| 1.10 | `GIT_SUBMODULE_STRATEGY` introduced |
| 14.10 | `GIT_SUBMODULE_PATHS` for selective sync |
| 15.7 | `GIT_SUBMODULE_DEPTH` variable added |
| 17.2 | `GIT_CLONE_EXTRA_FLAGS` with `FF_USE_GIT_NATIVE_CLONE` |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Large repo, fast builds, no history needed | `GIT_STRATEGY: clone`, `GIT_DEPTH: 1` |
| Large repo, persistent/shell runner | `GIT_STRATEGY: fetch`, `GIT_DEPTH: 20` |
| Need full git history (releases, changelogs) | `GIT_STRATEGY: clone`, `GIT_DEPTH: 0` |
| Job only uses artifacts, no source code | `GIT_STRATEGY: none` |
| Many submodules, only need some | `GIT_SUBMODULE_STRATEGY: recursive`, `GIT_SUBMODULE_PATHS: ":(exclude)unneeded"` |
| Submodules on same GitLab instance, no SSH | `GIT_SUBMODULE_FORCE_HTTPS: "true"` (uses `CI_JOB_TOKEN`) |

## Related Topics

- [../runner/executors.md](../runner/executors.md) — Executor type affects Git strategy performance
- [../runner/security.md](../runner/security.md) — `GIT_STRATEGY: fetch` risks on shared runners
- [../semantic-release/gitlab-integration.md](../semantic-release/gitlab-integration.md) — Requires `GIT_DEPTH: 0`
- [caching.md](caching.md) — `GIT_CLEAN_FLAGS` interaction with cache directories

## Sources

- [GitLab Runner — Configure Git Strategy](https://docs.gitlab.com/ci/runners/configure_runners/)
- [GitLab Runner Advanced Configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
