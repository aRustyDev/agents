---
name: ci-architecture-review-output
description: Behavioral spec for architecture reviews — pipeline graph, optimization recs, security audit
---

# CI Architecture Review Output

> **Scope:** Behavioral spec for architecture reviews — pipeline graph, optimization recs, security audit
> **Source cards:** OS-4
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Use this output format when asked to review, analyze, or assess a GitLab CI/CD
pipeline architecture. Produces a structured report with pipeline visualization,
optimization recommendations, and security observations.

## Output Structure

When generating a CI architecture review, follow this structure:

### 1. Pipeline Overview

- **Pipeline type** (basic, DAG, parent-child, multi-project)
- **Total stages and jobs** with counts
- **Trigger sources** (push, MR, schedule, API)
- **Estimated execution time** (parallel vs sequential)

### 2. Architecture Diagram

Render as a text-based stage→job flow:

```
[build] ──┬── [test:unit] ──┬── [deploy:staging] ── [deploy:production]
           │                    │
           ├── [test:integration] ┘
           │
           └── [test:e2e]
```

Include:
- `needs:` dependency arrows for DAG pipelines
- Parallel jobs and matrix expansions
- Downstream/child pipeline triggers
- Manual gate indicators

### 3. Configuration Quality Assessment

Evaluate across these dimensions:

| Dimension | Check |
|-----------|-------|
| **DRY** | Use of extends/includes/components vs duplication |
| **Security** | Secrets handling, protected branches, scanning |
| **Performance** | Caching, interruptible, needs: for DAG |
| **Reliability** | Retry strategies, timeout settings, allow_failure |
| **Maintainability** | File organization, naming, documentation |

### 4. Optimization Recommendations

Organize by impact:

- **High impact** — changes that significantly reduce pipeline time or cost
- **Medium impact** — improvements to reliability or maintainability
- **Low impact** — best-practice alignment and cleanup

Each recommendation should include:
- What to change and why
- Before/after YAML snippet
- Expected improvement (time, cost, reliability)

### 5. Security Observations

- Secrets exposure risks
- Missing scanning stages
- Privileged container usage
- Unprotected deployment paths

### 6. Summary Table

| Area | Status | Priority |
|------|--------|----------|
| Performance | ⚠️ Needs work | High |
| Security | ✅ Good | — |
| Maintainability | ⚠️ Needs work | Medium |
| Reliability | ✅ Good | — |

<!-- TODO: Expand with scoring rubric and severity levels -->

## Tone & Style Guidelines

- **Factual, not prescriptive** — explain trade-offs, don't just dictate
- **Link to reference docs** — cite specific skill docs for recommended patterns
- **Concrete examples** — show before/after YAML, not abstract advice
- **Prioritized** — high-impact items first, don't bury critical issues

## Examples

See [../examples/map-pipeline.md](../examples/map-pipeline.md) for a real-world review example.

## Common Patterns

- Start with pipeline overview for context before diving into details
- Group findings by dimension for scannable output
- Include estimated time/cost savings with optimization recommendations
- Reference specific line numbers in the analyzed pipeline

## Anti-Patterns

- Listing every possible optimization without prioritization
- Generic advice not specific to the analyzed pipeline
- Missing security review section
- Not providing actionable YAML fixes

## Related Topics

- [../references/pipelines/optimization.md](../references/pipelines/optimization.md) — optimization strategies
- [../references/pipelines/security.md](../references/pipelines/security.md) — pipeline security
- [../references/yaml/yaml-composition.md](../references/yaml/yaml-composition.md) — DRY patterns
- [../references/troubleshooting.md](../references/troubleshooting.md) — debugging common issues

## Sources

- Context card: OS-4

