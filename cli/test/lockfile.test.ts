import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import * as v from 'valibot'
import { computeHash, formatHash } from '../lib/hash'
import {
  checkStaleness,
  getSchema,
  type LockfileSchema,
  readLockfile,
  registerSchema,
  type StalenessReport,
  writeLockfile,
} from '../lib/lockfile'
import type { LockfileV1, PluginSourcesManifest } from '../lib/schemas'

// Base paths for real test files
const REPO_ROOT = '/private/etc/infra/pub/ai'
const WORKTREE = `${REPO_ROOT}`

// Temp directory created fresh before each test group
let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'lockfile-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Schema registry
// ---------------------------------------------------------------------------

describe('schema registry', () => {
  test('skills schema is pre-registered', () => {
    const schema = getSchema('skills')
    expect(schema).toBeDefined()
    expect(schema!.name).toBe('skills')
    expect(schema!.filename).toBe('skills-lock.json')
  })

  test('plugins schema is pre-registered', () => {
    const schema = getSchema('plugins')
    expect(schema).toBeDefined()
    expect(schema!.name).toBe('plugins')
    expect(schema!.filename).toBe('plugin.sources.json')
  })

  test('returns undefined for unknown schema', () => {
    expect(getSchema('nonexistent')).toBeUndefined()
  })

  test('registerSchema adds a new schema', () => {
    const TestSchema = v.object({ test: v.string() })
    type TestType = v.InferOutput<typeof TestSchema>

    const custom: LockfileSchema<TestType> = {
      name: 'custom-test',
      filename: 'custom.json',
      schema: TestSchema as v.BaseSchema<unknown, TestType, v.BaseIssue<unknown>>,
      async checkStaleness() {
        return { entries: [], allFresh: true }
      },
    }

    registerSchema(custom)
    expect(getSchema('custom-test')).toBeDefined()
    expect(getSchema('custom-test')!.filename).toBe('custom.json')
  })
})

// ---------------------------------------------------------------------------
// readLockfile
// ---------------------------------------------------------------------------

describe('readLockfile', () => {
  test('reads and validates real skills-lock.json', async () => {
    const result = await readLockfile<LockfileV1>('skills', `${REPO_ROOT}/skills-lock.json`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.version).toBe(1)
      expect(result.value.skills.beads).toBeDefined()
    }
  })

  test('reads and validates real plugin.sources.json', async () => {
    const result = await readLockfile<PluginSourcesManifest>(
      'plugins',
      `${WORKTREE}/context/plugins/blog-workflow/.claude-plugin/plugin.sources.json`
    )
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.sources).toBeDefined()
    }
  })

  test('returns error for non-existent file', async () => {
    const result = await readLockfile('skills', join(tmp, 'nonexistent.json'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FAILED')
    }
  })

  test('returns error for invalid JSON', async () => {
    const path = join(tmp, 'bad.json')
    await writeFile(path, '{ invalid json }')
    const result = await readLockfile('skills', path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_INVALID_JSON')
    }
  })

  test('returns error for schema mismatch', async () => {
    const path = join(tmp, 'wrong-schema.json')
    await writeFile(path, JSON.stringify({ version: 99, skills: {} }))
    const result = await readLockfile('skills', path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_VALIDATION_FAILED')
    }
  })

  test('returns error for unregistered schema name', async () => {
    const result = await readLockfile('nonexistent', join(tmp, 'any.json'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SCHEMA_NOT_FOUND')
    }
  })
})

// ---------------------------------------------------------------------------
// writeLockfile
// ---------------------------------------------------------------------------

describe('writeLockfile', () => {
  test('writes formatted JSON with trailing newline', async () => {
    const path = join(tmp, 'output.json')
    const data: LockfileV1 = {
      version: 1,
      skills: {
        test: {
          source: 'test/repo',
          sourceType: 'github',
          computedHash: 'a'.repeat(64),
        },
      },
    }

    const result = await writeLockfile('skills', path, data)
    expect(result.ok).toBe(true)

    const written = await readFile(path, 'utf-8')
    // 2-space indent
    expect(written).toContain('  ')
    // Trailing newline
    expect(written.endsWith('\n')).toBe(true)
    // Valid JSON
    const parsed = JSON.parse(written)
    expect(parsed.version).toBe(1)
  })

  test('validates data before writing', async () => {
    const path = join(tmp, 'invalid-write.json')
    const badData = { version: 99, skills: {} }

    const result = await writeLockfile('skills', path, badData)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_VALIDATION_FAILED')
    }
  })

  test('returns error for unregistered schema', async () => {
    const result = await writeLockfile('nonexistent', join(tmp, 'any.json'), {})
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SCHEMA_NOT_FOUND')
    }
  })

  test('round-trips: write then read produces same data', async () => {
    const path = join(tmp, 'roundtrip.json')
    const data: LockfileV1 = {
      version: 1,
      skills: {
        alpha: {
          source: 'org/alpha',
          sourceType: 'github',
          computedHash: 'b'.repeat(64),
        },
      },
    }

    const writeResult = await writeLockfile('skills', path, data)
    expect(writeResult.ok).toBe(true)

    const readResult = await readLockfile<LockfileV1>('skills', path)
    expect(readResult.ok).toBe(true)
    if (readResult.ok) {
      expect(readResult.value.version).toBe(1)
      expect(readResult.value.skills.alpha.computedHash).toBe('b'.repeat(64))
    }
  })
})

