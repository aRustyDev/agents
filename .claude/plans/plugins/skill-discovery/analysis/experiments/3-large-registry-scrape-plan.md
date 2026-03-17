# Experiment 3: Large Registry Scrape Plan

## Metadata

```yaml
experiment:
  id: "exp-003-large-registry-scrape"
  title: "Systematic scraping of large component registries"
  created: "2026-03-09"
  updated: "2026-03-09"
  status: "approved"
```

## Objective

Systematically scrape large component registries:
- skillsmp.com (414K+ skills) - API available
- smithery.ai (125K+ skills, 3.8K servers) - crawl4ai
- mcpservers.org (6.5K servers) - crawl4ai
- buildwithclaude.com (11K+ components) - crawl4ai / GitHub clone

**Dropped:** glama.ai (MCP servers are user-specific, not open source)

## Tool Selection (Approved)

| Registry | Method | Rationale |
|----------|--------|-----------|
| skillsmp.com | API | Documented at /docs/api |
| smithery.ai | crawl4ai | Pagination works |
| mcpservers.org | crawl4ai | Pagination works |
| buildwithclaude.com | crawl4ai / GitHub | Static pages, source repo available |

## Phase 0: Split Existing Data (FIRST)

Before scraping more, split existing `components.json` by source into raw files.

```bash
# Split current components.json into per-source raw files
python3 scripts/split-components-by-source.py
```

**Output structure:**
```
/meilisearch/indices/
├── components.json              # Will become gold tier (empty initially)
├── components-silver.json       # Verified components
└── raw/
    ├── awesome-modelcontextprotocol-servers.ndjson
    ├── awesome-punkpeye-awesome-mcp-servers.ndjson
    ├── awesome-wong2-awesome-mcp-servers.ndjson
    ├── awesome-anthropics-anthropic-cookbook.ndjson
    ├── mcp-so.ndjson
    ├── github.ndjson
    ├── buildwithclaude-com.ndjson
    ├── mcpservers-org.ndjson
    ├── smithery-ai.ndjson
    ├── skillsmp-com.ndjson
    └── claudemarketplaces.ndjson
```

## Phase 1: Pagination-Based Scraping (crawl4ai)

### mcpservers.org

```yaml
registry: mcpservers.org
total: 6523
per_page: 30
pages: 218
batches: 11 (20 URLs per batch)
estimated_time: 15 minutes
```

```python
# Batch URLs for crawl4ai
for batch_start in range(1, 219, 20):
    batch_end = min(batch_start + 19, 218)
    urls = [f"https://mcpservers.org/all?sort=newest&page={i}"
            for i in range(batch_start, batch_end + 1)]
    # crawl4ai call with urls
```

### smithery.ai/servers

```yaml
registry: smithery.ai/servers
total: 3807
per_page: ~20
pages: ~191
batches: 10
estimated_time: 15 minutes
```

### smithery.ai/skills

```yaml
registry: smithery.ai/skills
total: 125357
per_page: ~20
pages: ~6268
batches: 314
estimated_time: ~5 hours (with rate limiting)
note: Consider sampling strategy - crawl first 1000 pages initially
```

### buildwithclaude.com

```yaml
registry: buildwithclaude.com
sections:
  - /plugins (8089)
  - /skills (161)
  - /subagents (117)
  - /commands (175)
  - /hooks (28)
  - /mcp-servers (2824)
alternative: Clone https://github.com/davepoon/buildwithclaude
estimated_time: 30 minutes (crawl) or 5 minutes (git clone)
```

## Phase 2: API-Based Scraping

### skillsmp.com

```yaml
registry: skillsmp.com
total: 414701
api_docs: https://skillsmp.com/en/docs/api
estimated_time: TBD after API investigation
note: Verify rate limits before bulk retrieval
```

## Output Specification

Each raw file uses NDJSON format:

```json
{
  "id": "skillsmp_openclaw-router",
  "name": "acp-router",
  "type": "skill",
  "description": "Route plain-language requests...",
  "author": "openclaw",
  "canonical_url": "https://skillsmp.com/skills/...",
  "github_url": "https://github.com/openclaw/openclaw",
  "star_count": 0,
  "source_type": "registry",
  "source_name": "skillsmp.com",
  "source_url": "https://skillsmp.com",
  "tags": [],
  "discovered_at": "2026-03-09T12:00:00Z",
  "quality_tier": "bronze",
  "scrape_metadata": {
    "page": 1,
    "position": 5,
    "scraped_at": "2026-03-09T12:00:00Z"
  }
}
```

## Success Criteria

| Registry | Minimum | Target | Status |
|----------|---------|--------|--------|
| skillsmp.com | 10,000 | 100,000 | Pending |
| smithery.ai (skills) | 5,000 | 50,000 | Pending |
| smithery.ai (servers) | 2,000 | 3,800 | Pending |
| mcpservers.org | 2,000 | 6,500 | Pending |
| buildwithclaude.com | 500 | 11,000 | Pending |

## Execution Order

1. **Phase 0:** Split existing components.json (now)
2. **Phase 1a:** mcpservers.org (straightforward pagination)
3. **Phase 1b:** smithery.ai/servers (3.8K, manageable)
4. **Phase 1c:** buildwithclaude.com (clone repo or crawl)
5. **Phase 1d:** smithery.ai/skills (sample first 1000 pages)
6. **Phase 2:** skillsmp.com API (after rate limit verification)

## Rate Limiting

- **crawl4ai:** 2 second delay between batches
- **API calls:** Respect documented rate limits, default 1 req/sec
- **Checkpointing:** Save progress after each batch to allow resume
