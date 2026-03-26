# Phase 2: Content Parsing to SDK

## Goal

Move content-parsing leaf modules (`manifest.ts`, `lockfile.ts`, `taxonomy.ts`, `init-component.ts`) into the SDK, establishing the foundation that Phases 3 and 5 depend on.

## Non-Goals

- Restructuring the SDK's existing context layer.
- Changing manifest or lockfile schemas.
- Adding new frontmatter fields.
- Moving `chunker.ts` (already in `@agents/kg` after Phase 1).

## Prerequisites

- **Phase 1 complete** (or at least the chunker shim in place), because `manifest.ts` imports `parseFrontmatter` from `chunker.ts`. After Phase 1, this becomes `@agents/kg/chunker`. In Phase 2 we switch it to `@agents/sdk/context/frontmatter` instead.

## Files

### Move (cli/src/lib/ -> packages/sdk/src/)

| Source | Destination | Lines | Notes |
|--------|-------------|-------|-------|
| `manifest.ts` (307) | `sdk/src/context/manifest.ts` | 307 | Skill frontmatter + plugin manifest reading |
| `lockfile.ts` (366) | `sdk/src/providers/local/lockfile.ts` | 366 | Lockfile schema, read/write operations |
| `taxonomy.ts` (770) | `sdk/src/context/taxonomy.ts` | 770 | Skill categorization with YAML taxonomy data |
| `init-component.ts` (65) | `sdk/src/context/scaffold.ts` | 65 | Component scaffolding (init templates) |

### Modify

| File | Change |
|------|--------|
| `sdk/src/context/manifest.ts` (new) | Replace `import { parseFrontmatter } from './chunker'` with `import { parseFrontmatter } from './frontmatter'` |
| `sdk/src/context/manifest.ts` (new) | Replace `CliError` with `SdkError` |
| `sdk/src/providers/local/lockfile.ts` (new) | Replace `CliError` with `SdkError` |
| `sdk/src/context/index.ts` | Add re-exports for manifest, taxonomy, scaffold |
| `sdk/src/providers/local/index.ts` | Add re-export for lockfile |
| `sdk/package.json` | No dep changes needed (js-yaml already present) |
| `cli/src/commands/init.ts` | Update import from `'../lib/init-component'` to `'@agents/sdk/context/scaffold'` |
| `cli/src/commands/plugin.ts` | Update import from `'../lib/manifest'` to `'@agents/sdk/context/manifest'` |
| `cli/src/commands/add.ts` | Update lockfile import to `'@agents/sdk/providers/local/lockfile'` |
| `cli/src/lib/skill-discovery.ts` | Update `import { readSkillFrontmatter } from './manifest'` to `'@agents/sdk/context/manifest'` |
| `cli/src/lib/skill-info.ts` | Update manifest + lockfile imports |
| `cli/src/lib/skill-outdated.ts` | Update lockfile import |
| `cli/src/lib/plugin-ops.ts` | Update manifest import if it uses it |

### Delete (after consumers updated)

| File | Lines |
|------|-------|
| `packages/cli/src/lib/manifest.ts` | 307 |
| `packages/cli/src/lib/lockfile.ts` | 366 |
| `packages/cli/src/lib/taxonomy.ts` | 770 |
| `packages/cli/src/lib/init-component.ts` | 65 |

## Steps

- [ ] **2.1** Copy `manifest.ts` to `packages/sdk/src/context/manifest.ts`.
- [ ] **2.2** In the SDK copy, replace the chunker import:

  ```typescript
  // Before
  import { parseFrontmatter } from './chunker'
  // After
  import { parseFrontmatter } from './frontmatter'
  ```

  The SDK already has `context/frontmatter.ts` with a `parseFrontmatter` function. Verify the signatures are compatible:
  - KG chunker version: `parseFrontmatter(raw: string): { frontmatter: Record<string, unknown>; content: string }`
  - SDK frontmatter version: `parseFrontmatter(content: string): { attrs: Record<string, unknown>; body: string }`
  - **They differ in return shape!** The SDK version returns `{ attrs, body }` while chunker returns `{ frontmatter, content }`. The manifest module uses the chunker version's field names. Two options:
    - (a) Add an adapter in manifest.ts that maps attrs->frontmatter, body->content.
    - (b) Add the chunker's version of `parseFrontmatter` directly to `sdk/context/frontmatter.ts`.
  - **Decision: Option (b).** Add the chunker's `parseFrontmatter` signature to the SDK frontmatter module as `parseMarkdownFrontmatter` (with the `{ frontmatter, content }` return shape), keeping the existing `parseFrontmatter` for backward compatibility. Then manifest imports `parseMarkdownFrontmatter`.
