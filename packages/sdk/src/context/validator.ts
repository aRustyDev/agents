import { err, ok, type Result } from '@agents/core/types'
import * as v from 'valibot'
import { SdkError } from '../util/errors'
import type { SchemaValidator } from './component'

export function createSchemaValidator<T>(
  schema: v.BaseSchema<unknown, T, v.BaseIssue<unknown>>
): SchemaValidator<T> {
  return {
    validate(data: unknown): Result<T> {
      const result = v.safeParse(schema, data)
      if (result.success) return ok(result.output)
      const msg = result.issues.map((i) => i.message).join('; ')
      return err(new SdkError(msg, 'E_SCHEMA_INVALID'))
    },
  }
}
