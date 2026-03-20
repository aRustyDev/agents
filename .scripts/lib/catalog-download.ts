/**
 * Catalog download orchestrator.
 *
 * Composes git.ts, source-parser.ts, and skill-discovery.ts to replace
 * the npx-skills shell-out in the analyze pipeline.
 */

import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import {
  type CatalogEntry,
  computeContentHash,
  computeFileCount,
  computeHeadingTree,
  computeSectionCount,
  computeWordCount,
  type Tier1ErrorType,
} from './catalog'
import { cloneRepo, type GitCloneError } from './git'
import { discoverSkills } from './skill-discovery'
import {
  detectGitProtocol,
  type GitProtocol,
  getOwnerRepo,
  parseSource,
  resolveCloneUrl,
} from './source-parser'
import { CliError, err, ok, type Result } from './types'

/** Well-known subdirectory prefixes where skills may live in a repo. */
export const SKILL_LOOKUP_DIRS = ['', 'skills/', 'context/skills/', '.claude/skills/']

/** Build full SKILL.md lookup paths for a given skill name. */
const SKILL_LOOKUP_PATHS = (skillName: string) =>
  SKILL_LOOKUP_DIRS.map((prefix) => `${prefix}${skillName}/SKILL.md`)

/** Validated catalog source with resolved clone URL. */
export interface CatalogSource {
  ownerRepo: string
  cloneUrl: string
  ref?: string
  subpath?: string
  skillFilter?: string
}

/**
 * Validate a catalog source string. Accepts:
 * - `owner/repo` — standard entry
 * - `owner/repo#ref` — pinned to branch/tag
 * - `github.com/owner/repo/tree/ref/path` — pinned tree URL
 *
 * Rejects local paths, SSH raw URLs, non-GitHub sources.
 * Resolves clone URL using the detected git protocol (SSH/HTTPS).
 */
export function validateCatalogSource(
  source: string,
  protocol?: GitProtocol
): Result<CatalogSource> {
  const parsed = parseSource(source)
  if (!parsed.ok) return parsed as Result<never>

  // Must be a GitHub source
  if (parsed.value.type !== 'github') {
    return err(
      new CliError(
        `Catalog source must be GitHub (owner/repo or tree URL), got type "${parsed.value.type}": ${source}`,
        'E_NOT_GITHUB',
        'Supported: owner/repo, owner/repo#ref, github.com/o/r/tree/branch/path'
      )
    )
  }

  const ownerRepo = getOwnerRepo(parsed.value)
  if (!ownerRepo) {
    return err(
      new CliError(
        `Could not extract owner/repo from: ${source}`,
        'E_NOT_GITHUB',
        'Expected format: owner/repo'
      )
    )
  }

  const proto = protocol ?? detectGitProtocol()
  return ok({
    ownerRepo,
    cloneUrl: resolveCloneUrl(ownerRepo, proto),
    ref: parsed.value.ref,
    subpath: parsed.value.subpath,
    skillFilter: parsed.value.skillFilter,
  })
}

// ---------------------------------------------------------------------------
// downloadSkill types
// ---------------------------------------------------------------------------

export interface SkillDownloadResult {
  path: string | null
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  errorCode?: number
  contentHash?: string
  wordCount?: number
  sectionCount?: number
  fileCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  /** Parsed frontmatter name (from discovery). */
  discoveredName?: string
  /** Parsed frontmatter description. */
  discoveredDescription?: string
}

export interface DownloadOptions {
  /** Override clone with a local directory (for testing). */
  localOverride?: string
  /** AbortSignal for cancellation. */
  signal?: AbortSignal
  /** Clone timeout in ms (default: 60000). */
  timeout?: number
}

// ---------------------------------------------------------------------------
// downloadSkill implementation
// ---------------------------------------------------------------------------

/** Resolve the search directory: use localOverride or clone the repo. */
async function resolveSearchDir(
  validated: CatalogSource,
  opts: DownloadOptions
): Promise<Result<{ searchDir: string; cleanup?: () => Promise<void> }>> {
  if (opts.localOverride) {
    return ok({ searchDir: opts.localOverride })
  }

  const cloneResult = await cloneRepo(validated.cloneUrl, validated.ref)
  if (!cloneResult.ok) {
    const gitErr = cloneResult.error as GitCloneError
    return err(
      new CliError(
        `clone failed: ${gitErr.message}`,
        gitErr.isTimeout ? 'E_CLONE_TIMEOUT' : 'E_CLONE_FAILED',
        gitErr.hint
      )
    )
  }
  return ok({ searchDir: cloneResult.value.tempDir, cleanup: cloneResult.value.cleanup })
}

