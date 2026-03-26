/**
 * Skill discovery module.
 *
 * Recursively scans a directory tree for SKILL.md files, parses their
 * frontmatter, and returns structured metadata for each discovered skill.
 *
 * Discovery follows a two-phase strategy:
 * 1. **Priority search** -- check well-known directories first (skills/,
 *    content/skills/, .agents/skills/, .claude/skills/).
 * 2. **Fallback scan** -- if no skills are found in priority dirs, do a full
 *    recursive walk from the search root (up to `maxDepth`).
 *
 * Invalid SKILL.md files (missing or malformed frontmatter) are silently
 * skipped so that one bad file does not prevent the rest from being found.
 */

import { existsSync } from 'node:fs'
import { readdir } from 'node:fs/promises'
import { join, relative } from 'node:path'
import type { SkillFrontmatter } from '@agents/core/schemas'
import { CliError, err, ok, type Result } from '@agents/core/types'
import { readSkillFrontmatter } from './manifest'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface DiscoveredSkill {
  /** Absolute path to the SKILL.md file. */
  readonly path: string
  /** Path relative to the original `basePath` argument. */
  readonly relativePath: string
  /** Parsed and validated YAML frontmatter. */
  readonly frontmatter: SkillFrontmatter
  /** Convenience alias for `frontmatter.name`. */
  readonly name: string
}

export interface DiscoverOptions {
  /** Maximum directory depth to recurse into (default: 5). */
  maxDepth?: number
  /** Reserved for future use -- scan plugin directories too. */
  checkPlugins?: boolean
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Well-known directories where skills are typically stored. */
const PRIORITY_DIRS = ['skills', 'content/skills', '.agents/skills', '.claude/skills']

const DEFAULT_MAX_DEPTH = 5

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Discover all valid SKILL.md files under `basePath` (optionally scoped by
 * `subpath`).
 *
 * @param basePath - Root directory for discovery (used to compute relative paths).
 * @param subpath  - Optional subdirectory to restrict the search to.
 * @param opts     - Discovery options (maxDepth, etc.).
 * @returns An array of discovered skills, or an error if the search root
 *          does not exist.
 */
export async function discoverSkills(
  basePath: string,
  subpath?: string,
  opts?: DiscoverOptions
): Promise<Result<DiscoveredSkill[]>> {
  const searchRoot = subpath ? join(basePath, subpath) : basePath
  const maxDepth = opts?.maxDepth ?? DEFAULT_MAX_DEPTH

  if (!existsSync(searchRoot)) {
    return err(
      new CliError(
        `Path does not exist: ${searchRoot}`,
        'E_DISCOVERY_PATH',
        'Verify the path exists and is accessible'
      )
    )
  }

  const skillPaths: string[] = []

  // Phase 1: check well-known directories first
  for (const dir of PRIORITY_DIRS) {
    const candidate = join(searchRoot, dir)
    if (existsSync(candidate)) {
      const found = await findSkillFiles(candidate, maxDepth, 0)
      skillPaths.push(...found)
    }
  }

  // Phase 2: fallback recursive scan if nothing found in priority dirs
  if (skillPaths.length === 0) {
    const found = await findSkillFiles(searchRoot, maxDepth, 0)
    skillPaths.push(...found)
  }

  // Parse each SKILL.md and collect successes
  const skills: DiscoveredSkill[] = []
  for (const skillPath of skillPaths) {
    const result = await readSkillFrontmatter(skillPath)
    if (result.ok) {
      skills.push({
        path: skillPath,
        relativePath: relative(basePath, skillPath),
        frontmatter: result.value,
        name: result.value.name,
      })
    }
    // Files with invalid frontmatter are silently skipped (non-fatal)
  }

  return ok(skills)
}

/**
 * Filter a list of discovered skills to only those whose names appear in
 * `names` (case-insensitive).
 */
export function filterSkills(skills: DiscoveredSkill[], names: string[]): DiscoveredSkill[] {
  const lowerNames = new Set(names.map((n) => n.toLowerCase()))
  return skills.filter((s) => lowerNames.has(s.name.toLowerCase()))
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Recursively find all `SKILL.md` files under `dir`, up to `maxDepth` levels.
 *
 * Hidden directories (starting with `.`) are skipped to avoid scanning
 * `.git`, `.venv`, `node_modules`-style dirs, etc.
 */
async function findSkillFiles(
  dir: string,
  maxDepth: number,
  currentDepth: number
): Promise<string[]> {
  if (currentDepth > maxDepth) return []

  const results: string[] = []

  let entries: Awaited<ReturnType<typeof readdir>>
  try {
    entries = await readdir(dir, { withFileTypes: true })
  } catch {
    return []
  }

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    if (entry.isFile() && entry.name === 'SKILL.md') {
      results.push(fullPath)
    } else if (entry.isDirectory() && !entry.name.startsWith('.')) {
      const sub = await findSkillFiles(fullPath, maxDepth, currentDepth + 1)
      results.push(...sub)
    }
  }

  return results
}
