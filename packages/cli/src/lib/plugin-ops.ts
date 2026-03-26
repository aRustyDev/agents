/**
 * Plugin operations library.
 *
 * Extracted from commands/plugin.ts to enable reuse from lint.ts and tests.
 * Contains:
 *   - Plugin class (load, verify, build, hash operations)
 *   - Validation functions (validatePlugin, validateMarketplace)
 *   - Display helpers (printValidationResult, printBuildSummary)
 *   - Constants and utility functions
 */

import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { computeHash, formatHash, parseHash } from '@agents/core/hash'
import type { OutputFormatter } from '@agents/core/output'
import { currentDir } from '@agents/core/runtime'
import {
  detectUnknownPluginFields,
  LspConfig,
  MarketplaceManifest,
  McpConfig,
  PluginManifest,
  SkillFrontmatter,
} from '@agents/core/schemas'
import * as v from 'valibot'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Project root -- from packages/cli/src/lib/ it is 4 levels up. */
export const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')

/** Directory containing all plugins. */
export const PLUGINS_DIR = join(PROJECT_ROOT, 'content/plugins')

export const STATUS_ICONS: Record<string, string> = {
  fresh: '\u2713',
  stale: '\u26A0',
  missing: '\u2717',
  forked: '\u25CB',
  'no-hash': '?',
}

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

