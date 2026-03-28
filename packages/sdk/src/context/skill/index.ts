import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseSkill } from './parser'
import { skillSchemaValidator } from './schema'
import type { SkillFrontmatter } from './types'

export const skillModule: ComponentTypeModule<SkillFrontmatter> = {
  type: 'skill',
  schema: skillSchemaValidator,
  parse: parseSkill,
  validate(component: ParsedComponent<SkillFrontmatter>): ValidationResult {
    const errors = []
    const warnings = []
    if (!component.frontmatter.name) {
      errors.push({
        path: 'frontmatter.name',
        message: 'name is required',
        severity: 'error' as const,
      })
    }
    if (!component.frontmatter.description) {
      errors.push({
        path: 'frontmatter.description',
        message: 'description is required',
        severity: 'error' as const,
      })
    }
    if (!component.frontmatter.tags || component.frontmatter.tags.length === 0) {
      warnings.push({
        path: 'frontmatter.tags',
        message: 'tags are recommended',
        severity: 'warning' as const,
      })
    }
    return { valid: errors.length === 0, errors, warnings }
  },
}

export { parseSkill } from './parser'
export {
  SkillFrontmatter,
  SkillFrontmatterSchema,
  skillSchemaValidator,
} from './schema'
export type { SkillFrontmatter as SkillFrontmatterType } from './types'
