# Phase 5: Integration (remove, info, refactor, tests, docs)

**ID:** `phase-5`
**Dependencies:** phase-2, phase-3, phase-4
**Status:** pending
**Effort:** TBD

## Objective

Implement remaining commands (`remove`, `info`), refactor existing code to use new modules, write integration tests, and document everything. Note: filter utilities (`--agent`/`--skill`) were moved to phase 2; this phase uses them but does not define them. Task 5.3 (refactor) can start after phase-1 completes since it only needs `lib/git.ts`.

## Success Criteria

- [ ] `skill remove` command works (agent-aware removal with lock cleanup)
- [ ] `skill info <name>` shows detailed metadata for a single installed skill
- [ ] Existing `skill deps sync` uses new `lib/git.ts` instead of inline spawnSync
- [ ] Existing `skill catalog analyze` can use new `addSkill` instead of raw `npx skills add`
- [ ] `--agent`/`--skill` filters (from phase 2) wired into `outdated`, `update`, `remove`, `info`
- [ ] All commands documented in `--help` output
- [ ] Integration tests cover add -> list -> outdated -> update -> remove lifecycle

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Remove command logic | `.scripts/lib/skill-remove.ts` | TypeScript |
| Info command logic | `.scripts/lib/skill-info.ts` | TypeScript |
| Integration tests | `.scripts/test/skill-integration.test.ts` | bun:test |
| CLI help/docs updates | `.scripts/commands/skill.ts` | TypeScript |
| Refactored external-skills | `.scripts/lib/external-skills.ts` | TypeScript (modifications) |

## Files

**Create:**
- `.scripts/lib/skill-remove.ts`
- `.scripts/lib/skill-info.ts`
- `.scripts/test/skill-integration.test.ts`

**Modify:**
- `.scripts/commands/skill.ts` (add `remove`, `info` subcommands, add filters to all commands)
- `.scripts/lib/external-skills.ts` (replace inline git calls with `lib/git.ts`)
- `.scripts/lib/catalog.ts` (optionally use `addSkill` instead of `npx skills add`)

## Error Types

```typescript
// In lib/skill-remove.ts
export class RemoveError extends CliError {
  constructor(
    message: string,
    code:
      | 'E_SKILL_NOT_FOUND'
      | 'E_LOCK_UPDATE_FAILED'
      | 'E_FS_REMOVE_FAILED'
      | 'E_BROKEN_SYMLINK'
      | 'E_AGENT_NOT_FOUND',
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}

// In lib/skill-info.ts
export class InfoError extends CliError {
  constructor(
    message: string,
    code:
      | 'E_SKILL_NOT_FOUND'
      | 'E_LOCK_READ_FAILED'
      | 'E_FRONTMATTER_INVALID'
      | 'E_DISK_MISMATCH',
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}
```

## Tasks

### 5.1 Remove Command (`lib/skill-remove.ts`)

**Task Dependencies:** phase-1 (`lib/agents.ts` for agent registry paths, `lib/git.ts` not needed), phase-2 (`lib/skill-list.ts` for enumerating installed skills, `lib/skill-add.ts` for understanding canonical dir layout)

**Library Decisions:** No new deps. Uses `lib/lockfile.ts` (read/write lock), `lib/symlink.ts` (`checkSymlink` for detection, `rm` for removal), `lib/agents.ts` (agent path resolution), `lib/output.ts` (formatted output), `lib/prompts/` (interactive multiselect when no names given).

- [ ] Export `removeSkills(names: string[], opts: RemoveOptions): Promise<void>`
- [ ] If no names: interactive multiselect from installed skills
- [ ] For each skill x agent: remove the agent-specific dir/symlink
- [ ] If no agents still reference canonical: remove canonical dir
- [ ] Update global and local lock files
- [ ] Support `--agent` filter (remove only from specific agent)

#### Code Examples

