# Phase 1: Foundation Modules

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** TBD

## Objective

Create the five new library modules that all subsequent phases depend on: source parser, agent registry, git wrapper, skill discovery, and interactive prompts.

## Success Criteria

- [ ] `lib/source-parser.ts` parses all supported formats with test coverage on every format variant
- [ ] `lib/agents.ts` contains registry of 44+ agents with `detectInstalled()` (config dir check) and path resolution
- [ ] `lib/git.ts` provides shallow clone with ref support, temp dir lifecycle, timeout, `lsRemote`, and `fetchSkillFolderHash`
- [ ] `lib/skill-discovery.ts` recursively finds SKILL.md files with depth limit and plugin manifest awareness
- [ ] `lib/prompts/` provides searchable multiselect, confirmation, and fzf-style search prompts
- [ ] All modules have Valibot schemas in `lib/schemas.ts` for their data types
- [ ] All modules use `lib/runtime.ts` shims (no direct Bun API usage)
- [ ] `bun test` passes for all new modules

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Source parser module | `.scripts/lib/source-parser.ts` | TypeScript |
| Source parser tests | `.scripts/test/source-parser.test.ts` | bun:test |
| Agent registry module | `.scripts/lib/agents.ts` | TypeScript |
| Agent registry tests | `.scripts/test/agents.test.ts` | bun:test |
| Git wrapper module | `.scripts/lib/git.ts` | TypeScript |
| Git wrapper tests | `.scripts/test/git.test.ts` | bun:test |
| Skill discovery module | `.scripts/lib/skill-discovery.ts` | TypeScript |
| Skill discovery tests | `.scripts/test/skill-discovery.test.ts` | bun:test |
| Prompt library | `.scripts/lib/prompts/index.ts` | TypeScript |
| Prompt: search multiselect | `.scripts/lib/prompts/search-multiselect.ts` | TypeScript |
| Prompt: confirm | `.scripts/lib/prompts/confirm.ts` | TypeScript |
| Schema additions | `.scripts/lib/schemas.ts` | TypeScript (additions) |

## Files

**Create:**
- `.scripts/lib/source-parser.ts`
- `.scripts/lib/agents.ts`
- `.scripts/lib/git.ts`
- `.scripts/lib/skill-discovery.ts`
- `.scripts/lib/prompts/index.ts`
- `.scripts/lib/prompts/search-multiselect.ts`
- `.scripts/lib/prompts/confirm.ts`
- `.scripts/test/source-parser.test.ts`
- `.scripts/test/agents.test.ts`
- `.scripts/test/git.test.ts`
- `.scripts/test/skill-discovery.test.ts`

**Modify:**
- `.scripts/lib/schemas.ts` (add `ParsedSource`, `AgentType`, `AgentConfig` schemas)

## Tasks

### 1.1 Source Parser (`lib/source-parser.ts`)

- [ ] Define `ParsedSource` type: `{ type, url, subpath?, ref?, skillFilter?, localPath? }`
- [ ] Supported types: `github`, `gitlab`, `git`, `local`, `well-known`
- [ ] Parse formats (test matrix below)
- [ ] Export `getOwnerRepo(parsed)` -> `owner/repo` or null
- [ ] Export `sanitizeSubpath(path)` -> rejects `..` segments
- [ ] Add `ParsedSource` Valibot schema to `schemas.ts`
- [ ] Write tests for every format variant

**Source parser test matrix:**

| Input | type | url | ref | subpath | skillFilter |
|-------|------|-----|-----|---------|-------------|
| `owner/repo` | github | `https://github.com/owner/repo.git` | - | - | - |
| `owner/repo@skill-name` | github | `https://github.com/owner/repo.git` | - | - | `skill-name` |
| `owner/repo#main` | github | `https://github.com/owner/repo.git` | `main` | - | - |
| `owner/repo#v1.2.3` | github | `https://github.com/owner/repo.git` | `v1.2.3` | - | - |
| `owner/repo#abc1234` | github | `https://github.com/owner/repo.git` | `abc1234` | - | - |
| `owner/repo#main:skills/foo` | github | `https://github.com/owner/repo.git` | `main` | `skills/foo` | - |
| `owner/repo#main:skills/foo@bar` | github | `https://github.com/owner/repo.git` | `main` | `skills/foo` | `bar` |
| `github.com/o/r/tree/branch/path` | github | `https://github.com/o/r.git` | `branch` | `path` | - |
| `gitlab.com/o/r/-/tree/branch/path` | gitlab | `https://gitlab.com/o/r.git` | `branch` | `path` | - |
| `./local/path` | local | - | - | - | - |
| `/absolute/path` | local | - | - | - | - |
| `https://example.com/skills` | well-known | `https://example.com/skills` | - | - | - |
| `git@host:repo.git` | git | `git@host:repo.git` | - | - | - |
| `https://host/repo.git` | git | `https://host/repo.git` | - | - | - |

#### Task Dependencies

Depends on: none (first module, only depends on existing `lib/schemas.ts` and `lib/types.ts`)

#### Library Decisions

**No external dependencies.** The parser is entirely regex-based string manipulation. The input format `owner/repo#ref:subpath@skillFilter` is a custom DSL specific to this project -- no npm package exists for it. Regular expressions and `URL` constructor are sufficient for all parsing needs.

#### Error Types

```typescript
import { CliError } from './types'

/**
 * Error thrown when a source string cannot be parsed into any known format.
 *
 * @example
 * ```
 * error[E_INVALID_SOURCE]: Cannot parse source: ":::bad"
 *   hint: Expected owner/repo, local path, or URL
 * ```
 */
// Code: E_INVALID_SOURCE
// Hint: "Expected owner/repo, ./local/path, or https:// URL"

/**
 * Error thrown when a subpath contains path traversal segments.
 *
 * @example
 * ```
 * error[E_UNSAFE_SUBPATH]: Subpath contains ".." traversal: "../../../etc/passwd"
 *   hint: Subpaths must not contain ".." segments
 * ```
 */
// Code: E_UNSAFE_SUBPATH
// Hint: "Subpaths must not contain '..' segments"
```

#### Code Examples

