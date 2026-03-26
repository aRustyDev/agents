import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseHook } from './parser'
import { hookSchemaValidator } from './schema'
import type { HookFrontmatter } from './types'

export const hookModule: ComponentTypeModule<HookFrontmatter> = {
  type: 'hook',
  schema: hookSchemaValidator,
  parse: parseHook,
  validate(component: ParsedComponent<HookFrontmatter>): ValidationResult {
    const errors = []
    if (!component.frontmatter.name) {
      errors.push({
        path: 'frontmatter.name',
        message: 'name is required',
        severity: 'error' as const,
      })
    }
    return { valid: errors.length === 0, errors, warnings: [] }
  },
}

export { parseHook } from './parser'
export { hookSchemaValidator } from './schema'
export type { HookFrontmatter } from './types'
