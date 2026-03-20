/**
 * Registry crawling, rate limiting, state management, and component normalization.
 *
 * Port of .scripts/crawl-registries.py -- preserves the same crawl tiers,
 * rate limiting behavior, checkpoint/resume semantics, and component ID
 * generation so that output is compatible with the Python version.
 */

import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { spawnSync } from './runtime'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_OUTPUT_DIR = '/private/etc/dotfiles/adam/services/databases/meilisearch/indices'
const DEFAULT_STATE_FILE = join(DEFAULT_OUTPUT_DIR, '.crawl-state.json')

export const BACKOFF_CONFIG = {
  initialDelay: 2,
  multiplier: 2,
  maxDelay: 300, // 5 minute ceiling
  maxRetries: 5,
} as const

export const RATE_LIMITS: Record<string, RateLimitConfig> = {
  skillsmp: { delay: 2, dailyLimit: 500 },
  github: { delay: 2, dailyLimit: 5000 },
  claudemarketplaces: { delay: 0.5 },
  buildwithclaude: { delay: 1 },
  mcp_so: { delay: 3 },
}

// ---------------------------------------------------------------------------
// Rate Limiting
// ---------------------------------------------------------------------------

export interface RateLimitConfig {
  /** Seconds between requests. */
  delay: number
  /** Maximum requests per calendar day. */
  dailyLimit?: number
}

export class RateLimiter {
  private requestsToday = 0
  private resetDate: string

  constructor(
    private readonly registryName: string,
    private readonly config: RateLimitConfig
  ) {
    this.resetDate = new Date().toISOString().slice(0, 10) // YYYY-MM-DD
  }

  /** Check if we can make another request today. */
  canRequest(): boolean {
    if (this.config.dailyLimit === undefined) return true
    const today = new Date().toISOString().slice(0, 10)
    if (today > this.resetDate) {
      this.requestsToday = 0
      this.resetDate = today
    }
    return this.requestsToday < this.config.dailyLimit
  }

  /** Record that a request was made. */
  recordRequest(): void {
    this.requestsToday += 1
    if (this.config.dailyLimit !== undefined && this.requestsToday >= this.config.dailyLimit) {
      console.warn(`${this.registryName}: Daily limit reached (${this.config.dailyLimit})`)
      console.info('Resume tomorrow with: --tier <tier> --resume')
    }
  }

  /** Wait for the configured delay between requests. */
  async waitForSlot(): Promise<void> {
    await sleep(this.config.delay * 1000)
  }

  /** Get the current request count (for testing). */
  get count(): number {
    return this.requestsToday
  }
}

// ---------------------------------------------------------------------------
// Crawl State (checkpoint/resume)
// ---------------------------------------------------------------------------

export interface RegistryState {
  status: 'pending' | 'in_progress' | 'completed'
  lastPage: number
  totalFetched: number
  estimatedTotal?: number
  lastUrl?: string
  topicsCompleted?: string[]
  reposCompleted?: string[]
  apiUsed?: string
}

export interface CrawlFailure {
  url: string
  error: string
  timestamp: string
  willRetry?: boolean
}

export interface CrawlState {
  version: string
  startedAt?: string
  lastUpdated?: string
  tiers: Record<string, Record<string, RegistryState>>
  failures: CrawlFailure[]
  stats?: Record<string, unknown>
}

/** Create a fresh crawl state. */
export function createCrawlState(): CrawlState {
  return {
    version: '1.0',
    startedAt: new Date().toISOString(),
    tiers: {},
    failures: [],
  }
}

/** Load crawl state from a JSON checkpoint file, or create new. */
export function loadState(path?: string): CrawlState {
  const statePath = path ?? DEFAULT_STATE_FILE
  try {
    if (existsSync(statePath)) {
      const raw = JSON.parse(readFileSync(statePath, 'utf-8') || '{}')
      return {
        version: raw.version ?? '1.0',
        startedAt: raw.startedAt ?? raw.started_at,
        lastUpdated: raw.lastUpdated ?? raw.last_updated,
        tiers: raw.tiers ?? {},
        failures: raw.failures ?? [],
        stats: raw.stats,
      }
    }
  } catch {
    // Fall through to creating new state
  }
  return createCrawlState()
}

