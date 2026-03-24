---
name: component-catalog
description: Catalog discovery, version pinning (@major), evaluation criteria, and verified creators
---

# Component Catalog

> **Scope:** Catalog discovery, version pinning (@major), evaluation criteria, and verified creators
> **GitLab version:** 17.0+
> **Source cards:** CP-2
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when discovering, evaluating, or integrating CI/CD components from the
GitLab CI/CD Catalog.

## Key Concepts

- **CI/CD Catalog** — searchable registry of reusable pipeline components
- **Verified creators** badge indicates trusted component authors
- **Version pinning** strategies:
  - `@1` — latest 1.x.x (major pin, recommended)
  - `@1.2` — latest 1.2.x (minor pin)
  - `@1.2.3` — exact version (maximum stability)
  - `@~latest` — latest release tag (avoid in production)
- **Catalog publishing** requires specific project structure and release tags

<!-- TODO: Expand with catalog search, filtering, and evaluation criteria -->

## Examples

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/sast@1  # major pin
    inputs:
      stage: test
```

<!-- TODO: Expand with catalog browsing and multi-component examples -->

## Common Patterns

- Pin to major version `@1` for compatible updates
- Evaluate verified creator badge before adoption
- Review component source code before integration

## Anti-Patterns

- Using `@~latest` in production — unpredictable breaking changes
- Not reviewing component source for security implications
- Adopting unverified components without audit

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [authoring.md](authoring.md) — creating CI/CD components
- [inputs.md](inputs.md) — spec:inputs types and validation
- [security.md](security.md) — component security practices

## Sources

- [GitLab CI/CD components](https://docs.gitlab.com/ci/components/)
- Context card: CP-2


<!-- TODO: Expand with deeper research -->
