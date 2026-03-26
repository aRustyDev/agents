/**
 * Convenience factory for creating a pre-configured ProviderManager.
 *
 * Registers default providers based on available options. The CLI provides
 * SkillOperations for the local skill provider; without it, only non-skill
 * local providers and remote providers are registered.
 */

import type { Logger } from '../util/logger'
import { GitHubProvider } from './github'
import { LocalSkillProvider } from './local'
import { LocalAgentProvider } from './local/agent'
import { LocalCommandProvider } from './local/command'
import { LocalOutputStyleProvider } from './local/output-style'
import { LocalPluginProvider } from './local/plugin'
import { LocalRuleProvider } from './local/rule'
import type { SkillOperations } from './local/skill-ops'
import { ProviderManager } from './manager'
import { SmitheryProvider } from './smithery'

export function createDefaultProviders(opts?: {
  cwd?: string
  logger?: Logger
  skillOps?: SkillOperations
}): ProviderManager {
  const manager = new ProviderManager()
  const cwd = opts?.cwd

  // Remote providers (always registered)
  manager.register(new SmitheryProvider())
  manager.register(new GitHubProvider())

  // Local providers that don't need skill ops (always registered)
  manager.register(new LocalAgentProvider(cwd))
  manager.register(new LocalCommandProvider(cwd))
  manager.register(new LocalRuleProvider(cwd))
  manager.register(new LocalOutputStyleProvider(cwd))
  manager.register(new LocalPluginProvider(cwd))

  // LocalSkillProvider only registered if skillOps provided
  if (opts?.skillOps) {
    manager.register(new LocalSkillProvider(opts.skillOps, cwd))
  }

  return manager
}
