/**
 * Tests for @agents/sdk/providers/local/skill/update (updateSkills)
 *
 * Uses bun's mock.module() to replace checkOutdated and addSkill so that
 * updateSkills is exercised in isolation without network or filesystem
 * dependencies.
 */

import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import type { AddResult } from '@agents/sdk/providers/local/skill/add'
import type { OutdatedResult } from '@agents/sdk/providers/local/skill/outdated'

// ---------------------------------------------------------------------------
// Temp directory lifecycle
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-update-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a minimal OutdatedResult. */
function outdated(
  skill: string,
  source: string,
  status: OutdatedResult['status'] = 'outdated',
  extra: Partial<OutdatedResult> = {}
): OutdatedResult {
  return {
    skill,
    source,
    sourceType: 'github',
    status,
    currentHash: 'a'.repeat(64),
    ...extra,
  }
}

/** Build a successful AddResult. */
function addOk(name: string, source: string): AddResult {
  return {
    ok: true,
    installed: [{ name, source, canonicalPath: `/tmp/${name}`, agentLinks: [] }],
    warnings: [],
  }
}

/** Build a failed AddResult. */
function addFailed(message: string): AddResult {
  const { CliError } = require('@agents/core/types') as typeof import('@agents/core/types')
  return {
    ok: false,
    installed: [],
    error: new CliError(message, 'E_ADD_FAILED'),
    warnings: [],
  }
}

// ---------------------------------------------------------------------------
// UpdateError class
// ---------------------------------------------------------------------------

