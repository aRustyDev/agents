import { afterEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { cleanupTempDir, GitCloneError, gitRaw, lsRemote } from '../lib/git'
import { CliError } from '../lib/types'

// ---------------------------------------------------------------------------
// GitCloneError
// ---------------------------------------------------------------------------

describe('GitCloneError', () => {
  test('sets isTimeout flag', () => {
    const e = new GitCloneError('timed out', true, false)
    expect(e.isTimeout).toBe(true)
    expect(e.isAuthError).toBe(false)
  })

  test('sets isAuthError flag', () => {
    const e = new GitCloneError('auth failed', false, true)
    expect(e.isTimeout).toBe(false)
    expect(e.isAuthError).toBe(true)
  })

  test('display() includes hint', () => {
    const e = new GitCloneError('clone failed', false, false, 'try again')
    const output = e.display()
    expect(output).toContain('E_GIT_CLONE')
    expect(output).toContain('clone failed')
    expect(output).toContain('hint: try again')
  })

  test('extends CliError', () => {
    const e = new GitCloneError('test')
    expect(e).toBeInstanceOf(CliError)
    expect(e.code).toBe('E_GIT_CLONE')
  })

  test('preserves cause', () => {
    const cause = new Error('original')
    const e = new GitCloneError('wrapped', false, false, 'hint', cause)
    expect(e.cause).toBe(cause)
  })
})

// ---------------------------------------------------------------------------
// cleanupTempDir
// ---------------------------------------------------------------------------

describe('cleanupTempDir', () => {
  let tempDir: string

  afterEach(async () => {
    // Best-effort cleanup if test didn't remove it
    if (tempDir && existsSync(tempDir)) {
      const { rm } = await import('node:fs/promises')
      await rm(tempDir, { recursive: true, force: true })
    }
  })

  test('removes directory under tmpdir', async () => {
    tempDir = await mkdtemp(join(tmpdir(), 'git-test-'))
    // Create a file inside so it's non-empty
    await writeFile(join(tempDir, 'test.txt'), 'hello')
    expect(existsSync(tempDir)).toBe(true)

    await cleanupTempDir(tempDir)
    expect(existsSync(tempDir)).toBe(false)
  })

  test('does not throw if directory already removed', async () => {
    tempDir = await mkdtemp(join(tmpdir(), 'git-test-'))
    const { rm } = await import('node:fs/promises')
    await rm(tempDir, { recursive: true, force: true })

    // Should not throw -- rm with force: true is idempotent
    await cleanupTempDir(tempDir)
  })

  test('rejects directory outside tmpdir', async () => {
    await expect(cleanupTempDir('/usr/local/dangerous')).rejects.toThrow(
      'Refusing to delete directory outside tmpdir'
    )
  })

  test('rejected error has E_UNSAFE_CLEANUP code', async () => {
    try {
      await cleanupTempDir('/usr/local/dangerous')
      expect.unreachable('should have thrown')
    } catch (e) {
      expect(e).toBeInstanceOf(CliError)
      expect((e as CliError).code).toBe('E_UNSAFE_CLEANUP')
    }
  })
})

// ---------------------------------------------------------------------------
// lsRemote (network tests)
// ---------------------------------------------------------------------------

describe('lsRemote', () => {
  test('resolves HEAD for a public repo', async () => {
    const result = await lsRemote('https://github.com/vercel-labs/skills.git')
    expect(result.ok).toBe(true)
    if (result.ok) {
      // SHA is a 40-char hex string
      expect(result.value).toMatch(/^[0-9a-f]{40}$/)
    }
  })

  test('errors on nonexistent repo', async () => {
    const result = await lsRemote('https://github.com/nonexistent-owner-xyz/no-such-repo.git')
    expect(result.ok).toBe(false)
    if (!result.ok) {
      // May be E_GIT_LS_REMOTE (process error) or E_NO_REFS (empty output)
      // depending on how git handles the missing remote
      expect(['E_GIT_LS_REMOTE', 'E_NO_REFS']).toContain(result.error.code)
    }
  }, 30_000)

  test('errors on nonexistent tag', async () => {
    const result = await lsRemote(
      'https://github.com/vercel-labs/skills.git',
      'v999.999.999-does-not-exist'
    )
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_REFS')
    }
  })
})

// ---------------------------------------------------------------------------
// gitRaw
// ---------------------------------------------------------------------------

describe('gitRaw', () => {
  test('executes --version', async () => {
    const result = await gitRaw(['--version'])
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toContain('git version')
    }
  })

  test('errors on invalid commands', async () => {
    const result = await gitRaw(['not-a-real-subcommand'])
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_GIT_RAW')
    }
  })
})
