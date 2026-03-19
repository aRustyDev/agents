#!/usr/bin/env bun
/**
 * catalog.ts — Phase 2: Availability Check
 *
 * Reads context/skills/.TODO.yaml (entries in format `org/repo@skill-name`),
 * checks GitHub availability for each unique repo via HTTP HEAD, and writes
 * one NDJSON line per entry to context/skills/.catalog.ndjson.
 *
 * Usage:
 *   bun run .scripts/lib/catalog.ts
 *   bun run .scripts/lib/catalog.ts --concurrency 20 --delay 500
 *   bun run .scripts/lib/catalog.ts --dry-run
 *   bun run .scripts/lib/catalog.ts --resume
 *
 * Environment:
 *   GITHUB_TOKEN   Optional. Uses authenticated rate limit (5000/hr vs 60/min).
 *
 * .TODO.yaml format:
 *   Each line is either:
 *     - `org/repo@skill-name`   (standard entry — processed)
 *     - A URL, comment, or other text  (skipped)
 *
 * Output: context/skills/.catalog.ndjson
 *   One JSON line per .TODO.yaml entry:
 *   {"source":"org/repo","skill":"skill-name","availability":"available"}
 */

import { createWriteStream, existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AvailabilityStatus = 'available' | 'archived' | 'not_found' | 'private' | 'error'

export interface CatalogEntry {
  source: string // org/repo
  skill: string // skill name (part after @)
  availability: AvailabilityStatus
}

interface CheckOptions {
  concurrency?: number // parallel requests (default: 20)
  delayMs?: number // ms between batches (default: 500)
  token?: string // GitHub token for higher rate limit
  dryRun?: boolean // if true, skip actual HTTP requests
  timeout?: number // request timeout in ms (default: 10000)
}

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const REPO_ROOT = join(import.meta.dir, '..', '..')
const TODO_YAML_PATH = join(REPO_ROOT, 'context', 'skills', '.TODO.yaml')
const CATALOG_PATH = join(REPO_ROOT, 'context', 'skills', '.catalog.ndjson')

// ---------------------------------------------------------------------------
// Parsing
// ---------------------------------------------------------------------------

/**
 * Parse a single .TODO.yaml line.
 * Returns {source, skill} if the line matches `org/repo@skill-name`,
 * otherwise returns null (to be skipped).
 *
 * A valid entry looks like: `owner/repo-name@skill-name`
 * - owner: alphanumeric + hyphens
 * - repo:  alphanumeric + hyphens + dots
 * - skill: alphanumeric + hyphens + dots + underscores
 */
function parseTodoLine(line: string): { source: string; skill: string } | null {
  const trimmed = line.trim()

  // Skip blank lines, YAML list markers (- ...), comments (#), and URLs
  if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('http')) {
    return null
  }

  // Strip leading YAML list marker "- " if present
  const entry = trimmed.startsWith('- ') ? trimmed.slice(2).trim() : trimmed

  // Match pattern: org/repo@skill  (e.g. "anthropics/skills@pdf")
  // org/repo may contain hyphens, dots; skill may contain hyphens, underscores, dots
  const match = entry.match(/^([\w.-]+\/[\w./-]+)@([\w./-]+)$/)
  if (!match) return null

  const source = match[1] // e.g. "anthropics/skills"
  const skill = match[2] // e.g. "pdf"

  // Sanity check: source must be exactly "owner/repo" (one slash)
  const slashes = source.split('/').length - 1
  if (slashes !== 1) return null

  return { source, skill }
}

/**
 * Parse .TODO.yaml and return all valid entries.
 * Skips malformed lines (URLs, comments, etc.).
 */
export function parseTodoYaml(content: string): Array<{ source: string; skill: string }> {
  const entries: Array<{ source: string; skill: string }> = []

  for (const line of content.split('\n')) {
    const parsed = parseTodoLine(line)
    if (parsed) entries.push(parsed)
  }

  return entries
}

/**
 * Extract unique org/repo pairs from the entry list.
 */
export function uniqueRepos(entries: Array<{ source: string }>): string[] {
  return [...new Set(entries.map((e) => e.source))]
}

// ---------------------------------------------------------------------------
// HTTP availability check
// ---------------------------------------------------------------------------

/**
 * Check GitHub availability for a single org/repo.
 * Uses HTTP HEAD to minimize payload. GitHub redirects archived repos to
 * /owner/repo/archived — we detect that via the Location header on a 301.
 */
