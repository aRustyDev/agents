---
name: semantic-release-gitlab-integration
description: @semantic-release/gitlab plugin, to-be-continuous component, token setup, and asset upload
---

# Semantic Release GitLab Integration

> **Scope:** @semantic-release/gitlab plugin, to-be-continuous component, token setup, and asset upload
> **GitLab version:** 13.0+
> **Source cards:** SR-1, PR-1
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need automated versioning and releases via semantic-release in GitLab CI
- You're choosing between `@semantic-release/gitlab` plugin and the `to-be-continuous` component
- You need to configure authentication tokens (GITLAB_TOKEN vs CI_JOB_TOKEN)
- You need to upload release assets or manage changelogs

**Do NOT use when:**
- You don't use conventional commits (semantic-release requires commit message conventions)
- Manual versioning is sufficient for your project

## Key Concepts

### @semantic-release/gitlab Plugin (v13.3.2)

Lifecycle hooks:
- **verifyConditions** — Verify `GITLAB_TOKEN` access and permissions
- **publish** — Publish a GitLab Release (via Releases API)
- **success** — Comment on each resolved issue/MR
- **fail** — Open/update a GitLab issue with failure details

### Authentication

| Method | Variable | Scopes | Limitations |
|---|---|---|---|
| **Project/Personal Access Token** | `GL_TOKEN` or `GITLAB_TOKEN` | `api` + `write_repository` | Full functionality |
| **CI Job Token** | `CI_JOB_TOKEN` (set `useJobToken: true`) | Automatic | Cannot comment on issues/MRs; cannot interact with other projects |

> **Security:** Protect `GITLAB_TOKEN` — only expose on protected branches. Unprotecting for
> non-prod branches enables privilege escalation risk.

### Plugin Options

| Option | Default | Purpose |
|---|---|---|
| `gitlabUrl` | `CI_SERVER_URL` | GitLab instance URL |
| `useJobToken` | `false` | Use `CI_JOB_TOKEN` instead of `GITLAB_TOKEN` |
| `assets` | `[]` | Files to upload with the release |
| `milestones` | `[]` | Milestone titles to associate |
| `successComment` | built-in | Comment template for resolved issues/MRs (Lodash template) |
| `failComment` | built-in | Comment template for failure issues |
| `retryLimit` | `3` | Max retries for API rate limit errors (HTTP 429) |

### Asset Upload Options

| Field | Required | Purpose |
|---|---|---|
| `path` | Yes | Glob pattern for files |
| `label` | No | Short label for the asset link |
| `type` | No | `runbook`, `package`, `image`, `other` |
| `target` | No | `project_upload` (default) or `generic_package` (package registry) |
| `filepath` | No | Permalink path under project releases |

### to-be-continuous Component (@4.0.4)

Key variables:

| Variable | Default | Purpose |
|---|---|---|
| `SEMREL_AUTO_RELEASE_ENABLED` | — | When `true`, job runs automatically; otherwise manual |
| `SEMREL_BRANCHES_REF` | `/^(master\|main)$/` | Regex matching release branches |
| `SEMREL_TAG_FORMAT` | `$${version}` | **Must double `$`** to prevent CI variable interpolation |
| `SEMREL_COMMIT_SPEC` | `angular` | Preset: `angular`, `conventionalcommits`, etc. |
| `SEMREL_CHANGELOG_ENABLED` | — | Enable `@semantic-release/changelog` plugin |
| `SEMREL_DRY_RUN` | — | Dry-run mode (no actual release) |
| `SEMREL_GPG_SIGNKEY` | — | Path to GPG key for signing release commits |

**Modes:**
- **Application Deployment** — release triggers downstream deployment
- **Software Distribution (no commit)** — publishes without committing
- **Software Distribution (with commit)** — commits changelog/version files then publishes

### Hook Scripts

The TBC component supports custom lifecycle hooks:
- `verify-conditions.sh` — runs during verifyConditions
- `prepare.sh` — runs during prepare (build artifacts, update files)
- `publish.sh` — runs during publish (deploy, push images)

## Examples

### TBC Component Basic Setup

```yaml
include:
  - component: $CI_SERVER_FQDN/to-be-continuous/semantic-release/gitlab-ci-semrel@4.0.4
    inputs:
      auto-release-enabled: "true"
      commit-spec: conventionalcommits
      tag-format: "$${version}"
variables:
  GITLAB_TOKEN: $MY_PROJECT_TOKEN
```

### Custom release.config.cjs

