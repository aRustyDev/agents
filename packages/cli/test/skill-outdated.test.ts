/**
 * Tests for lib/skill-outdated.ts
 *
 * Uses bun's mock.module() to replace dependency modules before importing
 * the module under test via dynamic import().
 */

import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

// ---------------------------------------------------------------------------
// Temp directory lifecycle
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'outdated-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Write a minimal valid lockfile to disk. */
async function writeLockfile(
  dir: string,
  skills: Record<string, { source: string; sourceType: string; computedHash: string }>
): Promise<string> {
  const path = join(dir, 'skills-lock.json')
  await writeFile(path, JSON.stringify({ version: 1, skills }, null, 2))
  return path
}

/** Create a skill directory with a single SKILL.md file. */
async function createSkillDir(base: string, name: string, content: string): Promise<void> {
  const dir = join(base, 'content', 'skills', name)
  await mkdir(dir, { recursive: true })
  await writeFile(join(dir, 'SKILL.md'), content)
}

// ---------------------------------------------------------------------------
// github: "current" when hash matches
// ---------------------------------------------------------------------------

describe('github source', () => {
  test('reports "current" when fetchSkillFolderHash returns matching hash', async () => {
    const HASH = 'a'.repeat(64)

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => HASH,
      lsRemote: async () => ({ ok: true, value: 'unused' }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'my-skill': { source: 'owner/repo', sourceType: 'github', computedHash: HASH },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('current')
    expect(results[0]!.skill).toBe('my-skill')
    expect(results[0]!.currentHash).toBe(HASH)
    expect(results[0]!.remoteHash).toBe(HASH)
  })

  test('reports "outdated" when fetchSkillFolderHash returns different hash', async () => {
    const LOCAL_HASH = 'a'.repeat(64)
    const REMOTE_HASH = 'b'.repeat(64)

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => REMOTE_HASH,
      lsRemote: async () => ({ ok: true, value: 'unused' }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'my-skill': { source: 'owner/repo', sourceType: 'github', computedHash: LOCAL_HASH },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('outdated')
    expect(results[0]!.currentHash).toBe(LOCAL_HASH)
    expect(results[0]!.remoteHash).toBe(REMOTE_HASH)
  })

  test('reports "unavailable" when Trees API returns null', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: true, value: 'unused' }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'gone-skill': { source: 'owner/deleted', sourceType: 'github', computedHash: 'c'.repeat(64) },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('unavailable')
    expect(results[0]!.error).toContain('not found')
  })
})

// ---------------------------------------------------------------------------
// local source
// ---------------------------------------------------------------------------

