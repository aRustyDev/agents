# Phase 2: Mechanical Compute Functions

**ID:** `phase-2`
**Dependencies:** None
**Status:** pending
**Effort:** Small

## Objective

Implement native TypeScript functions for mechanical analysis (content hash, word count, section count, heading tree, file count) that replace shell-out operations and LLM-delegated computation. These are deterministic, zero-dependency functions using Bun APIs.

## Success Criteria

- [ ] `computeContentHash(content)` returns `sha256:<hex>` using `Bun.CryptoHasher`
- [ ] `computeWordCount(content)` returns word count via whitespace split
- [ ] `computeSectionCount(content)` returns count of `#` through `######` headings
- [ ] `computeHeadingTree(content)` returns `Array<{ depth, title }>` from headings
- [ ] `computeFileCount(dir)` returns recursive file count, handles nonexistent dirs gracefully
- [ ] All functions exported from `catalog.ts`
- [ ] `DownloadResult` type expanded with `contentHash`, `wordCount`, `fileCount`, `sectionCount`, `headingTree`
- [ ] Tests verify output matches shell equivalents for known skills

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| 5 compute functions | `cli/lib/catalog.ts` | TypeScript |
| Updated `DownloadResult` type | `cli/lib/catalog.ts` | TypeScript |
| Compute function tests | `cli/test/catalog-tier1.test.ts` | TypeScript |

## Files

**Create:**

- None

**Modify:**

- `cli/lib/catalog.ts` — add 5 exported compute functions, expand `DownloadResult` type
- `cli/test/catalog-tier1.test.ts` — tests for each compute function including edge cases (empty content, nonexistent dir, headings at various depths)

## Tasks

- [ ] Implement `computeContentHash(content: string): string`
- [ ] Implement `computeWordCount(content: string): number`
- [ ] Implement `computeSectionCount(content: string): number`
- [ ] Implement `computeHeadingTree(content: string): Array<{ depth: number; title: string }>`
- [ ] Implement `computeFileCount(dir: string): number` with try/catch for missing dirs
- [ ] Export all 5 functions
- [ ] Expand `DownloadResult` type with mechanical fields
- [ ] Write tests: verify against known skill files (e.g., `context/skills/beads/SKILL.md`)
- [ ] Write edge case tests: empty string, no headings, deeply nested dirs, nonexistent path

## Notes

- These functions are independent of Phase 1 and can be built in parallel
- `computeHeadingTree` is also mechanical (parsing headings) — moved out of the agent alongside `computeSectionCount`
- All functions are synchronous — no async needed for local file operations
- `Bun.CryptoHasher` is Bun-specific but is the native API; no `node:crypto` import needed
