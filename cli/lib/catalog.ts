#!/usr/bin/env bun
/**
 * catalog.ts — Phase 2: Availability Check
 *
 * Reads content/skills/.TODO.yaml (entries in format `org/repo@skill-name`),
 * checks GitHub availability for each unique repo via HTTP HEAD, and writes
 * one NDJSON line per entry to content/skills/.catalog.ndjson.
 *
 * Usage:
 *   bun run cli/lib/catalog.ts
 *   bun run cli/lib/catalog.ts --concurrency 20 --delay 500
 *   bun run cli/lib/catalog.ts --dry-run
 *   bun run cli/lib/catalog.ts --resume
 *
 * Environment:
 *   GITHUB_TOKEN   Optional. Uses authenticated rate limit (5000/hr vs 60/min).
 *
 * .TODO.yaml format:
 *   Each line is either:
 *     - `org/repo@skill-name`   (standard entry — processed)
 *     - A URL, comment, or other text  (skipped)
 *
 * Output: content/skills/.catalog.ndjson
 *   One JSON line per .TODO.yaml entry:
 *   {"source":"org/repo","skill":"skill-name","availability":"available"}
 */

import { createWriteStream, existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { currentDir } from './runtime'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AvailabilityStatus =
  | 'available'
  | 'archived'
  | 'not_found'
  | 'private'
  | 'error'
  | 'removed_from_repo'

export interface CatalogEntry {
  source: string // org/repo
  skill: string // skill name (part after @)
  availability: AvailabilityStatus
}

// ---------------------------------------------------------------------------
// Repo Manifest (per-repo metadata from discovery)
// ---------------------------------------------------------------------------

/** A single heading with its line number for section-level navigation. */
export interface SectionMapEntry {
  heading: string
  line: number
  depth: number
}

/**
 * Repo-level metadata captured during discovery.
 * Stored in `.catalog-repos.ndjson` (gitignored).
 */
export interface RepoManifest {
  /** owner/repo identifier */
  repo: string
  /** ISO timestamp of last clone/discovery */
  clonedAt: string
  /** Git HEAD SHA at time of clone */
  headSha: string
  /** Total file count in repo */
  totalFiles: number
  /** Repo size in bytes */
  repoSizeBytes: number
  /** Whether the repo is archived on GitHub */
  archived: boolean
  /** ISO timestamp of most recent commit */
  lastCommitAt?: string
  /** Total number of commits */
  commitCount?: number
  /** Number of unique contributors */
  contributorCount?: number
  /** Number of skills discovered in this repo */
  skillCount: number
  /** Names of discovered skills */
  skills: string[]
}

// ---------------------------------------------------------------------------
// Component Metadata (per-skill enrichment from discovery)
// ---------------------------------------------------------------------------

/**
 * Metadata computed per-component during repo discovery.
 * These fields are added to Tier1Result and stored on catalog entries.
 * All fields are optional — entries from before discovery won't have them.
 */
export interface ComponentMetadata {
  /** Actual path where SKILL.md was found (e.g., "content/skills/foo") */
  discoveredPath?: string
  /** ISO timestamp when this skill was last seen in a discovery run */
  lastSeenAt?: string
  /** HEAD SHA of the repo when skill was last seen */
  lastSeenHeadSha?: string
  /** Previous discoveredPath if the skill was moved */
  movedFrom?: string
  /** Total size of the skill directory in bytes */
  skillSizeBytes?: number
  /** Line count of SKILL.md */
  lineCount?: number
  /** Section map: heading text + line number for navigation */
  sectionMap?: SectionMapEntry[]
  /** All files in the skill directory (relative paths) */
  fileTree?: string[]
  /** True if skill directory contains only SKILL.md (no resources, no subdirs) */
  isSimple?: boolean
}

// ---------------------------------------------------------------------------
// Availability Check
// ---------------------------------------------------------------------------

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
const TODO_YAML_PATH = join(REPO_ROOT, 'content', 'skills', '.TODO.yaml')
const CATALOG_PATH = join(REPO_ROOT, 'content', 'skills', '.catalog.ndjson')

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

export type Tier1ErrorType =
  | 'download_failed'
  | 'download_timeout'
  | 'analysis_failed'
  | 'analysis_timeout'
  | 'rate_limited'
  | 'batch_failed'
  | 'invalid_source_entry'

export interface Tier1Result extends ComponentMetadata {
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
  treeSha?: string // git tree SHA of the skill folder (for stale detection)
  tier2Reviewed?: boolean
  // Error cache fields (detail lives in error log)
  attemptCount?: number
  lastErrorType?: Tier1ErrorType
  retryable?: boolean
  possibleForkOf?: string
  runId?: string
  batchId?: string
  analyzedAt?: string
}

// ---------------------------------------------------------------------------
// Error Log — Types + Functions (ADR-019)
// ---------------------------------------------------------------------------

export interface ErrorRecord {
  source: string
  skill: string
  runId: string
  batchId: string
  timestamp: string
  errorType: Tier1ErrorType
  errorDetail: string
  errorCode?: number
  retryable: boolean
}

/**
 * Append a single error record to the error log (NDJSON).
 */
export function appendError(errorLogPath: string, record: ErrorRecord): void {
  const line = `${JSON.stringify(record)}\n`
  const { appendFileSync } = require('node:fs')
  appendFileSync(errorLogPath, line, 'utf8')
}

/**
 * Append multiple error records in a single write (concurrent-safe).
 * Concatenates all lines into one string and writes atomically.
 */
export function appendErrors(errorLogPath: string, records: ErrorRecord[]): void {
  if (records.length === 0) return
  const data = `${records.map((r) => JSON.stringify(r)).join('\n')}\n`
  const { appendFileSync } = require('node:fs')
  appendFileSync(errorLogPath, data, 'utf8')
}

/**
 * Read all error records from the error log.
 */
export function readErrorLog(errorLogPath: string): ErrorRecord[] {
  if (!existsSync(errorLogPath)) return []
  const content = readFileSync(errorLogPath, 'utf8')
  const records: ErrorRecord[] = []
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      records.push(JSON.parse(trimmed) as ErrorRecord)
    } catch {
      // skip malformed lines
    }
  }
  return records
}

