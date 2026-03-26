/**
 * Skill removal orchestrator.
 *
 * Handles the full workflow of removing one or more skills:
 *
 * 1. Scan each agent's project-level skills directory for the skill
 *    (or limit to a single agent via `--agent`)
 * 2. Remove the symlink or directory from each agent
 * 3. If no agent still references the canonical directory, remove it
 * 4. Update the skills lockfile
 *
 * The public `removeSkills` function never throws -- all errors are
 * returned as structured `RemoveResult` objects.
 */

import { existsSync } from 'node:fs'
import { rm } from 'node:fs/promises'
import { join } from 'node:path'
import { CliError } from '@agents/core/types'
import type { AgentType } from './agents'
import { AGENT_CONFIGS, getAgentBaseDir } from './agents'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export class RemoveError extends CliError {
  constructor(
    message: string,
    code:
      | 'E_SKILL_NOT_FOUND'
      | 'E_LOCK_UPDATE_FAILED'
      | 'E_FS_REMOVE_FAILED'
      | 'E_BROKEN_SYMLINK'
      | 'E_AGENT_NOT_FOUND',
    hint?: string,
    cause?: unknown
  ) {
    super(message, code, hint, cause)
  }
}

export interface RemoveOptions {
  /** Limit removal to a single agent. */
  agent?: string
  /** Skip confirmation prompts. */
  yes?: boolean
  /** JSON output mode. */
  json?: boolean
  /** Quiet mode. */
  quiet?: boolean
  /** Use global (user-level) agent directories. */
  global?: boolean
  /** Working directory (project root). Defaults to cwd. */
  cwd?: string
}

export interface RemoveResult {
  /** Name of the skill. */
  skill: string
  /** Agents the skill was removed from. */
  removedFrom: AgentType[]
  /** Whether the canonical directory was removed. */
  canonicalRemoved: boolean
  /** Whether the lockfile entry was removed. */
  lockUpdated: boolean
  /** Error message if the skill was not found anywhere. */
  error?: string
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Remove skills from agent directories and update lock files.
 *
 * For each skill:
 * 1. Find all agent dirs that have it (or filter to `--agent`)
 * 2. Remove the symlink/directory from each agent dir
 * 3. If no agent still references the canonical dir, remove it
 * 4. Remove the lockfile entry
 *
 * Never throws -- errors are captured in `RemoveResult`.
 */
export async function removeSkills(
  names: string[],
  opts: RemoveOptions = {}
): Promise<RemoveResult[]> {
  const cwd = opts.cwd ?? process.cwd()
  const results: RemoveResult[] = []

  // Read current lock file
  const lockPath = join(cwd, 'skills-lock.json')
  const lockData = await readLock(lockPath)

  // Collect all known agents
  const allAgentTypes: AgentType[] = [...AGENT_CONFIGS.keys()]

  // Determine target agents for removal
  const targetAgents: AgentType[] = opts.agent
    ? allAgentTypes.filter((a) => a === opts.agent)
    : allAgentTypes

  for (const name of names) {
    const removedFrom: AgentType[] = []
    let canonicalRemoved = false

    // Remove from each agent's skills directory
    for (const agentType of targetAgents) {
      const baseDirResult = getAgentBaseDir(agentType, opts.global ?? false, cwd)
      if (!baseDirResult.ok) continue

      const agentSkillPath = join(baseDirResult.value, name)
      if (!existsSync(agentSkillPath)) continue

      try {
        await rm(agentSkillPath, { recursive: true, force: true })
        removedFrom.push(agentType)
      } catch {
        // Continue with other agents -- non-fatal
      }
    }

    // Determine whether any agent still has the skill
    const canonicalPath = join(cwd, 'content', 'skills', name)
    let anyAgentStillHasIt = false

    if (opts.agent) {
      // Only removed from one agent -- check the rest
      for (const agentType of allAgentTypes) {
        if (agentType === opts.agent) continue
        const baseDirResult = getAgentBaseDir(agentType, opts.global ?? false, cwd)
        if (!baseDirResult.ok) continue
        if (existsSync(join(baseDirResult.value, name))) {
          anyAgentStillHasIt = true
          break
        }
      }
    }
    // When no --agent filter, we removed from all agents, so canonical can go

    if (!anyAgentStillHasIt && existsSync(canonicalPath)) {
      try {
        await rm(canonicalPath, { recursive: true, force: true })
        canonicalRemoved = true
      } catch {
        // non-fatal
      }
    }

    // Update lock data in memory
    let lockUpdated = false
    if (canonicalRemoved && name in lockData.skills) {
      delete lockData.skills[name]
      lockUpdated = true
    }

    results.push({
      skill: name,
      removedFrom,
      canonicalRemoved,
      lockUpdated,
      error:
        removedFrom.length === 0 && !canonicalRemoved ? `Skill "${name}" not found` : undefined,
    })
  }

  // Persist lock file if any entries were removed
  if (results.some((r) => r.lockUpdated)) {
    await writeLock(lockPath, lockData)
  }

  return results
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

interface LockData {
  version: 1
  skills: Record<string, { source: string; sourceType: string; computedHash: string }>
}

/**
 * Read the skills lockfile, returning a default empty structure on any failure.
 */
async function readLock(path: string): Promise<LockData> {
  const { readText } = await import('@agents/core/runtime')
  try {
    const raw = await readText(path)
    return JSON.parse(raw) as LockData
  } catch {
    return { version: 1, skills: {} }
  }
}

/**
 * Write the skills lockfile.
 */
async function writeLock(path: string, data: LockData): Promise<void> {
  const { writeText } = await import('@agents/core/runtime')
  await writeText(path, JSON.stringify(data, null, 2) + '\n')
}
