import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { LocalRuleProvider } from '../../lib/component/provider-rule'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-rule-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createRule(baseDir: string, path: string, heading = 'Test Rule'): Promise<void> {
  const fullPath = join(baseDir, 'content', 'rules', path)
  await mkdir(dirname(fullPath), { recursive: true })
  await writeFile(fullPath, `# ${heading}\n\nRule content here.\n`)
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalRuleProvider capabilities', () => {
  test('declares rule support for search, list, and info', () => {
    const provider = new LocalRuleProvider(tmp)

    expect(provider.id).toBe('local-rule')
    expect(provider.displayName).toBe('Local Rules')
    expect(provider.capabilities.search).toContain('rule')
    expect(provider.capabilities.list).toContain('rule')
    expect(provider.capabilities.info).toContain('rule')
    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// discovery
// ---------------------------------------------------------------------------

describe('LocalRuleProvider discovery', () => {
  test('discovers rules in nested directories', async () => {
    await createRule(tmp, 'agent/hooks.md', 'Claude Code Hooks')
    await createRule(tmp, 'agent/skills/gap-detection.md', 'Skill Gap Detection')
    await createRule(tmp, 'pre-commit/bash.md', 'Bash Linting Rules')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.list('rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(3)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['agent/hooks', 'agent/skills/gap-detection', 'pre-commit/bash'])
  })

  test('derives name from path with / separator', async () => {
    await createRule(tmp, 'cloudflare/wrangler.md', 'Wrangler Config')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.list('rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('cloudflare/wrangler')
    expect(result.value[0]?.type).toBe('rule')
    expect(result.value[0]?.source).toBe('local')
  })

  test('extracts description from first H1 heading', async () => {
    await createRule(tmp, 'github/actions.md', 'GitHub Actions Rules')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.list('rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value[0]?.description).toBe('GitHub Actions Rules')
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalRuleProvider search', () => {
  test('filters by query on name and description', async () => {
    await createRule(tmp, 'agent/hooks.md', 'Claude Code Hooks')
    await createRule(tmp, 'pre-commit/bash.md', 'Bash Linting Rules')
    await createRule(tmp, 'github/actions.md', 'GitHub Actions')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.search({ query: 'bash' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('pre-commit/bash')
  })

  test('returns empty for non-rule type', async () => {
    await createRule(tmp, 'agent/hooks.md')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.search({ query: 'hooks', type: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// list
// ---------------------------------------------------------------------------

describe('LocalRuleProvider list', () => {
  test('returns all rules', async () => {
    await createRule(tmp, 'alpha.md', 'Alpha Rule')
    await createRule(tmp, 'nested/beta.md', 'Beta Rule')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.list('rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['alpha', 'nested/beta'])
  })

  test('returns empty when no rules directory exists', async () => {
    const provider = new LocalRuleProvider(tmp)
    const result = await provider.list('rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalRuleProvider info', () => {
  test('returns single rule by name', async () => {
    await createRule(tmp, 'agent/hooks.md', 'Claude Code Hooks')

    const provider = new LocalRuleProvider(tmp)
    const result = await provider.info('agent/hooks', 'rule')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('rule')
    expect(result.value.name).toBe('agent/hooks')
    expect(result.value.description).toBe('Claude Code Hooks')
    expect(result.value.localPath).toBe(join(tmp, 'content', 'rules', 'agent', 'hooks.md'))
  })

  test('returns error for missing rule', async () => {
    const provider = new LocalRuleProvider(tmp)
    const result = await provider.info('nonexistent', 'rule')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_RULE_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalRuleProvider(tmp)
    const result = await provider.info('something', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED_TYPE')
  })
})
