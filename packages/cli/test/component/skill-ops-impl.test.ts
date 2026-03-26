import { describe, expect, test } from 'bun:test'
import { createSkillOps } from '../../src/lib/component/skill-ops-impl'

describe('createSkillOps', () => {
  test('returns object with list, add, remove, info methods', () => {
    const ops = createSkillOps()
    expect(typeof ops.list).toBe('function')
    expect(typeof ops.add).toBe('function')
    expect(typeof ops.remove).toBe('function')
    expect(typeof ops.info).toBe('function')
  })

  test('returns exactly 4 methods', () => {
    const ops = createSkillOps()
    const keys = Object.keys(ops).sort()
    expect(keys).toEqual(['add', 'info', 'list', 'remove'])
  })
})