describe('UpdateError', () => {
  test('has skill, message, and code fields', async () => {
    const { UpdateError } = await import('@agents/sdk/providers/local/skill/update')
    const err = new UpdateError('beads', 'failed to update', 'E_UPDATE_FAILED')
    expect(err.skill).toBe('beads')
    expect(err.code).toBe('E_UPDATE_FAILED')
    expect(err.message).toBe('failed to update')
  })

  test('supports optional hint and cause', async () => {
    const { UpdateError } = await import('@agents/sdk/providers/local/skill/update')
    const cause = new Error('root cause')
    const err = new UpdateError('foo', 'msg', 'E_X', 'try Y', cause)
    expect(err.hint).toBe('try Y')
    expect(err.cause).toBe(cause)
  })

  test('extends CliError with display()', async () => {
    const { UpdateError } = await import('@agents/sdk/providers/local/skill/update')
    const err = new UpdateError('bar', 'boom', 'E_BOOM', 'check logs')
    expect(err.display()).toContain('E_BOOM')
    expect(err.display()).toContain('boom')
    expect(err.display()).toContain('check logs')
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- nothing outdated
// ---------------------------------------------------------------------------

describe('updateSkills -- nothing outdated', () => {
  test('returns "current" for all skills when none are outdated', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('alpha', 'org/alpha', 'current'),
        outdated('beta', 'org/beta', 'current'),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('unused', 'unused'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(2)
    expect(results.every((r) => r.status === 'current')).toBe(true)
  })

  test('returns empty array when lockfile has no skills', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('unused', 'unused'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- happy path
// ---------------------------------------------------------------------------

describe('updateSkills -- outdated skills', () => {
  test('updates a single outdated skill', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('stale-skill', 'org/repo', 'outdated')],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('stale-skill', 'org/repo'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(1)
    expect(results[0]!.skill).toBe('stale-skill')
    expect(results[0]!.status).toBe('updated')
  })

  test('updates outdated and passes through current', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('fresh', 'org/fresh', 'current'),
        outdated('stale', 'org/stale', 'outdated'),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('stale', 'org/stale'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(2)

    const staleResult = results.find((r) => r.skill === 'stale')
    const freshResult = results.find((r) => r.skill === 'fresh')

    expect(staleResult).toBeDefined()
    expect(staleResult!.status).toBe('updated')

    expect(freshResult).toBeDefined()
    expect(freshResult!.status).toBe('current')
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- skill name filtering
// ---------------------------------------------------------------------------

describe('updateSkills -- skill filtering', () => {
  test('only updates specified skills', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('alpha', 'org/alpha', 'outdated'),
        outdated('beta', 'org/beta', 'outdated'),
        outdated('gamma', 'org/gamma', 'outdated'),
      ],
    }))

    const addCalls: string[] = []
    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, source: string) => {
        addCalls.push(source)
        return addOk('any', source)
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, {
      cwd: tmp,
      skills: ['alpha', 'gamma'],
    })

    // alpha and gamma should be updated, beta should be skipped
    const alphaResult = results.find((r) => r.skill === 'alpha')
    const betaResult = results.find((r) => r.skill === 'beta')
    const gammaResult = results.find((r) => r.skill === 'gamma')

    expect(alphaResult!.status).toBe('updated')
    expect(gammaResult!.status).toBe('updated')
    expect(betaResult!.status).toBe('skipped')

    // addSkill should only have been called for alpha and gamma
    expect(addCalls).toHaveLength(2)
    expect(addCalls).toContain('org/alpha')
    expect(addCalls).toContain('org/gamma')
  })

  test('filter is case-insensitive', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('MySkill', 'org/repo', 'outdated')],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('MySkill', 'org/repo'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, {
      cwd: tmp,
      skills: ['myskill'],
    })

    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('updated')
  })

  test('filter for non-existent skill skips everything', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('alpha', 'org/alpha', 'outdated')],
    }))

    const addCalls: string[] = []
    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, source: string) => {
        addCalls.push(source)
        return addOk('alpha', source)
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, {
      cwd: tmp,
      skills: ['nonexistent'],
    })

    // alpha is outdated but not in the filter, so it becomes skipped
    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('skipped')

    // addSkill should NOT have been called
    expect(addCalls).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- partial failures
// ---------------------------------------------------------------------------

describe('updateSkills -- partial failures', () => {
  test('continues after one skill fails via AddResult.ok=false', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('bad', 'org/bad', 'outdated'),
        outdated('good', 'org/good', 'outdated'),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, source: string) => {
        if (source === 'org/bad') return addFailed('clone failed')
        return addOk('good', source)
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(2)

    const badResult = results.find((r) => r.skill === 'bad')
    const goodResult = results.find((r) => r.skill === 'good')

    expect(badResult!.status).toBe('failed')
    expect(badResult!.error).toBe('clone failed')

    expect(goodResult!.status).toBe('updated')
  })

  test('continues after one skill throws an exception', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('throws', 'org/throws', 'outdated'),
        outdated('works', 'org/works', 'outdated'),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, source: string) => {
        if (source === 'org/throws') throw new Error('unexpected crash')
        return addOk('works', source)
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(2)

    const throwsResult = results.find((r) => r.skill === 'throws')
    const worksResult = results.find((r) => r.skill === 'works')

    expect(throwsResult!.status).toBe('failed')
    expect(throwsResult!.error).toBe('unexpected crash')

    expect(worksResult!.status).toBe('updated')
  })

  test('handles non-Error throws gracefully', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('throws-string', 'org/x', 'outdated')],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => {
        throw 'raw string error'
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('failed')
    expect(results[0]!.error).toBe('raw string error')
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- unavailable / unknown passthrough
// ---------------------------------------------------------------------------

describe('updateSkills -- passthrough statuses', () => {
  test('unavailable skills are skipped', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('gone', 'org/gone', 'unavailable')],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('unused', 'unused'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('skipped')
  })

  test('unknown source type skills are skipped', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('weird', 'ftp://host/path', 'unknown', { sourceType: 'ftp' }),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('unused', 'unused'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(1)
    expect(results[0]!.status).toBe('skipped')
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- option passthrough
// ---------------------------------------------------------------------------

describe('updateSkills -- option passthrough', () => {
  test('passes cwd and copy to addSkill', async () => {
    let capturedOpts: Record<string, unknown> = {}

    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [outdated('skill-a', 'org/a', 'outdated')],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, _source: string, opts: Record<string, unknown>) => {
        capturedOpts = opts
        return addOk('skill-a', 'org/a')
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    await updateSkills(undefined, { cwd: '/custom/path', copy: true })

    expect(capturedOpts.cwd).toBe('/custom/path')
    expect(capturedOpts.copy).toBe(true)
    expect(capturedOpts.yes).toBe(true) // Always forced
    expect(capturedOpts.quiet).toBe(true) // Always forced during batch
  })

  test('passes stdin/fromFile/fromUrl to checkOutdated', async () => {
    let capturedOpts: Record<string, unknown> = {}

    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async (opts: Record<string, unknown>) => {
        capturedOpts = opts
        return []
      },
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async () => addOk('unused', 'unused'),
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    await updateSkills(undefined, {
      fromFile: '/path/to/lockfile.json',
      fromUrl: 'https://example.com/lock.json',
      stdin: true,
      cwd: '/some/dir',
    })

    expect(capturedOpts.fromFile).toBe('/path/to/lockfile.json')
    expect(capturedOpts.fromUrl).toBe('https://example.com/lock.json')
    expect(capturedOpts.stdin).toBe(true)
    expect(capturedOpts.cwd).toBe('/some/dir')
  })
})

// ---------------------------------------------------------------------------
// updateSkills -- mixed scenario
// ---------------------------------------------------------------------------

describe('updateSkills -- mixed scenario', () => {
  test('handles a realistic mix of current, outdated, unavailable, and unknown', async () => {
    mock.module('@agents/sdk/providers/local/skill/outdated', () => ({
      checkOutdated: async () => [
        outdated('fresh-skill', 'org/fresh', 'current'),
        outdated('stale-1', 'org/stale1', 'outdated'),
        outdated('stale-2', 'org/stale2', 'outdated'),
        outdated('gone-skill', 'org/gone', 'unavailable'),
        outdated('alien', 'ftp://host', 'unknown', { sourceType: 'ftp' }),
      ],
    }))

    mock.module('@agents/sdk/providers/local/skill/add', () => ({
      addSkill: async (_resolver: unknown, source: string) => {
        if (source === 'org/stale2') return addFailed('disk full')
        return addOk('any', source)
      },
    }))

    const { updateSkills } = await import('@agents/sdk/providers/local/skill/update')
    const results = await updateSkills(undefined, { cwd: tmp })

    expect(results).toHaveLength(5)

    const bySkill = Object.fromEntries(results.map((r) => [r.skill, r]))

    expect(bySkill['fresh-skill']!.status).toBe('current')
    expect(bySkill['stale-1']!.status).toBe('updated')
    expect(bySkill['stale-2']!.status).toBe('failed')
    expect(bySkill['stale-2']!.error).toBe('disk full')
    expect(bySkill['gone-skill']!.status).toBe('skipped')
    expect(bySkill['alien']!.status).toBe('skipped')
  })
})
