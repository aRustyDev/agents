import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  BACKOFF_CONFIG,
  type CatalogRecord,
  type CrawlState,
  computeStats,
  createCrawlState,
  getRegistryState,
  loadState,
  logFailure,
  parseAwesomeReadme,
  parseBuildWithClaudeHtml,
  parseMcpSoHtml,
  RATE_LIMITS,
  type RateLimitConfig,
  RateLimiter,
  type RegistryState,
  sanitizeId,
  saveState,
  transformToComponent,
  validateNdjson,
} from '@agents/sdk/catalog/pipeline/crawl'

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

let tmpDir: string

beforeEach(() => {
  tmpDir = join(tmpdir(), `registry-test-${Date.now()}-${Math.random().toString(36).slice(2)}`)
  mkdirSync(tmpDir, { recursive: true })
})

afterEach(() => {
  if (existsSync(tmpDir)) {
    rmSync(tmpDir, { recursive: true, force: true })
  }
})

// ---------------------------------------------------------------------------
// sanitizeId
// ---------------------------------------------------------------------------

describe('sanitizeId', () => {
  test('converts to lowercase', () => {
    expect(sanitizeId('MyComponent')).toBe('mycomponent')
  })

  test('replaces slashes with underscores', () => {
    expect(sanitizeId('org/repo')).toBe('org_repo')
  })

  test('replaces spaces with hyphens', () => {
    expect(sanitizeId('my component')).toBe('my-component')
  })

  test('replaces dots with hyphens', () => {
    expect(sanitizeId('my.component')).toBe('my-component')
  })

  test('replaces colons with underscores', () => {
    expect(sanitizeId('scope:name')).toBe('scope_name')
  })

  test('removes invalid characters', () => {
    expect(sanitizeId('my@component!v2')).toBe('mycomponentv2')
  })

  test('collapses multiple separators', () => {
    expect(sanitizeId('my--component__v2')).toBe('my_component_v2')
  })

  test('trims leading/trailing separators', () => {
    expect(sanitizeId('-my-component-')).toBe('my-component')
    expect(sanitizeId('_my_component_')).toBe('my_component')
  })

  test('handles complex real-world IDs', () => {
    const result = sanitizeId('skillsmp_john.doe/my skill v2')
    expect(result).toMatch(/^[a-z0-9_-]+$/)
  })

  test('produces valid pattern for GitHub owner/repo', () => {
    const result = sanitizeId('github_aRustyDev_my-tool')
    expect(result).toMatch(/^[a-z0-9_-]+$/)
    expect(result).toBe('github_arustydev_my-tool')
  })

  test('handles empty-ish input gracefully', () => {
    expect(sanitizeId('___')).toBe('')
    expect(sanitizeId('---')).toBe('')
  })

  test('output always matches pattern ^[a-z0-9_-]+$ (or is empty)', () => {
    const inputs = [
      'Simple',
      'with spaces',
      'with/slashes',
      'with.dots',
      'MiXeD_CaSe-123',
      'org/repo/sub',
      '@scope/package',
      'a:b:c',
      '!!!',
    ]
    for (const input of inputs) {
      const result = sanitizeId(input)
      if (result.length > 0) {
        expect(result).toMatch(/^[a-z0-9_-]+$/)
      }
    }
  })
})

// ---------------------------------------------------------------------------
// transformToComponent
// ---------------------------------------------------------------------------

