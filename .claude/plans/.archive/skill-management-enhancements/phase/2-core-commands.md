# Phase 2: Core Commands + Filters (add, init, list, filters)

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** pending
**Effort:** TBD

## Objective

Implement the three most-used skill management commands: `add` (install skills from sources), `init` (scaffold new skills), and `list` (show installed skills with filters). Also create the shared filter utilities (`--agent`/`--skill`) needed by all subsequent commands.

## Success Criteria

- [ ] `just agents skill add owner/repo@skill` installs a skill to detected agents
- [ ] `just agents skill add owner/repo#branch:path` clones at specific ref and subpath
- [ ] `just agents skill init my-skill` creates a SKILL.md from configurable template
- [ ] `just agents skill list` shows installed skills with agent/plugin grouping
- [ ] `just agents skill list --json` outputs machine-readable JSON
- [ ] `just agents skill list context/skills` lists skills at a custom path
- [ ] `--agent claude-code` and `--skill name` filters work on list
- [ ] `--copy` and `--symlink` install modes work
- [ ] Lock files updated on add (both global and local)
- [ ] `filterByAgent` and `filterBySkill` utility functions exported from `lib/skill-filters.ts`
- [ ] `validateAgentFilter` warns on unknown agent names
- [ ] Citty `filterArgs` shared definition available for all commands

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Filter utilities | `cli/lib/skill-filters.ts` | TypeScript |
| Filter tests | `cli/test/skill-filters.test.ts` | bun:test |
| Add command logic | `cli/lib/skill-add.ts` | TypeScript |
| Init command logic | `cli/lib/skill-init.ts` | TypeScript |
| List command logic | `cli/lib/skill-list.ts` | TypeScript |
| Skill init template | `cli/templates/SKILL.md.tmpl` | Markdown template |
| CLI subcommand wiring | `cli/commands/skill.ts` | TypeScript (additions) |
| Tests | `cli/test/skill-add.test.ts` | bun:test |
| Tests | `cli/test/skill-init.test.ts` | bun:test |
| Tests | `cli/test/skill-list.test.ts` | bun:test |

## Files

**Create:**

- `cli/lib/skill-filters.ts`
- `cli/lib/skill-add.ts`
- `cli/lib/skill-init.ts`
- `cli/lib/skill-list.ts`
- `cli/templates/SKILL.md.tmpl`
- `cli/test/skill-filters.test.ts`
- `cli/test/skill-add.test.ts`
- `cli/test/skill-init.test.ts`
- `cli/test/skill-list.test.ts`

**Modify:**

- `cli/commands/skill.ts` (add `add`, `init`, `list` subcommands)
- `cli/lib/lockfile.ts` (extend skills schema if needed for ref/sourceUrl fields)

## Tasks

### 2.0 Filter Utilities (`lib/skill-filters.ts`)

**Depends on:** phase-1 (`lib/agents.ts` for agent registry)

**Library Decisions:** No new deps. Uses `lib/agents.ts` (agent registry validation), Citty `ArgDef`. Pure utility functions with no side effects.

- [ ] Implement `filterByAgent(skills, agentFilter)` and `filterBySkill(skills, skillFilter)`
- [ ] Implement `validateAgentFilter(agentName, out)` — warns on unknown agent
- [ ] Export `filterArgs` Citty argument definitions for `--agent` and `--skill`
- [ ] Write tests with >= 3 cases per function

#### Code Examples

```typescript
// cli/lib/skill-filters.ts (new shared helper)

import type { AgentType } from './agents'
import { agents, detectInstalledAgents } from './agents'
import { createOutput, type OutputFormatter } from './output'

/** Installed skill with agent association metadata. */
export interface InstalledSkillEntry {
  name: string
  agents: AgentType[]
  source?: string
  computedHash?: string
  symlinkTarget?: string
}

/**
 * Filter skills to those installed for a specific agent.
 * Returns the full list if agentFilter is undefined.
 */
export function filterByAgent(
  skills: InstalledSkillEntry[],
  agentFilter?: string,
): InstalledSkillEntry[] {
  if (!agentFilter) return skills
  return skills.filter((s) => s.agents.includes(agentFilter as AgentType))
}

/**
 * Filter skills by name (exact match, case-insensitive).
 * Returns the full list if skillFilter is undefined.
 */
export function filterBySkill(
  skills: InstalledSkillEntry[],
  skillFilter?: string,
): InstalledSkillEntry[] {
  if (!skillFilter) return skills
  const lower = skillFilter.toLowerCase()
  return skills.filter((s) => s.name.toLowerCase() === lower)
}

/**
 * Validate an agent name against the registry.
 * Emits a warning via the output formatter if the agent is unknown.
 * Returns true if valid.
 */
export function validateAgentFilter(
  agentName: string,
  out: OutputFormatter,
): boolean {
  if (agentName in agents) return true
  out.warn(
    `Unknown agent "${agentName}". Known agents: ${Object.keys(agents).slice(0, 5).join(', ')}...`,
  )
  return false
}
```

```typescript
// Citty argument definitions (added to commands/skill.ts shared args)
import type { ArgDef } from 'citty'

export const filterArgs = {
  agent: {
    type: 'string',
    description: 'Filter by agent name (e.g., claude-code, cursor)',
  },
  skill: {
    type: 'string',
    description: 'Filter by skill name',
  },
} as const satisfies Record<string, ArgDef>
```

#### Example Test Cases

