/**
 * Zip archive primitives — create and extract zip files.
 *
 * Uses the system `zip` / `unzip` commands (available on macOS and Linux)
 * to avoid adding external dependencies.
 */

import { execSync } from 'node:child_process'
import { readdir, writeFile } from 'node:fs/promises'
import { dirname, join, relative } from 'node:path'
import { ensureDir } from './file-io'
import { BaseError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// zipDirectory
// ---------------------------------------------------------------------------

/**
 * Create a zip from a directory, preserving relative paths.
 *
 * @param sourceDir  - Root directory whose contents will be zipped.
 * @param outputPath - Absolute path for the resulting `.zip` file.
 * @param opts.exclude - Glob patterns passed to `zip -x`.
 */
export async function zipDirectory(
  sourceDir: string,
  outputPath: string,
  opts?: { exclude?: string[] }
): Promise<Result<{ path: string; fileCount: number }>> {
  const excludeArgs = (opts?.exclude ?? []).flatMap((p) => ['-x', p])
  try {
    const dirResult = await ensureDir(dirname(outputPath))
    if (!dirResult.ok) return dirResult as Result<never>

    execSync(['zip', '-r', outputPath, '.', ...excludeArgs].map((a) => `"${a}"`).join(' '), {
      cwd: sourceDir,
      stdio: 'pipe',
    })

    const fileCount = countZipEntries(outputPath)
    return ok({ path: outputPath, fileCount })
  } catch (e) {
    return err(
      new BaseError(
        `Failed to create zip: ${e instanceof Error ? e.message : String(e)}`,
        'E_ARCHIVE'
      )
    )
  }
}

// ---------------------------------------------------------------------------
// zipFiles
// ---------------------------------------------------------------------------

/**
 * Create a zip from explicit file entries.
 *
 * Each entry specifies a relative `path` inside the zip and the file content.
 * A temporary staging directory is used to materialize the entries before
 * running `zip`.
 */
export async function zipFiles(
  files: Array<{ path: string; content: string | Buffer }>,
  outputPath: string
): Promise<Result<{ path: string; fileCount: number }>> {
  const { mkdtemp, rm } = await import('node:fs/promises')
  const { tmpdir } = await import('node:os')
  const staging = await mkdtemp(join(tmpdir(), 'zipfiles-'))

  try {
    // Write each entry into the staging tree
    for (const f of files) {
      const dest = join(staging, f.path)
      const dirResult = await ensureDir(dirname(dest))
      if (!dirResult.ok) return dirResult as Result<never>
      await writeFile(dest, f.content)
    }

    const result = await zipDirectory(staging, outputPath)
    return result
  } catch (e) {
    return err(
      new BaseError(
        `Failed to create zip from files: ${e instanceof Error ? e.message : String(e)}`,
        'E_ARCHIVE'
      )
    )
  } finally {
    await rm(staging, { recursive: true, force: true }).catch(() => {})
  }
}

// ---------------------------------------------------------------------------
// unzip
// ---------------------------------------------------------------------------

/**
 * Extract a zip to a directory. Returns list of extracted file paths
 * (relative to `outputDir`).
 */
export async function unzip(zipPath: string, outputDir: string): Promise<Result<string[]>> {
  try {
    const dirResult = await ensureDir(outputDir)
    if (!dirResult.ok) return dirResult as Result<never>

    execSync(`unzip -o "${zipPath}" -d "${outputDir}"`, { stdio: 'pipe' })

    // Walk extracted tree to build relative path list
    const files: string[] = []
    async function walk(dir: string) {
      const entries = await readdir(dir, { withFileTypes: true })
      for (const e of entries) {
        const full = join(dir, e.name)
        if (e.isDirectory()) await walk(full)
        else files.push(relative(outputDir, full))
      }
    }
    await walk(outputDir)
    return ok(files.sort())
  } catch (e) {
    return err(
      new BaseError(
        `Failed to extract zip: ${e instanceof Error ? e.message : String(e)}`,
        'E_ARCHIVE'
      )
    )
  }
}

// ---------------------------------------------------------------------------
// listZip
// ---------------------------------------------------------------------------

/** List contents of a zip without extracting. Returns file paths only. */
export async function listZip(zipPath: string): Promise<Result<string[]>> {
  try {
    const files = listZipEntries(zipPath)
    return ok(files.sort())
  } catch (e) {
    return err(
      new BaseError(
        `Failed to list zip: ${e instanceof Error ? e.message : String(e)}`,
        'E_ARCHIVE'
      )
    )
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * List file entries in a zip using `unzip -Z1` (zipinfo mode).
 * Returns only file paths (directories are excluded).
 */
function listZipEntries(zipPath: string): string[] {
  const output = execSync(`unzip -Z1 "${zipPath}"`, { stdio: 'pipe' }).toString()
  return output
    .split('\n')
    .map((l) => l.trim())
    .filter((f) => f && !f.endsWith('/'))
}

/** Count file entries in a zip (excludes directories). */
function countZipEntries(zipPath: string): number {
  try {
    return listZipEntries(zipPath).length
  } catch {
    return 0
  }
}
