// Re-export shim — moved to @agents/sdk/providers/local/skill/add
// The SDK version takes an optional AgentResolver as first param;
// the CLI shim wraps it to inject the CLI agent resolver automatically.

import {
  type AddOptions,
  type AddResult,
  type InstalledEntry,
  addSkill as sdkAddSkill,
} from '@agents/sdk/providers/local/skill/add'
import { createCliAgentResolver } from './agents'

export type { AddOptions, AddResult, InstalledEntry }

/**
 * CLI-specific addSkill that auto-injects the CLI agent resolver.
 */
export async function addSkill(source: string, opts: AddOptions = {}): Promise<AddResult> {
  return sdkAddSkill(createCliAgentResolver(), source, opts)
}
