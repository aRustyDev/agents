import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { LocalAgentProvider } from '../../../src/providers/local/agent'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-agent-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createAgent(dir: string, name: string, desc = 'Test agent'): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(
    join(dir, `${name}.md`),
    `---\nname: ${name}\ndescription: ${desc}\ntools: Read, Write\n---\n\n# ${name}\n`
  )
}

async function createAppAgent(dir: string): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(join(dir, 'pyproject.toml'), '[project]\nname = "app"\n')
  await writeFile(join(dir, 'README.md'), '# App\n')
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalAgentProvider capabilities', () => {
  test('declares agent support for search, list, info', () => {
    const provider = new LocalAgentProvider(tmp)

    expect(provider.id).toBe('local-agent')
    expect(provider.displayName).toBe('Local Agents')
    expect(provider.capabilities.search).toContain('agent')
    expect(provider.capabilities.list).toContain('agent')
    expect(provider.capabilities.info).toContain('agent')
    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalAgentProvider search', () => {
  test('discovers agents in nested category dirs', async () => {
    const coreDir = join(tmp, 'content', 'agents', 'development', 'core')
    const infraDir = join(tmp, 'content', 'agents', 'infrastructure')

    await createAgent(coreDir, 'frontend-developer', 'Frontend expert')
    await createAgent(coreDir, 'backend-developer', 'Backend expert')
    await createAgent(infraDir, 'devops-engineer', 'DevOps expert')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(3)
    const names = result.value.items.map((c) => c.name).sort()
    expect(names).toEqual(['backend-developer', 'devops-engineer', 'frontend-developer'])
  })

  test('excludes dirs with pyproject.toml', async () => {
    const coreDir = join(tmp, 'content', 'agents', 'development', 'core')
    const appDir = join(tmp, 'content', 'agents', 'skill-reviewer')

    await createAgent(coreDir, 'frontend-developer')
    await createAppAgent(appDir)
    // Also add an .md to the app dir to confirm the whole subtree is skipped
    await writeFile(
      join(appDir, 'agent.md'),
      '---\nname: hidden\ndescription: Should not appear\n---\n'
    )

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('frontend-developer')
  })

  test('excludes README.md and prompt.md', async () => {
    const dir = join(tmp, 'content', 'agents', 'meta')
    await mkdir(dir, { recursive: true })
    await writeFile(
      join(dir, 'README.md'),
      '---\nname: readme\ndescription: Should not appear\n---\n'
    )
    await writeFile(
      join(dir, 'prompt.md'),
      '---\nname: prompt\ndescription: Should not appear\n---\n'
    )
    await createAgent(dir, 'real-agent', 'Included')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('real-agent')
  })

  test('excludes underscore-prefixed dirs', async () => {
    const hiddenDir = join(tmp, 'content', 'agents', '_context-agents')
    const visibleDir = join(tmp, 'content', 'agents', 'meta')

    await createAgent(hiddenDir, 'hidden-agent', 'Should not appear')
    await createAgent(visibleDir, 'visible-agent', 'Should appear')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('visible-agent')
  })

  test('filters by query on name and description', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await createAgent(dir, 'frontend-developer', 'Expert UI engineer')
    await createAgent(dir, 'backend-developer', 'Server-side specialist')
    await createAgent(dir, 'devops-engineer', 'Infrastructure automation')

    const provider = new LocalAgentProvider(tmp)

    // Filter by name
    const nameResult = await provider.search({ query: 'frontend' })
    expect(nameResult.ok).toBe(true)
    if (!nameResult.ok) return
    expect(nameResult.value.items).toHaveLength(1)
    expect(nameResult.value.items[0]?.name).toBe('frontend-developer')

    // Filter by description
    const descResult = await provider.search({ query: 'infrastructure' })
    expect(descResult.ok).toBe(true)
    if (!descResult.ok) return
    expect(descResult.value.items).toHaveLength(1)
    expect(descResult.value.items[0]?.name).toBe('devops-engineer')
  })

  test('returns empty for non-agent type', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await createAgent(dir, 'frontend-developer')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '', type: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })

  test('paginates results', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await createAgent(dir, 'alpha', 'Agent alpha')
    await createAgent(dir, 'beta', 'Agent beta')
    await createAgent(dir, 'gamma', 'Agent gamma')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.search({ query: '', page: 1, limit: 2 })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(2)
    expect(result.value.hasMore).toBe(true)
    expect(result.value.total).toBe(3)
    expect(result.value.page).toBe(1)
    expect(result.value.pageSize).toBe(2)
  })
})

