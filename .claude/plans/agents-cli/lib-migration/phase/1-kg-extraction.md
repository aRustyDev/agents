# Phase 1: Extract @agents/kg (Knowledge Graph)

## Goal

Create a new `packages/kg/` workspace package containing all knowledge-graph modules: graph construction, schema validation, file locking, embedding, search indexing, and markdown chunking.

## Non-Goals

- Moving Python files (`chunker.py`, `embedder.py`) -- they stay in `cli/src/lib/`.
- Changing chunking algorithms or embedding behavior.
- Adding new KG features.
- Wiring KG into the SDK catalog system (that is a future concern beyond this migration).

## Prerequisites

- None. This phase has no blockers -- KG modules are self-contained and only consumed by CLI commands and the graph-viewer server.

## Files

### Create (new package scaffold)

| File | Description |
|------|-------------|
| `packages/kg/package.json` | Package manifest with KG-specific deps |
| `packages/kg/tsconfig.json` | TypeScript config extending root |
| `packages/kg/src/index.ts` | Barrel re-exports |
| `packages/kg/src/graph.ts` | Graph construction (from `cli/src/lib/graph.ts`, 202 lines) |
| `packages/kg/src/graph-schema.ts` | JSON Schema validation (from `cli/src/lib/graph-schema.ts`, 121 lines) |
| `packages/kg/src/graph-lock.ts` | File-based graph locking (from `cli/src/lib/graph-lock.ts`, 158 lines) |
| `packages/kg/src/embedder.ts` | Ollama embedding client (from `cli/src/lib/embedder.ts`, 59 lines) |
| `packages/kg/src/meilisearch.ts` | Meilisearch client wrapper (from `cli/src/lib/meilisearch.ts`, 478 lines) |
| `packages/kg/src/chunker.ts` | Markdown chunking + frontmatter (from `cli/src/lib/chunker.ts`, 364 lines) |
| `packages/kg/test/chunker.test.ts` | Unit tests for chunker |
| `packages/kg/test/graph.test.ts` | Unit tests for graph construction |
| `packages/kg/test/embedder.test.ts` | Unit tests for embedder |

### Modify (update imports)

| File | Change |
|------|--------|
| `packages/cli/src/commands/kg.ts` | Change `from '../lib/chunker'` to `from '@agents/kg/chunker'`, etc. |
| `packages/cli/src/server/graph-viewer/routes/*.ts` | Change `from '../../lib/graph'` to `from '@agents/kg/graph'`, etc. |
| `packages/cli/package.json` | Add `"@agents/kg": "workspace:*"` dependency |
| `root package.json` | Add `packages/kg` to workspaces array |

### Delete (after consumers updated)

| File | Lines |
|------|-------|
| `packages/cli/src/lib/graph.ts` | 202 |
| `packages/cli/src/lib/graph-schema.ts` | 121 |
| `packages/cli/src/lib/graph-lock.ts` | 158 |
| `packages/cli/src/lib/embedder.ts` | 59 |
| `packages/cli/src/lib/meilisearch.ts` | 478 |
| `packages/cli/src/lib/chunker.ts` | 364 |

## Steps

- [ ] **1.1** Create `packages/kg/` directory structure.
- [ ] **1.2** Write `packages/kg/package.json`:

  ```json
  {
    "name": "@agents/kg",
    "version": "0.1.0",
    "private": true,
    "type": "module",
    "exports": {
      ".": "./src/index.ts",
      "./*": "./src/*.ts"
    },
    "dependencies": {
      "@agents/core": "workspace:*",
      "ajv": "^8.18.0",
      "ajv-formats": "^3.0.1",
      "graphology": "^0.26.0",
      "graphology-layout": "^0.6.1",
      "graphology-layout-forceatlas2": "^0.10.1",
      "js-yaml": "^4.1.0",
      "meilisearch": "^0.56.0",
      "ollama": "^0.5.0"
    }
  }
  ```

- [ ] **1.3** Write `packages/kg/tsconfig.json` extending root tsconfig.
- [ ] **1.4** Copy the 6 source files from `cli/src/lib/` to `packages/kg/src/`.
- [ ] **1.5** Update imports in each copied file:
  - `chunker.ts`: `@agents/core/runtime` stays (cross-package import is fine).
  - `meilisearch.ts`: `@agents/core/types` stays.
  - `graph.ts`, `graph-schema.ts`, `graph-lock.ts`: No external package imports to change (only node built-ins and direct deps).
  - `embedder.ts`: Only imports `ollama` -- no changes.
- [ ] **1.6** Replace `CliError` with a KG-specific error type in meilisearch.ts:

  ```typescript
  // Before
  import { CliError } from '@agents/core/types'
  // After
  import { CliError } from '@agents/core/types'  // Keep CliError for now -- it's from core, not CLI
  ```

  Note: `CliError` is actually defined in `@agents/core/types`, not in the CLI package. It can be used anywhere. No change needed in Phase 1; error code rename happens in Phase 6 cleanup.
- [ ] **1.7** Write `packages/kg/src/index.ts` barrel:

  ```typescript
  export * from './chunker'
  export * from './embedder'
  export * from './graph'
  export * from './graph-lock'
  export * from './graph-schema'
  export * from './meilisearch'
  ```

