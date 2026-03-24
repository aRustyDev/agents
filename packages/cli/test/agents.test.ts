import { describe, expect, test } from 'bun:test'
import { homedir } from 'node:os'
import { join } from 'node:path'
import * as v from 'valibot'
import { xdgConfig } from 'xdg-basedir'
import {
  AGENT_CONFIGS,
  AGENT_TYPES,
  type AgentConfig,
  AgentType,
  detectInstalledAgents,
  getAgentBaseDir,
  getAgentConfig,
  getNonUniversalAgents,
  getUniversalAgents,
  isUniversalAgent,
} from '../src/lib/agents'

const home = homedir()
const xdg = xdgConfig ?? join(home, '.config')

// ---------------------------------------------------------------------------
// Registry size
// ---------------------------------------------------------------------------

describe('agent registry size', () => {
  test('AgentType picklist has exactly 44 options', () => {
    expect(AgentType.options).toHaveLength(44)
  })

  test('AGENT_CONFIGS map has exactly 44 entries', () => {
    expect(AGENT_CONFIGS.size).toBe(44)
  })

  test('AGENT_TYPES array has exactly 44 entries', () => {
    expect(AGENT_TYPES).toHaveLength(44)
  })

  test('every picklist option has a config entry', () => {
    for (const opt of AgentType.options) {
      expect(AGENT_CONFIGS.has(opt)).toBe(true)
    }
  })

  test('every config key is a valid picklist option', () => {
    for (const key of AGENT_CONFIGS.keys()) {
      const result = v.safeParse(AgentType, key)
      expect(result.success).toBe(true)
    }
  })
})

// ---------------------------------------------------------------------------
// claude-code config
// ---------------------------------------------------------------------------

describe('claude-code config', () => {
  const config = getAgentConfig('claude-code')

  test('name matches key', () => {
    expect(config.name).toBe('claude-code')
  })

  test('displayName is Claude Code', () => {
    expect(config.displayName).toBe('Claude Code')
  })

  test('skillsDir is .claude/skills', () => {
    expect(config.skillsDir).toBe('.claude/skills')
  })

  test('globalSkillsDir resolves under home', () => {
    expect(config.globalSkillsDir).toBe(join(home, '.claude/skills'))
  })

  test('is universal', () => {
    expect(config.universal).toBe(true)
  })

  test('detectInstalled is a function', () => {
    expect(typeof config.detectInstalled).toBe('function')
  })
})

// ---------------------------------------------------------------------------
// AgentConfig field invariants
// ---------------------------------------------------------------------------

describe('AgentConfig field invariants', () => {
  for (const [key, config] of AGENT_CONFIGS) {
    test(`${key}: name matches map key`, () => {
      expect(config.name).toBe(key)
    })

    test(`${key}: displayName is non-empty string`, () => {
      expect(typeof config.displayName).toBe('string')
      expect(config.displayName.length).toBeGreaterThan(0)
    })

    test(`${key}: skillsDir is a relative path`, () => {
      expect(config.skillsDir).not.toMatch(/^\//)
      expect(config.skillsDir).not.toMatch(/^~/)
      expect(config.skillsDir.length).toBeGreaterThan(0)
    })

    test(`${key}: globalSkillsDir is an absolute path`, () => {
      expect(config.globalSkillsDir.startsWith('/')).toBe(true)
    })

    test(`${key}: universal is a boolean`, () => {
      expect(typeof config.universal).toBe('boolean')
    })

    test(`${key}: detectInstalled is a function`, () => {
      expect(typeof config.detectInstalled).toBe('function')
    })
  }
})

// ---------------------------------------------------------------------------
// XDG-aware agents
// ---------------------------------------------------------------------------

describe('XDG-aware agents', () => {
  test('amp globalSkillsDir uses XDG config path', () => {
    const config = getAgentConfig('amp')
    expect(config.globalSkillsDir).toBe(join(xdg, 'agents/skills'))
  })

  test('goose globalSkillsDir uses XDG config path', () => {
    const config = getAgentConfig('goose')
    expect(config.globalSkillsDir).toBe(join(xdg, 'goose/skills'))
  })
})

// ---------------------------------------------------------------------------
// detectInstalledAgents
// ---------------------------------------------------------------------------

describe('detectInstalledAgents', () => {
  test('returns an array of valid AgentType values', async () => {
    const installed = await detectInstalledAgents()
    expect(Array.isArray(installed)).toBe(true)
    for (const agent of installed) {
      const result = v.safeParse(AgentType, agent)
      expect(result.success).toBe(true)
    }
  })

  test('installed count does not exceed total agents', async () => {
    const installed = await detectInstalledAgents()
    expect(installed.length).toBeLessThanOrEqual(44)
  })
})

// ---------------------------------------------------------------------------
// getAgentBaseDir
// ---------------------------------------------------------------------------

describe('getAgentBaseDir', () => {
  test('project-scope resolves relative to cwd', () => {
    const result = getAgentBaseDir('claude-code', false, '/tmp/my-project')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('/tmp/my-project/.claude/skills')
    }
  })

  test('global-scope returns absolute globalSkillsDir', () => {
    const result = getAgentBaseDir('claude-code', true, '/tmp/my-project')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe(join(home, '.claude/skills'))
    }
  })

  test('project-scope for cursor uses .agents/skills', () => {
    const result = getAgentBaseDir('cursor', false, '/workspace')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('/workspace/.agents/skills')
    }
  })

  test('global-scope for amp uses XDG path', () => {
    const result = getAgentBaseDir('amp', true, '/workspace')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe(join(xdg, 'agents/skills'))
    }
  })

  test('returns error for unknown agent', () => {
    // Force an invalid value past the type system for the runtime check
    const result = getAgentBaseDir('nonexistent-agent' as AgentType, false, '/tmp')
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_UNKNOWN_AGENT')
      expect(result.error.hint).toBeDefined()
    }
  })
})

