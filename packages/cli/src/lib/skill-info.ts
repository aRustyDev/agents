// Re-export shim — moved to @agents/sdk/providers/local/skill/info
// The SDK version takes an optional AgentResolver as first param;
// the CLI shim wraps it to inject the CLI agent resolver automatically.

import type { Result } from '@agents/core/types'
import {
  InfoError,
  type InfoOptions,
  type SkillDetail,
  skillInfo as sdkSkillInfo,
} from '@agents/sdk/providers/local/skill/info'
import { createCliAgentResolver } from './agents'

export { InfoError, type InfoOptions, type SkillDetail }

/**
 * CLI-specific skillInfo that auto-injects the CLI agent resolver.
 */
export async function skillInfo(
  name: string,
  opts: InfoOptions = {}
): Promise<Result<SkillDetail>> {
  return sdkSkillInfo(createCliAgentResolver(), name, opts)
}
