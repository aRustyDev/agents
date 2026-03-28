# Phase 5: Skill Operations to SDK

## Goal

Move the 11 skill lifecycle modules from `cli/src/lib/` into the SDK, using the `AgentResolver` interface from Phase 4 instead of direct imports from `cli/src/lib/agents.ts`. After this phase, the CLI's `SkillOperations` DI adapter becomes trivial -- it just re-exports SDK functions.

## Non-Goals

- Changing skill add/remove/update behavior.
- Adding new skill operations.
- Moving the `agents.ts` file (it stays in CLI as the concrete `AgentResolver` implementation).
- Modifying the `SkillOperations` interface defined in `sdk/src/providers/local/skill-ops.ts` (it may be extended but not broken).

## Prerequisites

- **Phase 2 complete:** `manifest.ts` and `lockfile.ts` are in SDK. Skill modules that import `readSkillFrontmatter`, `readLockfile` must resolve from `@agents/sdk`.
- **Phase 4 complete:** `AgentResolver` interface exists in SDK. Skill modules that import `AGENT_CONFIGS`, `AgentType`, `getAgentBaseDir` will be refactored to accept an `AgentResolver` parameter.

## Files

### Move

| Source (cli/src/lib/) | Destination (sdk/src/) | Lines | Agent Dependency |
|-----------------------|------------------------|-------|------------------|
| `skill-add.ts` (311) | `providers/local/skill/add.ts` | 311 | Yes — uses `detectInstalledAgents`, `getAgentBaseDir` |
| `skill-remove.ts` (205) | `providers/local/skill/remove.ts` | 205 | Yes (`AGENT_CONFIGS`, `getAgentBaseDir`) |
| `skill-list.ts` (174) | `providers/local/skill/list.ts` | 174 | Yes (`AGENT_CONFIGS`) |
| `skill-info.ts` (143) | `providers/local/skill/info.ts` | 143 | Yes (`detectInstalledAgents`, `getAgentBaseDir`) |
| `skill-init.ts` (203) | `context/skill/init.ts` | 203 | None |
| `skill-outdated.ts` (334) | `providers/local/skill/outdated.ts` | 334 | None (uses lockfile) |
| `skill-update.ts` (162) | `providers/local/skill/update.ts` | 162 | Yes (indirect — delegates to `addSkill` which uses `AgentResolver`) |
| `skill-discovery.ts` (168) | `context/skill/discovery.ts` | 168 | None |
| `skill-filters.ts` (96) | `providers/local/skill/filters.ts` | 96 | Yes (`AgentType`, `AGENT_CONFIGS`) |
| `skill-find.ts` (117) | `providers/local/skill/find.ts` | 117 | None |
| `skill-search-api.ts` (284) | `providers/local/skill/search-api.ts` | 284 | None (uses meilisearch) |

### Create

| File | Description |
|------|-------------|
| `sdk/src/providers/local/skill/index.ts` | Barrel for skill submodule |
| `sdk/src/context/skill/init.ts` | Skill scaffolding (from skill-init.ts) |
| `sdk/src/context/skill/discovery.ts` | Skill file discovery (from skill-discovery.ts) |

### Modify

| File | Change |
|------|--------|
| `sdk/src/providers/local/skill-ops.ts` | Extend `SkillOperations` interface if needed (add `outdated`, `update`, `find`, `search`) |
| `sdk/src/providers/local/index.ts` | Re-export skill submodule |
| `sdk/src/context/skill/index.ts` | Re-export init and discovery |
| `sdk/package.json` | Add exports for `./providers/local/skill/*`, `./context/skill/init`, `./context/skill/discovery` |
| `cli/src/lib/component/skill-ops-impl.ts` | Update dynamic imports from `'../skill-*'` to `'@agents/sdk/providers/local/skill/*'` |
| `cli/src/commands/add.ts` | Update imports |
| `cli/src/commands/remove.ts` | Update imports |
| `cli/src/commands/list.ts` | Update imports |
| `cli/src/commands/info.ts` | Update imports |
| `cli/src/commands/search.ts` | Update imports |
| `cli/src/commands/update.ts` | Update imports |

