---
name: component-authoring
description: Component project structure, templates/ directory, spec:inputs, and Catalog publishing
---

# Component Authoring

> **Scope:** Component project structure, templates/ directory, spec:inputs, and Catalog publishing
> **GitLab version:** 17.0+
> **Source cards:** CP-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Creating reusable CI/CD components for the GitLab CI/CD Catalog
- Designing `spec:inputs` with type validation and defaults
- Publishing components with semantic versioning
- Testing components before catalog release

## Key Concepts

### Component Project Structure

```
my-component/
├── templates/
│   ├── build/                    # Subdirectory component
│   │   └── template.yml
│   └── test.yml                  # Single-file component
├── .gitlab-ci.yml                # Component's own CI pipeline
└── README.md
```

- **Single-file components:** `templates/<name>.yml`
- **Subdirectory components:** `templates/<name>/template.yml`
- **Limit:** Max **30 components** per project

### spec:inputs

Define typed inputs with validation:

```yaml
spec:
  inputs:
    image:
      type: string
      default: "node:lts"
      description: "Docker image to use"
    node-version:
      type: string
      options: ["18", "20", "22"]
      default: "20"
    timeout:
      type: number
      default: 30
    enable-cache:
      type: boolean
      default: true
    allowed-branches:
      type: array
      default: ["main"]
    pattern:
      type: string
      regex: '^v\d+\.\d+\.\d+$'
---
# Job definitions using $[[ inputs.image ]] interpolation
```

### Input Types

| Type | Validation | Interpolation |
|---|---|---|
| `string` | `options:`, `regex:` | `$[[ inputs.name ]]` |
| `number` | Numeric | `$[[ inputs.name ]]` |
| `boolean` | `true`/`false` | `$[[ inputs.name ]]` |
| `array` | List of strings | `$[[ inputs.name ]]` |

### include:component Syntax

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/components/build@1.2.0
    inputs:
      image: node:20-slim
      enable-cache: true
```

### Version Pinning

| Pin Style | Example | Behavior |
|---|---|---|
| Exact | `@1.2.0` | Immutable, recommended for production |
| Minor | `@1.2` | Latest patch in minor |
| Major | `@1` | Latest minor+patch in major |
| Latest | `@~latest` | Latest release (risky) |
| SHA | `@$CI_COMMIT_SHA` | For testing (self-referencing) |

### Catalog Publishing

1. Add **CI/CD Catalog** resource type to project settings
2. Use [semantic versioning](https://semver.org/) for releases
3. GitLab creates catalog entry on each release tag
4. **Verified creator** badge for trusted organizations

## Examples

### Minimal Component

```yaml
# templates/test.yml
spec:
  inputs:
    image:
      type: string
      default: node:lts
---
test:
  image: $[[ inputs.image ]]
  script:
    - npm ci
    - npm test
```

### Self-Referencing Test

```yaml
# .gitlab-ci.yml (component's own pipeline)
include:
  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/test@$CI_COMMIT_SHA
    inputs:
      image: node:20
```

### Consumer Usage

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/ci-components/build@2.1.0
    inputs:
      image: node:20-slim
      enable-cache: true
  - component: $CI_SERVER_FQDN/my-org/ci-components/deploy@2.1.0
    inputs:
      environment: staging
```

## Common Patterns

- **`include:component:` with `@semver`** for version-pinned includes
- **`spec:inputs` with `type` + `default` + `description`** for self-documenting components
- **Test components with `@$CI_COMMIT_SHA`** before publishing
- **Semantic versioning** for catalog releases

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Remote YAML without version pinning | Config changes unexpectedly | Use `@semver` pinning |
| Deep nesting of includes (3+) | Hard to debug, slow expansion | Flatten include hierarchy |
| Global keywords in components | Conflicts with consumer pipeline | Only define job-level keywords |
| Not testing before catalog publish | Broken components in catalog | Test with `@$CI_COMMIT_SHA` |
| Exceeding 30 components per project | Limit exceeded, components ignored | Split into multiple projects |

## Practitioner Pain Points

1. **Component testing requires self-referencing** — `@$CI_COMMIT_SHA` pattern is non-obvious.
2. **Global keywords in components conflict** — don't define `stages:`, `workflow:`, or `default:` in components.
3. **Catalog search/discovery still maturing** — finding relevant components requires browsing or direct links.
<!-- TODO: Expand with deeper research on component input validation patterns and catalog best practices -->

## Related Topics

- [../yaml/rules-patterns.md](../yaml/rules-patterns.md) — Rules in component templates
- [../pipelines/security.md](../pipelines/security.md) — SHA pinning and include integrity
- [inputs.md](inputs.md) — Detailed input type configuration
- [catalog.md](catalog.md) — Catalog publishing workflow

## Sources

- [CI/CD components](https://docs.gitlab.com/ci/components/)
- [CI/CD Catalog](https://docs.gitlab.com/ci/components/#cicd-catalog)