```typescript
// .scripts/lib/skill-remove.ts

import { rm } from 'node:fs/promises'
import { join } from 'node:path'
import { CliError, ok, err, type Result } from './types'
import type { AgentType } from './agents'
import { agents, getAgentBaseDir } from './agents'
import { readLockfile, writeLockfile, type LockfileV1 } from './lockfile'
import { checkSymlink } from './symlink'
import { createOutput, type OutputFormatter } from './output'

export class RemoveError extends CliError {
  constructor(
    message: string,
    code:
      | 'E_SKILL_NOT_FOUND'
      | 'E_LOCK_UPDATE_FAILED'
      | 'E_FS_REMOVE_FAILED'
      | 'E_BROKEN_SYMLINK'
      | 'E_AGENT_NOT_FOUND',
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}

export interface RemoveOptions {
  agent?: string       // Remove only from this agent
  yes?: boolean        // Skip confirmation prompts
  json?: boolean       // Structured output
  quiet?: boolean      // Suppress non-essential output
  global?: boolean     // Remove from global skills dir
  cwd?: string         // Working directory override
}

export interface RemoveResult {
  skill: string
  removedFrom: AgentType[]
  canonicalRemoved: boolean
  lockUpdated: boolean
  error?: string
}

/**
 * Remove one or more skills from agent directories and update lock files.
 *
 * For each skill:
 * 1. Determine target agents (all installed, or filtered by --agent)
 * 2. Remove the agent-specific dir/symlink for each target agent
 * 3. If no agents still reference the canonical dir, remove it
 * 4. Update the lock file to remove the entry
 */
export async function removeSkills(
  names: string[],
  opts: RemoveOptions,
): Promise<RemoveResult[]> {
  // ... implementation
}

/**
 * Remove a single skill's presence from one agent directory.
 * Handles both symlinks and copied directories.
 */
async function removeFromAgent(
  skillName: string,
  agentType: AgentType,
  opts: { global?: boolean; cwd?: string },
): Promise<Result<void>> {
  const baseDir = getAgentBaseDir(agentType, opts.global ?? false, opts.cwd)
  const skillPath = join(baseDir, 'skills', skillName)

  try {
    // Check if it's a symlink or a real directory
    const status = await checkSymlink(skillPath).catch(() => null)
    if (status) {
      // It's a symlink -- just remove the link
      await rm(skillPath)
    } else {
      // It's a copied directory -- remove recursively
      await rm(skillPath, { recursive: true, force: true })
    }
    return ok(undefined)
  } catch (cause) {
    return err(
      new RemoveError(
        `Failed to remove ${skillName} from ${agentType}`,
        'E_FS_REMOVE_FAILED',
        `Path: ${skillPath}`,
        cause,
      ),
    )
  }
}
```

#### Example Test Cases

