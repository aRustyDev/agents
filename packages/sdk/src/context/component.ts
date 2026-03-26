import type { Result } from '@agents/core/types'
import type { ComponentMetadata, ComponentType } from './types'

export interface ParsedComponent<T extends Record<string, unknown> = Record<string, unknown>> {
  readonly type: ComponentType
  readonly name: string
  readonly content: string
  readonly frontmatter: T
  readonly metadata: ComponentMetadata
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationIssue[]
  warnings: ValidationIssue[]
}

export interface ValidationIssue {
  path: string
  message: string
  severity: 'error' | 'warning'
}

export interface SchemaValidator<T> {
  validate(data: unknown): Result<T>
}
