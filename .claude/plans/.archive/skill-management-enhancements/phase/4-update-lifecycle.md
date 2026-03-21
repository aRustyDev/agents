# Phase 4: Update Lifecycle (outdated, update)

**ID:** `phase-4`
**Dependencies:** phase-1 (task 4.1 outdated); phase-2 (task 4.2 update needs `addSkill`)
**Status:** pending
**Effort:** TBD

## Objective

Implement `outdated` (detect available updates) and `update` (apply updates) commands with support for arbitrary data input methods (stdin, file, URL). Task 4.1 (`checkOutdated`) depends only on phase-1 modules (`git.ts`, `hash.ts`, `lockfile.ts`) and can start immediately after phase 1. Task 4.2 (`updateSkills`) requires `addSkill` from phase 2.

## Success Criteria

- [ ] `just agents skill outdated` reports which installed skills have upstream changes
- [ ] `just agents skill outdated --json` outputs machine-readable update status
- [ ] `just agents skill update` re-installs outdated skills
- [ ] `just agents skill update skill-name` updates a specific skill
- [ ] `echo '{"skills":...}' | just agents skill outdated --stdin` accepts piped data
- [ ] `just agents skill outdated --from-file status.json` reads from file
- [ ] `just agents skill outdated --from-url https://...` fetches JSON from URL (simple GET, no auth)
- [ ] Outdated uses GitHub Trees API (tree SHA comparison) for GitHub sources
- [ ] Outdated uses `git ls-remote` for git sources
- [ ] Outdated uses content hash comparison for local sources

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Outdated command logic | `.scripts/lib/skill-outdated.ts` | TypeScript |
| Update command logic | `.scripts/lib/skill-update.ts` | TypeScript |
| CLI subcommand wiring | `.scripts/commands/skill.ts` | TypeScript (additions) |
| Tests | `.scripts/test/skill-outdated.test.ts` | bun:test |
| Tests | `.scripts/test/skill-update.test.ts` | bun:test |

## Files

**Create:**
- `.scripts/lib/skill-outdated.ts`
- `.scripts/lib/skill-update.ts`
- `.scripts/test/skill-outdated.test.ts`
- `.scripts/test/skill-update.test.ts`

**Modify:**
- `.scripts/commands/skill.ts` (add `outdated`, `update` subcommands)

## Error Types

```typescript
// In lib/skill-outdated.ts

import { CliError } from './types'

/**
 * Thrown when a per-skill outdated check fails (network, parse, API).
 * Contains the skill name so callers can report partial results.
 */
export class OutdatedError extends CliError {
  constructor(
    readonly skill: string,
    message: string,
    code: string,
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}

// In lib/skill-update.ts

/**
 * Thrown when a per-skill update fails (re-install, lock write, etc.).
 * Contains the skill name and the original addSkill error.
 */
export class UpdateError extends CliError {
  constructor(
    readonly skill: string,
    message: string,
    code: string,
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}
```

## Edge Cases

