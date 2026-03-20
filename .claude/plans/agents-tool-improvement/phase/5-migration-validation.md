# Phase 5: Migration + Validation

**ID:** `phase-5`
**Dependencies:** phase-1, phase-2, phase-3, phase-4
**Status:** pending
**Effort:** Small

## Objective

Implement the `catalog scrub` backfill command, run it to clean existing data, validate the full pipeline end-to-end with a test batch, and update related subcommands (`cleanup`, `forks`, `summary`) for the new data model.

## Success Criteria

- [ ] `catalog scrub` command implemented with lock file protection
- [ ] `catalog scrub --dry-run` outputs a full change report without modifying files
- [ ] Scrub correctly separates error data from catalog entries
- [ ] After scrub: 0 entries with both `wordCount` AND `error` fields
- [ ] After scrub: all error-only entries have `attemptCount: 1` and errors in `.catalog-errors.ndjson`
- [ ] `catalog cleanup` works with new data model
- [ ] `catalog forks` works with new data model
- [ ] `catalog summary` shows `attemptCount` distribution
- [ ] Test batch with `--force --limit 1 --batch-size 5` produces clean results with new pipeline
- [ ] `validateBatchResults` reports 0 issues on test batch
- [ ] `catalog errors` shows correct breakdown from error log
- [ ] `catalog summary` reports accurate counts
- [ ] All tests pass (no hardcoded test count — just `bun test` with 0 failures)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| `catalog scrub` subcommand | `.scripts/commands/skill.ts` | TypeScript |
| Updated `catalog cleanup` | `.scripts/commands/skill.ts` | TypeScript |
| Updated `catalog forks` | `.scripts/commands/skill.ts` | TypeScript |
| Updated `catalog summary` | `.scripts/commands/skill.ts` | TypeScript |
| Backfilled catalog | `context/skills/.catalog.ndjson` | NDJSON (gitignored) |
| Backfilled error log | `context/skills/.catalog-errors.ndjson` | NDJSON (gitignored) |
| Validation test batch output | Manual | Console output |

## Files

**Create:**

- None (runtime files created by scrub)

**Modify:**

- `.scripts/commands/skill.ts` — add `catalog scrub` subcommand, update `catalog cleanup`, `catalog forks`, and `catalog summary` for new data model
- `.scripts/test/catalog-tier1.test.ts` — tests for scrub logic

## Tasks

- [ ] Implement `catalog scrub` subcommand:
  - Check for `.catalog.lock` — abort if held
  - Create `.catalog.lock`
  - Read `.catalog.ndjson`
  - Entries with `wordCount` AND `error`: strip error fields, set `attemptCount: 0`
  - Entries with `error` but no `wordCount`: move error to `.catalog-errors.ndjson`, set `attemptCount: 1`, set `retryable: true`
  - Rewrite clean catalog via tmp + rename
  - Release `.catalog.lock`
  - Report: N cleaned, M moved to error log
- [ ] Implement `catalog scrub --dry-run` with full change report:

  ```text
  [DRY RUN] catalog scrub

  Entries to clean (have data + error):
    1,623 entries — error fields will be stripped, attemptCount reset to 0
    Example: 0froq/skills@pnpm (wordCount: 330, error: "batch failed: ...")

  Entries to move to error log (error only, no data):
    975 entries — error moved to .catalog-errors.ndjson, attemptCount set to 1
    Example: someorg/repo@skill-name (error: "download failed: 404")

  Error type distribution of moved entries:
    706  batch_failed (retryable: true)
    435  download_failed (retryable: true, defaulted — old errors lack errorType)
     27  download_failed (retryable: true)
     ...

  Summary:
    Catalog entries modified: 2,598
    Error log entries created: 975
    Catalog size: 13,325 → 13,325 (entries unchanged, fields stripped)
  ```

- [ ] Update `catalog cleanup`: verify it still works (worktree cleanup is data-model-independent)
- [ ] Update `catalog forks`: verify it still works (reads `contentHash` which is unchanged)
- [ ] Update `catalog summary` to include `attemptCount` distribution:

  ```text
  Total entries: 13,325
    available: 12,212
    archived: 833
    not_found: 280

  Analysis status:
    Analyzed (attemptCount=0): 3,512
    Failed once (attemptCount=1): 1,125
    Failed twice+ (attemptCount>=2): 43
    Never attempted: 7,532

  Attempt count distribution:
    0: 11,044
    1: 1,125
    2: 43
    3+: 0
  ```

- [ ] Backup existing catalog: `cp .catalog.ndjson .catalog.ndjson.bak`
- [ ] Run `catalog scrub --dry-run` to preview changes
- [ ] Run `catalog scrub` on existing data
- [ ] Verify: `catalog errors` shows correct breakdown from error log
- [ ] Verify: `catalog summary` shows accurate counts with attemptCount distribution
- [ ] Run test batch: `just agents skill catalog analyze --force --limit 1 --batch-size 5`
- [ ] Verify test batch: real content hashes, no stale errors, attemptCount reset on success, `validateBatchResults` reports 0 issues
- [ ] Run all tests: `cd .scripts && bun test`

## Notes

- This is the integration gate — do NOT resume production runs until this phase passes
- Backup the catalog before running scrub: the rewrite is destructive
- The lock file (`.catalog.lock`) is a simple file existence check, not a proper flock — sufficient for preventing concurrent `scrub` + `analyze` but not bulletproof
- After validation, resume scaled runs with: `just agents skill catalog analyze --batch-size 25 --concurrency 3 --limit 200`
- The `--dry-run` output should be detailed enough that you can review the exact impact before committing to the scrub
