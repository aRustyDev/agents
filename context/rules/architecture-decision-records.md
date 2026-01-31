---
paths:
  - "docs/src/adr/*.md"
  - "adr-*.md"
---

# Architecture Decision Records

> **Skill**: Load `architecture-decision-records-dev` for authoring, reviewing, planning, updating, or backfilling ADRs.

## Directory & Naming

- Store ADRs in `docs/src/adr/`
- Name: `adr-NNN-title-in-kebab-case.md` (3-digit, sequential)
- Find next number: `ls docs/src/adr/ | grep -oP '\d+' | sort -n | tail -1`

## Required Sections

| Section | Purpose |
|---------|---------|
| Frontmatter | Per `frontmatter.md` rule — must include `status` field |
| Status | Proposed, Accepted, Deprecated, Superseded |
| Context | Problem statement and constraints |
| Decision | Specific, actionable choice |
| Alternatives | 2+ options with trade-offs |
| Consequences | Positive, negative, neutral |
| Diagram | At least one Mermaid diagram |

## Rules

1. **One decision per ADR** — keep scope focused
2. **Document the "why"** — rationale matters more than the "what"
3. **Never edit accepted ADRs** — write a new ADR that supersedes
4. **Be specific** — no placeholders, no hand-waving
5. **Include honest trade-offs** — every choice has downsides
6. **Title in imperative mood** — "Use X for Y", not "X was chosen"

## Status Lifecycle

```
Proposed → Accepted → [Deprecated | Superseded by ADR-NNN]
         → Withdrawn
```

When superseding: update old ADR status to `Superseded by ADR-NNN` and reference the old ADR in the new one.
