/**
 * Catalog reconciliation engine.
 *
 * Matches discovery results against existing catalog entries to detect
 * moves, renames, additions, and removals. Pure functions — no I/O.
 */

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