export async function checkRepoAvailability(
  ownerRepo: string,
  opts: { token?: string; timeout?: number; dryRun?: boolean } = {}
): Promise<AvailabilityStatus> {
  if (opts.dryRun) return 'available'

  const url = `https://github.com/${ownerRepo}`
  const timeout = opts.timeout ?? 10_000

  const headers: Record<string, string> = {
    'User-Agent': 'catalog-availability-checker/1.0 (ai-context-library)',
  }
  if (opts.token) {
    headers.Authorization = `token ${opts.token}`
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      method: 'HEAD',
      headers,
      redirect: 'manual', // capture redirects ourselves
      signal: controller.signal,
    })

    clearTimeout(timer)

    const status = response.status

    if (status === 200) return 'available'

    if (status === 301 || status === 302) {
      // GitHub archives repos by redirecting to the same URL (HEAD still returns 301)
      // A permanent redirect of a repo page typically signals archival or rename.
      // We conservatively mark 301 as 'archived'.
      return 'archived'
    }

    if (status === 404) return 'not_found'
    if (status === 401 || status === 403) return 'private'

    // 429 rate-limited — treat as error; caller should retry with backoff
    if (status === 429) return 'error'

    // Any other 4xx/5xx
    return 'error'
  } catch (_err) {
    clearTimeout(timer)
    // AbortError = timeout; fetch errors = network issue
    return 'error'
  }
}

// ---------------------------------------------------------------------------
// Batch checker with concurrency + rate limiting
// ---------------------------------------------------------------------------

/**
 * Check availability for all repos with concurrency control and rate limiting.
 * Returns a Map of ownerRepo → AvailabilityStatus.
 * Writes progress to stderr.
 */
export async function checkAllRepos(
  repos: string[],
  opts: CheckOptions = {}
): Promise<Map<string, AvailabilityStatus>> {
  const { concurrency = 20, delayMs = 500, token, dryRun = false, timeout = 10_000 } = opts

  const results = new Map<string, AvailabilityStatus>()
  const total = repos.length
  let done = 0

  // Process repos in batches of `concurrency`
  for (let i = 0; i < repos.length; i += concurrency) {
    const batch = repos.slice(i, i + concurrency)

    const batchResults = await Promise.all(
      batch.map((repo) =>
        checkRepoAvailability(repo, { token, timeout, dryRun })
          .then((status) => ({ repo, status }))
          .catch(() => ({ repo, status: 'error' as AvailabilityStatus }))
      )
    )

    for (const { repo, status } of batchResults) {
      results.set(repo, status)
      done++
    }

    // Progress report to stderr
    const pct = Math.round((done / total) * 100)
    process.stderr.write(
      `\r  Checking repos: ${done}/${total} (${pct}%)  [batch ${Math.ceil((i + concurrency) / concurrency)} of ${Math.ceil(total / concurrency)}]`
    )

    // Rate-limit delay between batches (skip after the last batch)
    if (i + concurrency < repos.length && delayMs > 0 && !dryRun) {
      await new Promise((resolve) => setTimeout(resolve, delayMs))
    }
  }

  process.stderr.write('\n')
  return results
}

// ---------------------------------------------------------------------------
// NDJSON output
// ---------------------------------------------------------------------------

/**
 * Write catalog entries to the output file incrementally.
 * Opens file in append mode so partial runs are resumable.
 */
function writeCatalogEntries(entries: CatalogEntry[], outputPath: string): void {
  const stream = createWriteStream(outputPath, { flags: 'a', encoding: 'utf8' })
  for (const entry of entries) {
    stream.write(`${JSON.stringify(entry)}\n`)
  }
  stream.end()
}

// ---------------------------------------------------------------------------
// Resume support
// ---------------------------------------------------------------------------

/**
 * Load already-processed repos from an existing .catalog.ndjson file.
 * Returns a Set of "source" values (org/repo) that are already present.
 */
function loadProcessedRepos(catalogPath: string): Set<string> {
  const processed = new Set<string>()
  if (!existsSync(catalogPath)) return processed

  const content = readFileSync(catalogPath, 'utf8')
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      const entry = JSON.parse(trimmed) as CatalogEntry
      if (entry.source) processed.add(entry.source)
    } catch {
      // malformed line — skip
    }
  }
  return processed
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

function printSummary(entries: CatalogEntry[]): void {
  const counts: Record<AvailabilityStatus, number> = {
    available: 0,
    archived: 0,
    not_found: 0,
    private: 0,
    error: 0,
  }

  for (const entry of entries) {
    counts[entry.availability]++
  }

  console.log('\nAvailability Summary:')
  console.log(`  available:  ${counts.available}`)
  console.log(`  archived:   ${counts.archived}`)
  console.log(`  not_found:  ${counts.not_found}`)
  console.log(`  private:    ${counts.private}`)
  console.log(`  error:      ${counts.error}`)
  console.log(`  total:      ${entries.length}`)
}

