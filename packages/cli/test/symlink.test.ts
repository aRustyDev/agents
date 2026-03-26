import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { lstat, mkdir, mkdtemp, readlink, realpath, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { auditSymlinks, checkSymlink, createSymlink, resolveChain } from '@agents/core/symlink'

// ---------------------------------------------------------------------------
// Shared fixture directory
// ---------------------------------------------------------------------------

let root: string

beforeAll(async () => {
  root = await realpath(await mkdtemp(join(tmpdir(), 'symlink-test-')))

  // Real files
  await writeFile(join(root, 'real-file.txt'), 'hello')
  await mkdir(join(root, 'real-dir'))
  await writeFile(join(root, 'real-dir', 'nested.txt'), 'nested')

  // Healthy symlink -> real file
  await symlink(join(root, 'real-file.txt'), join(root, 'healthy-link'))

  // Broken symlink -> non-existent target
  await symlink(join(root, 'does-not-exist'), join(root, 'broken-link'))

  // Chained symlinks: chain-a -> chain-b -> real-file.txt
  await symlink(join(root, 'real-file.txt'), join(root, 'chain-b'))
  await symlink(join(root, 'chain-b'), join(root, 'chain-a'))

  // Directory symlink -> real-dir
  await symlink(join(root, 'real-dir'), join(root, 'dir-link'))

  // Nested structure for audit
  await mkdir(join(root, 'sub'))
  await writeFile(join(root, 'sub', 'file.txt'), 'sub-file')
  await symlink(join(root, 'sub', 'file.txt'), join(root, 'sub', 'good-link'))
  await symlink(join(root, 'sub', 'gone'), join(root, 'sub', 'bad-link'))
})

afterAll(async () => {
  await rm(root, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// checkSymlink
// ---------------------------------------------------------------------------

describe('checkSymlink', () => {
  test('healthy symlink returns valid=true, broken=false', async () => {
    const status = await checkSymlink(join(root, 'healthy-link'))
    expect(status.valid).toBe(true)
    expect(status.broken).toBe(false)
    expect(status.path).toBe(join(root, 'healthy-link'))
    expect(status.target).toBe(join(root, 'real-file.txt'))
  })

  test('broken symlink returns valid=false, broken=true', async () => {
    const status = await checkSymlink(join(root, 'broken-link'))
    expect(status.valid).toBe(false)
    expect(status.broken).toBe(true)
    expect(status.target).toBe(join(root, 'does-not-exist'))
  })

  test('directory symlink is valid', async () => {
    const status = await checkSymlink(join(root, 'dir-link'))
    expect(status.valid).toBe(true)
    expect(status.broken).toBe(false)
  })

  test('throws for a regular file (not a symlink)', async () => {
    expect(checkSymlink(join(root, 'real-file.txt'))).rejects.toThrow('Not a symlink')
  })

  test('throws for a non-existent path', async () => {
    expect(checkSymlink(join(root, 'no-such-path'))).rejects.toThrow()
  })
})

// ---------------------------------------------------------------------------
// createSymlink
// ---------------------------------------------------------------------------

describe('createSymlink', () => {
  test('creates a new symlink', async () => {
    const link = join(root, 'new-link')
    const target = join(root, 'real-file.txt')
    await createSymlink(target, link)

    const stats = await lstat(link)
    expect(stats.isSymbolicLink()).toBe(true)

    const resolved = await readlink(link)
    expect(resolved).toBe(target)
  })

  test('overwrites an existing symlink', async () => {
    const link = join(root, 'overwrite-link')

    // Create initial symlink
    await symlink(join(root, 'real-file.txt'), link)

    // Overwrite with a different target
    const newTarget = join(root, 'real-dir')
    await createSymlink(newTarget, link)

    const resolved = await readlink(link)
    expect(resolved).toBe(newTarget)
  })

  test('creates parent directories if missing', async () => {
    const link = join(root, 'deep', 'nested', 'dir', 'link')
    const target = join(root, 'real-file.txt')
    await createSymlink(target, link)

    const stats = await lstat(link)
    expect(stats.isSymbolicLink()).toBe(true)
  })

  test('throws when path exists and is not a symlink', async () => {
    expect(createSymlink(join(root, 'real-dir'), join(root, 'real-file.txt'))).rejects.toThrow(
      'Path exists and is not a symlink'
    )
  })
})

// ---------------------------------------------------------------------------
// resolveChain
// ---------------------------------------------------------------------------

describe('resolveChain', () => {
  test('returns full chain for chained symlinks', async () => {
    const chain = await resolveChain(join(root, 'chain-a'))

    // chain-a -> chain-b -> real-file.txt
    expect(chain.length).toBeGreaterThanOrEqual(3)
    expect(chain[0]).toBe(join(root, 'chain-a'))
    expect(chain[1]).toBe(join(root, 'chain-b'))
    expect(chain[chain.length - 1]).toBe(join(root, 'real-file.txt'))
  })

  test('returns [path, target] for a simple symlink', async () => {
    const chain = await resolveChain(join(root, 'healthy-link'))

    expect(chain[0]).toBe(join(root, 'healthy-link'))
    expect(chain[chain.length - 1]).toBe(join(root, 'real-file.txt'))
  })

  test('returns [path] for a regular file', async () => {
    const chain = await resolveChain(join(root, 'real-file.txt'))
    expect(chain).toEqual([join(root, 'real-file.txt')])
  })

  test('handles broken chain gracefully', async () => {
    const chain = await resolveChain(join(root, 'broken-link'))

    expect(chain[0]).toBe(join(root, 'broken-link'))
    // Should include the broken target in the chain
    expect(chain.length).toBeGreaterThanOrEqual(2)
  })
})

// ---------------------------------------------------------------------------
// auditSymlinks
// ---------------------------------------------------------------------------

describe('auditSymlinks', () => {
  test('finds both healthy and broken symlinks', async () => {
    const report = await auditSymlinks(root)

    // At least the ones we created in beforeAll
    expect(report.healthy.length).toBeGreaterThanOrEqual(1)
    expect(report.broken.length).toBeGreaterThanOrEqual(1)

    const healthyPaths = report.healthy.map((s) => s.path)
    const brokenPaths = report.broken.map((s) => s.path)

    expect(healthyPaths).toContain(join(root, 'healthy-link'))
    expect(brokenPaths).toContain(join(root, 'broken-link'))
  })

  test('recursive scan finds symlinks in subdirectories', async () => {
    const report = await auditSymlinks(root, { recursive: true })

    const allPaths = [...report.healthy, ...report.broken].map((s) => s.path)
    expect(allPaths).toContain(join(root, 'sub', 'good-link'))
    expect(allPaths).toContain(join(root, 'sub', 'bad-link'))
  })

  test('non-recursive scan skips subdirectories', async () => {
    const report = await auditSymlinks(root, { recursive: false })

    const allPaths = [...report.healthy, ...report.broken].map((s) => s.path)
    expect(allPaths).not.toContain(join(root, 'sub', 'good-link'))
    expect(allPaths).not.toContain(join(root, 'sub', 'bad-link'))
  })

  test('healthy symlinks have valid=true, broken=false', async () => {
    const report = await auditSymlinks(root)
    for (const status of report.healthy) {
      expect(status.valid).toBe(true)
      expect(status.broken).toBe(false)
    }
  })

  test('broken symlinks have valid=false, broken=true', async () => {
    const report = await auditSymlinks(root)
    for (const status of report.broken) {
      expect(status.valid).toBe(false)
      expect(status.broken).toBe(true)
    }
  })

  test('returns empty report for directory with no symlinks', async () => {
    const emptyDir = await mkdtemp(join(tmpdir(), 'symlink-empty-'))
    await writeFile(join(emptyDir, 'plain.txt'), 'no links here')

    const report = await auditSymlinks(emptyDir)
    expect(report.healthy).toEqual([])
    expect(report.broken).toEqual([])

    await rm(emptyDir, { recursive: true, force: true })
  })
})
