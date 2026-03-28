/**
 * Catalog I/O functions for the pipeline.
 *
 * Reading/writing catalog NDJSON files, error logs, repo manifests,
 * and data transformation (merge, backfill, parsing).
 */

import { createWriteStream, existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import type {
  BackfillResult,
  CatalogEntry,
  CatalogEntryWithTier1,
  ErrorRecord,
  RepoManifest,
  Tier1ErrorType,
  Tier1Result,
  Tier1ResultWithTransient,
} from './types'

// ---------------------------------------------------------------------------
// TODO.yaml Parsing
// ---------------------------------------------------------------------------

/**
 * Parse a single .TODO.yaml line.
 * Returns {source, skill} if the line matches `org/repo@skill-name`,
 * otherwise returns null (to be skipped).
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
// Catalog NDJSON Read/Write
// ---------------------------------------------------------------------------

/**
 * Write catalog entries to the output file incrementally.
 * Opens file in append mode so partial runs are resumable.
 */
export function writeCatalogEntries(entries: CatalogEntry[], outputPath: string): void {
  const stream = createWriteStream(outputPath, { flags: 'a', encoding: 'utf8' })
  for (const entry of entries) {
    stream.write(`${JSON.stringify(entry)}\n`)
  }
  stream.end()
}

/**
 * Read catalog entries from an NDJSON file.
 */
export function readCatalog(path: string): CatalogEntry[] {
  const result: CatalogEntry[] = []
  const content = readFileSync(path, 'utf8')
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

/**
 * Load already-processed repos from an existing .catalog.ndjson file.
 * Returns a Set of "source" values (org/repo) that are already present.
 */
export function loadProcessedRepos(catalogPath: string): Set<string> {
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
// Error Log Functions (ADR-019)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Tier1 Result Parsing / Merging
// ---------------------------------------------------------------------------

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

  // Build a lookup index: "source\0skill" -> index in existing array
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
      } = result as Tier1ResultWithTransient
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
      // Reclassify batch_failed -> more specific type
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

// ---------------------------------------------------------------------------
// Filtering / Batching / Helpers
// ---------------------------------------------------------------------------

/**
 * Filter catalog entries to only those with `availability === 'available'`.
 */
export function filterAvailable(entries: CatalogEntry[]): CatalogEntry[] {
  return entries.filter((e) => e.availability === 'available')
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
  opts: { force?: boolean; retryErrors?: boolean } = {}
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

/**
 * Validate a batch of Tier1Results for common issues.
 * Called after merge to catch quality problems early.
 */
export function validateBatchResults(results: Tier1Result[]): {
  total: number
  missingContentHash: number
  pendingContentHash: number
  missingWordCount: number
  missingKeywords: number
  issues: string[]
} {
  const successes = results.filter((r) => r.wordCount != null)
  const report = {
    total: successes.length,
    missingContentHash: 0,
    pendingContentHash: 0,
    missingWordCount: 0,
    missingKeywords: 0,
    issues: [] as string[],
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

/**
 * Split entries into batches of `batchSize`, grouping by `source` to
 * minimize the number of distinct repo downloads per batch.
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
 * Detect possible forks by comparing contentHash values among entries
 * sharing the same skill name. Entries with identical hashes are marked
 * with `possibleForkOf` pointing to the first-seen source for that hash.
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
  for (const group of bySkill.values()) {
    if (group.length <= 1) continue

    const hashToFirstSource = new Map<string, string>()

    for (const entry of group) {
      if (!entry.contentHash) continue

      const firstSource = hashToFirstSource.get(entry.contentHash)
      if (firstSource === undefined) {
        hashToFirstSource.set(entry.contentHash, entry.source)
      } else if (firstSource !== entry.source) {
        entry.possibleForkOf = firstSource
      }
    }
  }

  return results
}

/**
 * Migrate catalog entries: rename `source_invalid` -> `invalid_source_entry`.
 * Idempotent — safe to run multiple times.
 */
export function migrateCatalogSchema(catalogPath: string): number {
  if (!existsSync(catalogPath)) return 0
  const entries = readCatalog(catalogPath)
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
