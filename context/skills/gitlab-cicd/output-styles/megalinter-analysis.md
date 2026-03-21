---
name: megalinter-analysis-output
description: Behavioral spec for formatting MegaLinter results — severity grouping, fix suggestions, config references
---

# MegaLinter Analysis Output

> **Scope:** Behavioral spec for formatting MegaLinter results — severity grouping, fix suggestions, config references
> **Source cards:** OS-1
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Use this output format when analyzing MegaLinter CI job results —
grouping findings by severity, suggesting fixes, and linking to config references.

<!-- TODO: Expand with full behavioral spec for MegaLinter output formatting -->

## Key Concepts

- Group lint findings by **severity** (error → warning → info)
- Organize by **linter** (language/tool) for actionable grouping
- Include **fix suggestions** with code snippets
- Link to **MegaLinter config references** for disabling/customizing rules
- Summarize **overall health** with pass/fail counts

<!-- TODO: Expand with output template structure and severity mapping -->

## Examples

<!-- TODO: Expand with example MegaLinter output format -->

## Common Patterns

- Severity-grouped findings with counts
- Auto-fix suggestions where available
- Config file references for rule customization

## Anti-Patterns

- Listing every finding without grouping or prioritization
- Missing severity context
- No fix suggestions

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [ci-architecture-review.md](ci-architecture-review.md) — architecture review output format
- [../references/troubleshooting.md](../references/troubleshooting.md) — debugging CI/CD issues

## Sources

- Context card: OS-1
