import { describe, expect, mock, test } from 'bun:test'
import {
  validateAgentFilter as _validateAgentFilter,
  filterByAgent,
  filterBySkill,
  type InstalledSkillEntry,
} from '@agents/sdk/providers/local/skill/filters'
import type { OutputFormatter } from '@agents/sdk/ui'
import { createCliAgentResolver } from '../src/lib/agents'

/** Convenience wrapper — auto-injects the CLI agent resolver. */
const validateAgentFilter = (agentName: string, out: OutputFormatter) =>
  _validateAgentFilter(agentName, out, createCliAgentResolver())

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

function entry(name: string, agents: string[] = []): InstalledSkillEntry {
  return {
    name,
    agents: agents as InstalledSkillEntry['agents'],
    source: `test/${name}`,
  }
}

function mockOutput(): OutputFormatter {
  return {
    table: mock(() => {}),
    success: mock(() => {}),
    error: mock(() => {}),
    warn: mock(() => {}),
    info: mock(() => {}),
    tree: mock(() => {}),
    ndjson: mock(() => {}),
    raw: mock(() => {}),
    spinner: mock(() => ({
      success: mock(() => {}),
      error: mock(() => {}),
      update: mock(() => {}),
    })),
  } as unknown as OutputFormatter
}

// ---------------------------------------------------------------------------
// filterByAgent
// ---------------------------------------------------------------------------

describe('filterByAgent', () => {
  const skills = [
    entry('beads', ['claude-code', 'cursor']),
    entry('gitlab-cicd', ['claude-code']),
    entry('pnpm', ['cursor', 'windsurf']),
    entry('solo', []),
  ]

  test('returns all skills when agentFilter is undefined', () => {
    const result = filterByAgent(skills)
    expect(result).toHaveLength(4)
  })

  test('returns all skills when agentFilter is empty string', () => {
    const result = filterByAgent(skills, '')
    expect(result).toHaveLength(4)
  })

  test('filters to only skills installed for a specific agent', () => {
    const result = filterByAgent(skills, 'claude-code')
    expect(result).toHaveLength(2)
    expect(result.map((s) => s.name).sort()).toEqual(['beads', 'gitlab-cicd'])
  })

  test('returns empty array when no skills match the agent', () => {
    const result = filterByAgent(skills, 'zed')
    expect(result).toHaveLength(0)
  })

  test('handles single agent match', () => {
    const result = filterByAgent(skills, 'windsurf')
    expect(result).toHaveLength(1)
    expect(result[0]!.name).toBe('pnpm')
  })
})

// ---------------------------------------------------------------------------
// filterBySkill
// ---------------------------------------------------------------------------

describe('filterBySkill', () => {
  const skills = [entry('beads'), entry('GitLab-CICD'), entry('pnpm')]

  test('returns all skills when skillFilter is undefined', () => {
    const result = filterBySkill(skills)
    expect(result).toHaveLength(3)
  })

  test('returns all skills when skillFilter is empty string', () => {
    const result = filterBySkill(skills, '')
    expect(result).toHaveLength(3)
  })

  test('matches skill name case-insensitively', () => {
    const result = filterBySkill(skills, 'gitlab-cicd')
    expect(result).toHaveLength(1)
    expect(result[0]!.name).toBe('GitLab-CICD')
  })

  test('returns empty array when skill name does not match', () => {
    const result = filterBySkill(skills, 'nonexistent')
    expect(result).toHaveLength(0)
  })

  test('exact match only (no partial matching)', () => {
    const result = filterBySkill(skills, 'bead')
    expect(result).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// validateAgentFilter
// ---------------------------------------------------------------------------

describe('validateAgentFilter', () => {
  test('returns true for a known agent', () => {
    const out = mockOutput()
    expect(validateAgentFilter('claude-code', out)).toBe(true)
    expect(out.warn).not.toHaveBeenCalled()
  })

  test('returns true for another known agent (cursor)', () => {
    const out = mockOutput()
    expect(validateAgentFilter('cursor', out)).toBe(true)
    expect(out.warn).not.toHaveBeenCalled()
  })

  test('returns false and warns for an unknown agent', () => {
    const out = mockOutput()
    expect(validateAgentFilter('unknown-agent-xyz', out)).toBe(false)
    expect(out.warn).toHaveBeenCalledTimes(1)
  })

  test('warning message mentions the unknown agent name', () => {
    const out = mockOutput()
    validateAgentFilter('fake-agent', out)
    const warnCall = (out.warn as ReturnType<typeof mock>).mock.calls[0]
    expect(warnCall[0]).toContain('fake-agent')
  })

  test('warning message lists some known agents', () => {
    const out = mockOutput()
    validateAgentFilter('nope', out)
    const warnCall = (out.warn as ReturnType<typeof mock>).mock.calls[0]
    expect(warnCall[0]).toContain('claude-code')
  })
})
