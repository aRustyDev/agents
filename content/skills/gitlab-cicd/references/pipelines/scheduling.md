---
name: scheduled-pipelines
description: Cron syntax, CI_PIPELINE_SOURCE == schedule detection, and schedule-only job patterns
---

# Scheduled Pipelines

> **Scope:** Cron syntax, CI_PIPELINE_SOURCE == schedule detection, and schedule-only job patterns
> **GitLab version:** 9.0+
> **Source cards:** NEW-17
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when setting up periodic pipeline runs — nightly builds, scheduled scans,
cleanup tasks, or time-based workflows.

## Key Concepts

- **Pipeline schedules** are configured in GitLab UI: CI/CD → Schedules
- Use **cron syntax** (5-field: minute hour day month weekday) for timing
- Scheduled pipelines set `CI_PIPELINE_SOURCE = "schedule"` — use in rules for filtering
- **Schedule-specific variables** can be defined per schedule in the UI
- Schedule **owner permissions** determine what the pipeline can access

<!-- TODO: Expand with cron syntax examples and timezone handling -->

## Examples

```yaml
# Schedule-only job
nightly_security_scan:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - ./run-security-scan.sh

# Exclude from schedules
build:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
    - when: on_success
```

<!-- TODO: Expand with multi-schedule patterns and variable-based routing -->

## Common Patterns

- **Nightly build schedule** with cron `0 2 * * *`
- **`$CI_PIPELINE_SOURCE == "schedule"`** to run schedule-only jobs
- **Separate schedules** for security scanning vs cleanup vs reporting

## Anti-Patterns

- Running full pipeline on schedule when only specific jobs are needed
- No schedule-specific `rules:` filtering — every job runs unnecessarily

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [types-and-triggers.md](types-and-triggers.md) — pipeline source types
- [../yaml/rules-patterns.md](../yaml/rules-patterns.md) — rules clause patterns

## Sources

- Context card: NEW-17


<!-- TODO: Expand with deeper research -->
