/**
 * Ajv-based validation for graph JSON data.
 *
 * Validates graph files against the JSON Schema contract defined in
 * `.data/graphs/schemas/graph.schema.json`. This schema encodes the
 * structural agreement between the AI agent (which writes JSON) and
 * the graph viewer UI (which renders it).
 */

import Ajv from 'ajv'
import addFormats from 'ajv-formats'

// ---------------------------------------------------------------------------
// Schema definition (inlined for zero-IO validation)
// ---------------------------------------------------------------------------

/**
 * The graph JSON Schema, inlined to avoid filesystem reads during validation.
 * This must stay in sync with `.data/graphs/schemas/graph.schema.json`.
 */
const GRAPH_SCHEMA = {
  // $schema omitted — Ajv draft-07 does not recognize the 2020-12 meta-schema URI.
  // The on-disk schema.json retains $schema for editor tooling; this inlined copy
  // strips it so Ajv can compile without error.
  title: 'Graph Data',
  type: 'object' as const,
  required: ['metadata', 'nodes', 'edges'],
  properties: {
    metadata: {
      type: 'object' as const,
      required: ['id', 'version'],
      properties: {
        id: { type: 'string' as const },
        version: { type: 'integer' as const, minimum: 1 },
        created: { type: 'string' as const, format: 'date-time' },
        modified: { type: 'string' as const, format: 'date-time' },
      },
    },
    nodes: {
      type: 'array' as const,
      items: {
        type: 'object' as const,
        required: ['id', 'type', 'label'],
        properties: {
          id: { type: 'string' as const, pattern: '^node-[a-zA-Z0-9_-]+$' },
          type: {
            type: 'string' as const,
            enum: ['Concept', 'Component', 'Document', 'Fragment'],
          },
          label: { type: 'string' as const, minLength: 1 },
          properties: { type: 'object' as const },
        },
      },
    },
    edges: {
      type: 'array' as const,
      items: {
        type: 'object' as const,
        required: ['id', 'source', 'target', 'type'],
        properties: {
          id: { type: 'string' as const, pattern: '^edge-[a-zA-Z0-9_-]+$' },
          source: { type: 'string' as const },
          target: { type: 'string' as const },
          type: {
            type: 'string' as const,
            enum: ['depends_on', 'relates_to', 'contains'],
          },
          properties: { type: 'object' as const },
        },
      },
    },
  },
} as const

// ---------------------------------------------------------------------------
// Ajv instance (singleton, created once)
// ---------------------------------------------------------------------------

const ajv = new Ajv({ allErrors: true })
addFormats(ajv)

const validate = ajv.compile(GRAPH_SCHEMA)

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Result of graph data validation. */
export interface ValidationResult {
  readonly valid: boolean
  readonly errors?: string[]
}

/**
 * Validate unknown data against the graph JSON Schema.
 *
 * Returns `{ valid: true }` on success, or `{ valid: false, errors: [...] }`
 * with human-readable error messages on failure.
 *
 * @param data - The data to validate (typically parsed from a JSON file).
 */
export function validateGraphData(data: unknown): ValidationResult {
  const valid = validate(data)

  if (valid) {
    return { valid: true }
  }

  const errors = (validate.errors ?? []).map((err) => {
    const path = err.instancePath || '(root)'
    const message = err.message ?? 'unknown error'
    const params = err.params
      ? ` (${Object.entries(err.params)
          .map(([k, v]) => `${k}: ${String(v)}`)
          .join(', ')})`
      : ''
    return `${path}: ${message}${params}`
  })

  return { valid: false, errors }
}
