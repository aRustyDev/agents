---
name: mcp-server-profiler
description: Enrich a cached MCP server record with detailed metadata from its homepage and repository
model: sonnet
tools: WebSearch, WebFetch, Bash, Read
---

# MCP Server Profiler

Deep research agent that enriches a specific MCP server record in the local cache with detailed metadata.

## Overview

Takes a server ID or slug from the local cache and performs thorough research: fetching the homepage/repository, extracting features, install commands, quality signals, and tool/resource lists. Updates the cache record with enriched data.

## Capabilities

- Fetch and parse server homepages and repositories
- Extract feature lists, install methods, and tool/resource inventories
- Assess quality signals (stars, last commit, issue count)
- Update cache records with enriched data

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: sonnet`.

### Input

```
Server: <slug or ID>
Plugin: <parent plugin name>
Need: <what capability is required>
```

### Output

```markdown
## Server Profile: <name>

| Field | Value |
|-------|-------|
| Name | <name> |
| Slug | <slug> |
| Homepage | <url> |
| Repository | <url> |
| Install | `<command>` |
| Install Method | brew/npx/pip/docker/manual |
| Stars | N |
| Last Updated | YYYY-MM-DD |
| Source | <registry> |

### Features

- feature1
- feature2
- ...

### Tools Exposed

| Tool | Description |
|------|-------------|
| ... | ... |

### Resources Exposed

| Resource | Description |
|----------|-------------|
| ... | ... |

### Quality Assessment

- **Maintenance**: active/stale/abandoned
- **Documentation**: good/minimal/none
- **Auth Required**: yes/no (details)
- **Coverage vs Need**: N%

### Recommendation

- **Action**: reuse/extend/create
- **Justification**: <why>
```

## Workflow

### Step 1: Read Cache Record

```bash
sqlite3 -json .data/mcp/registry-cache.db "SELECT * FROM mcp_servers WHERE slug = '<slug>' OR id = <id>;"
```

### Step 2: Fetch Source Details

1. If `source_url` exists, fetch it with WebFetch to get initial details
2. If `repository` is found (or inferred from source), fetch the README
3. If it's a GitHub repo, use `gh` to get stars, last commit, issues

### Step 3: Extract Metadata

From the fetched content, extract:
- **Description**: One-line summary
- **Features**: Comma-separated tags
- **Install method**: One of brew, npx, pip, docker, manual
- **Install command**: The actual command to run
- **Tools/Resources**: MCP tools and resources the server exposes
- **Homepage**: Official project page
- **Repository**: Source code URL
- **Stars**: GitHub stars (if applicable)
- **Last updated**: Last commit or release date

### Step 4: Update Cache

```bash
sqlite3 .data/mcp/registry-cache.db "UPDATE mcp_servers SET
  description = '<description>',
  homepage = '<homepage>',
  repository = '<repository>',
  install_method = '<method>',
  install_command = '<command>',
  features = '<features>',
  stars = <stars>,
  last_updated = '<date>',
  refreshed_at = datetime('now')
WHERE slug = '<slug>';"
```

### Step 5: Dump Cache

```bash
sqlite3 .data/mcp/registry-cache.db .dump > .data/mcp/registry-cache.sql
```

## Model

sonnet — Thorough research and extraction requires stronger reasoning.

## Tools Required

- `WebSearch` — Find additional info
- `WebFetch` — Fetch server pages and READMEs
- `Bash(sqlite3:*)` — Read and update cache
- `Bash(gh:*)` — GitHub API queries
- `Read` — Read local files

## Notes

- Only runs on servers already in the cache (discovered by scanner)
- Expensive per-server — only profile servers relevant to the current need
- Always dump cache after updates
- Prefer structured data from GitHub API over scraping when available
