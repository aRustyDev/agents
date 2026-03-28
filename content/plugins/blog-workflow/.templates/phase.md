---
type: phase
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to content-brainstorm.md}}"
children: []
phase_number: {{0, 1, 2, ...}}
title: "{{Phase Title}}"
content_type: tutorial | deep-dive | experiment | explainer
template: "{{template slug}}"
persona: "{{persona slug}}"
estimated_effort: "{{X-Y hours}}"
prerequisites:
  - "{{prerequisite knowledge}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Phase {{N}}: {{Title}}

## Summary

{{What this phase will cover and why it matters}}

## Target Audience

{{Who this content is for, what they should already know}}

## Key Points

1. {{Main point one}}
2. {{Main point two}}
3. {{Main point three}}

## Code Examples Needed

| Example | Purpose | Complexity |
|---------|---------|------------|
| {{example description}} | {{what it demonstrates}} | {{simple/moderate/complex}} |

## Related Research

| Finding | From Report Section | How It Applies |
|---------|---------------------|----------------|
| {{finding}} | {{section ref}} | {{application}} |

## Dependencies

### Requires (blocks this phase)

- {{other phase or external dependency}}

### Enables (this phase blocks)

- {{phases that depend on this one}}

## Child Project

{{If this phase spawns a child project, note it here}}

- Child project: `content/_projects/{{child-slug}}/`
- Reason: {{why this needs its own project}}
