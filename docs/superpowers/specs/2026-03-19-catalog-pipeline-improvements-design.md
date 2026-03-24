# Catalog Pipeline Improvements Design

**Date:** 2026-03-19
**Status:** Draft
**Context:** Phase 4 Tier 1 analysis has processed ~3,512 of ~12,200 available skills. Four issues identified from production runs need resolution before continuing at scale.

## Problem Statement

After processing ~30% of the catalog, four issues emerged:

1. **Stale error fields** (Critical) — 1,623 entries have both valid analysis data (`wordCount`) AND lingering `error` fields from prior failed runs. The merge strategy (`{ ...existing, ...newResult }`) doesn't clear old error fields on success, making error reports unreliable.

2. **No incremental skip** (Priority) — Each run re-processes all available entries. With 3,512 already analyzed, ~30% of each run is wasted work.

3. **Agent output quality** (Priority) — Haiku wraps NDJSON in markdown prose, 77 entries have `sha256:pending` instead of real hashes, 348 entries are missing keywords. Mechanical operations (hashing, counting) shouldn't be delegated to an LLM.

4. **No retry mechanism** (Convenience) — 45 batch-level failures (1,125 skills) from transient `claude` dispatch errors. No way to retry just the failures.

## Design

### 1. Error Log Separation

**Current:** Error fields (`error`, `errorType`, `errorDetail`, `errorCode`, `retryable`) live on catalog entries alongside analysis data.

**New:** Errors are stored in a separate append-only log. Catalog entries carry only success/attempt markers.

#### Error Log File

**Path:** `content/skills/.catalog-errors.ndjson` (gitignored)

**Schema:**

```json
{
  "source": "org/repo",
  "skill": "skill-name",
  "runId": "019...",
  "batchId": "019...",
  "timestamp": "2026-03-19T...",
  "errorType": "batch_failed | analysis_timeout | rate_limited | download_failed | download_timeout | analysis_failed",
  "errorDetail": "stderr output up to 500 chars",
  "errorCode": 1,
  "retryable": true
}
```

#### Catalog Entry Changes

**Remove:** `error`, `errorType`, `errorDetail`, `errorCode`

**Add:**

- `attemptCount` (number, default 0)
- `lastErrorType` (string | undefined) — cached from most recent error, used for skip logic without reading the full error log
- `retryable` (boolean | undefined) — cached from most recent error

**Keep:** `runId`, `batchId`, `analyzedAt` (stamped only on successful analysis)

**Rationale for caching `lastErrorType` and `retryable`:** The `filterForProcessing` function runs on every invocation. Reading and indexing the full error log (potentially thousands of records) on every run is expensive. Caching these two fields on the catalog entry avoids the need to read the error log for skip decisions. The error log remains the source of truth for full error history; the catalog fields are a performance cache.

#### Merge Behavior

**On success** (result has `wordCount`):

- Clear `lastErrorType`, `retryable`, and any lingering error fields from existing entry
- Reset `attemptCount` to 0
- Stamp `runId`, `batchId`, `analyzedAt`

**On failure:**

- Append error record to `.catalog-errors.ndjson`
- Increment `attemptCount` on catalog entry
- Set `lastErrorType` and `retryable` from the error
- Do NOT stamp `runId`/`batchId`/`analyzedAt`

#### Error Log Functions

New functions in `catalog.ts`:

- `appendError(errorLogPath, error)` — append one NDJSON line
- `appendErrors(errorLogPath, errors[])` — append multiple
- `readErrorLog(errorLogPath)` — read all error records
- `getErrorsForSkill(errorLogPath, source, skill)` — filter by skill

#### `DownloadResult` Error Fields

The `DownloadResult` type retains `error`/`errorType`/`errorDetail`/`errorCode` as **transient fields** internal to the orchestrator. These are used during `processBatch` to construct error log entries and are never written directly to the catalog. The flow is:

```text
preDownloadSkills → DownloadResult (with error fields)
  → processBatch routes errors to appendErrors() for the error log
  → processBatch increments attemptCount + caches lastErrorType/retryable on catalog entry
```

#### Backfill: `catalog scrub` Command

One-time cleanup of existing data:

1. Acquire a lock file (`.catalog.lock`) — abort if another process holds it
2. Read `.catalog.ndjson`
3. Entries with `wordCount` AND `error`: strip error fields, set `attemptCount: 0`, clear `lastErrorType`/`retryable`
4. Entries with `error` but no `wordCount`: move error to `.catalog-errors.ndjson`, set `attemptCount: 1`, set `retryable: true` (optimistic — old errors lack `errorType` so we assume retryable; permanent failures will fail again and get reclassified with proper `errorType` on retry)
5. Rewrite clean catalog
6. Release lock

#### CLI Change

`catalog errors` reads from `.catalog-errors.ndjson` instead of scanning the catalog for error fields.