```typescript
// .scripts/test/skill-remove.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

describe('removeSkills', () => {
  let tmp: string

  beforeEach(async () => {
    tmp = await mkdtemp(join(tmpdir(), 'skill-remove-test-'))
  })

  afterEach(async () => {
    await rm(tmp, { recursive: true, force: true })
  })

  test('removes skill from all agents when no --agent filter', async () => {
    // Setup: canonical dir + symlinks for two agents
    const canonical = join(tmp, 'context', 'skills', 'beads')
    const agent1 = join(tmp, '.claude', 'skills', 'beads')
    const agent2 = join(tmp, '.cursor', 'skills', 'beads')
    await mkdir(canonical, { recursive: true })
    await writeFile(join(canonical, 'SKILL.md'), '---\nname: beads\n---')
    await mkdir(join(tmp, '.claude', 'skills'), { recursive: true })
    await mkdir(join(tmp, '.cursor', 'skills'), { recursive: true })
    await symlink(canonical, agent1)
    await symlink(canonical, agent2)

    // Act: removeSkills(['beads'], { cwd: tmp })
    // Assert: all three paths removed
    expect(existsSync(agent1)).toBe(false)
    expect(existsSync(agent2)).toBe(false)
    expect(existsSync(canonical)).toBe(false)
  })

  test('removes from single agent with --agent filter, keeps canonical', async () => {
    // Setup: canonical dir + symlinks for two agents
    const canonical = join(tmp, 'context', 'skills', 'beads')
    const agent1 = join(tmp, '.claude', 'skills', 'beads')
    const agent2 = join(tmp, '.cursor', 'skills', 'beads')
    await mkdir(canonical, { recursive: true })
    await writeFile(join(canonical, 'SKILL.md'), '---\nname: beads\n---')
    await mkdir(join(tmp, '.claude', 'skills'), { recursive: true })
    await mkdir(join(tmp, '.cursor', 'skills'), { recursive: true })
    await symlink(canonical, agent1)
    await symlink(canonical, agent2)

    // Act: removeSkills(['beads'], { agent: 'claude-code', cwd: tmp })
    // Assert: agent1 removed, agent2 + canonical still exist
    expect(existsSync(agent1)).toBe(false)
    expect(existsSync(agent2)).toBe(true)
    expect(existsSync(canonical)).toBe(true)
  })

  test('removes canonical when no agents remain referencing it', async () => {
    // Setup: canonical dir + one agent symlink
    const canonical = join(tmp, 'context', 'skills', 'solo-skill')
    const agent1 = join(tmp, '.claude', 'skills', 'solo-skill')
    await mkdir(canonical, { recursive: true })
    await writeFile(join(canonical, 'SKILL.md'), '---\nname: solo-skill\n---')
    await mkdir(join(tmp, '.claude', 'skills'), { recursive: true })
    await symlink(canonical, agent1)

    // Act: removeSkills(['solo-skill'], { agent: 'claude-code', cwd: tmp })
    // Assert: both agent link and canonical removed (last reference)
    expect(existsSync(agent1)).toBe(false)
    expect(existsSync(canonical)).toBe(false)
  })

  test('handles skill not found gracefully', async () => {
    // Act: removeSkills(['nonexistent'], { cwd: tmp })
    // Assert: returns RemoveResult with error, does not throw
  })

  test('handles broken symlink during removal', async () => {
    // Setup: symlink pointing to deleted target
    const agent1 = join(tmp, '.claude', 'skills', 'ghost')
    await mkdir(join(tmp, '.claude', 'skills'), { recursive: true })
    await symlink('/nonexistent/path', agent1)

    // Act: removeSkills(['ghost'], { cwd: tmp })
    // Assert: broken symlink removed, no error thrown
    expect(existsSync(agent1)).toBe(false)
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Skill installed as symlink | Remove the symlink only, check if canonical should be cleaned |
| Skill installed as copy | Remove the entire copied directory recursively |
| Canonical dir shared by multiple agents | Only remove canonical when **zero** agents still reference it |
| Skill not found in any agent dir | Return `RemoveResult` with `E_SKILL_NOT_FOUND`, no crash |
| Broken symlink during removal | Remove the broken symlink file itself; log a warning |
| Permission denied on removal | Return `E_FS_REMOVE_FAILED` with cause, continue to next skill |
| Lock file write fails after FS removal | Return `E_LOCK_UPDATE_FAILED`; FS removal is already done (non-transactional) |

#### Acceptance Criteria

- [ ] `removeSkills()` exported from `lib/skill-remove.ts`
- [ ] Interactive multiselect when no skill names provided (respects `--yes`)
- [ ] `--agent` filter removes from one agent only and preserves canonical when other agents still reference it
- [ ] Lock file entries removed for fully-removed skills
- [ ] Lock file entries updated (agent list trimmed) for partially-removed skills
- [ ] Handles both symlink and copy installations
- [ ] Returns structured `RemoveResult[]` for JSON output
- [ ] At least 5 test cases covering the edge cases above

---

### 5.2 Info Command (`lib/skill-info.ts`)

**Task Dependencies:** phase-2 (`lib/skill-list.ts` for `listSkills()` which provides the enumeration that `info` builds upon), phase-1 (`lib/agents.ts` for agent names, `lib/source-parser.ts` for source display)

**Library Decisions:** No new deps. Uses `lib/manifest.ts` (`readSkillFrontmatter()`), `lib/lockfile.ts` (`readLockfile()`), `lib/symlink.ts` (`checkSymlink()`, `resolveChain()`), `lib/hash.ts` (`computeHash()`), `lib/output.ts` (`createOutput()`).

- [ ] Export `skillInfo(name: string, opts: InfoOptions): Promise<SkillDetail>`
- [ ] Show: frontmatter metadata, source (from lock), content hash, installed agents, symlink status, lock entry
- [ ] Support `--json` output
- [ ] Complements `list` (which shows all skills briefly) with deep detail on one skill

#### Code Examples

```typescript
// .scripts/lib/skill-info.ts

import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { CliError, ok, err, type Result } from './types'
import type { AgentType } from './agents'
import { agents, detectInstalledAgents, getAgentBaseDir } from './agents'
import { readSkillFrontmatter } from './manifest'
import type { SkillFrontmatter } from './schemas'
import { readLockfile } from './lockfile'
import type { LockfileV1 } from './schemas'
import { checkSymlink, resolveChain } from './symlink'
import { computeHash } from './hash'
import { createOutput, type OutputFormatter } from './output'

export class InfoError extends CliError {
  constructor(
    message: string,
    code:
      | 'E_SKILL_NOT_FOUND'
      | 'E_LOCK_READ_FAILED'
      | 'E_FRONTMATTER_INVALID'
      | 'E_DISK_MISMATCH',
    hint?: string,
    cause?: unknown,
  ) {
    super(message, code, hint, cause)
  }
}

export interface InfoOptions {
  json?: boolean
  quiet?: boolean
  global?: boolean
  cwd?: string
}

export interface SkillDetail {
  name: string
  path: string
  frontmatter: SkillFrontmatter | null
  source: string | null          // from lock entry
  sourceType: string | null      // from lock entry
  computedHash: string | null    // live hash from disk
  lockHash: string | null        // hash stored in lock
  hashMatch: boolean             // computedHash === lockHash
  installedAgents: AgentType[]   // which agents have this skill
  symlinkStatus: 'symlink' | 'copy' | 'missing'
  symlinkTarget: string | null   // resolved symlink target if applicable
  lockEntry: Record<string, unknown> | null
}

