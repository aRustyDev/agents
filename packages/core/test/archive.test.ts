import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { listZip, unzip, zipDirectory, zipFiles } from '@agents/core/archive'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'archive-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// zipDirectory
// ---------------------------------------------------------------------------

describe('zipDirectory', () => {
  test('creates a zip from a temp dir with files', async () => {
    const srcDir = join(tmp, 'source')
    await mkdir(srcDir, { recursive: true })
    await writeFile(join(srcDir, 'hello.txt'), 'hello world')
    await writeFile(join(srcDir, 'readme.md'), '# README')

    const zipPath = join(tmp, 'output.zip')
    const result = await zipDirectory(srcDir, zipPath)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.path).toBe(zipPath)
    expect(result.value.fileCount).toBe(2)
    expect(existsSync(zipPath)).toBe(true)
  })

  test('excludes patterns', async () => {
    const srcDir = join(tmp, 'source-excl')
    await mkdir(join(srcDir, '.git'), { recursive: true })
    await writeFile(join(srcDir, 'code.ts'), 'export default 42')
    await writeFile(join(srcDir, '.git', 'HEAD'), 'ref: refs/heads/main')
    await writeFile(join(srcDir, '.DS_Store'), 'junk')

    const zipPath = join(tmp, 'excluded.zip')
    const result = await zipDirectory(srcDir, zipPath, {
      exclude: ['.git/*', '.DS_Store'],
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    // The zip should only contain code.ts
    const listing = await listZip(zipPath)
    expect(listing.ok).toBe(true)
    if (!listing.ok) return
    expect(listing.value).toEqual(['code.ts'])
  })

  test('handles nested directories', async () => {
    const srcDir = join(tmp, 'nested')
    await mkdir(join(srcDir, 'sub', 'deep'), { recursive: true })
    await writeFile(join(srcDir, 'root.txt'), 'root')
    await writeFile(join(srcDir, 'sub', 'mid.txt'), 'mid')
    await writeFile(join(srcDir, 'sub', 'deep', 'leaf.txt'), 'leaf')

    const zipPath = join(tmp, 'nested.zip')
    const result = await zipDirectory(srcDir, zipPath)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.fileCount).toBe(3)
  })

  test('creates parent directories for output path', async () => {
    const srcDir = join(tmp, 'src-mkdir')
    await mkdir(srcDir, { recursive: true })
    await writeFile(join(srcDir, 'file.txt'), 'data')

    const zipPath = join(tmp, 'deep', 'nested', 'output.zip')
    const result = await zipDirectory(srcDir, zipPath)

    expect(result.ok).toBe(true)
    expect(existsSync(zipPath)).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// zipFiles
// ---------------------------------------------------------------------------

describe('zipFiles', () => {
  test('creates from explicit entries', async () => {
    const zipPath = join(tmp, 'from-entries.zip')
    const result = await zipFiles(
      [
        { path: 'SKILL.md', content: '# My Skill' },
        { path: 'lib/helper.ts', content: 'export const x = 1' },
      ],
      zipPath
    )

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.path).toBe(zipPath)
    expect(result.value.fileCount).toBe(2)
    expect(existsSync(zipPath)).toBe(true)
  })

  test('creates zip with Buffer content', async () => {
    const zipPath = join(tmp, 'buffer-entries.zip')
    const result = await zipFiles(
      [{ path: 'binary.bin', content: Buffer.from([0x00, 0xff, 0x80]) }],
      zipPath
    )

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.fileCount).toBe(1)
  })
})

// ---------------------------------------------------------------------------
// unzip
// ---------------------------------------------------------------------------

describe('unzip', () => {
  test('extracts files to target dir', async () => {
    // Create a zip first
    const srcDir = join(tmp, 'src-unzip')
    await mkdir(srcDir, { recursive: true })
    await writeFile(join(srcDir, 'a.txt'), 'alpha')
    await writeFile(join(srcDir, 'b.txt'), 'beta')

    const zipPath = join(tmp, 'to-extract.zip')
    await zipDirectory(srcDir, zipPath)

    // Extract
    const outDir = join(tmp, 'extracted')
    const result = await unzip(zipPath, outDir)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value).toContain('a.txt')
    expect(result.value).toContain('b.txt')
    expect(existsSync(join(outDir, 'a.txt'))).toBe(true)
    expect(existsSync(join(outDir, 'b.txt'))).toBe(true)
  })

  test('creates output directory if it does not exist', async () => {
    const srcDir = join(tmp, 'src-mkdir-unzip')
    await mkdir(srcDir, { recursive: true })
    await writeFile(join(srcDir, 'file.txt'), 'data')

    const zipPath = join(tmp, 'mkdir-test.zip')
    await zipDirectory(srcDir, zipPath)

    const outDir = join(tmp, 'new', 'deep', 'dir')
    const result = await unzip(zipPath, outDir)

    expect(result.ok).toBe(true)
    expect(existsSync(join(outDir, 'file.txt'))).toBe(true)
  })

  test('returns error for non-existent zip', async () => {
    const result = await unzip(join(tmp, 'nope.zip'), join(tmp, 'out'))

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_ARCHIVE')
  })
})

// ---------------------------------------------------------------------------
// listZip
// ---------------------------------------------------------------------------

describe('listZip', () => {
  test('returns file paths without extracting', async () => {
    const srcDir = join(tmp, 'src-list')
    await mkdir(join(srcDir, 'sub'), { recursive: true })
    await writeFile(join(srcDir, 'root.txt'), 'root')
    await writeFile(join(srcDir, 'sub', 'child.txt'), 'child')

    const zipPath = join(tmp, 'list-test.zip')
    await zipDirectory(srcDir, zipPath)

    const result = await listZip(zipPath)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value).toContain('root.txt')
    expect(result.value).toContain('sub/child.txt')
  })

  test('returns error for non-existent zip', async () => {
    const result = await listZip(join(tmp, 'missing.zip'))

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_ARCHIVE')
  })
})