export function deriveStatus(opts: {
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

export interface BuildResult {
  pluginName: string
  sources: SourceStatus[]
  copied: string[]
  skipped: string[]
  updated: string[]
  errors: string[]
}

export function buildResultSuccess(result: BuildResult): boolean {
  return result.errors.length === 0
}

// ---------------------------------------------------------------------------
// Plugin class
// ---------------------------------------------------------------------------

export interface SourceDef {
  source: string
  hash?: string
  forked?: boolean
  forked_at?: string
  type?: string
  base?: string
  notes?: string
}

export type SourcesMap = Record<string, string | SourceDef>

export interface SourcesFile {
  $schema?: string
  sources: SourcesMap
}

export class Plugin {
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
    const { writeFile: writeFileAsync } = await import('node:fs/promises')
    const json = `${JSON.stringify(data, null, 2)}\n`
    await writeFileAsync(this.sourcesFile, json, 'utf-8')
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

export function sourceToDict(s: SourceStatus): Record<string, unknown> {
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

export function countStatuses(sources: SourceStatus[]): Record<string, number> {
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
// Validation
// ---------------------------------------------------------------------------

export interface ValidationResult {
  plugin: string
  valid: boolean
  errors: string[]
  warnings: string[]
}

export async function validatePlugin(name: string): Promise<ValidationResult> {
  const pluginDir = join(PLUGINS_DIR, name)
  const manifestPath = join(pluginDir, '.claude-plugin', 'plugin.json')
  const errors: string[] = []
  const warnings: string[] = []

  // 1. Check plugin directory exists
  if (!existsSync(pluginDir)) {
    return {
      plugin: name,
      valid: false,
      errors: [`Plugin directory not found: ${pluginDir}`],
      warnings,
    }
  }

  // 2. Check manifest exists
  if (!existsSync(manifestPath)) {
    return {
      plugin: name,
      valid: false,
      errors: [`plugin.json not found: ${manifestPath}`],
      warnings,
    }
  }

  // 3. Parse and validate manifest against schema
  let rawData: Record<string, unknown>
  try {
    const raw = await readFile(manifestPath, 'utf-8')
    rawData = JSON.parse(raw) as Record<string, unknown>
  } catch (e) {
    return { plugin: name, valid: false, errors: [`Invalid JSON in plugin.json: ${e}`], warnings }
  }

  const parseResult = v.safeParse(PluginManifest, rawData)
  if (!parseResult.success) {
    for (const issue of parseResult.issues) {
      const path =
        issue.path?.map((p) => (typeof p === 'object' && 'key' in p ? p.key : p)).join('.') ?? ''
      errors.push(`Schema error${path ? ` at ${path}` : ''}: ${issue.message}`)
    }
  }

  // 4. Detect unknown fields
  const unknownFields = detectUnknownPluginFields(rawData)
  for (const field of unknownFields) {
    warnings.push(`Unknown field "${field}" — not recognized by Claude Code plugin loader`)
  }

  // 5. Verify referenced paths exist
  const pathArrays = ['commands', 'agents', 'skills', 'outputStyles'] as const
  for (const key of pathArrays) {
    const arr = rawData[key]
    if (Array.isArray(arr)) {
      for (const entry of arr) {
        if (typeof entry === 'string') {
          const resolved = join(pluginDir, entry)
          if (!existsSync(resolved)) {
            errors.push(`Missing ${key} file: ${entry} (resolved to ${resolved})`)
          }
        }
      }
    }
  }

  // 5b. Validate SKILL.md frontmatter for each skill
  const skillPaths = rawData.skills
  if (Array.isArray(skillPaths)) {
    for (const entry of skillPaths) {
      if (typeof entry !== 'string') continue
      const resolved = join(pluginDir, entry)
      if (!existsSync(resolved)) continue // already reported as missing

      try {
        const content = await readFile(resolved, 'utf-8')
        // Extract YAML frontmatter between --- delimiters
        const fmMatch = content.match(/^---\n([\s\S]*?)\n---/)
        if (!fmMatch) {
          warnings.push(`Skill ${entry}: no YAML frontmatter found`)
          continue
        }
        // Parse YAML (simple key: value for flat frontmatter)
        const fmLines = fmMatch[1].split('\n')
        const fmData: Record<string, unknown> = {}
        for (const line of fmLines) {
          const match = line.match(/^(\w[\w-]*)\s*:\s*(.*)$/)
          if (match) {
            const [, key, val] = match
            // Handle arrays (tags: [a, b, c])
            const arrMatch = val!.match(/^\[(.*)\]$/)
            if (arrMatch) {
              fmData[key!] = arrMatch[1]!
                .split(',')
                .map((s) => s.trim().replace(/^['"]|['"]$/g, ''))
            } else {
              fmData[key!] = val!.trim().replace(/^['"]|['"]$/g, '')
            }
          }
        }

        const fmResult = v.safeParse(SkillFrontmatter, fmData)
        if (!fmResult.success) {
          for (const issue of fmResult.issues) {
            const path =
              issue.path?.map((p) => (typeof p === 'object' && 'key' in p ? p.key : p)).join('.') ??
              ''
            warnings.push(
              `Skill ${entry} frontmatter${path ? ` at ${path}` : ''}: ${issue.message}`
            )
          }
        }
      } catch {
        /* skip if unreadable */
      }
    }
  }

  // 6. Check .lsp.json if present
  const lspPath = join(pluginDir, '.lsp.json')
  if (existsSync(lspPath)) {
    try {
      const lspRaw = await readFile(lspPath, 'utf-8')
      const lspData = JSON.parse(lspRaw)
      const lspResult = v.safeParse(LspConfig, lspData)
      if (!lspResult.success) {
        for (const issue of lspResult.issues) {
          const path =
            issue.path?.map((p) => (typeof p === 'object' && 'key' in p ? p.key : p)).join('.') ??
            ''
          errors.push(`.lsp.json schema error${path ? ` at ${path}` : ''}: ${issue.message}`)
        }
      } else if (Object.keys(lspResult.output.lspServers).length === 0) {
        warnings.push('.lsp.json has no servers defined — consider deleting if unused')
      }
    } catch {
      errors.push('.lsp.json contains invalid JSON')
    }
  }

  // 7. Check .mcp.json if present
  const mcpPath = join(pluginDir, '.mcp.json')
  if (existsSync(mcpPath)) {
    try {
      const mcpRaw = await readFile(mcpPath, 'utf-8')
      const mcpData = JSON.parse(mcpRaw)
      const mcpResult = v.safeParse(McpConfig, mcpData)
      if (!mcpResult.success) {
        for (const issue of mcpResult.issues) {
          const path =
            issue.path?.map((p) => (typeof p === 'object' && 'key' in p ? p.key : p)).join('.') ??
            ''
          errors.push(`.mcp.json schema error${path ? ` at ${path}` : ''}: ${issue.message}`)
        }
      } else {
        // Check for empty servers in whichever format matched
        const output = mcpResult.output
        const servers = 'mcpServers' in output ? output.mcpServers : output.mcp.servers
        if (Object.keys(servers).length === 0) {
          warnings.push(
            '.mcp.json has empty servers — consider deleting if no MCP servers are used'
          )
        }
      }
    } catch {
      errors.push('.mcp.json contains invalid JSON')
    }
  }

  return { plugin: name, valid: errors.length === 0, errors, warnings }
}

export async function validateMarketplace(): Promise<ValidationResult> {
  const marketplacePath = join(PROJECT_ROOT, '.claude-plugin', 'marketplace.json')
  const errors: string[] = []
  const warnings: string[] = []

  if (!existsSync(marketplacePath)) {
    return { plugin: 'marketplace', valid: false, errors: ['marketplace.json not found'], warnings }
  }

  let rawData: unknown
  try {
    const raw = await readFile(marketplacePath, 'utf-8')
    rawData = JSON.parse(raw)
  } catch (e) {
    return {
      plugin: 'marketplace',
      valid: false,
      errors: [`Invalid JSON: ${e}`],
      warnings,
    }
  }

  const parseResult = v.safeParse(MarketplaceManifest, rawData)
  if (!parseResult.success) {
    for (const issue of parseResult.issues) {
      const path =
        issue.path?.map((p) => (typeof p === 'object' && 'key' in p ? p.key : p)).join('.') ?? ''
      errors.push(`Schema error${path ? ` at ${path}` : ''}: ${issue.message}`)
    }
    return { plugin: 'marketplace', valid: errors.length === 0, errors, warnings }
  }

  // Check for duplicate plugin names
  const names = parseResult.output.plugins.map((p) => p.name)
  const dupes = names.filter((n, i) => names.indexOf(n) !== i)
  for (const d of new Set(dupes)) {
    errors.push(`Duplicate plugin name: "${d}"`)
  }

  // Check source paths exist
  for (const entry of parseResult.output.plugins) {
    const sourcePath = join(PROJECT_ROOT, entry.source)
    if (!existsSync(sourcePath)) {
      errors.push(`Plugin "${entry.name}" source path not found: ${entry.source}`)
    }

    // Version sync check -- compare with plugin's own plugin.json
    const pluginJsonPath = join(sourcePath, '.claude-plugin', 'plugin.json')
    if (existsSync(pluginJsonPath)) {
      try {
        const pluginRaw = await readFile(pluginJsonPath, 'utf-8')
        const pluginData = JSON.parse(pluginRaw) as { version?: string }
        if (pluginData.version && pluginData.version !== entry.version) {
          warnings.push(
            `Plugin "${entry.name}" version mismatch: marketplace has ${entry.version}, plugin.json has ${pluginData.version}`
          )
        }
      } catch {
        /* skip if unreadable */
      }
    }
  }

  return { plugin: 'marketplace', valid: errors.length === 0, errors, warnings }
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

export function printValidationResult(out: OutputFormatter, result: ValidationResult): void {
  if (result.valid && result.warnings.length === 0) {
    out.success(`Plugin "${result.plugin}" is valid`)
    return
  }

  out.info(`Validating plugin: ${result.plugin}\n`)

  if (result.errors.length > 0) {
    console.log('Errors:')
    for (const e of result.errors) {
      console.log(`  \u2717 ${e}`)
    }
  }

  if (result.warnings.length > 0) {
    console.log('Warnings:')
    for (const w of result.warnings) {
      console.log(`  \u26A0 ${w}`)
    }
  }

  if (result.valid) {
    out.warn(`Plugin valid with ${result.warnings.length} warning(s)`)
  } else {
    out.error(`Plugin validation failed: ${result.errors.length} error(s)`)
  }
}

export function printBuildSummary(out: OutputFormatter, result: BuildResult): void {
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
