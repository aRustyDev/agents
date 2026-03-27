import { access, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import type { ViewerData } from './types'

/** Ordered list of JS files to inline. Order matters -- dependencies first. */
const JS_LOAD_ORDER = [
  'markdown.js',
  'matrix-parser.js',
  'core.js',
  'comments.js',
  'benchmark.js',
  'ribbon.js',
]

const OVERLAY_FILES = [
  'overlays/structural.js',
  'overlays/operators.js',
  'overlays/progression.js',
  'overlays/decomposition.js',
]

/**
 * Assemble a standalone HTML file from template parts and viewer data.
 */
export async function assembleHtml(
  skillPath: string,
  data: ViewerData,
  outputPath: string
): Promise<void> {
  const shell = await readFile(join(skillPath, 'assets', 'viewer', 'shell.html'), 'utf-8')
  const styles = await readFile(join(skillPath, 'assets', 'viewer', 'styles.css'), 'utf-8')

  const scriptsDir = join(skillPath, 'scripts', 'viewer')
  const jsContents: string[] = []
  for (const filename of JS_LOAD_ORDER) {
    const content = await readFile(join(scriptsDir, filename), 'utf-8')
    jsContents.push(`/* === ${filename} === */\n${content}`)
  }

  // Load overlay files (skip missing — they're added incrementally)
  for (const filename of OVERLAY_FILES) {
    try {
      await access(join(scriptsDir, filename))
      const content = await readFile(join(scriptsDir, filename), 'utf-8')
      jsContents.push(`/* === ${filename} === */\n${content}`)
    } catch {
      // File doesn't exist yet — skip silently
    }
  }

  const dataScript = `<script>\nwindow.__VIEWER_DATA__ = ${JSON.stringify(data, null, 2)};\n</script>`
  const appScripts = jsContents.map((js) => `<script>\n${js}\n</script>`).join('\n')

  let html = shell
  html = html.replace('<!--STYLES-->', `<style>\n${styles}\n</style>`)
  html = html.replace('<!--SCRIPTS-->', `${dataScript}\n${appScripts}`)

  await mkdir(dirname(outputPath), { recursive: true })
  await writeFile(outputPath, html, 'utf-8')
}
