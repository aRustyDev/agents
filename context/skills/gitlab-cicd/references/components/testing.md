---
name: component-testing
description: Self-referencing with @$CI_COMMIT_SHA, integration test patterns, and matrix validation
---

# Component Testing

> **Scope:** Self-referencing with @$CI_COMMIT_SHA, integration test patterns, and matrix validation
> **GitLab version:** 17.0+
> **Source cards:** CP-4
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when testing CI/CD components before publishing to the Catalog —
self-referencing patterns, integration tests, and input validation.

## Key Concepts

- **Self-referencing** with `@$CI_COMMIT_SHA` — test component from current commit
- **Integration test patterns** — consume your own component in test jobs
- **Matrix testing** — validate across input combinations
- **Catalog release validation** — pre-publish checks

<!-- TODO: Expand with test strategy patterns and CI/CD component testing lifecycle -->

## Examples

```yaml
# Self-referencing test pattern
test_component:
  stage: test
  trigger:
    include:
      - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/my-component@$CI_COMMIT_SHA
        inputs:
          stage: test
    strategy: depend
```

<!-- TODO: Expand with matrix testing and multi-component validation -->

## Common Patterns

- `include:component: $CI_SERVER_FQDN/project/comp@$CI_COMMIT_SHA` for pre-merge testing
- Matrix testing across input combinations with `parallel:matrix`
- Pre-publish pipeline that validates all components in project

## Anti-Patterns

- Publishing untested components to catalog
- Testing against `@~latest` instead of `@$CI_COMMIT_SHA`
- Not testing with different input combinations and edge cases

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [authoring.md](authoring.md) — component project structure
- [inputs.md](inputs.md) — spec:inputs validation
- [catalog.md](catalog.md) — catalog publishing requirements

## Sources

- [GitLab CI/CD components](https://docs.gitlab.com/ci/components/)
- Context card: CP-4


<!-- TODO: Expand with deeper research -->
