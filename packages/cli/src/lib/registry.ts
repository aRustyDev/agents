/**
 * Re-export shim — registry.ts moved to @agents/sdk/catalog/pipeline/crawl in Phase 3.
 */

export type {
  CatalogRecord,
  CrawlFailure,
  CrawlOpts,
  CrawlState,
  CrawlStats,
  RateLimitConfig,
  RegistryState,
} from '@agents/sdk/catalog/pipeline/crawl'

export {
  BACKOFF_CONFIG,
  computeStats,
  crawlAwesomeLists,
  crawlBuildWithClaude,
  crawlClaudeMarketplaces,
  crawlGithubTopics,
  crawlSkillsmp,
  crawlTier,
  createCrawlState,
  fetchWithBackoff,
  getRegistryState,
  loadState,
  logFailure,
  parseAwesomeReadme,
  parseBuildWithClaudeHtml,
  parseMcpSoHtml,
  RATE_LIMITS,
  RateLimiter,
  sanitizeId,
  saveState,
  transformToComponent,
  validateNdjson,
} from '@agents/sdk/catalog/pipeline/crawl'
