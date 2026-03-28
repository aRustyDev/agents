# Architecture Decision Records

This section documents key architectural decisions made for the blog-workflow plugin.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help future maintainers understand why decisions were made.

## ADR Index

| # | Title | Status | Date |
|---|-------|--------|------|
| [0001](./0001-record-architecture-decisions.md) | Record Architecture Decisions | Accepted | 2026-03-16 |
| [0002](./0002-post-type-taxonomy.md) | Post Type Taxonomy Design | Accepted | 2026-03-16 |

## Creating New ADRs

Use the `adrs` CLI:

```bash
cd docs/src/adrs
adrs new "Decision Title"
```

Or create manually following the format in existing ADRs.

## ADR Status Values

| Status | Meaning |
|--------|---------|
| Proposed | Under consideration |
| Accepted | Decision made and active |
| Deprecated | No longer applies but kept for history |
| Superseded | Replaced by another ADR |

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Michael Nygard's Original Article](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
