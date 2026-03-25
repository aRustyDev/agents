/**
 * Catalog reconciliation engine.
 *
 * Matches discovery results against existing catalog entries to detect
 * moves, renames, additions, and removals. Pure functions — no I/O
 * (except applyReconciliation which writes atomically).
 */

import { readFileSync, renameSync, writeFileSync } from 'node:fs'
import type { CatalogEntryWithTier1, Tier1ErrorType } from './catalog'
import type { DiscoveredSkillResult, RepoDiscoveryResult } from './catalog-discover'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ReconciliationAction =
  | 'unchanged'
  | 'updated' // existing entry enriched with new mechanical data
  | 'moved' // same name, different discoveredPath
  | 'added' // found in repo but not in catalog
  | 'removed' // in catalog but not found in repo
  | 'renamed' // same path, different frontmatter name
  | 'error' // discovery failed for this repo

export interface ReconciliationEntry {
  source: string
  skill: string
  action: ReconciliationAction
  /** Previous path (for moves). */
  movedFrom?: string
  /** Previous name (for renames). */
  renamedFrom?: string
  /** New mechanical data (for updated/moved/added). */
  discovered?: DiscoveredSkillResult
  /** Error details (for error action). */
  error?: string
  errorType?: Tier1ErrorType
}

export interface ReconciliationReport {
  unchanged: ReconciliationEntry[]
  updated: ReconciliationEntry[]
  moved: ReconciliationEntry[]
  added: ReconciliationEntry[]
  removed: ReconciliationEntry[]
  renamed: ReconciliationEntry[]
  errors: ReconciliationEntry[]
}

// ---------------------------------------------------------------------------
// Core Reconciliation
// ---------------------------------------------------------------------------

/**
 * Reconcile discovery results against existing catalog entries.
 * Pure function — no I/O. Takes data in, returns a report.
 *
 * Detection logic:
 * - **Move**: catalog entry exists, discovered skill has same frontmatter name
 *   but different discoveredPath than what's stored
 * - **Addition**: discovered skill has no matching catalog entry
 * - **Removal**: catalog entry exists but skill not found in discovery
 * - **Rename**: discovered skill at same path as catalog entry but different name
 * - **Updated**: catalog entry exists, skill found, path matches — enrich with new data
 * - **Move+Rename**: different name AND different path — treated as removal + addition
 *   unless contentHash matches (then it's a move with analysis data preserved)
 */
export function reconcile(
  catalogEntries: CatalogEntryWithTier1[],
  discoveryResults: RepoDiscoveryResult[]
): ReconciliationReport {
  const report: ReconciliationReport = {
    unchanged: [],
    updated: [],
    moved: [],
    added: [],
    removed: [],
    renamed: [],
    errors: [],
  }

  // Build lookup: source → { skill → catalogEntry }
  const catalogBySource = new Map<string, Map<string, CatalogEntryWithTier1>>()
  for (const entry of catalogEntries) {
    if (!catalogBySource.has(entry.source)) {
      catalogBySource.set(entry.source, new Map())
    }
    catalogBySource.get(entry.source)?.set(entry.skill.toLowerCase(), entry)
  }

  for (const result of discoveryResults) {
    const source = result.manifest.repo
    const catalogSkills = catalogBySource.get(source) ?? new Map()

    // Track which catalog entries were matched
    const matched = new Set<string>()

    // Process errors
    for (const err of result.errors) {
      report.errors.push({
        source: err.source,
        skill: '',
        action: 'error',
        error: err.error,
        errorType: err.errorType,
      })
    }

    // Process discovered skills
    for (const disc of result.skills) {
      const nameKey = disc.skill.toLowerCase()
      const catalogEntry = catalogSkills.get(nameKey)

      if (catalogEntry) {
        matched.add(nameKey)

        // Check for move (same name, different path)
        const oldPath = catalogEntry.discoveredPath
        const newPath = disc.mechanical.discoveredPath
        if (oldPath && newPath && oldPath !== newPath) {
          report.moved.push({
            source,
            skill: disc.skill,
            action: 'moved',
            movedFrom: oldPath,
            discovered: disc,
          })
        } else {
          // Same name, same path (or no previous path) — update
          report.updated.push({
            source,
            skill: disc.skill,
            action: 'updated',
            discovered: disc,
          })
        }
      } else {
        // Check for rename: is there a catalog entry at the same discoveredPath with a different name?
        const renamedFrom = findRenameCandidate(catalogSkills, disc, matched)
        if (renamedFrom) {
          matched.add(renamedFrom.toLowerCase())
          report.renamed.push({
            source,
            skill: disc.skill,
            action: 'renamed',
            renamedFrom,
            discovered: disc,
          })
        } else {
          // New skill not in catalog
          report.added.push({
            source,
            skill: disc.skill,
            action: 'added',
            discovered: disc,
          })
        }
      }
    }

    // Catalog entries not matched = removed from repo
    for (const [nameKey, entry] of catalogSkills) {
      if (!matched.has(nameKey) && entry.availability === 'available') {
        // Only mark as removed if this repo was successfully cloned (no errors)
        if (result.errors.length === 0) {
          report.removed.push({
            source,
            skill: entry.skill,
            action: 'removed',
          })
        }
      }
    }
  }

  return report
}

