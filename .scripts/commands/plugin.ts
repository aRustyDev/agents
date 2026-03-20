/**
 * Plugin build and verification commands.
 *
 * Port of .scripts/build-plugin.py -- implements the same subcommands:
 *   build, check, hash, lint, check-all, build-all, update, update-all
 *
 * Uses the lib modules for hashing, manifest I/O, and output formatting.
 */

import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { defineCommand } from 'citty'
import { computeHash, formatHash, parseHash } from '../lib/hash'
import { createOutput, type OutputFormatter } from '../lib/output'
import { currentDir } from '../lib/runtime'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Project root -- from .scripts/commands/ it is 2 levels up. */
const PROJECT_ROOT = resolve(currentDir(import.meta), '../..')

/** Directory containing all plugins. */
const PLUGINS_DIR = join(PROJECT_ROOT, 'context/plugins')

// ---------------------------------------------------------------------------
// SourceStatus
// ---------------------------------------------------------------------------

export interface SourceStatus {
  localPath: string
  sourcePath: string
  expectedHash: string | null
  actualHash: string | null
  forked: boolean
  forkedAt: string | null
  missing: boolean
  status: 'fresh' | 'stale' | 'missing' | 'forked' | 'no-hash'
  icon: string
}

const STATUS_ICONS: Record<string, string> = {
  fresh: '\u2713',
  stale: '\u26A0',
  missing: '\u2717',
  forked: '\u25CB',
  'no-hash': '?',
}

function deriveStatus(opts: {
  forked: boolean
  missing: boolean
  expectedHash: string | null
  actualHash: string | null
}): 'fresh' | 'stale' | 'missing' | 'forked' | 'no-hash' {
  if (opts.forked) return 'forked'
  if (opts.missing) return 'missing'
  if (opts.expectedHash === null) return 'no-hash'
  if (opts.expectedHash === opts.actualHash) return 'fresh'
  return 'stale'
}

// ---------------------------------------------------------------------------
// BuildResult
// ---------------------------------------------------------------------------

interface BuildResult {
  pluginName: string
  sources: SourceStatus[]
  copied: string[]
  skipped: string[]
  updated: string[]
  errors: string[]
}

function buildResultSuccess(result: BuildResult): boolean {
  return result.errors.length === 0
}

// ---------------------------------------------------------------------------
// Plugin class
// ---------------------------------------------------------------------------

interface SourceDef {
  source: string
  hash?: string
  forked?: boolean
  forked_at?: string
  type?: string
  base?: string
  notes?: string
}

type SourcesMap = Record<string, string | SourceDef>

interface SourcesFile {
  $schema?: string
  sources: SourcesMap
}

class Plugin {
  readonly name: string
  readonly dir: string
  readonly sourcesFile: string

  constructor(name: string) {
    this.name = name
    this.dir = join(PLUGINS_DIR, name)
    this.sourcesFile = join(this.dir, '.claude-plugin', 'plugin.sources.json')
  }

  exists(): boolean {
    return existsSync(this.sourcesFile)
  }

  async loadSources(): Promise<SourcesFile> {
    if (!existsSync(this.sourcesFile)) {
      throw new Error(`Plugin not found: ${this.name}`)
    }
    const raw = await readFile(this.sourcesFile, 'utf-8')
    return JSON.parse(raw) as SourcesFile
  }

  async saveSources(data: SourcesFile): Promise<void> {
    const json = `${JSON.stringify(data, null, 2)}\n`
    await writeFile(this.sourcesFile, json, 'utf-8')
  }

