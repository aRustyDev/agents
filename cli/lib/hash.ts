/**
 * Content-addressed hashing for files and directories.
 *
 * Port of cli/plugin-hash.py -- the SHA256 algorithm is identical
 * so that both implementations produce the same digest for the same input.
 *
 * Directory hash algorithm:
 *   1. Recursively collect all files (skipping .git/, node_modules/, __pycache__/).
 *   2. Sort by relative POSIX path (forward slashes, UTF-8).
 *   3. For each file: update hasher with `relativePath \0 fileContents \0`.
 *   4. Return the final hex digest.
 */

import { readdir, stat } from 'node:fs/promises'
import { join, relative } from 'node:path'
import { createSha256Hasher, fileStream } from './runtime'

// Directories that are never included in a directory hash.
const SKIP_DIRS = new Set(['.git', 'node_modules', '__pycache__'])

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * SHA256 hash of a single file's contents, returned as a lowercase hex string.
 */
export async function hashFile(path: string): Promise<string> {
  const hasher = createSha256Hasher()

  // Stream in chunks to keep memory low for large files.
  const stream = await fileStream(path)
  for await (const chunk of stream) {
    hasher.update(chunk)
  }

  return hasher.digest('hex')
}

/**
 * Deterministic SHA256 hash of an entire directory tree.
 *
 * The hash encodes both structure (relative paths) and content so that
 * renaming, adding, or removing any file changes the digest.
 */
export async function hashDirectory(path: string): Promise<string> {
  const files = await collectFiles(path)

  // Sort by relative POSIX path for determinism (matches Python's sorted rglob).
  files.sort((a, b) => a.rel.localeCompare(b.rel))

  const hasher = createSha256Hasher()
  const NULL = new Uint8Array([0])

  for (const { abs, rel } of files) {
    // Relative path as UTF-8
    hasher.update(rel)
    hasher.update(NULL)

    // File contents streamed in chunks
    const stream = await fileStream(abs)
    for await (const chunk of stream) {
      hasher.update(chunk)
    }
    hasher.update(NULL)
  }

  return hasher.digest('hex')
}

/**
 * Auto-detect whether `path` is a file or directory and hash accordingly.
 *
 * @throws {Error} if `path` does not exist.
 */
export async function computeHash(path: string): Promise<string> {
  const info = await stat(path)
  if (info.isFile()) return hashFile(path)
  if (info.isDirectory()) return hashDirectory(path)
  throw new Error(`Path is neither a file nor a directory: ${path}`)
}

/**
 * Compute a short lock key from a source/skill pair.
 *
 * Used as the key in `sources.lock.json` so that manifest renames
 * do not lose tracking history.
 *
 * @returns First 12 hex chars of `sha256(source + "/" + skill)`.
 */
export function lockKey(source: string, skill: string): string {
  const input = `${source}/${skill}`
  const hasher = createSha256Hasher()
  hasher.update(input)
  return hasher.digest('hex').slice(0, 12)
}

/**
 * Prepend the `sha256:` prefix to a raw hex digest.
 */
export function formatHash(hex: string): string {
  return `sha256:${hex}`
}

/**
 * Strip the `sha256:` prefix if present, returning the raw hex digest.
 * Idempotent -- calling on an already-raw hex string is a no-op.
 */
export function parseHash(prefixed: string): string {
  if (prefixed.startsWith('sha256:')) return prefixed.slice(7)
  return prefixed
}

/**
 * Compute the hash of `path` and compare it to `expected`.
 *
 * `expected` may be either a raw hex string or prefixed with `sha256:`.
 */
export async function verifyHash(path: string, expected: string): Promise<boolean> {
  const actual = await computeHash(path)
  return actual === parseHash(expected)
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

interface FileEntry {
  /** Absolute path on disk. */
  abs: string
  /** Relative POSIX path from the root directory (forward slashes). */
  rel: string
}

/**
 * Recursively collect all files under `root`, skipping directories in
 * {@link SKIP_DIRS}. Returns entries with both absolute and relative paths.
 */
async function collectFiles(root: string): Promise<FileEntry[]> {
  const entries: FileEntry[] = []

  async function walk(dir: string): Promise<void> {
    const items = await readdir(dir, { withFileTypes: true })

    for (const item of items) {
      if (item.isDirectory()) {
        if (SKIP_DIRS.has(item.name)) continue
        await walk(join(dir, item.name))
      } else if (item.isFile()) {
        const abs = join(dir, item.name)
        // Use forward slashes for cross-platform consistency with the Python version.
        const rel = relative(root, abs).replaceAll('\\', '/')
        entries.push({ abs, rel })
      }
    }
  }

  await walk(root)
  return entries
}
