# ADR Template

Complete MADR template with aRustyDev frontmatter conventions.

## Template

```markdown
---
id: <uuidv4>
project:
  id: <project-uuid>
title: "ADR-NNN: <Title in Imperative Mood>"
status: proposed
tags: [adr, <domain>]
related:
  supersedes: []
  depends-on: []
---

# ADR-NNN: <Title>

## Status

Proposed

## Date

YYYY-MM-DD

## Deciders

- <name/role>

## Context and Problem Statement

<What situation necessitates this decision? Include:>
- Current state and its limitations
- Constraints (technical, organizational, timeline)
- Why this decision is needed now

## Decision Drivers

- <Driver 1 — most important first>
- <Driver 2>
- <Driver 3>

## Considered Options

### Option 1: <Name>

<Description>

| Pros | Cons |
|------|------|
| <benefit> | <trade-off> |
| <benefit> | <trade-off> |

### Option 2: <Name>

<Description>

| Pros | Cons |
|------|------|
| <benefit> | <trade-off> |
| <benefit> | <trade-off> |

## Decision Outcome

Chose **Option N: <Name>** because <rationale linking back to decision drivers>.

### Confirmation

<How will we know this decision is working? Metrics, signals, review date.>

## Diagram

` ``mermaid
<at least one diagram showing the decision's architectural impact>
` ``

## Consequences

### Positive

- <benefit>

### Negative

- <trade-off — every decision has downsides>

### Neutral

- <observation that is neither good nor bad>

## References

- [Related ADR](./adr-NNN-title.md)
- [INVESTIGATE: <gap to fill later>]
```

## Frontmatter Field Reference

| Field | Required | Source |
|-------|----------|--------|
| `id` | Yes | Generate with `uuidgen` |
| `project.id` | Yes | From `git config project.id` or git note on root commit |
| `title` | Yes | `"ADR-NNN: <Imperative Title>"` |
| `status` | Yes | `proposed` for new ADRs |
| `tags` | Yes | Always include `adr` + domain tag |
| `related.supersedes` | If applicable | UUID of replaced ADR |
| `related.depends-on` | If applicable | UUID of prerequisite ADR |

## Section Guidance

| Section | Length | Key Question |
|---------|--------|--------------|
| Context | 3-8 sentences | Why is this decision needed now? |
| Decision Drivers | 3-6 items | What factors matter most? |
| Considered Options | 2+ options | What alternatives exist? |
| Decision Outcome | 2-4 sentences | What was chosen and why? |
| Diagram | 1+ diagrams | What does this change architecturally? |
| Consequences | 3+ items | What are the trade-offs? |

## Diagram Types by Decision

| Decision Type | Suggested Diagram |
|---------------|-------------------|
| Component selection | C4 component diagram |
| Data flow change | Flowchart or sequence diagram |
| API design | Class or ER diagram |
| Infrastructure | Deployment diagram |
| Process change | State or activity diagram |
