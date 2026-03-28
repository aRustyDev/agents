/**
 * Runtime-aware shims for cross-runtime compatibility.
 *
 * Detects Bun vs Node at runtime and uses the optimal API for each.
 * Bun gets its native APIs (faster file I/O, native crypto).
 * Node gets standard library equivalents.
 *
 * All exports are async and work identically on both runtimes.
 */

/** True when running under Bun. */
export const isBun = typeof globalThis.Bun !== 'undefined'

// ---------------------------------------------------------------------------
// File I/O
// ---------------------------------------------------------------------------

/** Read a file as UTF-8 text. */
export async function readText(path: string): Promise<string> {
  if (isBun) return Bun.file(path).text()
  const { readFile } = await import('node:fs/promises')
  return readFile(path, 'utf-8')
}

/** Read a file and parse as JSON. */
export async function readJson<T = unknown>(path: string): Promise<T> {
  const text = await readText(path)
  return JSON.parse(text) as T
}

/** Write text to a file. */
export async function writeText(path: string, data: string): Promise<void> {
  if (isBun) {
    await Bun.write(path, data)
    return
  }
  const { writeFile } = await import('node:fs/promises')
  await writeFile(path, data)
}

/** Check if a file exists. */
export async function fileExists(path: string): Promise<boolean> {
  if (isBun) return Bun.file(path).exists()
  const { access } = await import('node:fs/promises')
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}

/** Read a file as a ReadableStream (for hashing large files). */
export async function fileStream(path: string): Promise<ReadableStream<Uint8Array>> {
  if (isBun) return Bun.file(path).stream()
  const { createReadStream } = await import('node:fs')
  const nodeStream = createReadStream(path)
  return new ReadableStream({
    start(controller) {
      nodeStream.on('data', (chunk: Buffer) => controller.enqueue(new Uint8Array(chunk)))
      nodeStream.on('end', () => controller.close())
      nodeStream.on('error', (err) => controller.error(err))
    },
  })
}

// ---------------------------------------------------------------------------
// Crypto
// ---------------------------------------------------------------------------

/** Create a SHA-256 incremental hasher. */
export function createSha256Hasher(): {
  update(data: Uint8Array | string): void
  digest(encoding: 'hex'): string
} {
  if (isBun) {
    const hasher = new Bun.CryptoHasher('sha256')
    return {
      update(data) {
        hasher.update(data)
      },
      digest(encoding) {
        return hasher.digest(encoding)
      },
    }
  }
  // Node.js path
  const crypto = require('node:crypto')
  const hash = crypto.createHash('sha256')
  return {
    update(data: Uint8Array | string) {
      hash.update(data)
    },
    digest(encoding: 'hex') {
      return hash.digest(encoding)
    },
  }
}

// ---------------------------------------------------------------------------
// Process spawning
// ---------------------------------------------------------------------------

interface SpawnSyncResult {
  stdout: string
  stderr: string
  exitCode: number
  success: boolean
}

/** Synchronously spawn a subprocess and capture output. */
export function spawnSync(
  cmd: string[],
  opts?: { cwd?: string; env?: Record<string, string>; stdin?: 'inherit' | 'pipe' }
): SpawnSyncResult {
  if (isBun) {
    const result = Bun.spawnSync(cmd, {
      cwd: opts?.cwd,
      env: opts?.env ? { ...process.env, ...opts.env } : undefined,
      stdin: opts?.stdin ?? 'pipe',
      stdout: 'pipe',
      stderr: 'pipe',
    })
    return {
      stdout: result.stdout?.toString() ?? '',
      stderr: result.stderr?.toString() ?? '',
      exitCode: result.exitCode,
      success: result.exitCode === 0,
    }
  }
  const cp = require('node:child_process')
  const result = cp.spawnSync(cmd[0], cmd.slice(1), {
    cwd: opts?.cwd,
    env: opts?.env ? { ...process.env, ...opts.env } : undefined,
    stdin: opts?.stdin ?? 'pipe',
    stdio: ['pipe', 'pipe', 'pipe'],
    encoding: 'utf-8',
  })
  return {
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? '',
    exitCode: result.status ?? 1,
    success: result.status === 0,
  }
}

/** Asynchronously spawn a subprocess and capture output. */
export async function spawnAsync(cmd: string[], opts?: { cwd?: string }): Promise<SpawnSyncResult> {
  if (isBun) {
    const proc = Bun.spawn(cmd, {
      cwd: opts?.cwd,
      stdout: 'pipe',
      stderr: 'pipe',
    })
    const stdout = await new Response(proc.stdout).text()
    const stderr = await new Response(proc.stderr).text()
    const exitCode = await proc.exited
    return { stdout, stderr, exitCode, success: exitCode === 0 }
  }
  const cp = await import('node:child_process')
  return new Promise((resolve) => {
    const proc = cp.spawn(cmd[0]!, cmd.slice(1), {
      cwd: opts?.cwd,
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    let stdout = ''
    let stderr = ''
    proc.stdout?.on('data', (d: Buffer) => {
      stdout += d.toString()
    })
    proc.stderr?.on('data', (d: Buffer) => {
      stderr += d.toString()
    })
    proc.on('close', (code) => {
      const exitCode = code ?? 1
      resolve({ stdout, stderr, exitCode, success: exitCode === 0 })
    })
  })
}

// ---------------------------------------------------------------------------
// Path resolution
// ---------------------------------------------------------------------------

/**
 * Get the directory of the current module.
 * Works on both Bun (import.meta.dir) and Node 21+ (import.meta.dirname).
 * For older Node, falls back to fileURLToPath.
 */
export function currentDir(meta: ImportMeta): string {
  if ('dir' in meta && typeof meta.dir === 'string') return meta.dir
  if ('dirname' in meta && typeof meta.dirname === 'string') return meta.dirname as string
  // Fallback for Node < 21
  const { fileURLToPath } = require('node:url')
  const { dirname } = require('node:path')
  return dirname(fileURLToPath(meta.url))
}