```typescript
// .scripts/lib/source-parser.ts
import * as v from 'valibot'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Types & schemas
// ---------------------------------------------------------------------------

/** The kind of remote hosting platform or local reference. */
export const SourceType = v.picklist(['github', 'gitlab', 'git', 'local', 'well-known'])
export type SourceType = v.InferOutput<typeof SourceType>

/** A fully parsed skill source reference. */
export const ParsedSource = v.object({
  type: SourceType,
  url: v.optional(v.string()),
  ref: v.optional(v.string()),
  subpath: v.optional(v.string()),
  skillFilter: v.optional(v.string()),
  localPath: v.optional(v.string()),
})
export type ParsedSource = v.InferOutput<typeof ParsedSource>

// ---------------------------------------------------------------------------
// Regex patterns (no external deps)
// ---------------------------------------------------------------------------

/** Matches `owner/repo` with optional `#ref`, `:subpath`, and `@skill`. */
const SHORT_RE = /^([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+)(?:#([^:@]+))?(?::([^@]+))?(?:@(.+))?$/

/** Matches `github.com/owner/repo/tree/branch/path`. */
const GITHUB_TREE_RE = /^(?:https?:\/\/)?github\.com\/([^/]+\/[^/]+)\/tree\/([^/]+)(?:\/(.+))?$/

/** Matches `gitlab.com/owner/repo/-/tree/branch/path`. */
const GITLAB_TREE_RE = /^(?:https?:\/\/)?gitlab\.com\/([^/]+\/[^/]+)\/-\/tree\/([^/]+)(?:\/(.+))?$/

/** Matches SSH git URLs: `git@host:repo.git`. */
const SSH_RE = /^git@[^:]+:.+\.git$/

/** Matches HTTPS git URLs ending in `.git`. */
const HTTPS_GIT_RE = /^https?:\/\/.+\.git$/

/** Matches local paths: `./...` or `/...`. */
const LOCAL_RE = /^[./]/

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Parse a skill source string into a structured representation.
 *
 * Format: `owner/repo#ref:subpath@skillFilter`
 * - `#` separates the git ref (branch, tag, SHA)
 * - `:` separates the subpath within the repo
 * - `@` separates the skill name filter
 *
 * Also supports full GitHub/GitLab tree URLs, SSH URLs, local paths,
 * and arbitrary HTTPS URLs (well-known).
 *
 * @param source - Raw source string from CLI or manifest
 * @returns Parsed source or an error
 */
export function parseSource(source: string): Result<ParsedSource> {
  const trimmed = source.trim()
  if (!trimmed) {
    return err(new CliError('Empty source string', 'E_INVALID_SOURCE', 'Provide a non-empty source'))
  }

  // Local path
  if (LOCAL_RE.test(trimmed)) {
    return ok({ type: 'local' as const, localPath: trimmed })
  }

  // GitHub tree URL
  const ghTree = GITHUB_TREE_RE.exec(trimmed)
  if (ghTree) {
    return ok({
      type: 'github' as const,
      url: `https://github.com/${ghTree[1]}.git`,
      ref: ghTree[2],
      subpath: ghTree[3],
    })
  }

  // GitLab tree URL
  const glTree = GITLAB_TREE_RE.exec(trimmed)
  if (glTree) {
    return ok({
      type: 'gitlab' as const,
      url: `https://gitlab.com/${glTree[1]}.git`,
      ref: glTree[2],
      subpath: glTree[3],
    })
  }

  // SSH git URL
  if (SSH_RE.test(trimmed)) {
    return ok({ type: 'git' as const, url: trimmed })
  }

  // HTTPS .git URL (not GitHub/GitLab tree)
  if (HTTPS_GIT_RE.test(trimmed)) {
    return ok({ type: 'git' as const, url: trimmed })
  }

  // Short form: owner/repo#ref:subpath@skill
  const short = SHORT_RE.exec(trimmed)
  if (short) {
    const parsed: ParsedSource = {
      type: 'github',
      url: `https://github.com/${short[1]}.git`,
    }
    if (short[2]) parsed.ref = short[2]
    if (short[3]) {
      const subResult = sanitizeSubpath(short[3])
      if (!subResult.ok) return subResult
      parsed.subpath = subResult.value
    }
    if (short[4]) parsed.skillFilter = short[4]
    return ok(parsed)
  }

  // Well-known HTTPS URL (no .git suffix)
  if (trimmed.startsWith('https://') || trimmed.startsWith('http://')) {
    return ok({ type: 'well-known' as const, url: trimmed })
  }

  return err(
    new CliError(
      `Cannot parse source: "${trimmed}"`,
      'E_INVALID_SOURCE',
      'Expected owner/repo, ./local/path, or https:// URL',
    ),
  )
}

/**
 * Extract `owner/repo` from a parsed source, if available.
 *
 * @param parsed - A previously parsed source
 * @returns `owner/repo` string or null for non-GitHub/GitLab sources
 */
export function getOwnerRepo(parsed: ParsedSource): string | null {
  if (!parsed.url) return null
  const match = parsed.url.match(/(?:github|gitlab)\.com\/([^/]+\/[^/]+?)(?:\.git)?$/)
  return match?.[1] ?? null
}

/**
 * Validate and normalize a subpath, rejecting directory traversal.
 *
 * @param subpath - Raw subpath string
 * @returns Sanitized subpath or an error
 */
export function sanitizeSubpath(subpath: string): Result<string> {
  const segments = subpath.split('/')
  if (segments.some((s) => s === '..')) {
    return err(
      new CliError(
        `Subpath contains ".." traversal: "${subpath}"`,
        'E_UNSAFE_SUBPATH',
        'Subpaths must not contain ".." segments',
      ),
    )
  }
  // Strip leading/trailing slashes and normalize
  return ok(segments.filter(Boolean).join('/'))
}
```

#### Example Test Cases

```typescript
// .scripts/test/source-parser.test.ts
import { describe, expect, test } from 'bun:test'
import { getOwnerRepo, parseSource, sanitizeSubpath } from '../lib/source-parser'

describe('parseSource', () => {
  // --- Happy path ---
  test('parses owner/repo shorthand', () => {
    const result = parseSource('vercel-labs/skills')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.type).toBe('github')
      expect(result.value.url).toBe('https://github.com/vercel-labs/skills.git')
      expect(result.value.ref).toBeUndefined()
      expect(result.value.skillFilter).toBeUndefined()
    }
  })

  test('parses full format with ref, subpath, and skill filter', () => {
    const result = parseSource('owner/repo#main:skills/foo@bar')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.type).toBe('github')
      expect(result.value.ref).toBe('main')
      expect(result.value.subpath).toBe('skills/foo')
      expect(result.value.skillFilter).toBe('bar')
    }
  })

  test('parses GitHub tree URL', () => {
    const result = parseSource('github.com/o/r/tree/branch/path')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.type).toBe('github')
      expect(result.value.url).toBe('https://github.com/o/r.git')
      expect(result.value.ref).toBe('branch')
      expect(result.value.subpath).toBe('path')
    }
  })

  test('parses local path', () => {
    const result = parseSource('./local/path')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.type).toBe('local')
      expect(result.value.localPath).toBe('./local/path')
    }
  })

  // --- Edge cases ---
  test('parses owner/repo with only skill filter (no ref)', () => {
    const result = parseSource('owner/repo@my-skill')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.ref).toBeUndefined()
      expect(result.value.skillFilter).toBe('my-skill')
    }
  })

  test('parses SSH git URL', () => {
    const result = parseSource('git@github.com:owner/repo.git')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.type).toBe('git')
      expect(result.value.url).toBe('git@github.com:owner/repo.git')
    }
  })

  // --- Error cases ---
  test('rejects empty string', () => {
    const result = parseSource('')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_INVALID_SOURCE')
  })

  test('rejects subpath with traversal', () => {
    const result = parseSource('owner/repo#main:../../../etc/passwd')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_UNSAFE_SUBPATH')
  })

  test('rejects non-parseable string', () => {
    const result = parseSource(':::bad:::')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_INVALID_SOURCE')
  })
})

describe('getOwnerRepo', () => {
  test('extracts owner/repo from GitHub parsed source', () => {
    const result = parseSource('vercel-labs/skills')
    if (result.ok) expect(getOwnerRepo(result.value)).toBe('vercel-labs/skills')
  })

  test('returns null for local source', () => {
    const result = parseSource('./local/path')
    if (result.ok) expect(getOwnerRepo(result.value)).toBeNull()
  })
})

describe('sanitizeSubpath', () => {
  test('normalizes leading/trailing slashes', () => {
    const result = sanitizeSubpath('/skills/foo/')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe('skills/foo')
  })

  test('rejects path traversal', () => {
    const result = sanitizeSubpath('../../etc/passwd')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_UNSAFE_SUBPATH')
  })

  test('allows single-segment paths', () => {
    const result = sanitizeSubpath('skills')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe('skills')
  })
})
```

#### Edge Cases

| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Empty string | `""` | `E_INVALID_SOURCE` error |
| Whitespace only | `"  "` | `E_INVALID_SOURCE` error |
| Path traversal in subpath | `owner/repo#main:../../etc` | `E_UNSAFE_SUBPATH` error |
| Repo name with dots | `my.org/my.repo` | Parsed as `github` type |
| Repo name with hyphens | `my-org/my-repo` | Parsed as `github` type |
| URL with https:// prefix, no .git | `https://example.com/skills` | Parsed as `well-known` |
| GitHub URL with https:// prefix | `https://github.com/o/r.git` | Parsed as `git` type (not tree URL) |
| Skill filter with special chars | `owner/repo@my_skill-v2` | `skillFilter` = `my_skill-v2` |
| Only ref, no subpath/filter | `owner/repo#v1.2.3` | Only `ref` set |
| Absolute local path | `/usr/local/skills` | Parsed as `local` type |
| GitLab tree URL | `gitlab.com/o/r/-/tree/main/sub` | Parsed as `gitlab` type |

#### Acceptance Criteria

- [ ] All 14 rows in the test matrix pass
- [ ] `parseSource` returns `Result<ParsedSource>`, never throws
- [ ] `sanitizeSubpath` rejects `..` anywhere in the path (beginning, middle, end)
- [ ] `getOwnerRepo` returns `null` for `local` and `well-known` types
- [ ] `ParsedSource` Valibot schema added to `schemas.ts` and validates correctly
- [ ] No external npm dependencies added

---

### 1.2 Agent Registry (`lib/agents.ts`)