describe('local source', () => {
  test('reports "current" when directory hash matches', async () => {
    await createSkillDir(tmp, 'local-skill', '# Skill\nStable content')

    // Compute the real hash of the directory we just created
    const { hashDirectory } = await import('@agents/core/hash')
    const realHash = await hashDirectory(join(tmp, 'content', 'skills', 'local-skill'))

    // No need to mock hash module for local -- use real implementation
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'local-skill': { source: 'local', sourceType: 'local', computedHash: realHash },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('current')
    expect(results[0]!.remoteHash).toBe(realHash)
  })

  test('reports "outdated" when directory hash differs', async () => {
    await createSkillDir(tmp, 'changed-skill', '# Changed content')

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'changed-skill': {
        source: 'local',
        sourceType: 'local',
        computedHash: 'f'.repeat(64),
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('outdated')
  })

  test('reports "unavailable" when directory is missing', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'missing-skill': {
        source: 'local',
        sourceType: 'local',
        computedHash: '0'.repeat(64),
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('unavailable')
    expect(results[0]!.error).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// Empty / missing lockfile
// ---------------------------------------------------------------------------

describe('edge cases', () => {
  test('empty lock file returns empty array', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {})

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(0)
  })

  test('no lock file returns empty array', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    // Point cwd to a directory with no skills-lock.json
    const results = await checkOutdated({ cwd: tmp })
    expect(results).toHaveLength(0)
  })

  test('unknown source type returns "unknown" status', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'weird-skill': {
        source: 'somewhere',
        sourceType: 'ftp',
        computedHash: 'd'.repeat(64),
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('unknown')
    expect(results[0]!.error).toContain('Unknown source type')
  })
})

// ---------------------------------------------------------------------------
// --from-url timeout
// ---------------------------------------------------------------------------

describe('--from-url', () => {
  test(
    'timeout produces OutdatedError with E_FETCH_TIMEOUT',
    async () => {
      mock.module('../src/lib/git', () => ({
        fetchSkillFolderHash: async () => null,
        lsRemote: async () => ({ ok: false, error: { message: 'unused' } }),
      }))

      const { resolveInput, OutdatedError } = await import('../src/lib/skill-outdated')

      // Start a server that never responds
      const server = Bun.serve({
        port: 0,
        async fetch() {
          // Hang for 30 seconds (well past the 5s timeout)
          await new Promise((resolve) => setTimeout(resolve, 30_000))
          return new Response('too late')
        },
      })

      try {
        const result = await resolveInput({
          fromUrl: `http://localhost:${server.port}/lockfile.json`,
        })

        expect(result.ok).toBe(false)
        if (!result.ok) {
          expect(result.error.code).toBe('E_FETCH_TIMEOUT')
          expect(result.error).toBeInstanceOf(OutdatedError)
        }
      } finally {
        server.stop(true)
      }
    },
    { timeout: 15_000 }
  )
})

// ---------------------------------------------------------------------------
// git source
// ---------------------------------------------------------------------------

describe('git source', () => {
  test('reports "current" when lsRemote returns matching hash', async () => {
    const HASH = 'e'.repeat(64)

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: true, value: HASH }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'git-skill': {
        source: 'https://example.com/repo.git',
        sourceType: 'git',
        computedHash: HASH,
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('current')
  })

  test('reports "outdated" when lsRemote returns different hash', async () => {
    const REMOTE = 'b'.repeat(64)

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({ ok: true, value: REMOTE }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'git-skill': {
        source: 'https://example.com/repo.git',
        sourceType: 'git',
        computedHash: 'a'.repeat(64),
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('outdated')
  })

  test('reports "unavailable" when lsRemote fails', async () => {
    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => null,
      lsRemote: async () => ({
        ok: false,
        error: { message: 'Network error', code: 'E_GIT_LS_REMOTE' },
      }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'git-skill': {
        source: 'https://example.com/dead-repo.git',
        sourceType: 'git',
        computedHash: 'f'.repeat(64),
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('unavailable')
    expect(results[0]!.error).toContain('Network error')
  })
})

// ---------------------------------------------------------------------------
// Mixed sources
// ---------------------------------------------------------------------------

describe('mixed sources', () => {
  test('handles github + local entries in a single lockfile', async () => {
    // Set up a real local skill directory
    await createSkillDir(tmp, 'local-one', '# Local Skill')

    const { hashDirectory } = await import('@agents/core/hash')
    const localHash = await hashDirectory(join(tmp, 'content', 'skills', 'local-one'))

    const GITHUB_HASH = 'b'.repeat(64)

    mock.module('../src/lib/git', () => ({
      fetchSkillFolderHash: async () => GITHUB_HASH,
      lsRemote: async () => ({ ok: true, value: 'unused' }),
    }))

    const { checkOutdated } = await import('../src/lib/skill-outdated')

    const lockPath = await writeLockfile(tmp, {
      'gh-skill': {
        source: 'owner/repo',
        sourceType: 'github',
        computedHash: GITHUB_HASH,
      },
      'local-one': {
        source: 'local',
        sourceType: 'local',
        computedHash: localHash,
      },
    })

    const results = await checkOutdated({ fromFile: lockPath, cwd: tmp })
    expect(results).toHaveLength(2)

    const ghResult = results.find((r) => r.skill === 'gh-skill')
    const localResult = results.find((r) => r.skill === 'local-one')

    expect(ghResult).toBeDefined()
    expect(ghResult!.status).toBe('current')

    expect(localResult).toBeDefined()
    expect(localResult!.status).toBe('current')
  })
})