/** Discover skills and find a specific one by name, with well-known path fallback. */
async function findSkillInDir(
  searchDir: string,
  skill: string,
  source: string
): Promise<SkillDownloadResult> {
  const discovered = await discoverSkills(searchDir)
  if (!discovered.ok) {
    return {
      path: null,
      error: `discovery failed: ${discovered.error.message}`,
      errorType: 'download_failed',
      errorDetail: discovered.error.hint ?? discovered.error.message,
    }
  }

  const match = discovered.value.find((s) => s.name.toLowerCase() === skill.toLowerCase())

  if (match) {
    const result = computeResult(match.path, join(match.path, '..'))
    result.discoveredName = match.name
    result.discoveredDescription = match.frontmatter.description
    return result
  }

  // Fallback: look for SKILL.md in well-known paths
  for (const p of SKILL_LOOKUP_PATHS(skill).map((rel) => join(searchDir, rel))) {
    if (existsSync(p)) {
      return computeResult(p, join(p, '..'))
    }
  }

  const names = discovered.value
    .map((s) => s.name)
    .join(', ')
    .slice(0, 200)
  return {
    path: null,
    error: `skill "${skill}" not found in ${source} (${discovered.value.length} skills discovered: ${names})`,
    errorType: 'download_failed',
    errorDetail: 'SKILL.md not found by discovery or direct path lookup',
  }
}

/**
 * Download and analyze a single skill from a catalog entry.
 *
 * Flow:
 * 1. Validate source with parseSource()
 * 2. Clone repo (or use localOverride)
 * 3. Discover SKILL.md via discoverSkills()
 * 4. Compute mechanical fields
 *
 * Never throws -- all errors returned in the result.
 */
export async function downloadSkill(
  source: string,
  skill: string,
  opts: DownloadOptions
): Promise<SkillDownloadResult> {
  // Step 1: Validate source
  const validated = validateCatalogSource(source)
  if (!validated.ok) {
    return {
      path: null,
      error: validated.error.message,
      errorType: 'source_invalid',
      errorDetail: validated.error.hint ?? validated.error.message,
    }
  }

  // Step 2: Get the skill directory
  const resolved = await resolveSearchDir(validated.value, opts)
  if (!resolved.ok) {
    const isTimeout = resolved.error.code === 'E_CLONE_TIMEOUT'
    return {
      path: null,
      error: resolved.error.message,
      errorType: isTimeout ? 'download_timeout' : 'download_failed',
      errorDetail: resolved.error.hint ?? resolved.error.message,
    }
  }

  try {
    // Step 3+4: Discover and compute
    return await findSkillInDir(resolved.value.searchDir, skill, source)
  } finally {
    if (resolved.value.cleanup) await resolved.value.cleanup()
  }
}

/** Read SKILL.md and compute all mechanical analysis fields. */
function computeResult(skillMdPath: string, skillDir: string): SkillDownloadResult {
  const content = readFileSync(skillMdPath, 'utf8')
  return {
    path: skillMdPath,
    contentHash: computeContentHash(content),
    wordCount: computeWordCount(content),
    sectionCount: computeSectionCount(content),
    fileCount: computeFileCount(skillDir),
    headingTree: computeHeadingTree(content),
  }
}

// ---------------------------------------------------------------------------
// Batch download
// ---------------------------------------------------------------------------

export interface BatchDownloadOptions {
  /** Use local directories instead of cloning (for testing). Skill dirs at localOverrideDir/<skill-name>/ */
  localOverrideDir?: string
  /** Force git protocol override (default: auto-detect). */
  protocol?: GitProtocol
  signal?: AbortSignal
  timeout?: number
}

/**
 * Download all skills in a batch.
 *
 * Groups entries by source so repos are cloned once per source.
 * In test mode (localOverrideDir), maps skill names to subdirectories.
 *
 * Map keys are skill names. In the catalog, skill names are unique per batch.
 */
