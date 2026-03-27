import { execFile } from 'node:child_process'
import { readdir, stat } from 'node:fs/promises'
import { basename, dirname, join, resolve } from 'node:path'
import { assembleHtml } from './assemble'
import { parseEngineReferences } from './parse-engines'
import { parseWorkspace } from './parse-workspace'
import type { ViewerData } from './types'

export interface BuildOptions {
  workspace: string
  skillPath?: string
  output?: string
  iteration?: number
  open?: boolean
}

export async function build(options: BuildOptions): Promise<string> {
  const workspace = resolve(options.workspace)
  const skillPath = options.skillPath
    ? resolve(options.skillPath)
    : await autoDetectSkillPath(workspace)

  const iteration = options.iteration ?? (await detectLatestIteration(workspace))
  const { evals, benchmark } = await parseWorkspace(workspace, iteration)
  const engineOperators = await parseEngineReferences(skillPath)
  const skillName = detectSkillName(workspace)

  const data: ViewerData = {
    skillName,
    iteration,
    generatedAt: new Date().toISOString(),
    evals,
    benchmark,
    engineOperators,
  }

  const outputPath = options.output ?? `/tmp/matrix-review-${skillName}.html`
  await assembleHtml(skillPath, data, outputPath)

  if (options.open !== false) {
    const cmd = process.platform === 'darwin' ? 'open' : 'xdg-open'
    execFile(cmd, [outputPath])
  }

  return outputPath
}

async function autoDetectSkillPath(workspace: string): Promise<string> {
  const parent = dirname(workspace)
  const wsName = basename(workspace).replace(/-workspace$/, '')

  const siblings = await readdir(parent, { withFileTypes: true })
  for (const entry of siblings) {
    if (!entry.isDirectory()) continue
    if (entry.name === basename(workspace)) continue
    if (entry.name !== wsName) continue
    const skillMd = join(parent, entry.name, 'SKILL.md')
    try {
      await stat(skillMd)
      return join(parent, entry.name)
    } catch {}
  }

  let dir = parent
  for (let i = 0; i < 10; i++) {
    try {
      await stat(join(dir, '.git'))
      const skillDir = join(dir, 'content', 'skills', wsName)
      const skillMd = join(skillDir, 'SKILL.md')
      try {
        await stat(skillMd)
        return skillDir
      } catch {
        break
      }
    } catch {
      dir = dirname(dir)
    }
  }

  throw new Error(
    `Could not auto-detect skill path for "${wsName}". Use --skill-path to specify it explicitly.`
  )
}

async function detectLatestIteration(workspace: string): Promise<number> {
  const entries = await readdir(workspace)
  const iterations = entries
    .filter((e) => e.match(/^iteration-\d+$/))
    .map((e) => parseInt(e.split('-')[1]))
    .sort((a, b) => b - a)
  return iterations[0] ?? 1
}

function detectSkillName(workspace: string): string {
  const name = basename(workspace)
  return name.replace(/-workspace$/, '')
}