/**
 * Check if a discovered skill is a rename of an existing catalog entry.
 * A rename = same discoveredPath, different frontmatter name.
 */
function findRenameCandidate(
  catalogSkills: Map<string, CatalogEntryWithTier1>,
  disc: DiscoveredSkillResult,
  alreadyMatched: Set<string>
): string | null {
  const newPath = disc.mechanical.discoveredPath
  if (!newPath) return null

  for (const [nameKey, entry] of catalogSkills) {
    if (alreadyMatched.has(nameKey)) continue
    if (entry.discoveredPath === newPath) {
      return entry.skill // this entry was at the same path but has a different name
    }
  }
  return null
}

// ---------------------------------------------------------------------------
// Move+Rename with contentHash Preservation
// ---------------------------------------------------------------------------

/**
 * For entries classified as "added" + "removed" from the same source,
 * check if they share a contentHash. If so, reclassify as a move
 * and preserve the analysis data from the old entry.
 *
 * Call this after reconcile() to refine the report.
 */
export function detectMoveRenames(
  report: ReconciliationReport,
  catalogEntries: CatalogEntryWithTier1[]
): void {
  if (report.added.length === 0 || report.removed.length === 0) return

  // Build lookup: source → removed entries with contentHash
  const removedBySource = new Map<string, ReconciliationEntry[]>()
  for (const entry of report.removed) {
    const group = removedBySource.get(entry.source) ?? []
    group.push(entry)
    removedBySource.set(entry.source, group)
  }

  const promotedToMove: Set<ReconciliationEntry> = new Set()
  const demotedFromRemoved: Set<ReconciliationEntry> = new Set()

  for (const added of report.added) {
    const removedInSameRepo = removedBySource.get(added.source) ?? []
    if (removedInSameRepo.length === 0) continue

    const addedHash = added.discovered?.mechanical.contentHash
    if (!addedHash) continue

    // Find a removed entry with matching contentHash
    for (const removed of removedInSameRepo) {
      if (demotedFromRemoved.has(removed)) continue
      const catalogEntry = catalogEntries.find(
        (e) => e.source === removed.source && e.skill === removed.skill
      )
      if (catalogEntry?.contentHash === addedHash) {
        // Same content, different name/path = move+rename
        promotedToMove.add(added)
        demotedFromRemoved.add(removed)

        report.moved.push({
          source: added.source,
          skill: added.skill,
          action: 'moved',
          movedFrom: catalogEntry.discoveredPath,
          renamedFrom: removed.skill,
          discovered: added.discovered,
        })
        break
      }
    }
  }

  // Remove promoted entries from added/removed lists
  report.added = report.added.filter((e) => !promotedToMove.has(e))
  report.removed = report.removed.filter((e) => !demotedFromRemoved.has(e))
}

// ---------------------------------------------------------------------------
// Apply Reconciliation — write changes back to catalog
// ---------------------------------------------------------------------------

/**
 * Apply reconciliation results to an existing catalog NDJSON file.
 *
 * - **added**: inserts new entries with mechanical data from discovery
 * - **removed**: marks entries as `removed_from_repo`
 * - **updated/moved**: refreshes mechanical fields from discovery
 * - **renamed**: updates skill name + mechanical fields, preserves analysis data
 *
 * Writes atomically (tmp + rename). Does not modify the NDJSON format.
 */
