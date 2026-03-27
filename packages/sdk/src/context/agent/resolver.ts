/**
 * Default AgentResolver implementation backed by a static list of configs.
 *
 * Useful for testing or for consumers who define their own agent set.
 */

import type { AgentConfig, AgentResolver } from './config'

/**
 * Create an AgentResolver from a static list of configs.
 * Useful for testing or for consumers who define their own agent set.
 */
export function createAgentResolver(configs: AgentConfig[]): AgentResolver {
  const byName = new Map(configs.map((c) => [c.name, c]))
  return {
    list: () => configs,
    get: (name) => byName.get(name),
    detectInstalled: () => configs.filter((c) => c.detectInstalled()),
    getUniversal: () => configs.filter((c) => c.universal),
    getBaseDir: (name, global, cwd) => {
      const config = byName.get(name)
      if (!config) return undefined
      return global ? config.globalSkillsDir : `${cwd}/${config.skillsDir}`
    },
  }
}