- [ ] Define `AgentType` union type (44 agents from vercel-labs/skills)
- [ ] Define `AgentConfig` interface: `{ name, displayName, skillsDir, globalSkillsDir, detectInstalled }`
- [ ] `detectInstalled` checks config directory presence only (e.g., `existsSync(~/.cursor)`), not binary detection
- [ ] Export `agents: Record<AgentType, AgentConfig>` registry
- [ ] Export `detectInstalledAgents(): Promise<AgentType[]>`
- [ ] Export `getUniversalAgents()` / `getNonUniversalAgents()` / `isUniversalAgent()`
- [ ] Export `getAgentBaseDir(agentType, global, cwd)` -- resolves install path
- [ ] Add `AgentType` and `AgentConfig` schemas to `schemas.ts`
- [ ] Write tests (mock `existsSync` for `detectInstalled`)

#### Task Dependencies

Depends on: none (standalone module; uses `existsSync` from `node:fs`, not runtime.ts since it is a synchronous check)

#### Library Decisions

**New dependency: `xdg-basedir` (`^5.1.0`).** Used for correct XDG Base Directory resolution (`xdgConfig`, `xdgData`, `xdgState`) when computing global skill directories for agents that follow the XDG spec (Amp, OpenCode, Goose, etc.). Avoids hardcoding `~/.config` and handles platform differences. The agent registry itself is static data (44 object literals) plus a `detectInstalled` function per agent that calls `existsSync`. The data was extracted from vercel-labs/skills v0.5.x (MIT license) and is maintained as our own copy.

#### Error Types

```typescript
/**
 * Error when an unknown agent name is passed to a lookup function.
 *
 * Code: E_UNKNOWN_AGENT
 * Hint: "Known agents: claude-code, cursor, windsurf, ..."
 */

/**
 * Error when agent base directory cannot be resolved.
 *
 * Code: E_AGENT_PATH
 * Hint: "Agent <name> has no configured skillsDir"
 */
```

#### Code Examples

```typescript
// .scripts/lib/agents.ts
import { existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { xdgConfig } from 'xdg-basedir'
import * as v from 'valibot'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Types & schemas
// ---------------------------------------------------------------------------

/**
 * Union of all recognized AI coding agent identifiers.
 * Sourced from vercel-labs/skills v0.5.x (MIT).
 */
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

/** Configuration for a single AI coding agent. */
export interface AgentConfig {
  /** Machine-readable identifier. */
  readonly name: AgentType
  /** Human-readable display name. */
  readonly displayName: string
  /** Project-scope skills directory (relative to project root). */
  readonly skillsDir: string
  /** Global skills directory (absolute path). */
  readonly globalSkillsDir: string
  /** Whether this agent supports the universal SKILL.md format. */
  readonly universal: boolean
  /** Check if this agent's config directory exists on the local machine. */
  detectInstalled(): boolean
}

// ---------------------------------------------------------------------------
// Registry (subset shown -- full file has all 44)
// ---------------------------------------------------------------------------

const home = homedir()
const configHome = xdgConfig ?? join(home, '.config')

/** Full registry of all known agents. */
export const agents: Record<AgentType, AgentConfig> = {
  'claude-code': {
    name: 'claude-code',
    displayName: 'Claude Code',
    skillsDir: '.claude/skills',
    globalSkillsDir: join(home, '.claude', 'skills'),
    universal: true,
    detectInstalled: () => existsSync(join(home, '.claude')),
  },
  cursor: {
    name: 'cursor',
    displayName: 'Cursor',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.cursor', 'skills'),
    universal: true,
    detectInstalled: () => existsSync(join(home, '.cursor')),
  },
  amp: {
    name: 'amp',
    displayName: 'Amp',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(configHome, 'agents/skills'),
    universal: true,
    detectInstalled: () => existsSync(join(configHome, 'amp')),
  },
  goose: {
    name: 'goose',
    displayName: 'Goose',
    skillsDir: '.goose/skills',
    globalSkillsDir: join(configHome, 'goose/skills'),
    universal: false,
    detectInstalled: () => existsSync(join(configHome, 'goose')),
  },
  // ... remaining agents follow the same pattern ...
  // Agents using XDG paths (amp, opencode, goose, kimi-cli) use `configHome`
  // Agents using home-relative paths (cursor, windsurf, etc.) use `home`
} as Record<AgentType, AgentConfig>

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Detect which agents are installed on the local machine.
 * Checks each agent's config directory for existence.
 *
 * @returns Array of installed agent type identifiers
 */
export async function detectInstalledAgents(): Promise<AgentType[]> {
  return Object.values(agents)
    .filter((a) => a.detectInstalled())
    .map((a) => a.name)
}

/**
 * Get all agents that support the universal SKILL.md format.
 */
export function getUniversalAgents(): AgentConfig[] {
  return Object.values(agents).filter((a) => a.universal)
}

/**
 * Get agents that require platform-specific skill formats.
 */
export function getNonUniversalAgents(): AgentConfig[] {
  return Object.values(agents).filter((a) => !a.universal)
}

/**
 * Check whether a given agent type supports universal skills.
 */
export function isUniversalAgent(agentType: AgentType): boolean {
  return agents[agentType]?.universal ?? false
}

/**
 * Resolve the base directory for skill installation.
 *
 * @param agentType - The agent to resolve for
 * @param global - If true, use the global skills directory
 * @param cwd - Current working directory (used for project-scope resolution)
 * @returns Absolute path to the skills directory
 */
export function getAgentBaseDir(
  agentType: AgentType,
  global: boolean,
  cwd: string,
): Result<string> {
  const agent = agents[agentType]
  if (!agent) {
    return err(
      new CliError(
        `Unknown agent: "${agentType}"`,
        'E_UNKNOWN_AGENT',
        `Known agents: ${Object.keys(agents).slice(0, 5).join(', ')}, ...`,
      ),
    )
  }
  if (global) return ok(agent.globalSkillsDir)
  return ok(join(cwd, agent.skillsDir))
}
```

#### Example Test Cases

```typescript
// .scripts/test/agents.test.ts
import { describe, expect, test } from 'bun:test'
import {
  agents,
  detectInstalledAgents,
  getAgentBaseDir,
  getNonUniversalAgents,
  getUniversalAgents,
  isUniversalAgent,
  type AgentType,
} from '../lib/agents'

describe('agents registry', () => {
  // --- Happy path ---
  test('contains at least 44 agents', () => {
    expect(Object.keys(agents).length).toBeGreaterThanOrEqual(44)
  })

  test('claude-code is registered with correct config', () => {
    const claude = agents['claude-code']
    expect(claude).toBeDefined()
    expect(claude.displayName).toBe('Claude Code')
    expect(claude.skillsDir).toBe('.claude/skills')
    expect(claude.universal).toBe(true)
  })

  test('every agent has required fields', () => {
    for (const [key, agent] of Object.entries(agents)) {
      expect(agent.name).toBe(key)
      expect(agent.displayName.length).toBeGreaterThan(0)
      expect(agent.skillsDir.length).toBeGreaterThan(0)
      expect(typeof agent.detectInstalled).toBe('function')
    }
  })
})

describe('detectInstalledAgents', () => {
  // --- Happy path ---
  test('returns array of AgentType strings', async () => {
    const installed = await detectInstalledAgents()
    expect(Array.isArray(installed)).toBe(true)
    // At minimum, claude-code should be installed in this dev environment
    // (since ~/.claude exists for claude code users)
  })

  // --- Edge case: all agents detected are valid ---
  test('only returns valid AgentType values', async () => {
    const installed = await detectInstalledAgents()
    const validNames = new Set(Object.keys(agents))
    for (const name of installed) {
      expect(validNames.has(name)).toBe(true)
    }
  })
})

describe('getAgentBaseDir', () => {
  // --- Happy path ---
  test('resolves project-scope directory', () => {
    const result = getAgentBaseDir('claude-code', false, '/home/user/project')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('/home/user/project/.claude/skills')
    }
  })

  test('resolves global directory', () => {
    const result = getAgentBaseDir('claude-code', true, '/ignored')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toContain('.claude/skills')
    }
  })

  // --- Error case ---
  test('returns error for unknown agent', () => {
    const result = getAgentBaseDir('nonexistent-agent' as AgentType, false, '/tmp')
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_UNKNOWN_AGENT')
    }
  })
})

describe('universal agent helpers', () => {
  test('getUniversalAgents returns non-empty array', () => {
    const universal = getUniversalAgents()
    expect(universal.length).toBeGreaterThan(0)
    expect(universal.every((a) => a.universal)).toBe(true)
  })

  test('isUniversalAgent returns true for claude-code', () => {
    expect(isUniversalAgent('claude-code')).toBe(true)
  })

  test('getNonUniversalAgents excludes universal agents', () => {
    const nonUniversal = getNonUniversalAgents()
    expect(nonUniversal.every((a) => !a.universal)).toBe(true)
  })
})
```

