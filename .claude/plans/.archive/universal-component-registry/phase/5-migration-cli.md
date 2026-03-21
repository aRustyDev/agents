# Phase 5: Migration + CLI Wiring

**ID:** `phase-5`
**Dependencies:** phase-3a-d (complete), phase-4a
**Status:** planned

## Objective

Wire the component system into the CLI. Create new `mcp` top-level command. Create a cross-type `component search` command. Refactor existing skill commands to optionally delegate through `ComponentManager`. Update CLAUDE.md documentation.

## Success Criteria

- [ ] `just agents mcp search "postgres"` searches Smithery for MCP servers
- [ ] `just agents mcp add smithery://ns/server --client claude-desktop` installs to client config
- [ ] `just agents mcp list --client cursor` lists MCP servers from Cursor's config
- [ ] `just agents mcp remove server-name --client claude-desktop` removes from config
- [ ] `just agents mcp info ns/server` shows server details from Smithery
- [ ] `just agents mcp publish --name ns/server --url https://...` publishes external URL (Phase 4a)
- [ ] `just agents component search "kubernetes"` searches all types across all providers
- [ ] `just agents component list` lists all installed components grouped by type
- [ ] All existing skill commands continue to work unchanged
- [ ] CLAUDE.md updated with new commands
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| MCP command tree | `cli/commands/mcp.ts` | TypeScript |
| Component command tree | `cli/commands/component.ts` | TypeScript |
| Manager factory | `cli/lib/component/factory.ts` | TypeScript |
| CLI wiring for agents.ts | `cli/bin/agents.ts` | TypeScript (modification) |
| MCP command tests | `cli/test/commands/mcp.test.ts` | bun:test |
| Component command tests | `cli/test/commands/component.test.ts` | bun:test |
| Manager factory tests | `cli/test/component/factory.test.ts` | bun:test |

## Files

**Create:**
- `cli/commands/mcp.ts`
- `cli/commands/component.ts`
- `cli/lib/component/factory.ts`
- `cli/test/commands/mcp.test.ts`
- `cli/test/commands/component.test.ts`
- `cli/test/component/factory.test.ts`

**Modify:**
- `cli/bin/agents.ts` (add `mcp` and `component` subcommands)
- `CLAUDE.md` (add new commands to Common Tasks table)

## Design

### Manager Factory

All CLI commands need a configured `ComponentManager` with all providers registered. Instead of repeating the registration in every command, create a factory:

```typescript
// cli/lib/component/factory.ts
import { ComponentManager } from './manager'
import { LocalProvider } from './provider-local'
import { LocalAgentProvider } from './provider-agent'
import { LocalPluginProvider } from './provider-plugin'
import { LocalRuleProvider } from './provider-rule'
import { LocalCommandProvider } from './provider-command'
import { LocalOutputStyleProvider } from './provider-output-style'
import { SmitheryProvider } from './provider-smithery'

/**
 * Create a fully-configured ComponentManager with all providers registered.
 * This is the canonical way to get a manager — CLI commands use this.
 */
export function createComponentManager(opts?: { cwd?: string }): ComponentManager {
  const cwd = opts?.cwd
  const manager = new ComponentManager()

  // Local providers
  manager.register(new LocalProvider(cwd))
  manager.register(new LocalAgentProvider(cwd))
  manager.register(new LocalPluginProvider(cwd))
  manager.register(new LocalRuleProvider(cwd))
  manager.register(new LocalCommandProvider(cwd))
  manager.register(new LocalOutputStyleProvider(cwd))

  // Remote providers
  manager.register(new SmitheryProvider())

  return manager
}
```

### MCP Command Tree

```
agents mcp
├── search <query>      [--limit] [--page] [--verified] [--namespace] [--json]
├── add <source>        [--client <name>] [--config <json>] [--name <id>]
├── list                [--client <name>] [--json]
├── remove <name>       [--client <name>]
├── info <name>         [--json]
└── publish             [--name <ns/slug>] [--url <external-url>] [--bundle-dir <path>]
                        [--config-schema <json>] [--dry-run] [--api-key <key>]
```

### Component Command Tree (cross-type)

```
agents component
├── search <query>      [--type <type>] [--limit] [--page] [--json]
└── list                [--type <type>] [--json]
```

### MCP Add Logic

Two modes based on `--client` flag:

**Without --client (default):** Delegate to `manager.add()` for the `mcp_server` type. This currently goes through `LocalProvider` (which wraps `addSkill`). For MCP servers, this doesn't make sense — there's no SKILL.md to install. So `mcp add` without `--client` should:
- Resolve the source via `parseSource()`
- If `smithery://` source: display server info from Smithery API and suggest `--client` flag
- If local source: copy MCP server config to a local `.mcp.json` or similar