```typescript
// cli/test/skill-filters.test.ts
import { describe, expect, test } from 'bun:test'
import { filterByAgent, filterBySkill, validateAgentFilter } from '../lib/skill-filters'

describe('filterByAgent', () => {
  const skills = [
    { name: 'beads', agents: ['claude-code' as const], source: 'steveyegge/beads' },
    { name: 'lang-ts', agents: ['claude-code' as const, 'cursor' as const], source: 'local' },
    { name: 'react', agents: ['cursor' as const], source: 'local' },
  ]

  test('filters to matching agent only', () => {
    const result = filterByAgent(skills, 'cursor')
    expect(result).toHaveLength(2)
    expect(result.map((s) => s.name)).toEqual(['lang-ts', 'react'])
  })

  test('returns all skills when no filter provided', () => {
    const result = filterByAgent(skills, undefined)
    expect(result).toHaveLength(3)
  })

  test('returns empty array when agent has no skills', () => {
    const result = filterByAgent(skills, 'windsurf')
    expect(result).toHaveLength(0)
  })
})

describe('filterBySkill', () => {
  const skills = [
    { name: 'beads', agents: ['claude-code' as const] },
    { name: 'Lang-TS', agents: ['claude-code' as const] },
  ]

  test('matches case-insensitively', () => {
    const result = filterBySkill(skills, 'lang-ts')
    expect(result).toHaveLength(1)
    expect(result[0].name).toBe('Lang-TS')
  })

  test('returns empty for unknown skill', () => {
    const result = filterBySkill(skills, 'nonexistent')
    expect(result).toHaveLength(0)
  })

  test('returns all when filter is undefined', () => {
    const result = filterBySkill(skills, undefined)
    expect(result).toHaveLength(2)
  })
})

describe('validateAgentFilter', () => {
  test('warns on unknown agent name', () => {
    const warnings: string[] = []
    const mockOut = { warn: (msg: string) => warnings.push(msg) } as any
    const valid = validateAgentFilter('unknown-agent', mockOut)
    expect(valid).toBe(false)
    expect(warnings).toHaveLength(1)
    expect(warnings[0]).toContain('Unknown agent')
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `--agent` with agent that has no skills | Return empty list, no error |
| `--skill` with glob pattern (e.g., `lang-*`) | Exact match only; glob support deferred |
| `--agent unknown-agent` | Warn but do not error; return empty result set |
| `--agent` and `--skill` combined | Apply both filters (intersection) |
| `--agent` with mixed-case name | Case-sensitive match against registry keys |

#### Acceptance Criteria

- [ ] `filterByAgent` and `filterBySkill` exported from `lib/skill-filters.ts`
- [ ] `validateAgentFilter` warns on unknown agent (not hard error)
- [ ] `filterArgs` Citty definitions exported for reuse by all commands
- [ ] Filter functions unit-tested with >= 3 cases each
- [ ] No external npm dependencies added

---

### 2.1 Add Command (`lib/skill-add.ts`)

**Depends on:** phase-1 (source-parser, git, skill-discovery, agents, prompts)

**Library decisions:** No new dependencies. Orchestrates existing Phase 1 modules (`lib/source-parser.ts`, `lib/git.ts`, `lib/skill-discovery.ts`, `lib/agents.ts`, `lib/prompts/`) plus existing `lib/symlink.ts`, `lib/lockfile.ts`, and `lib/runtime.ts`.

- [ ] Export `addSkill(source: string, opts: AddOptions): Promise<AddResult>`
- [ ] Orchestration flow:
  1. `parseSource(source)` -> `ParsedSource`
  2. If remote: `cloneRepo(url, ref)` -> temp dir
  3. `discoverSkills(dir, subpath)` -> `Skill[]` via `lib/skill-discovery.ts`
  4. If `skillFilter`: `filterSkills(skills, [skillFilter])`
  5. If interactive + multiple skills: prompt for selection via `searchMultiselect`
  6. If interactive: prompt for agent selection via `searchMultiselect` (auto-select if only one detected)
  7. If interactive: prompt for scope (project vs global)
  8. Install mode: `--copy` or `--symlink` (default: symlink)
  9. For each (skill, agent): copy to canonical dir, symlink from agent dir (using `lib/symlink.ts`)
  10. Update global lock (`skill-lock`) and local lock (`lockfile.ts`)
  11. Cleanup temp dir via `cleanup()` from `cloneRepo`
- [ ] Support `AddOptions`: `{ skill?, agent?, global?, copy?, yes?, fullDepth? }`
- [ ] Handle well-known sources (HTTP fetch, no clone)
- [ ] Handle local sources (no clone, direct path)
- [ ] Emit structured `AddResult` for JSON consumers
- [ ] `addSkill` is a parallel system -- does NOT modify `sources.yaml`

**Error handling per step:**

| Step | Failure | Behavior |
|------|---------|----------|
| parseSource | Invalid format | Return `AddResult { error: 'invalid_source' }` |
| cloneRepo | Timeout/auth/404 | Return `AddResult { error: 'clone_failed', detail }` |
| discoverSkills | No SKILL.md found | Return `AddResult { error: 'no_skills_found' }` |
| filterSkills | No match | Return `AddResult { error: 'skill_not_found', available: [...] }` |
| install (copy/symlink) | Permission denied | Try copy fallback if symlink fails; report if both fail |
| lock write | I/O error | Warn but don't fail (skill is installed, lock is stale) |

#### Error Types

```typescript
/**
 * Discriminated union of errors the add command can produce.
 * The `code` field acts as the discriminant for exhaustive handling.
 */
type AddErrorCode =
  | 'invalid_source'
  | 'clone_failed'
  | 'clone_timeout'
  | 'no_skills_found'
  | 'skill_not_found'
  | 'install_failed'
  | 'lock_write_failed'
  | 'no_agents_detected'
  | 'cancelled'

interface AddError {
  readonly code: AddErrorCode
  readonly message: string
  /** Available skill names when code is 'skill_not_found' */
  readonly available?: string[]
  /** Underlying CliError for wrapping git/IO failures */
  readonly cause?: CliError
}
```

#### Code Examples

```typescript
// cli/lib/skill-add.ts

import type { ParsedSource } from './source-parser'
import type { Skill } from './skill-discovery'
import type { AgentType } from './agents'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface AddOptions {
  /** Filter to a specific skill name within the source */
  skill?: string
  /** Target a specific agent instead of prompting */
  agent?: AgentType
  /** Install to global agent dir instead of project-local */
  global?: boolean
  /** Copy files instead of symlinking */
  copy?: boolean
  /** Skip interactive prompts (CI mode) */
  yes?: boolean
  /** Clone full history instead of shallow */
  fullDepth?: boolean
}