- [ ] **1.8** Add `"@agents/kg": "workspace:*"` to `packages/cli/package.json` dependencies.
- [ ] **1.9** Add `"packages/kg"` to root `package.json` workspaces.
- [ ] **1.10** Run `bun install` from root to link the new workspace package.
- [ ] **1.11** Update `packages/cli/src/commands/kg.ts` imports:

  ```typescript
  // Before
  import { chunkMarkdown, parseFrontmatter } from '../lib/chunker'
  import { embed } from '../lib/embedder'
  import { createClient, searchKeyword } from '../lib/meilisearch'
  // After
  import { chunkMarkdown, parseFrontmatter } from '@agents/kg/chunker'
  import { embed } from '@agents/kg/embedder'
  import { createClient, searchKeyword } from '@agents/kg/meilisearch'
  ```

- [ ] **1.12** Update `packages/cli/src/server/graph-viewer/routes/*.ts` imports similarly.
- [ ] **1.13** Update any other CLI files that import from the 6 moved modules (search with `grep`).
- [ ] **1.14** Write tests for `packages/kg/test/`:
  - `chunker.test.ts`: Test `parseFrontmatter`, `chunkMarkdown` with sample markdown.
  - `graph.test.ts`: Test graph construction from mock data.
  - `embedder.test.ts`: Test embed function signature (mock Ollama).
- [ ] **1.15** Run full test suite:
  - `bun test --cwd packages/kg` -- all new tests pass.
  - `bun test --cwd packages/cli` -- 1684 pass / 10 fail (unchanged).
- [ ] **1.16** Delete the 6 source files from `cli/src/lib/`.
- [ ] **1.17** Run CLI test suite again to confirm no regressions.

## Acceptance Criteria

1. `packages/kg/` exists with `package.json`, `tsconfig.json`, `src/`, and `test/`.
2. `bun test --cwd packages/kg` passes with at least 6 test cases.
3. `bun test --cwd packages/cli` maintains 1684 pass / 10 fail.
4. No file in `packages/cli/src/lib/` imports from `packages/kg/src/` via relative path.
5. `packages/cli/src/lib/` no longer contains: `graph.ts`, `graph-schema.ts`, `graph-lock.ts`, `embedder.ts`, `meilisearch.ts`, `chunker.ts`.
6. `bun run packages/cli/src/bin/agents.ts kg --help` still works.

## Failure Criteria

- **Stop if:** Moving `chunker.ts` breaks `manifest.ts` (Phase 2 dependency). In that case, leave a re-export shim in `cli/src/lib/chunker.ts`:

  ```typescript
  export { parseFrontmatter, chunkMarkdown, type Chunk, type ParsedMarkdown } from '@agents/kg/chunker'
  ```

  This shim allows Phase 1 to complete independently. Phase 2 will update `manifest.ts` to import from `@agents/kg/chunker` or `@agents/sdk/context/frontmatter` directly.

- **Stop if:** Graph-viewer server fails to start after import changes. Debug the import path resolution in Bun's module system before proceeding.

## Fallback Logic

1. If any moved module fails to resolve via `@agents/kg/*`, check that `packages/kg/package.json` exports map is correct and that `bun install` was re-run.
2. If Ollama types cause issues in `embedder.ts`, add `ollama` to `@agents/kg` devDependencies and use dynamic import.
3. If test count drops, diff the test output against the baseline and identify which tests regressed -- do not proceed to Phase 2 until resolved.

## Test Files

Move corresponding test files from `packages/cli/test/` to `packages/kg/test/`:
- `chunker.test.ts` --> `packages/kg/test/chunker.test.ts`
- `graph.test.ts` --> `packages/kg/test/graph.test.ts`

Update imports in moved tests to use `@agents/kg/*` paths. If tests have CLI-specific fixtures, keep them in CLI and update imports to point to `@agents/kg`.

## Dependency Notes

- `chunker.ts` is imported by `manifest.ts` (for `parseFrontmatter`). After Phase 1 moves chunker to `@agents/kg`, `manifest.ts` temporarily imports from `@agents/kg/chunker`. Phase 2 resolves this by switching manifest to use `@agents/sdk/context/frontmatter.parseFrontmatter` instead, removing the cross-package KG dependency from the content-parsing layer.
- `meilisearch.ts` is imported by `skill-search-api.ts` (Phase 5). After Phase 1, skill-search-api imports from `@agents/kg/meilisearch`. Phase 6 may move search to SDK, at which point the import path updates again.
- Graph modules are only consumed by `commands/kg.ts` and `server/graph-viewer/` -- no transitive dependency concerns.

## Examples

### Before (cli/src/commands/kg.ts)

```typescript
import { chunkMarkdown, parseFrontmatter } from '../lib/chunker'
import { embed } from '../lib/embedder'
import { buildGraph } from '../lib/graph'
```

### After (cli/src/commands/kg.ts)

```typescript
import { chunkMarkdown, parseFrontmatter } from '@agents/kg/chunker'
import { embed } from '@agents/kg/embedder'
import { buildGraph } from '@agents/kg/graph'
```

### Before (cli/src/lib/manifest.ts)

```typescript
import { parseFrontmatter } from './chunker'
```

### After Phase 1 (temporary -- resolved in Phase 2)

```typescript
import { parseFrontmatter } from '@agents/kg/chunker'
```

### packages/kg/package.json (new)

```json
{
  "name": "@agents/kg",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./src/index.ts",
    "./*": "./src/*.ts"
  },
  "dependencies": {
    "@agents/core": "workspace:*",
    "ajv": "^8.18.0",
    "ajv-formats": "^3.0.1",
    "graphology": "^0.26.0",
    "graphology-layout": "^0.6.1",
    "graphology-layout-forceatlas2": "^0.10.1",
    "js-yaml": "^4.1.0",
    "meilisearch": "^0.56.0",
    "ollama": "^0.5.0"
  }
}
```
