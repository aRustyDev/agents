# Phase 3: Incremental Skip + Retry

**ID:** `phase-3`
**Dependencies:** phase-1
**Status:** pending
**Effort:** Medium

## Objective

Make `analyze` skip already-analyzed skills by default and add `--retry-errors` flag for targeted retry of failed skills. Implement `filterForProcessing` to replace `filterAvailable` with awareness of `attemptCount`, `retryable`, and availability.

## Success Criteria

- [ ] `filterForProcessing(catalog, opts)` replaces `filterAvailable(entries)` in the analyze command
- [ ] Default behavior skips entries with `wordCount` AND `attemptCount == 0`
- [ ] Default behavior includes unattempted entries + retryable under attempt limit
- [ ] `--force` flag processes everything regardless of state
- [ ] `--retry-errors` flag processes only retryable entries (not unattempted)
- [ ] `--retry-errors --force` processes all entries with `attemptCount > 0`, ignores attempt limit
- [ ] Progress output shows skip/process breakdown
- [ ] Availability filtering preserved (only `available` entries processed)
- [ ] Permanently skips: `attemptCount >= 2` OR `retryable == false`

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| `filterForProcessing` function | `.scripts/lib/catalog.ts` | TypeScript |
| Updated CLI args | `.scripts/commands/skill.ts` | TypeScript |
| Progress output | `.scripts/commands/skill.ts` | TypeScript |
| Filter tests | `.scripts/test/catalog-tier1.test.ts` | TypeScript |

## Files

**Create:**
- None

**Modify:**
- `.scripts/lib/catalog.ts` — add `filterForProcessing` function
- `.scripts/commands/skill.ts` — replace `filterAvailable` call with `filterForProcessing`, add `--retry-errors` flag, update progress output, update `--force` flag semantics
- `.scripts/test/catalog-tier1.test.ts` — tests for all flag combinations and edge cases

## Tasks

- [ ] Implement `filterForProcessing(catalog, opts)` in `catalog.ts`
  - First filter by `availability === 'available'`
  - If `opts.force`: return all available
  - If `opts.retryErrors`: return entries with `attemptCount > 0` AND (`retryable === true` OR `opts.force`) AND (`attemptCount < 2` OR `opts.force`)
  - Default: return entries with no `wordCount`, OR (`attemptCount > 0` AND `attemptCount < 2` AND `retryable === true`)
- [ ] Add `--retry-errors` CLI flag to analyze command
- [ ] Update `--force` flag behavior: process everything, ignore attemptCount/retryable
- [ ] Replace `filterAvailable(allEntries)` with `filterForProcessing(allEntries, { force, retryErrors })`
- [ ] Add progress output showing skip/process breakdown
- [ ] Write tests for default behavior (skip analyzed, include unattempted + retryable)
- [ ] Write tests for `--force` (all available entries)
- [ ] Write tests for `--retry-errors` (only retryable)
- [ ] Write tests for `--retry-errors --force` (all errored, ignore limits)
- [ ] Write tests for permanent skip (attemptCount >= 2, retryable false)
- [ ] Write tests for backward compatibility (entries without attemptCount treated as 0)

## Notes

- This phase depends on Phase 1 because it uses `attemptCount` and `retryable` fields that Phase 1 adds to the catalog entry type
- `filterForProcessing` works entirely from catalog entry fields — it does NOT read the error log
- The old `filterAvailable` function can remain as a simpler utility but is no longer called from the analyze command
