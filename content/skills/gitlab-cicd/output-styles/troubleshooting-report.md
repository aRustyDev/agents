---
name: troubleshooting-report-output
description: Behavioral spec for debug reports — symptom → cause → fix → prevention structure
---

# Troubleshooting Report Output

> **Scope:** Behavioral spec for debug reports — symptom → cause → fix → prevention structure
> **Source cards:** OS-2
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Use this output format when diagnosing CI/CD pipeline failures —
structured as symptom → cause → fix → prevention.

## Key Concepts

### Report Structure

Every troubleshooting report should follow this flow:

1. **Symptom** — what the user sees (error message, behavior)
2. **Cause** — root cause analysis with explanation
3. **Fix** — specific remediation steps with YAML/config snippets
4. **Prevention** — how to avoid recurrence

### Operational Limits Reference

| Limit | Default | Notes |
|-------|---------|-------|
| Job timeout | 1 hour | Configurable at project/runner/job level |
| Artifact size | Instance-dependent | Monitor storage proactively |
| Runner output_limit | 4 MB | Logs truncated silently beyond this |
| `needs:` max dependencies | ~50 | Pipeline structure limit |
| `include:` depth | ~100 | Nested include limit |

<!-- TODO: Expand with full behavioral spec for troubleshooting output -->

## Examples

<!-- TODO: Expand with example troubleshooting report format -->

## Common Patterns

- Set explicit `timeout:` at job level for long-running tasks
- Monitor artifact storage usage proactively
- Use pagination for API-heavy CI operations

## Anti-Patterns

- Relying on default timeout for all job types
- Not monitoring storage quotas until exceeded
- Creating too many pipelines via API without rate awareness

## Practitioner Pain Points

- Limits differ between gitlab.com and self-managed instances
- No single page documenting all limits comprehensively
- Storage quota warnings come too late

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [../references/troubleshooting.md](../references/troubleshooting.md) — common error patterns
- [ci-architecture-review.md](ci-architecture-review.md) — architecture review output
- [../references/jobs/retry-resilience.md](../references/jobs/retry-resilience.md) — retry strategies

## Sources

- Context card: OS-2
