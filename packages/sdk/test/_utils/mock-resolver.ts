/**
 * Test-only AgentResolver that provides minimal defaults.
 *
 * Replaces the CLI's createCliAgentResolver() in SDK tests so they
 * don't depend on the full 44-agent CLI registry.
 */

import { homedir } from 'node:os'
import { join, resolve } from 'node:path'
import type { AgentConfig, AgentResolver } from '../../src/context/agent/config'

const PROJECT_ROOT = resolve(import.meta.dir, '../../../..')

function makeAgent(name: string, skillsDir: string, globalSkillsDir?: string): AgentConfig {
  return {
    name,
    displayName: name,
    skillsDir,
    globalSkillsDir: globalSkillsDir ?? join(homedir(), `.${name}`, 'skills'),
    universal: true,
    detectInstalled: () => true,
  }
}

/** Default agents matching the CLI's real agent registry (subset). */
const defaultAgents: AgentConfig[] = [
  makeAgent('claude-code', '.claude/skills', join(homedir(), '.claude/skills')),
  makeAgent('cursor', '.agents/skills', join(homedir(), '.cursor/skills')),
  makeAgent('windsurf', '.agents/skills', join(homedir(), '.codeium/windsurf/skills')),
  makeAgent('gemini-cli', '.gemini/skills', join(homedir(), '.gemini/skills')),
  makeAgent('codex', '.codex/skills', join(homedir(), '.codex/skills')),
]

/**
 * Create a test AgentResolver with configurable agents.
 *
 * If no agents are provided, returns a representative subset of 5 agents
 * matching the real CLI registry's directory layout.
 */
export function createMockResolver(agents: AgentConfig[] = defaultAgents): AgentResolver {
  return {
    list: () => agents,
    get: (name) => agents.find((a) => a.name === name),
    detectInstalled: () => agents.filter((a) => a.detectInstalled()),
    getUniversal: () => agents.filter((a) => a.universal),
    getBaseDir: (name, global, cwd) => {
      const agent = agents.find((a) => a.name === name)
      if (!agent) return undefined
      if (global) return agent.globalSkillsDir
      return resolve(cwd || PROJECT_ROOT, agent.skillsDir)
    },
  }
}