#### Error Log Maintenance

The error log is append-only and grows unbounded. To manage size:

- `catalog errors --prune` — removes error records for skills that now have successful analysis (`attemptCount == 0` in catalog). These are historical errors that were resolved by a later successful run.
- Rule of thumb: run `--prune` after a successful `--retry-errors` pass.
- No automatic pruning — the log is an audit trail. Pruning is opt-in.
- Expected size: ~50 bytes per error record. At 10K errors, the log is ~500KB. Pruning is a convenience, not a necessity.

### 2. Incremental Skip

**Default behavior:** `analyze` skips entries that already have successful analysis.

#### Skip Criteria

An entry is **skipped** if:

- Has `wordCount` (successful Tier 1 data) AND `attemptCount == 0`

An entry is **processed** if ANY of:

- No `wordCount` and `attemptCount == 0` (never touched)
- `attemptCount > 0` AND `attemptCount < 2` AND `retryable == true` (retriable failure, cached on catalog entry)
- `--force` flag passed (process everything)
- `--retry-errors` flag passed (process only failed+retryable)

An entry is **permanently skipped** (even without `--force`) if:

- `attemptCount >= 2` (exhausted retry budget)
- `retryable == false` (permanent failure like download 404)

#### Implementation

New function `filterForProcessing()` in `catalog.ts`:

```typescript
filterForProcessing(
  catalog: CatalogEntry[],
  opts: { force?: boolean, retryErrors?: boolean }
): CatalogEntry[]
```

This function works entirely from catalog entry fields (`wordCount`, `attemptCount`, `retryable`, `availability`). It does NOT read the error log — the cached fields are sufficient for filtering.

**Availability filtering is preserved:** `filterForProcessing` first filters to `availability === 'available'`, then applies skip/retry logic. This replaces `filterAvailable()` which only did the first step.

#### CLI Flags

- Default: skip analyzed, process unattempted + retryable under limit
- `--force`: process everything regardless of state
- `--retry-errors`: process ONLY retryable entries (not unattempted)

#### Progress Output

```text
Catalog: 13,325 total, 12,212 available
  Already analyzed: 3,512 (skipping)
  Permanent failures: 462 (skipping)
  Retryable failures: 1,125 (including)
  Never processed: 7,725 (including)
  To process: 8,850
```

### 3. Mechanical Work in Native TypeScript

**Current:** Haiku agent runs `wc -w`, `find`, `shasum`, `grep` via Bash tool to compute metrics.

**New:** Orchestrator computes mechanical fields natively in TypeScript. Agent only does judgment work.

#### New Utility Functions in `catalog.ts`

```typescript
/** SHA-256 hash of file content, returned as "sha256:<hex>" */
export function computeContentHash(content: string): string {
  return `sha256:${new Bun.CryptoHasher('sha256').update(content).digest('hex')}`
}

/** Word count via whitespace split */
export function computeWordCount(content: string): number {
  return content.split(/\s+/).filter(Boolean).length
}

/** Count markdown headings (# through ######) */
export function computeSectionCount(content: string): number {
  return content.split('\n').filter(l => /^#{1,6}\s/.test(l)).length
}

/** Extract heading tree: [{depth, title}] */
export function computeHeadingTree(content: string): Array<{ depth: number; title: string }> {
  return content.split('\n')
    .filter(l => /^#{1,6}\s/.test(l))
    .map(l => {
      const match = l.match(/^(#{1,6})\s+(.*)$/)
      return match ? { depth: match[1].length, title: match[2].trim() } : null
    })
    .filter(Boolean) as Array<{ depth: number; title: string }>
}

/** Recursive file count in directory. Returns 0 if dir doesn't exist. */
export function computeFileCount(dir: string): number {
  try {
    let count = 0
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isFile()) count++
      else if (entry.isDirectory()) count += computeFileCount(join(dir, entry.name))
    }
    return count
  } catch {
    return 0
  }
}
```

All synchronous, zero dependencies. `computeFileCount` handles nonexistent directories gracefully. `computeHeadingTree` is also mechanical (parsing headings) and moves out of the agent alongside the other metrics.

#### `DownloadResult` Type Expansion

```typescript
interface DownloadResult {
  path: string | null
  contentHash?: string
  wordCount?: number
  fileCount?: number
  sectionCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  // Transient error fields — routed to error log, not written to catalog
  error?: string
  errorType?: 'download_failed' | 'download_timeout'
  errorDetail?: string
  errorCode?: number
}
```

Mechanical fields computed in `preDownloadSkills` immediately after confirming `SKILL.md` exists.

#### Agent Prompt Changes

**Before (9 steps):**

1. Read SKILL.md
2. wc -w for word count
3. Count ## headings
4. find for file count
5. Extract keywords
6. Check for `<details>` blocks
7. Check frontmatter
8. Grep for hardcoded tokens
9. shasum -a 256