// ---------------------------------------------------------------------------
// Universal / non-universal partitioning
// ---------------------------------------------------------------------------

describe('universal / non-universal partitioning', () => {
  const universal = getUniversalAgents()
  const nonUniversal = getNonUniversalAgents()

  test('universal + non-universal covers all agents', () => {
    expect(universal.length + nonUniversal.length).toBe(44)
  })

  test('sets are disjoint (no overlap)', () => {
    const universalNames = new Set(universal.map((a) => a.name))
    const nonUniversalNames = new Set(nonUniversal.map((a) => a.name))
    for (const name of universalNames) {
      expect(nonUniversalNames.has(name)).toBe(false)
    }
  })

  test('every universal agent has universal=true', () => {
    for (const agent of universal) {
      expect(agent.universal).toBe(true)
    }
  })

  test('every non-universal agent has universal=false', () => {
    for (const agent of nonUniversal) {
      expect(agent.universal).toBe(false)
    }
  })
})

// ---------------------------------------------------------------------------
// isUniversalAgent
// ---------------------------------------------------------------------------

describe('isUniversalAgent', () => {
  test('returns true for known universal agents', () => {
    expect(isUniversalAgent('claude-code')).toBe(true)
    expect(isUniversalAgent('cursor')).toBe(true)
    expect(isUniversalAgent('windsurf')).toBe(true)
    expect(isUniversalAgent('amp')).toBe(true)
  })

  test('returns false for known non-universal agents', () => {
    expect(isUniversalAgent('aider')).toBe(false)
    expect(isUniversalAgent('continue')).toBe(false)
    expect(isUniversalAgent('copilot')).toBe(false)
    expect(isUniversalAgent('goose')).toBe(false)
  })

  test('isUniversalAgent agrees with getUniversalAgents', () => {
    const universalNames = new Set(getUniversalAgents().map((a) => a.name))
    for (const agentType of AGENT_TYPES) {
      expect(isUniversalAgent(agentType)).toBe(universalNames.has(agentType))
    }
  })
})

// ---------------------------------------------------------------------------
// Specific agent configs (spot checks)
// ---------------------------------------------------------------------------

describe('specific agent configs', () => {
  test('windsurf detects via ~/.codeium', () => {
    const config = getAgentConfig('windsurf')
    expect(config.globalSkillsDir).toBe(join(home, '.codeium/windsurf/skills'))
  })

  test('copilot uses .github/copilot/skills locally', () => {
    const config = getAgentConfig('copilot')
    expect(config.skillsDir).toBe('.github/copilot/skills')
    expect(config.globalSkillsDir).toBe(join(home, '.config/github-copilot/skills'))
  })

  test('zed uses .config/zed globally', () => {
    const config = getAgentConfig('zed')
    expect(config.globalSkillsDir).toBe(join(home, '.config/zed/skills'))
  })

  test('moatless-tools uses .moatless locally, .moatless-tools globally', () => {
    const config = getAgentConfig('moatless-tools')
    expect(config.skillsDir).toBe('.moatless/skills')
    expect(config.globalSkillsDir).toBe(join(home, '.moatless-tools/skills'))
  })

  test('sourcegraph-cody uses .cody locally', () => {
    const config = getAgentConfig('sourcegraph-cody')
    expect(config.skillsDir).toBe('.cody/skills')
  })

  test('otto-coder uses .otto locally, .otto-coder globally', () => {
    const config = getAgentConfig('otto-coder')
    expect(config.skillsDir).toBe('.otto/skills')
    expect(config.globalSkillsDir).toBe(join(home, '.otto-coder/skills'))
  })
})
