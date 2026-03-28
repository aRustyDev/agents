/**
 * Stale detection for catalog entries.
 *
 * Compares analyzed treeSha against upstream folder hashes
 * (fetched via GitHub Trees API) to identify skills that need
 * re-analysis due to content changes.
 */

import { fetchSkillFolderHash } from '@agents/core/git'
import type { CatalogEntryWithTier1 } from './catalog'
import { SKILL_LOOKUP_DIRS } from './catalog-download'

export type StaleStatus = 'current' | 'stale' | 'unknown'

export interface StaleCheckResult {
  source: string
  skill: string
  status: StaleStatus
  localHash?: string
  remoteHash?: string
  error?: string
}

/**
 * Compare local catalog treeSha against upstream tree SHAs.
 * Pure function — no I/O. Takes pre-fetched upstream hashes.
 *
 * Note: Uses `treeSha` (git tree SHA), NOT `contentHash` (SHA-256 of file content).
 * These are different hash types and cannot be compared cross-type.
 */
export function identifyStaleEntries(
  entries: CatalogEntryWithTier1[],
  upstreamHashes: Map<string, string>
): StaleCheckResult[] {
  const results: StaleCheckResult[] = []

  for (const entry of entries) {
    if (!entry.treeSha || !entry.wordCount) continue

    const key = `${entry.source}:${entry.skill}`
    const remoteHash = upstreamHashes.get(key)

    if (!remoteHash) {
      // No upstream hash available (API failed or not fetched)
      continue
    }

    results.push({
      source: entry.source,
      skill: entry.skill,
      status: entry.treeSha === remoteHash ? 'current' : 'stale',
      localHash: entry.treeSha,
      remoteHash,
    })
  }

  return results
}

/**
 * Fetch upstream folder hashes for a batch of catalog entries.
 * Uses GitHub Trees API — no cloning required.
 *
 * Returns a Map of "source:skill" → treeSHA.
 * Entries that fail API lookup are silently skipped.
 */
export async function fetchUpstreamHashes(
  entries: CatalogEntryWithTier1[],
  opts?: { concurrency?: number }
): Promise<Map<string, string>> {
  const concurrency = opts?.concurrency ?? 5
  const hashes = new Map<string, string>()
  const queue = [...entries.filter((e) => e.treeSha && e.wordCount)]

  async function worker() {
    while (queue.length > 0) {
      const entry = queue.shift()
      if (!entry) break

      // Use discoveredPath if available (from discovery engine), else fall back to well-known paths
      const paths = entry.discoveredPath
        ? [entry.discoveredPath]
        : SKILL_LOOKUP_DIRS.map((prefix) => `${prefix}${entry.skill}`)

      for (const path of paths) {
        const hash = await fetchSkillFolderHash(entry.source, path)
        if (hash) {
          hashes.set(`${entry.source}:${entry.skill}`, hash)
          break
        }
      }
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()))
  return hashes
}
