---
name: component-inputs
description: spec:inputs types (string/number/boolean/array), options, regex validation, and defaults
---

# Component Inputs

> **Scope:** spec:inputs types (string/number/boolean/array), options, regex validation, and defaults
> **GitLab version:** 17.0+
> **Source cards:** CP-3
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when defining or consuming `spec:inputs` for CI/CD components —
type validation, defaults, options, and constraints.

## Key Concepts

- **`spec:inputs`** defines typed parameters for components
- **Types:** `string` (default), `number`, `boolean`, `array`
- **`default:`** — value used when input not provided (makes input optional)
- **`options:`** — constrained list of valid string values
- **`regex:`** — pattern validation for string inputs
- **`description:`** — documentation hint for consumers

<!-- TODO: Expand with input validation rules and error messages -->

## Examples

```yaml
# Component spec with typed inputs
spec:
  inputs:
    stage:
      type: string
      default: test
      options:
        - build
        - test
        - deploy
    parallel_count:
      type: number
      default: 1
    enable_cache:
      type: boolean
      default: true
    version:
      type: string
      regex: ^\d+\.\d+\.\d+$
      description: "Semantic version (e.g., 1.2.3)"
```

<!-- TODO: Expand with array inputs and conditional input requirements -->

## Common Patterns

- Type-safe inputs with validated defaults
- `options:` for environment name constraints (staging/production)
- `regex:` for semver or naming convention enforcement
- Boolean inputs for feature flags in components

## Anti-Patterns

- Using `string` type when `number`/`boolean` would validate better
- Not providing defaults for optional inputs
- Overly complex regex that's hard to maintain

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [authoring.md](authoring.md) — component project structure
- [catalog.md](catalog.md) — catalog discovery and version pinning
- [testing.md](testing.md) — testing input combinations

## Sources

- [GitLab CI/CD components](https://docs.gitlab.com/ci/components/)
- Context card: CP-3


<!-- TODO: Expand with deeper research -->
