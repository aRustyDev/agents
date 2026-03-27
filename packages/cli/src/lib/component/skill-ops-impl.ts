import type { SkillOperations } from '@agents/sdk/providers/local/skill-ops'
import { createCliAgentResolver } from '../agents'

const resolver = createCliAgentResolver()

/**
 * CLI implementation of SkillOperations.
 * Bridges SDK's DI interface to SDK's skill modules via the CLI agent resolver.
 */
export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      const { listSkills } = await import('@agents/sdk/providers/local/skill/list')
      return listSkills(resolver, opts)
    },
    async add(source, opts) {
      const { addSkill } = await import('@agents/sdk/providers/local/skill/add')
      return addSkill(resolver, source, opts)
    },
    async remove(names, opts) {
      const { removeSkills } = await import('@agents/sdk/providers/local/skill/remove')
      return removeSkills(resolver, names, opts)
    },
    async info(name, opts) {
      const { skillInfo } = await import('@agents/sdk/providers/local/skill/info')
      return skillInfo(resolver, name, opts)
    },
  }
}
