import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { LocalPluginProvider } from '../../../src/providers/local/plugin'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-plugin-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createPlugin(
  baseDir: string,
  name: string,
  desc = 'Test plugin',
  extra: Record<string, unknown> = {}
): Promise<void> {
  const pluginDir = join(baseDir, 'content', 'plugins', name, '.claude-plugin')
  await mkdir(pluginDir, { recursive: true })
  await writeFile(
    join(pluginDir, 'plugin.json'),
    JSON.stringify({
      name,
      version: '1.0.0',
      description: desc,
      author: { name: 'Test Author' },
      keywords: ['test'],
      homepage: 'https://example.com',
      ...extra,
    })
  )
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalPluginProvider capabilities', () => {
  test('declares plugin support for search, list, info', () => {
    const provider = new LocalPluginProvider(tmp)

    expect(provider.id).toBe('local-plugin')
    expect(provider.displayName).toBe('Local Plugins')
    expect(provider.capabilities.search).toContain('plugin')
    expect(provider.capabilities.list).toContain('plugin')
    expect(provider.capabilities.info).toContain('plugin')
  })

  test('does not support add, remove, publish, outdated, update', () => {
    const provider = new LocalPluginProvider(tmp)

    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual([])
    expect(provider.capabilities.outdated).toEqual([])
    expect(provider.capabilities.update).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalPluginProvider search', () => {
  test('discovers plugins in nested dirs', async () => {
    await createPlugin(tmp, 'blog-workflow', 'Blog writing workflow')
    await createPlugin(tmp, 'terraform-dev', 'Terraform development')

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(2)
    const names = result.value.items.map((c) => c.name).sort()
    expect(names).toEqual(['blog-workflow', 'terraform-dev'])
  })

  test('excludes .template directory', async () => {
    await createPlugin(tmp, 'real-plugin', 'A real plugin')

    // Create a .template plugin that should be excluded
    const templateDir = join(tmp, 'content', 'plugins', '.template', '.claude-plugin')
    await mkdir(templateDir, { recursive: true })
    await writeFile(
      join(templateDir, 'plugin.json'),
      JSON.stringify({
        name: 'template-plugin',
        version: '0.0.0',
        description: 'Template',
        author: { name: 'Template' },
      })
    )

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('real-plugin')
  })

  test('filters by query on name, description, and keywords', async () => {
    await createPlugin(tmp, 'blog-workflow', 'Blog writing workflow', {
      keywords: ['blog', 'writing'],
    })
    await createPlugin(tmp, 'terraform-dev', 'Terraform development toolkit', {
      keywords: ['terraform', 'iac'],
    })

    const provider = new LocalPluginProvider(tmp)

    // Search by name
    const byName = await provider.search({ query: 'blog' })
    expect(byName.ok).toBe(true)
    if (byName.ok) {
      expect(byName.value.items).toHaveLength(1)
      expect(byName.value.items[0]?.name).toBe('blog-workflow')
    }

    // Search by description
    const byDesc = await provider.search({ query: 'toolkit' })
    expect(byDesc.ok).toBe(true)
    if (byDesc.ok) {
      expect(byDesc.value.items).toHaveLength(1)
      expect(byDesc.value.items[0]?.name).toBe('terraform-dev')
    }

    // Search by keyword
    const byTag = await provider.search({ query: 'iac' })
    expect(byTag.ok).toBe(true)
    if (byTag.ok) {
      expect(byTag.value.items).toHaveLength(1)
      expect(byTag.value.items[0]?.name).toBe('terraform-dev')
    }
  })

  test('returns empty for non-plugin type', async () => {
    await createPlugin(tmp, 'some-plugin')

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '', type: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })

  test('paginates results', async () => {
    await createPlugin(tmp, 'alpha', 'Alpha plugin')
    await createPlugin(tmp, 'beta', 'Beta plugin')
    await createPlugin(tmp, 'gamma', 'Gamma plugin')

    const provider = new LocalPluginProvider(tmp)

    const page1 = await provider.search({ query: '', page: 1, limit: 2 })
    expect(page1.ok).toBe(true)
    if (!page1.ok) return

    expect(page1.value.items).toHaveLength(2)
    expect(page1.value.hasMore).toBe(true)
    expect(page1.value.total).toBe(3)
    expect(page1.value.page).toBe(1)
    expect(page1.value.pageSize).toBe(2)

    const page2 = await provider.search({ query: '', page: 2, limit: 2 })
    expect(page2.ok).toBe(true)
    if (!page2.ok) return

    expect(page2.value.items).toHaveLength(1)
    expect(page2.value.hasMore).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// list
// ---------------------------------------------------------------------------

describe('LocalPluginProvider list', () => {
  test('returns all discovered plugins', async () => {
    await createPlugin(tmp, 'blog-workflow', 'Blog writing workflow')
    await createPlugin(tmp, 'terraform-dev', 'Terraform toolkit')

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.list('plugin')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['blog-workflow', 'terraform-dev'])
  })

  test('returns empty for unsupported type', async () => {
    await createPlugin(tmp, 'some-plugin')

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.list('skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalPluginProvider info', () => {
  test('returns plugin detail by name', async () => {
    await createPlugin(tmp, 'blog-workflow', 'Blog writing workflow', {
      version: '2.1.0',
      keywords: ['blog', 'writing'],
      homepage: 'https://blog.example.com',
    })

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.info('blog-workflow', 'plugin')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('plugin')
    expect(result.value.name).toBe('blog-workflow')
    expect(result.value.description).toBe('Blog writing workflow')
    expect(result.value.version).toBe('2.1.0')
    expect(result.value.author).toBe('Test Author')
    expect(result.value.tags).toEqual(['blog', 'writing'])
    expect(result.value.url).toBe('https://blog.example.com')
    expect(result.value.localPath).toBe(join(tmp, 'content', 'plugins', 'blog-workflow'))
    expect(result.value.source).toBe(join('content', 'plugins', 'blog-workflow'))
  })

  test('returns error for unknown plugin', async () => {
    const provider = new LocalPluginProvider(tmp)
    const result = await provider.info('nonexistent', 'plugin')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalPluginProvider(tmp)
    const result = await provider.info('something', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})

// ---------------------------------------------------------------------------
// Component shape
// ---------------------------------------------------------------------------

describe('LocalPluginProvider component shape', () => {
  test('maps manifest fields to Component correctly', async () => {
    await createPlugin(tmp, 'my-plugin', 'My description', {
      version: '3.0.0',
      author: { name: 'Jane Doe', email: 'jane@example.com' },
      keywords: ['alpha', 'beta'],
      homepage: 'https://myplugin.dev',
    })

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    const component = result.value.items[0]!
    expect(component.type).toBe('plugin')
    expect(component.name).toBe('my-plugin')
    expect(component.description).toBe('My description')
    expect(component.version).toBe('3.0.0')
    expect(component.author).toBe('Jane Doe')
    expect(component.tags).toEqual(['alpha', 'beta'])
    expect(component.url).toBe('https://myplugin.dev')
    expect(component.localPath).toBe(join(tmp, 'content', 'plugins', 'my-plugin'))
    expect(component.source).toBe(join('content', 'plugins', 'my-plugin'))
  })
})

// ---------------------------------------------------------------------------
// Error resilience
// ---------------------------------------------------------------------------

describe('LocalPluginProvider error resilience', () => {
  test('skips invalid plugin.json gracefully', async () => {
    // Create a valid plugin
    await createPlugin(tmp, 'good-plugin', 'Works fine')

    // Create a directory with invalid JSON in plugin.json
    const badDir = join(tmp, 'content', 'plugins', 'bad-plugin', '.claude-plugin')
    await mkdir(badDir, { recursive: true })
    await writeFile(join(badDir, 'plugin.json'), '{ not valid json !!!')

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    // Only the valid plugin should appear
    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('good-plugin')
  })

  // TODO: SDK plugin provider does not perform manifest schema validation.
  // If schema validation is added to the SDK, re-enable this test.
  test.skip('skips plugin with schema validation errors', async () => {
    await createPlugin(tmp, 'good-plugin', 'Works fine')

    // Create a plugin with invalid schema (missing required fields)
    const badDir = join(tmp, 'content', 'plugins', 'schema-fail', '.claude-plugin')
    await mkdir(badDir, { recursive: true })
    await writeFile(join(badDir, 'plugin.json'), JSON.stringify({ name: 'schema-fail' }))

    const provider = new LocalPluginProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('good-plugin')
  })

  test('handles missing plugins directory gracefully', async () => {
    // tmp exists but has no content/plugins/ directory
    const provider = new LocalPluginProvider(tmp)

    const searchResult = await provider.search({ query: '' })
    expect(searchResult.ok).toBe(true)
    if (searchResult.ok) {
      expect(searchResult.value.items).toEqual([])
      expect(searchResult.value.total).toBe(0)
    }

    const listResult = await provider.list('plugin')
    expect(listResult.ok).toBe(true)
    if (listResult.ok) {
      expect(listResult.value).toEqual([])
    }
  })
})

// ---------------------------------------------------------------------------
// Unsupported operations
// ---------------------------------------------------------------------------

describe('LocalPluginProvider unsupported operations', () => {
  test('add returns error', async () => {
    const provider = new LocalPluginProvider(tmp)
    const result = await provider.add('some-source', {})

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })

  test('remove returns error', async () => {
    const provider = new LocalPluginProvider(tmp)
    const result = await provider.remove('something', 'plugin')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})