describe('transformToComponent', () => {
  test('transforms valid raw data into a Component', () => {
    const raw = {
      name: 'my-skill',
      description: 'A test skill',
      author: 'testuser',
      url: 'https://example.com/my-skill',
      stars: 42,
      keywords: ['test', 'skill'],
    }

    const result = transformToComponent(raw, 'skill', 'skillsmp')
    expect(result.ok).toBe(true)
    if (result.ok) {
      const c = result.value
      expect(c.id).toBe('skillsmp_testuser_my-skill')
      expect(c.name).toBe('my-skill')
      expect(c.type).toBe('skill')
      expect(c.description).toBe('A test skill')
      expect(c.author).toBe('testuser')
      expect(c.canonical_url).toBe('https://example.com/my-skill')
      expect(c.star_count).toBe(42)
      expect(c.source_type).toBe('registry')
      expect(c.source_name).toBe('skillsmp')
      expect(c.tags).toEqual(['test', 'skill'])
      expect(c.discovered_at).toBeDefined()
    }
  })

  test('uses owner field when author is missing', () => {
    const raw = { name: 'tool', owner: 'orgname' }
    const result = transformToComponent(raw, 'mcp-server', 'github')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.author).toBe('orgname')
      expect(result.value.source_type).toBe('github')
    }
  })

  test('defaults to "unknown" author when both author and owner are missing', () => {
    const raw = { name: 'orphan-tool' }
    const result = transformToComponent(raw, 'plugin', 'test')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.author).toBe('unknown')
    }
  })

  test('returns error for non-object input', () => {
    const result = transformToComponent('not an object', 'skill', 'test')
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_TRANSFORM')
    }
  })

  test('returns error for null input', () => {
    const result = transformToComponent(null, 'skill', 'test')
    expect(result.ok).toBe(false)
  })

  test('github source sets source_type to github', () => {
    const raw = { name: 'test' }
    const result = transformToComponent(raw, 'skill', 'github')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source_type).toBe('github')
      expect(result.value.source_url).toBe('https://github.com')
    }
  })

  test('non-github source sets source_type to registry', () => {
    const raw = { name: 'test' }
    const result = transformToComponent(raw, 'skill', 'skillsmp')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source_type).toBe('registry')
      expect(result.value.source_url).toBe('https://skillsmp.com')
    }
  })

  test('picks up github_url from githubUrl field', () => {
    const raw = { name: 'test', githubUrl: 'https://github.com/org/repo' }
    const result = transformToComponent(raw, 'plugin', 'test')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.github_url).toBe('https://github.com/org/repo')
    }
  })

  test('picks up canonical_url from skillUrl field', () => {
    const raw = { name: 'test', skillUrl: 'https://skillsmp.com/s/test' }
    const result = transformToComponent(raw, 'skill', 'skillsmp')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.canonical_url).toBe('https://skillsmp.com/s/test')
    }
  })

  test('Component structure has all expected fields', () => {
    const raw = { name: 'complete', description: 'desc', author: 'me' }
    const result = transformToComponent(raw, 'agent', 'test')
    expect(result.ok).toBe(true)
    if (result.ok) {
      const c = result.value
      const keys = Object.keys(c)
      expect(keys).toContain('id')
      expect(keys).toContain('name')
      expect(keys).toContain('type')
      expect(keys).toContain('description')
      expect(keys).toContain('author')
      expect(keys).toContain('canonical_url')
      expect(keys).toContain('github_url')
      expect(keys).toContain('star_count')
      expect(keys).toContain('source_type')
      expect(keys).toContain('source_name')
      expect(keys).toContain('source_url')
      expect(keys).toContain('tags')
      expect(keys).toContain('discovered_at')
    }
  })
})

// ---------------------------------------------------------------------------
// RateLimiter
// ---------------------------------------------------------------------------

describe('RateLimiter', () => {
  test('canRequest returns true when no daily limit', () => {
    const limiter = new RateLimiter('test', { delay: 1 })
    expect(limiter.canRequest()).toBe(true)
  })

  test('canRequest respects daily limit', () => {
    const limiter = new RateLimiter('test', { delay: 1, dailyLimit: 3 })
    expect(limiter.canRequest()).toBe(true)

    limiter.recordRequest()
    limiter.recordRequest()
    expect(limiter.canRequest()).toBe(true)

    limiter.recordRequest() // hits limit
    expect(limiter.canRequest()).toBe(false)
  })

  test('recordRequest increments count', () => {
    const limiter = new RateLimiter('test', { delay: 1, dailyLimit: 100 })
    expect(limiter.count).toBe(0)
    limiter.recordRequest()
    expect(limiter.count).toBe(1)
    limiter.recordRequest()
    expect(limiter.count).toBe(2)
  })

  test('waitForSlot respects delay', async () => {
    const limiter = new RateLimiter('test', { delay: 0.05 }) // 50ms
    const start = Date.now()
    await limiter.waitForSlot()
    const elapsed = Date.now() - start
    expect(elapsed).toBeGreaterThanOrEqual(40) // allow small timing variance
  })

  test('canRequest always true without dailyLimit', () => {
    const limiter = new RateLimiter('unlimited', { delay: 0.5 })
    for (let i = 0; i < 100; i++) {
      expect(limiter.canRequest()).toBe(true)
      limiter.recordRequest()
    }
  })
})

// ---------------------------------------------------------------------------
// CrawlState: loadState / saveState round-trip
// ---------------------------------------------------------------------------

