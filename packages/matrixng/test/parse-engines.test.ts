import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'
import { parseEngineReferences } from '../src/parse-engines'

const WORKTREE = resolve(import.meta.dir, '../../..')
const SKILL_PATH = resolve(WORKTREE, 'content/skills/search-term-matrices')

describe('parseEngineReferences', () => {
  test('parses engine references from real skill files', async () => {
    const result = await parseEngineReferences(SKILL_PATH)
    const engines = Object.keys(result)
    expect(engines.length).toBeGreaterThan(10)
  })

  test('includes Google with standard operators', async () => {
    const result = await parseEngineReferences(SKILL_PATH)
    const google = result.Google
    expect(google).toBeDefined()
    expect(google?.length).toBeGreaterThan(5)
    const siteOp = google?.find((op) => op.operator.includes('site'))
    expect(siteOp).toBeDefined()
    expect(siteOp?.syntax).toContain('site:')
  })

  test('includes GitHub with code search operators', async () => {
    const result = await parseEngineReferences(SKILL_PATH)
    const github = result.GitHub
    expect(github).toBeDefined()
    const langOp = github?.find(
      (op) => op.operator.includes('language') || op.operator.includes('Language')
    )
    expect(langOp).toBeDefined()
  })

  test('each operator has all required fields', async () => {
    const result = await parseEngineReferences(SKILL_PATH)
    for (const [engine, operators] of Object.entries(result)) {
      for (const op of operators) {
        expect(op.engine).toBe(engine)
        expect(op.operator.length).toBeGreaterThan(0)
        expect(op.syntax.length).toBeGreaterThan(0)
      }
    }
  })
})
