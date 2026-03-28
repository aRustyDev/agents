---
name: architecture-decision-records-dev
description: >-
  Architecture Decision Record authoring, reviewing, and lifecycle management.
  Use when creating new ADRs, reviewing ADR quality, deciding what warrants
  an ADR, updating ADR status, superseding decisions, or backfilling ADRs
  from git history. Covers MADR template, E.C.A.D.R. quality criteria,
  status lifecycle, and code traceability patterns.
---

# Architecture Decision Records

Workflows for authoring, reviewing, planning, updating, and backfilling Architecture Decision Records (ADRs).

## When to Use

- Creating a new ADR for a technology or architecture decision
- Reviewing an existing ADR for quality and completeness
- Deciding whether something warrants an ADR
- Updating ADR status (accepting, deprecating, superseding)
- Backfilling undocumented decisions from git history
- Adding ADR references to code for traceability

## Workflows

### Author

When creating a new ADR.

**Process:**

1. Determine next ADR number:
   ```bash
   ls docs/src/adr/ | grep -oP '\d+' | sort -n | tail -1
   ```
2. Create file: `docs/src/adr/adr-NNN-title-in-kebab-case.md`
3. Add frontmatter (per `frontmatter.md` rule):
   ```yaml
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
   ```
4. Fill required sections (see template in `references/adr-template.md`)
5. Include at least one Mermaid diagram
6. Mark incomplete sections with INVESTIGATE markers

**Required Sections:**

| Section | Guidance |
|---------|----------|
| Status | Start with `proposed` |
| Context | Problem statement, constraints, why now |
| Decision Drivers | Prioritized factors influencing the choice |
| Considered Options | 2+ alternatives with honest trade-offs |
| Decision Outcome | Specific choice with rationale |
| Diagram | Mermaid diagram showing architectural impact |
| Consequences | Positive, negative, and neutral outcomes |

**INVESTIGATE Markers:**

For sections that cannot be filled from available information:

```markdown
- [INVESTIGATE: Confirm scaling requirements with infrastructure team]
- [INVESTIGATE: Benchmark Option 2 vs Option 3 performance]
```

These signal incomplete sections for later follow-up without blocking the ADR.

**Title Convention:**

Use imperative mood — describe the action, not the outcome:

| Good | Bad |
|------|-----|
| Use PostgreSQL for user data | PostgreSQL was chosen |
| Adopt event sourcing pattern | Event sourcing decision |
| Migrate from REST to gRPC | REST vs gRPC comparison |

### Review

Use the E.C.A.D.R. checklist when reviewing ADRs.

```markdown
## ADR Review (E.C.A.D.R.)

### Core Quality
- [ ] **E**xplicit problem statement — context clearly states the problem
- [ ] **C**omprehensive options — 2+ alternatives with trade-offs
- [ ] **A**ctionable decision — specific, implementable choice stated
- [ ] **D**ocumented consequences — positive, negative, and neutral listed
- [ ] **R**eviewable — readable by someone without current context

### Structure
- [ ] Frontmatter with id, status, project.id
- [ ] Status is valid (Proposed/Accepted/Deprecated/Superseded/Withdrawn)
- [ ] One decision per ADR
- [ ] Title in imperative mood
- [ ] At least one Mermaid diagram
- [ ] No placeholders or hand-waving
- [ ] Alternatives include honest trade-offs
- [ ] INVESTIGATE markers for known gaps (not silent omissions)

### Strategic Lenses (for significant decisions)
- [ ] Chesterton's Fence: if changing existing, original purpose documented?
- [ ] Path Dependence: irreversibility assessed, exit strategy defined?
- [ ] Second-System Effect: scope bounded, not over-engineering?
```

**Common Issues:**

| Issue | Fix |
|-------|-----|
| Vague context ("we need a database") | Add constraints, requirements, and "why now" |
| Single option presented | Add 2+ alternatives with honest pros/cons |
| Missing trade-offs | Every choice has downsides — document them |
| No diagram | Add Mermaid diagram showing architectural impact |
| Placeholder sections ("TBD") | Use INVESTIGATE markers with specific questions |
| Multiple decisions in one ADR | Split into separate, focused ADRs |
| Passive title ("Database was selected") | Use imperative mood ("Use PostgreSQL for X") |
| Missing frontmatter | Add per `frontmatter.md` rule |

### Plan

Use when deciding what needs an ADR.

**Decision Triggers:**

| Trigger | ADR? | Why |
|---------|------|-----|
| Technology choice (DB, framework, language) | Yes | Shapes system for years |
| Architectural pattern (microservices, event-driven) | Yes | Affects all future development |
| Infrastructure decision (cloud, deployment) | Yes | Lock-in implications |
| Security approach (auth, encryption) | Yes | Compliance and risk |
| API design (versioning, format) | Yes | External contract commitment |
| Build/CI pipeline architecture | Yes | Affects all contributors |
| Data model or schema design | Yes | Migration cost grows over time |
| Implementation detail (function names) | No | Too granular, easily changed |
| Temporary workaround | No | Not architectural |
| Minor tooling (linter config, editor settings) | No | Low impact, easily reversible |
| Standard library usage | No | No real alternatives |

