import type { SkillOperations } from '@agents/sdk/providers/local/skill-ops'

/**
 * CLI implementation of SkillOperations.
 * Bridges SDK's DI interface to CLI's skill-*.ts modules via dynamic imports.
 */
export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      const { listSkills } = await import('../skill-list')
      return listSkills(opts)
    },
    async add(source, opts) {
      const { addSkill } = await import('../skill-add')
      return addSkill(source, opts)
    },
    async remove(names, opts) {
      const { removeSkills } = await import('../skill-remove')
      return removeSkills(names, opts)
    },
    async info(name, opts) {
      const { skillInfo } = await import('../skill-info')
      return skillInfo(name, opts)
    },
  }
}
