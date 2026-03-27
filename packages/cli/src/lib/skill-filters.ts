// Re-export shim — moved to @agents/sdk/providers/local/skill/filters
// The SDK version's validateAgentFilter takes an optional AgentResolver param;
// the CLI shim wraps it to inject the CLI agent resolver automatically.

export {
  filterArgs,
  filterByAgent,
  filterBySkill,
  type InstalledSkillEntry,
} from '@agents/sdk/providers/local/skill/filters'

import { validateAgentFilter as sdkValidateAgentFilter } from '@agents/sdk/providers/local/skill/filters'
import type { OutputFormatter } from '@agents/sdk/ui'
import { createCliAgentResolver } from './agents'

/**
 * CLI-specific validateAgentFilter that auto-injects the CLI agent resolver.
 */
export function validateAgentFilter(agentName: string, out: OutputFormatter): boolean {
  return sdkValidateAgentFilter(agentName, out, createCliAgentResolver())
}
