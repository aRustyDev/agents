---
description: Find MCP servers (or a suite of servers) matching a stated purpose using cache-first research
argument-hint: "<purpose>" [--refresh] [--top N]
allowed-tools: Read, Write, Bash(sqlite3:*), Bash(mkdir:*), Grep, Glob, Task, AskUserQuestion
---

# Find MCP Servers

Search for MCP servers matching a given purpose. Queries the local SQLite+FTS5 cache first, then discovers and profiles new servers from remote registries on cache miss.

## Arguments

- `$1` - Purpose description in quotes. Example: `"static analysis and linting for Python"`
- `--refresh` - Force remote registry scan even if cache has matches
- `--top N` - Number of results to return (default: 5)

## Output

Printed to conversation. Optionally written to `.plans/mcp-research/<slugified-purpose>.md` if the user wants to save it.

## Workflow

### Step 1: Initialize Cache

Ensure the SQLite cache exists:

```bash
if [ ! -f .data/mcp/registry-cache.db ]; then
  mkdir -p .data/mcp
  sqlite3 .data/mcp/registry-cache.db < .data/mcp/registry-cache.sql
fi
```

### Step 2: Extract Keywords

Parse the purpose string into search keywords:
- Strip stop words (for, and, the, a, with, etc.)
- Identify domain terms (e.g., "python", "linting", "kubernetes")
- Build an FTS5 MATCH query using OR between terms

### Step 3: Search Local Cache

Query the FTS index:

```bash
sqlite3 -json .data/mcp/registry-cache.db "
  SELECT s.id, s.name, s.slug, s.description, s.features, s.install_method,
         s.install_command, s.repository, s.stars, s.last_updated, s.language
  FROM mcp_servers s
  JOIN mcp_servers_fts f ON s.id = f.rowid
  WHERE mcp_servers_fts MATCH '<keywords>'
  ORDER BY rank
  LIMIT 20;
"
```

Also search local MCP config files:

```
Grep: settings/mcp/*.yaml for keywords
```

### Step 4: Evaluate Cache Coverage

Count enriched matches (those with `description` and `features` populated):

- **Sufficient** (>= 3 enriched matches, no `--refresh`): Skip to Step 6
- **Insufficient** (< 3 enriched, or `--refresh` flag): Proceed to Step 5

### Step 5: Remote Discovery & Enrichment

#### 5a: Discover New Servers

Spawn `mcp-registry-scanner` agent (haiku) via Task tool:

```
Read context/agents/mcp-registry-scanner.md for full agent spec.

Input:
  Domain: <keywords from purpose>
  Plugin: standalone-search
```

This scans remote registries (smithery.ai, glama.ai, pulsemcp.com, mcp.so, GitHub, etc.) and inserts new discoveries into the cache.

#### 5b: Profile Promising Servers

For each new discovery (and any shallow cache hits missing description/features), spawn `mcp-server-profiler` agents (sonnet) in parallel via Task tool:

```
Read context/agents/mcp-server-profiler.md for full agent spec.

Input (per server):
  Server: <slug>
  Plugin: standalone-search
  Need: <original purpose string>
```

Run up to 5 profilers in parallel. Each enriches the cache record with description, features, tools, install method, stars, etc.

#### 5c: Re-query Cache

After enrichment completes, re-run the FTS query from Step 3 to get updated results.

### Step 6: Rank Results

Score each match against the stated purpose:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Feature relevance | 40% | How well do the server's features match the purpose |
| Maintenance | 25% | Stars, last_updated recency, active development |
| Install ease | 20% | brew/npx > pip > docker > manual |
| Tool coverage | 15% | Number and relevance of MCP tools exposed |

Sort by total score descending. Take top N (default 5).

### Step 7: Fetch Tool Details

For the top N results, query the tools table:

```bash
sqlite3 -json .data/mcp/registry-cache.db "
  SELECT t.name, t.description
  FROM mcp_server_tools t
  WHERE t.server_id = <id>;
"
```

### Step 8: Present Results

Display results to the user:

```markdown
## MCP Server Search: "<purpose>"

### Top Matches

#### 1. <server-name> (<score>/100)

| Field | Value |
|-------|-------|
| Repository | <url> |
| Install | `<command>` |
| Language | <lang> |
| Stars | <N> |
| Last Updated | <date> |
| Features | <comma-sep> |

**Tools**: `tool1`, `tool2`, `tool3`

**Why**: <1-2 sentence justification of relevance to the stated purpose>

---

(repeat for each result)

### Summary

| Rank | Server | Score | Install | Key Strength |
|------|--------|-------|---------|--------------|
| 1    | ...    | 92    | brew    | ...          |
| 2    | ...    | 85    | npx     | ...          |

### Recommendation

<1-3 sentences: which server(s) to use, whether a single server covers the need or a suite is required, any caveats>
```

### Step 9: Offer Next Steps

Use AskUserQuestion to ask what the user wants to do:

1. **Save report** — Write to `.plans/mcp-research/<slug>.md`
2. **Profile more** — Run profiler on additional cache entries
3. **Install one** — Show install instructions for a specific server
4. **Done** — End

### Step 10: Dump Cache

If any cache modifications were made:

```bash
sqlite3 .data/mcp/registry-cache.db .dump > .data/mcp/registry-cache.sql
```

## Examples

```
/find-mcp-servers "static analysis and code quality for Python"
/find-mcp-servers "kubernetes cluster management" --top 10
/find-mcp-servers "database schema management" --refresh
/find-mcp-servers "code indexing and AST analysis"
```