/**
 * Get detailed metadata for a single installed skill.
 *
 * Reads frontmatter from SKILL.md, cross-references the lock file,
 * checks symlink health for each agent, and computes a live content hash.
 */
export async function skillInfo(
  name: string,
  opts: InfoOptions,
): Promise<Result<SkillDetail>> {
  const cwd = opts.cwd ?? process.cwd()
  const skillPath = join(cwd, 'context', 'skills', name)

  if (!existsSync(skillPath)) {
    return err(
      new InfoError(
        `Skill "${name}" not found on disk`,
        'E_SKILL_NOT_FOUND',
        `Expected at: ${skillPath}`,
      ),
    )
  }

  // Read frontmatter
  const skillMdPath = join(skillPath, 'SKILL.md')
  const fmResult = await readSkillFrontmatter(skillMdPath)
  const frontmatter = fmResult.ok ? fmResult.value : null

  // Read lock entry
  const lockPath = join(cwd, 'skills-lock.json')
  const lockResult = await readLockfile<LockfileV1>('skills', lockPath)
  const lockData = lockResult.ok ? lockResult.value : null
  const lockEntry = lockData?.skills?.[name] ?? null

  // Compute live hash
  const computedHash = await computeHash(skillPath).catch(() => null)

  // Check which agents have this skill installed
  const installed = await detectInstalledAgents()
  const installedAgents: AgentType[] = []
  for (const agent of installed) {
    const agentSkillPath = join(
      getAgentBaseDir(agent, opts.global ?? false, cwd),
      'skills',
      name,
    )
    if (existsSync(agentSkillPath)) {
      installedAgents.push(agent)
    }
  }

  // Check symlink status
  let symlinkStatus: 'symlink' | 'copy' | 'missing' = 'missing'
  let symlinkTarget: string | null = null
  try {
    const status = await checkSymlink(skillPath)
    symlinkStatus = 'symlink'
    symlinkTarget = status.target
  } catch {
    if (existsSync(skillPath)) {
      symlinkStatus = 'copy'
    }
  }

  return ok({
    name,
    path: skillPath,
    frontmatter,
    source: lockEntry?.source ?? null,
    sourceType: lockEntry?.sourceType ?? null,
    computedHash,
    lockHash: lockEntry?.computedHash ?? null,
    hashMatch: computedHash != null && computedHash === lockEntry?.computedHash,
    installedAgents,
    symlinkStatus,
    symlinkTarget,
    lockEntry: lockEntry as Record<string, unknown> | null,
  })
}
```

```typescript
// CLI wiring in commands/skill.ts
const infoCommand = defineCommand({
  meta: { name: 'info', description: 'Show detailed metadata for an installed skill' },
  args: {
    ...globalArgs,
    name: { type: 'positional', description: 'Skill name', required: true },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const result = await skillInfo(args.name, {
      json: args.json,
      quiet: args.quiet,
    })
    if (!result.ok) {
      out.error(result.error.display())
      process.exit(2)
    }
    if (args.json) {
      out.raw(result.value)
    } else {
      out.info(`Skill: ${result.value.name}`)
      out.info(`Path: ${result.value.path}`)
      out.info(`Source: ${result.value.source ?? 'unknown'}`)
      out.info(`Hash match: ${result.value.hashMatch ? 'yes' : 'NO (drift detected)'}`)
      out.info(`Agents: ${result.value.installedAgents.join(', ') || 'none'}`)
      out.info(`Install mode: ${result.value.symlinkStatus}`)
    }
  },
})
```

#### Example Test Cases

```typescript
// .scripts/test/skill-info.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