**Scope Check:**

Before writing, verify the ADR is scoped to one decision:

- Can you state the decision in one sentence? If not, split.
- Does the ADR cover multiple independent choices? Split each into its own ADR.
- Is the decision reversible with minimal effort? Probably doesn't need an ADR.

**Timing:**

| When | Approach |
|------|----------|
| Before implementation | Ideal — decision drives the work |
| During implementation | Acceptable — capture as you learn |
| After implementation | Backfill — better late than never |

### Update

When changing ADR status or superseding decisions.

**Status Transitions:**

```
Proposed → Accepted     (team/lead approval)
Proposed → Withdrawn    (rejected before implementation)
Accepted → Deprecated   (no longer relevant, not replaced)
Accepted → Superseded   (replaced by newer ADR)
```

**Supersession Workflow:**

1. Create new ADR with the replacement decision
2. In new ADR frontmatter: `related: { supersedes: [<old-adr-uuid>] }`
3. In new ADR context: reference the old ADR and explain why it's being replaced
4. Update old ADR:
   - Change `status: superseded`
   - Add note: `Superseded by [ADR-NNN](./adr-NNN-title.md)`
5. Never delete the old ADR — it preserves decision history

**Deprecation:**

1. Update `status: deprecated`
2. Add context explaining why the decision is no longer relevant
3. No replacement ADR needed (unlike supersession)

### Backfill

When reconstructing undocumented decisions from git history.

**Process:**

1. **Classify files** by architectural significance:

   | Tier | Files | Signal Strength |
   |------|-------|-----------------|
   | 0 | Dependency manifests (Cargo.toml, package.json) | Highest — every change is a choice |
   | 1 | Infrastructure (Dockerfile, CI configs, terraform) | High — how the system runs |
   | 2 | Domain structure (core modules, entry points) | Medium — system shape |
   | 3 | Interface contracts (API schemas, protobuf) | Medium — external commitments |

2. **Identify decision commits** — look for structural changes, not edits:
   - New directory created
   - Dependency added/removed/major-bumped
   - New entry point or service
   - CI pipeline added or significantly changed

3. **Cluster related commits** into single decisions:
   - Related by intent, not just proximity
   - Typically spans days to weeks, not months
   - Should have a name you could say in a sentence ("the Redis migration")

4. **Ask for context** before generating — don't invent rationale:
   - What problem prompted this decision?
   - What alternatives were considered?
   - What trade-offs were accepted?

5. **Generate ADR** with reconstructed footer:
   ```
   ---
   *Reconstructed from commits abc123..def456 (2024-01-10 to 2024-01-12)*
   ```

**Quality Bar:**

A good backfilled ADR could have been written at the time of the decision. It captures "why", stands alone, and is honest about what's reconstructed vs confirmed.

## Quick Reference

### ADR Naming

```
docs/src/adr/adr-NNN-title-in-kebab-case.md
```

### Required Frontmatter

```yaml
---
id: <uuidv4>
project:
  id: <project-uuid>
title: "ADR-NNN: <Title>"
status: proposed  # proposed | accepted | deprecated | superseded | withdrawn
tags: [adr]
related:
  supersedes: []
  depends-on: []
---
```

### Section Quick Reference

| Section | Required | Content |
|---------|----------|---------|
| Status | Yes | Current lifecycle state |
| Context | Yes | Problem, constraints, "why now" |
| Decision Drivers | Yes | Prioritized factors |
| Considered Options | Yes | 2+ alternatives with trade-offs |
| Decision Outcome | Yes | Chosen option with rationale |
| Diagram | Yes | Mermaid showing architectural impact |
| Consequences | Yes | Positive, negative, neutral |
| References | No | Related ADRs, docs, links |

## aRustyDev Conventions

- ADRs live in `docs/src/adr/` (mdBook documentation)
- ADR format documented in CLAUDE.md under "ADR Format"
- Frontmatter follows `frontmatter.md` rule (UUIDs, project.id, status)
- Related ADRs referenced by UUID in `related:` frontmatter, not file path
- ADRs linked from issues and plans when they drive implementation decisions

## See Also

- `references/adr-template.md` — complete MADR template with frontmatter
- `references/quality-checklist.md` — full E.C.A.D.R. criteria and strategic lenses
- `references/code-traceability.md` — language-specific ADR references in code
- `references/decision-triggers.md` — detailed guidance on what warrants an ADR
- `examples/technology-selection.md` — example: choosing a CLI parsing library
- `examples/architectural-change.md` — example: adopting a new pattern
- `tables/status-lifecycle.md` — status transitions and governance
