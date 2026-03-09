---
name: map-terragrunt-pipeline-example
description: Annotated analysis of a real-world Terragrunt pipeline using CI/CD components and MegaLinter
---

# MAP Terragrunt Pipeline Example

> **Scope:** Annotated analysis of a real-world Terragrunt pipeline using CI/CD components and MegaLinter
> **Source cards:** EX-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

Reference this example when analyzing or modifying MAP team pipelines,
or when building similar operational automation with scheduled pipelines
and CI/CD components.

## Pipeline Overview

The MAP team uses two complementary pipelines in this workspace:

### ci-c4p-token-rotator Pipeline

**Purpose:** Automated service account token rotation on a schedule.

**Architecture:** Basic pipeline (linear stages), 5 stages, 2 primary jobs.

```
[quality] ── mega-linter, check-commit
[test]    ── test-hidden-variable-rotation (MR only)
[build]   ── (empty)
[deploy]  ── rotate-service-account-token (schedule only)
[notify]  ── (empty)
```

### map-terragrunt-pipeline Pipeline

**Purpose:** CI/CD component pipeline for Terragrunt lockfile validation.

**Architecture:** Component-based pipeline with cross-project includes.

```
[quality] ── mega-linter, check-commit, create-release
```

## Annotated Configuration

### Global Configuration

```yaml
# Both pipelines share this pattern:
default:
  tags:
    - c4p-production    # Tag-based routing to team runners

workflow:
  auto_cancel:
    on_new_commit: interruptible  # Cancel stale pipelines (16.0+)
```

**Why this works:**
- `default:tags` avoids repeating tags per-job → see [runner architecture](../references/runner/architecture.md)
- `auto_cancel:on_new_commit: interruptible` saves compute → see [optimization](../references/pipelines/optimization.md)

### Include Strategy

```yaml
include:
  # Cross-project template for MegaLinter
  - project: "c4p/map/ci-templates"
    file: "quality/mega-linter.yml"
  # CI/CD Catalog component — version-pinned
  - component: $CI_SERVER_FQDN/gtts/cicd/components/release/check-commit@1.1.0
    inputs:
      stage: quality
      merge_title_mode: true
```

**Patterns demonstrated:**
- `include:project` for org-internal shared templates (no version pin — trusts `main`) → see [yaml-composition](../references/yaml/yaml-composition.md)
- `include:component` with `@1.1.0` exact version pin → see [component catalog](../references/components/catalog.md)
- `inputs:` parameter passing to components → see [component inputs](../references/components/inputs.md)

### Schedule-Only Job Pattern

```yaml
rotate-service-account-token:
  stage: deploy
  image: $CI_REGISTRY/c4p/map/image-awscli-docker/awscli-docker:1.4.0
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule" && $CI_COMMIT_BRANCH == "main"
  script:
    # 1. Rotate token via GitLab API
    # 2. Extract new token + ID
    # 3. Update CI/CD group variables via API
```

**Why this works:**
- `rules:if` with `$CI_PIPELINE_SOURCE == "schedule"` → see [scheduling](../references/pipelines/scheduling.md)
- Uses `$CI_REGISTRY` for private images → see [docker-builds](../references/jobs/docker-builds.md)
- API calls with `PRIVATE-TOKEN` header for GitLab API auth
- Group-level variables (`$C4P_GROUP_ID`) for cross-project token management

### MR Test Pattern

```yaml
test-hidden-variable-rotation:
  stage: test
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  variables:
    TEST_VAR_NAME: "C4P_DEV_TOKEN_TEST"
  script:
    # 5-step validation: cleanup → create → verify → update → verify → delete
```

**Patterns demonstrated:**
- MR-only job via `$CI_PIPELINE_SOURCE == "merge_request_event"` → see [merge-request](../references/pipelines/merge-request.md)
- Job-level variables for test isolation → see [variable definition](../references/variables/definition.md)
- Idempotent test (pre-flight cleanup + post-test cleanup)

### Security Scanning Configuration

```yaml
# .ci/.checkov.yml — Checkov skip rules
skip-check:
  - CKV_GLB_1   # Skip specific checks with documented reasons
  - CKV_TF_1    # "we use version tags instead of git commit hashes"

# .ci/kics.yml — KICS exclusions
exclude-paths:
  - "external/"
exclude-queries:
  - "e592a0c5-..."  # IAM Access Analyzer
```

**Patterns demonstrated:**
- Separate config files per scanner in `.ci/` directory
- Documented skip reasons for audit trail → see [compliance](../references/security/compliance.md)

## Common Patterns

- **Schedule + MR pipeline separation** — deployment jobs on schedule, test jobs on MR
- **Component version pinning** — `@1.1.0` for reproducible builds
- **Cross-project includes** — shared MegaLinter template from org repo
- **Private registry images** — `$CI_REGISTRY` for internal Docker images
- **Idempotent test jobs** — cleanup before and after test execution

## Anti-Patterns

- **No `include:project` version pin** — `ci-templates` include trusts `main` branch; could break on upstream changes. Consider adding `ref:` pin.
- **Long inline scripts** — the rotation job has 50+ lines of shell; could extract to a script file for testability
- **No `retry:` on API-dependent jobs** — rotation job calls external APIs but has no retry strategy for transient failures
- **No `timeout:` set** — both jobs use default timeout; the rotation job should have an explicit short timeout

## Practitioner Pain Points

- Token rotation requires careful error handling — partial rotation leaves inconsistent state
- `masked_and_hidden` variables can't be read via API — requires specific update patterns
- MegaLinter include has no version pin — upstream changes can break quality stage

## Related Topics

- [../references/pipelines/scheduling.md](../references/pipelines/scheduling.md) — scheduled pipeline patterns
- [../references/pipelines/merge-request.md](../references/pipelines/merge-request.md) — MR pipeline configuration
- [../references/components/authoring.md](../references/components/authoring.md) — component design
- [../references/security/secrets-management.md](../references/security/secrets-management.md) — secrets handling
- [../references/variables/masking-protection.md](../references/variables/masking-protection.md) — masked/hidden variables

## Sources

- Workspace files: `.gitlab-ci.yml`, `.ci/kics.yml`, `.ci/.checkov.yml`
