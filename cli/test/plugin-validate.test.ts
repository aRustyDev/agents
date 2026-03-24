import { describe, expect, test } from 'bun:test'
import { validateMarketplace } from '../commands/plugin'

// ---------------------------------------------------------------------------
// validateMarketplace — tested against real marketplace.json
// ---------------------------------------------------------------------------

describe('validateMarketplace', () => {
  test('validates real marketplace.json successfully', async () => {
    const result = await validateMarketplace()
    expect(result.plugin).toBe('marketplace')
    // The real file should parse without schema errors
    // There may be warnings (e.g., source paths not found in worktree)
    // but the schema validation itself should succeed
    expect(result.errors.filter((e) => e.startsWith('Schema error'))).toHaveLength(0)
    expect(result.errors.filter((e) => e.startsWith('Invalid JSON'))).toHaveLength(0)
    expect(result.errors.filter((e) => e.startsWith('Duplicate plugin name'))).toHaveLength(0)
  })

  test('detects no duplicate plugin names in real marketplace', async () => {
    const result = await validateMarketplace()
    const dupeErrors = result.errors.filter((e) => e.startsWith('Duplicate plugin name'))
    expect(dupeErrors).toHaveLength(0)
  })
})
