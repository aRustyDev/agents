/**
 * Repo-level discovery engine.
 *
 * Clones each unique repo once, discovers ALL skills, and computes
 * ALL deterministic fields in a single pass. No LLM involvement.
 *
 * Produces RepoManifest + enriched catalog entries.
 */

import { existsSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import {
  type CatalogEntryWithTier1,
  type ComponentMetadata,
  computeContentHash,
  computeFileCount,
  computeFileTree,
  computeHeadingTree,
  computeLineCount,
  computeSectionCount,
  computeSectionMap,
  computeSkillSizeBytes,
  computeWordCount,
  extractKeywords,
  isSimpleSkill,
  type RepoManifest,
  type Tier1ErrorType,
} from './catalog'
import { cloneRepo, gitRaw } from './git'
import { discoverSkills } from './skill-discovery'
import { detectGitProtocol, type GitProtocol, resolveCloneUrl } from './source-parser'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Result of discovering a single skill in a repo. */
export interface DiscoveredSkillResult {
  source: string
  skill: string
  /** Full SKILL.md content, stored during discovery for manifest building. */
  content?: string
  /** All mechanical fields computed from the skill content + directory. */
  mechanical: ComponentMetadata & {
    wordCount: number
    sectionCount: number
    fileCount: number
    headingTree: Array<{ depth: number; title: string }>
    contentHash: string
    treeSha?: string
    keywords: string[]
  }
}

/** Result of discovering all skills in a single repo. */
export interface RepoDiscoveryResult {
  manifest: RepoManifest
  skills: DiscoveredSkillResult[]
  /** Skills in catalog but not found in this repo. */
  missing: Array<{ source: string; skill: string }>
  errors: Array<{ source: string; error: string; errorType: Tier1ErrorType }>
}

/** Options for the discovery engine. */
export interface DiscoverOptions {
  protocol?: GitProtocol
  /** Existing repo manifests for incremental skip. */
  cachedManifests?: RepoManifest[]
  /** If true, skip repos whose HEAD matches cached headSha. */
  incremental?: boolean
  concurrency?: number
  onProgress?: (done: number, total: number, repo: string) => void
}

// ---------------------------------------------------------------------------
// Repo Metadata Collection
// ---------------------------------------------------------------------------

/**
 * Collect repo-level metadata from a cloned directory.
 * Uses git commands for commit/contributor data, fs for size/file counts.
 */
export async function collectRepoMetadata(
  tempDir: string,
  source: string
): Promise<Omit<RepoManifest, 'skills' | 'skillCount'>> {
  // HEAD SHA
  const headResult = await gitRaw(['rev-parse', 'HEAD'], tempDir)
  const headSha = headResult.ok ? headResult.value.trim() : 'unknown'

  // Last commit date
  const dateResult = await gitRaw(['log', '-1', '--format=%aI'], tempDir)
  const lastCommitAt = dateResult.ok ? dateResult.value.trim() : undefined

  // Commit count (shallow clone = 1, but captures the intent)
  const countResult = await gitRaw(['rev-list', '--count', 'HEAD'], tempDir)
  const commitCount = countResult.ok ? parseInt(countResult.value.trim(), 10) : undefined

  // Contributor count
  const contribResult = await gitRaw(['shortlog', '-sn', '--no-merges', 'HEAD'], tempDir)
  const contributorCount = contribResult.ok
    ? contribResult.value.trim().split('\n').filter(Boolean).length
    : undefined

  // Repo size and file count via filesystem
  const repoSizeBytes = computeSkillSizeBytes(tempDir)
  const totalFiles = computeFileCount(tempDir)

  // Archived status — we don't have API access here, default to false
  // (availability check already captured this)
  const archived = false

  return {
    repo: source,
    clonedAt: new Date().toISOString(),
    headSha,
    totalFiles,
    repoSizeBytes,
    archived,
    lastCommitAt,
    commitCount,
    contributorCount,
  }
}

// ---------------------------------------------------------------------------
// Per-Skill Mechanical Computation
// ---------------------------------------------------------------------------

/**
 * Compute ALL deterministic fields for a single discovered skill.
 */
export async function computeAllMechanicalFields(
  skillMdPath: string,
  skillDir: string,
  tempDir: string,
  source: string,
  skillName: string
): Promise<DiscoveredSkillResult> {
  const content = readFileSync(skillMdPath, 'utf8')
  const relPath = relative(tempDir, skillDir).replace(/\\/g, '/')

  // treeSha from git
  let treeSha: string | undefined
  if (relPath && !relPath.startsWith('..')) {
    const result = await gitRaw(['rev-parse', `HEAD:${relPath}`], tempDir)
    if (result.ok) treeSha = result.value.trim()
  }

  return {
    source,
    skill: skillName,
    content,
    mechanical: {
      discoveredPath: relPath || '.',
      lastSeenAt: new Date().toISOString(),
      wordCount: computeWordCount(content),
      sectionCount: computeSectionCount(content),
      fileCount: computeFileCount(skillDir),
      headingTree: computeHeadingTree(content),
      contentHash: computeContentHash(content),
      treeSha,
      keywords: extractKeywords(content),
      lineCount: computeLineCount(content),
      sectionMap: computeSectionMap(content),
      fileTree: computeFileTree(skillDir),
      skillSizeBytes: computeSkillSizeBytes(skillDir),
      isSimple: isSimpleSkill(skillDir),
    },
  }
}

// ---------------------------------------------------------------------------
// Single Repo Discovery
// ---------------------------------------------------------------------------

/**
 * Clone a repo, discover all skills, compute all mechanical fields.
 * Returns a RepoDiscoveryResult with manifest + skill data + missing list.
 */
export async function discoverRepo(
  source: string,
  catalogSkills: string[],
  opts?: { protocol?: GitProtocol }
): Promise<RepoDiscoveryResult> {
  const protocol = opts?.protocol ?? detectGitProtocol()
  const cloneUrl = resolveCloneUrl(source, protocol)

  const cloneResult = await cloneRepo(cloneUrl)
  if (!cloneResult.ok) {
    const isTimeout = cloneResult.error.message.includes('timeout')
    return {
      manifest: emptyManifest(source),
      skills: [],
      missing: catalogSkills.map((s) => ({ source, skill: s })),
      errors: catalogSkills.map((s) => ({
        source,
        error: `clone failed: ${cloneResult.error.message}`,
        errorType: (isTimeout ? 'download_timeout' : 'download_failed') as Tier1ErrorType,
      })),
    }
  }

  try {
    const tempDir = cloneResult.value.tempDir

    // Collect repo metadata
    const repoMeta = await collectRepoMetadata(tempDir, source)

    // Discover all skills
    const discovered = await discoverSkills(tempDir)
    const discoveredSkills = discovered.ok ? discovered.value : []

    // Compute mechanical fields for each discovered skill
    const skills: DiscoveredSkillResult[] = []
    for (const disc of discoveredSkills) {
      const skillDir = join(disc.path, '..')
      const result = await computeAllMechanicalFields(
        disc.path,
        skillDir,
        tempDir,
        source,
        disc.name
      )
      // Set lastSeenHeadSha from repo metadata
      result.mechanical.lastSeenHeadSha = repoMeta.headSha
      skills.push(result)
    }

    // Identify skills in catalog but not discovered
    const discoveredNames = new Set(discoveredSkills.map((s) => s.name.toLowerCase()))
    const missing = catalogSkills
      .filter((s) => !discoveredNames.has(s.toLowerCase()))
      .map((s) => ({ source, skill: s }))

    const manifest: RepoManifest = {
      ...repoMeta,
      skillCount: skills.length,
      skills: skills.map((s) => s.skill),
    }

    return { manifest, skills, missing, errors: [] }
  } finally {
    await cloneResult.value.cleanup()
  }
}

// ---------------------------------------------------------------------------
// Incremental Discovery (HEAD SHA comparison)
// ---------------------------------------------------------------------------

/**
 * Fetch the remote HEAD SHA for a repo without cloning.
 * Uses `git ls-remote` — fast (~200ms per repo).
 * Returns null if the repo is unreachable.
 */
export async function fetchRemoteHeadSha(
  source: string,
  protocol?: GitProtocol
): Promise<string | null> {
  const proto = protocol ?? detectGitProtocol()
  const url = resolveCloneUrl(source, proto)
  const result = await gitRaw(['ls-remote', url, 'HEAD'])
  if (!result.ok) return null
  const sha = result.value.trim().split(/\s/)[0]
  return sha || null
}

// ---------------------------------------------------------------------------
// Multi-Repo Discovery (Concurrent)
// ---------------------------------------------------------------------------

/** Summary of incremental skip decisions. */
export interface DiscoverySummary {
  totalRepos: number
  cloned: number
  skipped: number
  results: RepoDiscoveryResult[]
}

/**
 * Discover all unique repos from catalog entries concurrently.
 * Groups entries by source, clones each repo once.
 *
 * In incremental mode (opts.incremental + opts.cachedManifests), skips repos
 * whose remote HEAD SHA matches the cached manifest's headSha.
 */
export async function discoverAllRepos(
  entries: CatalogEntryWithTier1[],
  opts: DiscoverOptions = {}
): Promise<DiscoverySummary> {
  const concurrency = opts.concurrency ?? 5

  // Group catalog skills by source
  const bySource = new Map<string, string[]>()
  for (const entry of entries) {
    if (entry.availability !== 'available') continue
    const skills = bySource.get(entry.source) ?? []
    skills.push(entry.skill)
    bySource.set(entry.source, skills)
  }

  // Build cache index for incremental mode
  const cache = new Map<string, RepoManifest>()
  if (opts.incremental && opts.cachedManifests) {
    for (const m of opts.cachedManifests) {
      cache.set(m.repo, m)
    }
  }

  const queue = [...bySource.entries()]
  const results: RepoDiscoveryResult[] = []
  let done = 0
  let skipped = 0

  async function worker() {
    while (queue.length > 0) {
      const item = queue.shift()
      if (!item) break
      const [source, catalogSkills] = item

      // Incremental: check if remote HEAD matches cache
      if (opts.incremental && cache.has(source)) {
        const cached = cache.get(source)
        if (cached) {
          const remoteHead = await fetchRemoteHeadSha(source, opts.protocol)
          if (remoteHead && remoteHead === cached.headSha) {
            skipped++
            done++
            opts.onProgress?.(done, bySource.size, `${source} (skipped)`)
            continue
          }
        }
      }

      const result = await discoverRepo(source, catalogSkills, {
        protocol: opts.protocol,
      })
      results.push(result)

      done++
      opts.onProgress?.(done, bySource.size, source)
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()))
  return {
    totalRepos: bySource.size,
    cloned: results.length,
    skipped,
    results,
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function emptyManifest(source: string): RepoManifest {
  return {
    repo: source,
    clonedAt: new Date().toISOString(),
    headSha: 'unknown',
    totalFiles: 0,
    repoSizeBytes: 0,
    archived: false,
    skillCount: 0,
    skills: [],
  }
}
