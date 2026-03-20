# Catalog Pipeline Improvements

**Created:** 2026-03-19
**Updated:** 2026-03-19
**Owner:** aRustyDev
**Spec:** `docs/superpowers/specs/2026-03-19-catalog-pipeline-improvements-design.md`

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Eliminate stale error data from catalog | Yes | 0 entries with both `wordCount` AND `error` fields |
| 2 | Skip already-analyzed skills by default | Yes | Runs process only unattempted + retryable entries |
| 3 | Move mechanical analysis out of Haiku agent | Yes | 0 pending/fake content hashes, agent uses `Read Glob Grep` only |
| 4 | Enable targeted retry of failed skills | Yes | `--retry-errors` flag processes only retryable failures |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Stale error entries (data + error) | 1,623 | 0 | 1,623 |
| Skills re-processed per run | ~3,512 (30%) | 0 (skip analyzed) | 3,512 |
| Pending/fake content hashes | 77 | 0 | 77 |
| Batch failures with no retry path | 1,125 | 0 (retryable via flag) | 1,125 |
| Agent allowed tools | Bash + Read + Glob + Grep | Read + Glob + Grep | Remove Bash |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Error Log Separation | pending | - | Error log exists, catalog entries have no error fields, merge routes errors to log |
| phase-2 | Mechanical Compute Functions | pending | - | 5 native TS functions, tests passing, `DownloadResult` carries computed fields |
| phase-3 | Incremental Skip + Retry | pending | phase-1 | `filterForProcessing` replaces `filterAvailable`, `--retry-errors`/`--force` flags work |
| phase-4 | Agent Prompt + Orchestrator Integration | pending | phase-1, phase-2 | Agent prompt reduced to 5 judgment steps, `--allowedTools` is `Read Glob Grep` |
| phase-5 | Migration + Validation | pending | phase-1, phase-2, phase-3, phase-4 | `catalog scrub` backfills existing data, test batch produces clean results |

### Phase Details

1. [Phase 1: Error Log Separation](./phase/1-error-log-separation.md)
2. [Phase 2: Mechanical Compute Functions](./phase/2-mechanical-compute.md)
3. [Phase 3: Incremental Skip + Retry](./phase/3-incremental-skip-retry.md)
4. [Phase 4: Agent Prompt + Orchestrator Integration](./phase/4-agent-prompt-integration.md)
5. [Phase 5: Migration + Validation](./phase/5-migration-validation.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backfill scrub corrupts catalog data | Low | High | Backup `.catalog.ndjson` before scrub, lock file prevents concurrent access |
| Native TS compute functions produce different results than shell equivalents | Low | Medium | Test against known skills with shell output for comparison |
| Reduced agent prompt causes Haiku to produce worse judgment output | Medium | Medium | Test batch of 5 skills before scaling, compare quality against pre-change results |
| Error log grows unbounded over many runs | Low | Low | `catalog errors --prune` for opt-in cleanup, ~50 bytes per record |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-19 | 2026-03-19 |
| Phase 1+2 complete (parallelizable) | | |
| Phase 3 complete | | |
| Phase 4 complete | | |
| Phase 5 migration + validation | | |
| Resume scaled catalog runs | | |

## Rollback Strategy

- **Catalog backup:** `cp .catalog.ndjson .catalog.ndjson.bak` before scrub
- **Error log is additive:** can be deleted to start fresh without data loss
- **Type changes are backward-compatible:** old entries without `attemptCount`/`lastErrorType`/`retryable` are treated as defaults (0/undefined/undefined)
- **Agent prompt is a string literal:** revert by restoring the old prompt array in `skill.ts`

## Notes

- Phases 1 and 2 are independent and can be implemented in parallel
- Phase 3 depends on Phase 1 (needs `attemptCount`/`retryable` fields on catalog entries)
- Phase 4 depends on both Phase 1 (error routing) and Phase 2 (mechanical data in manifest)
- Phase 5 is the integration/validation gate before resuming production runs