describe('skillInfo', () => {
  let tmp: string

  beforeEach(async () => {
    tmp = await mkdtemp(join(tmpdir(), 'skill-info-test-'))
  })

  afterEach(async () => {
    await rm(tmp, { recursive: true, force: true })
  })

  test('shows full metadata for an installed skill', async () => {
    // Setup: create a skill dir with SKILL.md and a lock entry
    const skillDir = join(tmp, 'context', 'skills', 'beads')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: beads\ndescription: Issue tracker\n---\n# Beads',
    )
    // Write a lock file
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          beads: {
            source: 'steveyegge/beads',
            sourceType: 'github',
            computedHash: 'a'.repeat(64),
          },
        },
      }),
    )

    // Act
    const result = await skillInfo('beads', { cwd: tmp })

    // Assert
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('beads')
      expect(result.value.frontmatter).toBeDefined()
      expect(result.value.source).toBe('steveyegge/beads')
      expect(result.value.symlinkStatus).toBe('copy')
    }
  })

  test('returns JSON-serializable output with --json', async () => {
    const skillDir = join(tmp, 'context', 'skills', 'test-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: test-skill\n---\n# Test',
    )

    const result = await skillInfo('test-skill', { json: true, cwd: tmp })

    expect(result.ok).toBe(true)
    if (result.ok) {
      // Verify the result is JSON-serializable (no circular refs, no functions)
      const serialized = JSON.stringify(result.value)
      const parsed = JSON.parse(serialized)
      expect(parsed.name).toBe('test-skill')
    }
  })

  test('returns error for skill not found', async () => {
    const result = await skillInfo('nonexistent', { cwd: tmp })

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
    }
  })

  test('detects hash mismatch between disk and lock', async () => {
    const skillDir = join(tmp, 'context', 'skills', 'drifted')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: drifted\n---\n# Changed')
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          drifted: {
            source: 'local',
            sourceType: 'local',
            computedHash: 'b'.repeat(64), // stale hash
          },
        },
      }),
    )

    const result = await skillInfo('drifted', { cwd: tmp })

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.hashMatch).toBe(false)
    }
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Skill exists on disk but not in lock | Return detail with `source: null`, `lockEntry: null`, `hashMatch: false` |
| Skill in lock but deleted from disk | Return `E_SKILL_NOT_FOUND` (disk is source of truth for `info`) |
| SKILL.md exists but has no/invalid frontmatter | Return detail with `frontmatter: null`, log warning |
| Skill is a symlink to a deleted target | Return detail with `symlinkStatus: 'symlink'`, `symlinkTarget` set, broken flag in output |
| Lock file itself is missing or invalid | Return detail with all lock-derived fields as `null` |

#### Acceptance Criteria

- [ ] `skillInfo()` exported from `lib/skill-info.ts`
- [ ] Returns `SkillDetail` with frontmatter, lock entry, hash, agent list, and symlink status
- [ ] `--json` output produces valid JSON matching the `SkillDetail` interface
- [ ] Gracefully handles missing lock file, missing frontmatter, and missing skill
- [ ] Human-readable output shows all fields with clear labels
- [ ] At least 4 test cases covering happy path, not found, JSON mode, and hash mismatch

---

### 5.3 Refactor Existing Code

**Task Dependencies:** phase-1 (`lib/git.ts` provides `lsRemote()` and `cloneRepo()` to replace inline git calls, `lib/skill-discovery.ts` for consistent SKILL.md scanning). The git refactor (replacing inline spawnSync) can start immediately after phase 1 — it does not need phases 2-4. The optional `addSkill` replacement in `catalog.ts` needs phase-2.

**Library Decisions:** No new deps. This task replaces inline code with existing modules created in phases 1-2. The key risk is that `lib/git.ts` may use different error types than the inline `spawnSync` calls in `external-skills.ts`.

- [ ] Replace `spawnSync(['git', 'ls-remote', ...])` in `external-skills.ts` with `lsRemote()` from `lib/git.ts`
- [ ] Replace `spawnSync(['git', 'clone', ...])` in `external-skills.ts` with `cloneRepo()` from `lib/git.ts`
- [ ] Evaluate replacing `npx skills add` calls in `catalog.ts` with `addSkill()` from `skill-add.ts`
- [ ] Ensure `skill deps sync` and `skill add` share the same installation codepath
- [ ] Wire `skill-discovery.ts` into `skill deps sync` for consistent SKILL.md scanning

#### Code Examples

```typescript
// Before (external-skills.ts line ~154-198):
export async function gitLsRemote(repoUrl: string, ref?: string): Promise<Result<string>> {
  const args = ref
    ? ['git', 'ls-remote', '--tags', repoUrl, ref]
    : ['git', 'ls-remote', repoUrl, 'HEAD']
  const proc = spawnSync(args)
  // ... manual error handling
}

// After (external-skills.ts, using lib/git.ts):
import { lsRemote } from './git'

export async function gitLsRemote(repoUrl: string, ref?: string): Promise<Result<string>> {
  // Delegate to the shared git wrapper; adapt error types for backward compat
  const result = await lsRemote(repoUrl, ref)
  if (!result.ok) {
    // Map GitCloneError to the CliError format external-skills.ts callers expect
    return err(
      new CliError(
        result.error.message,
        'E_GIT_LS_REMOTE',
        result.error.hint,
        result.error.cause,
      ),
    )
  }
  return result
}
```