#### Edge Cases

| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Unknown agent type | `'nonexistent'` as AgentType | `E_UNKNOWN_AGENT` error from `getAgentBaseDir` |
| Home dir not set | `HOME=""` | `homedir()` still returns something on macOS/Linux |
| Agent with no global dir | Agent without `globalSkillsDir` | Should never happen (all agents have it) but return empty string |
| Concurrent detection calls | Multiple `detectInstalledAgents()` | Safe -- `existsSync` is idempotent |
| Config dir exists but is a file | `~/.cursor` is a file, not dir | `existsSync` returns true -- acceptable false positive |
| cwd with trailing slash | `/home/user/project/` | `join()` normalizes -- no issue |

#### Acceptance Criteria

- [ ] Registry contains exactly 44 agents (matching vercel-labs/skills v0.5.x)
- [ ] Every agent has `name`, `displayName`, `skillsDir`, `globalSkillsDir`, `universal`, `detectInstalled`
- [ ] `detectInstalledAgents()` only uses `existsSync` (no `which` or binary detection)
- [ ] `getAgentBaseDir` returns `Result<string>` (never throws)
- [ ] `AgentType` Valibot schema added to `schemas.ts`
- [ ] No external npm dependencies added
- [ ] `getUniversalAgents()` and `getNonUniversalAgents()` are disjoint and cover all agents
- [ ] XDG-aware agents (amp, opencode, goose, kimi-cli) use `xdg-basedir` `configHome` for global dirs

---

### 1.3 Git Wrapper (`lib/git.ts`)

- [ ] Export `cloneRepo(url, ref?): Promise<{ tempDir: string, cleanup: () => Promise<void> }>`
  - Shallow clone (`--depth 1`) to `os.tmpdir()`
  - Optional `--branch ref` for tags/branches
  - 60s timeout via `spawnAsync` from `runtime.ts`
- [ ] Export `cleanupTempDir(dir)` -- validates within `os.tmpdir()` before deleting
- [ ] Export `GitCloneError` with `isTimeout`, `isAuthError` flags
- [ ] Extract `lsRemote(url, ref?)` from `external-skills.ts` -- runs `git ls-remote`, returns commit SHA
- [ ] Export `fetchSkillFolderHash(ownerRepo, skillPath, token?): Promise<string | null>`
  - Calls GitHub Trees API: `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1`
  - Uses `lib/github.ts` `getClient()` for auth
  - Returns tree SHA for the folder matching `skillPath`, or null
- [ ] Write tests (mock `spawnAsync` for clone/lsRemote, mock Octokit for fetchSkillFolderHash)

**Error handling:**

| Failure | Error type | Retryable |
|---------|-----------|-----------|
| Clone timeout (>60s) | `GitCloneError { isTimeout: true }` | Yes |
| Auth failure (401/403) | `GitCloneError { isAuthError: true }` | No (needs token) |
| Repo not found (128) | `GitCloneError` | No |
| Network failure | `GitCloneError` | Yes |
| Trees API 404 | Returns `null` | No |
| Trees API rate limit | Throws (caller handles) | Yes |

#### Task Dependencies

Depends on: none (uses existing `lib/runtime.ts` `spawnAsync` and `lib/github.ts` `getClient`/`parseRepo`)

#### Library Decisions

**New dependency: `simple-git` (`^3.33.0`).** Replaces raw `spawnAsync('git', ...)` calls with a typed API that provides structured response parsing, AbortController timeout support, and a `raw()` escape hatch for unsupported operations (worktrees, sparse-checkout, archive). 10.8M weekly downloads, 3 tiny deps (`@kwsites/file-exists`, `@kwsites/promise-deferred`, `debug`), bundled TypeScript types. The `fetchSkillFolderHash` function still uses `lib/github.ts` `getClient()` (Octokit) for the GitHub Trees API call since that's an HTTP API, not a git operation.

#### Error Types

```typescript
import { CliError } from './types'

/**
 * Specialized error for git clone operations with diagnostic flags.
 * Extends CliError with boolean indicators for common failure modes.
 */
export class GitCloneError extends CliError {
  constructor(
    message: string,
    readonly isTimeout: boolean = false,
    readonly isAuthError: boolean = false,
    hint?: string,
    cause?: unknown,
  ) {
    super(message, 'E_GIT_CLONE', hint, cause)
  }
}

/**
 * Error when git ls-remote fails to resolve a ref.
 * Code: E_GIT_LS_REMOTE
 */

/**
 * Error when no refs are found for the given repo/ref.
 * Code: E_NO_REFS
 */

/**
 * Error when the temp directory is outside os.tmpdir() (safety check).
 * Code: E_UNSAFE_CLEANUP
 */
```

#### Code Examples

```typescript
// .scripts/lib/git.ts
import { simpleGit, type SimpleGit, type SimpleGitOptions } from 'simple-git'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { getClient, parseRepo } from './github'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Error types
// ---------------------------------------------------------------------------

/** Specialized error for git clone failures with diagnostic flags. */
export class GitCloneError extends CliError {
  constructor(
    message: string,
    readonly isTimeout: boolean = false,
    readonly isAuthError: boolean = false,
    hint?: string,
    cause?: unknown,
  ) {
    super(message, 'E_GIT_CLONE', hint, cause)
  }
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CLONE_TIMEOUT_MS = 60_000
const TEMP_PREFIX = 'skill-clone-'

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

/**
 * Create a simple-git instance with standard timeout and abort support.
 * Use this for all git operations instead of spawning git directly.
 */
export function createGit(
  baseDir?: string,
  opts?: { timeout?: number; signal?: AbortSignal },
): SimpleGit {
  const config: Partial<SimpleGitOptions> = {
    baseDir: baseDir ?? process.cwd(),
    maxConcurrentProcesses: 4,
    timeout: { block: opts?.timeout ?? CLONE_TIMEOUT_MS },
  }
  const git = simpleGit(config)
  if (opts?.signal) {
    // simple-git abort plugin
    opts.signal.addEventListener('abort', () => git.clean('f', ['-d']))
  }
  return git
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Shallow-clone a git repository into a temporary directory.
 *
 * Uses simple-git's clone() with --depth 1 and optional --branch.
 * Returns a cleanup function that safely removes the temp directory.
 *
 * @param url - Repository URL (HTTPS or SSH)
 * @param ref - Optional branch, tag, or commit SHA to check out
 * @returns Object with `tempDir` path and `cleanup` function
 */
export async function cloneRepo(
  url: string,
  ref?: string,
): Promise<Result<{ tempDir: string; cleanup: () => Promise<void> }>> {
  const tempDir = await mkdtemp(join(tmpdir(), TEMP_PREFIX))
  const git = createGit(tmpdir())

  try {
    const cloneOpts = ['--depth', '1']
    if (ref) cloneOpts.push('--branch', ref)

    await git.clone(url, tempDir, cloneOpts)

    return ok({
      tempDir,
      cleanup: () => cleanupTempDir(tempDir),
    })
  } catch (e) {
    await rm(tempDir, { recursive: true, force: true })
    const msg = e instanceof Error ? e.message : String(e)

    if (msg.includes('Authentication failed') || msg.includes('could not read Username')) {
      return err(new GitCloneError(
        `Authentication failed for ${url}`, false, true,
        'Set GITHUB_TOKEN or run "gh auth login"',
      ))
    }
    if (msg.includes('timed out') || msg.includes('timeout')) {
      return err(new GitCloneError(
        `Clone timed out after ${CLONE_TIMEOUT_MS / 1000}s for ${url}`, true, false,
        'The repository may be too large or the network is slow',
      ))
    }

    return err(new GitCloneError(`Clone failed for ${url}`, false, false, msg))
  }
}

/**
 * Safely remove a temporary directory.
 * Validates the path is under `os.tmpdir()` before deletion.
 */
export async function cleanupTempDir(dir: string): Promise<void> {
  const resolvedDir = resolve(dir)
  const resolvedTmp = resolve(tmpdir())
  if (!resolvedDir.startsWith(resolvedTmp)) {
    throw new CliError(
      `Refusing to delete directory outside tmpdir: ${dir}`,
      'E_UNSAFE_CLEANUP',
      `Expected path under ${resolvedTmp}`,
    )
  }
  await rm(dir, { recursive: true, force: true })
}

/**
 * Resolve a remote ref to a commit SHA via `git ls-remote`.
 *
 * Uses simple-git's listRemote() which wraps `git ls-remote`.
 *
 * @param repoUrl - Repository URL
 * @param ref - Optional tag/branch ref to resolve
 * @returns Commit SHA string
 */
export async function lsRemote(repoUrl: string, ref?: string): Promise<Result<string>> {
  const git = createGit()

  try {
    const args = ref
      ? ['--tags', repoUrl, ref]
      : [repoUrl, 'HEAD']

    const output = await git.listRemote(args)
    const trimmed = output.trim()

    if (!trimmed) {
      return err(new CliError(
        `No refs found for ${repoUrl}${ref ? ` at ${ref}` : ''}`,
        'E_NO_REFS',
        ref
          ? `Tag "${ref}" may not exist. Check with: git ls-remote --tags ${repoUrl}`
          : 'Repository may be empty or inaccessible',
      ))
    }

    const sha = trimmed.split(/\s+/)[0]
    if (!sha) {
      return err(new CliError('Could not parse commit SHA from ls-remote output', 'E_PARSE_FAILED'))
    }

    return ok(sha)
  } catch (e) {
    return err(new CliError(
      `git ls-remote failed for ${repoUrl}`,
      'E_GIT_LS_REMOTE',
      e instanceof Error ? e.message : String(e),
    ))
  }
}

/**
 * Execute a raw git command via simple-git's raw() escape hatch.
 * Use for operations without dedicated simple-git methods
 * (worktrees, sparse-checkout, archive).
 *
 * @param args - Git command arguments (e.g., ['worktree', 'add', path, branch])
 * @param baseDir - Working directory for the command
 * @returns Raw stdout string
 */
export async function gitRaw(
  args: string[],
  baseDir?: string,
): Promise<Result<string>> {
  const git = createGit(baseDir)
  try {
    const output = await git.raw(args)
    return ok(output)
  } catch (e) {
    return err(new CliError(
      `git ${args[0]} failed`,
      'E_GIT_RAW',
      e instanceof Error ? e.message : String(e),
    ))
  }
}

/**
 * Fetch the tree SHA for a specific folder in a GitHub repository.
 *
 * Uses the GitHub Trees API (not git CLI) to find the SHA of the tree
 * object for the given skill path. This is an HTTP call, not a git op.
 *
 * @param ownerRepo - "owner/repo" string
 * @param skillPath - Path within the repo (e.g. "skills/beads")
 * @param branch - Branch to query (defaults to "HEAD")
 * @returns Tree SHA string, or null if the path does not exist
 */
export async function fetchSkillFolderHash(
  ownerRepo: string,
  skillPath: string,
  branch = 'HEAD',
): Promise<string | null> {
  const client = await getClient()
  const { owner, repo } = parseRepo(ownerRepo)

  try {
    const response = await client.request(
      'GET /repos/{owner}/{repo}/git/trees/{tree_sha}',
      { owner, repo, tree_sha: branch, recursive: '1' },
    )

    const normalizedPath = skillPath.replace(/\/$/, '')
    const entry = response.data.tree.find(
      (item: { path?: string; type?: string }) =>
        item.path === normalizedPath && item.type === 'tree',
    )

    return entry?.sha ?? null
  } catch {
    return null
  }
}
```

