/**
 * Check whether locked skills are outdated relative to their upstream source.
 *
 * Supports three source types:
 * - `github`: uses the GitHub Trees API to fetch a folder tree SHA and
 *   compare it to the stored `computedHash`.
 * - `git`: uses `git ls-remote` to resolve the current HEAD/ref and
 *   compare to the stored commit hash.
 * - `local`: hashes the on-disk directory and compares to `computedHash`.
 *
 * The main export `checkOutdated()` never throws -- per-skill errors are
 * captured and surfaced as `status: 'unavailable'` results.
 */

import { join } from 'node:path'
import { fetchSkillFolderHash, lsRemote } from './git'
import { hashDirectory } from './hash'
import { readLockfile } from './lockfile'
import type { LockfileV1, SkillLockEntry } from './schemas'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export class OutdatedError extends CliError {
  constructor(
    readonly skill: string,
    message: string,
    code: string,
    hint?: string,
    cause?: unknown
  ) {
    super(message, code, hint, cause)
  }
}

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface OutdatedOptions {
  stdin?: boolean
  fromFile?: string
  fromUrl?: string
  json?: boolean
  quiet?: boolean
  cwd?: string
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

const FETCH_TIMEOUT_MS = 5_000

/**
 * Resolve the lockfile data from one of the supported input sources.
 *
 * Priority:
 * 1. `--stdin`      read all of stdin, parse as JSON
 * 2. `--from-file`  read a lockfile at the given path
 * 3. `--from-url`   fetch JSON from a URL (5s timeout)
 * 4. Default        read `skills-lock.json` from cwd
 */
export async function resolveInput(opts: OutdatedOptions): Promise<Result<LockfileV1>> {
  if (opts.stdin) {
    return readFromStdin()
  }
  if (opts.fromUrl) {
    return fetchFromUrl(opts.fromUrl)
  }
  if (opts.fromFile) {
    return readLockfile<LockfileV1>('skills', opts.fromFile)
  }
  const cwd = opts.cwd ?? process.cwd()
  return readLockfile<LockfileV1>('skills', join(cwd, 'skills-lock.json'))
}

async function readFromStdin(): Promise<Result<LockfileV1>> {
  try {
    const chunks: string[] = []
    const reader = Bun.stdin.stream().getReader()
    const decoder = new TextDecoder()
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      chunks.push(decoder.decode(value, { stream: true }))
    }
    chunks.push(decoder.decode())
    const text = chunks.join('')
    const parsed = JSON.parse(text) as LockfileV1
    return ok(parsed)
  } catch (e) {
    return err(
      new OutdatedError(
        '',
        'Failed to read lockfile from stdin',
        'E_STDIN_READ',
        'Pipe valid JSON to stdin',
        e
      )
    )
  }
}

async function fetchFromUrl(url: string): Promise<Result<LockfileV1>> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)
  try {
    const response = await fetch(url, { signal: controller.signal })
    if (!response.ok) {
      return err(
        new OutdatedError(
          '',
          `HTTP ${response.status} fetching lockfile from ${url}`,
          'E_FETCH_FAILED',
          'Check the URL and try again'
        )
      )
    }
    const parsed = (await response.json()) as LockfileV1
    return ok(parsed)
  } catch (e) {
    const isAbort = e instanceof DOMException && e.name === 'AbortError'
    if (isAbort) {
      return err(
        new OutdatedError(
          '',
          `Fetch timed out after ${FETCH_TIMEOUT_MS}ms for ${url}`,
          'E_FETCH_TIMEOUT',
          'The server may be slow or unreachable'
        )
      )
    }
    return err(
      new OutdatedError(
        '',
        `Failed to fetch lockfile from ${url}`,
        'E_FETCH_FAILED',
        e instanceof Error ? e.message : String(e),
        e
      )
    )
  } finally {
    clearTimeout(timer)
  }
}

// ---------------------------------------------------------------------------
// Per-source check strategies
// ---------------------------------------------------------------------------