```typescript
// Before (external-skills.ts line ~280-401, syncSkill):
const proc = spawnSync([
  'git', 'clone', '--depth', '1', '--branch', entry.ref,
  repoUrl, `${tempBase}/repo`,
])

// After:
import { cloneRepo } from './git'

const cloneResult = await cloneRepo(repoUrl, entry.ref)
if (!cloneResult.ok) {
  return err(
    new CliError(
      `Failed to clone ${entry.source}`,
      'E_CLONE_FAILED',
      cloneResult.error.message,
    ),
  )
}
const repoDir = cloneResult.value.tempDir
// ... use repoDir instead of `${tempBase}/repo`
// ... in finally block: await cloneResult.value.cleanup()
```

```typescript
// Before (external-skills.ts syncSkill, npx fallback ~326-354):
const proc = spawnSync(
  ['npx', 'skills', 'add', '-y', '--copy', '--full-depth',
   `${entry.source}@${entry.skill}`],
  { cwd: npxDir }
)

// After (using addSkill from lib/skill-add.ts):
import { addSkill } from './skill-add'

const addResult = await addSkill(`${entry.source}@${entry.skill}`, {
  copy: true,
  yes: true,
  // Note: addSkill writes to its own lock files -- may need a 'skipLock' option
  // or a dedicated internal install function
})
```

#### Example Test Cases

```typescript
// .scripts/test/external-skills-refactor.test.ts
import { describe, expect, test, mock } from 'bun:test'

describe('gitLsRemote after refactor', () => {
  test('returns SHA using lib/git.ts lsRemote', async () => {
    // Mock lsRemote to return a known SHA
    // Verify gitLsRemote delegates correctly and maps the result
  })

  test('maps GitCloneError to E_GIT_LS_REMOTE code', async () => {
    // Mock lsRemote to return an error
    // Verify the error code is E_GIT_LS_REMOTE (backward compat)
  })

  test('syncSkill uses cloneRepo instead of inline spawnSync', async () => {
    // Mock cloneRepo to return a tempDir
    // Verify syncSkill calls cleanup() in finally block
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `external-skills.ts` sync uses old git path but new `lib/git.ts` has different error types | Map `GitCloneError` to existing `CliError` codes (`E_GIT_LS_REMOTE`, `E_CLONE_FAILED`) for backward compatibility |
| `cloneRepo` cleanup not called on early return | Use `try/finally` to guarantee `cleanup()` runs |
| `addSkill()` writes lock entries that conflict with `external-skills.ts` lock format | Keep `npx skills add` replacement **optional** (evaluate flag in task); if adopted, ensure lock format alignment |
| `spawnSync` vs `spawnAsync` — `cloneRepo` is async but `syncSkill` previously used sync | `syncSkill` is already `async`; no change needed in callers |
| `skill deps sync` and `skill add` produce different directory layouts | Wire `skill-discovery.ts` into both paths to normalize post-clone discovery |

#### Acceptance Criteria

- [ ] Zero direct `spawnSync(['git', ...])` calls remain in `external-skills.ts`
- [ ] All existing `skill deps check` and `skill deps sync` tests still pass after refactor
- [ ] `gitLsRemote()` is a thin wrapper around `lsRemote()` with error code mapping
- [ ] `syncSkill()` uses `cloneRepo()` with proper cleanup in `finally` block
- [ ] Decision documented (in code comment) on whether to replace `npx skills add` in `catalog.ts`
- [ ] `skill-discovery.ts` used in `skill deps sync` for SKILL.md scanning

---

### 5.4 Integration Tests

**Task Dependencies:** phase-2 (`lib/skill-add.ts`, `lib/skill-list.ts`, `lib/skill-filters.ts`), phase-4 (`lib/skill-outdated.ts`, `lib/skill-update.ts`), task 5.1 (`lib/skill-remove.ts`), task 5.2 (`lib/skill-info.ts`)

**Library Decisions:** No new deps. Tests use `bun:test`, `node:fs/promises` for temp dir setup, and import all skill-* modules under test.

- [ ] Full lifecycle test: add -> list -> outdated -> update -> remove
- [ ] Multi-agent test: add to claude-code + cursor, verify symlinks, remove from one
- [ ] Ref support test: add with `#branch`, verify correct checkout
- [ ] Copy vs symlink test: verify both modes produce correct filesystem state
- [ ] JSON output test: all commands with `--json` produce valid JSON
- [ ] Info test: `skill info <name>` returns correct metadata

#### Code Examples