#### Example Test Cases

```typescript
// .scripts/test/git.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdtemp } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { cleanupTempDir, GitCloneError, lsRemote } from '../lib/git'

describe('GitCloneError', () => {
  test('creates error with timeout flag', () => {
    const error = new GitCloneError('timed out', true, false)
    expect(error.isTimeout).toBe(true)
    expect(error.isAuthError).toBe(false)
    expect(error.code).toBe('E_GIT_CLONE')
    expect(error.message).toBe('timed out')
  })

  test('creates error with auth flag', () => {
    const error = new GitCloneError('auth failed', false, true)
    expect(error.isTimeout).toBe(false)
    expect(error.isAuthError).toBe(true)
  })

  test('display() includes hint', () => {
    const error = new GitCloneError('failed', false, false, 'try again')
    expect(error.display()).toContain('try again')
  })
})

describe('cleanupTempDir', () => {
  // --- Happy path ---
  test('removes directory under tmpdir', async () => {
    const dir = await mkdtemp(join(tmpdir(), 'git-test-'))
    expect(existsSync(dir)).toBe(true)
    await cleanupTempDir(dir)
    expect(existsSync(dir)).toBe(false)
  })

  // --- Edge case: already removed ---
  test('does not throw if directory already removed', async () => {
    const dir = join(tmpdir(), 'already-gone-' + Date.now())
    // Directory does not exist -- rm with force should be fine
    await expect(cleanupTempDir(dir)).resolves.toBeUndefined()
  })

  // --- Error case: path outside tmpdir ---
  test('rejects directory outside tmpdir', async () => {
    await expect(cleanupTempDir('/usr/local/dangerous')).rejects.toThrow('E_UNSAFE_CLEANUP')
  })
})

describe('lsRemote', () => {
  // --- Happy path (requires network, use .skip in CI) ---
  test('resolves HEAD for a public repo', async () => {
    const result = await lsRemote('https://github.com/vercel-labs/skills.git')
    expect(result.ok).toBe(true)
    if (result.ok) {
      // SHA is 40 hex chars
      expect(result.value).toMatch(/^[a-f0-9]{40}$/)
    }
  })

  // --- Edge case: nonexistent repo ---
  test('returns error for nonexistent repo', async () => {
    const result = await lsRemote('https://github.com/nonexistent/repo-that-does-not-exist-12345.git')
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_GIT_LS_REMOTE')
    }
  })

  // --- Edge case: nonexistent tag ---
  test('returns error for nonexistent tag', async () => {
    const result = await lsRemote(
      'https://github.com/vercel-labs/skills.git',
      'v999.999.999-nonexistent',
    )
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_REFS')
    }
  })
})

describe('gitRaw', () => {
  test('executes arbitrary git commands', async () => {
    const result = await gitRaw(['--version'])
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toContain('git version')
    }
  })

  test('returns error for invalid commands', async () => {
    const result = await gitRaw(['not-a-real-command'])
    expect(result.ok).toBe(false)
  })
})
```

#### Edge Cases

| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| Clone timeout | Repo is huge or network is down | `GitCloneError { isTimeout: true }` after 60s, temp dir cleaned up |
| Auth failure (private repo) | No token, repo requires auth | `GitCloneError { isAuthError: true }`, temp dir cleaned up |
| Repo does not exist | `https://github.com/nonexistent/repo.git` | `GitCloneError`, exit code 128, temp dir cleaned up |
| `cleanupTempDir` outside tmpdir | `/usr/local/important` | Throws `E_UNSAFE_CLEANUP` -- refuses to delete |
| `cleanupTempDir` already deleted | Path no longer exists | No error (rm with `force: true`) |
| `lsRemote` empty output | Repo exists but is empty | `E_NO_REFS` error |
| `lsRemote` with annotated tag | Tag resolves to ^{} ref | First column SHA is returned correctly |
| `fetchSkillFolderHash` path not found | Skill folder does not exist in tree | Returns `null` |
| `fetchSkillFolderHash` rate limited | GitHub API 403 | Returns `null` (catch block), caller retries |
| Branch name with slashes | `feature/my-branch` | Passed as `--branch` arg, works with git |

#### Acceptance Criteria

- [ ] `cloneRepo` creates a temp dir, clones, and returns a cleanup function
- [ ] `cloneRepo` timeout is 60s and returns `GitCloneError { isTimeout: true }` on expiry
- [ ] `cloneRepo` detects auth failures and sets `isAuthError: true`
- [ ] `cloneRepo` always cleans up temp dir on failure
- [ ] `cleanupTempDir` refuses to delete paths outside `os.tmpdir()`
- [ ] `lsRemote` is extracted from `external-skills.ts` and uses `spawnAsync` (not `spawnSync`)
- [ ] `fetchSkillFolderHash` returns `string | null`, never throws
- [ ] `GitCloneError` extends `CliError` (same `display()` interface)
- [ ] Uses `simple-git` for clone, ls-remote, and `raw()` for worktrees/sparse-checkout
- [ ] `gitRaw()` exported as escape hatch for arbitrary git commands
- [ ] `createGit()` factory exported for reuse across modules

---

### 1.4 Skill Discovery (`lib/skill-discovery.ts`)