### Delete

| File | Lines |
|------|-------|
| `packages/cli/src/lib/skill-add.ts` | 311 |
| `packages/cli/src/lib/skill-remove.ts` | 205 |
| `packages/cli/src/lib/skill-list.ts` | 174 |
| `packages/cli/src/lib/skill-info.ts` | 143 |
| `packages/cli/src/lib/skill-init.ts` | 203 |
| `packages/cli/src/lib/skill-outdated.ts` | 334 |
| `packages/cli/src/lib/skill-update.ts` | 162 |
| `packages/cli/src/lib/skill-discovery.ts` | 168 |
| `packages/cli/src/lib/skill-filters.ts` | 96 |
| `packages/cli/src/lib/skill-find.ts` | 117 |
| `packages/cli/src/lib/skill-search-api.ts` | 284 |

## Steps

### Stage A: Agent-Independent Modules First

Move modules that do NOT import from `agents.ts` -- these are simpler because they need no `AgentResolver` refactoring.

- [ ] **5.1** Copy `skill-init.ts` to `sdk/src/context/skill/init.ts`. Update imports:
  - `CliError` -> `SdkError`
  - Already imports from `@agents/core` (fine)
- [ ] **5.2** Copy `skill-discovery.ts` to `sdk/src/context/skill/discovery.ts`. Update imports:
  - `import { readSkillFrontmatter } from './manifest'` -> `import { readSkillFrontmatter } from '../manifest'` (now sibling in SDK context)
- [ ] **5.3** Copy `skill-outdated.ts` to `sdk/src/providers/local/skill/outdated.ts`. Update imports:
  - `import { readLockfile } from './lockfile'` -> `import { readLockfile } from '../lockfile'` (sibling in providers/local)
- [ ] **5.4** Copy `skill-find.ts` to `sdk/src/providers/local/skill/find.ts`. Update imports:
  - Schema imports from `@agents/sdk` become relative.
  - `import { searchSkillsAPI } from './skill-search-api'` -> `import { searchSkillsAPI } from './search-api'`
- [ ] **5.5** Copy `skill-search-api.ts` to `sdk/src/providers/local/skill/search-api.ts`. Update imports:
  - `import { checkHealth, createClient, searchKeyword } from './meilisearch'` -> `import { checkHealth, createClient, searchKeyword } from '@agents/kg/meilisearch'`
  - This creates an SDK -> KG dependency. Evaluate if acceptable. If not, use dynamic import.

### Stage B: Agent-Dependent Modules

These modules import `AGENT_CONFIGS`, `AgentType`, `detectInstalledAgents`, or `getAgentBaseDir`. Refactor them to accept an `AgentResolver` parameter.

- [ ] **5.7** Copy `skill-add.ts` to `sdk/src/providers/local/skill/add.ts`. Refactor:
  - `CliError` -> `SdkError`
  - Replace dynamic `import('./agents')` calls (`detectInstalledAgents`, `getAgentBaseDir`) with `AgentResolver` parameter:

  ```typescript
  // Before
  const { detectInstalledAgents } = await import('./agents')
  const installed = await detectInstalledAgents()
  const { getAgentBaseDir } = await import('./agents')

  // After
  import type { AgentResolver } from '../../../context/agent/config'
  export async function addSkill(
    resolver: AgentResolver,
    source: string,
    opts: AddSkillOpts
  ) {
    const installed = resolver.detectInstalled()
    // Use resolver.getBaseDir() instead of getAgentBaseDir()
  }
  ```

- [ ] **5.8** Copy `skill-update.ts` to `sdk/src/providers/local/skill/update.ts`. Refactor:
  - `import { addSkill } from './skill-add'` -> `import { addSkill } from './add'`
  - `import { checkOutdated } from './skill-outdated'` -> `import { checkOutdated } from './outdated'`
  - Since `addSkill` now requires `AgentResolver`, thread the resolver parameter through `updateSkill`:

  ```typescript
  // Before
  export async function updateSkill(opts: UpdateOpts) {
    const result = await addSkill(opts.source, opts)
  // After
  import type { AgentResolver } from '../../../context/agent/config'
  export async function updateSkill(resolver: AgentResolver, opts: UpdateOpts) {
    const result = await addSkill(resolver, opts.source, opts)
  ```

