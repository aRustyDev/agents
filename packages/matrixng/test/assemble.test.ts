import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { assembleHtml } from '../src/assemble'
import type { ViewerData } from '../src/types'

let tmpDir: string

beforeEach(async () => {
  tmpDir = await mkdtemp(join(tmpdir(), 'matrixng-test-'))
})

afterEach(async () => {
  await rm(tmpDir, { recursive: true, force: true })
})

const MINIMAL_VIEWER_DATA: ViewerData = {
  skillName: 'test-skill',
  iteration: 1,
  generatedAt: '2026-03-26T00:00:00Z',
  evals: [],
  benchmark: { configurations: [], delta: {}, analysis: { observations: [] } },
  engineOperators: {},
}

describe('assembleHtml', () => {
  test('produces a valid HTML file with injected data', async () => {
    const assetsDir = join(tmpDir, 'assets', 'viewer')
    const scriptsDir = join(tmpDir, 'scripts', 'viewer')
    await mkdir(assetsDir, { recursive: true })
    await mkdir(scriptsDir, { recursive: true })

    await writeFile(
      join(assetsDir, 'shell.html'),
      `<!DOCTYPE html>
<html><head><!--STYLES--></head><body><!--SCRIPTS--></body></html>`
    )
    await writeFile(join(assetsDir, 'styles.css'), 'body { margin: 0; }')
    await writeFile(join(scriptsDir, 'markdown.js'), '// markdown')
    await writeFile(join(scriptsDir, 'matrix-parser.js'), '// parser')
    await writeFile(join(scriptsDir, 'core.js'), '// core')
    await writeFile(join(scriptsDir, 'comments.js'), '// comments')
    await writeFile(join(scriptsDir, 'benchmark.js'), '// benchmark')

    const outputPath = join(tmpDir, 'output.html')
    await assembleHtml(tmpDir, MINIMAL_VIEWER_DATA, outputPath)

    const html = await readFile(outputPath, 'utf-8')
    expect(html).toContain('<!DOCTYPE html>')
    expect(html).toContain('body { margin: 0; }')
    expect(html).toContain('window.__VIEWER_DATA__')
    expect(html).toContain('"test-skill"')
    expect(html).toContain('// markdown')
    expect(html).toContain('// core')
    expect(html).toContain('// comments')
    expect(html).toContain('// benchmark')
  })

  test('inlines JS files in correct order', async () => {
    const assetsDir = join(tmpDir, 'assets', 'viewer')
    const scriptsDir = join(tmpDir, 'scripts', 'viewer')
    await mkdir(assetsDir, { recursive: true })
    await mkdir(scriptsDir, { recursive: true })

    await writeFile(
      join(assetsDir, 'shell.html'),
      '<html><head><!--STYLES--></head><body><!--SCRIPTS--></body></html>'
    )
    await writeFile(join(assetsDir, 'styles.css'), '')
    await writeFile(join(scriptsDir, 'markdown.js'), '/* 1-markdown */')
    await writeFile(join(scriptsDir, 'matrix-parser.js'), '/* 2-parser */')
    await writeFile(join(scriptsDir, 'core.js'), '/* 3-core */')
    await writeFile(join(scriptsDir, 'comments.js'), '/* 4-comments */')
    await writeFile(join(scriptsDir, 'benchmark.js'), '/* 5-benchmark */')

    const outputPath = join(tmpDir, 'output.html')
    await assembleHtml(tmpDir, MINIMAL_VIEWER_DATA, outputPath)

    const html = await readFile(outputPath, 'utf-8')
    const idx1 = html.indexOf('1-markdown')
    const idx2 = html.indexOf('2-parser')
    const idx3 = html.indexOf('3-core')
    const idx4 = html.indexOf('4-comments')
    const idx5 = html.indexOf('5-benchmark')
    const idxData = html.indexOf('__VIEWER_DATA__')

    // Data injected before scripts
    expect(idxData).toBeLessThan(idx1)
    // Scripts in order
    expect(idx1).toBeLessThan(idx2)
    expect(idx2).toBeLessThan(idx3)
    expect(idx3).toBeLessThan(idx4)
    expect(idx4).toBeLessThan(idx5)
  })
})
