---
description: Generate beads issues for each create/extend item in a plugin roadmap
argument-hint: <roadmap-path> [--dry-run]
allowed-tools: Read, Bash(bd:*), Bash(ls:*), AskUserQuestion
---

# Generate Plugin Issues

Create beads issues for each **Create** and **Extend** item in a plugin roadmap. Each issue gets proper labels and dependency relationships.

## Arguments

- `$1` - Path to roadmap document. Example: `.plans/plugins/terraform-dev/roadmap.md`
- `--dry-run` - Print issue previews without creating them

## Output

Created beads issue IDs (or previews in dry-run mode).

## Workflow

### Step 1: Parse Roadmap

1. Read the roadmap at `$1`
2. Extract plugin name from the document title
3. Parse all **Extend** and **Create** items from P0, P1, P2 sections
4. For each item, extract: component name, type, priority, description, dependencies

### Step 2: Build Issue List

For each item, prepare:

```
Title: [<plugin-name>] <Action> <type>: <component-name>
Body:
  ## Context
  Plugin: <plugin-name>
  Priority: <P0|P1|P2>
  Action: <extend|create>

  ## Description
  <description from roadmap>

  ## Gap (extend only)
  <gap description>

  ## Acceptance Criteria
  - [ ] Component implemented
  - [ ] Tests passing
  - [ ] Documentation updated
  - [ ] Integrated into plugin

Labels:
  - plugin:<plugin-name>
  - type:<skill|command|agent|style|hook|mcp|lsp>
  - priority:<p0|p1|p2>
  - action:<extend|create>

Blocks: <issues for components that depend on this one>
```

### Step 3: Resolve Dependencies

Walk the dependency graph from the roadmap:
- If component-a depends on component-b, then component-b's issue **blocks** component-a's issue
- Create issues in dependency order (dependencies first) so `--blocks` IDs are available

### Step 4: Create Issues

If `--dry-run`:
- Print each issue preview in a formatted table
- Show dependency relationships
- Report total issue count

If not dry-run, for each issue in dependency order:

```bash
bd create --title "<title>" --body "<body>" --label "plugin:<name>" --label "type:<type>" --label "priority:<pN>" --label "action:<action>"
```

For issues with dependencies, add `--blocks <id>` referencing the dependent issue IDs.

### Step 5: Report

```
## Issues Generated

| # | Title | Priority | Labels | Blocks |
|---|-------|----------|--------|--------|
| 1 | ...   | P0       | ...    | #3, #5 |
| 2 | ...   | P0       | ...    | —      |

**Total**: N issues created (N P0, N P1, N P2)
```

If `--dry-run`:
```
## Issue Preview (dry run)

N issues would be created. Re-run without --dry-run to create them.
```

## Examples

```
/generate-plugin-issues .plans/plugins/terraform-dev/roadmap.md --dry-run
/generate-plugin-issues .plans/plugins/terraform-dev/roadmap.md
/generate-plugin-issues .plans/plugins/rust-projects/roadmap.md
```
