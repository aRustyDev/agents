---
name: component-include-patterns
description: Annotated component template patterns extracted from workspace pipelines
---

# Component Include Patterns

> **Scope:** Annotated component template patterns extracted from workspace pipelines
> **Source cards:** EX-2
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

Reference this example when authoring CI/CD components or understanding
how the MAP team structures reusable pipeline templates with `spec:inputs`.

## Component Template Analysis

### validate-terragrunt-lockfile Component

**Location:** `templates/validate-terragrunt-lockfile/template.yml`
**Purpose:** Validates that Terragrunt lock files have multi-platform provider hashes.

### Input Specification

```yaml
spec:
  inputs:
    image:
      description: The image to use to run this job.
      default: c4p/map/image-awscli-docker/awscli-docker:1.5.0
      type: string
    image_registry:
      description: The image registry for the job image.
      default: registry.sscm.gus.cisco.com
      type: string
    stage:
      description: The name of the stage to run this job on.
      default: "quality"
    rules:
      description: When to run the job
      type: array
      default:
        - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    tags:
      description: GitLab runner tags to place the job
      type: array
      default: ["c4p-production"]
```

**Patterns demonstrated:**
- **Typed inputs** — `string`, `array` types for validation → see [component inputs](../references/components/inputs.md)
- **Sensible defaults** — every input has a default, making the component zero-config for typical use
- **Configurable rules** — `rules:` as array input allows consumers to customize trigger conditions
- **Registry abstraction** — separate `image` and `image_registry` inputs for flexible registry configuration
- **Runner tag flexibility** — `tags:` as array input for multi-environment support

### Input Interpolation Pattern

```yaml
validate-terragrunt-lockfile:
  image: $[[ inputs.image_registry ]]/$[[ inputs.image ]]
  stage: $[[ inputs.stage ]]
  tags:
    - $[[ inputs.tags ]]
  rules:
    - $[[ inputs.rules ]]
```

**Key observations:**
- Uses `$[[ inputs.* ]]` interpolation syntax (component-specific, not standard YAML variables)
- Image composed from two inputs: `registry/image` — allows registry override for air-gapped environments
- Tags and rules passed through as arrays

### Script Structure

The component script follows a two-phase pattern:

1. **Discovery phase** — `git diff` to find changed `terragrunt.hcl` files
2. **Validation phase** — check each directory for lock file completeness

```yaml
script:
  # Phase 1: Find changed files
  - |
    git fetch origin main
    CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep 'terragrunt\.hcl$' || true)
    # Early exit if no changes

  # Phase 2: Validate lock files
  - |
    for dir in $(echo "$CHANGED_FILES" | xargs -r dirname | sort -u); do
      # Check lock file exists and has multi-platform hashes
    done
```

**Patterns demonstrated:**
- Early exit when no relevant files changed (saves compute)
- `|| true` to prevent grep from failing when no matches
- Multi-platform hash validation (linux_amd64 + darwin_arm64)
- Clear error messages with remediation instructions

## Component Include Patterns in Workspace

### From ci-c4p-token-rotator

```yaml
include:
  # Org-internal shared template (no version pin)
  - project: "c4p/map/ci-templates"
    file: "quality/mega-linter.yml"
  # Catalog component with exact version
  - component: $CI_SERVER_FQDN/gtts/cicd/components/release/check-commit@1.1.0
    inputs:
      stage: quality
      merge_title_mode: true
```

### From map-terragrunt-pipeline

```yaml
include:
  - project: "c4p/map/ci-templates"
    file: "quality/mega-linter.yml"
  - component: $CI_SERVER_FQDN/gtts/cicd/components/release/check-commit@1.1.0
    inputs:
      stage: quality
      merge_title_mode: true
  - component: $CI_SERVER_FQDN/gtts/cicd/components/release/create@1.1.0
    inputs:
      use_conventional_commits: true
      stage: quality
      gitlab_token: $C4P_DEV_TOKEN
```

**Observations:**
- Both pipelines share identical MegaLinter + check-commit includes → candidate for extraction into a shared base
- `release/create` adds automated release creation with conventional commits
- `$CI_SERVER_FQDN` makes components portable across GitLab instances
- Components use `@1.1.0` exact pin while project templates use implicit `main`

## Common Patterns

- **Zero-config defaults** — all inputs optional with sensible defaults
- **Registry/image separation** — supports air-gapped and custom registry environments
- **Rules as input** — consumers customize when the component runs
- **`$CI_SERVER_FQDN`** — instance-agnostic component references
- **Exact version pinning** — `@1.1.0` for reproducible builds

## Anti-Patterns

- **Unversioned `include:project`** — `ci-templates` without `ref:` risks breakage
- **Duplicate includes** — identical MegaLinter + check-commit blocks in both pipelines; could use a shared base template
- **`$[[ inputs.tags ]]` as single array item** — may not properly expand multi-tag arrays

## Practitioner Pain Points

- `$[[ ]]` interpolation syntax differs from `${{ }}` (variables) — easy to confuse
- No built-in way to test component locally before pushing
- Array input expansion behavior isn't always intuitive

## Related Topics

- [../references/components/authoring.md](../references/components/authoring.md) — component project structure
- [../references/components/inputs.md](../references/components/inputs.md) — spec:inputs types
- [../references/components/catalog.md](../references/components/catalog.md) — catalog publishing
- [../references/components/testing.md](../references/components/testing.md) — component testing
- [../references/yaml/yaml-composition.md](../references/yaml/yaml-composition.md) — YAML reuse patterns

## Sources

- Workspace files: `templates/validate-terragrunt-lockfile/template.yml`, `.gitlab-ci.yml` (both repos)