**With --client:** Use `client-config.ts` to write the MCP server entry to the client's config file:
1. Resolve server source (Smithery URL → server details, or manual stdio/http config)
2. Determine transport type (stdio for command-based, http for URL-based)
3. Call `writeServerToClient(clientId, serverName, { transport, url/command, args, env })`
4. Report success with client-specific restart hint

### Component Search Logic

Cross-type search using `manager.search({ query })` with no type filter:
- Aggregates results from all providers
- Groups output by type in human mode
- Flat array in JSON mode
- Supports `--type` to filter to a single type

## Tasks

### Task 5.1: Manager Factory

**Files:** Create `cli/lib/component/factory.ts`, `cli/test/component/factory.test.ts`

Tests:
1. `createComponentManager()` returns a ComponentManager
2. Manager has all 7 providers registered (local + local-agent + local-plugin + local-rule + local-command + local-output-style + smithery)
3. `search({ type: 'skill' })` routes to local provider
4. `search({ type: 'mcp_server' })` routes to smithery provider
5. `search({ type: 'agent' })` routes to local-agent provider
6. Accepts `cwd` option and passes to local providers

### Task 5.2: MCP Command Tree

**Files:** Create `cli/commands/mcp.ts`, `cli/test/commands/mcp.test.ts`

Each subcommand follows the Citty pattern:

```typescript
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'
import { createOutput } from '../lib/output'
import { createComponentManager } from '../lib/component/factory'
import { EXIT } from '../lib/types'

export default defineCommand({
  meta: { name: 'mcp', description: 'MCP server management' },
  subCommands: {
    search: defineCommand({
      meta: { name: 'search', description: 'Search for MCP servers' },
      args: {
        ...globalArgs,
        query: { type: 'positional', description: 'Search query', required: false },
        limit: { type: 'string', description: 'Max results', default: '10' },
        page: { type: 'string', description: 'Page number', default: '1' },
        verified: { type: 'boolean', description: 'Only verified servers', default: false },
        namespace: { type: 'string', description: 'Filter by namespace' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()
        const result = await manager.search({
          query: (args.query as string) ?? '',
          type: 'mcp_server',
          limit: parseInt(args.limit as string, 10),
          page: parseInt(args.page as string, 10),
          verified: args.verified as boolean,
          namespace: args.namespace as string | undefined,
        })
        if (!result.ok) { out.error(result.error.display()); process.exit(EXIT.ERROR) }
        if (args.json) { out.raw(result.value); return }
        if (result.value.items.length === 0) { out.info('No MCP servers found'); return }
        out.table(
          result.value.items.map(c => ({
            name: c.name,
            description: (c.description ?? '').slice(0, 60),
            installs: c.installs ?? '-',
            verified: c.verified ? 'yes' : '-',
          })),
          ['name', 'description', 'installs', 'verified'],
        )
        if (result.value.hasMore) out.info(`Page ${result.value.page}. Use --page ${result.value.page + 1} for more.`)
      },
    }),

    add: defineCommand({
      meta: { name: 'add', description: 'Add an MCP server to a client' },
      args: {
        ...globalArgs,
        source: { type: 'positional', description: 'Server source (smithery://ns/slug, URL, or name)', required: true },
        client: { type: 'string', alias: 'c', description: 'Target client (claude-desktop, cursor, vscode, ...)' },
        name: { type: 'string', description: 'Server name/ID in client config' },
        config: { type: 'string', description: 'Server config JSON' },
      },
      async run({ args }) {
        // Route based on --client flag
        // With --client: write to client config via client-config.ts
        // Without --client: show info + suggest --client
      },
    }),

    list: defineCommand({ /* list from --client config or show hint */ }),
    remove: defineCommand({ /* remove from --client config */ }),
    info: defineCommand({ /* fetch from Smithery API */ }),
    publish: defineCommand({ /* delegate to manager.publish() — Phase 4a */ }),
  },
})
```

Tests:
1. `mcp search` subcommand is defined with correct args
2. `mcp add` subcommand is defined with --client flag
3. `mcp list` subcommand is defined
4. `mcp remove` subcommand is defined
5. `mcp info` subcommand is defined
6. `mcp publish` subcommand is defined
7. All subcommands have non-empty descriptions

### Task 5.3: Component Command Tree

**Files:** Create `cli/commands/component.ts`, `cli/test/commands/component.test.ts`

