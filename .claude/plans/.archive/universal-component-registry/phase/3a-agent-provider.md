# Phase 3a: Agent Provider

**ID:** `phase-3a`
**Dependencies:** phase-1 (complete)
**Status:** planned

## Objective

Create a `LocalAgentProvider` that discovers agent definition markdown files from `context/agents/` and exposes them as `Component` objects. Agents are nested in category subdirectories and use YAML frontmatter.

## Success Criteria

- [ ] `LocalAgentProvider` discovers all agent `.md` files in nested category directories
- [ ] Excludes application-agent directories (those with `pyproject.toml`)
- [ ] Excludes non-agent markdown (README.md, prompt.md in subagents/)
- [ ] Parses YAML frontmatter for `name`, `description`, `tools`, `allowed-tools`
- [ ] Search filters by query (substring on name+description)
- [ ] `manager.list('agent')` returns all discovered agents
- [ ] `manager.search({ type: 'agent', query: 'frontend' })` returns matching agents
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Agent provider | `cli/lib/component/provider-agent.ts` | TypeScript |
| Agent provider tests | `cli/test/component/provider-agent.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/component/provider-agent.ts`
- `cli/test/component/provider-agent.test.ts`

## On-Disk Structure

```
context/agents/
├── _context-agents/         # skip (underscore prefix)
├── development/
│   ├── core/
│   │   ├── frontend-developer.md    ← agent (has frontmatter)
│   │   ├── backend-developer.md     ← agent
│   │   └── fullstack-developer.md   ← agent
│   └── experience/
│       ├── mcp-developer.md         ← agent
│       └── dx-optimizer.md          ← agent
├── skill-reviewer/          # skip (has pyproject.toml — app agent)
│   ├── pyproject.toml
│   ├── subagents/
│   └── README.md            # skip
├── meta/
│   ├── orchestration/
│   │   └── bd-task-agent.md ← agent
│   └── skills/
│       └── skill-reviewer.md ← agent (different from the app dir)
└── ...
```

**Discovery pattern:** `glob("context/agents/**/*.md")` with these exclusions:
1. Directories containing `pyproject.toml` (application agents: `skill-reviewer/`, `skill-pr-addresser/`, `skill-agents-common/`)
2. Files named `README.md` or `prompt.md` (not agent definitions)
3. Directories starting with `_` (private/internal: `_context-agents/`)

**Frontmatter format:**
```yaml
---
name: frontend-developer
description: Expert UI engineer focused on crafting robust, scalable frontend solutions.
tools: Read, Write, Edit, Bash, Glob, Grep
---
```

Fields: `name` (required), `description` (required), `tools` (optional, comma-separated), `allowed-tools` (optional).

**Name derivation:** From frontmatter `name` field. If missing, derive from filename (strip `.md`).

## Tasks

### Task 3a.1: Agent Provider

- [ ] **Step 1: Write failing tests**

```typescript
// cli/test/component/provider-agent.test.ts
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { LocalAgentProvider } from '../../lib/component/provider-agent'

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'agent-provider-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

async function createAgent(dir: string, name: string, desc = 'Test agent'): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(join(dir, `${name}.md`), `---\nname: ${name}\ndescription: ${desc}\ntools: Read, Write\n---\n\n# ${name}\n`)
}

async function createAppAgent(dir: string): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(join(dir, 'pyproject.toml'), '[project]\nname = "app-agent"\n')
  await writeFile(join(dir, 'README.md'), '# App Agent\n')
}
```

Tests:
1. **capabilities: declares agent support for search, list, info**
2. **search: discovers agents in nested category dirs**
3. **search: excludes dirs with pyproject.toml** (app agents)
4. **search: excludes README.md and prompt.md**
5. **search: excludes underscore-prefixed dirs**
6. **search: filters by query on name+description**
7. **search: returns empty for non-agent type**
8. **search: paginates results**
9. **list: returns all agents**
10. **info: returns agent detail by name**
11. **info: returns error for unknown agent**
12. **agent Component has correct shape** (type, name, source, description, tags with tools)
13. **derives name from filename when frontmatter name missing**

- [ ] **Step 2: Run tests, verify fail**
- [ ] **Step 3: Implement provider**

```typescript
// cli/lib/component/provider-agent.ts
import { existsSync } from 'node:fs'
import { readdir, readFile } from 'node:fs/promises'
import { join, relative, basename } from 'node:path'
import { ok, err, CliError, type Result } from '../types'
import type { Component, ComponentType, ComponentProvider, SearchParams, PaginatedResult, ComponentAddOptions, ComponentAddResult, RemoveResult, ProviderCapabilities } from './types'
import { clampLimit, clampPage, emptyPage, paginateArray } from './pagination'

export class LocalAgentProvider implements ComponentProvider {
  readonly id = 'local-agent'
  readonly displayName = 'Local Agents'
  readonly capabilities: ProviderCapabilities = {
    search: ['agent'],
    add: [],
    list: ['agent'],
    remove: [],
    publish: [],
    info: ['agent'],
    outdated: [],
    update: [],
  }

  private readonly agentsDir: string

  constructor(cwd?: string) {
    this.agentsDir = join(cwd ?? process.cwd(), 'context', 'agents')
  }

  // ... discovery logic using glob + frontmatter parsing
  // Exclude: pyproject.toml dirs, README.md, prompt.md, _-prefixed dirs
  // Parse frontmatter with parseFrontmatter from lib/chunker.ts
}
```

Key implementation details:
- Use `readdir({ recursive: true, withFileTypes: true })` or manual recursive walk
- For each `.md` file found, check ancestors for `pyproject.toml` to exclude app agents
- Parse YAML frontmatter using `parseFrontmatter` from `lib/chunker.ts` (already exists)
- Map `tools` string to `tags` array (split on `, `)
- `source` = relative path from project root (e.g., `context/agents/development/core/frontend-developer.md`)

- [ ] **Step 4: Run tests, verify pass**
- [ ] **Step 5: Register in ComponentManager** — update `lib/component/index.ts` comment to show agent provider import pattern
- [ ] **Step 6: Commit**

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Agent dir doesn't exist | Return empty array, no error |
| Frontmatter missing `name` | Derive from filename (strip `.md`) |
| Frontmatter missing `description` | Use empty string |
| Binary files in agent dirs | Skip non-`.md` files |
| Symlinked agent files | Follow symlinks (default `readdir` behavior) |
| Duplicate names across categories | Both included (different `source` paths) |

## Acceptance Criteria

- [ ] `LocalAgentProvider` implements `ComponentProvider`
- [ ] Discovers agents from `context/agents/**/*.md` with correct exclusions
- [ ] Parses YAML frontmatter for name, description, tools
- [ ] Read-only: no add/remove support (agents are hand-authored)
- [ ] At least 13 test cases
- [ ] No external dependencies added
