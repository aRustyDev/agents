---
name: semantic-release-testing
description: Dry-run mode, semantic-release-info, SEMREL_INFO_NEXT_VERSION, and verification steps
---

# Semantic Release Testing

> **Scope:** Dry-run mode, semantic-release-info, SEMREL_INFO_NEXT_VERSION, and verification steps
> **GitLab version:** 13.0+
> **Source cards:** SR-3
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when testing semantic-release configurations before actual releases —
dry-run mode, version prediction, and verification steps.

## Key Concepts

- **Dry-run mode** — `--dry-run` flag simulates release without publishing
- **semantic-release-info** — lightweight tool to predict next version
- **`SEMREL_INFO_NEXT_VERSION`** — environment variable set by info plugin
- **Verification steps** — validate credentials, permissions, and config before release

<!-- TODO: Expand with MR-based dry-run patterns, verification scripts, and CI job templates -->

## Examples

```yaml
# Dry-run on merge requests
release_preview:
  stage: test
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - npx semantic-release --dry-run
  allow_failure: true
```

<!-- TODO: Expand with version prediction and pre-release validation patterns -->

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

- [configuration.md](configuration.md) — .releaserc configuration
- [gitlab-integration.md](gitlab-integration.md) — GitLab plugin setup

## Sources

- Context card: SR-3


<!-- TODO: Expand with deeper research -->