/** Save crawl state to a JSON checkpoint file. */
export function saveState(state: CrawlState, path?: string): void {
  const statePath = path ?? DEFAULT_STATE_FILE
  state.lastUpdated = new Date().toISOString()
  const dir = statePath.replace(/\/[^/]+$/, '')
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }
  writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8')
}

/** Get or create registry state within a tier. */
export function getRegistryState(state: CrawlState, tier: string, registry: string): RegistryState {
  if (!state.tiers[tier]) {
    state.tiers[tier] = {}
  }
  if (!state.tiers[tier]![registry]) {
    state.tiers[tier]![registry] = {
      status: 'pending',
      lastPage: 0,
      totalFetched: 0,
    }
  }
  return state.tiers[tier]![registry]!
}

/** Log a crawl failure into state. */
export function logFailure(state: CrawlState, url: string, error: string): void {
  state.failures.push({
    url,
    error,
    timestamp: new Date().toISOString(),
    willRetry: true,
  })
}

// ---------------------------------------------------------------------------
// Component Normalization
// ---------------------------------------------------------------------------

export interface Component {
  id: string
  name: string
  type: string
  description: string | null
  author?: string
  canonical_url?: string | null
  github_url?: string | null
  star_count?: number
  source_type: string
  source_name: string
  source_url?: string
  tags?: string[]
  discovered_at?: string
}

/**
 * Sanitize a raw ID string to match ^[a-z0-9_-]+$.
 *
 * Matches the Python _sanitize_id() implementation exactly:
 * - Lowercase the input
 * - Replace / with _, space with -, . with -, : with _
 * - Remove any remaining invalid characters
 * - Collapse multiple consecutive separators
 * - Trim leading/trailing separators
 */
export function sanitizeId(rawId: string): string {
  let clean = rawId.toLowerCase()
  clean = clean.replace(/\//g, '_').replace(/ /g, '-').replace(/\./g, '-').replace(/:/g, '_')
  clean = clean.replace(/[^a-z0-9_-]/g, '')
  clean = clean.replace(/[-_]{2,}/g, '_')
  clean = clean.replace(/^[-_]+|[-_]+$/g, '')
  return clean
}

/**
 * Transform raw crawl data into a normalized Component record.
 *
 * Returns a Result to allow callers to handle transformation failures.
 */
export function transformToComponent(
  raw: unknown,
  componentType: string,
  sourceName: string
): Result<Component> {
  if (typeof raw !== 'object' || raw === null) {
    return err(new CliError('Expected object for component transform', 'E_TRANSFORM'))
  }

  const data = raw as Record<string, unknown>
  const author = (data.author as string) ?? (data.owner as string) ?? 'unknown'
  const name = (data.name as string) ?? 'unknown'
  const componentId = sanitizeId(`${sourceName}_${author}_${name}`)

  if (!componentId) {
    return err(new CliError('Generated empty component ID', 'E_TRANSFORM'))
  }

  const component: Component = {
    id: componentId,
    name,
    type: componentType,
    description: (data.description as string) ?? null,
    author,
    canonical_url:
      (data.url as string) ?? (data.skillUrl as string) ?? (data.html_url as string) ?? null,
    github_url: (data.githubUrl as string) ?? (data.html_url as string) ?? null,
    star_count: (data.stars as number) ?? (data.stargazers_count as number) ?? 0,
    source_type: sourceName !== 'github' ? 'registry' : 'github',
    source_name: sourceName,
    source_url: sourceName !== 'github' ? `https://${sourceName}.com` : 'https://github.com',
    tags: (data.keywords as string[]) ?? (data.topics as string[]) ?? [],
    discovered_at: new Date().toISOString(),
  }

  return ok(component)
}

// ---------------------------------------------------------------------------
// Fetch with Backoff
// ---------------------------------------------------------------------------

/**
 * Fetch a URL with exponential backoff for retries on 429/5xx/timeout.
 *
 * Returns null on permanent failure (4xx other than 429) or after max retries.
 */
export async function fetchWithBackoff(url: string, state: CrawlState): Promise<Response | null> {
  let delay = BACKOFF_CONFIG.initialDelay

  for (let attempt = 0; attempt < BACKOFF_CONFIG.maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        signal: AbortSignal.timeout(30_000),
      })

      if (response.status === 429) {
        const retryAfter = Number.parseInt(response.headers.get('Retry-After') ?? String(delay), 10)
        console.warn(`Rate limited, waiting ${retryAfter}s (attempt ${attempt + 1})`)
        await sleep(retryAfter * 1000)
        continue
      }

      if (response.status >= 500) {
        console.warn(`Server error ${response.status}, backoff ${delay}s`)
        await sleep(delay * 1000)
        delay = Math.min(delay * BACKOFF_CONFIG.multiplier, BACKOFF_CONFIG.maxDelay)
        continue
      }

      if (response.status >= 400) {
        console.error(`Client error ${response.status}: ${url}`)
        logFailure(state, url, `http_${response.status}`)
        return null
      }

      return response
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e)
      if (message.includes('timeout') || message.includes('abort')) {
        console.warn(`Timeout, backoff ${delay}s (attempt ${attempt + 1})`)
      } else {
        console.warn(`Connection error: ${message}, backoff ${delay}s`)
      }
      await sleep(delay * 1000)
      delay = Math.min(delay * BACKOFF_CONFIG.multiplier, BACKOFF_CONFIG.maxDelay)
    }
  }

  console.error(`FAILED after ${BACKOFF_CONFIG.maxRetries} attempts: ${url}`)
  logFailure(state, url, 'max_retries_exhausted')
  return null
}

