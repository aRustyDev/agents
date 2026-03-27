import { describe, expect, test } from 'bun:test'
import { readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { build } from '../src/build'

const WORKTREE = resolve(import.meta.dir, '../../..')
const WORKSPACE = resolve(WORKTREE, 'content/skills/search-term-matrices-workspace')
const SKILL_PATH = resolve(WORKTREE, 'content/skills/search-term-matrices')

describe('build integration', () => {
  const outputPath = join(tmpdir(), 'matrixng-integration-test.html')

  test('builds a complete HTML file from real workspace data', async () => {
    await build({
      workspace: WORKSPACE,
      skillPath: SKILL_PATH,
      output: outputPath,
      iteration: 1,
      open: false,
    })

    const html = await readFile(outputPath, 'utf-8')

    // Basic structure
    expect(html).toContain('<!DOCTYPE html>')
    expect(html).toContain('window.__VIEWER_DATA__')

    // Data was injected
    expect(html).toContain('search-term-matrices')
    expect(html).toContain('offline-sync')
    expect(html).toContain('llm-regulatory')
    expect(html).toContain('webtransport')

    // All JS modules present
    expect(html).toContain('MatrixViewer')
    expect(html).toContain('renderMarkdown')
    expect(html).toContain('initComments')
    expect(html).toContain('renderBenchmark')

    // CSS present
    expect(html).toContain('<style>')

    // Benchmark data
    expect(html).toContain('pass_rate')
    expect(html).toContain('with_skill')
    expect(html).toContain('without_skill')

    // Clean up
    await rm(outputPath, { force: true })
  })

  test('auto-detects skill path from workspace sibling', async () => {
    const out = join(tmpdir(), 'matrixng-autodetect-test.html')
    await build({
      workspace: WORKSPACE,
      output: out,
      iteration: 1,
      open: false,
    })

    const html = await readFile(out, 'utf-8')
    expect(html).toContain('window.__VIEWER_DATA__')
    await rm(out, { force: true })
  })
})
