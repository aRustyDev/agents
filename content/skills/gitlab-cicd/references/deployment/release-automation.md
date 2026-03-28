---
name: release-automation
description: Changelog generation, release: keyword, multi-package coordination, and orchestration
---

# Release Automation

> **Scope:** Changelog generation, release: keyword, multi-package coordination, and orchestration
> **GitLab version:** 13.0+
> **Source cards:** NEW-12
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Automating release creation with changelogs and version bumping
- Coordinating multi-package releases in monorepos
- Integrating GitLab Releases API with CI/CD pipelines
- Using the `release:` keyword for declarative release creation

## Key Concepts

### release: Keyword

Declarative release creation in `.gitlab-ci.yml`:

```yaml
release:
  tag_name: $CI_COMMIT_TAG
  description: $CI_COMMIT_TAG_MESSAGE
  ref: $CI_COMMIT_SHA
  milestones: [v1.0.0]
  assets:
    links:
      - name: Package
        url: https://example.com/releases/$CI_COMMIT_TAG
        link_type: package
```

### Release Methods

| Method | When to Use |
|---|---|
| **`release:` keyword** | Simple tag-based releases with asset links |
| **semantic-release** | Automated versioning from conventional commits |
| **GitLab Releases API** | Programmatic release creation |
| **`glab release create`** | CLI-based release creation |

### Changelog Generation

| Method | Tool |
|---|---|
| **GitLab changelog API** | `POST /projects/:id/repository/changelog` |
| **semantic-release** | `@semantic-release/changelog` plugin |
| **conventional-changelog** | Standalone changelog generator |

### Multi-Package Coordination

For monorepos with multiple packages:
- **Per-package child pipelines** with independent release jobs
- **Release commit** updates all package versions atomically
- **Tag format** per package: `pkg-name-v1.2.0`

### Path-Based Release Triggers

```yaml
release-api:
  rules:
    - if: $CI_COMMIT_TAG
      changes: [packages/api/**]
  release:
    tag_name: $CI_COMMIT_TAG
    description: "API release $CI_COMMIT_TAG"
```

## Examples

### Tag-Based Release

```yaml
release:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG
  release:
    tag_name: $CI_COMMIT_TAG
    description: $CI_COMMIT_TAG_MESSAGE
    assets:
      links:
        - name: "Binary"
          url: "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/${CI_PROJECT_NAME}/${CI_COMMIT_TAG}/app.tar.gz"
          link_type: package
```

### Semantic-Release Integration

```yaml
release:
  stage: release
  image: node:lts-slim
  variables:
    GIT_DEPTH: 0
  before_script:
    - npm install -g semantic-release @semantic-release/gitlab
  script:
    - npx semantic-release
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Release with Changelog

```yaml
release:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  script:
    - echo "Creating release for $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    description: ./CHANGELOG.md
    ref: $CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
```

## Common Patterns

- **`release:` keyword** with `$CI_COMMIT_TAG` for declarative releases
- **semantic-release** for automated versioning and changelog generation
- **`rules:changes`** for monorepo per-package release triggers
- **release-cli image** for release creation without semantic-release
- **Asset links** to generic packages or build artifacts

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Manual version bumping | Error-prone, inconsistent | Use semantic-release or conventional commits |
| Running all jobs on release tags | Wastes CI/CD minutes | Filter with `rules:if: $CI_COMMIT_TAG` |
| No changelog | Users can't understand changes | Generate from conventional commits |
| Release without tag | Releases without git reference | Always create from tag |

## Practitioner Pain Points

1. **`release:` keyword requires `release-cli`** — the job image must include the release CLI tool, or use the GitLab release-cli image.
2. **Multi-package monorepo releases** — coordinating versions across packages requires custom orchestration.
3. **Changelog from conventional commits** — requires consistent commit message format (angular or conventionalcommits preset).
<!-- TODO: Expand with deeper research on multi-package release coordination and changelog API -->

## Related Topics

- [../semantic-release/gitlab-integration.md](../semantic-release/gitlab-integration.md) — Semantic-release plugin config
- [../pipelines/monorepo.md](../pipelines/monorepo.md) — Monorepo pipeline strategies
- [../jobs/git-strategies.md](../jobs/git-strategies.md) — GIT_DEPTH for release history

## Sources

- [GitLab Releases](https://docs.gitlab.com/user/project/releases/)
- [release keyword](https://docs.gitlab.com/ci/yaml/#release)