// ---------------------------------------------------------------------------
// Crawl Options
// ---------------------------------------------------------------------------

export interface CrawlOpts {
  dryRun?: boolean
  resume?: boolean
}

// ---------------------------------------------------------------------------
// Tier 1: API Crawlers
// ---------------------------------------------------------------------------

/**
 * Crawl skillsmp.com paginated API.
 *
 * Requires an API key from 1Password (op://Developer/skillsmp/credential).
 */
export async function crawlSkillsmp(
  state: CrawlState,
  output: string,
  opts?: CrawlOpts
): Promise<number> {
  console.info('Crawling skillsmp.com...')

  // Get API key from 1Password
  let apiKey: string
  try {
    const proc = spawnSync(['op', 'read', 'op://Developer/skillsmp/credential'])
    if (proc.exitCode !== 0) throw new Error('op read failed')
    apiKey = proc.stdout.trim()
  } catch {
    console.error('Failed to get skillsmp API key from 1Password')
    return 0
  }

  const regState = getRegistryState(state, 'api', 'skillsmp')
  const rateLimiter = new RateLimiter('skillsmp', RATE_LIMITS.skillsmp!)

  const startPage = regState.lastPage + 1
  let totalFetched = regState.totalFetched
  let page = startPage

  while (rateLimiter.canRequest()) {
    const url = `https://skillsmp.com/api/v1/skills/search?q=*&limit=100&page=${page}`

    if (opts?.dryRun) {
      console.info(`[DRY RUN] Would fetch: ${url}`)
      page += 1
      if (page > startPage + 2) break
      continue
    }

    const response = await fetchWithBackoff(url, state)
    if (!response) break

    rateLimiter.recordRequest()
    await rateLimiter.waitForSlot()

    const data = (await response.json()) as Record<string, unknown>
    const skills = ((data.data as Record<string, unknown>)?.skills ?? []) as Record<
      string,
      unknown
    >[]

    if (skills.length === 0) {
      console.info(`No more skills at page ${page}`)
      regState.status = 'completed'
      break
    }

    appendNdjson(output, skills, 'skill', 'skillsmp')

    totalFetched += skills.length
    regState.lastPage = page
    regState.totalFetched = totalFetched
    regState.status = 'in_progress'

    console.info(`Page ${page}: fetched ${skills.length} skills (total: ${totalFetched})`)
    page += 1
  }

  return totalFetched
}

/**
 * Crawl GitHub topic searches via the gh CLI.
 */