```typescript
// .scripts/test/skill-integration.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, rm, writeFile, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { addSkill } from '../lib/skill-add'
import { listSkills } from '../lib/skill-list'
import { checkOutdated } from '../lib/skill-outdated'
import { updateSkills } from '../lib/skill-update'
import { removeSkills } from '../lib/skill-remove'
import { skillInfo } from '../lib/skill-info'

describe('skill lifecycle integration', () => {
  let tmp: string

  beforeEach(async () => {
    tmp = await mkdtemp(join(tmpdir(), 'skill-integration-'))
    // Setup minimal project structure
    await mkdir(join(tmp, 'context', 'skills'), { recursive: true })
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({ version: 1, skills: {} }),
    )
  })

  afterEach(async () => {
    await rm(tmp, { recursive: true, force: true })
  })

  test('full lifecycle: add -> list -> info -> remove', async () => {
    // 1. Add a local skill
    const localSkill = join(tmp, 'source-skill')
    await mkdir(localSkill, { recursive: true })
    await writeFile(
      join(localSkill, 'SKILL.md'),
      '---\nname: test-skill\ndescription: A test\n---\n# Test Skill\n',
    )

    await addSkill(localSkill, { cwd: tmp, copy: true, yes: true })

    // 2. List and verify it appears
    const listed = await listSkills({ cwd: tmp })
    expect(listed.some((s) => s.name === 'test-skill')).toBe(true)

    // 3. Info shows correct metadata
    const info = await skillInfo('test-skill', { cwd: tmp })
    expect(info.ok).toBe(true)
    if (info.ok) {
      expect(info.value.symlinkStatus).toBe('copy')
    }

    // 4. Remove
    const results = await removeSkills(['test-skill'], { cwd: tmp, yes: true })
    expect(results[0].canonicalRemoved).toBe(true)

    // 5. Verify gone
    const afterRemove = await listSkills({ cwd: tmp })
    expect(afterRemove.some((s) => s.name === 'test-skill')).toBe(false)
  })

  test('add then immediate remove (no update)', async () => {
    // Verify the lock file is clean after add+remove cycle
    const localSkill = join(tmp, 'ephemeral-skill')
    await mkdir(localSkill, { recursive: true })
    await writeFile(join(localSkill, 'SKILL.md'), '---\nname: ephemeral\n---\n')

    await addSkill(localSkill, { cwd: tmp, copy: true, yes: true })
    await removeSkills(['ephemeral'], { cwd: tmp, yes: true })

    const lockRaw = await readFile(join(tmp, 'skills-lock.json'), 'utf-8')
    const lock = JSON.parse(lockRaw)
    expect(lock.skills).not.toHaveProperty('ephemeral')
  })

  test('add same skill twice is idempotent', async () => {
    const localSkill = join(tmp, 'idempotent-skill')
    await mkdir(localSkill, { recursive: true })
    await writeFile(join(localSkill, 'SKILL.md'), '---\nname: idem\n---\n')

    await addSkill(localSkill, { cwd: tmp, copy: true, yes: true })
    await addSkill(localSkill, { cwd: tmp, copy: true, yes: true })

    const listed = await listSkills({ cwd: tmp })
    const matches = listed.filter((s) => s.name === 'idem')
    expect(matches).toHaveLength(1) // not duplicated
  })
})
```

#### Example Test Cases

```typescript
describe('multi-agent integration', () => {
  test('add to one agent then add to another accumulates', async () => {
    // Setup: local skill
    // Act: addSkill with agent: 'claude-code', then addSkill with agent: 'cursor'
    // Assert: skill appears in both agent dirs; info shows both in installedAgents
  })

  test('remove from one agent preserves other agent installation', async () => {
    // Setup: skill installed in two agents
    // Act: removeSkills with agent: 'claude-code'
    // Assert: cursor still has it; info.installedAgents = ['cursor']
  })

  test('all commands with --json produce valid parseable JSON', async () => {
    // For each command output captured via a mock OutputFormatter:
    // Assert: JSON.parse(output) does not throw
    // Assert: output has expected top-level keys
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Add then immediate remove (no update in between) | Lock file has no orphaned entry |
| Add same skill twice (idempotent?) | Second add overwrites in-place; no duplicate entries |
| Add to one agent then add to another (accumulate?) | Skill appears in both agent dirs; lock entry tracks both |
| Remove all skills (empty state) | Lock file has `{ "version": 1, "skills": {} }` |
| Integration test temp dir cleanup on test failure | `afterEach` with `force: true` removes even if test throws |

#### Acceptance Criteria

- [ ] Full lifecycle test passes: add -> list -> outdated -> update -> remove
- [ ] Multi-agent test passes: install to two agents, remove from one, verify
- [ ] Copy vs symlink test verifies correct filesystem state for each mode
- [ ] JSON output test validates all commands produce parseable JSON
- [ ] All integration tests use temp directories (no pollution of real `context/skills/`)
- [ ] Tests are in `.scripts/test/skill-integration.test.ts`
- [ ] At least 6 test scenarios covering the lifecycle and edge cases

---

### 5.5 Documentation

**Task Dependencies:** tasks 5.1-5.4 (all features must be implemented before documenting), phase-2 and phase-4 (CLI wiring for all subcommands)

**Library Decisions:** No new deps. Documentation is in Citty `meta.description` fields and CLAUDE.md markdown.

- [ ] All new subcommands have `description` in Citty command definition
- [ ] Add skill management section to CLAUDE.md common tasks table
- [ ] Update justfile if new `just` recipes are needed

#### Code Examples

```typescript
// Citty command descriptions in commands/skill.ts

