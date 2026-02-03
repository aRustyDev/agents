---
name: mcp-research
description: >-
  Discover, profile, and evaluate MCP servers for a given domain or purpose.
  Use when searching for MCP servers to add to a project, comparing server
  capabilities, enriching the local registry cache, or evaluating whether
  a server suite covers a stated need. Covers cache-first discovery,
  remote registry scanning, deep server profiling, and gap analysis.
---

# MCP Server Research

Guide for discovering, profiling, and evaluating MCP servers using the local SQLite+FTS5 registry cache and three specialized agents.

## When to Use This Skill

- Finding MCP servers for a specific domain (e.g., "code analysis", "database management")
- Profiling an MCP server to understand its tools, install method, and quality
- Comparing multiple servers to recommend the best fit
- Seeding or enriching the local registry cache
- Running the `/find-mcp-servers` slash command

## Architecture

```
┌─────────────────────┐
│  /find-mcp-servers  │  ← Slash command (entry point)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────────┐
│ plugin-mcp-researcher│────▶│ SQLite+FTS5 Cache    │
│ (orchestrator)       │     │ .data/mcp/registry-  │
└────────┬────────────┘     │ cache.db             │
         │                   └──────────────────────┘
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌─────────────┐
│Scanner │ │  Profiler    │
│(haiku) │ │  (sonnet)    │
└────────┘ └─────────────┘
```

### Components

| Component | Type | Model | Purpose |
|-----------|------|-------|---------|
| `plugin-mcp-researcher` | agent | haiku | Cache-first orchestrator — queries FTS, dispatches scanner/profiler |
| `mcp-registry-scanner` | agent | haiku | Lightweight discovery — finds NEW servers across remote registries |
| `mcp-server-profiler` | agent | sonnet | Deep enrichment — fetches README, extracts tools, updates cache |
| `/find-mcp-servers` | command | — | User-facing slash command for server discovery |

### Cache Layer

```
.data/mcp/registry-cache.db   ← SQLite+FTS5 (gitignored)
.data/mcp/registry-cache.sql  ← text dump (version controlled)
```

**Tables:**

| Table | Purpose |
|-------|---------|
| `mcp_servers` | Core server records (name, slug, description, install, stars, etc.) |
| `mcp_servers_fts` | FTS5 virtual table over name, description, features |
| `mcp_server_tools` | Tools exposed by each server |
| `mcp_server_deps` | Dependencies required by each server |
| `mcp_server_assessments` | Quality/relevance assessments per server per domain |

**Cache management:**

```bash
just mcp-cache-load    # Load DB from SQL dump
just mcp-cache-dump    # Dump DB to SQL file
just mcp-cache-stats   # Show server/tool counts
just mcp-cache-search "query"  # FTS5 search
```

## Workflow: Discovering Servers

### Step 1: Query Local Cache

Always check the cache first. Build an FTS5 MATCH query from the purpose keywords:

```bash
sqlite3 -json .data/mcp/registry-cache.db "
  SELECT s.id, s.name, s.slug, s.description, s.features,
         s.install_method, s.install_command, s.repository, s.stars
  FROM mcp_servers s
  JOIN mcp_servers_fts f ON s.id = f.rowid
  WHERE mcp_servers_fts MATCH '<keyword1> OR <keyword2>'
  ORDER BY rank
  LIMIT 20;
"
```

### Step 2: Evaluate Coverage

Count enriched matches (those with `description` AND `features` populated):

- **>= 3 enriched**: Sufficient — skip to ranking
- **< 3 enriched**: Insufficient — proceed to remote discovery

### Step 3: Remote Discovery (if needed)

Spawn `mcp-registry-scanner` (haiku) via Task tool:

```
Domain: <keywords>
Plugin: standalone-search
```

The scanner searches 24+ registries in tiered priority order, deduplicates against the cache, and inserts minimal records for new finds.

### Step 4: Deep Profiling (if needed)

For each new discovery (or shallow cache hit missing description/features), spawn `mcp-server-profiler` (sonnet) via Task tool:

```
Server: <slug>
Plugin: standalone-search
Need: <original purpose string>
```

Run up to 5 profilers in parallel. Each enriches the cache with:
- Full description and feature tags
- Install method and command
- Repository URL and stars
- Language and transport protocol
- Tools exposed (inserted into `mcp_server_tools`)
- Dependencies (inserted into `mcp_server_deps`)

### Step 5: Rank and Present

Score matches using weighted criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Feature relevance | 40% | How well do features match the stated purpose |
| Maintenance | 25% | Stars, last_updated recency, active development |
| Install ease | 20% | brew/npx > pip > docker > manual |
| Tool coverage | 15% | Number and relevance of MCP tools exposed |

## Workflow: Profiling a Single Server

When you need to deeply research one specific server:

1. Check if it exists in cache: `sqlite3 .data/mcp/registry-cache.db "SELECT * FROM mcp_servers WHERE slug='<slug>';"`
2. If not cached, insert a minimal record first
3. Spawn `mcp-server-profiler` with the slug
4. The profiler will:
   - Fetch the repository README (via `gh api` or WebSearch)
   - Extract metadata: description, features, install method, language, transport
   - Identify tools from README documentation or package manifests
   - Check quality signals: stars, forks, last commit date, open issues
   - UPDATE the cache record and INSERT tool/dep records

## Workflow: Seeding from YAML Config

When bulk-loading servers from `settings/mcp/*.yaml`:

```bash
# Read category entries from YAML
# For each entry, INSERT OR IGNORE into mcp_servers with:
#   - slug (normalized from name)
#   - source_registry (from YAML source field)
#   - source_url (from YAML url field)
# Then dump cache
sqlite3 .data/mcp/registry-cache.db .dump > .data/mcp/registry-cache.sql
```

## Registry Reference

See `reference/registries.yaml` for the full list of 24+ MCP server registries organized by tier.

### Tier 1 (always search)

- smithery.ai — Curated registry with install commands
- registry.modelcontextprotocol.io — Official MCP registry
- glama.ai — Detailed server profiles
- pulsemcp.com — Community registry
- mcp.so — Search-focused directory
- GitHub topic search (`gh search repos --topic mcp-server`)

### Tier 2 (search on cache miss)

- mcpservers.org, mcpdb.org, mcp-get.com, opentools.com, cursor.directory, lobehub.com

### Tier 3 (search if Tier 2 insufficient)

- himcp.ai, mcpmarket.com, portkey.ai, cline.bot, apitracker.io, and others

## Web Scraping for Profiling

The profiler agent needs to fetch web content (READMEs, registry pages) and convert to markdown. Available methods in priority order:

### 1. GitHub API (preferred for GitHub repos)

```bash
# Raw README — already markdown, no conversion needed
gh api repos/<owner>/<repo>/readme --jq '.content' | base64 -d

# Or via raw URL
curl -sL https://raw.githubusercontent.com/<owner>/<repo>/main/README.md
```

### 2. WebSearch (always available)

Use `site:<domain> <server-name>` queries to find registry pages. WebSearch results include summaries that often contain the key metadata.

### 3. WebFetch (when available)

Fetches URL content and converts HTML to markdown. Works for static pages. May be auto-denied in background subagents.

### 4. Firecrawl MCP (when credits available)

Most capable option — handles JS-rendered pages, returns clean markdown. Use `firecrawl_scrape` with `formats: ["markdown"]`. Falls back to other methods when credits are exhausted.

### 5. CLI Fallbacks

When MCP tools and WebFetch are unavailable:

```bash
# curl + pandoc (if installed)
curl -sL <url> | pandoc -f html -t markdown --wrap=none

# Python markdownify (if installed)
curl -sL <url> | python3 -c "import sys; from markdownify import markdownify; print(markdownify(sys.stdin.read()))"

# Jina Reader API (free tier)
curl -sL "https://r.jina.ai/<url>"
```

## Common Patterns

### Inserting a new server

```sql
INSERT INTO mcp_servers (name, slug, source_registry, source_url)
VALUES ('<name>', '<slug>', '<registry>', '<url>');
```

### Updating after profiling

```sql
UPDATE mcp_servers SET
  description = '<desc>',
  features = '<comma,separated,tags>',
  install_method = '<brew|npx|pip|docker|manual>',
  install_command = '<command>',
  repository = '<url>',
  language = '<lang>',
  stars = <N>,
  last_updated = '<ISO date>',
  refreshed_at = datetime('now')
WHERE slug = '<slug>';
```

### Inserting tools

```sql
INSERT INTO mcp_server_tools (server_id, name, description)
SELECT id, '<tool_name>', '<tool_description>'
FROM mcp_servers WHERE slug = '<slug>';
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| FTS returns no results | Keywords too specific or DB empty | Use broader terms, check `just mcp-cache-stats` |
| Profiler can't fetch README | WebFetch/firecrawl denied in subagent | Fall back to `gh api` or WebSearch |
| Firecrawl credits exhausted | API quota hit | Use `gh api`, WebSearch, or CLI fallbacks |
| Duplicate slugs on insert | Server already cached | Use `INSERT OR IGNORE` or check before inserting |
| DB locked errors | Concurrent writes from parallel agents | Run profilers sequentially or use WAL mode |
| Cache not persisted | Forgot to dump after changes | Run `just mcp-cache-dump` |

## Checklist

- [ ] Cache initialized (`just mcp-cache-load`)
- [ ] FTS query built from purpose keywords
- [ ] Cache checked before any remote calls
- [ ] Scanner spawned only on cache miss
- [ ] Profilers run in parallel (max 5)
- [ ] Cache dumped after modifications (`just mcp-cache-dump`)
- [ ] Results ranked by weighted criteria
- [ ] Tools fetched for top results

## References

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- Registry list: `reference/registries.yaml`
- Agent definitions: `context/agents/mcp-registry-scanner.md`, `context/agents/mcp-server-profiler.md`, `context/agents/plugin-mcp-researcher.md`
- Command: `context/commands/find-mcp-servers.md`
