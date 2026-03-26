import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseOutputStyle } from './parser'
import { outputStyleSchemaValidator } from './schema'
import type { OutputStyleFrontmatter } from './types'

export const outputStyleModule: ComponentTypeModule<OutputStyleFrontmatter> = {
  type: 'output-style',
  schema: outputStyleSchemaValidator,
  parse: parseOutputStyle,
  validate(component: ParsedComponent<OutputStyleFrontmatter>): ValidationResult {
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

export { parseOutputStyle } from './parser'
export { outputStyleSchemaValidator } from './schema'
export type { OutputStyleFrontmatter } from './types'