  async getSourceStatus(localPath: string, sourceDef: string | SourceDef): Promise<SourceStatus> {
    let sourcePath: string
    let expectedHash: string | null = null
    let forked = false
    let forkedAt: string | null = null

    if (typeof sourceDef === 'string') {
      sourcePath = sourceDef
    } else {
      sourcePath = sourceDef.source ?? ''
      expectedHash = sourceDef.hash ? parseHash(sourceDef.hash) : null
      forked = sourceDef.forked ?? false
      forkedAt = sourceDef.forked_at ?? null

      // Check for planning format (has type/base but no source)
      if (!sourcePath && sourceDef.type) {
        forked = true // Treat planning entries as forked (skip verification)
      }
    }

    // Skip if source path is empty (planning format)
    if (!sourcePath) {
      const status = deriveStatus({ forked, missing: false, expectedHash, actualHash: null })
      return {
        localPath,
        sourcePath,
        expectedHash,
        actualHash: null,
        forked,
        forkedAt,
        missing: false,
        status,
        icon: STATUS_ICONS[status] ?? '?',
      }
    }

    const fullSourcePath = resolve(PROJECT_ROOT, sourcePath)
    if (!existsSync(fullSourcePath)) {
      const status = deriveStatus({ forked, missing: true, expectedHash, actualHash: null })
      return {
        localPath,
        sourcePath,
        expectedHash,
        actualHash: null,
        forked,
        forkedAt,
        missing: true,
        status,
        icon: STATUS_ICONS[status] ?? '?',
      }
    }

    const actualHash = await computeHash(fullSourcePath)
    const status = deriveStatus({ forked, missing: false, expectedHash, actualHash })
    return {
      localPath,
      sourcePath,
      expectedHash,
      actualHash,
      forked,
      forkedAt,
      missing: false,
      status,
      icon: STATUS_ICONS[status] ?? '?',
    }
  }

  async verifySources(): Promise<SourceStatus[]> {
    const data = await this.loadSources()
    const sources = data.sources
    // Handle list format (planning/roadmap) vs dict format (build)
    if (Array.isArray(sources)) {
      return [] // Skip planning format, not buildable
    }
    const results: SourceStatus[] = []
    for (const [lp, sd] of Object.entries(sources)) {
      results.push(await this.getSourceStatus(lp, sd))
    }
    return results
  }

  async updateHash(localPath: string): Promise<string> {
    const data = await this.loadSources()
    const sources = data.sources as Record<string, string | SourceDef>

    if (!(localPath in sources)) {
      throw new Error(`Component not found: ${localPath}`)
    }

    let sourceDef = sources[localPath]
    if (typeof sourceDef === 'string') {
      const sourcePath = sourceDef
      sources[localPath] = { source: sourcePath }
      sourceDef = sources[localPath] as SourceDef
    }

    const sourcePath = (sourceDef as SourceDef).source ?? ''
    const fullSourcePath = resolve(PROJECT_ROOT, sourcePath)
    if (!existsSync(fullSourcePath)) {
      throw new Error(`Source not found: ${sourcePath}`)
    }

    const newHash = await computeHash(fullSourcePath)
    ;(sourceDef as SourceDef).hash = formatHash(newHash)
    await this.saveSources(data)
    return newHash
  }

  async updateAllHashes(): Promise<string[]> {
    const updated: string[] = []
    const data = await this.loadSources()
    const sources = data.sources as Record<string, string | SourceDef>

    for (const [localPath, rawDef] of Object.entries(sources)) {
      let sourceDef = rawDef
      // Convert legacy format to extended format
      if (typeof sourceDef === 'string') {
        const sourcePath = sourceDef
        sources[localPath] = { source: sourcePath }
        sourceDef = sources[localPath] as SourceDef
      }

      const entry = sourceDef as SourceDef
      if (entry.forked) continue

      const sourcePath = entry.source ?? ''
      const fullSourcePath = resolve(PROJECT_ROOT, sourcePath)
      if (existsSync(fullSourcePath)) {
        const newHash = await computeHash(fullSourcePath)
        entry.hash = formatHash(newHash)
        updated.push(localPath)
      }
    }

    await this.saveSources(data)
    return updated
  }

  copySource(localPath: string, sourcePath: string): void {
    const target = join(this.dir, localPath)
    const source = resolve(PROJECT_ROOT, sourcePath)
    const targetDir = join(target, '..')

    mkdirSync(targetDir, { recursive: true })

    if (statSync(source).isDirectory()) {
      if (existsSync(target)) {
        rmSync(target, { recursive: true })
      }
      cpSync(source, target, { recursive: true })
    } else {
      cpSync(source, target)
    }
  }

