/**
 * Verb-first command: agents doctor
 *
 * Checks the health of the development environment, CLI installation,
 * and component integrity. Reports runtime availability, project structure,
 * config validity, and installed component counts.
 */

import { execSync } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { defineCommand } from 'citty'
import { getProjectConfigPath, getUserConfigPath, readConfigFile } from '../lib/config'
import { createOutput } from '../lib/output'
import { currentDir } from '../lib/runtime'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CheckResult {
  category: string
  check: string
  status: 'ok' | 'warn' | 'error'
  detail: string
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Lazily computed project root to avoid import.meta resolution in tests. */
function getProjectRoot(): string {
  return resolve(currentDir(import.meta), '../../../..')
}

/** Run a shell command and return trimmed stdout, or null on failure. */
function whichCmd(cmd: string): string | null {
  try {
    return execSync(`which ${cmd}`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim()
  } catch {
    return null
  }
}

/** Get version from a command, or null on failure. */
function cmdVersion(cmd: string, args: string): string | null {
  try {
    return execSync(`${cmd} ${args}`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
    }).trim()
  } catch {
    return null
  }
}

/** Count subdirectories in a directory (each subdir = one component). */
function countSubdirs(dir: string): number {
  try {
    if (!existsSync(dir)) return 0
    return readdirSync(dir, { withFileTypes: true }).filter((d) => d.isDirectory()).length
  } catch {
    return 0
  }
}

/** Count files in a directory (each file = one component). */
function countFiles(dir: string): number {
  try {
    if (!existsSync(dir)) return 0
    return readdirSync(dir, { withFileTypes: true }).filter((d) => d.isFile()).length
  } catch {
    return 0
  }
}

// ---------------------------------------------------------------------------
// Check runners
// ---------------------------------------------------------------------------

function runRuntimeChecks(): CheckResult[] {
  const results: CheckResult[] = []

  // Bun version
  const bunGlobal = globalThis.Bun as { version?: string } | undefined
  const bunVersion = bunGlobal?.version ?? null
  if (bunVersion) {
    results.push({ category: 'Runtime', check: 'Bun', status: 'ok', detail: `v${bunVersion}` })
  } else {
    results.push({
      category: 'Runtime',
      check: 'Bun',
      status: 'error',
      detail: 'Bun runtime not detected',
    })
  }

  // Node.js
  const nodePath = whichCmd('node')
  if (nodePath) {
    const nodeVer = cmdVersion('node', '--version')
    results.push({
      category: 'Runtime',
      check: 'Node.js',
      status: 'ok',
      detail: nodeVer ?? 'found',
    })
  } else {
    results.push({
      category: 'Runtime',
      check: 'Node.js',
      status: 'warn',
      detail: 'not found in PATH',
    })
  }

  // Git
  const gitPath = whichCmd('git')
  if (gitPath) {
    const gitVer = cmdVersion('git', '--version')
    const ver = gitVer?.replace('git version ', '') ?? 'found'
    results.push({ category: 'Runtime', check: 'Git', status: 'ok', detail: ver })
  } else {
    results.push({
      category: 'Runtime',
      check: 'Git',
      status: 'error',
      detail: 'not found in PATH',
    })
  }

  return results
}

function runProjectChecks(projectRoot: string): CheckResult[] {
  const results: CheckResult[] = []

  const checks: Array<{ name: string; path: string }> = [
    { name: 'content/ directory', path: join(projectRoot, 'content') },
    { name: 'packages/cli/src/', path: join(projectRoot, 'packages/cli/src') },
    { name: 'package.json', path: join(projectRoot, 'package.json') },
    { name: 'bun.lock', path: join(projectRoot, 'bun.lock') },
  ]

  for (const check of checks) {
    if (existsSync(check.path)) {
      results.push({
        category: 'Project',
        check: check.name,
        status: 'ok',
        detail: 'found',
      })
    } else {
      results.push({
        category: 'Project',
        check: check.name,
        status: 'error',
        detail: 'not found',
      })
    }
  }

  return results
}

async function runConfigChecks(): Promise<CheckResult[]> {
  const results: CheckResult[] = []

  // User config
  const userPath = getUserConfigPath()
  if (!existsSync(userPath)) {
    results.push({
      category: 'Config',
      check: 'User config',
      status: 'ok',
      detail: `${userPath} (not found, using defaults)`,
    })
  } else {
    const userResult = await readConfigFile(userPath)
    if (userResult.ok) {
      results.push({
        category: 'Config',
        check: 'User config',
        status: 'ok',
        detail: `${userPath} (valid)`,
      })
    } else {
      results.push({
        category: 'Config',
        check: 'User config',
        status: 'error',
        detail: `${userPath} (parse error: ${userResult.error.message})`,
      })
    }
  }

  // Project config
  const projectPath = getProjectConfigPath()
  if (!existsSync(projectPath)) {
    results.push({
      category: 'Config',
      check: 'Project config',
      status: 'ok',
      detail: `${projectPath} (not found, using defaults)`,
    })
  } else {
    const projectResult = await readConfigFile(projectPath)
    if (projectResult.ok) {
      results.push({
        category: 'Config',
        check: 'Project config',
        status: 'ok',
        detail: `${projectPath} (valid)`,
      })
    } else {
      results.push({
        category: 'Config',
        check: 'Project config',
        status: 'error',
        detail: `${projectPath} (parse error: ${projectResult.error.message})`,
      })
    }
  }

  return results
}

function runComponentChecks(projectRoot: string): CheckResult[] {
  const results: CheckResult[] = []
  const contentDir = join(projectRoot, 'content')

  const skillCount = countSubdirs(join(contentDir, 'skills'))
  results.push({
    category: 'Components',
    check: 'Skills',
    status: 'ok',
    detail: `${skillCount} installed`,
  })

  const pluginCount = countSubdirs(join(contentDir, 'plugins'))
  results.push({
    category: 'Components',
    check: 'Plugins',
    status: 'ok',
    detail: `${pluginCount} installed`,
  })

  const ruleCount = countFiles(join(contentDir, 'rules'))
  results.push({
    category: 'Components',
    check: 'Rules',
    status: 'ok',
    detail: `${ruleCount} installed`,
  })

  return results
}

// ---------------------------------------------------------------------------
// Exported check runner (for testing)
// ---------------------------------------------------------------------------

export async function runChecks(projectRoot?: string): Promise<CheckResult[]> {
  const root = projectRoot ?? getProjectRoot()
  const results: CheckResult[] = []

  results.push(...runRuntimeChecks())
  results.push(...runProjectChecks(root))
  results.push(...(await runConfigChecks()))
  results.push(...runComponentChecks(root))

  return results
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

function statusIcon(status: CheckResult['status']): string {
  if (status === 'ok') return '\u2713'
  if (status === 'warn') return '\u26A0'
  return '\u2717'
}

function displayResults(results: CheckResult[]): boolean {
  const categories = [...new Set(results.map((r) => r.category))]
  let hasErrors = false

  for (const category of categories) {
    console.log(`\n${category}`)
    for (const r of results.filter((r) => r.category === category)) {
      console.log(`  ${statusIcon(r.status)} ${r.check}: ${r.detail}`)
      if (r.status === 'error') hasErrors = true
    }
  }

  return hasErrors
}

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'doctor', description: 'Check environment health and component integrity' },
  args: {
    ...globalArgs,
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    const results = await runChecks()

    if (args.json) {
      out.raw(results)
      process.exit(EXIT.OK)
    }

    const hasErrors = displayResults(results)

    console.log()
    if (hasErrors) {
      console.log('Some checks failed. See errors above.')
      process.exit(EXIT.FAILURES)
    } else {
      console.log('All checks passed!')
      process.exit(EXIT.OK)
    }
  },
})
