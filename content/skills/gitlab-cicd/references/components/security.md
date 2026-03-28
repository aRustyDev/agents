---
name: component-security
description: Version pinning audit, include:integrity, minimal credentials, and source review
---

# Component Security

> **Scope:** Version pinning audit, include:integrity, minimal credentials, and source review
> **GitLab version:** 17.0+
> **Source cards:** CP-5
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when auditing component security, managing version pinning policies,
or minimizing credential exposure in CI/CD component usage.

## Key Concepts

- **Version pinning** — exact pin `@1.2.3` for maximum security, major pin `@1` for convenience
- **`include:integrity`** — SHA256 verification for tamper detection
- **Source auditing** — review component source before adoption and on updates
- **Minimal credential exposure** — avoid passing secrets as component inputs
- **Self-managed mirroring** — fork/mirror external components for enterprise control
- **Ephemeral runners** — use for security-sensitive component jobs

<!-- TODO: Expand with integrity hash generation, audit workflows, and enterprise policies -->

## Examples

```yaml
include:
  - component: $CI_SERVER_FQDN/org/sast@1.2.3  # exact pin
    integrity: sha256:abc123...                   # tamper detection
    inputs:
      stage: security
```

<!-- TODO: Expand with audit trail and update verification patterns -->

## Common Patterns

- Pin to exact version `@1.2.3` for security-sensitive components
- Fork/mirror external components for enterprise control
- Use `include:integrity` SHA256 for tamper detection on remote includes
- Audit component updates before version bumps

## Anti-Patterns

- Using `@~latest` for security-sensitive components
- Passing secrets as component inputs without encryption
- Not auditing third-party component source code

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [catalog.md](catalog.md) — catalog evaluation criteria
- [authoring.md](authoring.md) — component project structure
- [../security/secrets-management.md](../security/secrets-management.md) — secrets handling
- [../pipelines/security.md](../pipelines/security.md) — pipeline security

## Sources

- [GitLab CI/CD components](https://docs.gitlab.com/ci/components/)
- Context card: CP-5


<!-- TODO: Expand with deeper research -->