/**
 * Get error records for a specific skill.
 */
export function getErrorsForSkill(
  errorLogPath: string,
  source: string,
  skill: string
): ErrorRecord[] {
  return readErrorLog(errorLogPath).filter((r) => r.source === source && r.skill === skill)
}

// ---------------------------------------------------------------------------
// Mechanical Compute Functions (ADR-021)
// ---------------------------------------------------------------------------

/**
 * Compute SHA-256 content hash of a string.
 * Returns `sha256:<hex>` format.
 */
export function computeContentHash(content: string): string {
  const { createSha256Hasher } = require('./runtime') as typeof import('./runtime')
  const hasher = createSha256Hasher()
  hasher.update(content)
  return `sha256:${hasher.digest('hex')}`
}

/**
 * Count words in content by splitting on whitespace.
 */
export function computeWordCount(content: string): number {
  const trimmed = content.trim()
  if (!trimmed) return 0
  return trimmed.split(/\s+/).length
}

/**
 * Count markdown sections (lines starting with # through ######).
 */
export function computeSectionCount(content: string): number {
  let count = 0
  for (const line of content.split('\n')) {
    if (/^#{1,6}\s/.test(line)) count++
  }
  return count
}

/**
 * Extract heading tree from markdown content.
 * Returns array of {depth, title} for each heading.
 */
export function computeHeadingTree(content: string): Array<{ depth: number; title: string }> {
  const tree: Array<{ depth: number; title: string }> = []
  for (const line of content.split('\n')) {
    const match = line.match(/^(#{1,6})\s+(.+)$/)
    if (match) {
      tree.push({ depth: match[1].length, title: match[2].trim() })
    }
  }
  return tree
}

/**
 * Count files recursively in a directory.
 * Returns 0 for nonexistent directories.
 */
export function computeFileCount(dir: string): number {
  const { readdirSync } = require('node:fs')
  try {
    let count = 0
    const entries = readdirSync(dir, { withFileTypes: true })
    for (const entry of entries) {
      if (entry.isFile()) {
        count++
      } else if (entry.isDirectory()) {
        count += computeFileCount(join(dir, entry.name))
      }
    }
    return count
  } catch {
    return 0
  }
}

// ---------------------------------------------------------------------------
// Component Metadata Compute Functions
// ---------------------------------------------------------------------------

/**
 * Compute a section map: heading text + line number for navigation.
 */
export function computeSectionMap(content: string): SectionMapEntry[] {
  const entries: SectionMapEntry[] = []
  const lines = content.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^(#{1,6})\s+(.+)$/)
    if (match) {
      entries.push({ heading: match[2].trim(), line: i + 1, depth: match[1].length })
    }
  }
  return entries
}

/**
 * Count lines in content.
 */
export function computeLineCount(content: string): number {
  if (!content) return 0
  return content.split('\n').length
}

/**
 * List all files in a directory recursively (relative paths).
 * Returns empty array for nonexistent directories.
 */
export function computeFileTree(dir: string): string[] {
  const { readdirSync, statSync } = require('node:fs') as typeof import('node:fs')
  const { relative } = require('node:path') as typeof import('node:path')
  const files: string[] = []
  try {
    function walk(current: string): void {
      for (const entry of readdirSync(current, { withFileTypes: true })) {
        const full = join(current, entry.name)
        if (entry.isFile()) {
          files.push(relative(dir, full))
        } else if (entry.isDirectory() && entry.name !== '.git' && entry.name !== 'node_modules') {
          walk(full)
        }
      }
    }
    walk(dir)
  } catch {
    /* nonexistent dir */
  }
  return files.sort()
}

/**
 * Compute total size of a directory in bytes.
 * Returns 0 for nonexistent directories.
 */
export function computeSkillSizeBytes(dir: string): number {
  const { statSync, readdirSync } = require('node:fs') as typeof import('node:fs')
  try {
    let total = 0
    function walk(current: string): void {
      for (const entry of readdirSync(current, { withFileTypes: true })) {
        const full = join(current, entry.name)
        if (entry.isFile()) {
          total += statSync(full).size
        } else if (entry.isDirectory() && entry.name !== '.git') {
          walk(full)
        }
      }
    }
    walk(dir)
    return total
  } catch {
    return 0
  }
}

/**
 * Check if a skill is "simple" — directory contains only SKILL.md.
 * No resources, no subdirectories, no additional files.
 */
export function isSimpleSkill(dir: string): boolean {
  const { readdirSync } = require('node:fs') as typeof import('node:fs')
  try {
    const entries = readdirSync(dir, { withFileTypes: true })
    return entries.length === 1 && entries[0].isFile() && entries[0].name === 'SKILL.md'
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// Keyword Extraction (Mechanical)
// ---------------------------------------------------------------------------

const STOP_WORDS = new Set([
  'a',
  'an',
  'the',
  'and',
  'or',
  'but',
  'in',
  'on',
  'at',
  'to',
  'for',
  'of',
  'with',
  'by',
  'from',
  'is',
  'are',
  'was',
  'were',
  'be',
  'been',
  'being',
  'have',
  'has',
  'had',
  'do',
  'does',
  'did',
  'will',
  'would',
  'could',
  'should',
  'may',
  'might',
  'shall',
  'can',
  'not',
  'no',
  'nor',
  'so',
  'if',
  'then',
  'than',
  'that',
  'this',
  'these',
  'those',
  'it',
  'its',
  'as',
  'up',
  'out',
  'about',
  'into',
  'over',
  'after',
  'before',
  'between',
  'under',
  'above',
  'such',
  'each',
  'every',
  'all',
  'any',
  'both',
  'few',
  'more',
  'most',
  'other',
  'some',
  'only',
  'own',
  'same',
  'how',
  'what',
  'when',
  'where',
  'which',
  'who',
  'whom',
  'why',
  'use',
  'using',
  'used',
  'also',
  'just',
  'like',
  'make',
  'get',
])

/**
 * Extract keywords mechanically from markdown content.
 *
 * Sources (in priority order):
 * 1. Heading titles (h1-h3) — split into individual terms
 * 2. Frontmatter description — significant terms
 * 3. Code fence language identifiers (e.g., typescript, python, rust)
 *
 * Filters stop words, deduplicates, lowercases.
 */
export function extractKeywords(content: string): string[] {
  const terms = new Set<string>()

  // 1. Headings (h1-h3 only — deeper headings are too specific)
  for (const line of content.split('\n')) {
    const match = line.match(/^#{1,3}\s+(.+)$/)
    if (match) {
      for (const word of tokenize(match[1])) {
        terms.add(word)
      }
    }
  }

  // 2. Frontmatter description
  const descMatch = content.match(/^---[\s\S]*?description:\s*(.+?)$/m)
  if (descMatch) {
    for (const word of tokenize(descMatch[1])) {
      terms.add(word)
    }
  }

  // 3. Code fence languages
  for (const match of content.matchAll(/^```(\w+)/gm)) {
    const lang = match[1].toLowerCase()
    if (lang !== 'text' && lang !== 'markdown' && lang !== 'md' && lang !== 'plaintext') {
      terms.add(lang)
    }
  }

  return [...terms].slice(0, 30) // cap at 30 keywords
}

/** Tokenize a string into lowercase terms, filtering stop words and short tokens. */
function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP_WORDS.has(w))
}

/** CatalogEntry extended with optional Tier1 analysis fields. */
export type CatalogEntryWithTier1 = CatalogEntry & Partial<Tier1Result>

// ---------------------------------------------------------------------------
// Incremental Processing Filter
// ---------------------------------------------------------------------------

export interface FilterProcessingOpts {
  force?: boolean
  retryErrors?: boolean
}

/**
 * Filter catalog entries to determine which should be processed.
 *
 * Default: unattempted available entries + retryable under attempt limit.
 * --force: all available entries regardless of state.
 * --retry-errors: only retryable entries with attemptCount > 0.
 * --retry-errors --force: all errored entries, ignoring attempt limits.
 */
export function filterForProcessing(
  entries: CatalogEntryWithTier1[],
  opts: FilterProcessingOpts = {}
): CatalogEntryWithTier1[] {
  const MAX_ATTEMPTS = 2

  // First: only available entries
  const available = entries.filter((e) => e.availability === 'available')

  if (opts.force && !opts.retryErrors) {
    return available
  }

  if (opts.retryErrors) {
    // Only entries that have been attempted before
    const errored = available.filter((e) => (e.attemptCount ?? 0) > 0)
    if (opts.force) {
      return errored
    }
    // Respect attempt limit and retryable flag
    return errored.filter((e) => e.retryable !== false && (e.attemptCount ?? 0) < MAX_ATTEMPTS)
  }

  // Default: unattempted entries + retryable under attempt limit
  return available.filter((e) => {
    const attempts = e.attemptCount ?? 0
    const hasData = e.wordCount != null

    // Already analyzed successfully and no errors — skip
    if (hasData && attempts === 0) return false

    // Never attempted — include
    if (attempts === 0) return true

    // Attempted but retryable and under limit — include
    if (e.retryable !== false && attempts < MAX_ATTEMPTS) return true

    return false
  })
}

// ---------------------------------------------------------------------------
// Batch Validation
// ---------------------------------------------------------------------------

export interface ValidationReport {
  total: number
  missingContentHash: number
  pendingContentHash: number
  missingWordCount: number
  missingKeywords: number
  issues: string[]
}

/**
 * Validate a batch of Tier1Results for common issues.
 * Called after merge to catch quality problems early.
 */
export function validateBatchResults(results: Tier1Result[]): ValidationReport {
  const successes = results.filter((r) => r.wordCount != null)
  const report: ValidationReport = {
    total: successes.length,
    missingContentHash: 0,
    pendingContentHash: 0,
    missingWordCount: 0,
    missingKeywords: 0,
    issues: [],
  }

  for (const r of successes) {
    if (!r.contentHash) {
      report.missingContentHash++
      report.issues.push(`${r.source}@${r.skill}: missing contentHash`)
    } else if (r.contentHash === 'sha256:pending' || r.contentHash.includes('pending')) {
      report.pendingContentHash++
      report.issues.push(`${r.source}@${r.skill}: pending contentHash`)
    }
    if (r.wordCount == null) {
      report.missingWordCount++
    }
    if (!r.keywords || r.keywords.length === 0) {
      report.missingKeywords++
      report.issues.push(`${r.source}@${r.skill}: missing keywords`)
    }
  }

  return report
}

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

// ---------------------------------------------------------------------------
// Repo Manifest I/O
// ---------------------------------------------------------------------------

/**
 * Read repo manifests from an NDJSON file.
 * Returns empty array if file doesn't exist.
 */
export function readRepoManifest(path: string): RepoManifest[] {
  if (!existsSync(path)) return []
  const content = readFileSync(path, 'utf8')
  const manifests: RepoManifest[] = []
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      manifests.push(JSON.parse(trimmed) as RepoManifest)
    } catch {
      /* skip malformed lines */
    }
  }
  return manifests
}

/**
 * Write repo manifests to an NDJSON file (atomic: write tmp then rename).
 */
export function writeRepoManifest(path: string, manifests: RepoManifest[]): void {
  const tmpPath = `${path}.tmp`
  const lines = `${manifests.map((m) => JSON.stringify(m)).join('\n')}\n`
  writeFileSync(tmpPath, lines, 'utf8')
  renameSync(tmpPath, path)
}

/**
 * Merge a single repo manifest into an existing manifest file.
 * Updates existing entry by repo name or appends new.
 */
export function mergeRepoManifest(path: string, manifest: RepoManifest): void {
  const existing = readRepoManifest(path)
  const idx = existing.findIndex((m) => m.repo === manifest.repo)
  if (idx >= 0) {
    existing[idx] = manifest
  } else {
    existing.push(manifest)
  }
  writeRepoManifest(path, existing)
}

/**
 * Migrate catalog entries: rename `source_invalid` → `invalid_source_entry`.
 * Idempotent — safe to run multiple times.
 */
export function migrateCatalogSchema(catalogPath: string): number {
  if (!existsSync(catalogPath)) return 0
  const entries = readCatalogEntries(catalogPath)
  let migrated = 0
  for (const entry of entries) {
    const e = entry as Record<string, unknown>
    if (e.lastErrorType === 'source_invalid') {
      e.lastErrorType = 'invalid_source_entry'
      migrated++
    }
  }
  if (migrated > 0) {
    const tmpPath = `${catalogPath}.tmp`
    const lines = `${entries.map((e) => JSON.stringify(e)).join('\n')}\n`
    writeFileSync(tmpPath, lines, 'utf8')
    renameSync(tmpPath, catalogPath)
  }
  return migrated
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

/** Internal fields used during processing but not persisted to catalog. */
interface TransientErrorFields {
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  errorCode?: number
}

/**
 * Tier1Result extended with transient error fields from the orchestrator.
 * These fields are used internally by mergeTier1Results to route errors
 * to the error log — they are NOT written to the catalog.
 */
export type Tier1ResultWithTransient = Tier1Result & TransientErrorFields

/**
 * Merge Tier1Result fields into an existing `.catalog.ndjson` file.
 * Routes successes to the catalog and failures to the error log.
 *
 * This is the single authority for catalog + error log state coordination.
 * - Successes (have wordCount): merge into catalog, clear error cache, reset attemptCount
 * - Failures (no wordCount, have error): append ErrorRecord to log, increment attemptCount
 */
export function mergeTier1Results(
  catalogPath: string,
  errorLogPath: string,
  results: Tier1ResultWithTransient[]
): void {
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

  // Split results into successes and failures
  const errorRecords: ErrorRecord[] = []

  for (const result of results) {
    const key = `${result.source}\0${result.skill}`
    const idx = index.get(key)
    const isSuccess = result.wordCount != null && !result.error

    if (isSuccess) {
      // Success: merge data, clear error cache, reset attemptCount
      const {
        error: _e,
        errorType: _et,
        errorDetail: _ed,
        errorCode: _ec,
        ...cleanResult
      } = result as TransientErrorFields & Tier1Result
      const merged: Partial<CatalogEntryWithTier1> = {
        ...cleanResult,
        attemptCount: 0,
        lastErrorType: undefined,
        retryable: undefined,
      }

      if (idx !== undefined) {
        // Strip old error fields from existing entry too
        const entry = existing[idx]
        delete (entry as Record<string, unknown>).error
        delete (entry as Record<string, unknown>).errorDetail
        delete (entry as Record<string, unknown>).errorCode
        existing[idx] = { ...entry, ...merged }
      } else {
        existing.push({
          source: result.source,
          skill: result.skill,
          availability: 'available',
          ...merged,
        } as CatalogEntryWithTier1)
        index.set(key, existing.length - 1)
      }
    } else if (result.error) {
      // Failure: build error record for error log
      const errorType = result.errorType ?? ('batch_failed' as Tier1ErrorType)
      errorRecords.push({
        source: result.source,
        skill: result.skill,
        runId: result.runId ?? '',
        batchId: result.batchId ?? '',
        timestamp: result.analyzedAt ?? new Date().toISOString(),
        errorType,
        errorDetail: result.errorDetail ?? result.error ?? '',
        errorCode: result.errorCode,
        retryable: result.retryable ?? false,
      })

      // Update catalog entry with error cache fields
      const prevAttemptCount = idx !== undefined ? (existing[idx].attemptCount ?? 0) : 0
      const catalogUpdate: Partial<CatalogEntryWithTier1> = {
        attemptCount: prevAttemptCount + 1,
        lastErrorType: errorType,
        retryable: result.retryable ?? false,
        runId: result.runId,
        batchId: result.batchId,
        analyzedAt: result.analyzedAt,
      }

      if (idx !== undefined) {
        // Strip old error fields
        const entry = existing[idx]
        delete (entry as Record<string, unknown>).error
        delete (entry as Record<string, unknown>).errorDetail
        delete (entry as Record<string, unknown>).errorCode
        existing[idx] = { ...entry, ...catalogUpdate }
      } else {
        existing.push({
          source: result.source,
          skill: result.skill,
          availability: 'available',
          ...catalogUpdate,
        } as CatalogEntryWithTier1)
        index.set(key, existing.length - 1)
      }
    }
  }

  // Append errors to error log
  if (errorRecords.length > 0) {
    appendErrors(errorLogPath, errorRecords)
  }

  // Write catalog back atomically: write to temp file, then rename
  const tmpPath = `${catalogPath}.tmp`
  const lines = `${existing.map((e) => JSON.stringify(e)).join('\n')}\n`
  writeFileSync(tmpPath, lines, 'utf8')
  renameSync(tmpPath, catalogPath)
}

/**
 * Merge backfill results into catalog — fills missing fields only.
 *
 * Unlike `mergeTier1Results`, this does NOT overwrite existing data.
 * For each entry, only undefined/null fields are filled from the backfill result.
 * Error entries with `lastErrorType === 'batch_failed'` are reclassified
 * if the backfill provides a more specific error type.
 */
export function mergeBackfillResults(
  catalogPath: string,
  errorLogPath: string,
  results: BackfillResult[]
): { updated: number; reclassified: number; failed: number } {
  const existing: CatalogEntryWithTier1[] = []
  if (existsSync(catalogPath)) {
    const content = readFileSync(catalogPath, 'utf8')
    for (const line of content.split('\n')) {
      const trimmed = line.trim()
      if (!trimmed) continue
      try {
        existing.push(JSON.parse(trimmed) as CatalogEntryWithTier1)
      } catch {
        /* skip */
      }
    }
  }

  const index = new Map<string, number>()
  for (let i = 0; i < existing.length; i++) {
    index.set(`${existing[i].source}\0${existing[i].skill}`, i)
  }

  let updated = 0
  let reclassified = 0
  let failed = 0
  const errorRecords: ErrorRecord[] = []

  for (const result of results) {
    const key = `${result.source}\0${result.skill}`
    const idx = index.get(key)
    if (idx === undefined) continue // entry not in catalog

    const entry = existing[idx]

    if (result.error) {
      // Reclassify batch_failed → more specific type
      if (
        entry.lastErrorType === 'batch_failed' &&
        result.errorType &&
        result.errorType !== 'batch_failed'
      ) {
        entry.lastErrorType = result.errorType
        entry.retryable = result.errorType === 'download_timeout'
        reclassified++
        errorRecords.push({
          source: result.source,
          skill: result.skill,
          runId: result.runId ?? '',
          batchId: '',
          timestamp: new Date().toISOString(),
          errorType: result.errorType,
          errorDetail: result.errorDetail ?? result.error,
          retryable: result.errorType === 'download_timeout',
        })
      }
      failed++
      continue
    }

    // Fill missing fields only (null, undefined, or empty arrays)
    let changed = false
    const fillFields: (keyof Tier1Result)[] = [
      'headingTree',
      'treeSha',
      'keywords',
      'fileCount',
      'sectionCount',
    ]
    for (const field of fillFields) {
      const current = entry[field]
      const isEmpty = current == null || (Array.isArray(current) && current.length === 0)
      if (isEmpty && result[field] != null) {
        ;(entry as Record<string, unknown>)[field] = result[field]
        changed = true
      }
    }
    if (changed) updated++
  }

  if (errorRecords.length > 0) {
    appendErrors(errorLogPath, errorRecords)
  }

  const tmpPath = `${catalogPath}.tmp`
  const lines = `${existing.map((e) => JSON.stringify(e)).join('\n')}\n`
  writeFileSync(tmpPath, lines, 'utf8')
  renameSync(tmpPath, catalogPath)

  return { updated, reclassified, failed }
}

/** Result from a backfill operation — partial fields only. */
export interface BackfillResult {
  source: string
  skill: string
  headingTree?: Array<{ depth: number; title: string }>
  treeSha?: string
  keywords?: string[]
  fileCount?: number
  sectionCount?: number
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  runId?: string
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