describe('CrawlState', () => {
  test('createCrawlState returns fresh state', () => {
    const state = createCrawlState()
    expect(state.version).toBe('1.0')
    expect(state.startedAt).toBeDefined()
    expect(state.tiers).toEqual({})
    expect(state.failures).toEqual([])
  })

  test('loadState returns fresh state for missing file', () => {
    const state = loadState(join(tmpDir, 'nonexistent.json'))
    expect(state.version).toBe('1.0')
    expect(state.startedAt).toBeDefined()
  })

  test('saveState and loadState round-trip', () => {
    const path = join(tmpDir, 'state.json')
    const state = createCrawlState()
    state.tiers.api = {
      skillsmp: {
        status: 'in_progress',
        lastPage: 5,
        totalFetched: 500,
      },
    }
    state.failures.push({
      url: 'https://example.com/fail',
      error: 'http_500',
      timestamp: new Date().toISOString(),
    })

    saveState(state, path)

    const loaded = loadState(path)
    expect(loaded.version).toBe('1.0')
    expect(loaded.tiers.api!.skillsmp!.status).toBe('in_progress')
    expect(loaded.tiers.api!.skillsmp!.lastPage).toBe(5)
    expect(loaded.tiers.api!.skillsmp!.totalFetched).toBe(500)
    expect(loaded.failures).toHaveLength(1)
    expect(loaded.failures[0]!.url).toBe('https://example.com/fail')
    expect(loaded.lastUpdated).toBeDefined()
  })

  test('saveState creates parent directories', () => {
    const path = join(tmpDir, 'nested', 'deep', 'state.json')
    const state = createCrawlState()
    saveState(state, path)
    expect(existsSync(path)).toBe(true)
  })

  test('getRegistryState creates tier and registry if missing', () => {
    const state = createCrawlState()
    const regState = getRegistryState(state, 'api', 'github')
    expect(regState.status).toBe('pending')
    expect(regState.lastPage).toBe(0)
    expect(regState.totalFetched).toBe(0)
    expect(state.tiers.api).toBeDefined()
    expect(state.tiers.api!.github).toBeDefined()
  })

  test('getRegistryState returns existing state', () => {
    const state = createCrawlState()
    const first = getRegistryState(state, 'api', 'github')
    first.status = 'in_progress'
    first.totalFetched = 100

    const second = getRegistryState(state, 'api', 'github')
    expect(second.status).toBe('in_progress')
    expect(second.totalFetched).toBe(100)
  })

  test('logFailure appends to failures array', () => {
    const state = createCrawlState()
    logFailure(state, 'https://fail.com', 'http_429')
    logFailure(state, 'https://fail2.com', 'timeout')

    expect(state.failures).toHaveLength(2)
    expect(state.failures[0]!.url).toBe('https://fail.com')
    expect(state.failures[0]!.error).toBe('http_429')
    expect(state.failures[0]!.timestamp).toBeDefined()
    expect(state.failures[1]!.url).toBe('https://fail2.com')
  })
})

// ---------------------------------------------------------------------------
// validateNdjson
// ---------------------------------------------------------------------------