- [ ] **2.3** Replace `CliError` with `SdkError` in the SDK copy of manifest.ts:

  ```typescript
  // Before
  import { CliError, err, ok, type Result } from '@agents/core/types'
  // After
  import { err, ok, type Result } from '@agents/core/types'
  import { SdkError } from '../util/errors'
  ```

  Update all `new CliError(...)` to `new SdkError(...)` with appropriate codes.
- [ ] **2.4** Copy `lockfile.ts` to `packages/sdk/src/providers/local/lockfile.ts`.
- [ ] **2.5** Update lockfile.ts imports for SDK context:
  - `CliError` -> `SdkError`
  - Schema imports (`PluginSourcesManifest`, `LockfileV1`) are already from `@agents/sdk` -- change to relative imports since we are now inside SDK.

  ```typescript
  // Before
  import { PluginSourcesManifest } from '@agents/sdk/context/plugin/schema'
  import { LockfileV1 } from '@agents/sdk/providers/local/schemas'
  // After
  import { PluginSourcesManifest } from '../../context/plugin/schema'
  import { LockfileV1 } from './schemas'
  ```

- [ ] **2.6** Copy `taxonomy.ts` to `packages/sdk/src/context/taxonomy.ts`.
- [ ] **2.7** Update taxonomy.ts imports -- it uses `@agents/core/runtime` and `js-yaml`, both available in SDK.
- [ ] **2.8** Copy `init-component.ts` to `packages/sdk/src/context/scaffold.ts`.
- [ ] **2.9** Update scaffold.ts imports:

  ```typescript
  // Before
  import { type ComponentType, getComponentMeta } from '@agents/sdk/context/types'
  // After
  import { type ComponentType, getComponentMeta } from './types'
  ```

- [ ] **2.10** Update `packages/sdk/src/context/frontmatter.ts` -- add the chunker-compatible parse function:

  ```typescript
  /** Chunker-compatible frontmatter parser (returns { frontmatter, content } shape). */
  export function parseMarkdownFrontmatter(raw: string): {
    frontmatter: Record<string, unknown>
    content: string
  } {
    const { attrs, body } = parseFrontmatter(raw)
    return { frontmatter: attrs, content: body }
  }
  ```

- [ ] **2.11** Update SDK barrel exports:
  - `sdk/src/context/index.ts`: Add exports for manifest, taxonomy, scaffold.
  - `sdk/src/providers/local/index.ts`: Add export for lockfile.
- [ ] **2.12** Update `sdk/package.json` exports map if needed (add `./context/manifest`, `./context/taxonomy`, `./context/scaffold`, `./providers/local/lockfile`).
- [ ] **2.13** Update all CLI consumers (commands and remaining lib files) to import from SDK:
  - `commands/plugin.ts`: `import { readPluginManifest } from '@agents/sdk/context/manifest'`
  - `commands/add.ts`: `import { readLockfile, writeLockfile } from '@agents/sdk/providers/local/lockfile'`
  - `commands/init.ts`: `import { initComponent } from '@agents/sdk/context/scaffold'`
  - `lib/skill-discovery.ts`: `import { readSkillFrontmatter } from '@agents/sdk/context/manifest'`
  - `lib/skill-info.ts`: Update manifest and lockfile imports.
  - `lib/skill-outdated.ts`: Update lockfile import.
  - `lib/catalog-download.ts`: Check for lockfile/manifest imports and update.
- [ ] **2.14** Run `bun test --cwd packages/sdk` -- expect 382+ pass / 0 fail.
- [ ] **2.15** Run `bun test --cwd packages/cli` -- expect 1684 pass / 10 fail.
- [ ] **2.16** Delete the 4 source files from `cli/src/lib/`.
- [ ] **2.17** Run test suite again to confirm clean deletion.

