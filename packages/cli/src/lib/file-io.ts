/**
 * Unified file I/O operations with Result error handling.
 *
 * All operations return Result<T, CliError> to avoid scattered try/catch
 * blocks across command implementations. Designed for use by verb-first
 * command modules in the agents CLI.
 */

import { existsSync, statSync } from 'node:fs'
import { copyFile, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { CliError, err, ok, type Result } from './types'

// Re-export symlink utilities for single-import convenience
export { auditSymlinks, checkSymlink, createSymlink, resolveChain } from './symlink'
export type { AuditOptions, SymlinkReport, SymlinkStatus } from './symlink'

// ---------------------------------------------------------------------------
// Read operations
// ---------------------------------------------------------------------------

/** Read a file as UTF-8 text. */
export async function readTextFile(path: string): Promise<Result<string>> {
  try {
    const content = await readFile(path, 'utf-8')
    return ok(content)
  } catch (e) {
    return err(new CliError(
      `Failed to read ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_READ_FILE'
    ))
  }
}

/** Read and parse a JSON file. */
export async function readJsonFile<T = unknown>(path: string): Promise<Result<T>> {
  const text = await readTextFile(path)
  if (!text.ok) return text
  try {
    return ok(JSON.parse(text.value) as T)
  } catch (e) {
    return err(new CliError(
      `Failed to parse JSON in ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_PARSE_JSON'
    ))
  }
}

/** Read directory entries. */
export async function listDirectory(
  path: string,
  opts?: { recursive?: boolean; withFileTypes?: true }
): Promise<Result<import('node:fs').Dirent[]>> {
  try {
    const entries = await readdir(path, { withFileTypes: true, recursive: opts?.recursive })
    return ok(entries)
  } catch (e) {
    return err(new CliError(
      `Failed to read directory ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_READ_DIR'
    ))
  }
}

// ---------------------------------------------------------------------------
// Write operations
// ---------------------------------------------------------------------------

/** Write text content to a file, creating parent directories as needed. */
export async function writeTextFile(path: string, content: string): Promise<Result<void>> {
  try {
    await mkdir(dirname(path), { recursive: true })
    await writeFile(path, content, 'utf-8')
    return ok(undefined)
  } catch (e) {
    return err(new CliError(
      `Failed to write ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_WRITE_FILE'
    ))
  }
}

/** Serialize data as JSON and write to a file. */
export async function writeJsonFile(path: string, data: unknown, indent = 2): Promise<Result<void>> {
  try {
    const content = JSON.stringify(data, null, indent) + '\n'
    return writeTextFile(path, content)
  } catch (e) {
    return err(new CliError(
      `Failed to serialize JSON for ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_SERIALIZE_JSON'
    ))
  }
}

// ---------------------------------------------------------------------------
// Directory operations
// ---------------------------------------------------------------------------

/** Ensure a directory exists, creating it recursively if needed. */
export async function ensureDir(path: string): Promise<Result<void>> {
  try {
    await mkdir(path, { recursive: true })
    return ok(undefined)
  } catch (e) {
    return err(new CliError(
      `Failed to create directory ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_MKDIR'
    ))
  }
}

// ---------------------------------------------------------------------------
// Copy / Remove operations
// ---------------------------------------------------------------------------

/** Copy a file from source to destination, creating parent dirs as needed. */
export async function copyFileSafe(src: string, dest: string): Promise<Result<void>> {
  try {
    await mkdir(dirname(dest), { recursive: true })
    await copyFile(src, dest)
    return ok(undefined)
  } catch (e) {
    return err(new CliError(
      `Failed to copy ${src} → ${dest}: ${e instanceof Error ? e.message : String(e)}`,
      'E_COPY_FILE'
    ))
  }
}

/** Remove a file or directory. */
export async function removePath(path: string, opts?: { recursive?: boolean }): Promise<Result<void>> {
  try {
    await rm(path, { recursive: opts?.recursive, force: true })
    return ok(undefined)
  } catch (e) {
    return err(new CliError(
      `Failed to remove ${path}: ${e instanceof Error ? e.message : String(e)}`,
      'E_REMOVE'
    ))
  }
}

// ---------------------------------------------------------------------------
// Existence checks (sync — fine for guard clauses)
// ---------------------------------------------------------------------------

/** Check if a path exists (synchronous). */
export function pathExists(path: string): boolean {
  return existsSync(path)
}

/** Check if a file exists at the given path (synchronous). */
export function fileExists(path: string): boolean {
  try {
    return statSync(path).isFile()
  } catch {
    return false
  }
}

/** Check if a directory exists at the given path (synchronous). */
export function dirExists(path: string): boolean {
  try {
    return statSync(path).isDirectory()
  } catch {
    return false
  }
}