export interface InstalledEntry {
  skill: string
  agent: AgentType
  path: string
  mode: 'copy' | 'symlink'
}

export interface AddResult {
  ok: boolean
  installed: InstalledEntry[]
  error?: AddError
  warnings: string[]
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

/**
 * Install one or more skills from a source string.
 *
 * Orchestrates parsing, cloning, discovery, prompting, installation,
 * and lock file updates. Each step can fail independently; failures
 * are captured in the returned `AddResult` rather than thrown.
 *
 * @param source - A source specifier (e.g. `owner/repo@skill`, `./local/path`)
 * @param opts   - Installation options
 * @returns Structured result with installed entries or error details
 */
export async function addSkill(
  source: string,
  opts: AddOptions = {},
): Promise<AddResult> {
  const { parseSource } = await import('./source-parser')
  const { cloneRepo, cleanupTempDir } = await import('./git')
  const { discoverSkills, filterSkills } = await import('./skill-discovery')
  const { detectInstalledAgents, getAgentBaseDir } = await import('./agents')
  const { searchMultiselect, confirm } = await import('./prompts')
  const { createSymlink } = await import('./symlink')
  const { writeLockfile } = await import('./lockfile')

  const warnings: string[] = []
  let tempDir: string | undefined

  try {
    // Step 1: Parse source
    const parsed = parseSource(source)
    if (!parsed.ok) {
      return { ok: false, installed: [], error: { code: 'invalid_source', message: parsed.error.message }, warnings }
    }

    // Step 2: Resolve to a local directory
    let searchDir: string
    if (parsed.value.type === 'local') {
      searchDir = parsed.value.localPath!
    } else {
      const clone = await cloneRepo(parsed.value.url!, parsed.value.ref)
      tempDir = clone.tempDir
      searchDir = clone.tempDir
    }

    // Step 3: Discover skills
    const skills = await discoverSkills(searchDir, parsed.value.subpath)
    if (skills.length === 0) {
      return { ok: false, installed: [], error: { code: 'no_skills_found', message: `No SKILL.md found in ${source}` }, warnings }
    }

    // Step 4: Filter if skill name specified
    let selected: Skill[]
    if (opts.skill || parsed.value.skillFilter) {
      const filterName = opts.skill ?? parsed.value.skillFilter!
      selected = filterSkills(skills, [filterName])
      if (selected.length === 0) {
        return {
          ok: false,
          installed: [],
          error: {
            code: 'skill_not_found',
            message: `Skill "${filterName}" not found`,
            available: skills.map((s) => s.name),
          },
          warnings,
        }
      }
    } else if (skills.length > 1 && !opts.yes) {
      // Step 5: Interactive skill selection
      selected = await searchMultiselect({
        message: 'Select skills to install',
        items: skills,
        labelKey: 'name',
      })
    } else {
      selected = skills
    }

    // Step 6: Detect agents
    const agents = await detectInstalledAgents()
    if (agents.length === 0) {
      return { ok: false, installed: [], error: { code: 'no_agents_detected', message: 'No supported agents found on this machine' }, warnings }
    }

    // ... Steps 7-11: agent selection, scope, install, lock update
    // (full implementation follows this pattern)

    return { ok: true, installed: [], warnings }
  } finally {
    if (tempDir) await cleanupTempDir(tempDir)
  }
}
```

#### Example Test Cases

```typescript
// cli/test/skill-add.test.ts

import { afterAll, beforeAll, describe, expect, mock, test } from 'bun:test'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

describe('addSkill', () => {
  let fixtureDir: string

  beforeAll(async () => {
    fixtureDir = await mkdtemp(join(tmpdir(), 'skill-add-test-'))
    // Create a minimal skill fixture
    const skillDir = join(fixtureDir, 'my-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: Test skill\nversion: 0.1.0\n---\n# My Skill\n',
    )
  })

  afterAll(async () => {
    await rm(fixtureDir, { recursive: true, force: true })
  })

  test('adds skill from local source (no clone)', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const result = await addSkill(fixtureDir, {
      yes: true,
      agent: 'claude-code' as any,
    })
    expect(result.ok).toBe(true)
    expect(result.installed.length).toBeGreaterThanOrEqual(1)
    expect(result.installed[0]!.skill).toBe('my-skill')
  })

  test('returns no_skills_found for source without SKILL.md', async () => {
    const emptyDir = await mkdtemp(join(tmpdir(), 'skill-add-empty-'))
    const { addSkill } = await import('../lib/skill-add')
    const result = await addSkill(emptyDir, { yes: true })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('no_skills_found')
    await rm(emptyDir, { recursive: true, force: true })
  })

  test('returns invalid_source for malformed source string', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const result = await addSkill('', { yes: true })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('invalid_source')
  })