describe('validateNdjson', () => {
  test('returns error for missing file', () => {
    const result = validateNdjson(join(tmpDir, 'nope.json'))
    expect(result.errors).toHaveLength(1)
    expect(result.errors[0]).toContain('File not found')
  })

  test('validates valid NDJSON records', () => {
    const filePath = join(tmpDir, 'valid.json')
    const records = [
      {
        id: 'test-1',
        name: 'Test One',
        type: 'skill',
        source_name: 'test',
        source_type: 'registry',
      },
      {
        id: 'test-2',
        name: 'Test Two',
        type: 'plugin',
        source_name: 'github',
        source_type: 'github',
      },
    ]
    writeFileSync(filePath, records.map((r) => JSON.stringify(r)).join('\n') + '\n', 'utf-8')

    const result = validateNdjson(filePath)
    expect(result.valid).toBe(2)
    expect(result.invalid).toBe(0)
    expect(result.errors).toHaveLength(0)
  })

  test('reports invalid records with missing fields', () => {
    const filePath = join(tmpDir, 'invalid.json')
    const records = [
      { id: 'good', name: 'Good', type: 'skill', source_name: 'test', source_type: 'registry' },
      { name: 'No ID', type: 'skill' }, // missing id, source_name, source_type
      { id: 'no-name', type: 'skill', source_name: 'test', source_type: 'registry' }, // missing name
    ]
    writeFileSync(filePath, records.map((r) => JSON.stringify(r)).join('\n') + '\n', 'utf-8')

    const result = validateNdjson(filePath)
    expect(result.valid).toBe(1)
    expect(result.invalid).toBe(2)
    expect(result.errors.length).toBeGreaterThan(0)
  })

  test('reports invalid JSON lines', () => {
    const filePath = join(tmpDir, 'bad-json.json')
    writeFileSync(filePath, '{"valid": true}\nnot json\n', 'utf-8')

    const result = validateNdjson(filePath)
    expect(result.invalid).toBeGreaterThan(0)
    expect(result.errors.some((e) => e.includes('Invalid JSON'))).toBe(true)
  })

  test('rejects IDs with invalid pattern', () => {
    const filePath = join(tmpDir, 'bad-id.json')
    const record = {
      id: 'UPPERCASE-ID',
      name: 'Test',
      type: 'skill',
      source_name: 'test',
      source_type: 'registry',
    }
    writeFileSync(filePath, JSON.stringify(record) + '\n', 'utf-8')

    const result = validateNdjson(filePath)
    expect(result.invalid).toBe(1)
  })

  test('skips blank lines', () => {
    const filePath = join(tmpDir, 'blanks.json')
    const record = {
      id: 'test',
      name: 'Test',
      type: 'skill',
      source_name: 'x',
      source_type: 'registry',
    }
    writeFileSync(filePath, '\n' + JSON.stringify(record) + '\n\n', 'utf-8')

    const result = validateNdjson(filePath)
    expect(result.valid).toBe(1)
    expect(result.invalid).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// computeStats
// ---------------------------------------------------------------------------

describe('computeStats', () => {
  test('computes stats from empty state', () => {
    const state = createCrawlState()
    const stats = computeStats(state)
    expect(stats.totalFetched).toBe(0)
    expect(stats.failureCount).toBe(0)
    expect(stats.tiers).toHaveLength(0)
  })

  test('computes stats from populated state', () => {
    const state = createCrawlState()
    state.tiers.api = {
      skillsmp: { status: 'completed', lastPage: 10, totalFetched: 1000 },
      github: { status: 'in_progress', lastPage: 3, totalFetched: 300 },
    }
    state.tiers.scrape = {
      buildwithclaude: { status: 'pending', lastPage: 0, totalFetched: 0 },
    }
    state.failures = [
      { url: 'https://fail.com', error: 'timeout', timestamp: '2024-01-01T00:00:00Z' },
    ]

    const stats = computeStats(state)
    expect(stats.totalFetched).toBe(1300)
    expect(stats.failureCount).toBe(1)
    expect(stats.tiers).toHaveLength(2)
    expect(stats.tiers[0]!.name).toBe('api')
    expect(stats.tiers[0]!.registries).toHaveLength(2)
    expect(stats.recentFailures).toHaveLength(1)
  })
})

// ---------------------------------------------------------------------------
// HTML Parsing
// ---------------------------------------------------------------------------

describe('parseBuildWithClaudeHtml', () => {
  test('extracts projects from embedded JSON', () => {
    const html = `
      <html><body>
      <script type="application/json">
        {"projects": [
          {"name": "My App", "description": "A cool app", "url": "https://example.com"}
        ]}
      </script>
      </body></html>
    `
    const projects = parseBuildWithClaudeHtml(html)
    expect(projects).toHaveLength(1)
    expect(projects[0]!.name).toBe('My App')
    expect(projects[0]!.description).toBe('A cool app')
  })

  test('falls back to card parsing', () => {
    const html = `
      <html><body>
      <div class="project-card">
        <h2>Card Title</h2>
        <p>This is a description of the project card</p>
        <a href="https://example.com/project">Link</a>
      </div>
      </body></html>
    `
    const projects = parseBuildWithClaudeHtml(html)
    expect(projects).toHaveLength(1)
    expect(projects[0]!.name).toBe('Card Title')
  })

  test('returns empty for HTML without projects', () => {
    const html = '<html><body><p>Nothing here</p></body></html>'
    const projects = parseBuildWithClaudeHtml(html)
    expect(projects).toHaveLength(0)
  })
})

describe('parseMcpSoHtml', () => {
  test('extracts from JSON-LD', () => {
    const html = `
      <script type="application/ld+json">
        {"@type": "SoftwareApplication", "name": "Test Server", "description": "A server"}
      </script>
    `
    const servers = parseMcpSoHtml(html)
    expect(servers).toHaveLength(1)
    expect(servers[0]!.name).toBe('Test Server')
  })

  test('extracts from __NEXT_DATA__', () => {
    const html = `
      <script id="__NEXT_DATA__" type="application/json">
        {"props": {"pageProps": {"servers": [
          {"name": "NextServer", "description": "From Next.js data"}
        ]}}}
      </script>
    `
    const servers = parseMcpSoHtml(html)
    expect(servers).toHaveLength(1)
    expect(servers[0]!.name).toBe('NextServer')
  })

  test('returns empty for unrecognized HTML', () => {
    const html = '<html><body>No data</body></html>'
    expect(parseMcpSoHtml(html)).toHaveLength(0)
  })
})

describe('parseAwesomeReadme', () => {
  test('extracts markdown links with descriptions', () => {
    const md = [
      '# Awesome List',
      '',
      '- [Tool A](https://github.com/org/tool-a) - A great tool',
      '- [Tool B](https://example.com/tool-b) - Another tool',
      '* [Tool C](https://github.com/other/tool-c) - Third tool',
    ].join('\n')

    const components = parseAwesomeReadme(md)
    expect(components).toHaveLength(3)
    expect(components[0]!.name).toBe('Tool A')
    expect(components[0]!.author).toBe('org')
    expect(components[0]!.githubUrl).toBe('https://github.com/org/tool-a')
    expect(components[1]!.githubUrl).toBeNull()
  })

  test('skips badge/image links', () => {
    const md = [
      '- [badge](http://shields.io/badge)',
      '- [image](https://example.com/logo.png)',
      '- [svg](https://example.com/icon.svg)',
      '- [gif](https://example.com/anim.gif)',
      '- [Real Tool](https://github.com/org/real) - Actual component',
    ].join('\n')

    const components = parseAwesomeReadme(md)
    expect(components).toHaveLength(1)
    expect(components[0]!.name).toBe('Real Tool')
  })

  test('skips anchor links', () => {
    const md = ['- [Section](#section)', '- [Tool](https://github.com/org/tool) - Real'].join('\n')

    const components = parseAwesomeReadme(md)
    expect(components).toHaveLength(1)
  })

  test('handles links without descriptions', () => {
    const md = '- [Tool](https://github.com/org/tool)'
    const components = parseAwesomeReadme(md)
    expect(components).toHaveLength(1)
    expect(components[0]!.description).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

describe('constants', () => {
  test('BACKOFF_CONFIG has expected shape', () => {
    expect(BACKOFF_CONFIG.initialDelay).toBe(2)
    expect(BACKOFF_CONFIG.multiplier).toBe(2)
    expect(BACKOFF_CONFIG.maxDelay).toBe(300)
    expect(BACKOFF_CONFIG.maxRetries).toBe(5)
  })

  test('RATE_LIMITS has all expected registries', () => {
    expect(RATE_LIMITS.skillsmp).toBeDefined()
    expect(RATE_LIMITS.github).toBeDefined()
    expect(RATE_LIMITS.claudemarketplaces).toBeDefined()
    expect(RATE_LIMITS.buildwithclaude).toBeDefined()
    expect(RATE_LIMITS.mcp_so).toBeDefined()
  })

  test('RATE_LIMITS match Python config', () => {
    expect(RATE_LIMITS.skillsmp!.delay).toBe(2)
    expect(RATE_LIMITS.skillsmp!.dailyLimit).toBe(500)
    expect(RATE_LIMITS.github!.delay).toBe(2)
    expect(RATE_LIMITS.github!.dailyLimit).toBe(5000)
    expect(RATE_LIMITS.claudemarketplaces!.delay).toBe(0.5)
    expect(RATE_LIMITS.claudemarketplaces!.dailyLimit).toBeUndefined()
    expect(RATE_LIMITS.buildwithclaude!.delay).toBe(1)
    expect(RATE_LIMITS.buildwithclaude!.dailyLimit).toBeUndefined()
    expect(RATE_LIMITS.mcp_so!.delay).toBe(3)
    expect(RATE_LIMITS.mcp_so!.dailyLimit).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// Command module exports — CLI-specific, tested in packages/cli/
// ---------------------------------------------------------------------------
// The 'registry command module' tests were removed during test migration
// because they import from CLI command modules (../src/commands/registry).
// Those tests remain in packages/cli/test/ as part of CLI command wiring tests.
