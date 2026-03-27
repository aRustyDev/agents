# Phase 4: Agent Abstraction

## Goal

Create a portable agent configuration interface in the SDK so that skill modules (Phase 5) can depend on an abstract `AgentResolver` rather than the CLI's concrete `agents.ts` with its 44-agent registry and filesystem detection.

## Non-Goals

- Moving the CLI's `agents.ts` file out of CLI -- it stays as the concrete implementation.
- Changing the agent list or detection logic.
- Creating new agent types.
- Building agent management commands.

## Prerequisites

- None. This phase is independent -- it creates new SDK interfaces. However, it must complete before Phase 5 begins, because Phase 5 moves skill modules that currently `import { AGENT_CONFIGS, getAgentBaseDir } from './agents'`.

## Files

### Create

| File | Description |
|------|-------------|
| `sdk/src/context/agent/config.ts` | `AgentConfig` interface, `AgentResolver` interface, `AgentType` type alias |
| `sdk/src/context/agent/resolver.ts` | Default `AgentResolver` implementation scaffold (used for testing) |

### Modify

| File | Change |
|------|--------|
| `sdk/src/context/agent/index.ts` | Re-export new config and resolver modules |
| `sdk/src/context/agent/types.ts` | May need reconciliation with new AgentConfig |
| `cli/src/lib/agents.ts` | Add `implements AgentResolver` and export a factory function |
| `sdk/package.json` | Verify exports include `./context/agent/*` (already present) |

### Delete

None. This phase only adds new code.

## Steps

- [ ] **4.1** Audit the SDK's existing agent types in `sdk/src/context/agent/types.ts`:

  ```typescript
  // Current contents
  export interface AgentFrontmatter {
    name: string
    description?: string
    tools?: string[]
    tags?: string[]
  }
  ```

  This is frontmatter metadata for agent YAML files -- different from the CLI's `AgentConfig` which is about agent tool config directories. They coexist without conflict.

- [ ] **4.2** Create `sdk/src/context/agent/config.ts`:

  ```typescript
  /**
   * Portable agent configuration interface.
   *
   * Defines the shape of an agent's directory layout and capabilities.
   * The CLI provides a concrete implementation with 44+ agents;
   * SDK consumers can provide their own.
   */

  /** Agent identifier type -- a string union in the CLI, generic string in SDK. */
  export type AgentId = string

  /** Configuration for a single AI coding agent. */
  export interface AgentConfig {
    /** Machine identifier (e.g., 'claude-code', 'cursor'). */
    readonly name: string
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

  /**
   * Resolves agent configurations at runtime.
   *
   * The SDK defines this interface; the CLI provides the implementation
   * that knows about 44+ concrete agents and their filesystem paths.
   */
  export interface AgentResolver {
    /** List all known agent configurations. */
    list(): AgentConfig[]
    /** Get a specific agent by identifier. Returns undefined if unknown. */
    get(name: string): AgentConfig | undefined
    /** List only agents detected as installed on this machine. */
    detectInstalled(): AgentConfig[]
    /** List agents that support the universal skill format. */
    getUniversal(): AgentConfig[]
    /**
     * Resolve the base skills directory for an agent.
     * @param name - Agent identifier
     * @param global - true for user-level, false for project-scope
     * @param cwd - Project working directory (used when global=false)
     */
    getBaseDir(name: string, global: boolean, cwd: string): string | undefined
  }
  ```

