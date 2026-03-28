import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { LocalCommandProvider } from '../../../src/providers/local/command'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-command-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createCommand(baseDir: string, path: string, desc = 'Test command'): Promise<void> {
  const fullPath = join(baseDir, 'content', 'commands', path)
  await mkdir(dirname(fullPath), { recursive: true })
  await writeFile(
    fullPath,
    `---\ndescription: ${desc}\nargument-hint: <arg>\nallowed-tools: Read, Write\n---\n\n# Command\n`
  )
}

async function createCommandRaw(baseDir: string, path: string, content: string): Promise<void> {
  const fullPath = join(baseDir, 'content', 'commands', path)
  await mkdir(dirname(fullPath), { recursive: true })
  await writeFile(fullPath, content)
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalCommandProvider capabilities', () => {
  test('declares command support for search, list, and info', () => {
    const provider = new LocalCommandProvider(tmp)

    expect(provider.id).toBe('local-command')
    expect(provider.displayName).toBe('Local Commands')
    expect(provider.capabilities.search).toContain('command')
    expect(provider.capabilities.list).toContain('command')
    expect(provider.capabilities.info).toContain('command')
    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// discovery
// ---------------------------------------------------------------------------

describe('LocalCommandProvider discovery', () => {
  test('discovers commands in nested directories', async () => {
    await createCommand(tmp, 'skill/create.md', 'Create a skill')
    await createCommand(tmp, 'skill/validate.md', 'Validate a skill')
    await createCommand(tmp, 'plugin/check.md', 'Check a plugin')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(3)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['plugin:check', 'skill:create', 'skill:validate'])
  })

  test('derives name using : separator', async () => {
    await createCommand(tmp, 'context/skill/create.md', 'Create skill')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('context:skill:create')
    expect(result.value[0]?.type).toBe('command')
    expect(result.value[0]?.source).toBe('local')
  })

  test('parses description from frontmatter', async () => {
    await createCommand(tmp, 'test.md', 'A detailed test command')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value[0]?.description).toBe('A detailed test command')
  })

  test('parses allowed-tools into tags', async () => {
    await createCommandRaw(
      tmp,
      'deploy.md',
      '---\ndescription: Deploy app\nallowed-tools: Read, Write, Bash(docker:*)\n---\n\n# Deploy\n'
    )

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value[0]?.tags).toEqual(['Read', 'Write', 'Bash(docker:*)'])
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalCommandProvider search', () => {
  test('filters by query on name and description', async () => {
    await createCommand(tmp, 'skill/create.md', 'Create a new skill')
    await createCommand(tmp, 'plugin/check.md', 'Check plugin validity')
    await createCommand(tmp, 'skill/validate.md', 'Validate skill structure')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.search({ query: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    // Matches "skill:create" (name + description), "skill:validate" (name)
    expect(result.value.items).toHaveLength(2)
    const names = result.value.items.map((c) => c.name).sort()
    expect(names).toEqual(['skill:create', 'skill:validate'])
  })

  test('returns empty for non-command type', async () => {
    await createCommand(tmp, 'test.md')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.search({ query: 'test', type: 'rule' })

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

describe('LocalCommandProvider list', () => {
  test('returns all commands', async () => {
    await createCommand(tmp, 'alpha.md', 'Alpha cmd')
    await createCommand(tmp, 'nested/beta.md', 'Beta cmd')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['alpha', 'nested:beta'])
  })

  test('returns empty when no commands directory exists', async () => {
    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalCommandProvider info', () => {
  test('returns single command by name', async () => {
    await createCommand(tmp, 'skill/create.md', 'Create a new skill')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.info('skill:create', 'command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('command')
    expect(result.value.name).toBe('skill:create')
    expect(result.value.description).toBe('Create a new skill')
    expect(result.value.tags).toEqual(['Read', 'Write'])
    expect(result.value.localPath).toBe(join(tmp, 'content', 'commands', 'skill', 'create.md'))
  })

  test('returns error for missing command', async () => {
    const provider = new LocalCommandProvider(tmp)
    const result = await provider.info('nonexistent', 'command')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalCommandProvider(tmp)
    const result = await provider.info('something', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})

// ---------------------------------------------------------------------------
// edge cases
// ---------------------------------------------------------------------------

describe('LocalCommandProvider edge cases', () => {
  test('handles commands without frontmatter gracefully', async () => {
    await createCommandRaw(tmp, 'bare.md', '# A bare command\n\nNo frontmatter at all.\n')

    const provider = new LocalCommandProvider(tmp)
    const result = await provider.list('command')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('bare')
    expect(result.value[0]?.description).toBe('')
    expect(result.value[0]?.tags).toBeUndefined()
  })
})
