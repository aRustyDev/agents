import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { LocalOutputStyleProvider } from '../../src/lib/component/provider-output-style'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-output-style-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createStyle(dir: string, name: string, content: string): Promise<void> {
  const stylesDir = join(dir, 'content', 'output-styles')
  await mkdir(stylesDir, { recursive: true })
  await writeFile(join(stylesDir, `${name}.md`), content)
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalOutputStyleProvider capabilities', () => {
  test('declares output-style support for search, list, info', () => {
    const provider = new LocalOutputStyleProvider(tmp)

    expect(provider.id).toBe('local-output-style')
    expect(provider.displayName).toBe('Local Output Styles')
    expect(provider.capabilities.search).toContain('output-style')
    expect(provider.capabilities.list).toContain('output-style')
    expect(provider.capabilities.info).toContain('output-style')
    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual([])
    expect(provider.capabilities.outdated).toEqual([])
    expect(provider.capabilities.update).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// discovery
// ---------------------------------------------------------------------------

describe('LocalOutputStyleProvider discovery', () => {
  test('discovers output style files', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')
    await createStyle(tmp, 'code-review', '# Code Review\n\nStyle for reviews.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['code-review', 'feedback-submission'])
  })

  test('excludes TODO.md', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')
    // Write TODO.md directly into the output-styles directory
    const stylesDir = join(tmp, 'content', 'output-styles')
    await writeFile(join(stylesDir, 'TODO.md'), '# TODO\n\n- Add more styles')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('feedback-submission')
  })

  test('excludes dot-prefixed files', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')
    const stylesDir = join(tmp, 'content', 'output-styles')
    await writeFile(join(stylesDir, '.hidden-style.md'), '# Hidden\n\nDo not discover.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('feedback-submission')
  })

  test('name derived from filename by stripping .md', async () => {
    await createStyle(tmp, 'my-custom-style', '# Custom\n\nA custom style.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]?.name).toBe('my-custom-style')
    expect(result.value[0]?.type).toBe('output-style')
  })

  test('description extracted from first paragraph after heading', async () => {
    const content = [
      '# Feedback Submission',
      '',
      'Output style for formatting user feedback submissions.',
      '',
      '## Section Two',
      '',
      'More details here.',
    ].join('\n')

    await createStyle(tmp, 'feedback-submission', content)

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value[0]?.description).toBe(
      'Output style for formatting user feedback submissions.'
    )
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalOutputStyleProvider search', () => {
  test('filters by query matching name', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')
    await createStyle(tmp, 'code-review', '# Code Review\n\nStyle for reviews.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.search({ query: 'feedback' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('feedback-submission')
  })

  test('returns empty for non-output-style type', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.search({ query: 'feedback', type: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// missing directory
// ---------------------------------------------------------------------------

describe('LocalOutputStyleProvider missing directory', () => {
  test('handles missing directory gracefully', async () => {
    // tmp has no content/output-styles/ directory
    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.list('output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })

  test('search returns empty page when directory missing', async () => {
    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.search({ query: 'anything' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.total).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalOutputStyleProvider info', () => {
  test('returns single style by name', async () => {
    await createStyle(tmp, 'feedback-submission', '# Feedback\n\nStyle for feedback.')
    await createStyle(tmp, 'code-review', '# Code Review\n\nStyle for reviews.')

    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.info('feedback-submission', 'output-style')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.name).toBe('feedback-submission')
    expect(result.value.type).toBe('output-style')
    expect(result.value.description).toBe('Style for feedback.')
    expect(result.value.localPath).toBe(
      join(tmp, 'content', 'output-styles', 'feedback-submission.md')
    )
  })

  test('returns error for missing style', async () => {
    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.info('nonexistent', 'output-style')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_OUTPUT_STYLE_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalOutputStyleProvider(tmp)
    const result = await provider.info('something', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED_TYPE')
  })
})