- [ ] **4.3** Create `sdk/src/context/agent/resolver.ts` with a minimal default implementation (for testing and for consumers who don't need the full 44-agent registry):

  ```typescript
  import type { AgentConfig, AgentResolver } from './config'

  /**
   * Create an AgentResolver from a static list of configs.
   * Useful for testing or for consumers who define their own agent set.
   */
  export function createAgentResolver(configs: AgentConfig[]): AgentResolver {
    const byName = new Map(configs.map(c => [c.name, c]))
    return {
      list: () => configs,
      get: (name) => byName.get(name),
      detectInstalled: () => configs.filter(c => c.detectInstalled()),
      getUniversal: () => configs.filter(c => c.universal),
      getBaseDir: (name, global, cwd) => {
        const config = byName.get(name)
        if (!config) return undefined
        return global ? config.globalSkillsDir : `${cwd}/${config.skillsDir}`
      },
    }
  }
  ```

- [ ] **4.4** Update `sdk/src/context/agent/index.ts` to re-export:

  ```typescript
  export * from './config'
  export * from './resolver'
  export * from './parser'
  export * from './schema'
  export * from './types'
  ```

- [ ] **4.5** Update CLI's `agents.ts` to implement the SDK interface. Add at the bottom:

  ```typescript
  import type { AgentResolver } from '@agents/sdk/context/agent/config'

  /** Create an AgentResolver backed by the full 44-agent CLI registry. */
  export function createCliAgentResolver(): AgentResolver {
    return {
      list: () => [...AGENT_CONFIGS.values()],
      get: (name) => AGENT_CONFIGS.get(name as AgentType),
      detectInstalled: () =>
        AGENT_TYPES
          .filter(t => AGENT_CONFIGS.get(t)?.detectInstalled())
          .map(t => AGENT_CONFIGS.get(t)!),
      getUniversal: () => getUniversalAgents(),
      getBaseDir: (name, global, cwd) => {
        const result = getAgentBaseDir(name as AgentType, global, cwd)
        return result.ok ? result.value : undefined
      },
    }
  }
  ```

  This keeps full backward compatibility -- existing code that imports `AGENT_CONFIGS` directly still works. Phase 5 will progressively switch to `AgentResolver`.

  **Important: sync vs async detection.** There are two distinct "detect installed" concepts:
  - `AgentConfig.detectInstalled()` — per-config **synchronous** method (returns `boolean`). Checks a single agent.
  - `detectInstalledAgents()` — module-level **async** function in `cli/src/lib/agents.ts`. Iterates all agents and returns the installed subset.

  The new `AgentResolver.detectInstalled()` returns `AgentConfig[]` **synchronously** (it calls each config's sync `detectInstalled()` and filters). Phase 5 call sites that currently `await detectInstalledAgents()` should switch to the synchronous `resolver.detectInstalled()` — no `await` needed.

- [ ] **4.6** Write tests:
  - `sdk/test/context/agent/config.test.ts`: Verify interface contract with mock data.
  - `sdk/test/context/agent/resolver.test.ts`: Test `createAgentResolver` with sample configs.

- [ ] **4.7** Run `bun test --cwd packages/sdk` -- 382+ pass / 0 fail.
- [ ] **4.8** Run `bun test --cwd packages/cli` -- 1684 pass / 10 fail.

## Acceptance Criteria

1. `sdk/src/context/agent/config.ts` exports `AgentConfig`, `AgentResolver`, `AgentId`.
2. `sdk/src/context/agent/resolver.ts` exports `createAgentResolver`.
3. `cli/src/lib/agents.ts` exports `createCliAgentResolver()` that returns a valid `AgentResolver`.
4. At least 4 unit tests cover the resolver interface.
5. No existing tests break.
6. No files deleted -- this phase is purely additive.

## Failure Criteria

- **Stop if:** The `AgentConfig` interface from the SDK conflicts with the CLI's existing `AgentConfig` type (same name, different shape). Resolution: name the SDK version `PortableAgentConfig` or add a type alias.
- **Stop if:** Adding `import type { AgentResolver } from '@agents/sdk/...'` to `cli/src/lib/agents.ts` creates a circular workspace dependency. Check: CLI depends on SDK (already true), so this direction is fine. If there is somehow a reverse dep, investigate.

## Fallback Logic

1. If the interface proves too restrictive for some agents, make all fields optional except `name` and `skillsDir`.
2. If `detectInstalled()` causes issues in test environments (no home directory), make it optional on the interface with a default of `() => false`.
3. If CLI's `AgentType` picklist (valibot schema) cannot be reconciled with SDK's generic `AgentId = string`, keep them separate. The CLI uses `AgentType` internally; the SDK interface uses `string`. The adapter in `createCliAgentResolver` handles the cast.

## Examples

### SDK consumer (Phase 5 skill module)

```typescript
// Before (in cli/src/lib/skill-list.ts)
import type { AgentType } from './agents'
import { AGENT_CONFIGS } from './agents'

export async function listSkills(opts: { agent?: AgentType }) {
  const agents = opts.agent ? [AGENT_CONFIGS.get(opts.agent)!] : [...AGENT_CONFIGS.values()]
  // ...
}
```

```typescript
// After (in sdk/src/providers/local/skill/list.ts)
import type { AgentResolver } from '../../context/agent/config'

export async function listSkills(
  resolver: AgentResolver,
  opts: { agent?: string }
) {
  const agents = opts.agent
    ? [resolver.get(opts.agent)].filter(Boolean)
    : resolver.list()
  // ...
}
```

### CLI wiring (in component/skill-ops-impl.ts, after Phase 5)

```typescript
import { createCliAgentResolver } from '../agents'
import { listSkills } from '@agents/sdk/providers/local/skill/list'

const resolver = createCliAgentResolver()

export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      return listSkills(resolver, opts)
    },
    // ...
  }
}
```

## Dependency Notes

- This phase creates no inter-phase dependencies -- it is purely additive.
- The `AgentResolver` interface is consumed by Phase 5 modules. Phase 5 cannot start until this interface exists.
- The CLI's `agents.ts` keeps its existing exports (`AGENT_CONFIGS`, `AgentType`, `getAgentBaseDir`). The new `createCliAgentResolver` is additive. Old callers continue to work until Phase 5 migrates them.
- The SDK's existing `context/agent/types.ts` (`AgentFrontmatter`) is about agent YAML metadata, not agent tool configuration. The two coexist in the same directory without conflict.