  async build(opts: {
    force?: boolean
    checkOnly?: boolean
    updateHashes?: boolean
  }): Promise<BuildResult> {
    const { force = false, checkOnly = false, updateHashes = false } = opts
    const result: BuildResult = {
      pluginName: this.name,
      sources: [],
      copied: [],
      skipped: [],
      updated: [],
      errors: [],
    }

    result.sources = await this.verifySources()

    // Categorize sources by status
    const byStatus = {
      stale: result.sources.filter((s) => s.status === 'stale'),
      missing: result.sources.filter((s) => s.status === 'missing'),
      'no-hash': result.sources.filter((s) => s.status === 'no-hash'),
      forked: result.sources.filter((s) => s.status === 'forked'),
    }

    // Handle missing sources
    for (const s of byStatus.missing) {
      result.errors.push(`Missing source: ${s.sourcePath}`)
    }
    if (result.errors.length > 0 && !force) {
      return result
    }

    // Handle stale sources
    const stale = byStatus.stale
    if (stale.length > 0 && !force && !updateHashes) {
      if (checkOnly) {
        for (const s of stale) {
          result.errors.push(`Stale: ${s.localPath}`)
        }
        return result
      }
      // Non-interactive mode: report as errors
      for (const s of stale) {
        result.errors.push(`Stale: ${s.localPath}`)
      }
      return result
    }

    // Update hashes if requested
    if (updateHashes || force) {
      for (const s of [...stale, ...byStatus['no-hash']]) {
        if (!s.forked && !s.missing) {
          await this.updateHash(s.localPath)
          result.updated.push(s.localPath)
        }
      }
    }

    // Track forked components as skipped
    for (const s of byStatus.forked) {
      result.skipped.push(s.localPath)
    }

    if (!checkOnly) {
      // Copy all non-skipped sources
      const data = await this.loadSources()
      const sources = data.sources as Record<string, string | SourceDef>
      for (const [localPath, sourceDef] of Object.entries(sources)) {
        if (result.skipped.includes(localPath)) continue
        const sourcePath =
          typeof sourceDef === 'string' ? sourceDef : (sourceDef as SourceDef).source
        if (sourcePath && existsSync(resolve(PROJECT_ROOT, sourcePath))) {
          this.copySource(localPath, sourcePath)
          result.copied.push(localPath)
        }
      }
    }

    return result
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sourceToDict(s: SourceStatus): Record<string, unknown> {
  return {
    local_path: s.localPath,
    source_path: s.sourcePath,
    status: s.status,
    expected_hash: s.expectedHash ? formatHash(s.expectedHash) : null,
    actual_hash: s.actualHash ? formatHash(s.actualHash) : null,
    forked: s.forked,
    forked_at: s.forkedAt,
  }
}

function countStatuses(sources: SourceStatus[]): Record<string, number> {
  const counts: Record<string, number> = {}
  for (const s of sources) {
    counts[s.status] = (counts[s.status] ?? 0) + 1
  }
  return counts
}

/**
 * List all plugin directories that have a plugin.sources.json.
 * Recurses into category subdirectories (e.g., frontend/, releases/).
 */
export function listPlugins(): string[] {
  const plugins: string[] = []

  function scan(dir: string, prefix: string): void {
    if (!existsSync(dir)) return
    for (const entry of readdirSync(dir)) {
      if (entry.startsWith('.') || entry === '.template') continue
      const fullPath = join(dir, entry)
      if (!statSync(fullPath).isDirectory()) continue

      const sourcesFile = join(fullPath, '.claude-plugin', 'plugin.sources.json')
      if (existsSync(sourcesFile)) {
        plugins.push(prefix ? `${prefix}/${entry}` : entry)
      } else {
        // Could be a category directory (e.g., frontend/, releases/)
        scan(fullPath, prefix ? `${prefix}/${entry}` : entry)
      }
    }
  }

  scan(PLUGINS_DIR, '')
  return plugins.sort()
}

// ---------------------------------------------------------------------------
// Command definitions
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'plugin', description: 'Plugin build and verification' },
  subCommands: {
    build: defineCommand({
      meta: { name: 'build', description: 'Build a plugin (copy sources, verify hashes)' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
        force: {
          type: 'boolean',
          alias: 'f',
          description: 'Force rebuild, update hashes',
          default: false,
        },
        checkOnly: {
          type: 'boolean',
          alias: 'c',
          description: 'Verify hashes only, do not copy',
          default: false,
        },
        updateHashes: {
          type: 'boolean',
          alias: 'u',
          description: 'Update hashes without prompting',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const result = await plugin.build({
          force: args.force,
          checkOnly: args.checkOnly,
          updateHashes: args.updateHashes,
        })

        if (args.json) {
          out.raw({
            plugin: result.pluginName,
            sources: result.sources.map(sourceToDict),
            copied: result.copied,
            skipped: result.skipped,
            updated: result.updated,
            errors: result.errors,
            success: buildResultSuccess(result),
          })
        } else {
          printBuildSummary(out, result)
        }

        process.exit(buildResultSuccess(result) ? EXIT.OK : EXIT.FAILURES)
      },
    }),

    check: defineCommand({
      meta: { name: 'check', description: 'Verify plugin source hashes' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const sources = await plugin.verifySources()
        const counts = countStatuses(sources)

        // JSON output mode
        if (args.json) {
          const output = {
            plugin: plugin.name,
            sources: sources.map(sourceToDict),
            summary: counts,
            ok: !(counts.stale ?? 0) && !(counts.missing ?? 0),
          }
          out.raw(output)
          process.exit(output.ok ? EXIT.OK : EXIT.FAILURES)
        }

        // Text output
        out.info(`Plugin: ${plugin.name}\n`)

        if (args.verbose) {
          for (const s of sources) {
            console.log(`  ${s.icon} ${s.localPath} (${s.status})`)
            console.log(`      Source: ${s.sourcePath}`)
            if (s.expectedHash) {
              console.log(`      Expected: ${formatHash(s.expectedHash)}`)
            }
            if (s.actualHash) {
              console.log(`      Actual:   ${formatHash(s.actualHash)}`)
            }
            if (s.forkedAt) {
              console.log(`      Forked at: ${s.forkedAt}`)
            }
          }
        } else {
          for (const s of sources) {
            console.log(`  ${s.icon} ${s.localPath} (${s.status})`)
          }
        }

        const fresh = counts.fresh ?? 0
        const stale = counts.stale ?? 0
        const forked = counts.forked ?? 0
        const noHash = counts['no-hash'] ?? 0
        const missing = counts.missing ?? 0

        console.log(
          `\nSummary: ${fresh} fresh, ${stale} stale, ` +
            `${forked} forked, ${noHash} no-hash, ${missing} missing`
        )

        if (stale || missing) {
          process.exit(EXIT.FAILURES)
        }
        if (noHash) {
          out.warn('Plugin uses legacy format without hashes')
        }
        process.exit(EXIT.OK)
      },
    }),

    hash: defineCommand({
      meta: { name: 'hash', description: 'Compute hash of a path' },
      args: {
        ...globalArgs,
        path: { type: 'positional', description: 'File or directory to hash', required: true },
        hexOnly: {
          type: 'boolean',
          description: 'Output raw hex only, no sha256: prefix',
          default: false,
        },
      },
      async run({ args }) {
        const targetPath = resolve(args.path)
        if (!existsSync(targetPath)) {
          console.error(`Error: Path not found: ${targetPath}`)
          process.exit(EXIT.FAILURES)
        }

        const hex = await computeHash(targetPath)

        if (args.json) {
          console.log(JSON.stringify({ path: targetPath, hash: formatHash(hex) }))
        } else if (args.hexOnly) {
          console.log(hex)
        } else {
          console.log(formatHash(hex))
        }
        process.exit(EXIT.OK)
      },
    }),

    lint: defineCommand({
      meta: { name: 'lint', description: 'Lint plugin Claude Code files (via cclint)' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name (omit to lint all)' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })

        let pluginNames: string[]
        if (args.name) {
          const plugin = new Plugin(args.name)
          if (!existsSync(plugin.dir)) {
            out.error(`Plugin not found: ${args.name}`)
            process.exit(EXIT.FAILURES)
          }
          pluginNames = [args.name]
        } else {
          pluginNames = listPlugins()
          if (pluginNames.length === 0) {
            out.info('No plugins found')
            process.exit(EXIT.OK)
          }
        }

        const { CClint } = await import('@carlrannaberg/cclint')
        const linter = new CClint()
        let hasErrors = false
        const allResults: Record<string, unknown>[] = []

        for (const name of pluginNames) {
          const pluginDir = join(PLUGINS_DIR, name)
          try {
            const summary = await linter.lintProject(pluginDir, { quiet: true })
            const errorCount = summary.totalErrors
            const warnCount = summary.totalWarnings

            if (args.json) {
              allResults.push({
                plugin: name,
                totalFiles: summary.totalFiles,
                errors: errorCount,
                warnings: warnCount,
                valid: errorCount === 0,
              })
            } else {
              if (errorCount > 0) {
                console.log(`  \u2717 ${name}: ${errorCount} error(s), ${warnCount} warning(s)`)
                hasErrors = true
              } else if (warnCount > 0) {
                console.log(`  \u26A0 ${name}: ${warnCount} warning(s)`)
              } else {
                console.log(`  \u2713 ${name}: OK`)
              }
            }

            if (errorCount > 0) hasErrors = true
          } catch (e) {
            if (args.json) {
              allResults.push({ plugin: name, error: String(e) })
            } else {
              console.log(`  \u2717 ${name}: lint error - ${e}`)
            }
            hasErrors = true
          }
        }

        if (args.json) {
          out.raw(allResults)
        }

        process.exit(hasErrors ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    update: defineCommand({
      meta: { name: 'update', description: 'Update all hashes for a plugin' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const updated = await plugin.updateAllHashes()

        if (args.json) {
          out.raw({ plugin: args.name, updated })
        } else {
          out.info(`Updating hashes for ${args.name}...`)
          for (const localPath of updated) {
            console.log(`  \u2713 ${localPath}`)
          }
          out.success(`Updated ${updated.length} component(s)`)
        }

        process.exit(EXIT.OK)
      },
    }),

    'check-all': defineCommand({
      meta: { name: 'check-all', description: 'Verify all plugin sources' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Checking ${plugins.length} plugins...`)
        const results: Record<string, unknown>[] = []
        const failed: string[] = []

        for (const name of plugins) {
          spinner.update({ text: `Checking ${name}...` })
          const plugin = new Plugin(name)
          const sources = await plugin.verifySources()
          const counts = countStatuses(sources)

          const stale = counts.stale ?? 0
          const missing = counts.missing ?? 0
          const fresh = counts.fresh ?? 0
          const total = sources.length
          const ok = !(stale || missing)

          results.push({
            name,
            fresh,
            stale,
            missing,
            forked: counts.forked ?? 0,
            no_hash: counts['no-hash'] ?? 0,
            total,
            ok,
          })

          if (!ok) failed.push(name)
        }

        spinner.success({ text: `Checked ${plugins.length} plugins` })

        if (args.json) {
          out.raw({
            plugins: results,
            summary: {
              total: plugins.length,
              ok: plugins.length - failed.length,
              failed: failed.length,
            },
            failed,
            ok: failed.length === 0,
          })
        } else {
          for (const r of results) {
            if (r.ok) {
              console.log(`  \u2713 ${r.name}: ${r.fresh}/${r.total} fresh`)
            } else {
              console.log(
                `  \u2717 ${r.name}: ${r.fresh}/${r.total} fresh, ` +
                  `${r.stale} stale, ${r.missing} missing`
              )
            }
          }

          const okCount = plugins.length - failed.length
          const icon = failed.length ? '\u2717' : '\u2713'
          console.log(`\n${icon} ${okCount}/${plugins.length} plugins OK`)
          if (failed.length) {
            console.log(`\nFailed: ${failed.join(', ')}`)
          }
        }

        process.exit(failed.length ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    'build-all': defineCommand({
      meta: { name: 'build-all', description: 'Build all plugins' },
      args: {
        ...globalArgs,
        force: {
          type: 'boolean',
          alias: 'f',
          description: 'Force rebuild, update hashes',
          default: false,
        },
        checkOnly: {
          type: 'boolean',
          alias: 'c',
          description: 'Verify hashes only, do not copy',
          default: false,
        },
        updateHashes: {
          type: 'boolean',
          alias: 'u',
          description: 'Update hashes without prompting',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Building ${plugins.length} plugins...`)
        const failed: string[] = []
        const allResults: Record<string, unknown>[] = []

        for (const name of plugins) {
          spinner.update({ text: `Building ${name}...` })
          const plugin = new Plugin(name)
          const result = await plugin.build({
            force: args.force,
            checkOnly: args.checkOnly,
            updateHashes: args.updateHashes,
          })

          if (buildResultSuccess(result)) {
            if (!args.json) {
              console.log(
                `  \u2713 ${name}: ${result.copied.length} copied, ${result.updated.length} updated`
              )
            }
          } else {
            if (!args.json) {
              console.log(`  \u2717 ${name}: ${result.errors[0] ?? 'unknown error'}`)
            }
            failed.push(name)
          }

          if (args.json) {
            allResults.push({
              name,
              copied: result.copied.length,
              updated: result.updated.length,
              errors: result.errors,
              success: buildResultSuccess(result),
            })
          }
        }

        spinner.success({ text: `Built ${plugins.length} plugins` })

        if (args.json) {
          out.raw({
            plugins: allResults,
            summary: {
              total: plugins.length,
              ok: plugins.length - failed.length,
              failed: failed.length,
            },
            failed,
            ok: failed.length === 0,
          })
        } else {
          const okCount = plugins.length - failed.length
          const icon = failed.length ? '\u2717' : '\u2713'
          console.log(`\n${icon} ${okCount}/${plugins.length} plugins built`)
          if (failed.length) {
            console.log(`\nFailed: ${failed.join(', ')}`)
          }
        }

        process.exit(failed.length ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    'update-all': defineCommand({
      meta: { name: 'update-all', description: 'Update all plugin hashes' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Updating ${plugins.length} plugins...`)
        const allResults: Record<string, unknown>[] = []

        for (const name of plugins) {
          spinner.update({ text: `Updating ${name}...` })
          const plugin = new Plugin(name)
          const updated = await plugin.updateAllHashes()

          if (args.json) {
            allResults.push({ name, updated: updated.length })
          } else {
            console.log(`  \u2713 ${name}: ${updated.length} hashes updated`)
          }
        }

        spinner.success({ text: `Updated ${plugins.length} plugins` })

        if (args.json) {
          out.raw({ plugins: allResults })
        } else {
          out.success(`${plugins.length} plugins updated`)
        }

        process.exit(EXIT.OK)
      },
    }),
  },
})

// ---------------------------------------------------------------------------
// Print helpers (human mode only)
// ---------------------------------------------------------------------------

function printBuildSummary(out: OutputFormatter, result: BuildResult): void {
  out.info(`Building plugin: ${result.pluginName}\n`)

  console.log('Components:')
  for (const s of result.sources) {
    console.log(`  ${s.icon} ${s.localPath} (${s.status})`)
  }

  console.log('\nActions:')
  if (result.updated.length > 0) {
    console.log(`  Updated: ${result.updated.length} component(s)`)
  }
  if (result.skipped.length > 0) {
    console.log(`  Skipped: ${result.skipped.length} forked`)
  }
  const fresh = result.sources.filter((s) => s.status === 'fresh')
  if (fresh.length > 0) {
    console.log(`  Fresh: ${fresh.length} component(s)`)
  }
  if (result.copied.length > 0) {
    console.log(`  Copied: ${result.copied.length} component(s)`)
  }

  if (result.errors.length > 0) {
    console.log('\nErrors:')
    for (const e of result.errors) {
      console.log(`  \u2717 ${e}`)
    }
    out.error('Build failed')
  } else {
    out.success('Plugin built successfully')
  }
}
