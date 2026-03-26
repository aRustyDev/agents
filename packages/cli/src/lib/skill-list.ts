/**
 * Skill listing module.
 *
 * Scans `content/skills/` (or a custom path) for installed skills, checks
 * which agents have each skill installed (via symlink or directory presence),
 * and returns a filterable list.
 *
 * Supports `--agent` and `--skill` filters via the shared `skill-filters`
 * module.
 *
 * The public `listSkills` function never throws -- all errors are returned
 * as structured `ListResult` objects.
 */

import { existsSync } from 'node:fs'
import { lstat, readdir, readlink } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { CliError } from '@agents/core/types'
import type { AgentType } from './agents'
import { AGENT_CONFIGS } from './agents'
import { filterByAgent, filterBySkill, type InstalledSkillEntry } from './skill-filters'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ListOptions {
  /** Working directory (project root). Defaults to cwd. */
  cwd?: string
  /** Base directory containing skills. Defaults to `content/skills/`. */
  skillsDir?: string
  /** Filter to a specific agent. */
  agent?: string
  /** Filter to a specific skill name. */
  skill?: string
  /** JSON output mode. */
  json?: boolean
  /** Quiet mode. */
  quiet?: boolean
}

export interface InstalledSkill extends InstalledSkillEntry {
  /** Absolute path to the skill directory. */
  path: string
  /** Description from SKILL.md frontmatter. */
  description?: string
  /** Version from SKILL.md frontmatter. */
  version?: string
  /** Tags from SKILL.md frontmatter. */
  tags?: string[]
}

export interface ListResult {
  /** Whether the operation completed successfully. */
  ok: boolean
  /** Discovered installed skills. */
  skills: InstalledSkill[]
  /** Error that caused the operation to fail. */
  error?: CliError
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * List all installed skills with agent detection and optional filtering.
 *
 * Never throws -- all errors are captured in the returned `ListResult`.
 */
export async function listSkills(opts: ListOptions = {}): Promise<ListResult> {
  const cwd = opts.cwd ?? process.cwd()
  const skillsDir = opts.skillsDir ?? join(cwd, 'content', 'skills')

  if (!existsSync(skillsDir)) {
    return {
      ok: true,
      skills: [],
    }
  }

  // Read skill directories
  let entries: Awaited<ReturnType<typeof readdir>>
  try {
    entries = await readdir(skillsDir, { withFileTypes: true })
  } catch (e) {
    return {
      ok: false,
      skills: [],
      error: new CliError(
        `Failed to read skills directory: ${skillsDir}`,
        'E_READ_FAILED',
        e instanceof Error ? e.message : String(e)
      ),
    }
  }

  const skills: InstalledSkill[] = []

  for (const entry of entries) {
    // Only process directories (or symlinks that resolve to directories)
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue

    const skillDir = join(skillsDir, entry.name)
    const skillMdPath = join(skillDir, 'SKILL.md')

    // Must have a SKILL.md file
    if (!existsSync(skillMdPath)) continue

    // Parse frontmatter
    const { readSkillFrontmatter } = await import('./manifest')
    const fmResult = await readSkillFrontmatter(skillMdPath)
    if (!fmResult.ok) continue // Skip skills with invalid frontmatter

    const fm = fmResult.value

    // Detect which agents have this skill
    const agentList = await detectAgentsForSkill(entry.name, cwd)

    // Check for symlink target
    let symlinkTarget: string | undefined
    try {
      const stats = await lstat(skillDir)
      if (stats.isSymbolicLink()) {
        const target = await readlink(skillDir)
        symlinkTarget = resolve(dirname(skillDir), target)
      }
    } catch {
      // Not a symlink or unreadable -- that's fine
    }

    skills.push({
      name: fm.name,
      path: skillDir,
      description: fm.description,
      version: fm.version,
      tags: fm.tags,
      agents: agentList,
      source: fm.source,
      symlinkTarget,
    })
  }

  // Apply filters
  let filtered: InstalledSkillEntry[] = skills
  filtered = filterByAgent(filtered, opts.agent)
  filtered = filterBySkill(filtered, opts.skill)

  // Restore full type after filtering
  const result = filtered as InstalledSkill[]

  return { ok: true, skills: result }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Detect which agents have a skill installed by checking for the skill
 * directory (or symlink) in each agent's project-level skills directory.
 */
async function detectAgentsForSkill(skillName: string, cwd: string): Promise<AgentType[]> {
  const found: AgentType[] = []

  for (const [agentType, config] of AGENT_CONFIGS) {
    const agentSkillDir = join(cwd, config.skillsDir, skillName)
    if (existsSync(agentSkillDir)) {
      found.push(agentType)
    }
  }

  return found
}
