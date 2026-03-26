/**
 * Detailed metadata retrieval for a single installed skill.
 *
 * Reads frontmatter, checks the lock file, computes a live hash, audits
 * agent directories, and reports symlink status.  All operations are
 * fail-safe -- partial metadata is returned when individual sources are
 * unavailable.
 */

import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { hashDirectory } from '@agents/core/hash'
import type { LockfileV1, SkillFrontmatter } from '@agents/core/schemas'
import { checkSymlink } from '@agents/core/symlink'
import { CliError, err, ok, type Result } from '@agents/core/types'
import type { AgentType } from './agents'
import { detectInstalledAgents, getAgentBaseDir } from './agents'
// Importing lockfile registers the built-in 'skills' schema as a side effect.
import { readLockfile } from './lockfile'
import { readSkillFrontmatter } from './manifest'

// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------

export class InfoError extends CliError {}

// ---------------------------------------------------------------------------
// Options & output
// ---------------------------------------------------------------------------

export interface InfoOptions {
  json?: boolean
  quiet?: boolean
  global?: boolean
  cwd?: string
}

export interface SkillDetail {
  name: string
  path: string
  frontmatter: SkillFrontmatter | null
  source: string | null
  sourceType: string | null
  computedHash: string | null
  lockHash: string | null
  hashMatch: boolean
  installedAgents: AgentType[]
  symlinkStatus: 'symlink' | 'copy' | 'missing'
  symlinkTarget: string | null
}

// ---------------------------------------------------------------------------
// Main function
// ---------------------------------------------------------------------------

/**
 * Get detailed metadata for a single installed skill.
 *
 * Reads frontmatter, checks lock file, computes hash, and audits agent dirs.
 * Returns Result to keep the never-throw pattern.
 */
export async function skillInfo(
  name: string,
  opts: InfoOptions = {}
): Promise<Result<SkillDetail>> {
  const cwd = opts.cwd ?? process.cwd()
  const skillPath = join(cwd, 'content', 'skills', name)

  if (!existsSync(skillPath)) {
    return err(
      new InfoError(
        `Skill "${name}" not found on disk`,
        'E_SKILL_NOT_FOUND',
        `Expected at: ${skillPath}`
      )
    )
  }

  // -- Frontmatter ----------------------------------------------------------
  const skillMdPath = join(skillPath, 'SKILL.md')
  const fmResult = await readSkillFrontmatter(skillMdPath)
  const frontmatter = fmResult.ok ? fmResult.value : null

  // -- Lock entry -----------------------------------------------------------
  const lockPath = join(cwd, 'skills-lock.json')
  const lockResult = await readLockfile<LockfileV1>('skills', lockPath)
  const lockData = lockResult.ok ? lockResult.value : null
  const lockEntry = lockData?.skills?.[name] ?? null

  // -- Live hash ------------------------------------------------------------
  let computedHash: string | null = null
  try {
    computedHash = await hashDirectory(skillPath)
  } catch {
    // hash unavailable -- leave null
  }

  // -- Installed agents -----------------------------------------------------
  const installed = await detectInstalledAgents()
  const installedAgents: AgentType[] = []
  for (const agent of installed) {
    const baseDirResult = getAgentBaseDir(agent, opts.global ?? false, cwd)
    if (!baseDirResult.ok) continue
    const agentSkillPath = join(baseDirResult.value, name)
    if (existsSync(agentSkillPath)) {
      installedAgents.push(agent)
    }
  }

  // -- Symlink status -------------------------------------------------------
  let symlinkStatus: 'symlink' | 'copy' | 'missing' = 'missing'
  let symlinkTarget: string | null = null
  try {
    const status = await checkSymlink(skillPath)
    symlinkStatus = 'symlink'
    symlinkTarget = status.target
  } catch {
    // checkSymlink throws when the path is not a symlink (or does not exist).
    // If the path exists on disk it is a regular copy, otherwise missing.
    if (existsSync(skillPath)) {
      symlinkStatus = 'copy'
    }
  }

  return ok({
    name,
    path: skillPath,
    frontmatter,
    source: lockEntry?.source ?? null,
    sourceType: lockEntry?.sourceType ?? null,
    computedHash,
    lockHash: lockEntry?.computedHash ?? null,
    hashMatch:
      computedHash != null &&
      lockEntry?.computedHash != null &&
      computedHash === lockEntry.computedHash,
    installedAgents,
    symlinkStatus,
    symlinkTarget,
  })
}
