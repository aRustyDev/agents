# Component Collection Status Report

**Generated:** 2026-03-09T18:00:00Z
**Updated:** 2026-03-09T17:55:00Z - mcpservers.org COMPLETE, smithery.ai crawl in progress

## Current State

| Metric | Value |
|--------|-------|
| Total Bronze Records | 14,077 |
| Unique Sources | 11 |
| Component Types | 6 |
| Quality Tier | Bronze (all raw) |

## By Source (Bronze Files)

| Source | Count | Status |
|--------|-------|--------|
| mcpservers.org | 8,191 | ✅ COMPLETE (125% of advertised) |
| awesome:modelcontextprotocol/servers | 1,503 | Complete |
| awesome:punkpeye/awesome-mcp-servers | 1,474 | Complete |
| mcp_so | 1,384 | 92% of target |
| awesome:wong2/awesome-mcp-servers | 533 | Complete |
| smithery.ai | 368 | 10% of advertised (~3,810) |
| github | 352 | Partial |
| buildwithclaude.com | 234 | 46% of target |
| awesome:anthropics/anthropic-cookbook | 28 | Complete |
| skillsmp.com | 9 | <1% of target |
| claudemarketplaces | 1 | - |

## By Type

| Type | Count |
|------|-------|
| mcp_server | 5,148 |
| skill | 221 |
| hook | 89 |
| plugin | 86 |
| agent | 68 |
| command | 56 |

## Known Universe (Estimated)

| Registry | Advertised | Collected | Coverage |
|----------|------------|-----------|----------|
| skillsmp.com | 414,701 | 9 | 0.002% |
| smithery.ai (skills) | 125,357 | 7 | 0.006% |
| smithery.ai (servers) | 3,810 | 368 | 9.7% |
| ~~glama.ai~~ | ~~18,503~~ | ~~0~~ | DROPPED |
| buildwithclaude.com | 11,394 | 234 | 2.05% |
| mcpservers.org | 6,523 | 8,191 | ✅ 125% |
| mcp.so | ~2,000 | 1,384 | ~69% |
| **Total Estimated** | **~563,500** | **14,077** | **~2.5%** |

> **Note:** glama.ai dropped (2026-03-09) - MCP servers appear user-specific, not open source.
> **Note:** mcpservers.org completed 2026-03-09 - collected 8,191 servers (exceeds advertised 6,523).

## Files Created

### Scripts (Reusable)

```
/meilisearch/indices/scripts/
├── count-components.sh      # Summary statistics
├── count-components.jq      # JQ module for analysis
└── check-registry-completeness.sh  # Progress check
```

### Scope Definitions

```
/plans/skill-discovery/analysis/results/
├── registry-scope-definitions.yaml  # "Done" criteria per registry
└── registry-probe-summary.yaml      # Probe experiment results
```

### Planning Documents (Require Approval)

```
/plans/skill-discovery/analysis/experiments/
├── 3-large-registry-scrape-plan.md  # Scraping strategy
└── 4-verification-deduplication-plan.md  # Quality tiering
```

## Pending Decisions

### Experiment 3: Large Registry Scraping

1. **Tool selection per registry:**
   - API for skillsmp.com? (documented at /docs/api)
   - crawl4ai or Playwright for glama.ai?

2. **Rate limiting strategy:**
   - Delays between requests
   - Batch sizes

3. **Raw data storage format:**
   - NDJSON per registry confirmed?

### Experiment 4: Verification & Deduplication

1. **Schema changes:**
   - Add `quality_tier` field?
   - Add `name_normalized` field?
   - Add `content_hash` field?

2. **Fork handling:**
   - Keep separate with `fork_of` link?
   - Merge into original?
   - Exclude unless modified?

3. **Naming authority:**
   - How to determine canonical component when multiple exist with same name?

4. **Stale component handling:**
   - Mark as stale after 12 months no activity?
   - Demote tier?

## Recommended Next Steps

1. ✅ ~~Complete mcpservers.org crawl~~ - DONE (8,191 servers)
2. **Continue smithery.ai/servers crawl** - 368 of ~3,810 (need smaller batches for full extraction)
3. **Complete buildwithclaude.com crawl** - 234 of ~11,394
4. **Investigate APIs** for skillsmp.com (414K skills)
5. **Merge bronze files** into components.json
6. **Pilot Silver tier** verification on current 14,077 components
