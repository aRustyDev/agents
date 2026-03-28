import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseRule } from './parser'
import { ruleSchemaValidator } from './schema'
import type { RuleFrontmatter } from './types'

export const ruleModule: ComponentTypeModule<RuleFrontmatter> = {
  type: 'rule',
  schema: ruleSchemaValidator,
  parse: parseRule,
  validate(component: ParsedComponent<RuleFrontmatter>): ValidationResult {
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
      warnings.push({
        path: 'frontmatter.description',
        message: 'description is recommended',
        severity: 'warning' as const,
      })
    }
    return { valid: errors.length === 0, errors, warnings }
  },
}

export { parseRule } from './parser'
export { ruleSchemaValidator } from './schema'
export type { RuleFrontmatter } from './types'
