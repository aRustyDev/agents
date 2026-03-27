// Re-export shim — moved to @agents/sdk/providers/local/skill/list
// The SDK version takes an optional AgentResolver as first param;
// the CLI shim wraps it to inject the CLI agent resolver automatically.

import {
  type InstalledSkill,
  type ListOptions,
  type ListResult,
  listSkills as sdkListSkills,
} from '@agents/sdk/providers/local/skill/list'
import { createCliAgentResolver } from './agents'

export type { ListOptions, ListResult, InstalledSkill }

/**
 * CLI-specific listSkills that auto-injects the CLI agent resolver.
 */
export async function listSkills(opts: ListOptions = {}): Promise<ListResult> {
  return sdkListSkills(createCliAgentResolver(), opts)
}
