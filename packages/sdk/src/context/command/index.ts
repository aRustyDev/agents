import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseCommand } from './parser'
import { commandSchemaValidator } from './schema'
import type { CommandFrontmatter } from './types'

export const commandModule: ComponentTypeModule<CommandFrontmatter> = {
  type: 'command',
  schema: commandSchemaValidator,
  parse: parseCommand,
  validate(component: ParsedComponent<CommandFrontmatter>): ValidationResult {
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

export { parseCommand } from './parser'
export { commandSchemaValidator } from './schema'
export type { CommandFrontmatter } from './types'