export async function crawlGithubTopics(
  state: CrawlState,
  output: string,
  opts?: CrawlOpts
): Promise<number> {
  console.info('Crawling GitHub topics...')

  const topics: [string, string][] = [
    ['claude-skills', 'skill'],
    ['claude-code-agents', 'agent'],
    ['claude-code-hooks', 'hook'],
    ['mcp-server', 'mcp_server'],
    ['claude-code-plugin', 'plugin'],
  ]

  const regState = getRegistryState(state, 'api', 'github')
  const completedTopics = new Set(regState.topicsCompleted ?? [])
  let totalFetched = regState.totalFetched

  for (const [topic, componentType] of topics) {
    if (completedTopics.has(topic)) {
      console.info(`Skipping ${topic} (already completed)`)
      continue
    }

    if (opts?.dryRun) {
      console.info(`[DRY RUN] Would search: topic:${topic}`)
      continue
    }

    const proc = spawnSync([
      'gh',
      'search',
      'repos',
      `topic:${topic}`,
      '--sort',
      'stars',
      '--limit',
      '100',
      '--json',
      'name,url,description,stargazersCount,owner',
    ])

    if (proc.exitCode !== 0) {
      console.error(`gh search failed for topic:${topic}`)
      logFailure(state, `topic:${topic}`, 'gh_cli_error')
      continue
    }

    let repos: Record<string, unknown>[]
    try {
      repos = JSON.parse(proc.stdout)
    } catch {
      console.error(`Failed to parse gh output for topic:${topic}`)
      logFailure(state, `topic:${topic}`, 'json_parse_error')
      continue
    }

    const normalized = repos.map((repo) => ({
      name: repo.name,
      description: repo.description,
      owner: (repo.owner as Record<string, unknown>)?.login,
      html_url: repo.url,
      stargazers_count: repo.stargazersCount ?? 0,
    }))

    appendNdjson(output, normalized, componentType, 'github')

    totalFetched += repos.length
    completedTopics.add(topic)
    regState.topicsCompleted = [...completedTopics]
    regState.totalFetched = totalFetched

    console.info(`Topic ${topic}: fetched ${repos.length} repos`)
    await sleep(RATE_LIMITS.github!.delay * 1000)
  }

  if (completedTopics.size === topics.length) {
    regState.status = 'completed'
  }

  return totalFetched
}

/**
 * Crawl claudemarketplaces.com JSON API.
 */
export async function crawlClaudeMarketplaces(
  state: CrawlState,
  output: string,
  opts?: CrawlOpts
): Promise<number> {
  console.info('Crawling claudemarketplaces.com...')

  const regState = getRegistryState(state, 'api', 'claudemarketplaces')
  if (regState.status === 'completed') {
    console.info('claudemarketplaces already completed')
    return regState.totalFetched
  }

  const url = 'https://claudemarketplaces.com/api/marketplaces'

  if (opts?.dryRun) {
    console.info(`[DRY RUN] Would fetch: ${url}`)
    return 0
  }

  const response = await fetchWithBackoff(url, state)
  if (!response) return 0

  const data = await response.json()
  const marketplaces = (
    Array.isArray(data) ? data : ((data as Record<string, unknown>).marketplaces ?? [])
  ) as Record<string, unknown>[]

  appendNdjson(output, marketplaces, 'plugin', 'claudemarketplaces')

  regState.status = 'completed'
  regState.totalFetched = marketplaces.length

  console.info(`Fetched ${marketplaces.length} marketplaces`)
  return marketplaces.length
}

// ---------------------------------------------------------------------------
// Tier 2: Scrape Crawlers
// ---------------------------------------------------------------------------

/**
 * Crawl buildwithclaude.com via HTML scraping with pagination.
 */
export async function crawlBuildWithClaude(
  state: CrawlState,
  output: string,
  opts?: CrawlOpts
): Promise<number> {
  console.info('Crawling buildwithclaude.com...')

  const regState = getRegistryState(state, 'scrape', 'buildwithclaude')
  if (regState.status === 'completed') {
    console.info('buildwithclaude already completed')
    return regState.totalFetched
  }

  const baseUrl = 'https://buildwithclaude.com/showcase'
  const startPage = regState.lastPage + 1
  let totalFetched = regState.totalFetched
  let page = startPage
  let consecutiveEmpty = 0

  while (consecutiveEmpty < 2) {
    const url = `${baseUrl}?page=${page}`

    if (opts?.dryRun) {
      console.info(`[DRY RUN] Would fetch: ${url}`)
      page += 1
      if (page > startPage + 2) break
      continue
    }

    const response = await fetchWithBackoff(url, state)
    if (!response) break

    await sleep(RATE_LIMITS.buildwithclaude!.delay * 1000)

    const html = await response.text()
    const projects = parseBuildWithClaudeHtml(html)

    if (projects.length === 0) {
      consecutiveEmpty += 1
      console.info(`No projects at page ${page}, empty count: ${consecutiveEmpty}`)
      page += 1
      continue
    }

    consecutiveEmpty = 0

    appendNdjson(output, projects, 'plugin', 'buildwithclaude')

    totalFetched += projects.length
    regState.lastPage = page
    regState.totalFetched = totalFetched
    regState.status = 'in_progress'

    console.info(`Page ${page}: fetched ${projects.length} projects (total: ${totalFetched})`)
    page += 1
  }

  if (consecutiveEmpty >= 2) {
    regState.status = 'completed'
  }

  return totalFetched
}