- [ ] **5.9** Copy `skill-filters.ts` to `sdk/src/providers/local/skill/filters.ts`. Refactor:

  ```typescript
  // Before
  import type { AgentType } from './agents'
  import { AGENT_CONFIGS } from './agents'

  export function filterByAgent(skills: InstalledSkillEntry[], agent?: AgentType) {
    if (!agent) return skills
    const config = AGENT_CONFIGS.get(agent)
    // ...
  }
  ```

  ```typescript
  // After
  import type { AgentResolver } from '../../../context/agent/config'

  export function filterByAgent(
    resolver: AgentResolver,
    skills: InstalledSkillEntry[],
    agent?: string
  ) {
    if (!agent) return skills
    const config = resolver.get(agent)
    // ...
  }
  ```

- [ ] **5.10** Copy `skill-list.ts` to `sdk/src/providers/local/skill/list.ts`. Refactor:

  ```typescript
  // Before
  import { AGENT_CONFIGS } from './agents'
  export async function listSkills(opts: { cwd?: string; agent?: AgentType }) {
    const agents = opts.agent ? [AGENT_CONFIGS.get(opts.agent)!] : [...AGENT_CONFIGS.values()]
  ```

  ```typescript
  // After
  import type { AgentResolver } from '../../../context/agent/config'
  export async function listSkills(resolver: AgentResolver, opts: { cwd?: string; agent?: string }) {
    const agents = opts.agent
      ? [resolver.get(opts.agent)].filter((c): c is AgentConfig => c !== undefined)
      : resolver.list()
  ```

- [ ] **5.11** Copy `skill-remove.ts` to `sdk/src/providers/local/skill/remove.ts`. Refactor similarly -- replace `AGENT_CONFIGS` and `getAgentBaseDir` with `resolver` parameter.
- [ ] **5.12** Copy `skill-info.ts` to `sdk/src/providers/local/skill/info.ts`. Refactor:
  - Replace `detectInstalledAgents` with `resolver.detectInstalled()`
  - Replace `getAgentBaseDir` with `resolver.getBaseDir()`
  - Replace `readLockfile` import to SDK path
  - Replace `readSkillFrontmatter` import to SDK path

### Stage C: Wire Up

- [ ] **5.13** Create `sdk/src/providers/local/skill/index.ts` barrel:

  ```typescript
  export * from './add'
  export * from './find'
  export * from './filters'
  export * from './info'
  export * from './list'
  export * from './outdated'
  export * from './remove'
  export * from './search-api'
  export * from './update'
  ```

- [ ] **5.14** Update `sdk/src/context/skill/index.ts` to add:

  ```typescript
  export * from './init'
  export * from './discovery'
  ```

- [ ] **5.15** Update `sdk/package.json` exports for new paths.
- [ ] **5.16** Update `cli/src/lib/component/skill-ops-impl.ts`:

  ```typescript
  // Before
  export function createSkillOps(): SkillOperations {
    return {
      async list(opts) {
        const { listSkills } = await import('../skill-list')
        return listSkills(opts)
      },
  ```

  ```typescript
  // After
  import { createCliAgentResolver } from '../agents'
  import type { SkillOperations } from '@agents/sdk/providers/local/skill-ops'

  const resolver = createCliAgentResolver()

  export function createSkillOps(): SkillOperations {
    return {
      async list(opts) {
        const { listSkills } = await import('@agents/sdk/providers/local/skill/list')
        return listSkills(resolver, opts)
      },
  ```

