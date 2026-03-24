# Test Baseline — 2026-03-24

Pre-restructure test state for regression tracking.

## Summary

| Metric | Count |
|--------|-------|
| Total tests | 1,672 |
| Passing | 1,580 |
| Failing | 92 |
| Errors | 3 |
| Files | 67 |

## Failure Categories

| Category | Count | Root Cause |
|----------|-------|------------|
| Hash functions (hashFile, hashDirectory, computeHash, verifyHash, computeContentHash) | 26 | `fileStream` API change — hash functions use a Bun API that changed behavior |
| Skill lifecycle (add, remove, outdated, info) | 12 | Lockfile/discovery integration — depends on real filesystem state |
| findSkills / catalog backend | 11 | catalog.ndjson path or search backend state |
| Plugin operations (listPlugins, fixture ops, command module) | 9 | Plugin directory structure changes — stale test assumptions |
| Git operations (lsRemote, gitRaw, parseRepo, cleanupTempDir) | 9 | Network-dependent or temp directory cleanup issues |
| computeAllMechanicalFields | 4 | Discovery module — may need fixture updates |
| Skill CLI wiring | 3 | Command registration — subcommand list changed |
| Search (page parameter, auto mode) | 3 | Search API pagination changes |
| Integration tests (catalog-download, LocalProvider) | 2 | Network or auth-dependent |
| Other (chunkFile, mixed sources) | 3 | Various |

## Regression Benchmark

During the monorepo restructure (Phases 0-5), the success criterion is:
- **Zero regressions**: no NEW test failures introduced by file moves/renames
- The 92 pre-existing failures are NOT blockers for the restructure
- Fixing pre-existing failures is tracked separately

## How to Check for Regressions

```bash
# Run tests and compare
bun test --cwd cli 2>&1 | tail -5
# Expected: 1580 pass, 92 fail (±3 for flaky tests)
# Regression = pass count drops OR fail count increases
```
