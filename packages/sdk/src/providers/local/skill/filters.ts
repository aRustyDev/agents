/**
 * Filter utilities for skill listings.
 *
 * Provides reusable filter functions and CLI argument definitions for
 * `--agent` and `--skill` flags used across skill list, add, and remove
 * commands.
 */

import type { AgentResolver } from '../../../context/agent/config'
import type { OutputFormatter } from '../../../ui'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface InstalledSkillEntry {
  /** Skill name (from frontmatter). */
  name: string
  /** Agents that have this skill installed. */
  agents: string[]
  /** Source string (e.g. "owner/repo" or "./local/path"). */
  source?: string
  /** SHA256 hex digest of the skill directory. */
  computedHash?: string
  /** Symlink target path (if installed via symlink). */
  symlinkTarget?: string
}

// ---------------------------------------------------------------------------
// Filter functions
// ---------------------------------------------------------------------------

/**
 * Filter skills to only those installed for a specific agent.
 *
 * Returns all skills when `agentFilter` is undefined or empty.
 */
export function filterByAgent(
  skills: InstalledSkillEntry[],
  agentFilter?: string
): InstalledSkillEntry[] {
  if (!agentFilter) return skills
  return skills.filter((s) => s.agents.includes(agentFilter))
}

/**
 * Filter skills to only those matching a specific name (case-insensitive).
 *
 * Returns all skills when `skillFilter` is undefined or empty.
 */
export function filterBySkill(
  skills: InstalledSkillEntry[],
  skillFilter?: string
): InstalledSkillEntry[] {
  if (!skillFilter) return skills
  const lower = skillFilter.toLowerCase()
  return skills.filter((s) => s.name.toLowerCase() === lower)
}

/**
 * Validate that an agent name is known. Emits a warning via the output
 * formatter if the agent is not in the registry.
 *
 * @param agentName - Agent identifier to validate.
 * @param out - Output formatter for warnings.
 * @param resolver - Optional AgentResolver for looking up known agents.
 * @returns `true` if the agent is valid, `false` otherwise.
 */
export function validateAgentFilter(
  agentName: string,
  out: OutputFormatter,
  resolver?: AgentResolver
): boolean {
  if (resolver) {
    if (resolver.get(agentName)) return true
    const known = resolver
      .list()
      .slice(0, 5)
      .map((c) => c.name)
    out.warn(`Unknown agent "${agentName}". Known agents: ${known.join(', ')}...`)
    return false
  }
  // Without a resolver, assume valid
  return true
}

// ---------------------------------------------------------------------------
// Shared CLI argument definitions
// ---------------------------------------------------------------------------

/**
 * Reusable citty argument definitions for `--agent` and `--skill` flags.
 *
 * Usage:
 * ```ts
 * import { filterArgs } from './skill-filters'
 *
 * defineCommand({
 *   args: { ...filterArgs, ... },
 * })
 * ```
 */
export const filterArgs = {
  agent: {
    type: 'string' as const,
    description: 'Filter by agent name (e.g., claude-code, cursor)',
  },
  skill: { type: 'string' as const, description: 'Filter by skill name' },
} as const
