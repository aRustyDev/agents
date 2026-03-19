/**
 * Symlink health checking, creation, and auditing.
 *
 * Provides utilities for verifying symlink integrity, creating symlinks
 * with parent directory creation, resolving symlink chains, and auditing
 * directories for broken links.
 */

import { access, lstat, mkdir, readdir, readlink, realpath, rm, symlink } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SymlinkStatus {
  /** The symlink path */
  path: string
  /** What the symlink points to */
  target: string
  /** Target exists and is accessible */
  valid: boolean
  /** Symlink exists but target does not */
  broken: boolean
}

export interface SymlinkReport {
  healthy: SymlinkStatus[]
  broken: SymlinkStatus[]
}

// ---------------------------------------------------------------------------
// checkSymlink
// ---------------------------------------------------------------------------

/**
 * Inspect a single path to determine its symlink health.
 *
 * Uses `lstat` to verify the path is a symlink, `readlink` to discover the
 * target, and `access` to confirm the target is reachable.
 *
 * @throws if the path does not exist or is not a symlink
 */
export async function checkSymlink(path: string): Promise<SymlinkStatus> {
  const stats = await lstat(path)

  if (!stats.isSymbolicLink()) {
    throw new Error(`Not a symlink: ${path}`)
  }

  const target = await readlink(path)
  const absoluteTarget = resolve(dirname(path), target)

  let valid = false
  try {
    await access(absoluteTarget)
    valid = true
  } catch {
    // target is unreachable
  }

  return {
    path,
    target,
    valid,
    broken: !valid,
  }
}

// ---------------------------------------------------------------------------
// createSymlink
// ---------------------------------------------------------------------------

/**
 * Create a symlink from `link` pointing to `target`.
 *
 * If the parent directory of `link` does not exist it is created recursively.
 * If `link` already exists and is a symlink it is removed first and recreated.
 * If `link` exists but is not a symlink, an error is thrown to avoid
 * accidentally destroying real files.
 */
export async function createSymlink(target: string, link: string): Promise<void> {
  // Ensure parent directory exists
  await mkdir(dirname(link), { recursive: true })

  // If link already exists, handle it
  try {
    const stats = await lstat(link)
    if (stats.isSymbolicLink()) {
      await rm(link)
    } else {
      throw new Error(`Path exists and is not a symlink: ${link}`)
    }
  } catch (e) {
    // If the error is our own rethrow, propagate it
    if (e instanceof Error && e.message.startsWith('Path exists')) throw e
    // Otherwise the path doesn't exist, which is fine
  }

  await symlink(target, link)
}

// ---------------------------------------------------------------------------
// resolveChain
// ---------------------------------------------------------------------------

/**
 * Follow a chain of symlinks and return every path in the chain.
 *
 * Returns an array starting with the original path, followed by each
 * intermediate symlink target, and ending with the final real path
 * (resolved via `realpath`).
 *
 * For a non-chained symlink `A -> B` the result is `[A, B]`.
 * For a chain `A -> B -> C` the result is `[A, B, C]`.
 *
 * @throws if the starting path does not exist
 */
export async function resolveChain(path: string): Promise<string[]> {
  const chain: string[] = [resolve(path)]
  const seen = new Set<string>()
  let current = resolve(path)

  while (true) {
    // Guard against circular symlinks
    if (seen.has(current)) break
    seen.add(current)

    let stats
    try {
      stats = await lstat(current)
    } catch {
      // Current path doesn't exist (broken end of chain) -- stop here
      break
    }

    if (!stats.isSymbolicLink()) break

    const target = await readlink(current)
    const absoluteTarget = resolve(dirname(current), target)
    chain.push(absoluteTarget)
    current = absoluteTarget
  }

  // Append the final realpath if it differs from the last chain entry
  try {
    const real = await realpath(chain[0]!)
    if (chain[chain.length - 1] !== real) {
      chain.push(real)
    }
  } catch {
    // realpath fails when the final target doesn't exist -- that's ok
  }

  return chain
}

// ---------------------------------------------------------------------------
// auditSymlinks
// ---------------------------------------------------------------------------

export interface AuditOptions {
  /** Recurse into subdirectories. Defaults to `true`. */
  recursive?: boolean
}

/**
 * Scan a directory for all symlinks and categorise them as healthy or broken.
 *
 * By default the scan is recursive. Set `opts.recursive` to `false` to limit
 * the scan to the immediate directory.
 */
export async function auditSymlinks(
  dir: string,
  opts?: AuditOptions,
): Promise<SymlinkReport> {
  const recursive = opts?.recursive ?? true
  const report: SymlinkReport = { healthy: [], broken: [] }

  await scanDir(resolve(dir), recursive, report)

  return report
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

async function scanDir(
  dir: string,
  recursive: boolean,
  report: SymlinkReport,
): Promise<void> {
  let entries
  try {
    entries = await readdir(dir, { withFileTypes: true })
  } catch {
    return // directory unreadable -- skip silently
  }

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)

    if (entry.isSymbolicLink()) {
      const status = await checkSymlink(fullPath)
      if (status.valid) {
        report.healthy.push(status)
      } else {
        report.broken.push(status)
      }
    } else if (recursive && entry.isDirectory()) {
      await scanDir(fullPath, recursive, report)
    }
  }
}
