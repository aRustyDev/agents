/**
 * Agent registry — 44 AI coding agents with config-directory detection.
 *
 * Data extracted from vercel-labs/skills v0.5.x (MIT license).
 */

import { existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
import * as v from 'valibot'
import { xdgConfig } from 'xdg-basedir'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

export const AgentType = v.picklist([
  'claude-code',
  'cursor',
  'windsurf',
  'gemini-cli',
  'codex',
  'amp',
  'aider',
  'cline',
  'roo-code',
  'continue',
  'copilot',
  'zed',
  'void',
  'pear',
  'aide',
  'trae',
  'junie',
  'kilo-code',
  'otto-coder',
  'wing',
  'melty',
  'goose',
  'augment',
  'sourcegraph-cody',
  'tabnine',
  'replit',
  'devin',
  'hex',
  'marscode',
  'codefuse',
  'bloop',
  'sweep',
  'mentat',
  'grit',
  'codegen',
  'ellipsis',
  'what-the-diff',
  'coderabbit',
  'bitbucket',
  'opendevin',
  'swe-agent',
  'acr',
  'agentless',
  'moatless-tools',
])

export type AgentType = v.InferOutput<typeof AgentType>

// ---------------------------------------------------------------------------
// AgentConfig
// ---------------------------------------------------------------------------

export interface AgentConfig {
  /** Machine identifier — matches the AgentType picklist value. */
  readonly name: AgentType
  /** Human-readable display name. */
  readonly displayName: string
  /** Project-relative skills directory (no leading /). */
  readonly skillsDir: string
  /** Absolute path to the global (user-level) skills directory. */
  readonly globalSkillsDir: string
  /** Whether the agent supports the universal skill format. */
  readonly universal: boolean
  /** Returns true if the agent appears to be installed on this machine. */
  detectInstalled(): boolean
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const home = homedir()
const xdg = xdgConfig ?? join(home, '.config')

function homeAgent(
  name: AgentType,
  displayName: string,
  skillsDir: string,
  globalSkillsDir: string,
  universal: boolean,
  detectDir: string
): AgentConfig {
  return {
    name,
    displayName,
    skillsDir,
    globalSkillsDir: join(home, globalSkillsDir),
    universal,
    detectInstalled: () => existsSync(join(home, detectDir)),
  }
}

function xdgAgent(
  name: AgentType,
  displayName: string,
  skillsDir: string,
  globalSkillsDir: string,
  universal: boolean,
  detectDir: string
): AgentConfig {
  return {
    name,
    displayName,
    skillsDir,
    globalSkillsDir: join(xdg, globalSkillsDir),
    universal,
    detectInstalled: () => existsSync(join(xdg, detectDir)),
  }
}

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

export const AGENT_CONFIGS: ReadonlyMap<AgentType, AgentConfig> = new Map<AgentType, AgentConfig>([
  [
    'claude-code',
    homeAgent('claude-code', 'Claude Code', '.claude/skills', '.claude/skills', true, '.claude'),
  ],
  ['cursor', homeAgent('cursor', 'Cursor', '.agents/skills', '.cursor/skills', true, '.cursor')],
  [
    'windsurf',
    homeAgent(
      'windsurf',
      'Windsurf',
      '.agents/skills',
      '.codeium/windsurf/skills',
      true,
      '.codeium'
    ),
  ],
  [
    'gemini-cli',
    homeAgent('gemini-cli', 'Gemini CLI', '.gemini/skills', '.gemini/skills', true, '.gemini'),
  ],
  ['codex', homeAgent('codex', 'Codex CLI', '.codex/skills', '.codex/skills', true, '.codex')],
  ['amp', xdgAgent('amp', 'Amp', '.agents/skills', 'agents/skills', true, 'amp')],
  ['aider', homeAgent('aider', 'Aider', '.aider/skills', '.aider/skills', false, '.aider')],
  ['cline', homeAgent('cline', 'Cline', '.agents/skills', '.cline/skills', true, '.cline')],
  [
    'roo-code',
    homeAgent('roo-code', 'Roo Code', '.agents/skills', '.roo-code/skills', true, '.roo-code'),
  ],
  [
    'continue',
    homeAgent('continue', 'Continue', '.continue/skills', '.continue/skills', false, '.continue'),
  ],
  [
    'copilot',
    homeAgent(
      'copilot',
      'GitHub Copilot',
      '.github/copilot/skills',
      '.config/github-copilot/skills',
      false,
      '.config/github-copilot'
    ),
  ],
  ['zed', homeAgent('zed', 'Zed', '.zed/skills', '.config/zed/skills', false, '.config/zed')],
  ['void', homeAgent('void', 'Void', '.void/skills', '.void/skills', true, '.void')],
  ['pear', homeAgent('pear', 'PearAI', '.pear/skills', '.pear/skills', true, '.pear')],
  ['aide', homeAgent('aide', 'Aide', '.aide/skills', '.aide/skills', true, '.aide')],
  ['trae', homeAgent('trae', 'Trae', '.trae/skills', '.trae/skills', true, '.trae')],
  [
    'junie',
    homeAgent('junie', 'JetBrains Junie', '.junie/skills', '.junie/skills', false, '.junie'),
  ],
  [
    'kilo-code',
    homeAgent('kilo-code', 'Kilo Code', '.agents/skills', '.kilo-code/skills', true, '.kilo-code'),
  ],
  [
    'otto-coder',
    homeAgent(
      'otto-coder',
      'Otto Coder',
      '.otto/skills',
      '.otto-coder/skills',
      false,
      '.otto-coder'
    ),
  ],
  ['wing', homeAgent('wing', 'Wing', '.wing/skills', '.wing/skills', false, '.wing')],
  ['melty', homeAgent('melty', 'Melty', '.melty/skills', '.melty/skills', false, '.melty')],
  ['goose', xdgAgent('goose', 'Goose', '.goose/skills', 'goose/skills', false, 'goose')],
  [
    'augment',
    homeAgent('augment', 'Augment', '.augment/skills', '.augment/skills', false, '.augment'),
  ],
  [
    'sourcegraph-cody',
    homeAgent(
      'sourcegraph-cody',
      'Sourcegraph Cody',
      '.cody/skills',
      '.sourcegraph-cody/skills',
      false,
      '.sourcegraph-cody'
    ),
  ],
  [
    'tabnine',
    homeAgent('tabnine', 'Tabnine', '.tabnine/skills', '.tabnine/skills', false, '.tabnine'),
  ],
  ['replit', homeAgent('replit', 'Replit', '.replit/skills', '.replit/skills', false, '.replit')],
  ['devin', homeAgent('devin', 'Devin', '.devin/skills', '.devin/skills', false, '.devin')],
  ['hex', homeAgent('hex', 'Hex', '.hex/skills', '.hex/skills', false, '.hex')],
  [
    'marscode',
    homeAgent('marscode', 'MarsCode', '.marscode/skills', '.marscode/skills', false, '.marscode'),
  ],
  [
    'codefuse',
    homeAgent('codefuse', 'CodeFuse', '.codefuse/skills', '.codefuse/skills', false, '.codefuse'),
  ],
  ['bloop', homeAgent('bloop', 'Bloop', '.bloop/skills', '.bloop/skills', false, '.bloop')],
  ['sweep', homeAgent('sweep', 'Sweep', '.sweep/skills', '.sweep/skills', false, '.sweep')],
  ['mentat', homeAgent('mentat', 'Mentat', '.mentat/skills', '.mentat/skills', false, '.mentat')],
  ['grit', homeAgent('grit', 'Grit', '.grit/skills', '.grit/skills', false, '.grit')],
  [
    'codegen',
    homeAgent('codegen', 'Codegen', '.codegen/skills', '.codegen/skills', false, '.codegen'),
  ],
  [
    'ellipsis',
    homeAgent('ellipsis', 'Ellipsis', '.ellipsis/skills', '.ellipsis/skills', false, '.ellipsis'),
  ],
  [
    'what-the-diff',
    homeAgent(
      'what-the-diff',
      'What The Diff',
      '.what-the-diff/skills',
      '.what-the-diff/skills',
      false,
      '.what-the-diff'
    ),
  ],
  [
    'coderabbit',
    homeAgent(
      'coderabbit',
      'CodeRabbit',
      '.coderabbit/skills',
      '.coderabbit/skills',
      false,
      '.coderabbit'
    ),
  ],
  [
    'bitbucket',
    homeAgent(
      'bitbucket',
      'Bitbucket',
      '.bitbucket/skills',
      '.bitbucket/skills',
      false,
      '.bitbucket'
    ),
  ],
  [
    'opendevin',
    homeAgent(
      'opendevin',
      'OpenDevin',
      '.opendevin/skills',
      '.opendevin/skills',
      false,
      '.opendevin'
    ),
  ],
  [
    'swe-agent',
    homeAgent(
      'swe-agent',
      'SWE-agent',
      '.swe-agent/skills',
      '.swe-agent/skills',
      false,
      '.swe-agent'
    ),
  ],
  ['acr', homeAgent('acr', 'ACR', '.acr/skills', '.acr/skills', false, '.acr')],
  [
    'agentless',
    homeAgent(
      'agentless',
      'Agentless',
      '.agentless/skills',
      '.agentless/skills',
      false,
      '.agentless'
    ),
  ],
  [
    'moatless-tools',
    homeAgent(
      'moatless-tools',
      'Moatless Tools',
      '.moatless/skills',
      '.moatless-tools/skills',
      false,
      '.moatless-tools'
    ),
  ],
])

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** All agent type identifiers. */
export const AGENT_TYPES: readonly AgentType[] = [...AGENT_CONFIGS.keys()]

/** Get the config for a specific agent. */
export function getAgentConfig(agentType: AgentType): AgentConfig {
  // biome-ignore lint/style/noNonNullAssertion: Map is populated from AGENT_TYPES — all keys guaranteed present
  return AGENT_CONFIGS.get(agentType)!
}

/** Return only agents whose config directory exists on this machine. */
export async function detectInstalledAgents(): Promise<AgentType[]> {
  return AGENT_TYPES.filter((t) => AGENT_CONFIGS.get(t)?.detectInstalled())
}

/** Return agents that support the universal skill format. */
export function getUniversalAgents(): AgentConfig[] {
  return AGENT_TYPES.filter((t) => AGENT_CONFIGS.get(t)?.universal).map(
    // biome-ignore lint/style/noNonNullAssertion: filtered from AGENT_TYPES — key guaranteed in Map
    (t) => AGENT_CONFIGS.get(t)!
  )
}

/** Return agents that do NOT support the universal skill format. */
export function getNonUniversalAgents(): AgentConfig[] {
  return AGENT_TYPES.filter((t) => !AGENT_CONFIGS.get(t)?.universal).map(
    // biome-ignore lint/style/noNonNullAssertion: filtered from AGENT_TYPES — key guaranteed in Map
    (t) => AGENT_CONFIGS.get(t)!
  )
}

/** Check whether a given agent supports the universal skill format. */
export function isUniversalAgent(agentType: AgentType): boolean {
  return AGENT_CONFIGS.get(agentType)?.universal
}

/**
 * Resolve the base skills directory for an agent.
 *
 * @param agentType  — Agent identifier
 * @param global     — true for user-level directory, false for project-scope
 * @param cwd        — Project working directory (used when global=false)
 */
export function getAgentBaseDir(
  agentType: AgentType,
  global: boolean,
  cwd: string
): Result<string> {
  const config = AGENT_CONFIGS.get(agentType)
  if (!config) {
    return err(
      new CliError(
        `Unknown agent type: ${agentType}`,
        'E_UNKNOWN_AGENT',
        `Valid agents: ${AGENT_TYPES.join(', ')}`
      )
    )
  }
  if (global) {
    return ok(config.globalSkillsDir)
  }
  return ok(join(cwd, config.skillsDir))
}
