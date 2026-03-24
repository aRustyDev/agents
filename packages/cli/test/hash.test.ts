import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  computeHash,
  formatHash,
  hashDirectory,
  hashFile,
  parseHash,
  verifyHash,
} from '../src/lib/hash'

const HEX64_REGEX = /^[0-9a-f]{64}$/

// Temp directory created fresh before each test group.
let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'hash-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// hashFile
// ---------------------------------------------------------------------------

describe('hashFile', () => {
  test('returns a 64-character lowercase hex string', async () => {
    const p = join(tmp, 'hello.txt')
    await writeFile(p, 'hello world\n')
    const hash = await hashFile(p)
    expect(hash).toMatch(HEX64_REGEX)
  })

  test('is deterministic (same content = same hash)', async () => {
    const p1 = join(tmp, 'a.txt')
    const p2 = join(tmp, 'b.txt')
    const content = 'deterministic content'
    await writeFile(p1, content)
    await writeFile(p2, content)

    const h1 = await hashFile(p1)
    const h2 = await hashFile(p2)
    expect(h1).toBe(h2)
  })

  test('different content produces different hashes', async () => {
    const p1 = join(tmp, 'x.txt')
    const p2 = join(tmp, 'y.txt')
    await writeFile(p1, 'alpha')
    await writeFile(p2, 'beta')

    const h1 = await hashFile(p1)
    const h2 = await hashFile(p2)
    expect(h1).not.toBe(h2)
  })

  test('handles empty files', async () => {
    const p = join(tmp, 'empty.txt')
    await writeFile(p, '')
    const hash = await hashFile(p)
    expect(hash).toMatch(HEX64_REGEX)
    // SHA256 of empty input is well-known
    expect(hash).toBe('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
  })

  test('handles binary content', async () => {
    const p = join(tmp, 'binary.bin')
    const buf = new Uint8Array([0x00, 0xff, 0x80, 0x7f, 0x01])
    await writeFile(p, buf)
    const hash = await hashFile(p)
    expect(hash).toMatch(HEX64_REGEX)
  })
})

// ---------------------------------------------------------------------------
// hashDirectory
// ---------------------------------------------------------------------------

describe('hashDirectory', () => {
  test('returns a 64-character lowercase hex string', async () => {
    await writeFile(join(tmp, 'file.txt'), 'content')
    const hash = await hashDirectory(tmp)
    expect(hash).toMatch(HEX64_REGEX)
  })

  test('is deterministic (same structure = same hash)', async () => {
    const d1 = join(tmp, 'd1')
    const d2 = join(tmp, 'd2')
    await mkdir(d1)
    await mkdir(d2)
    await writeFile(join(d1, 'a.txt'), 'alpha')
    await writeFile(join(d1, 'b.txt'), 'beta')
    await writeFile(join(d2, 'a.txt'), 'alpha')
    await writeFile(join(d2, 'b.txt'), 'beta')

    const h1 = await hashDirectory(d1)
    const h2 = await hashDirectory(d2)
    expect(h1).toBe(h2)
  })

  test('adding a file changes the hash', async () => {
    await writeFile(join(tmp, 'a.txt'), 'alpha')
    const before = await hashDirectory(tmp)

    await writeFile(join(tmp, 'b.txt'), 'beta')
    const after = await hashDirectory(tmp)

    expect(before).not.toBe(after)
  })

  test('changing file content changes the hash', async () => {
    await writeFile(join(tmp, 'data.txt'), 'version-1')
    const h1 = await hashDirectory(tmp)

    await writeFile(join(tmp, 'data.txt'), 'version-2')
    const h2 = await hashDirectory(tmp)

    expect(h1).not.toBe(h2)
  })

  test('renaming a file changes the hash (path is part of hash)', async () => {
    const dir = join(tmp, 'rename-test')
    await mkdir(dir)
    await writeFile(join(dir, 'old-name.txt'), 'same content')
    const h1 = await hashDirectory(dir)

    // Recreate with different filename but same content
    await rm(dir, { recursive: true })
    await mkdir(dir)
    await writeFile(join(dir, 'new-name.txt'), 'same content')
    const h2 = await hashDirectory(dir)

    expect(h1).not.toBe(h2)
  })

  test('file ordering does not matter (sorted internally)', async () => {
    // Create files in reverse alphabetical order
    const dir1 = join(tmp, 'order1')
    await mkdir(dir1)
    await writeFile(join(dir1, 'z.txt'), 'last')
    await writeFile(join(dir1, 'a.txt'), 'first')
    await writeFile(join(dir1, 'm.txt'), 'middle')

    // Create files in forward alphabetical order
    const dir2 = join(tmp, 'order2')
    await mkdir(dir2)
    await writeFile(join(dir2, 'a.txt'), 'first')
    await writeFile(join(dir2, 'm.txt'), 'middle')
    await writeFile(join(dir2, 'z.txt'), 'last')

    const h1 = await hashDirectory(dir1)
    const h2 = await hashDirectory(dir2)
    expect(h1).toBe(h2)
  })

  test('handles nested subdirectories', async () => {
    const sub = join(tmp, 'sub')
    const deep = join(sub, 'deep')
    await mkdir(sub)
    await mkdir(deep)
    await writeFile(join(tmp, 'root.txt'), 'root')
    await writeFile(join(sub, 'mid.txt'), 'mid')
    await writeFile(join(deep, 'leaf.txt'), 'leaf')

    const hash = await hashDirectory(tmp)
    expect(hash).toMatch(HEX64_REGEX)
  })

  test('skips .git directories', async () => {
    await writeFile(join(tmp, 'code.ts'), 'export default 42')

    const h1 = await hashDirectory(tmp)

    // Adding a .git directory should not change the hash
    const gitDir = join(tmp, '.git')
    await mkdir(gitDir)
    await writeFile(join(gitDir, 'HEAD'), 'ref: refs/heads/main')

    const h2 = await hashDirectory(tmp)
    expect(h1).toBe(h2)
  })

  test('skips node_modules directories', async () => {
    await writeFile(join(tmp, 'index.ts'), 'console.log("hi")')
    const h1 = await hashDirectory(tmp)

    const nm = join(tmp, 'node_modules')
    await mkdir(nm)
    await writeFile(join(nm, 'package.json'), '{}')

    const h2 = await hashDirectory(tmp)
    expect(h1).toBe(h2)
  })

  test('skips __pycache__ directories', async () => {
    await writeFile(join(tmp, 'main.py'), 'print("hi")')
    const h1 = await hashDirectory(tmp)

    const cache = join(tmp, '__pycache__')
    await mkdir(cache)
    await writeFile(join(cache, 'main.cpython-311.pyc'), '\x00\x00')

    const h2 = await hashDirectory(tmp)
    expect(h1).toBe(h2)
  })

  test('handles empty directory', async () => {
    const emptyDir = join(tmp, 'empty')
    await mkdir(emptyDir)
    const hash = await hashDirectory(emptyDir)
    // SHA256 of empty input (no files = nothing fed to hasher)
    expect(hash).toBe('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
  })
})

// ---------------------------------------------------------------------------
// computeHash
// ---------------------------------------------------------------------------

describe('computeHash', () => {
  test('auto-detects a file', async () => {
    const p = join(tmp, 'file.txt')
    await writeFile(p, 'test content')

    const fromCompute = await computeHash(p)
    const fromDirect = await hashFile(p)
    expect(fromCompute).toBe(fromDirect)
  })

  test('auto-detects a directory', async () => {
    const dir = join(tmp, 'dir')
    await mkdir(dir)
    await writeFile(join(dir, 'f.txt'), 'data')

    const fromCompute = await computeHash(dir)
    const fromDirect = await hashDirectory(dir)
    expect(fromCompute).toBe(fromDirect)
  })

  test('throws for non-existent path', async () => {
    const bogus = join(tmp, 'does-not-exist')
    expect(computeHash(bogus)).rejects.toThrow()
  })
})

// ---------------------------------------------------------------------------
// formatHash / parseHash
// ---------------------------------------------------------------------------

describe('formatHash', () => {
  test('prepends sha256: prefix', () => {
    const hex = 'abcdef0123456789'
    expect(formatHash(hex)).toBe('sha256:abcdef0123456789')
  })
})

describe('parseHash', () => {
  test('strips sha256: prefix', () => {
    expect(parseHash('sha256:abc123')).toBe('abc123')
  })

  test('returns raw hex unchanged', () => {
    expect(parseHash('abc123')).toBe('abc123')
  })

  test('round-trips with formatHash', () => {
    const hex = 'deadbeef'
    expect(parseHash(formatHash(hex))).toBe(hex)
  })

  test('is idempotent on raw hex', () => {
    const raw = 'cafe0000'
    expect(parseHash(parseHash(raw))).toBe(raw)
  })
})

// ---------------------------------------------------------------------------
// verifyHash
// ---------------------------------------------------------------------------

describe('verifyHash', () => {
  test('returns true when hash matches', async () => {
    const p = join(tmp, 'verify.txt')
    await writeFile(p, 'verify me')

    const hash = await hashFile(p)
    expect(await verifyHash(p, hash)).toBe(true)
  })

  test('returns true when hash matches with prefix', async () => {
    const p = join(tmp, 'verify2.txt')
    await writeFile(p, 'verify me too')

    const hash = await hashFile(p)
    expect(await verifyHash(p, formatHash(hash))).toBe(true)
  })

  test('returns false when hash does not match', async () => {
    const p = join(tmp, 'mismatch.txt')
    await writeFile(p, 'actual content')

    expect(await verifyHash(p, 'aaaa'.repeat(16))).toBe(false)
  })

  test('works with directories', async () => {
    const dir = join(tmp, 'verify-dir')
    await mkdir(dir)
    await writeFile(join(dir, 'f.txt'), 'data')

    const hash = await hashDirectory(dir)
    expect(await verifyHash(dir, hash)).toBe(true)
    expect(await verifyHash(dir, 'wrong')).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// Real file smoke test
// ---------------------------------------------------------------------------

describe('real file integration', () => {
  const realFile = join(import.meta.dir, '..', 'package.json')

  test('hashes a real file from the repo to a valid 64-char hex string', async () => {
    const hash = await hashFile(realFile)
    expect(hash).toMatch(HEX64_REGEX)
    expect(hash.length).toBe(64)
  })
})
