# ADR-025: Use Git Tree SHA for Catalog Stale Detection

## Status

Accepted

## Context

The catalog stores `contentHash` (SHA-256 of SKILL.md content) on each entry after Tier 1 analysis. With 6,000+ analyzed entries, re-analyzing everything on each run wastes API credits and time. The problem is detecting which entries have changed upstream without downloading every file again.

The existing `contentHash` cannot be compared against remote without fetching the file first, defeating the purpose of stale detection. A different signal is needed that the GitHub API can provide without a full clone.

Git tree objects are a natural fit: `git rev-parse HEAD:<skill-dir>` returns a SHA that changes whenever any file in that directory tree changes. The GitHub Trees API (`GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1`) can return this same SHA without cloning.

## Decision Drivers

1. **No-clone stale detection** — must identify changed skills without downloading them
2. **Directory granularity** — a skill's stale status must reflect changes to any file in its directory, not just `SKILL.md`
3. **Batch efficiency** — stale check must handle hundreds of entries with reasonable API concurrency
4. **Hash type clarity** — `treeSha` and `contentHash` must not be compared cross-type

## Considered Options

### Option 1: Re-Download and Compare `contentHash`

Download SKILL.md for each entry and compare SHA-256 against the stored `contentHash`.

- Pro: Uses the already-stored field; no new API calls
- Con: Requires a full clone or file download for every entry; defeats the purpose of stale detection

### Option 2: GitHub Contents API with `If-None-Match`

`GET /repos/.../contents/SKILL.md` with ETag caching.

- Pro: Per-file; works for single-file skills
- Con: Per-file only — misses changes to supporting files in the skill directory; ETag is not a stable cross-session cache key in the GitHub API

### Option 3: Git Tree SHA from `rev-parse` + Trees API (Chosen)

Store `treeSha` during download; compare against upstream via GitHub Trees API.

- Pro: Single API call per repo covers all files in the skill directory; `treeSha` is a stable, meaningful identifier; stale detection requires no cloning
- Con: `treeSha` is a git object SHA, not a content hash — cannot be compared against `contentHash`; requires authenticated API access

### Option 4: Repo Commit SHA

Store the HEAD commit SHA of the repository; compare against upstream latest commit.

- Pro: Simplest to fetch (one API call per repo)
- Con: Too coarse — any commit anywhere in the repo marks all skills stale, even if their directories were untouched

## Decision

**Store `treeSha` (from `git rev-parse HEAD:<skill-subdir>`) on catalog entries during download; compare against upstream via GitHub Trees API for stale detection.**

Two new functions in `.scripts/lib/stale.ts`:

- `fetchUpstreamHashes(entries, concurrency)` — batches `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` calls; groups entries by repo to minimize API requests; uses the keychain token provider from ADR-022
- `identifyStaleEntries(local, upstream)` — pure comparison function; returns entries where `local.treeSha !== upstream.treeSha`

The `catalog stale` command checks up to 100 entries by default with concurrency 5. Both limits are configurable via `--limit` and `--concurrency` flags.

`treeSha` is stored alongside `contentHash` in the catalog NDJSON; they are different hash types computed by different algorithms and must never be compared against each other.

## Consequences

### Positive

- Stale detection requires zero clones — only GitHub API calls
- Directory-granular: any change to any file in the skill subdirectory is detected
- `identifyStaleEntries` is a pure function — fully unit-testable without API calls

### Negative

- `treeSha` requires authenticated GitHub API access — rate-limited to 5,000 requests/hour per token
- `treeSha` and `contentHash` are intentionally different types; confusing them causes silent false-negatives (they will never match even for identical content)

### Neutral

- `treeSha` is populated only for skills downloaded via the new orchestrator (ADR-024); entries downloaded via `--legacy-download` have `treeSha: null` and are skipped by stale detection
- The Trees API response includes all files recursively; the response is not stored — only the top-level tree SHA is compared
