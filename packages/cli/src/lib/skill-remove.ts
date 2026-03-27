// Re-export shim — moved to @agents/sdk/providers/local/skill/remove
// The SDK version takes an optional AgentResolver as first param;
// the CLI shim wraps it to inject the CLI agent resolver automatically.

import {
  RemoveError,
  type RemoveOptions,
  type RemoveResult,
  removeSkills as sdkRemoveSkills,
} from '@agents/sdk/providers/local/skill/remove'
import { createCliAgentResolver } from './agents'

export { RemoveError, type RemoveOptions, type RemoveResult }

/**
 * CLI-specific removeSkills that auto-injects the CLI agent resolver.
 */
export async function removeSkills(
  names: string[],
  opts: RemoveOptions = {}
): Promise<RemoveResult[]> {
  return sdkRemoveSkills(createCliAgentResolver(), names, opts)
}
