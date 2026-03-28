---
description: Research existing components that match brainstormed plugin needs
argument-hint: <brainstorm-path>
allowed-tools: Read, Write, Glob, Grep, Bash(mkdir:*), Bash(ls:*), Bash(ccpm:*), Bash(gh:*), WebSearch, WebFetch, Task, AskUserQuestion
---

# Research Plugin Components

Search local and remote registries for existing components that match brainstormed plugin needs. Uses parallel researcher agents for speed.

## Arguments

- `$1` - Path to brainstorm document. Example: `.plans/plugins/terraform-dev/brainstorm.md`

## Output

`.plans/plugins/<plugin-name>/research.md`

## Workflow

### Step 1: Parse Brainstorm

1. Read the brainstorm document at `$1`
2. Extract plugin name from the document title
3. Parse all components from each category table (name, purpose, priority)
4. Create output directory: `mkdir -p .plans/plugins/<plugin-name>/`

### Step 2: Search for Existing Plugins

Search `content/plugins/` for plugins in the same domain:

```text
Glob: content/plugins/*/README.md
Glob: content/plugins/*/.claude-plugin/plugin.json
```

Assess overlap with the brainstormed plugin.

### Step 3: Research Components in Parallel

Launch parallel research agents using the Task tool. Group by component type:

#### Skills (parallel, one per skill)

For each skill in the brainstorm, spawn a `plugin-skill-researcher` agent (haiku):

- Search `content/skills/` locally
- Search ccpm registry
- Search claude-plugins.dev

#### MCP Servers (parallel, one per server)

For each MCP server in the brainstorm, spawn a `plugin-mcp-researcher` agent (haiku):

- Query knowledge graph first (`.data/mcp/knowledge-graph.db`)
- On cache miss, the researcher spawns `mcp-registry-scanner` (haiku) for remote discovery
- For promising new finds, spawns `mcp-server-profiler` (sonnet) to enrich records
- Knowledge graph is dumped via `just kg-dump` after any changes

Ensure the knowledge graph is initialized before spawning researchers:

```bash
if [ ! -f .data/mcp/knowledge-graph.db ]; then
  just kg-init && just kg-load
fi
```

#### Commands (sequential, local only)

Search `content/commands/` for matching commands:

```text
Grep: content/commands/*.md for relevant keywords
```

#### Agents (sequential, local only)

Search `content/agents/` for matching agents:

```text
Grep: content/agents/*.md for relevant keywords
```

#### Output Styles (sequential, local only)

Search `content/output-styles/` for matching styles:

```text
Glob: content/output-styles/*.md
```

#### Hooks (sequential, local only)

Search `content/hooks/` for matching hooks:

```text
Glob: content/hooks/*
```

#### LSP Servers (sequential)

Search GitHub for LSP servers matching the domain:

```text
WebSearch: "<domain> LSP server language server protocol"
```

### Step 4: Assess Components

Spawn a `plugin-component-assessor` agent (sonnet) with the brainstorm and all research results. It produces a unified assessment with coverage scores and reuse/extend/create recommendations.

### Step 5: Write Research Report

Write to `.plans/plugins/<plugin-name>/research.md`:

```markdown
# Plugin Research: <name>

## Existing Plugins

| Plugin | Domain | Coverage | Recommendation |
|--------|--------|----------|----------------|
| ...    | ...    | N%       | reference/merge |

## Component Research

### Skills

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| ...  | ...      | local  | 80%      | reuse  |

### Commands

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| ...  | ...      | local  | 60%      | extend |

### Agents

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| ...  | ...      | local  | 0%       | create |

### Output Styles

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|

### Hooks

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|

### MCP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| ...  | ...      | smithery | 90%   | reuse  |

### LSP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|

## Summary

- **Reuse**: N components
- **Extend**: N components
- **Create**: N components
```

### Step 6: Report

```text
## Research Complete

| Field | Value |
|-------|-------|
| Plugin | <name> |
| Output | .plans/plugins/<name>/research.md |
| Reuse | N components |
| Extend | N components |
| Create | N components |

**Next step**: `/plan-plugin-roadmap .plans/plugins/<name>/research.md`
```

## Examples

```text
/research-plugin-components .plans/plugins/terraform-dev/brainstorm.md
/research-plugin-components .plans/plugins/rust-projects/brainstorm.md
```