- [ ] **5.17** Update CLI command files (`add.ts`, `remove.ts`, `list.ts`, `info.ts`, `search.ts`, `update.ts`) to import from SDK or go through the component manager.
- [ ] **5.18** Consider extending the `SkillOperations` interface in `sdk/src/providers/local/skill-ops.ts` to include operations not currently covered:

  ```typescript
  export interface SkillOperations {
    list(opts: { cwd?: string; agent?: string }): Promise<{ ok: boolean; skills: any[] }>
    add(source: string, opts: any): Promise<any>
    remove(names: string[], opts: any): Promise<any[]>
    info(name: string, opts: any): Promise<any>
    // New:
    outdated?(opts: any): Promise<any[]>
    update?(opts: any): Promise<any>
    find?(query: string, opts: any): Promise<any[]>
    init?(name: string, opts: any): Promise<any>
  }
  ```

  Mark new methods as optional to preserve backward compatibility.

### Stage D: Verify and Clean

- [ ] **5.19** Run `bun test --cwd packages/sdk` -- expect significant increase (382 + new skill tests).
- [ ] **5.20** Run `bun test --cwd packages/cli` -- 1684 / 10 maintained.
- [ ] **5.21** Delete the 11 source files from `cli/src/lib/`.
- [ ] **5.22** Run full test suite after deletion.
- [ ] **5.23** Verify skill commands work end-to-end:

  ```bash
  bun run packages/cli/src/bin/agents.ts list --type skill
  bun run packages/cli/src/bin/agents.ts add --help
  bun run packages/cli/src/bin/agents.ts remove --help
  ```

## Acceptance Criteria

1. `sdk/src/providers/local/skill/` contains at least 9 files (add, remove, list, info, outdated, update, find, filters, search-api, index).
2. `sdk/src/context/skill/init.ts` and `sdk/src/context/skill/discovery.ts` exist.
3. No SDK module imports from `cli/src/lib/agents.ts` directly. All agent access goes through `AgentResolver`.
4. `cli/src/lib/component/skill-ops-impl.ts` imports from `@agents/sdk/providers/local/skill/*`.
5. SDK tests: 382+ pass / 0 fail (likely 400+ with new skill tests).
6. CLI tests: 1684 pass / 10 fail.
7. `cli/src/lib/` no longer contains any `skill-*.ts` files.
8. All skill CLI commands work interactively.

## Failure Criteria

- **Stop if:** The `AgentResolver` parameter threading breaks more than 5 functions' signatures. Consider using a module-level resolver setter instead:

  ```typescript
  let _resolver: AgentResolver | undefined
  export function setAgentResolver(r: AgentResolver) { _resolver = r }
  ```

  This is less clean but avoids changing every function signature.

- **Stop if:** `skill-search-api.ts` importing `@agents/kg/meilisearch` creates an unacceptable SDK -> KG dependency. In that case, keep `skill-search-api.ts` in CLI as a thin adapter and export a narrower interface from SDK.

- **Stop if:** More than 30 CLI tests fail after moving. Roll back and investigate which tests depend on file-path assumptions.

## Fallback Logic

1. **Incremental shims:** If moving all 11 files at once is too risky, move them in sub-batches:
   - Batch A (no agent deps): skill-init, skill-discovery, skill-outdated (3 files)
   - Batch B (agent deps): skill-add, skill-update, skill-list, skill-remove, skill-info, skill-filters (6 files)
   - Batch C (search): skill-find, skill-search-api (2 files)
   Leave re-export shims in CLI for each batch.

2. **Module-level resolver:** If threading `AgentResolver` through all call sites is impractical, use a module initializer pattern:

   ```typescript
   // sdk/src/providers/local/skill/_resolver.ts
   let resolver: AgentResolver
   export function initSkillModule(r: AgentResolver) { resolver = r }
   export function getResolver(): AgentResolver { return resolver }
   ```

   CLI calls `initSkillModule(createCliAgentResolver())` at startup.

3. **Keep skill-search-api in CLI:** If the KG dependency from SDK is problematic, `skill-search-api.ts` and `skill-find.ts` can stay in CLI. Adjust target file count from 4 to 6.

## Examples

### Before (cli/src/lib/skill-list.ts)

