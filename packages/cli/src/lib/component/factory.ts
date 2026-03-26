import { createDefaultProviders } from '@agents/sdk/providers/factory'
import type { ProviderManager } from '@agents/sdk/providers/manager'
import { createSkillOps } from './skill-ops-impl'

/**
 * Create a fully-configured ProviderManager with all providers registered.
 *
 * Delegates to SDK's createDefaultProviders with CLI-specific SkillOperations
 * wired via dependency injection.
 *
 * @param opts.cwd - Working directory for local providers (default: process.cwd())
 * @param opts.smitheryBaseUrl - Override Smithery API base URL
 */
export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ProviderManager {
  return createDefaultProviders({
    cwd: opts?.cwd,
    skillOps: createSkillOps(),
    smitheryBaseUrl: opts?.smitheryBaseUrl,
  })
}