/**
 * Crawl mcp.so MCP server directory.
 *
 * NOTE: mcp.so is a Next.js site requiring JavaScript rendering.
 * Automated crawl attempts API endpoints first, then falls back to HTML scraping.
 * For full coverage, use crawl4ai MCP tool manually.
 */
async function crawlMcpSo(state: CrawlState, output: string, opts?: CrawlOpts): Promise<number> {
  console.info('Crawling mcp.so...')
  console.warn('mcp.so requires JS rendering - results may be limited')

  const regState = getRegistryState(state, 'scrape', 'mcp_so')
  if (regState.status === 'completed') {
    console.info('mcp.so already completed')
    return regState.totalFetched
  }

  const apiEndpoints = [
    'https://mcp.so/api/servers',
    'https://mcp.so/api/v1/servers',
    'https://mcp.so/servers.json',
  ]

  let totalFetched = 0

  // Try API endpoints
  for (const apiUrl of apiEndpoints) {
    if (opts?.dryRun) {
      console.info(`[DRY RUN] Would try API: ${apiUrl}`)
      continue
    }

    try {
      const response = await fetch(apiUrl, { signal: AbortSignal.timeout(10_000) })
      if (response.ok) {
        const data = await response.json()
        const servers = (
          Array.isArray(data) ? data : ((data as Record<string, unknown>).servers ?? [])
        ) as Record<string, unknown>[]

        appendNdjson(output, servers, 'mcp_server', 'mcp_so')

        totalFetched = servers.length
        regState.status = 'completed'
        regState.totalFetched = totalFetched
        regState.apiUsed = apiUrl

        console.info(`API ${apiUrl}: fetched ${totalFetched} servers`)
        return totalFetched
      }
    } catch {}
  }

  // Fallback: scrape HTML pages
  if (!opts?.dryRun) {
    console.info('API endpoints failed, falling back to HTML scraping')
    totalFetched = await scrapeMcpSoHtml(state, regState, output)
  }

  return totalFetched
}

/** Scrape mcp.so via HTML pages with pagination. */
async function scrapeMcpSoHtml(
  state: CrawlState,
  regState: RegistryState,
  output: string
): Promise<number> {
  const baseUrl = 'https://mcp.so'
  const startPage = regState.lastPage + 1
  let totalFetched = regState.totalFetched
  let page = startPage
  let consecutiveEmpty = 0

  while (consecutiveEmpty < 2) {
    const urlPatterns = [
      `${baseUrl}/servers?page=${page}`,
      `${baseUrl}?page=${page}`,
      `${baseUrl}/page/${page}`,
    ]

    let response: Response | null = null
    for (const url of urlPatterns) {
      response = await fetchWithBackoff(url, state)
      if (response?.ok) break
    }

    if (!response?.ok) {
      console.warn(`No valid response for page ${page}`)
      break
    }

    await sleep(RATE_LIMITS.mcp_so!.delay * 1000)

    const html = await response.text()
    const servers = parseMcpSoHtml(html)

    if (servers.length === 0) {
      consecutiveEmpty += 1
      page += 1
      continue
    }

    consecutiveEmpty = 0

    appendNdjson(output, servers, 'mcp_server', 'mcp_so')

    totalFetched += servers.length
    regState.lastPage = page
    regState.totalFetched = totalFetched
    regState.status = 'in_progress'

    console.info(`Page ${page}: fetched ${servers.length} servers (total: ${totalFetched})`)
    page += 1
  }

  if (consecutiveEmpty >= 2) {
    regState.status = 'completed'
  }

  return totalFetched
}

