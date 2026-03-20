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

import { createWriteStream, existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { currentDir } from './runtime'

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

const REPO_ROOT = join(currentDir(import.meta), '..', '..')
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
// Phase 4: Tier 1 Analysis — Types
// ---------------------------------------------------------------------------

export interface Tier1Result {
  source: string
  skill: string
  wordCount?: number
  sectionCount?: number
  fileCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  keywords?: string[]
  internalLinks?: string[]
  externalLinks?: string[]
  complexity?: 'simple' | 'moderate' | 'complex'
  progressiveDisclosure?: boolean
  pdTechniques?: string[]
  bestPracticesMechanical?: { score: number; violations: string[] }
  securityMechanical?: { score: number; concerns: string[] }
  contentHash?: string
  tier2Reviewed?: boolean
  error?: string
  errorType?:
    | 'download_failed'
    | 'download_timeout'
    | 'analysis_failed'
    | 'analysis_timeout'
    | 'rate_limited'
    | 'batch_failed'
  errorDetail?: string
  errorCode?: number
  retryable?: boolean
  possibleForkOf?: string
  runId?: string
  batchId?: string
  analyzedAt?: string
}

/** CatalogEntry extended with optional Tier1 analysis fields. */
export type CatalogEntryWithTier1 = CatalogEntry & Partial<Tier1Result>

// ---------------------------------------------------------------------------
// Phase 4: Tier 1 Analysis — Data Transformation Functions
// ---------------------------------------------------------------------------

/**
 * Read catalog entries from an NDJSON file.
 * Re-export of the internal readCatalogEntries for public consumption.
 */
export function readCatalog(path: string): CatalogEntry[] {
  return readCatalogEntries(path)
}

/**
 * Filter catalog entries to only those with `availability === 'available'`.
 */
export function filterAvailable(entries: CatalogEntry[]): CatalogEntry[] {
  return entries.filter((e) => e.availability === 'available')
}

/**
 * Split entries into batches of `batchSize`, grouping by `source` to
 * minimize the number of distinct repo downloads per batch.
 *
 * Strategy: sort entries by source first so entries from the same repo
 * are adjacent, then chunk into groups of batchSize.
 */
export function createBatches(entries: CatalogEntry[], batchSize: number): CatalogEntry[][] {
  if (batchSize <= 0) throw new Error(`batchSize must be positive, got ${batchSize}`)
  if (entries.length === 0) return []

  // Sort by source to group entries from the same repo together
  const sorted = [...entries].sort((a, b) => a.source.localeCompare(b.source))

  const batches: CatalogEntry[][] = []
  for (let i = 0; i < sorted.length; i += batchSize) {
    batches.push(sorted.slice(i, i + batchSize))
  }
  return batches
}

/**
 * Format a batch of catalog entries as newline-separated `org/repo@skill-name`
 * strings suitable for the skill-inspector-t1 agent prompt.
 */
export function formatBatchPrompt(batch: CatalogEntry[]): string {
  return batch.map((e) => `${e.source}@${e.skill}`).join('\n')
}

/**
 * Parse NDJSON lines from agent stdout into Tier1Result objects.
 * Skips blank lines and malformed JSON, logging parse errors to stderr.
 */
export function parseTier1Output(stdout: string): Tier1Result[] {
  const results: Tier1Result[] = []

  for (const line of stdout.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue

    try {
      const parsed = JSON.parse(trimmed) as Record<string, unknown>

      // Validate minimum required fields
      if (typeof parsed.source !== 'string' || typeof parsed.skill !== 'string') {
        process.stderr.write(
          `[parseTier1Output] skipping line missing source/skill: ${trimmed.slice(0, 120)}\n`
        )
        continue
      }

      results.push(parsed as unknown as Tier1Result)
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      process.stderr.write(
        `[parseTier1Output] skipping malformed JSON: ${msg} — line: ${trimmed.slice(0, 120)}\n`
      )
    }
  }

  return results
}

/**
 * Detect possible forks by comparing contentHash values among entries
 * sharing the same skill name. Entries with identical hashes are marked
 * with `possibleForkOf` pointing to the first-seen source for that hash.
 *
 * Returns a new array with the `possibleForkOf` field set where applicable.
 * Only entries that have a non-empty `contentHash` participate in detection.
 */
export function detectForks(results: Tier1Result[]): Tier1Result[] {
  // Group by skill name
  const bySkill = new Map<string, Tier1Result[]>()
  for (const r of results) {
    const group = bySkill.get(r.skill)
    if (group) {
      group.push(r)
    } else {
      bySkill.set(r.skill, [r])
    }
  }

  // For each group with >1 entry, check content hashes
  // Track first-seen hash → source mapping per skill
  for (const group of bySkill.values()) {
    if (group.length <= 1) continue

    const hashToFirstSource = new Map<string, string>()

    for (const entry of group) {
      if (!entry.contentHash) continue

      const firstSource = hashToFirstSource.get(entry.contentHash)
      if (firstSource === undefined) {
        // First time seeing this hash for this skill
        hashToFirstSource.set(entry.contentHash, entry.source)
      } else if (firstSource !== entry.source) {
        // Same hash, different source — possible fork
        entry.possibleForkOf = firstSource
      }
    }
  }

  return results
}

/**
 * Merge Tier1Result fields into an existing `.catalog.ndjson` file.
 *
 * For each result, finds a matching entry (by source + skill) and merges
 * the Tier1 fields onto it. Results that don't match an existing entry are
 * appended. The file is rewritten atomically.
 */
export function mergeTier1Results(catalogPath: string, results: Tier1Result[]): void {
  // Read existing entries — tolerant of missing file
  const existing: CatalogEntryWithTier1[] = []
  if (existsSync(catalogPath)) {
    const content = readFileSync(catalogPath, 'utf8')
    for (const line of content.split('\n')) {
      const trimmed = line.trim()
      if (!trimmed) continue
      try {
        existing.push(JSON.parse(trimmed) as CatalogEntryWithTier1)
      } catch {
        // skip malformed lines
      }
    }
  }

  // Build a lookup index: "source\0skill" → index in existing array
  const index = new Map<string, number>()
  for (let i = 0; i < existing.length; i++) {
    const key = `${existing[i].source}\0${existing[i].skill}`
    index.set(key, i)
  }

  // Merge or append each result
  for (const result of results) {
    const key = `${result.source}\0${result.skill}`
    const idx = index.get(key)

    if (idx !== undefined) {
      // Merge Tier1 fields into existing entry
      existing[idx] = { ...existing[idx], ...result }
    } else {
      // New entry — create a minimal CatalogEntry + Tier1 fields
      const newEntry: CatalogEntryWithTier1 = {
        source: result.source,
        skill: result.skill,
        availability: 'available', // if we got T1 results, it was available
        ...result,
      }
      existing.push(newEntry)
      index.set(key, existing.length - 1)
    }
  }

  // Write back atomically: write to temp file, then rename
  const tmpPath = `${catalogPath}.tmp`
  const lines = `${existing.map((e) => JSON.stringify(e)).join('\n')}\n`
  writeFileSync(tmpPath, lines, 'utf8')
  renameSync(tmpPath, catalogPath)
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
    for (const r of repos.slice(0, 10)) console.log(`  ${r}`)
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

// Run when executed directly (not when imported as a module)
const isDirectExecution =
  import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('/catalog.ts')

if (isDirectExecution) {
  main().catch((err) => {
    console.error('Fatal error:', err)
    process.exit(1)
  })
}