- [ ] Export `discoverSkills(basePath, subpath?, opts?): Promise<Skill[]>`
  - Recursively scans for `SKILL.md` files up to `opts.maxDepth` (default: 5)
  - Priority search: checks known skill directories first (`skills/`, `context/skills/`, `.agents/skills/`)
  - Falls back to recursive scan if priority paths don't exist
  - Parses each `SKILL.md` via `readSkillFrontmatter` from `manifest.ts`
- [ ] Export `filterSkills(skills, names): Skill[]` -- case-insensitive name matching
- [ ] Check plugin manifests (`.claude-plugin/plugin.json`) for declared skill paths
- [ ] Respect `subpath` to restrict discovery to a subdirectory
- [ ] Write tests with fixture directories

#### Task Dependencies

Depends on: none (uses existing `lib/manifest.ts` `readSkillFrontmatter` and `lib/chunker.ts` `parseFrontmatter` which are already implemented)

#### Library Decisions

**No external dependencies for frontmatter parsing.** Uses the existing `parseFrontmatter` from `lib/chunker.ts` (which uses `js-yaml`, already a project dependency) via `readSkillFrontmatter` from `lib/manifest.ts`. Directory traversal uses `node:fs/promises` `readdir` with `{ recursive: true }` (Node 18.17+, supported by Bun). No need for `fast-glob` here since we control the search pattern (always `SKILL.md` file name match).

#### Error Types

```typescript
/**
 * Error when the base path does not exist or is not a directory.
 * Code: E_DISCOVERY_PATH
 * Hint: "Path does not exist: /some/path"
 */

/**
 * Warning (non-fatal) when a SKILL.md file has invalid frontmatter.
 * Logged but not thrown -- the file is skipped and discovery continues.
 * The Skill result includes a `warnings` array for these cases.
 */
```

#### Code Examples

```typescript
// .scripts/lib/skill-discovery.ts
import { readdir, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { join, relative } from 'node:path'
import { readSkillFrontmatter } from './manifest'
import { readPluginManifest } from './manifest'
import type { SkillFrontmatter } from './schemas'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** A discovered skill with its metadata and location. */
export interface DiscoveredSkill {
  /** Absolute path to the SKILL.md file. */
  readonly path: string
  /** Path relative to the search base. */
  readonly relativePath: string
  /** Parsed and validated frontmatter. */
  readonly frontmatter: SkillFrontmatter
  /** Name from frontmatter (convenience accessor). */
  readonly name: string
}

/** Options for skill discovery. */
export interface DiscoverOptions {
  /** Maximum directory depth to scan (default: 5). */
  maxDepth?: number
  /** If true, also check plugin manifests for declared skills. */
  checkPlugins?: boolean
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Known skill directory names, checked in priority order. */
const PRIORITY_DIRS = ['skills', 'context/skills', '.agents/skills', '.claude/skills']

const DEFAULT_MAX_DEPTH = 5

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Discover SKILL.md files under a base path.
 *
 * First checks well-known skill directories (priority search), then
 * falls back to a recursive scan if none are found. Parses frontmatter
 * from each discovered file via `readSkillFrontmatter`.
 *
 * @param basePath - Root directory to search
 * @param subpath - Optional subdirectory to restrict search to
 * @param opts - Discovery options (maxDepth, checkPlugins)
 * @returns Array of discovered skills with parsed frontmatter
 */
export async function discoverSkills(
  basePath: string,
  subpath?: string,
  opts?: DiscoverOptions,
): Promise<Result<DiscoveredSkill[]>> {
  const searchRoot = subpath ? join(basePath, subpath) : basePath
  const maxDepth = opts?.maxDepth ?? DEFAULT_MAX_DEPTH

  if (!existsSync(searchRoot)) {
    return err(
      new CliError(
        `Path does not exist: ${searchRoot}`,
        'E_DISCOVERY_PATH',
        'Verify the path exists and is accessible',
      ),
    )
  }

  const skillPaths: string[] = []

  // Priority search: check well-known directories first
  for (const dir of PRIORITY_DIRS) {
    const candidate = join(searchRoot, dir)
    if (existsSync(candidate)) {
      const found = await findSkillFiles(candidate, maxDepth, 0)
      skillPaths.push(...found)
    }
  }

  // Fallback: recursive scan from root if no priority paths found skills
  if (skillPaths.length === 0) {
    const found = await findSkillFiles(searchRoot, maxDepth, 0)
    skillPaths.push(...found)
  }

  // Parse each SKILL.md
  const skills: DiscoveredSkill[] = []
  for (const skillPath of skillPaths) {
    const result = await readSkillFrontmatter(skillPath)
    if (result.ok) {
      skills.push({
        path: skillPath,
        relativePath: relative(basePath, skillPath),
        frontmatter: result.value,
        name: result.value.name,
      })
    }
    // Skip files with invalid frontmatter (non-fatal)
  }

  return ok(skills)
}

/**
 * Filter a list of discovered skills by name (case-insensitive).
 *
 * @param skills - Array of discovered skills
 * @param names - Skill names to match
 * @returns Filtered array
 */
export function filterSkills(skills: DiscoveredSkill[], names: string[]): DiscoveredSkill[] {
  const lowerNames = new Set(names.map((n) => n.toLowerCase()))
  return skills.filter((s) => lowerNames.has(s.name.toLowerCase()))
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Recursively find SKILL.md files under a directory with depth limiting.
 */
async function findSkillFiles(
  dir: string,
  maxDepth: number,
  currentDepth: number,
): Promise<string[]> {
  if (currentDepth > maxDepth) return []

  const results: string[] = []

  let entries: Awaited<ReturnType<typeof readdir>>
  try {
    entries = await readdir(dir, { withFileTypes: true })
  } catch {
    return []
  }

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    if (entry.isFile() && entry.name === 'SKILL.md') {
      results.push(fullPath)
    } else if (entry.isDirectory() && !entry.name.startsWith('.')) {
      const sub = await findSkillFiles(fullPath, maxDepth, currentDepth + 1)
      results.push(...sub)
    }
  }

  return results
}
```

#### Example Test Cases

```typescript
// .scripts/test/skill-discovery.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { mkdtemp } from 'node:fs/promises'
import { discoverSkills, filterSkills } from '../lib/skill-discovery'

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-disc-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

/**
 * Helper to create a minimal SKILL.md fixture.
 */
async function createSkill(dir: string, name: string, description = 'Test skill'): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(
    join(dir, 'SKILL.md'),
    `---\nname: ${name}\ndescription: ${description}\n---\n\n# ${name}\n`,
  )
}

describe('discoverSkills', () => {
  // --- Happy path ---
  test('discovers skills in context/skills/ directory', async () => {
    await createSkill(join(tmp, 'context/skills/my-skill'), 'my-skill')
    await createSkill(join(tmp, 'context/skills/other'), 'other')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(2)
      const names = result.value.map((s) => s.name).sort()
      expect(names).toEqual(['my-skill', 'other'])
    }
  })

  // --- Edge case: deeply nested ---
  test('respects maxDepth and stops searching', async () => {
    // Create skill at depth 8 (beyond default maxDepth of 5)
    const deepPath = join(tmp, 'a/b/c/d/e/f/g/h')
    await createSkill(deepPath, 'deep-skill')

    const result = await discoverSkills(tmp, undefined, { maxDepth: 3 })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(0)
    }
  })

  // --- Edge case: no skills found ---
  test('returns empty array when no SKILL.md files exist', async () => {
    await mkdir(join(tmp, 'empty-dir'), { recursive: true })
    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(0)
    }
  })

  // --- Error case: path does not exist ---
  test('returns error for nonexistent path', async () => {
    const result = await discoverSkills(join(tmp, 'nonexistent'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_DISCOVERY_PATH')
    }
  })

  // --- Edge case: subpath restriction ---
  test('restricts discovery to subpath', async () => {
    await createSkill(join(tmp, 'skills/a'), 'a')
    await createSkill(join(tmp, 'other/b'), 'b')

    const result = await discoverSkills(tmp, 'skills')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(1)
      expect(result.value[0]!.name).toBe('a')
    }
  })

  // --- Edge case: invalid frontmatter skipped ---
  test('skips SKILL.md with invalid frontmatter', async () => {
    await createSkill(join(tmp, 'context/skills/good'), 'good')
    // Create bad SKILL.md
    await mkdir(join(tmp, 'context/skills/bad'), { recursive: true })
    await writeFile(join(tmp, 'context/skills/bad/SKILL.md'), '# No frontmatter at all\n')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(1)
      expect(result.value[0]!.name).toBe('good')
    }
  })
})