// ---------------------------------------------------------------------------
// Tier 3: Awesome Lists
// ---------------------------------------------------------------------------

/**
 * Crawl awesome list repositories for component links.
 */
export async function crawlAwesomeLists(
  state: CrawlState,
  output: string,
  opts?: CrawlOpts
): Promise<number> {
  console.info('Crawling awesome lists...')

  const awesomeRepos: [string, string][] = [
    ['punkpeye/awesome-mcp-servers', 'mcp_server'],
    ['anthropics/anthropic-cookbook', 'skill'],
    ['wong2/awesome-mcp-servers', 'mcp_server'],
    ['modelcontextprotocol/servers', 'mcp_server'],
  ]

  const regState = getRegistryState(state, 'awesome', 'awesome_lists')
  const completedRepos = new Set(regState.reposCompleted ?? [])
  let totalFetched = regState.totalFetched

  for (const [repo, defaultType] of awesomeRepos) {
    if (completedRepos.has(repo)) {
      console.info(`Skipping ${repo} (already completed)`)
      continue
    }

    if (opts?.dryRun) {
      console.info(`[DRY RUN] Would parse: ${repo}`)
      continue
    }

    // Fetch README.md using gh CLI
    const proc = spawnSync(['gh', 'api', `repos/${repo}/readme`, '--jq', '.content'])

    if (proc.exitCode !== 0) {
      console.error(`Failed to fetch ${repo} README`)
      logFailure(state, `gh:repos/${repo}/readme`, 'gh_api_error')
      continue
    }

    let readmeContent: string
    try {
      const base64Content = proc.stdout.trim()
      readmeContent = atob(base64Content)
    } catch (e) {
      console.error(`Failed to decode ${repo} README: ${e}`)
      continue
    }

    const links = parseAwesomeReadme(readmeContent)

    // Write each link with its detected component type
    for (const link of links) {
      const componentType = (link as Record<string, unknown>).type ?? defaultType
      const result = transformToComponent(link, componentType as string, `awesome:${repo}`)
      if (result.ok) {
        appendFileSync(output, JSON.stringify(result.value) + '\n', 'utf-8')
      }
    }

    totalFetched += links.length
    completedRepos.add(repo)
    regState.reposCompleted = [...completedRepos]
    regState.totalFetched = totalFetched

    console.info(`${repo}: parsed ${links.length} components`)
    await sleep(1000)
  }

  if (completedRepos.size === awesomeRepos.length) {
    regState.status = 'completed'
  }

  return totalFetched
}

// ---------------------------------------------------------------------------
// HTML Parsing Helpers
// ---------------------------------------------------------------------------

/**
 * Parse project data from buildwithclaude HTML.
 * Looks for JSON embedded in script tags, then falls back to card patterns.
 */
export function parseBuildWithClaudeHtml(html: string): Record<string, unknown>[] {
  const projects: Record<string, unknown>[] = []

  // Try to find JSON data embedded in script tags
  const jsonPattern = /<script[^>]*type="application\/json"[^>]*>([^<]+)<\/script>/gi
  let match: RegExpExecArray | null = jsonPattern.exec(html)
  while (match !== null) {
    try {
      const data = JSON.parse(match[1]!)
      if (typeof data === 'object' && data !== null && 'projects' in data) {
        for (const proj of (data as Record<string, unknown[]>).projects!) {
          const p = proj as Record<string, unknown>
          projects.push({
            name: p.name ?? p.title,
            description: p.description,
            url: p.url ?? p.link,
            author: p.author ?? p.creator,
          })
        }
      }
    } catch {}
    match = jsonPattern.exec(html)
  }

  // Fallback: parse HTML structure for card patterns
  if (projects.length === 0) {
    const cardPattern = /<div[^>]*class="[^"]*card[^"]*"[^>]*>([\s\S]*?)<\/div>/gi
    const titlePattern = /<h[23][^>]*>([^<]+)<\/h[23]>/i
    const descPattern = /<p[^>]*>([^<]{10,200})<\/p>/i
    const linkPattern = /<a[^>]*href="([^"]+)"[^>]*>/i

    let cardMatch: RegExpExecArray | null = cardPattern.exec(html)
    while (cardMatch !== null) {
      const cardHtml = cardMatch[1]!
      const titleMatch = titlePattern.exec(cardHtml)
      const descMatch = descPattern.exec(cardHtml)
      const linkMatch = linkPattern.exec(cardHtml)

      if (titleMatch) {
        projects.push({
          name: titleMatch[1]!.trim(),
          description: descMatch ? descMatch[1]!.trim() : null,
          url: linkMatch ? linkMatch[1] : null,
          author: null,
        })
      }
      cardMatch = cardPattern.exec(html)
    }
  }

  return projects
}

