import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import type { Assertion, Benchmark, EvalCase, GradingResult, ParsedMatrix, RunData } from './types'

export interface WorkspaceData {
  evals: EvalCase[]
  benchmark: Benchmark
}

export async function parseWorkspace(
  workspacePath: string,
  iteration?: number
): Promise<WorkspaceData> {
  const iterDir = await resolveIterationDir(workspacePath, iteration)
  const evalDirs = await findEvalDirs(iterDir)
  const evals = await Promise.all(evalDirs.map((dir) => parseEvalDir(dir)))
  const benchmark = await readJsonFile<Benchmark>(join(iterDir, 'benchmark.json'))

  return { evals, benchmark }
}

async function resolveIterationDir(workspacePath: string, iteration?: number): Promise<string> {
  if (iteration !== undefined) {
    return join(workspacePath, `iteration-${iteration}`)
  }
  const entries = await readdir(workspacePath)
  const iterDirs = entries
    .filter((e) => e.match(/^iteration-\d+$/))
    .sort((a, b) => {
      const numA = parseInt(a.split('-')[1])
      const numB = parseInt(b.split('-')[1])
      return numB - numA
    })
  if (iterDirs.length === 0) throw new Error(`No iteration directories found in ${workspacePath}`)
  return join(workspacePath, iterDirs[0])
}

async function findEvalDirs(iterDir: string): Promise<string[]> {
  const entries = await readdir(iterDir, { withFileTypes: true })
  return entries
    .filter((e) => e.isDirectory() && e.name.startsWith('eval-'))
    .map((e) => join(iterDir, e.name))
    .sort()
}

async function parseEvalDir(evalDir: string): Promise<EvalCase> {
  const metadata = await readJsonFile<{
    eval_id: number
    eval_name: string
    prompt: string
    assertions: Assertion[]
  }>(join(evalDir, 'eval_metadata.json'))

  const withSkill = await parseRunData(join(evalDir, 'with_skill'))
  const withoutSkill = await parseRunData(join(evalDir, 'without_skill'))

  return {
    evalId: metadata.eval_id,
    evalName: metadata.eval_name,
    prompt: metadata.prompt,
    configurations: {
      with_skill: withSkill,
      without_skill: withoutSkill,
    },
    assertions: metadata.assertions,
  }
}

async function parseRunData(runDir: string): Promise<RunData> {
  const outputsDir = join(runDir, 'outputs')
  const outputFiles = await readdir(outputsDir)
  const mdFile = outputFiles.find((f) => f.endsWith('.md'))
  const raw = mdFile ? await readFile(join(outputsDir, mdFile), 'utf-8') : ''

  const grading = await readJsonFile<GradingResult>(join(runDir, 'grading.json'))
  const timing = await readJsonFile<{ total_tokens: number; duration_ms: number }>(
    join(runDir, 'timing.json')
  )

  const parsed: ParsedMatrix = {
    context: null,
    tiers: [],
    runtimeRecovery: [],
    gradingSummary: '',
    decomposition: null,
  }

  return { raw, parsed, grading, timing }
}

async function readJsonFile<T>(path: string): Promise<T> {
  const content = await readFile(path, 'utf-8')
  return JSON.parse(content) as T
}