export async function downloadBatch(
  entries: CatalogEntry[],
  opts: BatchDownloadOptions = {}
): Promise<Map<string, SkillDownloadResult>> {
  const results = new Map<string, SkillDownloadResult>()

  // Group entries by source for efficient cloning
  const bySource = new Map<string, CatalogEntry[]>()
  for (const entry of entries) {
    const group = bySource.get(entry.source) ?? []
    group.push(entry)
    bySource.set(entry.source, group)
  }

  for (const [source, group] of bySource) {
    if (opts.localOverrideDir) {
      // Test mode: use local directories (no network)
      for (const entry of group) {
        const localDir = join(opts.localOverrideDir, entry.skill)
        if (!existsSync(localDir)) {
          results.set(entry.skill, {
            path: null,
            error: `local directory not found: ${localDir}`,
            errorType: 'download_failed',
            errorDetail: 'localOverrideDir set but skill directory missing',
          })
          continue
        }
        const result = await downloadSkill(source, entry.skill, {
          localOverride: localDir,
          signal: opts.signal,
        })
        results.set(entry.skill, result)
      }
      continue
    }

    // Production mode: clone once per source, discover all skills
    await downloadBatchForSource(source, group, opts, results)
  }

  return results
}

/** Fill all group entries in the results map with the same error result. */
function fillGroupWithError(
  group: CatalogEntry[],
  results: Map<string, SkillDownloadResult>,
  errorResult: Omit<SkillDownloadResult, 'path'> & { path: null }
): void {
  for (const entry of group) {
    results.set(entry.skill, errorResult)
  }
}

/**
 * Resolve a single skill entry from a cloned repo.
 * Tries discovery map first, then falls back to well-known path lookup.
 */
function resolveSkillFromClone(
  entry: CatalogEntry,
  source: string,
  tempDir: string,
  discoveredMap: Map<string, { path: string; name: string; frontmatter: { description?: string } }>
): SkillDownloadResult {
  const match = discoveredMap.get(entry.skill.toLowerCase())
  if (match) {
    const result = computeResult(match.path, join(match.path, '..'))
    result.discoveredName = match.name
    result.discoveredDescription = match.frontmatter.description
    return result
  }

  // Direct path fallback using well-known paths
  for (const p of SKILL_LOOKUP_PATHS(entry.skill).map((rel) => join(tempDir, rel))) {
    if (existsSync(p)) {
      return computeResult(p, join(p, '..'))
    }
  }

  return {
    path: null,
    error: `skill "${entry.skill}" not found in ${source}`,
    errorType: 'download_failed',
    errorDetail: `Discovered ${discoveredMap.size} skills but none matched "${entry.skill}"`,
  }
}

/** Download all skills from a single source (clones once). */
async function downloadBatchForSource(
  source: string,
  group: CatalogEntry[],
  opts: BatchDownloadOptions,
  results: Map<string, SkillDownloadResult>
): Promise<void> {
  const validated = validateCatalogSource(source, opts.protocol)
  if (!validated.ok) {
    fillGroupWithError(group, results, {
      path: null,
      error: validated.error.message,
      errorType: 'source_invalid',
      errorDetail: validated.error.hint ?? validated.error.message,
    })
    return
  }

  const cloneResult = await cloneRepo(validated.value.cloneUrl, validated.value.ref)
  if (!cloneResult.ok) {
    const gitErr = cloneResult.error as GitCloneError
    fillGroupWithError(group, results, {
      path: null,
      error: `clone failed: ${gitErr.message}`,
      errorType: gitErr.isTimeout ? 'download_timeout' : 'download_failed',
      errorDetail: gitErr.hint ?? gitErr.message,
    })
    return
  }

  try {
    // Discover all skills in the cloned repo
    const discovered = await discoverSkills(cloneResult.value.tempDir)
    const discoveredMap = new Map(
      (discovered.ok ? discovered.value : []).map((s) => [s.name.toLowerCase(), s])
    )

    for (const entry of group) {
      results.set(
        entry.skill,
        resolveSkillFromClone(entry, source, cloneResult.value.tempDir, discoveredMap)
      )
    }
  } finally {
    await cloneResult.value.cleanup()
  }
}