```typescript
export default defineCommand({
  meta: { name: 'component', description: 'Cross-type component management' },
  subCommands: {
    search: defineCommand({
      meta: { name: 'search', description: 'Search all component types' },
      args: {
        ...globalArgs,
        query: { type: 'positional', description: 'Search query', required: true },
        type: { type: 'string', description: 'Filter by type (skill, mcp_server, agent, plugin, rule, command, output_style)' },
        limit: { type: 'string', description: 'Max results', default: '10' },
        page: { type: 'string', description: 'Page number', default: '1' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()
        const result = await manager.search({
          query: args.query as string,
          type: args.type ? (args.type as ComponentType) : undefined,
          limit: parseInt(args.limit as string, 10),
          page: parseInt(args.page as string, 10),
        })
        if (!result.ok) { out.error(result.error.display()); process.exit(EXIT.ERROR) }
        if (args.json) { out.raw(result.value); return }
        // Group by type in human output
        const grouped = new Map<string, Component[]>()
        for (const c of result.value.items) {
          if (!grouped.has(c.type)) grouped.set(c.type, [])
          grouped.get(c.type)!.push(c)
        }
        for (const [type, items] of grouped) {
          out.info(`\n${type} (${items.length}):`)
          out.table(items.map(c => ({ name: c.name, description: (c.description ?? '').slice(0, 60) })))
        }
      },
    }),

    list: defineCommand({
      meta: { name: 'list', description: 'List all installed components' },
      args: {
        ...globalArgs,
        type: { type: 'string', description: 'Filter by type' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()
        // List all types or filtered type
        const types = args.type
          ? [args.type as ComponentType]
          : ['skill', 'mcp_server', 'agent', 'plugin', 'rule', 'command', 'output_style'] as ComponentType[]

        const allComponents: Component[] = []
        for (const type of types) {
          const result = await manager.list(type)
          if (result.ok) allComponents.push(...result.value)
        }

        if (args.json) { out.raw(allComponents); return }
        // Group by type
        const grouped = new Map<string, Component[]>()
        for (const c of allComponents) {
          if (!grouped.has(c.type)) grouped.set(c.type, [])
          grouped.get(c.type)!.push(c)
        }
        for (const [type, items] of grouped) {
          out.info(`\n${type} (${items.length}):`)
          out.table(items.map(c => ({ name: c.name, source: c.source, description: (c.description ?? '').slice(0, 50) })))
        }
      },
    }),
  },
})
```

Tests:
1. `component search` subcommand defined
2. `component list` subcommand defined
3. Both have non-empty descriptions
4. `--type` flag accepts valid ComponentType values

### Task 5.4: Wire into Main CLI

**Files:** Modify `cli/bin/agents.ts`

Add `mcp` and `component` to the subCommands:

```typescript
subCommands: {
  plugin: () => import('../commands/plugin').then(m => m.default),
  skill: () => import('../commands/skill').then(m => m.default),
  mcp: () => import('../commands/mcp').then(m => m.default),           // NEW
  component: () => import('../commands/component').then(m => m.default), // NEW
  kg: () => import('../commands/kg').then(m => m.default),
  registry: () => import('../commands/registry').then(m => m.default),
  'graph-viewer': () => import('../commands/graph-viewer').then(m => m.default),
},
```

Test: verify the main command imports resolve without error.

### Task 5.5: Documentation

**Files:** Modify `CLAUDE.md`

Add to Common Tasks table:

```markdown
| Task | Command |
|------|---------|
| Search MCP servers | `just agents mcp search "postgres"` |
| Add MCP to client | `just agents mcp add smithery://ns/server --client claude-desktop` |
| List MCP in client | `just agents mcp list --client cursor` |
| Remove MCP from client | `just agents mcp remove server-name --client cursor` |
| MCP server info | `just agents mcp info ns/server-name` |
| Search all components | `just agents component search "kubernetes"` |
| List all components | `just agents component list` |
| List by type | `just agents component list --type agent` |
```

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `mcp add` without `--client` | Show server info and suggest adding `--client` flag |
| `mcp add --client unknown` | Error: "Unknown client. Available: claude-desktop, cursor, ..." |
| `mcp list` without `--client` | List from all detected clients? Or require `--client`? Require for MVP. |
| `mcp remove` server not in client | Warn but succeed (idempotent) |
| `component search` with no providers for a type | Return empty for that type, results from other types still show |
| `component list` in empty project | Return empty, no error |
| `--json` on all commands | Output valid JSON to stdout |
| `--quiet` on all commands | Suppress info/warn, only errors |

## Acceptance Criteria

- [ ] `agents mcp` command tree with 6 subcommands (search, add, list, remove, info, publish)
- [ ] `agents component` command tree with 2 subcommands (search, list)
- [ ] `createComponentManager()` factory with all 7 providers
- [ ] `mcp add --client` writes to client config files
- [ ] `mcp list --client` reads from client config files
- [ ] `component search` aggregates across all providers and types
- [ ] All commands support `--json` and `--quiet`
- [ ] CLAUDE.md updated
- [ ] At least 20 tests across command + factory test files
- [ ] Existing skill commands unchanged (backward compatible)