// ---------------------------------------------------------------------------
// Round-trip
// ---------------------------------------------------------------------------

describe('round-trip', () => {
  test('zip then unzip preserves content', async () => {
    const srcDir = join(tmp, 'roundtrip-src')
    await mkdir(join(srcDir, 'sub'), { recursive: true })
    await writeFile(join(srcDir, 'hello.txt'), 'hello world')
    await writeFile(join(srcDir, 'sub', 'nested.md'), '# Nested\n\nContent here.')

    const zipPath = join(tmp, 'roundtrip.zip')
    const zipResult = await zipDirectory(srcDir, zipPath)
    expect(zipResult.ok).toBe(true)

    const outDir = join(tmp, 'roundtrip-out')
    const unzipResult = await unzip(zipPath, outDir)
    expect(unzipResult.ok).toBe(true)

    // Verify content is preserved
    const hello = await readFile(join(outDir, 'hello.txt'), 'utf-8')
    expect(hello).toBe('hello world')

    const nested = await readFile(join(outDir, 'sub', 'nested.md'), 'utf-8')
    expect(nested).toBe('# Nested\n\nContent here.')
  })

  test('zipFiles then unzip preserves content', async () => {
    const zipPath = join(tmp, 'files-roundtrip.zip')
    const zipResult = await zipFiles(
      [
        { path: 'SKILL.md', content: '# Test Skill\nDescription here.' },
        { path: 'examples/demo.ts', content: 'console.log("demo")' },
      ],
      zipPath
    )
    expect(zipResult.ok).toBe(true)

    const outDir = join(tmp, 'files-roundtrip-out')
    const unzipResult = await unzip(zipPath, outDir)
    expect(unzipResult.ok).toBe(true)

    const skill = await readFile(join(outDir, 'SKILL.md'), 'utf-8')
    expect(skill).toBe('# Test Skill\nDescription here.')

    const demo = await readFile(join(outDir, 'examples', 'demo.ts'), 'utf-8')
    expect(demo).toBe('console.log("demo")')
  })
})