export function applyReconciliation(
  catalogPath: string,
  report: ReconciliationReport,
  discoveryResults: DiscoveredSkillResult[]
): { added: number; removed: number; updated: number; moved: number } {
  // Read existing catalog
  const existing: CatalogEntryWithTier1[] = []
  const content = readFileSync(catalogPath, 'utf8')
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      existing.push(JSON.parse(trimmed) as CatalogEntryWithTier1)
    } catch {
      /* skip malformed lines */
    }
  }

  // Build index: "source\0skill" → index
  const index = new Map<string, number>()
  for (let i = 0; i < existing.length; i++) {
    index.set(`${existing[i].source}\0${existing[i].skill}`, i)
  }

  // Build discovery lookup for fast access
  const discoveryMap = new Map<string, DiscoveredSkillResult>()
  for (const d of discoveryResults) {
    discoveryMap.set(`${d.source}:${d.skill}`, d)
  }

  const stats = { added: 0, removed: 0, updated: 0, moved: 0 }

  // Apply updates — refresh mechanical fields on existing entries
  for (const entry of report.updated) {
    const key = `${entry.source}\0${entry.skill}`
    const idx = index.get(key)
    if (idx === undefined || !entry.discovered) continue
    mergeMechanical(existing[idx], entry.discovered)
    stats.updated++
  }

  // Apply moves — update discoveredPath + mechanical fields
  for (const entry of report.moved) {
    const key = `${entry.source}\0${entry.skill}`
    const idx = index.get(key)
    if (idx === undefined || !entry.discovered) continue
    existing[idx].movedFrom = entry.movedFrom
    mergeMechanical(existing[idx], entry.discovered)
    stats.moved++
  }

  // Apply renames — update skill name, preserve analysis data
  for (const entry of report.renamed) {
    if (!entry.renamedFrom || !entry.discovered) continue
    const oldKey = `${entry.source}\0${entry.renamedFrom}`
    const idx = index.get(oldKey)
    if (idx === undefined) continue
    // Update the skill name
    existing[idx].skill = entry.skill
    mergeMechanical(existing[idx], entry.discovered)
    // Update index
    index.delete(oldKey)
    index.set(`${entry.source}\0${entry.skill}`, idx)
  }

  // Apply removals — mark as removed_from_repo
  for (const entry of report.removed) {
    const key = `${entry.source}\0${entry.skill}`
    const idx = index.get(key)
    if (idx === undefined) continue
    existing[idx].availability = 'removed_from_repo'
    stats.removed++
  }

  // Apply additions — create new entries with mechanical data
  for (const entry of report.added) {
    if (!entry.discovered) continue
    const newEntry: CatalogEntryWithTier1 = {
      source: entry.source,
      skill: entry.skill,
      availability: 'available',
      discoveredPath: entry.discovered.mechanical.discoveredPath,
      lastSeenAt: entry.discovered.mechanical.lastSeenAt,
      lastSeenHeadSha: entry.discovered.mechanical.lastSeenHeadSha,
      contentHash: entry.discovered.mechanical.contentHash,
      wordCount: entry.discovered.mechanical.wordCount,
      sectionCount: entry.discovered.mechanical.sectionCount,
      fileCount: entry.discovered.mechanical.fileCount,
      headingTree: entry.discovered.mechanical.headingTree,
      keywords: entry.discovered.mechanical.keywords,
      lineCount: entry.discovered.mechanical.lineCount,
      sectionMap: entry.discovered.mechanical.sectionMap,
      fileTree: entry.discovered.mechanical.fileTree,
      skillSizeBytes: entry.discovered.mechanical.skillSizeBytes,
      isSimple: entry.discovered.mechanical.isSimple,
      treeSha: entry.discovered.mechanical.treeSha,
    }
    existing.push(newEntry)
    index.set(`${entry.source}\0${entry.skill}`, existing.length - 1)
    stats.added++
  }

  // Write atomically: tmp + rename
  const tmpPath = `${catalogPath}.tmp`
  const lines = `${existing.map((e) => JSON.stringify(e)).join('\n')}\n`
  writeFileSync(tmpPath, lines, 'utf8')
  renameSync(tmpPath, catalogPath)

  return stats
}

/**
 * Merge mechanical fields from a discovered skill onto an existing catalog entry.
 * Overwrites only the deterministic fields — preserves LLM analysis data.
 */
function mergeMechanical(entry: CatalogEntryWithTier1, disc: DiscoveredSkillResult): void {
  entry.discoveredPath = disc.mechanical.discoveredPath
  entry.lastSeenAt = disc.mechanical.lastSeenAt
  entry.lastSeenHeadSha = disc.mechanical.lastSeenHeadSha
  entry.contentHash = disc.mechanical.contentHash
  entry.wordCount = disc.mechanical.wordCount
  entry.sectionCount = disc.mechanical.sectionCount
  entry.fileCount = disc.mechanical.fileCount
  entry.headingTree = disc.mechanical.headingTree
  entry.keywords = disc.mechanical.keywords
  entry.treeSha = disc.mechanical.treeSha
  entry.lineCount = disc.mechanical.lineCount
  entry.sectionMap = disc.mechanical.sectionMap
  entry.fileTree = disc.mechanical.fileTree
  entry.skillSizeBytes = disc.mechanical.skillSizeBytes
  entry.isSimple = disc.mechanical.isSimple
}