## Acceptance Criteria

1. `packages/sdk/src/context/manifest.ts` exists and exports `readSkillFrontmatter`, `readPluginManifest`.
2. `packages/sdk/src/providers/local/lockfile.ts` exists and exports `readLockfile`, `writeLockfile`.
3. `packages/sdk/src/context/taxonomy.ts` exists and exports taxonomy functions.
4. `packages/sdk/src/context/scaffold.ts` exists and exports `initComponent`.
5. No `CliError` usage in any SDK file -- all use `SdkError`.
6. SDK tests pass: 382+ / 0.
7. CLI tests unchanged: 1684 / 10.
8. `cli/src/lib/` no longer contains: `manifest.ts`, `lockfile.ts`, `taxonomy.ts`, `init-component.ts`.
9. `manifest.ts` in SDK does NOT import from `@agents/kg` -- it uses `@agents/sdk/context/frontmatter`.

## Failure Criteria

- **Stop if:** The `parseFrontmatter` signature mismatch causes widespread test failures. In that case, keep the chunker version's exact signature in the SDK frontmatter module rather than introducing an adapter.
- **Stop if:** Lockfile's import of `PluginSourcesManifest` creates a circular dependency within SDK. Resolve by moving the schema to a shared types file.

## Fallback Logic

1. If `manifest.ts` is too tightly coupled to chunker's `parseFrontmatter`, temporarily add a direct copy of the function to manifest.ts itself (inline it) rather than creating a cross-package dependency on `@agents/kg`.
2. If `taxonomy.ts` has runtime dependencies on the CLI's working directory that break in SDK context, keep it in CLI and mark it as "CLI-only" in the plan. Update the file count accordingly.
3. Leave re-export shims in `cli/src/lib/` if too many consumers are hard to update simultaneously:

   ```typescript
   // cli/src/lib/manifest.ts (shim)
   export * from '@agents/sdk/context/manifest'
   ```

## Examples

### Before (cli/src/lib/manifest.ts)

```typescript
import { CliError, err, ok, type Result, type SourceFormat } from '@agents/core/types'
import { SkillFrontmatter } from '@agents/sdk/context/skill/schema'
import * as v from 'valibot'
import { parseFrontmatter } from './chunker'

export async function readSkillFrontmatter(skillDir: string): Promise<Result<SkillFrontmatter>> {
  // ...
}
```

### After (sdk/src/context/manifest.ts)

```typescript
import { err, ok, type Result, type SourceFormat } from '@agents/core/types'
import { SdkError } from '../util/errors'
import { SkillFrontmatter } from './skill/schema'
import * as v from 'valibot'
import { parseMarkdownFrontmatter } from './frontmatter'

export async function readSkillFrontmatter(skillDir: string): Promise<Result<SkillFrontmatter>> {
  // ... (same logic, SdkError instead of CliError)
}
```

### Before (cli/src/lib/skill-info.ts)

```typescript
import { readLockfile } from './lockfile'
import { readSkillFrontmatter } from './manifest'
```

### After (cli/src/lib/skill-info.ts, during Phase 2)

```typescript
import { readLockfile } from '@agents/sdk/providers/local/lockfile'
import { readSkillFrontmatter } from '@agents/sdk/context/manifest'
```

## Dependency Notes

- **manifest.ts -> chunker.ts:** This is the key cross-phase dependency. Phase 1 moves chunker to `@agents/kg`. Phase 2 breaks that link by using `sdk/context/frontmatter` instead. If Phase 1 has not run, the shim in `cli/src/lib/chunker.ts` still provides `parseFrontmatter`.
- **lockfile.ts -> sdk schemas:** Lockfile already imports from `@agents/sdk`. Moving it into SDK converts these to relative imports -- simpler, no circular risk.
- **skill-discovery.ts -> manifest.ts:** After Phase 2, skill-discovery imports from `@agents/sdk/context/manifest`. This prepares it for Phase 5 where skill-discovery itself moves to SDK.
- **skill-outdated.ts -> lockfile.ts:** Same pattern -- after Phase 2, outdated imports from `@agents/sdk/providers/local/lockfile`.
