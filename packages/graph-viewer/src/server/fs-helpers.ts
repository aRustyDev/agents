/**
 * Filesystem helpers for graph persistence.
 *
 * Provides atomic and direct write operations. Atomic writes use a
 * write-then-rename strategy so readers never see partial content --
 * the file either contains the old data or the new data, never a mix.
 *
 * Uses the runtime-agnostic `writeText` helper so this works on both
 * Bun and Node.js.
 */

import { rename } from 'node:fs/promises'
import { writeText } from '@agents/core/runtime'

/**
 * Atomically write data to a file.
 *
 * Writes to `path + '.tmp'` first, then renames to `path`. This guarantees
 * that concurrent readers always see a complete file. If the process crashes
 * between write and rename, only the `.tmp` file is left behind (harmless).
 *
 * @param path - The target file path.
 * @param data - The string content to write.
 */
export async function atomicWrite(path: string, data: string): Promise<void> {
  const tmpPath = `${path}.tmp`
  await writeText(tmpPath, data)
  await rename(tmpPath, path)
}

/**
 * Write data directly to a file without atomic rename.
 *
 * Used for non-critical files like lock files where a partial write is
 * acceptable — the lock file is always treated as optional and can be
 * regenerated from the graph data.
 *
 * @param path - The target file path.
 * @param data - The string content to write.
 */
export async function directWrite(path: string, data: string): Promise<void> {
  await writeText(path, data)
}
