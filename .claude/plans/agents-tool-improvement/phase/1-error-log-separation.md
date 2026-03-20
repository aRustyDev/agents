# Phase 1: Error Log Separation

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Separate error records from the catalog into an append-only error log file. Catalog entries carry only `attemptCount`, `lastErrorType`, and `retryable` as cached fields. All error detail lives in `.catalog-errors.ndjson`.

## Success Criteria

- [ ] `ErrorRecord` type defined with full error schema (source, skill, runId, batchId, timestamp, errorType, errorDetail, errorCode, retryable)
- [ ] `appendError`, `appendErrors`, `readErrorLog`, `getErrorsForSkill` functions in `catalog.ts`
- [ ] `appendErrors` uses a single `writeFileSync` call with all lines concatenated (concurrent-safe for parallel workers)
- [ ] `Tier1Result` type updated: `error`/`errorDetail`/`errorCode` removed, `attemptCount`/`lastErrorType`/`retryable` added
- [ ] `mergeTier1Results` signature updated to `(catalogPath, errorLogPath, results)` — merge function is the single authority for routing successes to catalog and failures to error log
- [ ] On success: clears error cache fields, resets `attemptCount` to 0
- [ ] On failure: appends `ErrorRecord` to error log, increments `attemptCount`, caches `lastErrorType`/`retryable`
- [ ] `catalog errors` CLI reads from `.catalog-errors.ndjson`
- [ ] `catalog errors --prune` removes resolved errors
- [ ] `.catalog-errors.ndjson` added to `context/skills/.gitignore`
- [ ] All existing tests still pass, new tests for error log functions

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Error log types + functions | `.scripts/lib/catalog.ts` | TypeScript |
| Updated merge function | `.scripts/lib/catalog.ts` | TypeScript |
| Updated errors CLI | `.scripts/commands/skill.ts` | TypeScript |
| Error log tests | `.scripts/test/catalog-tier1.test.ts` | TypeScript |
| Gitignore update | `context/skills/.gitignore` | Text |

## Files

**Create:**
- None (error log file created at runtime)

**Modify:**
- `.scripts/lib/catalog.ts` — `ErrorRecord` type, error log functions, update `Tier1Result`, update `mergeTier1Results` signature and implementation
- `.scripts/commands/skill.ts` — update `processBatch` to pass `errorLogPath` to merge, update `catalog errors` subcommand, add `--prune` flag
- `.scripts/test/catalog-tier1.test.ts` — tests for error log append/read, merge success-clears-errors, merge failure-increments-attemptCount, merge routes errors to log
- `context/skills/.gitignore` — add `.catalog-errors.ndjson`

## Tasks

- [ ] Define `ErrorRecord` interface in `catalog.ts`
- [ ] Implement `appendError(path, error)` — append single NDJSON line
- [ ] Implement `appendErrors(path, errors[])` — concatenate all lines into a single string, write with one `writeFileSync` call (concurrent-safe: single write = atomic at OS level for small payloads)
- [ ] Implement `readErrorLog(path)` — read all records
- [ ] Implement `getErrorsForSkill(path, source, skill)` — filter by skill
- [ ] Update `Tier1Result`: remove `error`/`errorDetail`/`errorCode`, add `attemptCount`/`lastErrorType`/`retryable`
- [ ] Update `mergeTier1Results` signature: `(catalogPath: string, errorLogPath: string, results: Tier1Result[]) => void`
  - Internally splits results into successes (has `wordCount`) and failures (no `wordCount`)
  - Successes: merge into catalog, clear error cache fields, reset `attemptCount` to 0
  - Failures: convert to `ErrorRecord[]`, call `appendErrors` to write to error log, merge into catalog with incremented `attemptCount` and cached `lastErrorType`/`retryable`
  - This makes `mergeTier1Results` the single authority for catalog + error log state coordination
- [ ] Update all `mergeTier1Results` call sites to pass `errorLogPath`
- [ ] Update `catalog errors` CLI to read from `.catalog-errors.ndjson`
- [ ] Add `--prune` flag to `catalog errors`: remove records for skills with `attemptCount == 0` in catalog
- [ ] Add `.catalog-errors.ndjson` to `context/skills/.gitignore`
- [ ] Write tests for all error log functions
- [ ] Write tests for merge behavior (success clears, failure increments, failures routed to error log)
- [ ] Write test for concurrent-safe append (verify single `writeFileSync` call pattern)

## Notes

- `DownloadResult` retains transient error fields — these are internal to the orchestrator and passed through to `mergeTier1Results`, which routes them to the error log
- `lastErrorType` and `retryable` on the catalog entry are a performance cache to avoid reading the full error log on every `filterForProcessing` call
- Old entries without `attemptCount` are treated as `attemptCount: 0` (backward compatible)
- The merge function is self-contained: callers pass results (successes + failures), the merge function decides what goes to the catalog vs error log. This prevents caller-level bugs where errors aren't logged or `attemptCount` isn't incremented.