  test('returns skill_not_found with available names when filter misses', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const result = await addSkill(fixtureDir, {
      yes: true,
      skill: 'nonexistent-skill',
    })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('skill_not_found')
    expect(result.error?.available).toContain('my-skill')
  })
})
```

#### Edge Cases

| Input / Scenario | Expected Behavior |
|---|---|
| Source has no SKILL.md anywhere | Return `{ ok: false, error: { code: 'no_skills_found' } }` |
| Clone exceeds 60s timeout | Return `{ ok: false, error: { code: 'clone_timeout' } }`, cleanup temp dir |
| Skill already installed at target path | Overwrite if `--yes`; prompt for confirmation otherwise |
| No agents detected on machine | Return `{ ok: false, error: { code: 'no_agents_detected' } }` |
| Well-known source (HTTPS, not git) | HTTP fetch skill manifest, skip `cloneRepo` entirely |
| Local path does not exist | `parseSource` returns error; propagated as `invalid_source` |
| Source has 50+ skills, no filter | Show `searchMultiselect`; in `--yes` mode install all |
| Symlink creation fails (permissions) | Fall back to copy mode; add warning to `result.warnings` |
| Lock write fails after install | Add warning but return `ok: true` (skill is installed) |
| `owner/repo@skill` with `--skill other` | CLI `--skill` overrides the `@skill` in the source string |

#### Acceptance Criteria

- [ ] `addSkill()` returns `AddResult` for all code paths (never throws)
- [ ] Remote sources are shallow-cloned and temp dirs are cleaned up even on error
- [ ] Local sources skip the clone step entirely
- [ ] `--yes` skips all interactive prompts and installs all discovered skills
- [ ] `--copy` copies files instead of creating symlinks
- [ ] Lock file is updated with source URL, source type, and computed hash
- [ ] The function is fully testable with mocked git and agent detection
- [ ] JSON consumers get structured `AddResult` (no console side effects in the library)

---

### 2.2 Init Command (`lib/skill-init.ts`)

**Depends on:** phase-1 (agents module for default path resolution)

**Library decisions:** No new dependencies. Uses `writeText` and `fileExists` from `lib/runtime.ts` for filesystem operations. Template rendering uses plain `String.prototype.replace()` with `{{name}}` / `{{description}}` placeholders -- no template engine dependency.

- [ ] Export `initSkill(name: string, opts: InitOptions): Promise<void>`
- [ ] Template resolution order:
  1. `opts.template` (explicit path)
  2. `cli/templates/SKILL.md.tmpl` (project template)
  3. Built-in hardcoded template (fallback)
- [ ] Generate frontmatter with `name`, `description` (prompted or from `--description`)
- [ ] Optionally generate additional sections based on template
- [ ] Create directory at `opts.path` or default `context/skills/<name>/`
- [ ] Write `SKILL.md` from template
- [ ] Validate output via `readSkillFrontmatter` (eat your own dog food)

#### Error Types

```typescript
/**
 * Discriminated union of errors the init command can produce.
 */
type InitErrorCode =
  | 'invalid_name'
  | 'dir_exists'
  | 'template_not_found'
  | 'template_read_failed'
  | 'write_failed'
  | 'validation_failed'

interface InitError {
  readonly code: InitErrorCode
  readonly message: string
  readonly cause?: CliError
}
```

#### Code Examples

```typescript
// cli/lib/skill-init.ts

import { join, resolve } from 'node:path'
import { mkdir } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { readText, writeText, fileExists } from './runtime'
import { readSkillFrontmatter } from './manifest'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface InitOptions {
  /** Short description for the skill frontmatter */
  description?: string
  /** Explicit path to a custom template file */
  template?: string
  /** Target directory (default: context/skills/<name>/) */
  path?: string
  /** Skip confirmation prompts */
  yes?: boolean
}

export interface InitResult {
  ok: boolean
  skillPath: string
  error?: InitError
}

// ---------------------------------------------------------------------------
// Template
// ---------------------------------------------------------------------------

/** Built-in fallback template when no file-based template is found. */
const BUILTIN_TEMPLATE = `---
name: {{name}}
description: {{description}}
version: 0.1.0
tags: []
---

# {{name}}

{{description}}

## Usage

<!-- Describe when and how to use this skill -->

## References

<!-- Links to relevant documentation -->
`

/**
 * Resolve and read a template, following the priority chain:
 * 1. Explicit path from opts
 * 2. Project-local cli/templates/SKILL.md.tmpl
 * 3. Built-in hardcoded template
 */
async function resolveTemplate(
  explicitPath?: string,
  projectRoot?: string,
): Promise<Result<string>> {
  if (explicitPath) {
    if (!existsSync(explicitPath)) {
      return err(new CliError(
        `Template not found: ${explicitPath}`,
        'E_TEMPLATE_NOT_FOUND',
      ))
    }
    return ok(await readText(explicitPath))
  }

  if (projectRoot) {
    const projectTemplate = join(projectRoot, 'cli/templates/SKILL.md.tmpl')
    if (existsSync(projectTemplate)) {
      return ok(await readText(projectTemplate))
    }
  }

  return ok(BUILTIN_TEMPLATE)
}

/**
 * Render a template by replacing `{{key}}` placeholders.
 * Uses simple string replacement -- no template engine needed.
 */