// ---------------------------------------------------------------------------
// CLI helpers
// ---------------------------------------------------------------------------

interface CliArgs {
  dryRun: boolean
  resume: boolean
  concurrency: number
  delayMs: number
  token: string | undefined
}

function parseCliArgs(): CliArgs {
  const args = process.argv.slice(2)
  const dryRun = args.includes('--dry-run')
  const resume = args.includes('--resume')

  let concurrency = 20
  let delayMs = 500

  const concurrencyIdx = args.findIndex((a) => a === '--concurrency')
  if (concurrencyIdx !== -1 && args[concurrencyIdx + 1]) {
    concurrency = parseInt(args[concurrencyIdx + 1], 10)
  }

  const delayIdx = args.findIndex((a) => a === '--delay')
  if (delayIdx !== -1 && args[delayIdx + 1]) {
    delayMs = parseInt(args[delayIdx + 1], 10)
  }

  return { dryRun, resume, concurrency, delayMs, token: process.env.GITHUB_TOKEN }
}

function loadTodoEntries(): Array<{ source: string; skill: string }> {
  if (!existsSync(TODO_YAML_PATH)) {
    console.error(`Error: Input file not found: ${TODO_YAML_PATH}`)
    console.error()
    console.error('Expected format (one entry per line):')
    console.error('  org/repo@skill-name')
    console.error('  # comments are skipped')
    console.error('  https://... URLs are skipped')
    process.exit(1)
  }
  const content = readFileSync(TODO_YAML_PATH, 'utf8')
  return parseTodoYaml(content)
}

function readCatalogEntries(catalogPath: string): CatalogEntry[] {
  const result: CatalogEntry[] = []
  const content = readFileSync(catalogPath, 'utf8')
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      result.push(JSON.parse(trimmed) as CatalogEntry)
    } catch {
      // skip malformed lines
    }
  }
  return result
}

function buildNewEntries(
  allEntries: Array<{ source: string; skill: string }>,
  statusMap: Map<string, AvailabilityStatus>,
  alreadyProcessed: Set<string>
): CatalogEntry[] {
  const newEntries: CatalogEntry[] = []
  for (const entry of allEntries) {
    if (alreadyProcessed.has(entry.source)) continue
    newEntries.push({
      source: entry.source,
      skill: entry.skill,
      availability: statusMap.get(entry.source) ?? 'error',
    })
  }
  return newEntries
}

// ---------------------------------------------------------------------------
// CLI entry point
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const { dryRun, resume, concurrency, delayMs, token } = parseCliArgs()
  const allEntries = loadTodoEntries()
  const repos = uniqueRepos(allEntries)

  console.log(`Reading: ${TODO_YAML_PATH}`)
  console.log(`  Parsed ${allEntries.length} valid entries`)
  console.log(`  Unique repos: ${repos.length}`)

  if (dryRun) {
    console.log('\n[DRY RUN] Would check these repos (first 10):')
    repos.slice(0, 10).forEach((r) => console.log(`  ${r}`))
    if (repos.length > 10) console.log(`  ... and ${repos.length - 10} more`)
    return
  }

  // Resume: skip repos already in the catalog
  let alreadyProcessed = new Set<string>()
  let reposToCheck = repos

  if (resume && existsSync(CATALOG_PATH)) {
    alreadyProcessed = loadProcessedRepos(CATALOG_PATH)
    reposToCheck = repos.filter((r) => !alreadyProcessed.has(r))
    console.log(`  Resume: ${alreadyProcessed.size} already done, ${reposToCheck.length} remaining`)
  }

  const tokenMsg = token
    ? 'present (5000 req/hr limit)'
    : 'absent (60 req/min unauthenticated — consider setting GITHUB_TOKEN)'
  console.log(`  GitHub token: ${tokenMsg}`)
  console.log(`  Concurrency: ${concurrency}, batch delay: ${delayMs}ms`)
  console.log(`\nChecking ${reposToCheck.length} repos...`)

  const statusMap = await checkAllRepos(reposToCheck, {
    concurrency,
    delayMs,
    token,
    timeout: 10_000,
  })
  const newEntries = buildNewEntries(allEntries, statusMap, alreadyProcessed)

  console.log(`\nWriting ${newEntries.length} entries to: ${CATALOG_PATH}`)
  writeCatalogEntries(newEntries, CATALOG_PATH)

  // For summary, use all written entries (previously written + new)
  const allWritten =
    resume && alreadyProcessed.size > 0 ? readCatalogEntries(CATALOG_PATH) : newEntries

  printSummary(allWritten)
}

// Run when executed directly
main().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