// ---------------------------------------------------------------------------
// checkStaleness — skills
// ---------------------------------------------------------------------------

describe('checkStaleness (skills)', () => {
  test('reports fresh when hash matches', async () => {
    // Create a skill directory structure
    const skillDir = join(tmp, 'context', 'skills', 'test-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: test\n---\n# Test')

    // Compute the actual hash
    const hash = await computeHash(skillDir)

    // Write a lockfile with the correct hash
    const lockPath = join(tmp, 'skills-lock.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        version: 1,
        skills: {
          'test-skill': {
            source: 'local',
            sourceType: 'local',
            computedHash: hash,
          },
        },
      })
    )

    const result = await checkStaleness('skills', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(true)
      expect(result.value.entries).toHaveLength(1)
      expect(result.value.entries[0]!.status).toBe('fresh')
    }
  })

  test('reports stale when hash does not match', async () => {
    const skillDir = join(tmp, 'context', 'skills', 'stale-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: stale\n---\n# Stale')

    const lockPath = join(tmp, 'skills-lock.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        version: 1,
        skills: {
          'stale-skill': {
            source: 'local',
            sourceType: 'local',
            computedHash: 'f'.repeat(64),
          },
        },
      })
    )

    const result = await checkStaleness('skills', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(false)
      expect(result.value.entries[0]!.status).toBe('stale')
    }
  })

  test('reports missing when skill directory does not exist', async () => {
    const lockPath = join(tmp, 'skills-lock.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        version: 1,
        skills: {
          'missing-skill': {
            source: 'nowhere',
            sourceType: 'local',
            computedHash: '0'.repeat(64),
          },
        },
      })
    )

    const result = await checkStaleness('skills', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(false)
      expect(result.value.entries[0]!.status).toBe('missing')
    }
  })
})

// ---------------------------------------------------------------------------
// checkStaleness — plugins
// ---------------------------------------------------------------------------

describe('checkStaleness (plugins)', () => {
  test('reports fresh for matching extended source', async () => {
    // Create a source file
    const sourceFile = join(tmp, 'context', 'output-styles', 'feedback.md')
    await mkdir(join(tmp, 'context', 'output-styles'), { recursive: true })
    await writeFile(sourceFile, '# Feedback\nSubmit your feedback here.')

    const hash = await computeHash(sourceFile)

    const lockPath = join(tmp, 'plugin.sources.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        sources: {
          'styles/feedback.md': {
            source: 'context/output-styles/feedback.md',
            hash: formatHash(hash),
          },
        },
      })
    )

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(true)
      expect(result.value.entries[0]!.status).toBe('fresh')
    }
  })

  test('reports stale for mismatched hash', async () => {
    const sourceFile = join(tmp, 'context', 'file.md')
    await mkdir(join(tmp, 'context'), { recursive: true })
    await writeFile(sourceFile, 'content')

    const lockPath = join(tmp, 'plugin.sources.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        sources: {
          'file.md': {
            source: 'context/file.md',
            hash: 'sha256:' + '0'.repeat(64),
          },
        },
      })
    )

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(false)
      expect(result.value.entries[0]!.status).toBe('stale')
    }
  })

  test('reports missing for non-existent source', async () => {
    const lockPath = join(tmp, 'plugin.sources.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        sources: {
          'missing.md': {
            source: 'context/missing.md',
            hash: 'sha256:' + 'a'.repeat(64),
          },
        },
      })
    )

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.entries[0]!.status).toBe('missing')
    }
  })

  test('reports no-hash for entry without hash', async () => {
    const sourceFile = join(tmp, 'context', 'nohash.md')
    await mkdir(join(tmp, 'context'), { recursive: true })
    await writeFile(sourceFile, 'content')

    const lockPath = join(tmp, 'plugin.sources.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        sources: {
          'nohash.md': {
            source: 'context/nohash.md',
          },
        },
      })
    )

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.entries[0]!.status).toBe('no-hash')
    }
  })

  test('reports no-hash for legacy string source', async () => {
    const sourceFile = join(tmp, 'context', 'legacy.md')
    await mkdir(join(tmp, 'context'), { recursive: true })
    await writeFile(sourceFile, 'content')

    const lockPath = join(tmp, 'plugin.sources.json')
    await writeFile(
      lockPath,
      JSON.stringify({
        sources: {
          'legacy.md': 'context/legacy.md',
        },
      })
    )

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.entries[0]!.status).toBe('no-hash')
    }
  })

  test('handles empty sources manifest', async () => {
    const lockPath = join(tmp, 'empty-sources.json')
    await writeFile(lockPath, JSON.stringify({ sources: {} }))

    const result = await checkStaleness('plugins', lockPath, tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.allFresh).toBe(true)
      expect(result.value.entries).toHaveLength(0)
    }
  })
})

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

describe('error handling', () => {
  test('checkStaleness returns error for unregistered schema', async () => {
    const result = await checkStaleness('nonexistent', '/dev/null', tmp)
    expect(result.ok).toBe(false)
  })

  test('checkStaleness returns error for missing file', async () => {
    const result = await checkStaleness('skills', join(tmp, 'nonexistent.json'), tmp)
    expect(result.ok).toBe(false)
  })
})