const removeCommand = defineCommand({
  meta: {
    name: 'remove',
    description: 'Remove installed skills from agent directories and clean up lock files',
  },
  args: {
    ...globalArgs,
    ...filterArgs,
    names: {
      type: 'positional',
      description: 'Skill names to remove (interactive if omitted)',
      required: false,
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip confirmation prompts',
      default: false,
    },
  },
  async run({ args }) { /* ... */ },
})

const infoCommand = defineCommand({
  meta: {
    name: 'info',
    description: 'Show detailed metadata for a single installed skill',
  },
  args: {
    ...globalArgs,
    name: {
      type: 'positional',
      description: 'Skill name to inspect',
      required: true,
    },
  },
  async run({ args }) { /* ... */ },
})
```

```markdown
<!-- Addition to CLAUDE.md Common Tasks table -->

| Task | Command |
|------|---------|
| Add a skill | `just agents skill add owner/repo@skill` |
| List installed skills | `just agents skill list` |
| List skills for one agent | `just agents skill list --agent claude-code` |
| Check for updates | `just agents skill outdated` |
| Update all skills | `just agents skill update` |
| Remove a skill | `just agents skill remove skill-name` |
| Skill details | `just agents skill info skill-name` |
| Find remote skills | `just agents skill find "search query"` |
```

#### Example Test Cases

```typescript
// .scripts/test/skill-commands.test.ts (additions)
import { describe, expect, test } from 'bun:test'

describe('CLI help output', () => {
  test('skill remove has description in --help', async () => {
    // Verify the Citty command has meta.description set
    // This can be tested by importing the command definition
    // and checking meta.description is non-empty
    expect(removeCommand.meta?.description).toBeTruthy()
    expect(removeCommand.meta?.description).toContain('Remove')
  })

  test('skill info has description in --help', async () => {
    expect(infoCommand.meta?.description).toBeTruthy()
    expect(infoCommand.meta?.description).toContain('metadata')
  })

  test('all skill subcommands have non-empty descriptions', async () => {
    // Import the parent skill command and iterate subcommands
    // Assert: every subcommand has meta.description defined
  })
})
```

#### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| User runs `just agents skill` with no subcommand | Shows help listing all subcommands with descriptions |
| User runs `just agents skill remove --help` | Shows remove-specific args including `--agent` filter |
| CLAUDE.md table formatting breaks with long command | Keep command column under 60 chars; use backtick code spans |

#### Acceptance Criteria

- [ ] Every new subcommand (`add`, `find`, `outdated`, `update`, `remove`, `info`) has a non-empty `meta.description`
- [ ] `--agent` and `--skill` filter flags have descriptions in all applicable subcommands
- [ ] CLAUDE.md common tasks table updated with at least 7 new skill management entries
- [ ] Justfile updated with any new convenience recipes (e.g., `just skill-info <name>`)
- [ ] `just agents skill --help` shows a complete list of subcommands

## Notes

- This phase is the only one that modifies existing files -- phases 1-4 are purely additive
- The `remove` command is phase-5 because it needs the agent registry and lock file integration from earlier phases
- `info` is low-effort given the `list` infrastructure from phase 2 -- it's a single-skill deep view
- Replacing `npx skills add` with our own `addSkill` in catalog.ts is optional -- evaluate whether it's worth the coupling
- The integration tests should use temp dirs to avoid polluting the real `context/skills/`
- `RemoveError` and `InfoError` extend `CliError` to maintain the project's consistent error pattern (code + hint + cause)
- The refactor in 5.3 must maintain backward compatibility for all error codes that `external-skills.ts` callers depend on
- Filter utilities (`filterByAgent`, `filterBySkill`, `filterArgs`) are defined in phase 2 (`lib/skill-filters.ts`) — this phase wires them into the remaining commands
- Task 5.3 (refactor) can start after phase-1 if desired — it only replaces inline git calls with `lib/git.ts`
