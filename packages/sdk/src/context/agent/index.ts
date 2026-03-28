import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseAgent } from './parser'
import { agentSchemaValidator } from './schema'
import type { AgentFrontmatter } from './types'

export const agentModule: ComponentTypeModule<AgentFrontmatter> = {
  type: 'agent',
  schema: agentSchemaValidator,
  parse: parseAgent,
  validate(component: ParsedComponent<AgentFrontmatter>): ValidationResult {
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

export { parseAgent } from './parser'
export { agentSchemaValidator } from './schema'
export type { AgentFrontmatter } from './types'