| # | Edge Case | Affected Task | Expected Behavior |
|---|-----------|---------------|-------------------|
| 1 | Skill in lock but source repo deleted (404) | 4.1 | Report `status: 'unavailable'`, do not throw. Log warning with repo URL. |
| 2 | Skill in lock with no `skillFolderHash` (local-only install, can't check) | 4.1 | Report `status: 'unknown'`. Hint: "re-install from remote source to enable tracking". |
| 3 | GitHub API rate limit (403) | 4.1 | Throw `OutdatedError` with `code: 'E_RATE_LIMIT'`. Include `X-RateLimit-Reset` header value in hint. |
| 4 | `--stdin` with invalid JSON | 4.1, 4.2 | Return `err(CliError)` with `code: 'E_INVALID_JSON'`, hint: "stdin must be valid JSON". |
| 5 | `--stdin` with valid JSON but wrong schema | 4.1, 4.2 | Return `err(CliError)` with `code: 'E_VALIDATION_FAILED'`, list valibot issues in hint. |
| 6 | `--from-file` path doesn't exist | 4.1, 4.2 | Return `err(CliError)` with `code: 'E_FILE_NOT_FOUND'`, include resolved absolute path in hint. |
| 7 | `--from-url` timeout (>5s) | 4.1, 4.2 | Return `err(CliError)` with `code: 'E_FETCH_TIMEOUT'`, hint: "URL did not respond within 5 seconds". |
| 8 | `--from-url` returns HTML (not JSON) | 4.1, 4.2 | Return `err(CliError)` with `code: 'E_INVALID_JSON'`, hint: "URL returned non-JSON content (check content-type)". |
| 9 | All skills are current (nothing to update) | 4.1, 4.2 | Report success with 0 outdated/updated. Human output: "All skills are up to date." |
| 10 | Update fails for one skill in batch (partial failure) | 4.2 | Continue updating remaining skills. Report `status: 'failed'` for the failed skill, `status: 'updated'` for successes. Exit code 1 (partial). |
| 11 | Lock file is empty/missing | 4.1, 4.2 | `checkOutdated`: return empty array with info message. `updateSkills`: return empty array, no error. |
| 12 | Concurrent update (two processes writing lock) | 4.2 | Read lock immediately before write, merge changes, write atomically. Accept last-write-wins for MVP; document as known limitation. |

## Tasks

### 4.1 Outdated Command (`lib/skill-outdated.ts`)

**Task Dependencies:** Phase 1 only (`lib/git.ts` for `fetchSkillFolderHash` and `lsRemote`, `lib/hash.ts` for `hashDirectory`, existing `lib/lockfile.ts` for `readLockfile`). Does NOT depend on phase 2 — `checkOutdated` reads lock state but does not install anything.

**Library Decisions:** No new dependencies. Uses `lib/git.ts` (fetchSkillFolderHash, lsRemote), `lib/hash.ts` (hashDirectory), `lib/github.ts` (getClient for Trees API auth), `lib/lockfile.ts` (readLockfile), `lib/runtime.ts` (readText, readJson), `lib/output.ts` (createOutput), `lib/types.ts` (Result, CliError).

- [ ] Export `checkOutdated(opts: OutdatedOptions): Promise<OutdatedResult[]>`
- [ ] Data input methods:
  - Default: read from global lock file + local lock file
  - `--stdin`: parse JSON from stdin (`process.stdin`)
  - `--from-file <path>`: read JSON from file
  - `--from-url <url>`: `fetch(url)` -> parse JSON (simple GET, no auth headers, 5s timeout)
- [ ] Per-source-type check strategy:
  - `github`: `fetchSkillFolderHash(ownerRepo, skillPath)` via `lib/git.ts`, compare to stored `skillFolderHash`
  - `git`: `lsRemote(url, ref)` from `lib/git.ts`, compare to stored `upstream_commit`
  - `local`: `hashDirectory(path)` from `lib/hash.ts`, compare to stored `computedHash`
  - `well-known`: re-fetch and compare content hash
- [ ] Group checks by source (batch GitHub API calls per repo -- one Trees API call covers all skills in that repo)
- [ ] `OutdatedResult`: `{ skill, source, status: 'current'|'outdated'|'unavailable'|'unknown', currentHash?, remoteHash? }`
- [ ] Output: human-readable summary or `--json` array

**`--from-url` clarification:** This is a simple convenience for fetching pre-computed status JSON from any URL. It's a plain `fetch(url)` with a 5-second timeout -- no auth, no webhooks, no polling. Use case: CI pipeline publishes a status JSON artifact, developer checks it locally.

#### Code Examples

```typescript
// lib/skill-outdated.ts

import { readLockfile, type StalenessEntry } from './lockfile'
import { fetchSkillFolderHash, lsRemote } from './git'
import { hashDirectory } from './hash'
import { getClient } from './github'
import { readText, readJson } from './runtime'
import { createOutput, type OutputFormatter } from './output'
import { CliError, ok, err, type Result } from './types'
import type { LockfileV1, SkillLockEntry } from './schemas'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface OutdatedOptions {
  /** Read pre-computed status from stdin instead of checking live. */
  stdin?: boolean
  /** Read pre-computed status from a local JSON file. */
  fromFile?: string
  /** Fetch pre-computed status JSON from a URL (GET, 5s timeout). */
  fromUrl?: string
  /** Emit JSON instead of human-readable output. */
  json?: boolean
  /** Suppress non-essential output. */
  quiet?: boolean
}

export type OutdatedStatus = 'current' | 'outdated' | 'unavailable' | 'unknown'

export interface OutdatedResult {
  skill: string
  source: string
  sourceType: string
  status: OutdatedStatus
  currentHash?: string
  remoteHash?: string
  error?: string
}

// ---------------------------------------------------------------------------
// Input resolution
// ---------------------------------------------------------------------------

/**
 * Resolve the lock data from the configured input method.
 *
 * Priority: --stdin > --from-file > --from-url > default lock files.
 */
async function resolveInput(opts: OutdatedOptions): Promise<Result<LockfileV1>> {
  if (opts.stdin) {
    return parseStdinAsLockfile()
  }
  if (opts.fromFile) {
    return readLockfile<LockfileV1>('skills', opts.fromFile)
  }
  if (opts.fromUrl) {
    return fetchUrlAsLockfile(opts.fromUrl)
  }
  // Default: read from the project lock file
  return readLockfile<LockfileV1>('skills', 'skills-lock.json')
}

async function parseStdinAsLockfile(): Promise<Result<LockfileV1>> {
  const chunks: Buffer[] = []
  for await (const chunk of process.stdin) {
    chunks.push(chunk)
  }
  const raw = Buffer.concat(chunks).toString('utf-8')
  try {
    return ok(JSON.parse(raw) as LockfileV1)
  } catch (e) {
    return err(new CliError('Invalid JSON on stdin', 'E_INVALID_JSON', 'stdin must be valid JSON', e))
  }
}

async function fetchUrlAsLockfile(url: string): Promise<Result<LockfileV1>> {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(5_000) })
    const text = await response.text()
    return ok(JSON.parse(text) as LockfileV1)
  } catch (e) {
    if (e instanceof DOMException && e.name === 'TimeoutError') {
      return err(new CliError(
        `Fetch timed out: ${url}`,
        'E_FETCH_TIMEOUT',
        'URL did not respond within 5 seconds',
      ))
    }
    return err(new CliError(`Failed to fetch: ${url}`, 'E_FETCH_FAILED', undefined, e))
  }
}

// ---------------------------------------------------------------------------
// Per-source check strategies
// ---------------------------------------------------------------------------

async function checkGithubSkill(
  entry: SkillLockEntry,
  name: string,
): Promise<OutdatedResult> {
  // fetchSkillFolderHash returns the tree SHA for the skill's folder
  // from the GitHub Trees API. One API call per repo covers all skills.
  const remoteHash = await fetchSkillFolderHash(entry.source, name)
  if (remoteHash === null) {
    return {
      skill: name,
      source: entry.source,
      sourceType: 'github',
      status: 'unavailable',
      currentHash: entry.computedHash,
    }
  }
  return {
    skill: name,
    source: entry.source,
    sourceType: 'github',
    status: remoteHash === entry.computedHash ? 'current' : 'outdated',
    currentHash: entry.computedHash,
    remoteHash,
  }
}

async function checkLocalSkill(
  entry: SkillLockEntry,
  name: string,
  skillPath: string,
): Promise<OutdatedResult> {
  const currentHash = await hashDirectory(skillPath)
  return {
    skill: name,
    source: entry.source,
    sourceType: 'local',
    status: currentHash === entry.computedHash ? 'current' : 'outdated',
    currentHash: entry.computedHash,
    remoteHash: currentHash,
  }
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export async function checkOutdated(opts: OutdatedOptions): Promise<OutdatedResult[]> {
  const inputResult = await resolveInput(opts)
  if (!inputResult.ok) {
    throw new OutdatedError('*', inputResult.error.message, inputResult.error.code)
  }

  const lock = inputResult.value
  const results: OutdatedResult[] = []

  // Group github skills by owner/repo for batched Trees API calls
  const githubByRepo = new Map<string, { name: string; entry: SkillLockEntry }[]>()

  for (const [name, entry] of Object.entries(lock.skills)) {
    if (entry.sourceType === 'github') {
      const repo = entry.source
      if (!githubByRepo.has(repo)) githubByRepo.set(repo, [])
      githubByRepo.get(repo)!.push({ name, entry })
    } else if (entry.sourceType === 'local') {
      results.push(await checkLocalSkill(entry, name, `context/skills/${name}`))
    }
    // ... git, well-known handled similarly
  }

  // Batch GitHub checks: one Trees API call per repo
  for (const [_repo, skills] of githubByRepo) {
    for (const { name, entry } of skills) {
      try {
        results.push(await checkGithubSkill(entry, name))
      } catch (e) {
        results.push({
          skill: name,
          source: entry.source,
          sourceType: 'github',
          status: 'unavailable',
          error: e instanceof Error ? e.message : String(e),
        })
      }
    }
  }

  return results
}
```

#### Example Test Cases

```typescript
// .scripts/test/skill-outdated.test.ts

import { describe, expect, mock, test, beforeEach } from 'bun:test'
import { checkOutdated, type OutdatedOptions, type OutdatedResult } from '../lib/skill-outdated'

// ---------------------------------------------------------------------------
// GitHub source (mock Trees API)
// ---------------------------------------------------------------------------

describe('checkOutdated — github source', () => {
  test('reports "current" when tree SHA matches lock hash', async () => {
    // Mock fetchSkillFolderHash to return the same hash as in the lock
    mock.module('../lib/git', () => ({
      fetchSkillFolderHash: async () => '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            beads: {
              source: 'steveyegge/beads',
              sourceType: 'github',
              computedHash: '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('current')
    expect(results[0].skill).toBe('beads')
  })

  test('reports "outdated" when tree SHA differs from lock hash', async () => {
    mock.module('../lib/git', () => ({
      fetchSkillFolderHash: async () => 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            beads: {
              source: 'steveyegge/beads',
              sourceType: 'github',
              computedHash: '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results[0].status).toBe('outdated')
    expect(results[0].remoteHash).toBe('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
  })

  test('reports "unavailable" when Trees API returns null (404)', async () => {
    mock.module('../lib/git', () => ({
      fetchSkillFolderHash: async () => null,
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            deleted: {
              source: 'org/gone-repo',
              sourceType: 'github',
              computedHash: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results[0].status).toBe('unavailable')
  })
})

// ---------------------------------------------------------------------------
// Local source (hash comparison)
// ---------------------------------------------------------------------------

describe('checkOutdated — local source', () => {
  test('reports "current" when directory hash matches', async () => {
    const fixedHash = 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
    mock.module('../lib/hash', () => ({
      hashDirectory: async () => fixedHash,
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            'my-local': {
              source: './local/path',
              sourceType: 'local',
              computedHash: fixedHash,
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('current')
  })

  test('reports "outdated" when directory hash differs', async () => {
    mock.module('../lib/hash', () => ({
      hashDirectory: async () => 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            'my-local': {
              source: './local/path',
              sourceType: 'local',
              computedHash: 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results[0].status).toBe('outdated')
  })

  test('reports "unavailable" when directory does not exist', async () => {
    mock.module('../lib/hash', () => ({
      hashDirectory: async () => { throw new Error('ENOENT') },
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            missing: {
              source: './gone/path',
              sourceType: 'local',
              computedHash: 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results[0].status).toBe('unavailable')
  })
})

// ---------------------------------------------------------------------------
// Stdin input parsing
// ---------------------------------------------------------------------------

describe('checkOutdated — stdin input', () => {
  test('parses valid JSON from stdin', async () => {
    // Mock process.stdin as an async iterable
    const lockData = JSON.stringify({
      version: 1,
      skills: {
        beads: {
          source: 'steveyegge/beads',
          sourceType: 'github',
          computedHash: '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
        },
      },
    })
    // ... mock stdin with Buffer.from(lockData)
    mock.module('../lib/git', () => ({
      fetchSkillFolderHash: async () => '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
    }))

    const results = await checkOutdated({ stdin: true })
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('current')
  })

  test('throws on invalid JSON from stdin', async () => {
    // Mock process.stdin to yield "not json"
    await expect(checkOutdated({ stdin: true })).rejects.toThrow()
  })

  test('throws on valid JSON with wrong schema from stdin', async () => {
    // Mock process.stdin to yield '{"wrong": "shape"}'
    await expect(checkOutdated({ stdin: true })).rejects.toThrow()
  })
})

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe('checkOutdated — edge cases', () => {
  test('returns empty array when lock file is empty', async () => {
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: { version: 1, skills: {} },
      }),
    }))

    const results = await checkOutdated({})
    expect(results).toEqual([])
  })

  test('reports "unknown" for skill with no computedHash', async () => {
    // Simulates a local-only install that was never hashed
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            untracked: {
              source: './local',
              sourceType: 'local',
              computedHash: '',
            },
          },
        },
      }),
    }))

    const results = await checkOutdated({})
    expect(results[0].status).toBe('unknown')
  })

  test('--from-url returns error on timeout', async () => {
    // Mock fetch to simulate timeout
    globalThis.fetch = async () => {
      throw new DOMException('The operation was aborted.', 'TimeoutError')
    }

    await expect(
      checkOutdated({ fromUrl: 'https://slow.example.com/status.json' })
    ).rejects.toThrow()
  })
})
```

#### Acceptance Criteria

- [ ] `checkOutdated({})` reads lock file and returns `OutdatedResult[]` for every entry
- [ ] GitHub source skills use `fetchSkillFolderHash` (Trees API), not full clone
- [ ] Git source skills use `lsRemote` to compare upstream commit SHA
- [ ] Local source skills use `hashDirectory` to compare content hash
- [ ] GitHub skills grouped by `owner/repo` -- one Trees API call per repo, not per skill
- [ ] `--stdin` reads JSON from process.stdin and validates with valibot
- [ ] `--from-file` reads JSON from disk path and validates with valibot
- [ ] `--from-url` fetches with 5s timeout via `AbortSignal.timeout(5000)`
- [ ] Invalid input (bad JSON, wrong schema) returns `err(CliError)`, does not throw
- [ ] `OutdatedResult.status` is `'unavailable'` (not throw) when source repo is 404
- [ ] `OutdatedResult.status` is `'unknown'` when skill has no stored hash
- [ ] Rate limit 403 produces `OutdatedError` with `E_RATE_LIMIT` code
- [ ] Human output shows a table: skill name, source, status, current hash (truncated), remote hash (truncated)
- [ ] JSON output (`--json`) emits the `OutdatedResult[]` array
- [ ] Empty lock file returns empty array with info message, not error

### 4.2 Update Command (`lib/skill-update.ts`)

**Task Dependencies:** Task 4.1 (`checkOutdated` to find what needs updating), Phase 2 (`lib/skill-add.ts` for `addSkill`)

**Library Decisions:** No new dependencies. Calls `checkOutdated` from `lib/skill-outdated.ts` and `addSkill` from `lib/skill-add.ts`. Uses `lib/lockfile.ts` (readLockfile, writeLockfile), `lib/output.ts` (createOutput), `lib/types.ts` (Result, CliError).

- [ ] Export `updateSkills(skills: string[], opts: UpdateOptions): Promise<UpdateResult[]>`
- [ ] If no skill names: update all outdated (run `checkOutdated` first)
- [ ] If skill names: update only specified skills
- [ ] Data input: same methods as outdated (`--stdin`, `--from-file`, `--from-url`)
- [ ] Update strategy: call `addSkill(source, { yes: true })` from `lib/skill-add.ts` for each outdated skill
- [ ] Preserve agent associations from the existing lock entry
- [ ] Report: `UpdateResult { skill, status: 'updated'|'failed'|'skipped', error? }`

#### Code Examples

```typescript
// lib/skill-update.ts

import { checkOutdated, type OutdatedOptions, type OutdatedResult } from './skill-outdated'
import { addSkill } from './skill-add'
import { readLockfile, writeLockfile } from './lockfile'
import { createOutput, type OutputFormatter } from './output'
import { CliError, ok, err, type Result } from './types'
import type { LockfileV1 } from './schemas'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface UpdateOptions {
  /** Same input methods as outdated. */
  stdin?: boolean
  fromFile?: string
  fromUrl?: string
  /** Skip confirmation prompts. */
  yes?: boolean
  /** Emit JSON instead of human-readable output. */
  json?: boolean
  /** Suppress non-essential output. */
  quiet?: boolean
}

export type UpdateStatus = 'updated' | 'failed' | 'skipped'

export interface UpdateResult {
  skill: string
  status: UpdateStatus
  error?: string
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

/**
 * Update installed skills that have upstream changes.
 *
 * If `skills` is empty, updates ALL outdated skills.
 * If `skills` is provided, updates only the named skills (if they are outdated).
 *
 * Each update calls `addSkill(source, { yes: true })` which performs
 * a full re-install, preserving agent associations from the lock entry.
 */
export async function updateSkills(
  skills: string[],
  opts: UpdateOptions,
): Promise<UpdateResult[]> {
  const out = createOutput({ json: opts.json ?? false, quiet: opts.quiet ?? false })

  // 1. Determine which skills are outdated
  const outdatedOpts: OutdatedOptions = {
    stdin: opts.stdin,
    fromFile: opts.fromFile,
    fromUrl: opts.fromUrl,
    json: false,   // internal call, we handle output
    quiet: true,
  }
  const allResults = await checkOutdated(outdatedOpts)
  const outdated = allResults.filter((r) => r.status === 'outdated')

  // 2. Filter to requested skills (or all outdated)
  const toUpdate = skills.length > 0
    ? outdated.filter((r) => skills.includes(r.skill))
    : outdated

  if (toUpdate.length === 0) {
    out.info('All skills are up to date.')
    return []
  }

  // 3. Read current lock to preserve agent associations
  const lockResult = await readLockfile<LockfileV1>('skills', 'skills-lock.json')
  const currentLock = lockResult.ok ? lockResult.value : null

  // 4. Update each skill via addSkill (re-install)
  const results: UpdateResult[] = []
  for (const entry of toUpdate) {
    const spin = out.spinner(`Updating ${entry.skill}...`)
    try {
      // Re-install from the declared source with --yes (non-interactive)
      await addSkill(entry.source, { yes: true })
      spin.success({ text: `Updated ${entry.skill}` })
      results.push({ skill: entry.skill, status: 'updated' })
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      spin.error({ text: `Failed to update ${entry.skill}: ${msg}` })
      results.push({
        skill: entry.skill,
        status: 'failed',
        error: msg,
      })
    }
  }

  return results
}
```

#### Example Test Cases

```typescript
// .scripts/test/skill-update.test.ts

import { describe, expect, mock, test, beforeEach } from 'bun:test'
import { updateSkills, type UpdateOptions, type UpdateResult } from '../lib/skill-update'

// ---------------------------------------------------------------------------
// Update all outdated
// ---------------------------------------------------------------------------

describe('updateSkills — update all', () => {
  test('updates all skills when none specified', async () => {
    // Mock checkOutdated to return 2 outdated skills
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'outdated' },
        { skill: 'pnpm', source: '0froq/skills', sourceType: 'github', status: 'outdated' },
      ],
    }))
    // Mock addSkill to succeed
    mock.module('../lib/skill-add', () => ({
      addSkill: async () => ({ ok: true }),
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: { version: 1, skills: {} },
      }),
    }))

    const results = await updateSkills([], { yes: true })
    expect(results).toHaveLength(2)
    expect(results.every((r) => r.status === 'updated')).toBe(true)
  })

  test('returns empty array when all skills are current', async () => {
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'current' },
      ],
    }))

    const results = await updateSkills([], { yes: true })
    expect(results).toEqual([])
  })

  test('skips "unavailable" and "unknown" statuses', async () => {
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'gone', source: 'org/deleted', sourceType: 'github', status: 'unavailable' },
        { skill: 'local', source: './local', sourceType: 'local', status: 'unknown' },
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'outdated' },
      ],
    }))
    mock.module('../lib/skill-add', () => ({
      addSkill: async () => ({ ok: true }),
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: { version: 1, skills: {} },
      }),
    }))

    const results = await updateSkills([], { yes: true })
    expect(results).toHaveLength(1)
    expect(results[0].skill).toBe('beads')
    expect(results[0].status).toBe('updated')
  })
})

// ---------------------------------------------------------------------------
// Update single skill by name
// ---------------------------------------------------------------------------

describe('updateSkills — single skill', () => {
  test('updates only the named skill', async () => {
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'outdated' },
        { skill: 'pnpm', source: '0froq/skills', sourceType: 'github', status: 'outdated' },
      ],
    }))
    mock.module('../lib/skill-add', () => ({
      addSkill: async () => ({ ok: true }),
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: { version: 1, skills: {} },
      }),
    }))

    const results = await updateSkills(['beads'], { yes: true })
    expect(results).toHaveLength(1)
    expect(results[0].skill).toBe('beads')
    expect(results[0].status).toBe('updated')
  })

  test('returns empty when named skill is not outdated', async () => {
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'current' },
      ],
    }))

    const results = await updateSkills(['beads'], { yes: true })
    expect(results).toEqual([])
  })

  test('returns empty when named skill does not exist in lock', async () => {
    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [],
    }))

    const results = await updateSkills(['nonexistent'], { yes: true })
    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// Preserves agent associations
// ---------------------------------------------------------------------------

describe('updateSkills — agent associations', () => {
  test('passes existing lock entry to addSkill for agent preservation', async () => {
    let capturedOpts: Record<string, unknown> | undefined

    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'beads', source: 'steveyegge/beads', sourceType: 'github', status: 'outdated' },
      ],
    }))
    mock.module('../lib/skill-add', () => ({
      addSkill: async (_source: string, opts: Record<string, unknown>) => {
        capturedOpts = opts
        return { ok: true }
      },
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: {
          version: 1,
          skills: {
            beads: {
              source: 'steveyegge/beads',
              sourceType: 'github',
              computedHash: '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
            },
          },
        },
      }),
    }))

    await updateSkills([], { yes: true })
    expect(capturedOpts).toBeDefined()
    expect(capturedOpts!.yes).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// Partial failure
// ---------------------------------------------------------------------------

describe('updateSkills — partial failure', () => {
  test('continues updating after one skill fails', async () => {
    let callCount = 0

    mock.module('../lib/skill-outdated', () => ({
      checkOutdated: async () => [
        { skill: 'fail-skill', source: 'org/fail', sourceType: 'github', status: 'outdated' },
        { skill: 'ok-skill', source: 'org/ok', sourceType: 'github', status: 'outdated' },
      ],
    }))
    mock.module('../lib/skill-add', () => ({
      addSkill: async (source: string) => {
        callCount++
        if (source === 'org/fail') throw new Error('clone failed')
        return { ok: true }
      },
    }))
    mock.module('../lib/lockfile', () => ({
      readLockfile: async () => ({
        ok: true,
        value: { version: 1, skills: {} },
      }),
    }))

    const results = await updateSkills([], { yes: true })
    expect(callCount).toBe(2) // Both attempted
    expect(results).toHaveLength(2)
    expect(results[0].status).toBe('failed')
    expect(results[0].error).toContain('clone failed')
    expect(results[1].status).toBe('updated')
  })
})
```

#### Acceptance Criteria

- [ ] `updateSkills([], opts)` runs `checkOutdated` then calls `addSkill` for each outdated skill
- [ ] `updateSkills(['beads'], opts)` updates only the named skill (if it is outdated)
- [ ] Named skills that are not outdated are silently skipped (not an error)
- [ ] Named skills that do not exist in the lock file are silently skipped
- [ ] `addSkill` called with `{ yes: true }` for non-interactive re-install
- [ ] Agent associations from the existing lock entry are preserved across re-install
- [ ] Partial failure: if one skill fails, remaining skills still update; exit code 1
- [ ] `UpdateResult.status` is `'failed'` with `error` message for failed skills
- [ ] Data input methods (`--stdin`, `--from-file`, `--from-url`) forwarded to `checkOutdated`
- [ ] Human output uses spinner per skill (`Updating beads...` -> `Updated beads` / `Failed to update beads`)
- [ ] JSON output (`--json`) emits the `UpdateResult[]` array
- [ ] Empty lock file or "all current" produces info message and empty results, not error

### 4.3 CLI Wiring

**Task Dependencies:** Tasks 4.1 and 4.2 (the library modules being wired)

**Library Decisions:** No new dependencies. Wires `checkOutdated` and `updateSkills` into Citty subcommands in the existing `commands/skill.ts` file.

- [ ] Add `skill outdated [--json] [--stdin] [--from-file] [--from-url]` subcommand
- [ ] Add `skill update [skills...] [--json] [--stdin] [--from-file] [--from-url] [--yes]` subcommand

#### Code Examples

```typescript
// Additions to .scripts/commands/skill.ts

import { defineCommand } from 'citty'
import { checkOutdated } from '../lib/skill-outdated'
import { updateSkills } from '../lib/skill-update'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// skill outdated
// ---------------------------------------------------------------------------

const outdatedCommand = defineCommand({
  meta: { name: 'outdated', description: 'Check which installed skills have upstream changes' },
  args: {
    ...globalArgs,
    stdin: {
      type: 'boolean',
      description: 'Read pre-computed status JSON from stdin',
      default: false,
    },
    'from-file': {
      type: 'string',
      description: 'Read pre-computed status JSON from a local file',
    },
    'from-url': {
      type: 'string',
      description: 'Fetch pre-computed status JSON from a URL (GET, 5s timeout)',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    try {
      const results = await checkOutdated({
        stdin: args.stdin,
        fromFile: args['from-file'],
        fromUrl: args['from-url'],
        json: args.json,
        quiet: args.quiet,
      })

      if (args.json) {
        out.raw(results)
      } else {
        const outdated = results.filter((r) => r.status === 'outdated')
        if (outdated.length === 0) {
          out.success('All skills are up to date.')
        } else {
          out.table(
            results.map((r) => ({
              skill: r.skill,
              source: r.source,
              status: r.status,
              current: r.currentHash?.slice(0, 8) ?? '-',
              remote: r.remoteHash?.slice(0, 8) ?? '-',
            })),
          )
        }
      }
      process.exit(EXIT.OK)
    } catch (e) {
      out.error(e instanceof Error ? e.message : String(e))
      process.exit(EXIT.ERROR)
    }
  },
})

// ---------------------------------------------------------------------------
// skill update
// ---------------------------------------------------------------------------

const updateCommand = defineCommand({
  meta: { name: 'update', description: 'Re-install outdated skills from upstream' },
  args: {
    ...globalArgs,
    skills: {
      type: 'positional',
      description: 'Skill names to update (omit for all outdated)',
      required: false,
    },
    stdin: {
      type: 'boolean',
      description: 'Read pre-computed status JSON from stdin',
      default: false,
    },
    'from-file': {
      type: 'string',
      description: 'Read pre-computed status JSON from a local file',
    },
    'from-url': {
      type: 'string',
      description: 'Fetch pre-computed status JSON from a URL (GET, 5s timeout)',
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip confirmation prompts',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const skillNames = args.skills ? String(args.skills).split(',').map((s) => s.trim()) : []

    try {
      const results = await updateSkills(skillNames, {
        stdin: args.stdin,
        fromFile: args['from-file'],
        fromUrl: args['from-url'],
        yes: args.yes,
        json: args.json,
        quiet: args.quiet,
      })

      if (args.json) {
        out.raw(results)
      } else {
        const updated = results.filter((r) => r.status === 'updated')
        const failed = results.filter((r) => r.status === 'failed')
        if (updated.length > 0) {
          out.success(`Updated ${updated.length} skill(s): ${updated.map((r) => r.skill).join(', ')}`)
        }
        if (failed.length > 0) {
          out.error(`Failed to update ${failed.length} skill(s): ${failed.map((r) => r.skill).join(', ')}`)
        }
        if (results.length === 0) {
          out.info('Nothing to update.')
        }
      }

      const hasFailed = results.some((r) => r.status === 'failed')
      process.exit(hasFailed ? EXIT.FAILURES : EXIT.OK)
    } catch (e) {
      out.error(e instanceof Error ? e.message : String(e))
      process.exit(EXIT.ERROR)
    }
  },
})
```

#### Example Test Cases

```typescript
// Integration-level tests for CLI wiring (in skill-outdated.test.ts and skill-update.test.ts)

import { describe, expect, test } from 'bun:test'
import { spawnSync } from '../lib/runtime'

// These test the CLI entry point via `bun run .scripts/bin/agents.ts`
// to verify argument parsing and subcommand routing.

describe('CLI — skill outdated', () => {
  test('--json flag produces valid JSON output', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'outdated', '--json',
    ], { cwd: '/private/etc/infra/pub/ai' })
    // Should exit 0 or 2, but output must be valid JSON
    if (proc.exitCode === 0) {
      expect(() => JSON.parse(proc.stdout)).not.toThrow()
    }
  })

  test('--from-file with missing path exits with error', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'outdated', '--from-file', '/nonexistent/path.json',
    ], { cwd: '/private/etc/infra/pub/ai' })
    expect(proc.exitCode).not.toBe(0)
    expect(proc.stderr).toContain('E_')
  })

  test('--help outputs usage information', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'outdated', '--help',
    ], { cwd: '/private/etc/infra/pub/ai' })
    expect(proc.stdout).toContain('outdated')
    expect(proc.stdout).toContain('--stdin')
    expect(proc.stdout).toContain('--from-file')
    expect(proc.stdout).toContain('--from-url')
  })
})

describe('CLI — skill update', () => {
  test('--json flag produces valid JSON output', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'update', '--json', '--yes',
    ], { cwd: '/private/etc/infra/pub/ai' })
    if (proc.exitCode === 0) {
      expect(() => JSON.parse(proc.stdout)).not.toThrow()
    }
  })

  test('accepts skill names as positional arguments', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'update', 'beads', '--yes', '--json',
    ], { cwd: '/private/etc/infra/pub/ai' })
    // Should not crash with positional arg
    expect(proc.exitCode).toBeDefined()
  })

  test('--help outputs usage information', () => {
    const proc = spawnSync([
      'bun', 'run', '.scripts/bin/agents.ts',
      'skill', 'update', '--help',
    ], { cwd: '/private/etc/infra/pub/ai' })
    expect(proc.stdout).toContain('update')
    expect(proc.stdout).toContain('--yes')
    expect(proc.stdout).toContain('--stdin')
  })
})
```

#### Acceptance Criteria

- [ ] `skill outdated` subcommand registered in Citty command tree under `skill`
- [ ] `skill update` subcommand registered in Citty command tree under `skill`
- [ ] `skill outdated` accepts `--json`, `--stdin`, `--from-file <path>`, `--from-url <url>`
- [ ] `skill update` accepts positional `[skills...]`, `--json`, `--stdin`, `--from-file`, `--from-url`, `--yes`
- [ ] Both commands inherit `globalArgs` (--verbose, --json, --quiet)
- [ ] `--help` for both commands describes all flags
- [ ] Exit codes: 0 (success), 1 (partial failures in update), 2 (fatal error)
- [ ] `skill update` with `--yes` skips confirmation prompt
- [ ] `skill update` without `--yes` prompts for confirmation before re-installing (using `lib/prompts/confirm.ts`)
- [ ] Both commands pass through to the library functions without duplicating logic

## Notes

- Named `outdated` (not `check`) to avoid collision with existing `skill deps check` and `skill check-all` -- follows npm convention (`npm outdated`)
- The existing `external-skills.ts` `checkDrift` function covers the git-ls-remote path -- reuse that logic but generalize it
- The `--stdin` / `--from-file` / `--from-url` input methods allow integration with CI systems or pre-computed status artifacts
- The GitHub Trees API path (tree SHA comparison) is the most efficient -- one API call per repo, not per skill
- `update` deliberately re-invokes `addSkill` rather than doing partial updates -- simpler, matches vercel's approach
- Rate limiting: GitHub API calls should respect the existing `github.ts` auth + token caching