```typescript
import { existsSync } from 'node:fs'
import { lstat, readdir, readlink } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { CliError } from '@agents/core/types'
import type { AgentType } from './agents'
import { AGENT_CONFIGS } from './agents'
import { filterByAgent, filterBySkill, type InstalledSkillEntry } from './skill-filters'

export async function listSkills(opts: {
  cwd?: string
  agent?: AgentType
  // ...
}) {
  const agents = opts.agent
    ? [AGENT_CONFIGS.get(opts.agent)!]
    : [...AGENT_CONFIGS.values()]
  // ...
}
```

### After (sdk/src/providers/local/skill/list.ts)

```typescript
import { existsSync } from 'node:fs'
import { lstat, readdir, readlink } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import type { AgentConfig, AgentResolver } from '../../../context/agent/config'
import { SdkError } from '../../../util/errors'
import { filterByAgent, filterBySkill, type InstalledSkillEntry } from './filters'

export async function listSkills(
  resolver: AgentResolver,
  opts: {
    cwd?: string
    agent?: string
    // ...
  }
) {
  const agents: AgentConfig[] = opts.agent
    ? [resolver.get(opts.agent)].filter((c): c is AgentConfig => c !== undefined)
    : resolver.list()
  // ...
}
```

### Before (cli/src/lib/component/skill-ops-impl.ts)

```typescript
export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      const { listSkills } = await import('../skill-list')
      return listSkills(opts)
    },
```

### After (cli/src/lib/component/skill-ops-impl.ts)

```typescript
import { createCliAgentResolver } from '../agents'

const resolver = createCliAgentResolver()

export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      const { listSkills } = await import('@agents/sdk/providers/local/skill/list')
      return listSkills(resolver, opts)
    },
```

## Test Files

Move corresponding test files from `packages/cli/test/` to `packages/sdk/test/providers/local/`:
- `skill-add.test.ts` --> `packages/sdk/test/providers/local/skill/add.test.ts`
- `skill-remove.test.ts` --> `packages/sdk/test/providers/local/skill/remove.test.ts`
- `skill-list.test.ts` --> `packages/sdk/test/providers/local/skill/list.test.ts`
- `skill-info.test.ts` --> `packages/sdk/test/providers/local/skill/info.test.ts`
- `skill-outdated.test.ts` --> `packages/sdk/test/providers/local/skill/outdated.test.ts`
- `skill-filters.test.ts` --> `packages/sdk/test/providers/local/skill/filters.test.ts`
- `skill-find.test.ts` --> `packages/sdk/test/providers/local/skill/find.test.ts`

Update imports in moved tests to use `@agents/sdk/providers/local/skill/*` paths. Tests for agent-dependent modules (Stage B) will need mock `AgentResolver` instances instead of importing from `cli/src/lib/agents.ts` directly. If tests have CLI-specific fixtures, keep them in CLI and update imports to point to the new SDK package paths.

## Dependency Notes

- **skill-search-api -> meilisearch:** After Phase 1, meilisearch is in `@agents/kg`. Moving skill-search-api to SDK creates `@agents/sdk` -> `@agents/kg` dependency. This may be acceptable (SDK can depend on KG for search features). If not, use dynamic import or keep search-api in CLI.
- **skill-discovery -> manifest:** Already resolved by Phase 2. Discovery imports `readSkillFrontmatter` from `@agents/sdk/context/manifest`.
- **skill-outdated -> lockfile:** Already resolved by Phase 2. Outdated imports `readLockfile` from `@agents/sdk/providers/local/lockfile`.
- **skill-update -> skill-add + skill-outdated:** All three move in this phase. `skill-update` and `skill-add` are both in Stage B (agent-dependent); internal relative imports. `skill-update` must also pass `AgentResolver` through to `addSkill()`.
- **skill-filters -> agents:** Resolved by Phase 4's `AgentResolver`. Filters accept resolver as parameter.
- **skill-list -> skill-filters:** Both move to `sdk/providers/local/skill/`. Internal relative import.
- **skill-info -> agents + lockfile + manifest:** All resolved by Phases 2 + 4.
