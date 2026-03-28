// Provider types

export type { McpServerEntry } from './clients/config'
export {
  formatServerConfig,
  listServersInClient,
  readClientConfig,
  removeServerFromClient,
  stripJsonComments,
  writeServerToClient,
} from './clients/config'
export type { ClientConfig, ClientFormat, ClientTransport, InstallMethod } from './clients/registry'
// Client registry
export {
  CLIENT_IDS,
  CLIENT_REGISTRY,
  getClientConfig,
  getConfigPath,
} from './clients/registry'
// Factory
export { createDefaultProviders } from './factory'
// GitHub
export { GitHubProvider } from './github'
export {
  buildComponentSearchQuery,
  buildSkillSearchQuery,
  buildTopicSearchQuery,
} from './github/search'
export * from './interface'
// Local providers
export { LocalSkillProvider } from './local'
export { LocalAgentProvider } from './local/agent'
export { LocalCommandProvider } from './local/command'
export { LocalOutputStyleProvider } from './local/output-style'
export { LocalPluginProvider } from './local/plugin'
export { LocalRuleProvider } from './local/rule'
export { ExternalSourcesManifest, LockfileV1 } from './local/schemas'
export type { SkillOperations } from './local/skill-ops'
// Manager
export { ComponentManager, ProviderManager } from './manager'
export * from './pagination'
// Smithery
export { SmitheryProvider } from './smithery'
export type { SmitheryAuth } from './smithery/auth'
export { resolveSmitheryAuth, validateSmitheryApiKey } from './smithery/auth'
export type { SmitheryPublishOptions } from './smithery/publish'
export { pollDeployment, publishToSmithery } from './smithery/publish'
