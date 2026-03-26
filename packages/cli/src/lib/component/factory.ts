import { ComponentManager } from '@agents/sdk/providers/manager'
import { LocalAgentProvider } from './provider-agent'
import { LocalCommandProvider } from './provider-command'
import { LocalProvider } from './provider-local'
import { LocalOutputStyleProvider } from './provider-output-style'
import { LocalPluginProvider } from './provider-plugin'
import { LocalRuleProvider } from './provider-rule'
import { SmitheryProvider } from './provider-smithery'

/**
 * Create a fully-configured ComponentManager with all providers registered.
 *
 * This is the canonical way to get a manager instance -- CLI commands use this
 * rather than manually registering providers.
 *
 * @param opts.cwd - Working directory for local providers (default: process.cwd())
 * @param opts.smitheryBaseUrl - Override Smithery API base URL
 */
export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ComponentManager {
  const cwd = opts?.cwd
  const manager = new ComponentManager()

  // Local providers (filesystem-based)
  manager.register(new LocalProvider(cwd))
  manager.register(new LocalAgentProvider(cwd))
  manager.register(new LocalPluginProvider(cwd))
  manager.register(new LocalRuleProvider(cwd))
  manager.register(new LocalCommandProvider(cwd))
  manager.register(new LocalOutputStyleProvider(cwd))

  // Remote providers
  manager.register(
    new SmitheryProvider(opts?.smitheryBaseUrl ? { baseUrl: opts.smitheryBaseUrl } : undefined)
  )

  return manager
}