```javascript
module.exports = {
  branches: ['main', { name: 'next', prerelease: true }],
  plugins: [
    ['@semantic-release/commit-analyzer', { preset: 'conventionalcommits' }],
    '@semantic-release/release-notes-generator',
    ['@semantic-release/changelog', { changelogFile: 'CHANGELOG.md' }],
    ['@semantic-release/gitlab', {
      assets: [{ path: 'dist/**', label: 'Distribution' }],
      successComment: 'Released in ${nextRelease.version}',
      milestones: ['${nextRelease.version}'],
    }],
    ['@semantic-release/git', {
      message: 'chore(release): ${nextRelease.version} [skip ci]',
      assets: ['CHANGELOG.md', 'package.json'],
    }],
  ],
};
```

### Standalone CI Job

```yaml
semantic-release:
  stage: release
  image: node:lts-slim
  variables:
    GITLAB_TOKEN: $SEMANTIC_RELEASE_TOKEN
    GIT_DEPTH: 0  # Full history required
  before_script:
    - npm install -g semantic-release @semantic-release/gitlab
      @semantic-release/changelog @semantic-release/git
  script:
    - npx semantic-release
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Common Patterns

- **`SEMREL_TAG_FORMAT: $${version}`** — double `$` to escape CI variable interpolation
- **`GIT_DEPTH: 0`** required for semantic-release (needs full commit history)
- **`conventionalcommits` preset** for standard commit format
- **TBC component** with `include:component` for turnkey setup
- **`semantic-release-info` job** for dry-run version prediction via dotenv
- **GPG signing** with `SEMREL_GPG_SIGNKEY` for verified release commits

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using `CI_JOB_TOKEN` without understanding limitations | Disables issue/MR comments | Accept limitation or use GITLAB_TOKEN |
| `${version}` in tag format (single `$`) | CI eats the `$` — tag is malformed | Use `$${version}` (double dollar) |
| `[skip ci]` in release commit message | Prevents tag pipeline from running | Configure commit message without `[skip ci]` or use `[skip ci on prod]` |
| `@semantic-release/gitlab` < 6.0.7 with GitLab ≥ 14.0 | Tags API removed in 14.0; plugin switched to Releases API | Upgrade to ≥ 6.0.7 (latest: v13.3.2) |
| Unprotecting GITLAB_TOKEN for non-prod branches | Privilege escalation risk | Keep token protected; use CI_JOB_TOKEN for non-prod |
| Pinning to pre-v24 semantic-release with `conventionalcommits` | `conventional-changelog-conventionalcommits` v8.0.0 broke compatibility | Upgrade semantic-release to v24+ |

## Practitioner Pain Points

1. **GITLAB_TOKEN must have `api` + `write_repository` scopes** — Missing scopes cause `verifyConditions` failure. For TBC, also need `read_repository`.

2. **`[skip ci]` prevents tag pipeline** — Release commit with `[skip ci]` suppresses all pipelines including the tag pipeline. **Fix:** Use `[skip ci on prod]` or remove `[skip ci]`.

3. **`${version}` in tag format gets eaten by CI** — GitLab CI interprets `$` as variable reference. **Fix:** Double the dollar sign: `$${version}`.

4. **Shallow clone breaks semantic-release** — `GIT_DEPTH` default of 20 is insufficient. **Fix:** Set `GIT_DEPTH: 0` for release jobs.

5. **`useJobToken` disables `successComment` and `failComment`** — `CI_JOB_TOKEN` doesn't have API access for issue/MR comments. **Workaround:** Accept the limitation or use a project access token.

## Version Notes

| Version | Change |
|---|---|
| 14.0 | GitLab removed Tags API — `@semantic-release/gitlab` ≥ 6.0.7 required |
| 16.10 | SemVer enforced for CI/CD Catalog components only (not general releases) |
| 17.0+ | `include:component` fully GA — preferred over `include:project` |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Simple project, standard releases | TBC component with `SEMREL_AUTO_RELEASE_ENABLED` |
| Complex multi-package monorepo | Custom `release.config.cjs` with per-package plugins |
| Restricted environment, no PAT allowed | `useJobToken: true` (accept no issue/MR comments) |
| Need changelog committed to repo | Enable `SEMREL_CHANGELOG_ENABLED` or add `@semantic-release/changelog` |
| Pre-release branches (next, beta) | Configure `branches: [main, { name: "next", prerelease: true }]` |

## Related Topics

- [configuration.md](configuration.md) — `release.config.cjs` and plugin configuration details
- [testing.md](testing.md) — Testing semantic-release configuration
- [../jobs/git-strategies.md](../jobs/git-strategies.md) — `GIT_DEPTH: 0` requirement
- [../variables/masking-protection.md](../variables/masking-protection.md) — Protecting GITLAB_TOKEN

## Sources

- [@semantic-release/gitlab (GitHub)](https://github.com/semantic-release/gitlab)
- [to-be-continuous/semantic-release](https://to-be-continuous.gitlab.io/doc/ref/semantic-release/)
- [semantic-release Documentation](https://semantic-release.gitbook.io/)