describe('filterSkills', () => {
  test('filters by name case-insensitively', () => {
    const skills = [
      { path: '/a', relativePath: 'a', name: 'Beads', frontmatter: { name: 'Beads', description: '' } },
      { path: '/b', relativePath: 'b', name: 'gitlab-cicd', frontmatter: { name: 'gitlab-cicd', description: '' } },
    ] as const
    const filtered = filterSkills(skills as any, ['beads'])
    expect(filtered).toHaveLength(1)
    expect(filtered[0]!.name).toBe('Beads')
  })

  test('returns empty when no names match', () => {
    const skills = [
      { path: '/a', relativePath: 'a', name: 'foo', frontmatter: { name: 'foo', description: '' } },
    ] as const
    const filtered = filterSkills(skills as any, ['bar'])
    expect(filtered).toHaveLength(0)
  })

  test('handles empty skills array', () => {
    const filtered = filterSkills([], ['anything'])
    expect(filtered).toHaveLength(0)
  })
})

describe('discoverSkills - real project', () => {
  test('discovers skills in the actual project', async () => {
    const result = await discoverSkills('/private/etc/infra/pub/ai')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.length).toBeGreaterThan(0)
      // At minimum, beads and gitlab-cicd should exist
      const names = result.value.map((s) => s.name)
      expect(names).toContain('beads')
      expect(names).toContain('gitlab-cicd')
    }
  })
})
```

#### Edge Cases

| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| No SKILL.md files | Empty directory tree | Returns `ok([])` |
| Deeply nested skill | Skill at depth > maxDepth | Not discovered (respects depth limit) |
| Invalid frontmatter | SKILL.md without `---` delimiters | Skipped silently, not in results |
| Missing required fields | SKILL.md with `description` but no `name` | Skipped (validation failure) |
| Hidden directories | `.git/`, `.venv/` | Skipped (dot-prefixed dirs are excluded) |
| Symlinked SKILL.md | Symlink to another SKILL.md | Followed and parsed (readdir follows symlinks) |
| Permission denied | Unreadable directory | Skipped (catch block in `findSkillFiles`) |
| Duplicate names | Two skills with same `name` in frontmatter | Both included (caller deduplicates) |
| Subpath is a file | `subpath` points to a file, not dir | `E_DISCOVERY_PATH` (existsSync returns true but readdir fails) |
| Plugin-declared skills | `.claude-plugin/plugin.json` lists skill paths | Checked when `checkPlugins: true` |

#### Acceptance Criteria

- [ ] `discoverSkills` finds SKILL.md files in priority directories before falling back to full scan
- [ ] `discoverSkills` respects `maxDepth` option (default: 5)
- [ ] `discoverSkills` skips hidden directories (starting with `.`)
- [ ] `discoverSkills` returns `Result<DiscoveredSkill[]>` (error only for missing basePath)
- [ ] Invalid SKILL.md files are skipped without failing the entire discovery
- [ ] `filterSkills` is case-insensitive
- [ ] Uses `readSkillFrontmatter` from `lib/manifest.ts` (no duplicate parsing logic)
- [ ] No external npm dependencies added
- [ ] Tests use temp fixture directories (not hardcoded to project structure, except one integration test)

---

### 1.5 Interactive Prompts (`lib/prompts/`)

- [ ] `search-multiselect.ts` -- fzf-style filtered multiselect
  - Raw readline keypresses (no external dependency)
  - Debounced filter input (150-250ms adaptive)
  - Locked sections (pre-selected items that can't be deselected)
  - `cancelSymbol` for escape handling
  - Returns `T[] | typeof cancelSymbol`
- [ ] `confirm.ts` -- simple y/n confirmation prompt
- [ ] `index.ts` -- barrel export
- [ ] All prompts respect `--yes` flag (non-interactive mode) via options parameter
- [ ] All prompts detect non-TTY and skip interaction (return defaults)

#### Task Dependencies

Depends on: none (standalone UI module, no dependency on other Phase 1 tasks)

#### Library Decisions

**No external dependencies.** The prompt library uses raw `node:readline` for terminal input handling. This is intentional -- the project needs only two prompt types (multiselect search and confirm), and pulling in a full prompt library (e.g., `@inquirer/prompts`, `prompts`, `enquirer`) would add unnecessary weight. The `readline` module provides `createInterface`, raw mode keypresses via `process.stdin.setRawMode(true)`, and cursor control via ANSI escape codes. The debounced filter uses a simple `setTimeout`-based approach.

#### Error Types

```typescript
/**
 * Symbol returned when the user cancels a prompt (presses Escape).
 * Callers check: `if (result === cancelSymbol) { ... }`
 */
export const cancelSymbol: unique symbol = Symbol('cancel')
export type CancelSymbol = typeof cancelSymbol

/**
 * No explicit error types -- prompts return values or cancelSymbol.
 * In non-TTY mode, prompts return default values without interaction.
 */
```

#### Code Examples

```typescript
// .scripts/lib/prompts/confirm.ts
import { createInterface } from 'node:readline'
import { cancelSymbol, type CancelSymbol } from './index'

/** Options for the confirm prompt. */
export interface ConfirmOptions {
  /** The question to display. */
  message: string
  /** Default value if user presses Enter without input (default: false). */
  default?: boolean
  /** If true, skip prompt and return default value. */
  yes?: boolean
}

/**
 * Display a y/n confirmation prompt.
 *
 * Respects `--yes` flag (returns default without interaction) and
 * non-TTY environments (returns default silently).
 *
 * @param opts - Prompt configuration
 * @returns `true` for yes, `false` for no, or `cancelSymbol` on Escape
 */
export async function confirm(
  opts: ConfirmOptions,
): Promise<boolean | CancelSymbol> {
  const defaultValue = opts.default ?? false

  // Non-interactive mode
  if (opts.yes || !process.stdin.isTTY) {
    return defaultValue
  }

  const hint = defaultValue ? '[Y/n]' : '[y/N]'

  return new Promise((resolve) => {
    const rl = createInterface({
      input: process.stdin,
      output: process.stdout,
    })

    rl.question(`${opts.message} ${hint} `, (answer) => {
      rl.close()
      const trimmed = answer.trim().toLowerCase()
      if (trimmed === '') resolve(defaultValue)
      else if (trimmed === 'y' || trimmed === 'yes') resolve(true)
      else if (trimmed === 'n' || trimmed === 'no') resolve(false)
      else resolve(defaultValue)
    })
  })
}
```

```typescript
// .scripts/lib/prompts/search-multiselect.ts
import { cancelSymbol, type CancelSymbol } from './index'

/** A selectable item in the multiselect list. */
export interface SelectItem<T> {
  /** Display label. */
  label: string
  /** Underlying value returned when selected. */
  value: T
  /** If true, item is pre-selected and cannot be deselected. */
  locked?: boolean
}

/** Options for the search multiselect prompt. */
export interface SearchMultiselectOptions<T> {
  /** Prompt message displayed above the list. */
  message: string
  /** Available items. */
  items: SelectItem<T>[]
  /** Pre-selected item values (in addition to locked items). */
  initial?: T[]
  /** Maximum visible items before scrolling (default: 10). */
  pageSize?: number
  /** If true, skip prompt and return initial + locked items. */
  yes?: boolean
}

/**
 * Display a searchable multiselect prompt with fzf-style filtering.
 *
 * - Type to filter items (debounced 150ms)
 * - Space to toggle selection
 * - Enter to confirm
 * - Escape to cancel
 * - Locked items are always selected and cannot be toggled
 *
 * @param opts - Prompt configuration
 * @returns Selected values or cancelSymbol
 */
