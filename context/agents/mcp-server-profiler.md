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
sqlite3 -json .data/mcp/knowledge-graph.db "SELECT * FROM v_mcp_servers WHERE slug = '<slug>';"
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
- **Tools/Resources**: MCP tools and resources the server exposes (extract `input_schema` JSON from README tool documentation where available)
- **Homepage**: Official project page
- **Repository**: Source code URL
- **Stars**: GitHub stars (if applicable)
- **Last updated**: Last commit or release date

### Step 4: Update Cache

```bash
# Update entity content and metadata
sqlite3 .data/mcp/knowledge-graph.db "UPDATE entities SET
  content = '<description>',
  metadata = json_set(COALESCE(metadata, '{}'), '$.features', '<features>'),
  updated_at = datetime('now')
WHERE slug = '<slug>' AND entity_type = 'mcp_server';"

# Update extension fields
sqlite3 .data/mcp/knowledge-graph.db "UPDATE mcp_servers_ext SET
  homepage = '<homepage>',
  repository = '<repository>',
  install_method = '<method>',
  install_command = '<command>',
  stars = <stars>,
  last_updated = '<date>',
  refreshed_at = datetime('now')
WHERE entity_id = (SELECT id FROM entities WHERE slug = '<slug>' AND entity_type = 'mcp_server');"
```

### Step 4b: Record Assessment

If a `Need` was provided, insert a relevance assessment:

```bash
sqlite3 .data/mcp/knowledge-graph.db "INSERT INTO mcp_server_assessments
  (server_id, domain, relevance_score, coverage_pct, recommendation, notes, assessed_at)
  SELECT id, '<need>', <relevance_0_100>, <coverage_pct>, '<reuse|extend|create>',
    '<justification>', datetime('now')
  FROM entities WHERE slug = '<slug>' AND entity_type = 'mcp_server';"
```

### Step 5: Dump Knowledge Graph

```bash
just kg-dump
```

## Model

sonnet — Thorough research and extraction requires stronger reasoning.

## Tools Required

- `WebSearch` — Find additional info
- `WebFetch` — Fetch server pages and READMEs
- `Bash(sqlite3:*)` — Read and update cache
- `Bash(gh:*)` — GitHub API queries
- `Read` — Read local files

## Web Scraping Priority

When fetching server content (READMEs, registry pages), use this fallback chain in order:

1. **gh api** — `gh api repos/<owner>/<repo>/readme --jq '.content' | base64 -d` (preferred for GitHub repos)
2. **crawl4ai-mcp** — If the crawl4ai MCP server is connected, use it for JS-rendered pages
3. **trafilatura** — `trafilatura -u <url>` CLI for clean text extraction
4. **WebSearch** — `site:<domain> <server-name>` queries; results include summaries with key metadata
5. **WebFetch** — Fetches URL and converts HTML to markdown; may be denied in background subagents
6. **Jina Reader** — `curl -sL "https://r.jina.ai/<url>"` (free tier)
7. **firecrawl** — `firecrawl_scrape` with `formats: ["markdown"]`; use when credits available
8. **markdownify** — `curl -sL <url> | python3 -c "import sys; from markdownify import markdownify; print(markdownify(sys.stdin.read()))"`
9. **html2text** — `curl -sL <url> | html2text` (last resort)

## Database Schema Reference

MCP servers are stored in the unified knowledge graph:

```
entities: id, entity_type='mcp_server', slug, name, content (description),
  metadata (JSON with features), file_path, file_hash, created_at, updated_at

mcp_servers_ext: entity_id (FK), install_method (brew|npx|pip|docker|manual),
  install_command, repository, homepage, language, transport (stdio|sse|http-stream),
  stars (INT), last_updated (ISO), pricing (free|paid|freemium), pricing_notes,
  source_registry, source_url, dockerized (0|1|2), locale, config_schema (JSON),
  discovered_at, refreshed_at

v_mcp_servers: Convenience view joining entities + mcp_servers_ext

mcp_server_tools: id, server_id (FK to entities), name, description, input_schema (JSON)
mcp_server_deps: id, server_id (FK), name, kind, required, version_constraint, notes
mcp_server_assessments: id, server_id (FK), domain, relevance_score, coverage_pct,
  recommendation (reuse|extend|create), notes, has_unit_tests, has_integration_tests,
  has_e2e_tests, test_coverage_pct, test_robustness, codebase_ast, codebase_index,
  codebase_summary, assessed_at
```

## Notes

- Only runs on servers already in the cache (discovered by scanner)
- Expensive per-server — only profile servers relevant to the current need
- Always dump cache after updates
- Prefer structured data from GitHub API over scraping when available
