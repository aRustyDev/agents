import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { existsSync, statSync } from 'node:fs'
import { mkdtemp, realpath, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  copyFileSafe,
  dirExists,
  ensureDir,
  fileExists,
  listDirectory,
  pathExists,
  readJsonFile,
  readTextFile,
  removePath,
  writeJsonFile,
  writeTextFile,
} from '@agents/core/file-io'

// ---------------------------------------------------------------------------
// Shared fixture directory
// ---------------------------------------------------------------------------

let root: string

beforeAll(async () => {
  root = await realpath(await mkdtemp(join(tmpdir(), 'file-io-test-')))
})

afterAll(async () => {
  const { rm } = await import('node:fs/promises')
  await rm(root, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// readTextFile
// ---------------------------------------------------------------------------

describe('readTextFile', () => {
  test('reads a file successfully', async () => {
    const path = join(root, 'read-text.txt')
    await writeFile(path, 'hello world', 'utf-8')

    const result = await readTextFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('hello world')
    }
  })

  test('returns error for non-existent file', async () => {
    const result = await readTextFile(join(root, 'does-not-exist.txt'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FILE')
      expect(result.error.message).toContain('does-not-exist.txt')
    }
  })

  test('reads UTF-8 content with special characters', async () => {
    const path = join(root, 'utf8-special.txt')
    const content = 'emoji: 🚀 accents: café ñ'
    await writeFile(path, content, 'utf-8')

    const result = await readTextFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe(content)
    }
  })
})

// ---------------------------------------------------------------------------
// readJsonFile
// ---------------------------------------------------------------------------

describe('readJsonFile', () => {
  test('parses valid JSON', async () => {
    const path = join(root, 'valid.json')
    await writeFile(path, JSON.stringify({ name: 'test', count: 42 }), 'utf-8')

    const result = await readJsonFile<{ name: string; count: number }>(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('test')
      expect(result.value.count).toBe(42)
    }
  })

  test('returns error for invalid JSON', async () => {
    const path = join(root, 'invalid.json')
    await writeFile(path, '{ broken json }', 'utf-8')

    const result = await readJsonFile(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_PARSE_JSON')
      expect(result.error.message).toContain('invalid.json')
    }
  })

  test('returns error for non-existent file', async () => {
    const result = await readJsonFile(join(root, 'no-such.json'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FILE')
    }
  })
})

// ---------------------------------------------------------------------------
// writeTextFile
// ---------------------------------------------------------------------------

describe('writeTextFile', () => {
  test('writes content to file', async () => {
    const path = join(root, 'write-text.txt')
    const result = await writeTextFile(path, 'written content')
    expect(result.ok).toBe(true)

    const { readFile: rf } = await import('node:fs/promises')
    const content = await rf(path, 'utf-8')
    expect(content).toBe('written content')
  })

  test('creates parent directories', async () => {
    const path = join(root, 'deep', 'nested', 'dir', 'file.txt')
    const result = await writeTextFile(path, 'deep content')
    expect(result.ok).toBe(true)

    expect(existsSync(path)).toBe(true)
    const { readFile: rf } = await import('node:fs/promises')
    const content = await rf(path, 'utf-8')
    expect(content).toBe('deep content')
  })
})

// ---------------------------------------------------------------------------
// writeJsonFile
// ---------------------------------------------------------------------------

describe('writeJsonFile', () => {
  test('serializes and writes JSON', async () => {
    const path = join(root, 'write.json')
    const data = { hello: 'world', num: 123 }
    const result = await writeJsonFile(path, data)
    expect(result.ok).toBe(true)

    const { readFile: rf } = await import('node:fs/promises')
    const content = await rf(path, 'utf-8')
    expect(JSON.parse(content)).toEqual(data)
    // Should end with newline
    expect(content.endsWith('\n')).toBe(true)
  })

  test('respects custom indent', async () => {
    const path = join(root, 'write-indent.json')
    const data = { a: 1 }
    await writeJsonFile(path, data, 4)

    const { readFile: rf } = await import('node:fs/promises')
    const content = await rf(path, 'utf-8')
    expect(content).toBe(JSON.stringify(data, null, 4) + '\n')
  })
})

// ---------------------------------------------------------------------------
// ensureDir
// ---------------------------------------------------------------------------

describe('ensureDir', () => {
  test('creates nested directories', async () => {
    const path = join(root, 'ensure', 'deeply', 'nested')
    const result = await ensureDir(path)
    expect(result.ok).toBe(true)
    expect(existsSync(path)).toBe(true)
    expect(statSync(path).isDirectory()).toBe(true)
  })

  test('succeeds if directory already exists', async () => {
    const path = join(root, 'ensure-existing')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(path, { recursive: true })

    const result = await ensureDir(path)
    expect(result.ok).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// copyFileSafe
// ---------------------------------------------------------------------------

describe('copyFileSafe', () => {
  test('copies file to destination', async () => {
    const src = join(root, 'copy-src.txt')
    await writeFile(src, 'copy me', 'utf-8')
    const dest = join(root, 'copy-dest.txt')

    const result = await copyFileSafe(src, dest)
    expect(result.ok).toBe(true)

    const { readFile: rf } = await import('node:fs/promises')
    const content = await rf(dest, 'utf-8')
    expect(content).toBe('copy me')
  })

  test('creates parent directories for destination', async () => {
    const src = join(root, 'copy-src2.txt')
    await writeFile(src, 'deep copy', 'utf-8')
    const dest = join(root, 'copy-deep', 'nested', 'dest.txt')

    const result = await copyFileSafe(src, dest)
    expect(result.ok).toBe(true)
    expect(existsSync(dest)).toBe(true)
  })

  test('returns error for non-existent source', async () => {
    const result = await copyFileSafe(
      join(root, 'no-such-source.txt'),
      join(root, 'wont-exist.txt')
    )
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_COPY_FILE')
    }
  })
})

// ---------------------------------------------------------------------------
// removePath
// ---------------------------------------------------------------------------

describe('removePath', () => {
  test('removes a file', async () => {
    const path = join(root, 'remove-me.txt')
    await writeFile(path, 'bye', 'utf-8')
    expect(existsSync(path)).toBe(true)

    const result = await removePath(path)
    expect(result.ok).toBe(true)
    expect(existsSync(path)).toBe(false)
  })

  test('removes a directory recursively', async () => {
    const dir = join(root, 'remove-dir')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(join(dir, 'sub'), { recursive: true })
    await writeFile(join(dir, 'sub', 'file.txt'), 'nested', 'utf-8')

    const result = await removePath(dir, { recursive: true })
    expect(result.ok).toBe(true)
    expect(existsSync(dir)).toBe(false)
  })

  test('succeeds for non-existent path (force)', async () => {
    const result = await removePath(join(root, 'already-gone'))
    expect(result.ok).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// pathExists / fileExists / dirExists
// ---------------------------------------------------------------------------

describe('pathExists', () => {
  test('returns true for existing file', async () => {
    const path = join(root, 'exists-file.txt')
    await writeFile(path, 'hi', 'utf-8')
    expect(pathExists(path)).toBe(true)
  })

  test('returns false for non-existent path', () => {
    expect(pathExists(join(root, 'nope.txt'))).toBe(false)
  })
})

describe('fileExists', () => {
  test('returns true for a file', async () => {
    const path = join(root, 'is-file.txt')
    await writeFile(path, 'content', 'utf-8')
    expect(fileExists(path)).toBe(true)
  })

  test('returns false for a directory', async () => {
    const dir = join(root, 'is-dir-not-file')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })
    expect(fileExists(dir)).toBe(false)
  })

  test('returns false for non-existent path', () => {
    expect(fileExists(join(root, 'nope-file'))).toBe(false)
  })
})

describe('dirExists', () => {
  test('returns true for a directory', async () => {
    const dir = join(root, 'is-a-dir')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })
    expect(dirExists(dir)).toBe(true)
  })

  test('returns false for a file', async () => {
    const path = join(root, 'is-file-not-dir.txt')
    await writeFile(path, 'content', 'utf-8')
    expect(dirExists(path)).toBe(false)
  })

  test('returns false for non-existent path', () => {
    expect(dirExists(join(root, 'nope-dir'))).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// listDirectory
// ---------------------------------------------------------------------------

describe('listDirectory', () => {
  test('lists directory entries', async () => {
    const dir = join(root, 'list-dir')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })
    await writeFile(join(dir, 'a.txt'), 'a', 'utf-8')
    await writeFile(join(dir, 'b.txt'), 'b', 'utf-8')
    await mkdir(join(dir, 'sub'))

    const result = await listDirectory(dir)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const names = result.value.map((e) => e.name).sort()
      expect(names).toContain('a.txt')
      expect(names).toContain('b.txt')
      expect(names).toContain('sub')
    }
  })

  test('returns error for non-existent directory', async () => {
    const result = await listDirectory(join(root, 'no-such-dir'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_DIR')
    }
  })

  test('lists entries recursively', async () => {
    const dir = join(root, 'list-recursive')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(join(dir, 'child'), { recursive: true })
    await writeFile(join(dir, 'top.txt'), 'top', 'utf-8')
    await writeFile(join(dir, 'child', 'bottom.txt'), 'bottom', 'utf-8')

    const result = await listDirectory(dir, { recursive: true })
    expect(result.ok).toBe(true)
    if (result.ok) {
      const names = result.value.map((e) => e.name)
      expect(names).toContain('top.txt')
      expect(names).toContain('bottom.txt')
    }
  })
})