function renderTemplate(
  template: string,
  vars: Record<string, string>,
): string {
  let result = template
  for (const [key, value] of Object.entries(vars)) {
    result = result.replaceAll(`{{${key}}}`, value)
  }
  return result
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/** Skill names must be lowercase kebab-case: letters, digits, hyphens. */
const VALID_NAME_RE = /^[a-z][a-z0-9-]*[a-z0-9]$/

function validateName(name: string): Result<string> {
  if (name.length < 2) {
    return err(new CliError('Skill name must be at least 2 characters', 'E_INVALID_NAME'))
  }
  if (!VALID_NAME_RE.test(name)) {
    return err(new CliError(
      `Invalid skill name: "${name}"`,
      'E_INVALID_NAME',
      'Must be lowercase kebab-case (e.g. my-skill, lang-rust-dev)',
    ))
  }
  return ok(name)
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

/**
 * Scaffold a new skill directory with a SKILL.md from template.
 *
 * @param name - Kebab-case skill name (e.g. `lang-rust-dev`)
 * @param opts - Options for description, template, and target path
 * @returns Path to the created SKILL.md or an error
 */
export async function initSkill(
  name: string,
  opts: InitOptions = {},
): Promise<InitResult> {
  // Validate name
  const nameResult = validateName(name)
  if (!nameResult.ok) {
    return { ok: false, skillPath: '', error: { code: 'invalid_name', message: nameResult.error.message } }
  }

  // Resolve target directory
  const targetDir = opts.path
    ? resolve(opts.path)
    : join(process.cwd(), 'context/skills', name)

  const skillPath = join(targetDir, 'SKILL.md')

  // Check for existing directory with SKILL.md
  if (existsSync(skillPath) && !opts.yes) {
    return { ok: false, skillPath, error: { code: 'dir_exists', message: `SKILL.md already exists at ${skillPath}` } }
  }

  // Resolve and render template
  const tmplResult = await resolveTemplate(opts.template)
  if (!tmplResult.ok) {
    return { ok: false, skillPath, error: { code: 'template_not_found', message: tmplResult.error.message } }
  }

  const rendered = renderTemplate(tmplResult.value, {
    name,
    description: opts.description ?? `A skill for ${name}`,
  })

  // Write to disk
  await mkdir(targetDir, { recursive: true })
  await writeText(skillPath, rendered)

  // Self-validate the output
  const validation = await readSkillFrontmatter(skillPath)
  if (!validation.ok) {
    return { ok: false, skillPath, error: { code: 'validation_failed', message: validation.error.message, cause: validation.error } }
  }

  return { ok: true, skillPath }
}
```

```markdown
<!-- cli/templates/SKILL.md.tmpl -->
---
name: {{name}}
description: {{description}}
version: 0.1.0

## tags: []

---

# {{name}}

{{description}}

## Usage

<!-- Describe when and how to use this skill -->

## References

<!-- Links to relevant documentation -->
```

#### Example Test Cases

```typescript
// cli/test/skill-init.test.ts

import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { mkdtemp, rm, readFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

describe('initSkill', () => {
  let workDir: string

  beforeAll(async () => {
    workDir = await mkdtemp(join(tmpdir(), 'skill-init-test-'))
  })

  afterAll(async () => {
    await rm(workDir, { recursive: true, force: true })
  })

  test('generates SKILL.md from built-in template', async () => {
    const { initSkill } = await import('../lib/skill-init')
    const result = await initSkill('my-test-skill', {
      description: 'A test skill',
      path: join(workDir, 'my-test-skill'),
    })
    expect(result.ok).toBe(true)
    expect(existsSync(result.skillPath)).toBe(true)

    const content = await readFile(result.skillPath, 'utf-8')
    expect(content).toContain('name: my-test-skill')
    expect(content).toContain('description: A test skill')
  })

  test('uses custom template when provided', async () => {
    const tmplPath = join(workDir, 'custom.tmpl')
    await Bun.write(tmplPath, '---\nname: {{name}}\ndescription: {{description}}\nversion: 1.0.0\n---\nCustom: {{name}}\n')

    const { initSkill } = await import('../lib/skill-init')
    const result = await initSkill('custom-skill', {
      template: tmplPath,
      path: join(workDir, 'custom-skill'),
    })
    expect(result.ok).toBe(true)

    const content = await readFile(result.skillPath, 'utf-8')
    expect(content).toContain('version: 1.0.0')
    expect(content).toContain('Custom: custom-skill')
  })

  test('returns dir_exists error when SKILL.md already exists', async () => {
    // First init succeeds
    const { initSkill } = await import('../lib/skill-init')
    const dir = join(workDir, 'existing-skill')
    await initSkill('existing-skill', { path: dir })

    // Second init without --yes should fail
    const result = await initSkill('existing-skill', { path: dir })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('dir_exists')
  })

  test('rejects invalid skill names', async () => {
    const { initSkill } = await import('../lib/skill-init')

    const spaceName = await initSkill('my skill', { path: join(workDir, 'bad1') })
    expect(spaceName.ok).toBe(false)
    expect(spaceName.error?.code).toBe('invalid_name')

    const upperName = await initSkill('MySkill', { path: join(workDir, 'bad2') })
    expect(upperName.ok).toBe(false)
    expect(upperName.error?.code).toBe('invalid_name')
  })
})
```

#### Edge Cases

| Input / Scenario | Expected Behavior |
|---|---|
| Skill name with spaces (`my skill`) | Return `{ ok: false, error: { code: 'invalid_name' } }` |
| Skill name with special chars (`my_skill!`) | Return `{ ok: false, error: { code: 'invalid_name' } }` |
| Skill name is uppercase (`MySkill`) | Return `{ ok: false, error: { code: 'invalid_name' } }` |
| Single character name (`a`) | Return `{ ok: false, error: { code: 'invalid_name' } }` |
| Directory already exists with SKILL.md | Return `dir_exists` error unless `--yes` is set |
| Directory exists but has no SKILL.md | Create SKILL.md in existing directory (safe) |
| Template path does not exist | Return `{ ok: false, error: { code: 'template_not_found' } }` |
| Template produces invalid frontmatter | Return `{ ok: false, error: { code: 'validation_failed' } }` |
| No `--description` provided | Use fallback: `"A skill for <name>"` |
| `--path` with deeply nested non-existent dirs | `mkdir -p` creates all intermediate directories |

#### Acceptance Criteria

- [ ] `initSkill()` returns `InitResult` for all code paths (never throws)
- [ ] Name validation rejects anything that is not lowercase kebab-case
- [ ] Template resolution follows the documented 3-level priority chain
- [ ] Template uses `{{name}}` and `{{description}}` -- no template engine dependency
- [ ] Generated SKILL.md passes `readSkillFrontmatter` validation (self-test)
- [ ] `--yes` overwrites an existing SKILL.md without prompting
- [ ] Default output path is `context/skills/<name>/SKILL.md`
- [ ] Custom `--path` is respected and directories are created recursively

---

### 2.3 List Command (`lib/skill-list.ts`)

**Depends on:** 2.1 (shares `InstalledEntry` type concept), phase-1 (agents module)

**Library decisions:** Uses `console-table-printer` (already in `package.json` at `^2.15.0`) for human-readable table output via `lib/output.ts`. JSON mode emits raw arrays. No new dependencies.

- [ ] Export `listSkills(opts: ListOptions): Promise<InstalledSkill[]>`
- [ ] Scan path (default: `context/skills/`, override via positional arg)
- [ ] For each skill dir: `readSkillFrontmatter` to get metadata
- [ ] Detect which agents have the skill installed (check agent dirs + symlinks via `lib/agents.ts`)
- [ ] Support `--agent <name>` filter: only show skills installed for that agent
- [ ] Support `--skill <name>` filter: only show matching skills
- [ ] Support `--json` output: array of `InstalledSkill` objects
- [ ] Support `--global` to scan global install dirs
- [ ] Human output: grouped by plugin (if lock file has plugin info), tabular via `console-table-printer`

#### Error Types

```typescript
/**
 * Discriminated union of errors the list command can produce.
 */
type ListErrorCode =
  | 'scan_dir_not_found'
  | 'scan_failed'
  | 'global_dir_not_found'

interface ListError {
  readonly code: ListErrorCode
  readonly message: string
  readonly cause?: CliError
}
```

#### Code Examples

```typescript
// cli/lib/skill-list.ts

import { join, resolve } from 'node:path'
import { readdirSync, statSync, lstatSync } from 'node:fs'
import { readSkillFrontmatter } from './manifest'
import { detectInstalledAgents, getAgentBaseDir, type AgentType } from './agents'
import { auditSymlinks } from './symlink'
import { CliError, type Result, ok, err } from './types'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface ListOptions {
  /** Directory to scan (default: context/skills/) */
  path?: string
  /** Filter by agent name */
  agent?: string
  /** Filter by skill name (substring match) */
  skill?: string
  /** Scan global install directories instead of project-local */
  global?: boolean
  /** Output as JSON array */
  json?: boolean
}

export interface InstalledSkill {
  /** Skill name from frontmatter */
  name: string
  /** Short description from frontmatter */
  description: string
  /** Semver version from frontmatter */
  version?: string
  /** Absolute path to the skill directory */
  path: string
  /** Agents that have this skill installed */
  agents: AgentType[]
  /** Whether the skill dir is a symlink */
  isSymlink: boolean
  /** Source info from lock file, if available */
  source?: string
  /** Tags from frontmatter */
  tags?: string[]
}

export interface ListResult {
  ok: boolean
  skills: InstalledSkill[]
  error?: ListError
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * List all valid skill directory names under a given path.
 * Skips dotdirs, .templates, and non-directories.
 */
function scanSkillDirs(dir: string): string[] {
  try {
    return readdirSync(dir)
      .filter((name) => !name.startsWith('.') && name !== '.templates' && name !== 'justfile')
      .filter((name) => {
        try {
          return statSync(join(dir, name)).isDirectory()
        } catch {
          return false
        }
      })
      .sort()
  } catch {
    return []
  }
}

/**
 * Check if a skill directory is a symlink.
 */
function isSymlinkDir(path: string): boolean {
  try {
    return lstatSync(path).isSymbolicLink()
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

/**
 * Scan for installed skills and return structured metadata.
 *
 * Reads frontmatter from each SKILL.md, checks agent installation
 * status, and applies optional filters.
 *
 * @param opts - Scan path, filters, and output options
 * @returns Array of installed skill metadata or an error
 */
export async function listSkills(
  opts: ListOptions = {},
): Promise<ListResult> {
  const scanDir = opts.path ? resolve(opts.path) : join(process.cwd(), 'context/skills')

  try {
    statSync(scanDir)
  } catch {
    return {
      ok: false,
      skills: [],
      error: { code: 'scan_dir_not_found', message: `Skills directory not found: ${scanDir}` },
    }
  }

  const dirs = scanSkillDirs(scanDir)
  const skills: InstalledSkill[] = []

  // Detect agents once for all skills
  const installedAgents = await detectInstalledAgents()

  for (const dirName of dirs) {
    const skillDir = join(scanDir, dirName)
    const skillMdPath = join(skillDir, 'SKILL.md')

    const frontmatter = await readSkillFrontmatter(skillMdPath)
    if (!frontmatter.ok) {
      // Skill dir exists but has no valid SKILL.md -- skip with warning
      continue
    }

    // Check which agents have this skill
    const agentsWithSkill: AgentType[] = []
    for (const agent of installedAgents) {
      const agentDir = getAgentBaseDir(agent, opts.global ?? false)
      // Check if agent skills dir contains a symlink or copy of this skill
      // Implementation checks agent-specific skill directories
    }

    const entry: InstalledSkill = {
      name: frontmatter.value.name,
      description: frontmatter.value.description,
      version: frontmatter.value.version,
      path: skillDir,
      agents: agentsWithSkill,
      isSymlink: isSymlinkDir(skillDir),
      source: frontmatter.value.source,
      tags: frontmatter.value.tags,
    }

    skills.push(entry)
  }

  // Apply filters
  let filtered = skills
  if (opts.skill) {
    const q = opts.skill.toLowerCase()
    filtered = filtered.filter((s) => s.name.toLowerCase().includes(q))
  }
  if (opts.agent) {
    filtered = filtered.filter((s) => s.agents.includes(opts.agent as AgentType))
  }

  return { ok: true, skills: filtered }
}
```

#### Example Test Cases

```typescript
// cli/test/skill-list.test.ts

import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { mkdtemp, mkdir, writeFile, rm, symlink } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

describe('listSkills', () => {
  let fixtureDir: string

  beforeAll(async () => {
    fixtureDir = await mkdtemp(join(tmpdir(), 'skill-list-test-'))

    // Create two skill directories with valid SKILL.md
    for (const name of ['alpha-skill', 'beta-skill']) {
      const dir = join(fixtureDir, name)
      await mkdir(dir, { recursive: true })
      await writeFile(
        join(dir, 'SKILL.md'),
        `---\nname: ${name}\ndescription: Test ${name}\nversion: 0.1.0\ntags:\n  - test\n---\n# ${name}\n`,
      )
    }

    // Create a directory without SKILL.md (should be skipped)
    await mkdir(join(fixtureDir, 'no-skill-dir'))
    await writeFile(join(fixtureDir, 'no-skill-dir', 'README.md'), '# Not a skill')

    // Create a dotdir (should be skipped)
    await mkdir(join(fixtureDir, '.hidden'))
  })

  afterAll(async () => {
    await rm(fixtureDir, { recursive: true, force: true })
  })

  test('scans directory and returns skills with frontmatter', async () => {
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ path: fixtureDir })
    expect(result.ok).toBe(true)
    expect(result.skills.length).toBe(2)
    expect(result.skills.map((s) => s.name).sort()).toEqual(['alpha-skill', 'beta-skill'])
    expect(result.skills[0]!.version).toBe('0.1.0')
  })

  test('filters by --skill name (substring match)', async () => {
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ path: fixtureDir, skill: 'alpha' })
    expect(result.ok).toBe(true)
    expect(result.skills.length).toBe(1)
    expect(result.skills[0]!.name).toBe('alpha-skill')
  })

  test('returns JSON-serializable output', async () => {
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ path: fixtureDir, json: true })
    expect(result.ok).toBe(true)
    const json = JSON.stringify(result.skills)
    const parsed = JSON.parse(json)
    expect(Array.isArray(parsed)).toBe(true)
    expect(parsed[0]).toHaveProperty('name')
    expect(parsed[0]).toHaveProperty('description')
  })

  test('returns empty array for directory with no valid skills', async () => {
    const emptyDir = await mkdtemp(join(tmpdir(), 'skill-list-empty-'))
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ path: emptyDir })
    expect(result.ok).toBe(true)
    expect(result.skills).toEqual([])
    await rm(emptyDir, { recursive: true, force: true })
  })

  test('returns error for non-existent scan directory', async () => {
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ path: '/tmp/definitely-does-not-exist-xyz' })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('scan_dir_not_found')
  })
})
```

#### Edge Cases

| Input / Scenario | Expected Behavior |
|---|---|
| Empty skills directory (no subdirs) | Return `{ ok: true, skills: [] }` |
| Broken symlinks in skill dirs | Skip the broken entry, do not crash |
| Skill dir exists but SKILL.md has no frontmatter | Skip silently (no entry in results) |
| Skill dir exists but SKILL.md has invalid frontmatter | Skip silently (no entry in results) |
| `--global` but no global skill directory configured | Return `{ ok: false, error: { code: 'global_dir_not_found' } }` |
| `--agent cursor` filter with no cursor-installed skills | Return `{ ok: true, skills: [] }` (empty, not error) |
| `--skill` filter matches nothing | Return `{ ok: true, skills: [] }` (empty, not error) |
| Dotdirs (`.hidden/`) in scan path | Skipped by `scanSkillDirs` filter |
| Non-directory entries (files, `justfile`) in scan path | Skipped by `isDirectory()` check |
| Scan path with 500+ skill dirs | Performance: sequential `readSkillFrontmatter` is fine (I/O bound, ~1ms each) |
| Skill dir is a symlink to another skill | Report `isSymlink: true`; resolve frontmatter from target |

#### Acceptance Criteria

- [ ] `listSkills()` returns `ListResult` for all code paths (never throws)
- [ ] Scan skips dotdirs, `.templates`, `justfile`, and non-directories
- [ ] Each skill's frontmatter is parsed via `readSkillFrontmatter` (shared validation)
- [ ] `--skill` filter is case-insensitive substring match
- [ ] `--agent` filter checks actual agent installation directories
- [ ] `--json` mode produces a JSON array of `InstalledSkill` objects
- [ ] Human mode uses `console-table-printer` via `lib/output.ts`
- [ ] Broken symlinks and invalid SKILL.md files are skipped without crashing
- [ ] `--global` scans global agent directories via `getAgentBaseDir(agent, true)`
- [ ] Replaces the existing `listSkills()` helper in `commands/skill.ts`

---

### 2.4 CLI Wiring

**Depends on:** 2.1, 2.2, 2.3

**Library decisions:** No new dependencies. Uses Citty `defineCommand` and `args` patterns already established in `commands/skill.ts`. Uses `globalArgs` from `commands/shared-args.ts` for `--json`, `--quiet`, `--verbose`.

- [ ] Add `skill add <source> [--agent] [--skill] [--copy] [--global] [--yes]` subcommand
- [ ] Add `skill init <name> [--description] [--template] [--path]` subcommand
- [ ] Add `skill list [path] [--agent] [--skill] [--json] [--global]` subcommand
- [ ] Ensure `mkdir -p cli/templates` in phase setup

#### Code Examples

```typescript
// Additions to cli/commands/skill.ts

