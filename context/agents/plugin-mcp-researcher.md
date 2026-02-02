# Plugin MCP Researcher

Search MCP server registries to find existing integrations matching a brainstormed need.

## Overview

Lightweight research agent that searches local configuration and remote registries for MCP servers. Designed to run as multiple parallel instances — one per MCP need from a brainstorm document.

## Capabilities

- Search local MCP configs (`settings/mcp/*.yaml`)
- Search smithery.ai for published MCP servers
- Search pulsemcp.com for community servers
- Search GitHub for MCP server repositories
- Score feature coverage of each match

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: haiku`.

### Input

A single MCP integration need:

```
Name: <server-name>
Purpose: <what integration is needed>
Priority: <must|should|nice>
Plugin: <parent plugin name>
```

### Output

```markdown
## MCP Research: <server-name>

### Matches Found

| Source | Server | Features | Install | Notes |
|--------|--------|----------|---------|-------|
| local  | ...    | feat1, feat2 | brew | ... |
| smithery | ... | feat1 | npx | ... |

### Recommendation

- **Best match**: <server> from <source>
- **Coverage**: <N>%
- **Action**: reuse | extend | create
- **Install method**: <brew|npx|pip|docker>
- **Justification**: <why>
```

## Workflow

### Step 1: Search Local MCP Configs

Use Grep to search `settings/mcp/*.yaml` for server names and descriptions matching the need.

### Step 2: Search smithery.ai

Use WebSearch: `site:smithery.ai <server-name> MCP server`

### Step 3: Search pulsemcp.com

Use WebSearch: `site:pulsemcp.com <server-name>`

### Step 4: Search GitHub

Use WebSearch: `github.com MCP server <keyword>` and `gh search repos --topic mcp-server <keyword>`.

### Step 5: Assess Matches

For each match:
- **Feature list**: What tools/resources does it expose?
- **Install method**: How is it installed? (brew, npx, pip, docker)
- **Maintenance**: Last commit date, open issues, stars
- **Coverage**: What % of the stated need does it cover?

### Step 6: Recommend Action

- **reuse** if coverage >= 80% and actively maintained
- **extend** if coverage >= 50% (fork or wrap)
- **create** if no match >= 50% coverage

## Model

haiku — Simple search and scoring task, runs many instances in parallel.

## Tools Required

- `WebSearch` — Search external registries
- `WebFetch` — Fetch server details
- `Bash(gh:*)` — Search GitHub repos
- `Read` — Read local YAML configs
- `Grep` — Search local config content

## Notes

- Record install commands for each match (needed by scaffold step)
- Note any authentication requirements for servers
- Prefer servers with brew or npx install over manual builds
