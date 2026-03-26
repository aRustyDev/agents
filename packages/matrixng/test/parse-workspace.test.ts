import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'
import { parseWorkspace } from '../src/parse-workspace'

const WORKTREE = resolve(import.meta.dir, '../../..')
const WORKSPACE = resolve(WORKTREE, 'content/skills/search-term-matrices-workspace')

describe('parseWorkspace', () => {
  test('parses iteration-1 with 3 evals', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    expect(result.evals).toHaveLength(3)
    expect(result.benchmark).toBeDefined()
    expect(result.benchmark.configurations).toHaveLength(2)
  })

  test('each eval has both configurations', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    for (const ev of result.evals) {
      expect(ev.configurations.with_skill).toBeDefined()
      expect(ev.configurations.without_skill).toBeDefined()
      expect(ev.configurations.with_skill.raw.length).toBeGreaterThan(0)
      expect(ev.configurations.without_skill.raw.length).toBeGreaterThan(0)
    }
  })

  test('grading data is populated', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    const eval1 = result.evals.find((e) => e.evalId === 1)
    expect(eval1).toBeDefined()
    expect(eval1?.configurations.with_skill.grading.pass_rate).toBe(1.0)
    expect(eval1?.configurations.with_skill.grading.expectations.length).toBeGreaterThan(0)
  })

  test('timing data is populated', async () => {
    const result = await parseWorkspace(WORKSPACE, 1)
    const eval1 = result.evals.find((e) => e.evalId === 1)
    expect(eval1).toBeDefined()
    expect(eval1?.configurations.with_skill.timing.total_tokens).toBeGreaterThan(0)
    expect(eval1?.configurations.with_skill.timing.duration_ms).toBeGreaterThan(0)
  })

  test('auto-detects latest iteration when not specified', async () => {
    const result = await parseWorkspace(WORKSPACE)
    expect(result.evals.length).toBeGreaterThan(0)
  })
})
