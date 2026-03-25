import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdtemp, readFile, realpath } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { initComponent } from '../../src/lib/init-component'

// ---------------------------------------------------------------------------
// Shared temp directory
// ---------------------------------------------------------------------------

let root: string

beforeAll(async () => {
  root = await realpath(await mkdtemp(join(tmpdir(), 'init-component-test-')))
})

afterAll(async () => {
  const { rm } = await import('node:fs/promises')
  await rm(root, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Persona scaffolding
// ---------------------------------------------------------------------------

describe('initComponent — persona', () => {
  test('creates directory with template files', async () => {
    const result = await initComponent('persona', 'test-persona', { cwd: root })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(existsSync(result.value.path)).toBe(true)
      expect(result.value.files).toContain('PERSONA.md')
    }
  })

  test('replaces {{name}} placeholders in persona template', async () => {
    const dir = join(root, 'test-persona')
    const content = await readFile(join(dir, 'PERSONA.md'), 'utf-8')
    expect(content).toContain('name: test-persona')
    expect(content).toContain('# test-persona')
    expect(content).not.toContain('{{name}}')
  })

  test('fails if directory already exists', async () => {
    const result = await initComponent('persona', 'test-persona', { cwd: root })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_EXISTS')
    }
  })
})

// ---------------------------------------------------------------------------
// Hook scaffolding
// ---------------------------------------------------------------------------

describe('initComponent — hook', () => {
  test('creates directory with hook.sh', async () => {
    const result = await initComponent('hook', 'my-hook', { cwd: root })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.files).toContain('hook.sh')
    }
  })

  test('replaces {{name}} placeholders in hook template', async () => {
    const dir = join(root, 'my-hook')
    const content = await readFile(join(dir, 'hook.sh'), 'utf-8')
    expect(content).toContain('# Hook: my-hook')
    expect(content).toContain('echo "Hook my-hook executed"')
    expect(content).not.toContain('{{name}}')
  })
})

// ---------------------------------------------------------------------------
// Error cases
// ---------------------------------------------------------------------------

describe('initComponent — error handling', () => {
  test('fails for types without templateDir (skill has its own init)', async () => {
    const result = await initComponent('skill', 'some-skill', { cwd: root })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_TEMPLATE')
    }
  })

  test('fails for types without templateDir (agent)', async () => {
    const result = await initComponent('agent', 'some-agent', { cwd: root })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_TEMPLATE')
    }
  })

  test('fails for types without templateDir (mcp-server)', async () => {
    const result = await initComponent('mcp-server', 'my-server', { cwd: root })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_TEMPLATE')
    }
  })

  test('returns path and files list on success', async () => {
    const result = await initComponent('persona', 'detail-check', { cwd: root })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.path).toBe(join(root, 'detail-check'))
      expect(Array.isArray(result.value.files)).toBe(true)
      expect(result.value.files.length).toBeGreaterThan(0)
    }
  })
})
