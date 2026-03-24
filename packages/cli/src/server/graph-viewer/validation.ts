/**
 * Server-side validation wrapper.
 *
 * Re-exports the core `validateGraphData` function from `lib/graph-schema.ts`
 * under a shorter name for use in route handlers. Keeping the actual schema
 * definition and Ajv compilation in the shared library avoids duplicating the
 * schema across server and CLI entry points.
 */

import { type ValidationResult, validateGraphData } from '../../lib/graph-schema'

/**
 * Validate unknown data against the graph JSON Schema.
 *
 * @param data - The data to validate (typically parsed from a request body).
 * @returns `{ valid: true }` on success, or `{ valid: false, errors: [...] }`.
 */
export function validateGraph(data: unknown): ValidationResult {
  return validateGraphData(data)
}