async function checkGithub(name: string, entry: SkillLockEntry): Promise<OutdatedResult> {
  try {
    const remoteHash = await fetchSkillFolderHash(entry.source, name)
    if (remoteHash === null) {
      return {
        skill: name,
        source: entry.source,
        sourceType: entry.sourceType,
        status: 'unavailable',
        currentHash: entry.computedHash,
        error: `Skill folder "${name}" not found in ${entry.source}`,
      }
    }
    const status: OutdatedStatus = remoteHash === entry.computedHash ? 'current' : 'outdated'
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status,
      currentHash: entry.computedHash,
      remoteHash,
    }
  } catch (e) {
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status: 'unavailable',
      currentHash: entry.computedHash,
      error: e instanceof Error ? e.message : String(e),
    }
  }
}

async function checkGit(name: string, entry: SkillLockEntry): Promise<OutdatedResult> {
  try {
    const result = await lsRemote(entry.source)
    if (!result.ok) {
      return {
        skill: name,
        source: entry.source,
        sourceType: entry.sourceType,
        status: 'unavailable',
        currentHash: entry.computedHash,
        error: result.error.message,
      }
    }
    const remoteHash = result.value
    const status: OutdatedStatus = remoteHash === entry.computedHash ? 'current' : 'outdated'
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status,
      currentHash: entry.computedHash,
      remoteHash,
    }
  } catch (e) {
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status: 'unavailable',
      currentHash: entry.computedHash,
      error: e instanceof Error ? e.message : String(e),
    }
  }
}

async function checkLocal(
  name: string,
  entry: SkillLockEntry,
  cwd: string
): Promise<OutdatedResult> {
  const skillDir = join(cwd, 'context', 'skills', name)
  try {
    const localHash = await hashDirectory(skillDir)
    const status: OutdatedStatus = localHash === entry.computedHash ? 'current' : 'outdated'
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status,
      currentHash: entry.computedHash,
      remoteHash: localHash,
    }
  } catch (e) {
    return {
      skill: name,
      source: entry.source,
      sourceType: entry.sourceType,
      status: 'unavailable',
      currentHash: entry.computedHash,
      error: e instanceof Error ? e.message : String(e),
    }
  }
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

/**
 * Check all skills in a lockfile for outdated status.
 *
 * Never throws. Per-skill errors are reported as `status: 'unavailable'`
 * with an `error` message describing the failure.
 *
 * @param opts - Input resolution and display options.
 * @returns Array of per-skill outdated check results.
 */
export async function checkOutdated(opts: OutdatedOptions = {}): Promise<OutdatedResult[]> {
  const cwd = opts.cwd ?? process.cwd()

  const inputResult = await resolveInput(opts)
  if (!inputResult.ok) {
    // No lockfile available -- return empty rather than throwing
    return []
  }

  const lockfile = inputResult.value
  const skills = lockfile.skills
  if (!skills || Object.keys(skills).length === 0) {
    return []
  }

  const results: OutdatedResult[] = []

  // Process all skills concurrently
  const checks = Object.entries(skills).map(
    async ([name, entry]: [string, SkillLockEntry]): Promise<OutdatedResult> => {
      switch (entry.sourceType) {
        case 'github':
          return checkGithub(name, entry)
        case 'git':
          return checkGit(name, entry)
        case 'local':
          return checkLocal(name, entry, cwd)
        default:
          return {
            skill: name,
            source: entry.source,
            sourceType: entry.sourceType,
            status: 'unknown',
            currentHash: entry.computedHash,
            error: `Unknown source type: ${entry.sourceType}`,
          }
      }
    }
  )

  const settled = await Promise.allSettled(checks)
  for (const result of settled) {
    if (result.status === 'fulfilled') {
      results.push(result.value)
    } else {
      // Should not happen since individual checks catch errors, but guard anyway
      results.push({
        skill: '(unknown)',
        source: '',
        sourceType: '',
        status: 'unavailable',
        error: result.reason instanceof Error ? result.reason.message : String(result.reason),
      })
    }
  }

  return results
}