// ---------------------------------------------------------------------------
// list
// ---------------------------------------------------------------------------

describe('LocalAgentProvider list', () => {
  test('returns all agents', async () => {
    const dir1 = join(tmp, 'content', 'agents', 'dev', 'core')
    const dir2 = join(tmp, 'content', 'agents', 'infra')

    await createAgent(dir1, 'frontend-developer', 'UI expert')
    await createAgent(dir2, 'devops-engineer', 'DevOps expert')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.list('agent')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['devops-engineer', 'frontend-developer'])
  })

  test('returns empty for unsupported type', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await createAgent(dir, 'some-agent')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.list('skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalAgentProvider info', () => {
  test('returns agent detail by name', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev', 'core')
    await createAgent(dir, 'frontend-developer', 'Expert UI engineer')

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.info('frontend-developer', 'agent')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('agent')
    expect(result.value.name).toBe('frontend-developer')
    expect(result.value.description).toBe('Expert UI engineer')
    expect(result.value.localPath).toBe(join(dir, 'frontend-developer.md'))
    expect(result.value.source).toBe('content/agents/dev/core/frontend-developer.md')
  })

  test('returns error for unknown agent', async () => {
    const provider = new LocalAgentProvider(tmp)
    const result = await provider.info('nonexistent', 'agent')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalAgentProvider(tmp)
    const result = await provider.info('something', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})

// ---------------------------------------------------------------------------
// Component shape
// ---------------------------------------------------------------------------

describe('LocalAgentProvider component shape', () => {
  test('agent Component has correct shape (type, source, tags from tools)', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await mkdir(dir, { recursive: true })
    await writeFile(
      join(dir, 'test-agent.md'),
      '---\nname: test-agent\ndescription: A test agent\ntools: Read, Write, Edit, Bash\n---\n\n# test-agent\n'
    )

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.list('agent')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    const agent = result.value[0]!
    expect(agent.type).toBe('agent')
    expect(agent.name).toBe('test-agent')
    expect(agent.description).toBe('A test agent')
    expect(agent.source).toBe('content/agents/dev/test-agent.md')
    expect(agent.localPath).toBe(join(dir, 'test-agent.md'))
    expect(agent.tags).toEqual(['Read', 'Write', 'Edit', 'Bash'])
  })

  test('derives name from filename when frontmatter name missing', async () => {
    const dir = join(tmp, 'content', 'agents', 'dev')
    await mkdir(dir, { recursive: true })
    await writeFile(
      join(dir, 'my-cool-agent.md'),
      '---\ndescription: An agent without a name field\ntools: Glob\n---\n\n# Agent\n'
    )

    const provider = new LocalAgentProvider(tmp)
    const result = await provider.list('agent')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('my-cool-agent')
    expect(result.value[0]?.description).toBe('An agent without a name field')
  })
})

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe('LocalAgentProvider edge cases', () => {
  test('handles missing agents dir gracefully (empty, no error)', async () => {
    // tmp has no content/agents/ directory at all
    const provider = new LocalAgentProvider(tmp)

    const searchResult = await provider.search({ query: '' })
    expect(searchResult.ok).toBe(true)
    if (!searchResult.ok) return
    expect(searchResult.value.items).toEqual([])

    const listResult = await provider.list('agent')
    expect(listResult.ok).toBe(true)
    if (!listResult.ok) return
    expect(listResult.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// add / remove (unsupported)
// ---------------------------------------------------------------------------

describe('LocalAgentProvider unsupported ops', () => {
  test('add returns unsupported error', async () => {
    const provider = new LocalAgentProvider(tmp)
    const result = await provider.add('some-source', {})

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })

  test('remove returns unsupported error', async () => {
    const provider = new LocalAgentProvider(tmp)
    const result = await provider.remove('some-agent', 'agent')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})
