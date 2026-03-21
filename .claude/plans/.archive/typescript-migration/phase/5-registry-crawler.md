---
id: c4cfe5f0-946f-460a-9ef1-c981f8124971
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 5: Registry Crawler"
status: pending
related:
  depends-on: [1105f062-33cf-4eff-a759-f17fb55296c3]
---

# Phase 5: Registry Crawler

**ID:** `phase-5`
**Dependencies:** phase-1
**Status:** pending
**Effort:** Medium

## Objective

Port the multi-tier registry crawler from Python to TypeScript, replacing `httpx` with native `fetch` and maintaining checkpoint/resume and rate limiting behavior.

## Success Criteria

- [ ] `ai-tools registry crawl --tier api --dry-run` shows what would be crawled
- [ ] `ai-tools registry crawl --tier api` produces NDJSON output matching Python's format
- [ ] Component IDs and field names match Python's `transform_to_component()` output
- [ ] Rate limiting respects per-registry delays and daily limits
- [ ] Checkpoint/resume works (interrupt and restart produces no duplicates)
- [ ] `ai-tools registry stats` shows crawl statistics
- [ ] `ai-tools registry validate` validates existing crawl output
- [ ] All justfile registry recipes point to TypeScript

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Registry module | `cli/lib/registry.ts` | TypeScript |
| Registry commands | `cli/commands/registry.ts` | TypeScript |
| Integration tests | `cli/test/registry.test.ts` | TypeScript |

## Files

**Create:**
- `cli/lib/registry.ts`
- `cli/test/registry.test.ts`

**Modify:**
- `cli/commands/registry.ts` (replace stub with full implementation)
- `justfile` (update registry recipes if any exist)

## Tasks

### lib/registry.ts — Rate limiting
- [ ] Implement `RateLimitConfig` interface (delay, dailyLimit)
- [ ] Implement `RateLimiter` class (canRequest, recordRequest, waitForSlot)
- [ ] Implement backoff utility (initial delay, multiplier, max delay, max retries)
- [ ] Configure per-registry rate limits (skillsmp: 2s/500, github: 2s/5000, etc.)

### lib/registry.ts — Crawl state
- [ ] Implement `CrawlState` interface (version, startedAt, tiers, failures)
- [ ] Implement `RegistryState` interface (status, lastPage, totalFetched, estimatedTotal)
- [ ] Implement `loadState()` — read from JSON checkpoint file
- [ ] Implement `saveState()` — write to JSON checkpoint file
- [ ] Implement `logFailure()` — append to failures array

### lib/registry.ts — Tier crawlers
- [ ] Implement `crawlSkillsmp()` — paginated API, JSON responses
- [ ] Implement `crawlGithubTopics()` — via `gh` CLI or GitHub API
- [ ] Implement `crawlClaudeMarketplaces()` — JSON API
- [ ] Implement `crawlBuildWithClaude()` — HTML scraping (regex or node-html-parser)
- [ ] Implement `crawlAwesomeLists()` — markdown parsing from GitHub repos
- [ ] All crawlers: respect rate limits, update state, write NDJSON output

### lib/registry.ts — Component normalization
- [ ] Implement `Component` interface (id, name, type, description, author, urls, tags, etc.)
- [ ] Implement `transformToComponent()` — normalize raw data to Component schema
- [ ] Implement `sanitizeId()` — convert to `^[a-z0-9_-]+$` pattern
- [ ] Write tests: transform known raw records, validate output shape

### commands/registry.ts
- [ ] Implement `crawl` subcommand — tier selection, resume, dry-run, progress output
- [ ] Implement `validate` subcommand — read NDJSON output, validate each record
- [ ] Implement `stats` subcommand — count records, show per-registry breakdown

### Parity validation
- [ ] Run Python crawler with `--tier api` on one registry, capture NDJSON
- [ ] Run TS crawler with `--tier api` on same registry, capture NDJSON
- [ ] Compare: component IDs, field names, record count (exact values may differ due to timing)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, crawl completed |
| 1 | Validation failures in output |
| 2 | Process error (network, rate limit, parse failure) |

## Notes

- Use native `fetch` — no `httpx` equivalent needed
- Use `Bun.write()` for streaming NDJSON output (one JSON object per line, no pretty-print)
- HTML scraping for `buildwithclaude` tier: start with regex (matching Python), consider `node-html-parser` (~15 KB, zero deps) if regex proves fragile
- The `mcp.so` scraper may need JS rendering — evaluate whether to keep or drop this source
- Checkpoint files should be gitignored
