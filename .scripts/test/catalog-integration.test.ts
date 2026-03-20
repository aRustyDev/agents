// .scripts/test/catalog-integration.test.ts
import { describe, expect, it } from 'bun:test'
import { downloadSkill } from '../lib/catalog-download'

describe('catalog-download integration', () => {
  it('downloads a real public skill (0x2e/superpowers@systematic-debugging)', async () => {
    const result = await downloadSkill('0x2e/superpowers', 'systematic-debugging', {
      timeout: 60_000,
    })

    expect(result.path).toBeTruthy()
    expect(result.contentHash).toMatch(/^sha256:[a-f0-9]{64}$/)
    expect(result.wordCount).toBeGreaterThan(100)
    expect(result.error).toBeUndefined()
  }, 90_000)

  it('returns structured error for nonexistent repo', async () => {
    const result = await downloadSkill(
      'definitely-not-a-real-org/nonexistent-repo-12345',
      'fake-skill',
      { timeout: 30_000 }
    )

    expect(result.path).toBeNull()
    expect(result.error).toBeDefined()
    expect(result.errorType).toBe('download_failed')
    expect(result.errorDetail).toBeDefined()
  }, 60_000)
})
