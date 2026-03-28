---
name: notifications
description: Slack integration, email notifications, webhooks, pipeline badges, and chat ops
---

# Notifications

> **Scope:** Slack integration, email notifications, webhooks, pipeline badges, and chat ops
> **GitLab version:** 9.0+
> **Source cards:** NEW-16
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when configuring pipeline notifications, status badges,
or chat integrations for CI/CD visibility.

## Key Concepts

- **Pipeline status badges** — embed in README for project health visibility
- **Email notifications** — built-in for pipeline failure alerts
- **Slack/Teams integration** — project integrations for pipeline events
- **Custom webhooks** — programmatic notification via pipeline webhooks
- **ChatOps** — trigger pipelines from chat commands

<!-- TODO: Expand with integration setup, webhook payload formats, and filter configuration -->

## Examples

```markdown
<!-- Pipeline badge in README -->
[![pipeline status](https://gitlab.example.com/org/project/badges/main/pipeline.svg)](https://gitlab.example.com/org/project/-/commits/main)

[![coverage report](https://gitlab.example.com/org/project/badges/main/coverage.svg)](https://gitlab.example.com/org/project/-/commits/main)
```

<!-- TODO: Expand with Slack integration and webhook configuration -->

## Common Patterns

- Pipeline badge in project README for visibility
- Slack notification for **failed pipelines only** (avoid noise)
- Separate notification channels per environment

## Anti-Patterns

- Notifying on every pipeline event — causes alert fatigue
- No failure notifications — broken pipelines go unnoticed

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [cross-project.md](cross-project.md) — cross-project triggers and integration
- [../pipelines/environments.md](../pipelines/environments.md) — environment-based deployments

## Sources

- Context card: NEW-16


<!-- TODO: Expand with deeper research -->