**After (5 steps):**

1. Read SKILL.md at given path
2. Extract keywords from headings and first paragraph
3. Check for `<details>` blocks (progressive disclosure)
4. Check frontmatter for name/description (best practices)
5. Grep for hardcoded tokens/paths (security)

Manifest now includes pre-computed metrics:

```json
{
  "source": "org/repo",
  "skill": "name",
  "localPath": "/tmp/worktrees/.../SKILL.md",
  "wordCount": 1250,
  "sectionCount": 8,
  "fileCount": 3,
  "contentHash": "sha256:abc123..."
}
```

Agent uses provided `wordCount`/`sectionCount`/`fileCount` to determine `complexity` rating.

#### `--allowedTools` Change

**Before:** `"Bash(mdq:*,wc:*,find:*,stat:*,sha256sum:*,shasum:*) Read Glob Grep"`

**After:** `"Read Glob Grep"`

No more Bash access for the agent.

#### Merge Priority

Orchestrator's mechanical fields are authoritative — written directly to the catalog entry. Agent's NDJSON output contributes only judgment fields: `keywords`, `complexity`, `progressiveDisclosure`, `bestPracticesMechanical`, `securityMechanical`.

### 4. Retry via `--retry-errors`

**New flag:** `--retry-errors` filters to entries with `attemptCount > 0` AND `retryable == true` AND `attemptCount < 2`.

#### Flag Interaction Matrix

| Flags | Processes |
|---|---|
| (default) | Unattempted + retryable under limit |
| `--retry-errors` | Only retryable under limit |
| `--force` | Everything, ignores attemptCount/retryable |
| `--retry-errors --force` | All entries with `attemptCount > 0`, ignores attempt limit and retryable flag |

#### `attemptCount` Lifecycle

- Starts at 0 (never attempted)
- Incremented when error appended to error log
- Reset to 0 on successful analysis (has `wordCount`)
- Skip threshold: `attemptCount >= 2` unless `--force`

#### Concurrency Safety

`attemptCount` is incremented during the merge phase (`mergeTier1Results`), which rewrites the full catalog atomically via tmp-file + rename. Since the merge happens once at the end of the run (after all batches complete), there is no race between concurrent workers — they produce results in memory, and the merge is a single sequential operation.

If the same `source@skill` appears in multiple batches (shouldn't happen since batches are deduplicated by `createBatches`), the last-write-wins merge strategy applies. The error log captures all attempts regardless.

#### CLI Output for Retry Mode

```text
Retry mode: processing failed+retryable entries only
  Retryable errors: 1,125
  Over attempt limit: 43 (skipping, use --force to include)
  To process: 1,082
```

## Files Modified

| File | Changes |
|---|---|
| `cli/lib/catalog.ts` | Add `attemptCount`/`lastErrorType`/`retryable` to `Tier1Result`, remove `error`/`errorDetail`/`errorCode` from type, add error log functions, add mechanical compute functions (`computeContentHash`, `computeWordCount`, `computeSectionCount`, `computeHeadingTree`, `computeFileCount`), add `filterForProcessing`, update `mergeTier1Results` for error separation and success-clears-errors |
| `cli/commands/skill.ts` | Update `preDownloadSkills` to compute mechanical fields, update agent prompt (5 steps instead of 9), update `--allowedTools` to `"Read Glob Grep"`, add `--retry-errors`/`--force` flags, change default to skip-analyzed, add `catalog scrub` subcommand, update `catalog errors` to read error log + support `--prune`, update `catalog cleanup`/`catalog forks` for new data model, update `processBatch` to route errors to error log |
| `cli/test/catalog-tier1.test.ts` | Tests for mechanical compute functions, error log append/read, `filterForProcessing` (all flag combinations), merge behavior (success clears errors, failure increments attemptCount), `catalog scrub` logic |
| `content/skills/.gitignore` | Add `.catalog-errors.ndjson` |

## New Files

| File | Purpose |
|---|---|
| `content/skills/.catalog-errors.ndjson` | Append-only error log (gitignored) |

## Migration

**Prerequisites:** No `catalog analyze` run should be in progress. Check with `git worktree list | grep skill-inspect` — if any skill-inspect worktrees exist, wait or run `catalog cleanup` first.

**Steps:**

1. Run `catalog scrub` once to backfill existing data (separates errors from catalog, sets `attemptCount`, defaults historical errors to `retryable: true`)
2. All subsequent `analyze` runs use the new behavior automatically
3. Old entries without `attemptCount` are treated as `attemptCount: 0` (never attempted)
4. Old entries without `lastErrorType` are treated as having no cached error state

**Rollback:** The scrub is destructive to the catalog file (rewrites it). Back up `.catalog.ndjson` before running. The error log is additive and can be deleted to start fresh.
