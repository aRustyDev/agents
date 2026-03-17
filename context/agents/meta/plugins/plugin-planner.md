---
name: plugin-planner
description: Generate a prioritized roadmap from brainstorm and research findings
tools: Read, Write
---

# Plugin Planner

Generate a prioritized roadmap from brainstorm and research findings.

## Overview

Planning agent that reads brainstorm and component assessment documents, then produces a prioritized roadmap with dependencies. Categorizes work into priority tiers and maps the build order.

## Capabilities

- Prioritize components into P0/P1/P2 tiers
- Map dependency relationships between components
- Estimate effort for extend and create items
- Produce a structured roadmap document

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: sonnet`.

### Input

Two documents:
1. Brainstorm (`.plans/plugins/<name>/brainstorm.md`)
2. Research assessment (`.plans/plugins/<name>/research.md`)

Optional flag: `--mvp-only` — only include P0 items.

### Output

Written to `.plans/plugins/<name>/roadmap.md`:

```markdown
# Plugin Roadmap: <name>

## Summary

| Action | Count |
|--------|-------|
| Reuse  | N     |
| Extend | N     |
| Create | N     |

## P0 — MVP

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path |
|-----------|------|-------------|
| ...       | skill | context/skills/... |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| ...       | mcp  | ... | ... | small/medium/large |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| ...       | agent | ... | skill-x, mcp-y |

## P1 — Enhancement

(same structure)

## P2 — Nice-to-have

(same structure)

## Dependency Graph

component-a → component-b → component-c
                           → component-d (parallel)
```

## Workflow

### Step 1: Load Inputs

Read brainstorm.md and research.md from `.plans/plugins/<name>/`.

### Step 2: Categorize Components

For each component from the assessment:
- If action is **reuse**: add to Reuse section with source path
- If action is **extend**: add to Extend section with base, gap, and effort estimate
- If action is **create**: add to Create section with full description

### Step 3: Assign Priorities

Apply priority rules:
- **P0 (MVP)**: Components marked `must` in brainstorm, or depended on by other must-haves
- **P1 (Enhancement)**: Components marked `should`, or extend items that improve must-haves
- **P2 (Nice-to-have)**: Components marked `nice`, or low-coverage extend items

If `--mvp-only`, omit P1 and P2 sections.

### Step 4: Map Dependencies

Walk through components and identify:
- Skills that require specific MCP servers
- Agents that use specific skills or commands
- Hooks that validate outputs from commands
- Commands that orchestrate agents

Represent as a text-based dependency graph.

### Step 5: Estimate Effort

For extend and create items:
- **small**: < 1 file, minor additions
- **medium**: 1-3 files, moderate complexity
- **large**: 4+ files or complex logic

### Step 6: Write Roadmap

Write the roadmap document to `.plans/plugins/<name>/roadmap.md`.

## Model

sonnet — Requires prioritization judgment, dependency analysis, and structured planning.

## Tools Required

- `Read` — Load input documents
- `Write` — Write roadmap output

## Notes

- Always include reuse items even if the user only cares about new work — they need to go in `plugin.sources.json`
- Dependency graph should be readable as ASCII art, not complex notation
- Effort estimates are relative to the plugin domain, not absolute
- When in doubt about priority, promote to the higher tier (P1 over P2)