/**
 * Parse MCP server data from mcp.so HTML.
 * Looks for JSON-LD data and Next.js __NEXT_DATA__.
 */
export function parseMcpSoHtml(html: string): Record<string, unknown>[] {
  const servers: Record<string, unknown>[] = []

  // Look for JSON-LD data
  const jsonLdPattern = /<script[^>]*type="application\/ld\+json"[^>]*>([^<]+)<\/script>/gi
  let match: RegExpExecArray | null = jsonLdPattern.exec(html)
  while (match !== null) {
    try {
      const data = JSON.parse(match[1]!) as Record<string, unknown>
      if (data['@type'] === 'SoftwareApplication') {
        servers.push({
          name: data.name,
          description: data.description,
          url: data.url,
          author: (data.author as Record<string, unknown>)?.name,
        })
      }
    } catch {}
    match = jsonLdPattern.exec(html)
  }

  // Look for Next.js __NEXT_DATA__
  const nextDataPattern = /<script[^>]*id="__NEXT_DATA__"[^>]*>([^<]+)<\/script>/i
  const nextMatch = nextDataPattern.exec(html)
  if (nextMatch) {
    try {
      const data = JSON.parse(nextMatch[1]!) as Record<string, unknown>
      const props = (data.props as Record<string, unknown>)?.pageProps as
        | Record<string, unknown>
        | undefined
      if (props) {
        for (const key of ['servers', 'items', 'data', 'results']) {
          const items = props[key]
          if (Array.isArray(items)) {
            for (const item of items) {
              const rec = item as Record<string, unknown>
              if (rec.name) {
                servers.push({
                  name: rec.name,
                  description: rec.description,
                  url: rec.url ?? rec.homepage,
                  author: rec.author ?? rec.owner,
                  stars: rec.stars ?? rec.stargazers_count,
                  githubUrl: rec.github ?? rec.repository,
                })
              }
            }
          }
        }
      }
    } catch {
      // ignore parse errors
    }
  }

  return servers
}

/**
 * Parse awesome list README for component links.
 *
 * Matches markdown link patterns like:
 *   - [Name](url) - Description
 *   * [Name](url) - Description
 */
export function parseAwesomeReadme(content: string): Record<string, unknown>[] {
  const components: Record<string, unknown>[] = []
  const linkPattern = /[-*]\s*\[([^\]]+)\]\(([^)]+)\)\s*[-\u2013:]?\s*(.*)$/

  for (const line of content.split('\n')) {
    const match = linkPattern.exec(line)
    if (!match) continue

    const name = match[1]!.trim()
    const url = match[2]!.trim()
    const description = match[3]?.trim() || null

    // Skip non-component links
    if (url.startsWith('http://shields.io')) continue
    if (/\.(png|svg|gif)$/.test(url)) continue
    if (url.startsWith('#')) continue

    // Determine GitHub owner if it's a GitHub URL
    let owner: string | null = null
    const githubMatch = /https:\/\/github\.com\/([^/]+\/[^/]+)/.exec(url)
    if (githubMatch) {
      owner = githubMatch[1]!.split('/')[0]!
    }

    components.push({
      name,
      description,
      url,
      githubUrl: url.includes('github.com') ? url : null,
      author: owner,
    })
  }

  return components
}

// ---------------------------------------------------------------------------
// NDJSON Output
// ---------------------------------------------------------------------------

