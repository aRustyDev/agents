import type { EngineOperator } from './types'

/**
 * Parse engine reference markdown files into operator lookup.
 * Pass 1: stub returning empty object.
 * Pass 2: will read references/engines/*.md and extract operator tables.
 */
export async function parseEngineReferences(
  _skillPath: string
): Promise<Record<string, EngineOperator[]>> {
  return {}
}
