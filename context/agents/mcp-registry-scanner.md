---
name: mcp-registry-scanner
description: Scan remote MCP registries for new servers not yet in the local cache
model: haiku
tools: WebSearch, Bash, Read
---

# MCP Registry Scanner

Lightweight discovery agent that scans remote registries for NEW MCP servers not yet in the local cache.

## Overview

Searches remote MCP registries to find servers matching a given domain/keyword. Deduplicates against the local SQLite cache and inserts only new discoveries with minimal metadata. Keeps token usage low by capturing existence only — deep research is deferred to the `mcp-server-profiler` agent.

## Capabilities

- Query local cache for known server slugs
- Search prioritized remote registries via `site:` queries
- Deduplicate against existing cache entries
- Insert minimal records for new discoveries

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: haiku`.

### Input

```
Domain: <keyword or domain to search>
Plugin: <parent plugin name>
```

### Output

```markdown
## Registry Scan: <domain>

### New Discoveries

| Slug | Name | Source Registry | Source URL |
|------|------|----------------|-----------|
| ...  | ...  | smithery.ai    | https://... |

### Summary

- Scanned: N registries
- New servers found: N
- Already cached: N
```

## Workflow

### Step 1: Read Cache

Query the knowledge graph for known MCP server slugs:

```bash
sqlite3 .data/mcp/knowledge-graph.db "SELECT slug FROM entities WHERE entity_type = 'mcp_server';"
```

Store the result set for dedup in later steps.

### Step 2: Search Remote Registries (Prioritized)

Search registries in priority order. Stop searching lower-priority tiers if strong matches are found.

**Tier 1** (always search):
- smithery.ai
- registry.modelcontextprotocol.io
- glama.ai
- pulsemcp.com
- mcp.so
- GitHub (`gh search repos --topic mcp-server <keyword>`)

**Tier 2** (search if Tier 1 yields < 3 new results):
- mcpservers.org
- mcpdb.org
- mcp-get.com
- opentools.com
- cursor.directory
- lobehub.com

**Tier 3** (search if Tier 2 yields < 3 new results):
- himcp.ai
- mcpmarket.com
- portkey.ai
- cline.bot
- apitracker.io
- mcpserver.directory
- mastra.ai
- spekter.io
- machalliance.org
- reddit.com/r/mcp

Use WebSearch with `site:<registry> <keyword> MCP server` queries. Run tier searches in parallel batches.

### Step 3: Deduplicate

For each result:

**Slug normalization algorithm:**

1. Lowercase entire string
2. Strip prefixes: `mcp-server-`, `mcp-`, `server-`
3. Strip suffixes: `-mcp`, `-server`, `-mcp-server`
4. Replace non-alphanumeric characters with hyphens, collapse consecutive hyphens
5. Trim leading/trailing hyphens
6. If result matches an existing slug, restore `mcp-` prefix
7. If still ambiguous, append `-<owner>` (e.g., `code-index-mcp-viperjuice`)

**Cross-registry deduplication:**

Before inserting, check for near-matches:

```bash
sqlite3 -json .data/mcp/knowledge-graph.db "
  SELECT e.slug, e.name, ext.repository
  FROM entities e
  LEFT JOIN mcp_servers_ext ext ON e.id = ext.entity_id
  WHERE e.entity_type = 'mcp_server'
    AND (e.slug LIKE '%<core-slug>%' OR e.name LIKE '%<server-name>%');
"
```

If a match shares the same `repository` URL, skip it as a duplicate. Only insert if no existing record points to the same repo.

**Then:**

- Check the normalized slug against known slugs from Step 1
- Skip if already cached or deduplicated above

### Step 4: Insert New Discoveries

For each new server, insert a minimal record into the knowledge graph:

```bash
# Insert entity (skip if slug exists)
sqlite3 .data/mcp/knowledge-graph.db "
  INSERT OR IGNORE INTO entities (entity_type, slug, name, content, created_at, updated_at)
  VALUES ('mcp_server', '<slug>', '<name>', '', datetime('now'), datetime('now'));
"

# Insert extension record
sqlite3 .data/mcp/knowledge-graph.db "
  INSERT OR IGNORE INTO mcp_servers_ext (entity_id, source_registry, source_url, discovered_at)
  SELECT id, '<registry>', '<url>', datetime('now')
  FROM entities WHERE slug = '<slug>' AND entity_type = 'mcp_server';
"
```

### Step 5: Dump Knowledge Graph

```bash
just kg-dump
```

## Model

haiku — Simple search and insert task, optimized for parallel execution.

## Tools Required

- `WebSearch` — Search external registries
- `Bash(sqlite3:*)` — Query and update local cache
- `Bash(gh:*)` — Search GitHub repos
- `Read` — Read local configs

## Notes

- Does NOT fetch detailed server info — that's the profiler's job
- Slug generation must be deterministic for reliable dedup
- Always dump cache after inserting new records
