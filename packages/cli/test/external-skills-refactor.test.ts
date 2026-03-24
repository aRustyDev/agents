/**
 * Regression tests for the external-skills.ts refactor to lib/git.ts.
 *
 * Verifies that:
 * 1. gitLsRemote delegates to lsRemote from git.ts
 * 2. Error codes are preserved (E_GIT_LS_REMOTE, E_NO_REFS)
 * 3. syncSkill uses cloneRepo (verified via cleanup being called)
 */

import { beforeEach, describe, expect, mock, test } from 'bun:test'
import { CliError, err, ok } from '../src/lib/types'

// ---------------------------------------------------------------------------
// Mock setup: replace git.ts functions before importing external-skills
// ---------------------------------------------------------------------------

const mockLsRemote = mock(() => Promise.resolve(ok('abc123def456')))
const mockCloneCleanup = mock(() => Promise.resolve())
const mockCloneRepo = mock(() =>
  Promise.resolve(
    ok({
      tempDir: '/tmp/mock-clone',
      cleanup: mockCloneCleanup,
    })
  )
)
const mockGitRaw = mock(() => Promise.resolve(ok('')))

mock.module('../src/lib/git', () => ({
  lsRemote: mockLsRemote,
  cloneRepo: mockCloneRepo,
  gitRaw: mockGitRaw,
  cleanupTempDir: mock(() => Promise.resolve()),
  createGit: mock(() => ({})),
  fetchSkillFolderHash: mock(() => Promise.resolve(null)),
}))

// Also mock spawnSync so npx/which calls don't run real processes
mock.module('../src/lib/runtime', () => ({
  spawnSync: mock(() => ({ stdout: '', stderr: '', exitCode: 1, success: false })),
  isBun: true,
  readText: mock(),
  readJson: mock(),
  writeText: mock(),
  fileExists: mock(),
  fileStream: mock(),
  createSha256Hasher: mock(),
  spawnAsync: mock(),
  currentDir: mock(),
}))

// Import AFTER mocks are set up
const { gitLsRemote, syncSkill } = await import('../src/lib/external-skills')

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('gitLsRemote delegates to lsRemote', () => {
  beforeEach(() => {
    mockLsRemote.mockClear()
  })

  test('calls lsRemote with the same arguments', async () => {
    mockLsRemote.mockResolvedValueOnce(ok('deadbeef12345678'))

    const result = await gitLsRemote('https://github.com/org/repo.git', 'v1.0.0')

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('deadbeef12345678')
    }
    expect(mockLsRemote).toHaveBeenCalledTimes(1)
    expect(mockLsRemote).toHaveBeenCalledWith('https://github.com/org/repo.git', 'v1.0.0')
  })

  test('calls lsRemote without ref when none provided', async () => {
    mockLsRemote.mockResolvedValueOnce(ok('face0000'))

    const result = await gitLsRemote('https://github.com/org/repo.git')

    expect(result.ok).toBe(true)
    expect(mockLsRemote).toHaveBeenCalledWith('https://github.com/org/repo.git', undefined)
  })
})

describe('error codes are preserved', () => {
  beforeEach(() => {
    mockLsRemote.mockClear()
  })

  test('E_GIT_LS_REMOTE is returned on git failure', async () => {
    mockLsRemote.mockResolvedValueOnce(
      err(
        new CliError(
          'git ls-remote failed for https://github.com/org/repo.git',
          'E_GIT_LS_REMOTE',
          'some error'
        )
      )
    )

    const result = await gitLsRemote('https://github.com/org/repo.git')

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_GIT_LS_REMOTE')
    }
  })

  test('E_NO_REFS is returned when no refs found', async () => {
    mockLsRemote.mockResolvedValueOnce(
      err(new CliError('No refs found', 'E_NO_REFS', 'Repository may be empty'))
    )

    const result = await gitLsRemote('https://github.com/org/repo.git', 'v999.0.0')

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_REFS')
    }
  })
})

describe('syncSkill uses cloneRepo', () => {
  beforeEach(() => {
    mockCloneRepo.mockClear()
    mockCloneCleanup.mockClear()
  })

  test('calls cleanup on cloneRepo result (pinned ref)', async () => {
    // cloneRepo returns a tempDir that does not actually contain the skill,
    // so syncSkill will return E_SKILL_NOT_FOUND -- but cleanup should still be called
    mockCloneRepo.mockResolvedValueOnce(
      ok({
        tempDir: '/tmp/mock-clone-pinned',
        cleanup: mockCloneCleanup,
      })
    )

    const entry = {
      name: 'test-skill',
      source: 'org/repo',
      skill: 'their-skill',
      ref: 'v1.0.0',
      passthrough: false,
    }

    const result = await syncSkill(entry, '/tmp/fake-external', '/tmp/fake-skills')

    // The skill won't be found in the mock tempDir, so we expect E_SKILL_NOT_FOUND
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
    }

    // Crucially, cleanup must be called even on failure
    expect(mockCloneCleanup).toHaveBeenCalledTimes(1)
    expect(mockCloneRepo).toHaveBeenCalledWith('https://github.com/org/repo.git', 'v1.0.0')
  })

  test('maps clone failure to E_CLONE_FAILED', async () => {
    mockCloneRepo.mockResolvedValueOnce(
      err(new CliError('Clone failed', 'E_GIT_CLONE', 'Network error'))
    )

    const entry = {
      name: 'test-skill',
      source: 'org/repo',
      skill: 'their-skill',
      ref: 'v1.0.0',
      passthrough: false,
    }

    const result = await syncSkill(entry, '/tmp/fake-external', '/tmp/fake-skills')

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_CLONE_FAILED')
    }
  })
})
