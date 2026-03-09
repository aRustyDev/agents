---
name: variable-definition
description: Defining variables in YAML, UI, API — options, description, and expand behavior
---

# Variable Definition

> **Scope:** Defining variables in YAML, UI, API — options, description, and expand behavior
> **GitLab version:** 9.0+
> **Source cards:** VA-5
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult this when defining custom CI/CD variables at global, job, or include levels,
or configuring manual pipeline variable inputs with dropdowns and descriptions.

## Key Concepts

### Variable Definition Locations

| Location | Syntax | Precedence | Scope |
|----------|--------|-----------|-------|
| Global `variables:` | In `.gitlab-ci.yml` top-level | Low (pipeline default) | All jobs |
| Job-level `variables:` | Under specific job | Overrides global | Single job |
| `include:inputs` | Via `spec:inputs` in included file | Depends on expansion | Included template |
| CI/CD Settings (UI/API) | Project → Settings → CI/CD | Higher than YAML | All pipelines |
| Group-level | Group → Settings → CI/CD | Inherited by projects | All group pipelines |

### Variable Sub-Keywords

| Sub-keyword | Purpose | Version |
|------------|---------|--------|
| `value:` | Default value for variable | 13.7+ |
| `description:` | UI hint text for manual pipeline runs | 13.7+ |
| `options:` | Dropdown list for manual pipeline inputs | 15.7+ |
| `expand:` | Control recursive variable expansion (`false` to disable) | 13.7+ |

### Variable Inheritance Control

- `inherit:variables: true` (default) — job inherits all global variables
- `inherit:variables: false` — job opts out of all global variables
- `inherit:variables: [VAR_A, VAR_B]` — selectively inherit named variables

<!-- TODO: Expand with API-defined variables and instance-level variables -->

## Examples

```yaml
# Global defaults with job-level overrides
variables:
  APP_ENV: staging
  DEPLOY_REGION: us-east-1

build:
  variables:
    APP_ENV: production  # overrides global
  script:
    - echo "Building for $APP_ENV in $DEPLOY_REGION"
```

```yaml
# Manual pipeline with dropdown and description
variables:
  DEPLOY_ENV:
    value: staging
    description: "Target deployment environment"
    options:
      - staging
      - production
      - canary
  DRY_RUN:
    value: "true"
    description: "Set to false for actual deployment"

deploy:
  rules:
    - if: $CI_PIPELINE_SOURCE == "web"
  script:
    - ./deploy.sh --env=$DEPLOY_ENV --dry-run=$DRY_RUN
```

```yaml
# Expansion control and inheritance
variables:
  BASE_URL: "https://api.example.com"
  ENCODED_TOKEN:
    value: "$RAW_TOKEN"   # normally expands
    expand: false           # keeps literal "$RAW_TOKEN"

minimal_job:
  inherit:
    variables: false  # no global vars
  variables:
    LOCAL_ONLY: "value"
  script:
    - echo "$LOCAL_ONLY"
```

## Common Patterns

- **Define defaults in global `variables:`** — override only where needed at job level
- **Use `options:` for constrained inputs** — prevents typos in manual pipeline runs
- **`description:` for self-documenting triggers** — UI shows hint text when running manually
- **`inherit:variables: false`** to create clean-room jobs that don't inherit globals
- **`expand: false`** when variable values contain `$` characters that shouldn't expand

## Anti-Patterns

- **Defining all variables at job level** — creates duplication; use global defaults
- **Not using `inherit:variables`** to control inheritance — jobs may inherit unexpected values
- **Putting secrets in YAML `variables:`** — use CI/CD Settings (masked/protected) instead
- **Forgetting `expand: false`** on values containing `$` — causes unexpected recursive expansion

## Related Topics

- [precedence.md](precedence.md) — 11-level variable precedence hierarchy
- [scopes.md](scopes.md) — variable expansion contexts
- [masking-protection.md](masking-protection.md) — masking rules and protected variables
- [predefined.md](predefined.md) — 170+ built-in CI/CD variables

## Sources

- [GitLab CI/CD variables](https://docs.gitlab.com/ci/variables/)
- Context card: VA-5