import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'

// -- add subcommand ----------------------------------------------------------

const addCommand = defineCommand({
  meta: {
    name: 'add',
    description: 'Install skills from a source (repo, local path, or URL)',
  },
  args: {
    ...globalArgs,
    source: {
      type: 'positional',
      description: 'Source specifier (owner/repo, owner/repo@skill, ./local/path)',
      required: true,
    },
    agent: {
      type: 'string',
      description: 'Target agent (e.g. claude-code, cursor)',
    },
    skill: {
      type: 'string',
      description: 'Filter to a specific skill name within the source',
    },
    copy: {
      type: 'boolean',
      description: 'Copy files instead of symlinking',
      default: false,
    },
    global: {
      type: 'boolean',
      description: 'Install to global agent directory',
      default: false,
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip interactive prompts',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    const { addSkill } = await import('../lib/skill-add')

    const result = await addSkill(args.source as string, {
      agent: args.agent as any,
      skill: args.skill as string | undefined,
      copy: args.copy as boolean,
      global: args.global as boolean,
      yes: args.yes as boolean,
    })

    if (!result.ok) {
      out.error(result.error!.message, result.error)
      process.exit(EXIT.FAILURES)
    }

    for (const entry of result.installed) {
      out.success(`Installed ${entry.skill} -> ${entry.agent} (${entry.mode})`)
    }
    for (const w of result.warnings) {
      out.warn(w)
    }

    process.exit(EXIT.OK)
  },
})

// -- init subcommand ---------------------------------------------------------

const initCommand = defineCommand({
  meta: {
    name: 'init',
    description: 'Scaffold a new skill with SKILL.md from template',
  },
  args: {
    ...globalArgs,
    name: {
      type: 'positional',
      description: 'Skill name (lowercase kebab-case)',
      required: true,
    },
    description: {
      type: 'string',
      alias: 'd',
      description: 'Short description for the skill',
    },
    template: {
      type: 'string',
      alias: 't',
      description: 'Path to a custom SKILL.md template',
    },
    path: {
      type: 'string',
      alias: 'p',
      description: 'Target directory (default: context/skills/<name>/)',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    const { initSkill } = await import('../lib/skill-init')

    const result = await initSkill(args.name as string, {
      description: args.description as string | undefined,
      template: args.template as string | undefined,
      path: args.path as string | undefined,
    })

    if (!result.ok) {
      out.error(result.error!.message)
      process.exit(EXIT.FAILURES)
    }

    out.success(`Created ${result.skillPath}`)
    process.exit(EXIT.OK)
  },
})

// -- list subcommand ---------------------------------------------------------

const listCommand = defineCommand({
  meta: {
    name: 'list',
    description: 'Show installed skills with agent and plugin grouping',
  },
  args: {
    ...globalArgs,
    path: {
      type: 'positional',
      description: 'Skills directory to scan (default: context/skills/)',
      required: false,
    },
    agent: {
      type: 'string',
      description: 'Filter by agent name',
    },
    skill: {
      type: 'string',
      description: 'Filter by skill name',
    },
    global: {
      type: 'boolean',
      description: 'Scan global install directories',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    const { listSkills } = await import('../lib/skill-list')

    const result = await listSkills({
      path: args.path as string | undefined,
      agent: args.agent as string | undefined,
      skill: args.skill as string | undefined,
      global: args.global as boolean,
      json: args.json as boolean,
    })

    if (!result.ok) {
      out.error(result.error!.message)
      process.exit(EXIT.FAILURES)
    }

    if (args.json) {
      out.raw(result.skills)
    } else {
      if (result.skills.length === 0) {
        out.info('No skills found')
      } else {
        out.table(
          result.skills.map((s) => ({
            name: s.name,
            version: s.version ?? '-',
            agents: s.agents.join(', ') || '-',
            symlink: s.isSymlink ? 'yes' : 'no',
            tags: s.tags?.join(', ') ?? '-',
          })),
        )
      }
    }

    process.exit(EXIT.OK)
  },
})

// Then add to the parent command's subCommands:
// subCommands: { ..., add: addCommand, init: initCommand, list: listCommand }
```

#### Example Test Cases

```typescript
// CLI wiring tests can be added to cli/test/skill-commands.test.ts
// (extends existing file)

import { describe, expect, test } from 'bun:test'
import { spawnSync } from '../lib/runtime'

describe('skill CLI subcommands', () => {
  test('skill add --help shows usage', () => {
    const result = spawnSync(['bun', 'run', 'bin/agents.ts', 'skill', 'add', '--help'], {
      cwd: process.cwd(),
    })
    expect(result.stdout).toContain('source')
    expect(result.stdout).toContain('--agent')
    expect(result.stdout).toContain('--copy')
  })

  test('skill init --help shows usage', () => {
    const result = spawnSync(['bun', 'run', 'bin/agents.ts', 'skill', 'init', '--help'], {
      cwd: process.cwd(),
    })
    expect(result.stdout).toContain('name')
    expect(result.stdout).toContain('--description')
    expect(result.stdout).toContain('--template')
  })

  test('skill list --help shows usage', () => {
    const result = spawnSync(['bun', 'run', 'bin/agents.ts', 'skill', 'list', '--help'], {
      cwd: process.cwd(),
    })
    expect(result.stdout).toContain('--agent')
    expect(result.stdout).toContain('--skill')
    expect(result.stdout).toContain('--json')
    expect(result.stdout).toContain('--global')
  })

  test('skill list --json returns valid JSON array', () => {
    const result = spawnSync(
      ['bun', 'run', 'bin/agents.ts', 'skill', 'list', '--json'],
      { cwd: process.cwd() },
    )
    expect(result.exitCode).toBe(0)
    const parsed = JSON.parse(result.stdout)
    expect(Array.isArray(parsed)).toBe(true)
  })
})
```

#### Edge Cases

| Input / Scenario | Expected Behavior |
|---|---|
| `skill add` with no source argument | Citty prints usage/help text and exits non-zero |
| `skill init` with no name argument | Citty prints usage/help text and exits non-zero |
| `skill list` with no arguments | Scans default `context/skills/` directory |
| `skill list /nonexistent/path` | Prints error and exits with code 1 |
| `--json` and `--quiet` combined on list | JSON output takes precedence, quiet is no-op |
| `--json` on add/init | Structured JSON output instead of human messages |
| Very long source string (>500 chars) | Passed through to `parseSource`; it validates |

#### Acceptance Criteria

- [ ] All three subcommands register correctly in the `skill` parent command
- [ ] `--help` works for `add`, `init`, and `list` individually
- [ ] `globalArgs` (json, quiet, verbose) are inherited by all subcommands
- [ ] `--json` produces structured output for all three commands
- [ ] Exit codes follow `EXIT.OK` (0) / `EXIT.FAILURES` (1) / `EXIT.ERROR` (2) convention
- [ ] Error messages use `createOutput` (never raw `console.log` in command handlers)
- [ ] `cli/templates/` directory is created as part of phase setup
- [ ] Existing subcommands (`validate`, `hash`, `lint`, `check-all`, `deps`) are not affected

## Notes

- `add` is the largest command; keep orchestration in `skill-add.ts`, filesystem ops in existing `symlink.ts` + `runtime.ts`
- `list` replaces the existing `listSkills()` helper in `commands/skill.ts` -- move that logic to `lib/skill-list.ts`
- The init template should be customizable per-project (check for local template first)
- All commands respect `--yes` for CI/non-interactive usage
- `addSkill` writes to lock files only -- it does NOT touch `sources.yaml` (the external deps manifest managed by `skill deps`)