/** Append an array of raw records to an NDJSON output file. */
function appendNdjson(
  outputPath: string,
  records: Record<string, unknown>[],
  componentType: string,
  sourceName: string
): void {
  const lines: string[] = []
  for (const record of records) {
    const result = transformToComponent(record, componentType, sourceName)
    if (result.ok) {
      lines.push(JSON.stringify(result.value))
    }
  }
  if (lines.length > 0) {
    const content = lines.join('\n') + '\n'
    appendFileSync(outputPath, content, 'utf-8')
  }
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/** Validate component records from an NDJSON file. Returns count of invalid records. */
export function validateNdjson(filePath: string): {
  valid: number
  invalid: number
  errors: string[]
} {
  const errors: string[] = []
  let valid = 0
  let invalid = 0

  if (!existsSync(filePath)) {
    return { valid: 0, invalid: 0, errors: [`File not found: ${filePath}`] }
  }

  const content = readFileSync(filePath, 'utf-8')
  const lines = content.split('\n')

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!.trim()
    if (!line) continue

    try {
      const doc = JSON.parse(line) as Record<string, unknown>

      // Validate required fields
      const missing: string[] = []
      if (!doc.id || typeof doc.id !== 'string') missing.push('id')
      if (!doc.name || typeof doc.name !== 'string') missing.push('name')
      if (!doc.type || typeof doc.type !== 'string') missing.push('type')
      if (!doc.source_name || typeof doc.source_name !== 'string') missing.push('source_name')
      if (!doc.source_type || typeof doc.source_type !== 'string') missing.push('source_type')

      // Validate ID pattern
      if (typeof doc.id === 'string' && !/^[a-z0-9_-]+$/.test(doc.id)) {
        missing.push('id (invalid pattern)')
      }

      if (missing.length > 0) {
        invalid += 1
        errors.push(`Line ${i + 1}: missing or invalid fields: ${missing.join(', ')}`)
        if (errors.length > 10) {
          errors.push('Too many errors, stopping validation')
          break
        }
      } else {
        valid += 1
      }
    } catch (e) {
      invalid += 1
      errors.push(`Line ${i + 1}: Invalid JSON: ${e instanceof Error ? e.message : String(e)}`)
    }
  }

  return { valid, invalid, errors }
}

// ---------------------------------------------------------------------------
// Statistics
// ---------------------------------------------------------------------------

export interface CrawlStats {
  startedAt?: string
  lastUpdated?: string
  tiers: {
    name: string
    registries: {
      name: string
      status: string
      fetched: number
    }[]
  }[]
  totalFetched: number
  failureCount: number
  recentFailures: CrawlFailure[]
}

/** Compute statistics from crawl state. */
export function computeStats(state: CrawlState): CrawlStats {
  let totalFetched = 0
  const tiers: CrawlStats['tiers'] = []

  for (const [tierName, registries] of Object.entries(state.tiers)) {
    const tierRegistries: CrawlStats['tiers'][number]['registries'] = []
    for (const [regName, regData] of Object.entries(registries)) {
      const fetched = regData.totalFetched ?? 0
      totalFetched += fetched
      tierRegistries.push({
        name: regName,
        status: regData.status ?? 'pending',
        fetched,
      })
    }
    tiers.push({ name: tierName, registries: tierRegistries })
  }

  return {
    startedAt: state.startedAt,
    lastUpdated: state.lastUpdated,
    tiers,
    totalFetched,
    failureCount: state.failures.length,
    recentFailures: state.failures.slice(-5),
  }
}

// ---------------------------------------------------------------------------
// Run full tier crawl
// ---------------------------------------------------------------------------

/** Run all crawlers for a given tier. */
export async function crawlTier(
  tier: string,
  state: CrawlState,
  outputFile: string,
  opts?: CrawlOpts
): Promise<number> {
  let total = 0

  if (tier === 'api' || tier === 'all') {
    console.info('=== API Tier ===')
    total += await crawlSkillsmp(state, outputFile, opts)
    total += await crawlGithubTopics(state, outputFile, opts)
    total += await crawlClaudeMarketplaces(state, outputFile, opts)
  }

  if (tier === 'scrape' || tier === 'all') {
    console.info('=== Scrape Tier ===')
    total += await crawlBuildWithClaude(state, outputFile, opts)
    total += await crawlMcpSo(state, outputFile, opts)
  }

  if (tier === 'awesome' || tier === 'all') {
    console.info('=== Awesome Lists Tier ===')
    total += await crawlAwesomeLists(state, outputFile, opts)
  }

  return total
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
