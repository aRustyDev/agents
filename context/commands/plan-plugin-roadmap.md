---
description: Generate a prioritized roadmap from brainstorm and research findings
argument-hint: <research-path> [--mvp-only]
allowed-tools: Read, Write, Bash(mkdir:*), Task
---

# Plan Plugin Roadmap

Read brainstorm and research documents, then produce a prioritized roadmap with dependency mapping.

## Arguments

- `$1` - Path to research document. Example: `.plans/plugins/terraform-dev/research.md`
- `--mvp-only` - Only include P0 (must-have) components in the roadmap

## Output

`.plans/plugins/<plugin-name>/roadmap.md`

## Workflow

### Step 1: Locate Inputs

1. Read research document at `$1`
2. Derive plugin name and directory from path
3. Read brainstorm document from same directory: `.plans/plugins/<plugin-name>/brainstorm.md`
4. Validate both documents exist and are well-formed

### Step 2: Generate Roadmap

Spawn a `plugin-planner` agent (sonnet) with:
- The brainstorm document
- The research document
- The `--mvp-only` flag if present

The agent produces the roadmap following this structure:

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
| ...       | mcp  | ... | ... | small  |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| ...       | agent | ... | skill-x, mcp-y |

## P1 — Enhancement

(same structure as P0)

## P2 — Nice-to-have

(same structure as P0)

## Dependency Graph

component-a → component-b → component-c
                           → component-d (parallel)
```

### Step 3: Write Output

Write the roadmap to `.plans/plugins/<plugin-name>/roadmap.md`.

### Step 4: Report

```
## Roadmap Complete

| Field | Value |
|-------|-------|
| Plugin | <name> |
| Output | .plans/plugins/<name>/roadmap.md |
| P0 items | N (N reuse, N extend, N create) |
| P1 items | N |
| P2 items | N |

**Next steps**:
1. Review the roadmap and adjust priorities if needed
2. `/scaffold-plugin <name> .plans/plugins/<name>/roadmap.md`
3. `/generate-plugin-issues .plans/plugins/<name>/roadmap.md`
```

## Examples

```
/plan-plugin-roadmap .plans/plugins/terraform-dev/research.md
/plan-plugin-roadmap .plans/plugins/rust-projects/research.md --mvp-only
```