export async function searchMultiselect<T>(
  opts: SearchMultiselectOptions<T>,
): Promise<T[] | CancelSymbol> {
  const lockedValues = opts.items.filter((i) => i.locked).map((i) => i.value)
  const initialValues = [...lockedValues, ...(opts.initial ?? [])]

  // Non-interactive mode
  if (opts.yes || !process.stdin.isTTY) {
    return initialValues
  }

  // Full interactive implementation uses raw mode keypresses
  // and ANSI escape codes for rendering -- see full implementation
  // placeholder for plan purposes:
  return new Promise((resolve) => {
    const stdin = process.stdin
    if (!stdin.setRawMode) {
      resolve(initialValues)
      return
    }

    stdin.setRawMode(true)
    stdin.resume()

    let filterText = ''
    let selected = new Set(initialValues)
    let cursorIndex = 0
    let debounceTimer: ReturnType<typeof setTimeout> | null = null

    const filtered = () =>
      opts.items.filter((item) =>
        item.label.toLowerCase().includes(filterText.toLowerCase()),
      )

    const render = () => {
      // Clear and redraw using ANSI escape codes
      const items = filtered()
      const pageSize = opts.pageSize ?? 10
      // ... rendering logic with cursor positioning ...
      process.stdout.write(`\x1B[2K\r${opts.message} > ${filterText}\n`)
      for (let i = 0; i < Math.min(items.length, pageSize); i++) {
        const item = items[i]!
        const isSelected = selected.has(item.value)
        const isCursor = i === cursorIndex
        const prefix = isCursor ? '>' : ' '
        const check = isSelected ? '[x]' : '[ ]'
        const lock = item.locked ? ' (locked)' : ''
        process.stdout.write(`\x1B[2K${prefix} ${check} ${item.label}${lock}\n`)
      }
    }

    const onKeypress = (data: Buffer) => {
      const key = data.toString()

      // Escape
      if (key === '\x1B') {
        cleanup()
        resolve(cancelSymbol)
        return
      }

      // Enter
      if (key === '\r') {
        cleanup()
        resolve([...selected])
        return
      }

      // Space: toggle
      if (key === ' ') {
        const items = filtered()
        const item = items[cursorIndex]
        if (item && !item.locked) {
          if (selected.has(item.value)) selected.delete(item.value)
          else selected.add(item.value)
        }
        render()
        return
      }

      // Arrow up/down
      if (key === '\x1B[A') { cursorIndex = Math.max(0, cursorIndex - 1); render(); return }
      if (key === '\x1B[B') { cursorIndex = Math.min(filtered().length - 1, cursorIndex + 1); render(); return }

      // Backspace
      if (key === '\x7F') {
        filterText = filterText.slice(0, -1)
        cursorIndex = 0
        scheduleRender()
        return
      }

      // Printable character
      if (key.length === 1 && key >= ' ') {
        filterText += key
        cursorIndex = 0
        scheduleRender()
      }
    }

    const scheduleRender = () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(render, 150)
    }

    const cleanup = () => {
      stdin.setRawMode(false)
      stdin.pause()
      stdin.removeListener('data', onKeypress)
    }

    stdin.on('data', onKeypress)
    render()
  })
}
```

```typescript
// .scripts/lib/prompts/index.ts
/**
 * Interactive terminal prompt library.
 *
 * Zero external dependencies -- uses raw `node:readline` and ANSI escapes.
 * All prompts respect `--yes` flag and detect non-TTY environments.
 */

/** Symbol returned when the user cancels a prompt. */
export const cancelSymbol: unique symbol = Symbol('cancel')
export type CancelSymbol = typeof cancelSymbol

export { confirm, type ConfirmOptions } from './confirm'
export {
  searchMultiselect,
  type SearchMultiselectOptions,
  type SelectItem,
} from './search-multiselect'
```

#### Example Test Cases

```typescript
// .scripts/test/prompts.test.ts
import { describe, expect, test } from 'bun:test'
import { cancelSymbol } from '../lib/prompts/index'

// Note: Interactive prompt testing is limited without a real TTY.
// These tests verify non-interactive / --yes mode behavior.

describe('cancelSymbol', () => {
  test('is a unique symbol', () => {
    expect(typeof cancelSymbol).toBe('symbol')
    expect(cancelSymbol.toString()).toContain('cancel')
  })

  test('is not equal to any other symbol', () => {
    const other = Symbol('cancel')
    expect(cancelSymbol).not.toBe(other)
  })
})

describe('confirm (non-interactive)', () => {
  // Dynamic import to avoid TTY side effects at module level
  const getConfirm = async () => {
    const mod = await import('../lib/prompts/confirm')
    return mod.confirm
  }

  // --- Happy path: --yes flag ---
  test('returns default when yes=true', async () => {
    const confirm = await getConfirm()
    const result = await confirm({ message: 'Continue?', yes: true })
    expect(result).toBe(false) // default is false
  })

  test('returns custom default when yes=true', async () => {
    const confirm = await getConfirm()
    const result = await confirm({ message: 'Continue?', default: true, yes: true })
    expect(result).toBe(true)
  })

  // --- Edge case: non-TTY environment ---
  test('returns default in non-TTY (CI) environment', async () => {
    const confirm = await getConfirm()
    // In bun:test, stdin is not a TTY, so this should return default
    const result = await confirm({ message: 'Continue?', default: true })
    expect(result).toBe(true)
  })
})

describe('searchMultiselect (non-interactive)', () => {
  const getMultiselect = async () => {
    const mod = await import('../lib/prompts/search-multiselect')
    return mod.searchMultiselect
  }

  // --- Happy path: --yes flag returns initial + locked ---
  test('returns initial and locked items when yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select items:',
      items: [
        { label: 'A', value: 'a', locked: true },
        { label: 'B', value: 'b' },
        { label: 'C', value: 'c' },
      ],
      initial: ['c'],
      yes: true,
    })
    expect(Array.isArray(result)).toBe(true)
    if (Array.isArray(result)) {
      expect(result).toContain('a') // locked
      expect(result).toContain('c') // initial
      expect(result).not.toContain('b')
    }
  })

  // --- Edge case: no items ---
  test('returns empty array when no items and yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select:',
      items: [],
      yes: true,
    })
    expect(result).toEqual([])
  })

  // --- Edge case: all locked ---
  test('returns all locked items when yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select:',
      items: [
        { label: 'A', value: 'a', locked: true },
        { label: 'B', value: 'b', locked: true },
      ],
      yes: true,
    })
    expect(result).toEqual(['a', 'b'])
  })
})
```

#### Edge Cases

| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| Non-TTY environment | Running in CI pipeline | Returns default values without interaction |
| `--yes` flag | `opts.yes = true` | Returns default/initial values immediately |
| Escape pressed | User presses Escape | Returns `cancelSymbol` |
| Empty items list | No items to select from | Shows empty list, Enter returns `[]` |
| All items locked | Every item has `locked: true` | All shown as selected, cannot toggle, Enter returns all |
| Filter matches nothing | Search text produces 0 results | Empty list shown, Enter returns currently selected |
| Very long item labels | Labels > terminal width | Truncated with ellipsis in rendering |
| Rapid typing | User types faster than debounce | Only final debounced render fires |
| stdin not available | `process.stdin.setRawMode` is undefined | Returns initial/default values |
| Unicode in filter | User types emoji or CJK characters | Filter works on `.includes()` (Unicode-safe) |

#### Acceptance Criteria

- [ ] `confirm` returns `boolean | CancelSymbol`
- [ ] `searchMultiselect` returns `T[] | CancelSymbol`
- [ ] Both prompts return defaults when `yes: true` is passed
- [ ] Both prompts return defaults when `process.stdin.isTTY` is false
- [ ] `cancelSymbol` is a unique symbol exported from `index.ts`
- [ ] Locked items cannot be deselected in multiselect
- [ ] Search filter is debounced at ~150ms
- [ ] No external npm dependencies added (raw `node:readline` only)
- [ ] Barrel export from `lib/prompts/index.ts` re-exports all public types and functions
- [ ] Tests cover non-interactive mode (TTY interaction cannot be unit-tested)

## Notes

- Source parser uses `#` for git ref (not `@`) to avoid collision with `owner/repo@skill` convention
- Agent registry data extracted from vercel-labs/skills v0.5.x (MIT license) -- we maintain our own copy
- Agent detection is config-dir-only (`existsSync(~/.cursor)`), not binary detection (`which cursor`)
- The prompt library is intentionally in `lib/prompts/` not `commands/` -- it's reusable infrastructure
- Git wrapper uses `simple-git` instead of raw `spawnSync(['git', ...])` — typed responses, AbortController, `raw()` for worktrees
- Agent registry uses `xdg-basedir` for correct XDG path resolution on XDG-aware agents
- `fetchSkillFolderHash` lives in `git.ts` despite using the GitHub API because it's specifically for git-hosted skill version tracking -- it bridges git refs and GitHub's Trees API
- `skill-discovery.ts` is the recursive SKILL.md scanner that `add`, `sync`, and `catalog` commands all need
