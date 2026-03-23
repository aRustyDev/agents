# Phase 1: Schema & Data Model Evolution

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Evolve the catalog data model to support repo-level tracking, enhanced component metadata, and cleaner error classification. All changes are additive — existing entries remain valid.

## Success Criteria

- [ ] `RepoManifest` type defined with all repo-level fields
- [ ] `.catalog-repos.ndjson` file format established
- [ ] `CatalogEntryWithTier1` extended with `discoveredPath`, `lastSeenAt`, `lastSeenHeadSha`, `movedFrom`, `skillSizeBytes`, `lineCount`, `sectionMap`, `fileTree`, `isSimple`
- [ ] `source_invalid` renamed to `invalid_source_entry` with structured detail
- [ ] `batch_failed` entries re-attempted and reclassified (target: 0 remaining)
- [ ] Orphaned state transitions removed from code and diagram
- [ ] Existing tests pass; new tests for schema changes
- [ ] Migration script backfills `invalid_source_entry` rename on existing entries

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| RepoManifest type | `cli/lib/catalog.ts` | TypeScript interface |
| Enhanced Tier1Result fields | `cli/lib/catalog.ts` | TypeScript interface additions |
| Error type rename | `cli/lib/catalog.ts` | Type union update |
| Repo manifest reader/writer | `cli/lib/catalog.ts` | Functions |
| Migration script | `cli/lib/catalog.ts` | `migrateCatalogSchema()` function |
| Schema tests | `cli/test/catalog-schema.test.ts` | bun:test |

## Files

**Create:**
- `cli/test/catalog-schema.test.ts`

**Modify:**
- `cli/lib/catalog.ts` — types, reader/writer for repo manifest, error rename
- `cli/lib/catalog-download.ts` — use new error type name
- `cli/lib/catalog-stale.ts` — use new types
- `cli/commands/skill.ts` — migration command, error type references

## Tasks

- [ ] Define `RepoManifest` interface (repo, clonedAt, headSha, totalFiles, repoSizeBytes, archived, lastCommitAt, commitCount, contributorCount, skillCount, skills[])
- [ ] Define `ComponentMetadata` interface (discoveredPath, lastSeenAt, lastSeenHeadSha, movedFrom, skillSizeBytes, lineCount, sectionMap, fileTree, isSimple)
- [ ] Add `ComponentMetadata` fields to `Tier1Result` (all optional)
- [ ] Rename `source_invalid` → `invalid_source_entry` in `Tier1ErrorType` union
- [ ] Add `readRepoManifest()` / `writeRepoManifest()` functions
- [ ] Add `sectionMap` computation: `computeSectionMap(content): Array<{heading, line}>`
- [ ] Add `computeLineCount(content): number`
- [ ] Add `computeFileTree(dir): string[]`
- [ ] Add `computeSkillSizeBytes(dir): number`
- [ ] Add `isSimpleSkill(dir): boolean` (true if SKILL.md only, no subdirs)
- [ ] Re-run 458 `batch_failed` entries with `--retry-errors` to reclassify
- [ ] Write migration function that renames `source_invalid` → `invalid_source_entry` on all existing entries
- [ ] Remove orphaned `AgentAnalysis → BatchFailed` transition from state diagram
- [ ] Write tests for all new compute functions
- [ ] Write tests for repo manifest read/write

## Notes

- All new fields on `Tier1Result` are optional — existing entries without them are valid
- The `RepoManifest` is a separate file (`.catalog-repos.ndjson`) to avoid bloating the per-skill catalog
- `sectionMap` is similar to `headingTree` but includes line numbers for precise navigation
- `isSimple` = true when the skill directory contains only SKILL.md (no resources, no subdirs)
