---
name: semantic-release-configuration
description: .releaserc options, presets, hook scripts, GPG signing, and plugin chain configuration
---

# Semantic Release Configuration

> **Scope:** .releaserc options, presets, hook scripts, GPG signing, and plugin chain configuration
> **GitLab version:** 13.0+
> **Source cards:** SR-2, SR-4, SR-5
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when configuring `.releaserc` files, plugin chains, presets,
or hook scripts for semantic-release in GitLab CI/CD.

## Key Concepts

- **`.releaserc`** (or `.releaserc.json`/`.releaserc.yml`) — main configuration file
- **Plugin chain** — ordered list of plugins that execute in lifecycle order
- **Presets** — conventional-commits preset is most common
- **Branches** — configure release branches (main, maintenance, prerelease)
- **Hook scripts** — `prepare`, `publish`, `success`, `fail` lifecycle hooks
- **GPG signing** — sign tags and commits for verified releases

<!-- TODO: Expand with complete .releaserc reference, plugin configuration options, and multi-branch setup -->

## Examples

```json
// .releaserc.json — basic configuration
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    ["@semantic-release/gitlab", {
      "gitlabUrl": "https://gitlab.example.com"
    }],
    "@semantic-release/git"
  ]
}
```

<!-- TODO: Expand with multi-branch, monorepo, and custom plugin configurations -->

## Common Patterns

<!-- TODO: Expand with deeper research -->

## Anti-Patterns

<!-- TODO: Expand with deeper research -->

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [gitlab-integration.md](gitlab-integration.md) — @semantic-release/gitlab plugin
- [testing.md](testing.md) — dry-run and verification
- [../deployment/release-automation.md](../deployment/release-automation.md) — GitLab release keyword

## Sources

- Context cards: SR-2, SR-4, SR-5


<!-- TODO: Expand with deeper research -->
