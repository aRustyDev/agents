import { pathExists, readTextFile, writeTextFile } from '@agents/core/file-io'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'

export function parseNdjson<T>(content: string): T[] {
  return content
    .split('\n')
    .filter((line) => line.trim().length > 0)
    .map((line) => JSON.parse(line) as T)
}

export function serializeNdjson<T>(entries: T[]): string {
  return entries.map((e) => JSON.stringify(e)).join('\n') + '\n'
}

export async function readNdjsonFile<T>(path: string): Promise<Result<T[]>> {
  if (!pathExists(path)) return ok([])
  const content = await readTextFile(path)
  if (!content.ok) return content as Result<never>
  try {
    return ok(parseNdjson<T>(content.value))
  } catch (e) {
    return err(new SdkError(`Failed to parse NDJSON: ${path}`, 'E_STORAGE_BACKEND', String(e)))
  }
}

export async function writeNdjsonFile<T>(path: string, entries: T[]): Promise<Result<void>> {
  // Atomic write: write to .tmp then rename
  const tmpPath = `${path}.tmp`
  const content = serializeNdjson(entries)
  const writeResult = await writeTextFile(tmpPath, content)
  if (!writeResult.ok) return writeResult
  try {
    const { renameSync } = await import('node:fs')
    renameSync(tmpPath, path)
    return ok(undefined)
  } catch (e) {
    return err(
      new SdkError(`Failed to atomically rename ${tmpPath}`, 'E_STORAGE_BACKEND', String(e))
    )
  }
}

export async function appendNdjsonFile<T>(path: string, entries: T[]): Promise<Result<void>> {
  const { appendFileSync } = await import('node:fs')
  try {
    const content = entries.map((e) => JSON.stringify(e)).join('\n') + '\n'
    appendFileSync(path, content)
    return ok(undefined)
  } catch (e) {
    return err(new SdkError(`Failed to append to ${path}`, 'E_STORAGE_BACKEND', String(e)))
  }
}
