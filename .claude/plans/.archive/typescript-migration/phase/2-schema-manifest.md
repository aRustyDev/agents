---
id: c4d1eba9-dea5-4b58-af0a-53113a016208
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 2: Schema & Manifest Layer"
status: pending
related:
  depends-on: [1105f062-33cf-4eff-a759-f17fb55296c3]
---

# Phase 2: Schema & Manifest Layer

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** pending
**Effort:** Medium

## Objective

Build the Valibot schema definitions and the lockfile/manifest I/O layer that plugin and skill commands depend on. This establishes the validation and type inference foundation.

## Success Criteria

- [ ] All real `skills-lock.json` files in the repo parse without errors
- [ ] All real `plugin.json` and `plugin.sources.json` files parse without errors
- [ ] Lockfile staleness detection matches Python's `build-plugin.py check` output
- [ ] Schema registry supports registering new lockfile formats without code changes to core
- [ ] All types are inferred from Valibot schemas (no manual type definitions)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Schema definitions | `cli/lib/schemas.ts` | TypeScript |
| Lockfile operations | `cli/lib/lockfile.ts` | TypeScript |
| Manifest I/O | `cli/lib/manifest.ts` | TypeScript |
| Test suites | `cli/test/{schemas,lockfile,manifest}.test.ts` | TypeScript |

## Files

**Create:**
- `cli/lib/schemas.ts`
- `cli/lib/lockfile.ts`
- `cli/lib/manifest.ts`
- `cli/test/schemas.test.ts`
- `cli/test/lockfile.test.ts`
- `cli/test/manifest.test.ts`

**Modify:**
- None

## Tasks

### lib/schemas.ts
- [ ] Define `SkillLockEntry` schema (source, sourceType, computedHash with sha256 regex)
- [ ] Define `PluginLockEntry` schema
- [ ] Define `LockfileV1` schema (version literal, entries record)
- [ ] Define `PluginManifest` schema (name, version, description, author, keywords, etc.)
- [ ] Define `PluginSources` schema (extended format with source, hash, forked, forked_at)
- [ ] Define `SkillFrontmatter` schema (name, description, tags, source)
- [ ] Define `ComponentRecord` schema (id, name, type, description, canonical_url, etc.)
- [ ] Define `StatusMessage` schema (status picklist, message, optional data)
- [ ] Export inferred types: `type PluginManifest = v.InferOutput<typeof PluginManifest>`
- [ ] Write validation tests against real repo files

### lib/lockfile.ts
- [ ] Define `LockfileSchema<T>` interface (name, filename, schema, checkStaleness)
- [ ] Implement schema registry: `registerSchema()`, internal `Map<string, LockfileSchema>`
- [ ] Implement `readLockfile()` — read JSON, validate with registered schema, return Result
- [ ] Implement `writeLockfile()` — serialize with formatting, validate before write
- [ ] Implement `checkStaleness()` — compare computed hashes against lockfile entries
- [ ] Pre-register `skills` and `plugins` schemas
- [ ] Write tests: read real lockfiles, verify staleness against known state

### lib/manifest.ts
- [ ] Implement `readPluginManifest()` — read `.claude-plugin/plugin.json`, validate
- [ ] Implement `readPluginSources()` — read `.claude-plugin/plugin.sources.json`, validate
- [ ] Implement `readSkillFrontmatter()` — parse YAML frontmatter from SKILL.md, validate
- [ ] Implement `detectSourceFormat()` — classify as 'legacy' | 'extended' | 'planning'
- [ ] Implement `normalizeSource()` — convert any format to ExtendedSource
- [ ] Write parity tests: load every plugin manifest in the repo, compare to Python output

## Notes

- Test against real files in `context/plugins/` and `context/skills/`, not just fixtures
- The lockfile schema registry is the extensible pattern — adding a new lockfile type means calling `registerSchema()` with a new schema object
- Three source formats must be supported: legacy (string path), extended (object with hash), planning (object with type/base, no source)
- Staleness detection depends on `lib/hash.ts` from Phase 1
