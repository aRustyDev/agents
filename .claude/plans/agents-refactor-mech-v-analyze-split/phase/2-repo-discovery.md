---
id: 945af810-a69c-450a-ba64-7e5024e579d3
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
status: pending
related:
  depends-on: [eeb7137a-e202-485b-881f-8ed38e853f1f]
---

# Phase 2: Repo-level Mechanical Discovery

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** pending
**Effort:** Large

## Objective

Replace the per-skill-name download model with a per-repo discovery engine. Clone each unique repo once, discover ALL skills, and compute ALL deterministic fields in a single pass. Produces a repo manifest and enriched catalog entries without any LLM involvement.

## Success Criteria

- [ ] `catalog discover` command exists (separate from `catalog analyze`)
- [ ] Discovers all skills per repo (not just the one the catalog expects)
- [ ] Produces `.catalog-repos.ndjson` with repo-level metadata
- [ ] Computes all mechanical fields per skill: wordCount, sectionCount, fileCount, headingTree, treeSha, contentHash, keywords (mechanical), lineCount, sectionMap, fileTree, skillSizeBytes, isSimple, discoveredPath
- [ ] Repo metadata captured: totalFiles, repoSizeBytes, archived, lastCommitAt, commitCount, contributorCount
- [ ] Groups by unique repo — a repo with 30 skills is cloned once
- [ ] Reports newly discovered skills not in catalog
- [ ] Reports skills in catalog not found in repo
- [ ] Handles non-standard skill locations (recursive discovery)
- [ ] Progress reporting with concurrency control
- [ ] Incremental discovery: skip repos where HEAD SHA matches `.catalog-repos.ndjson` (full run ~2.5h → incremental <5min)
- [ ] `--dry-run` produces structured JSON summary: `{ newSkills, movedSkills, removedSkills, unchangedSkills, reposToClone, reposSkipped }`

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Discovery engine | `cli/lib/catalog-discover.ts` | TypeScript module |
| Repo metadata collector | `cli/lib/repo-metadata.ts` | TypeScript module |
| CLI command | `cli/commands/skill.ts` | `catalog discover` subcommand |
| Unit tests | `cli/test/catalog-discover.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/catalog-discover.ts` — discovery engine
- `cli/lib/repo-metadata.ts` — repo-level metadata collection (git log, contributors, size)
- `cli/test/catalog-discover.test.ts`

**Modify:**
- `cli/commands/skill.ts` — add `catalog discover` subcommand
- `cli/lib/catalog-download.ts` — refactor to share clone infrastructure
- `cli/lib/catalog.ts` — repo manifest write/merge functions

## Tasks

- [ ] Extract unique repos from catalog: `Set<source>` from all available entries
- [ ] Implement `discoverRepo(source, opts)` — clone, collect repo metadata, discover all skills, compute all mechanical fields per skill
- [ ] Implement `collectRepoMetadata(tempDir)` — git log for commit count, contributors, last commit; du for size; file count
- [ ] Implement `computeAllMechanicalFields(skillMdPath, skillDir, tempDir)` — single function that computes every deterministic field
- [ ] Implement `discoverAllRepos(repos, opts)` — concurrent repo processing with progress
- [ ] Wire `catalog discover` CLI command with flags: `--limit`, `--concurrency`, `--dry-run`, `--report-only` (don't write, just show what would change)
- [ ] Produce discovery report: new skills, missing skills, moved skills, unchanged skills
- [ ] Write repo manifest to `.catalog-repos.ndjson`
- [ ] Enrich existing catalog entries with newly computed fields (via `mergeBackfillResults` pattern)
- [ ] Handle `--auto-discover` flag for adding new skills to catalog (default: report only)
- [ ] Implement incremental discovery: read `.catalog-repos.ndjson`, compare `headSha` with `git ls-remote`, skip repos that haven't changed
- [ ] Implement `--dry-run` with structured JSON output (counts of new/moved/removed/unchanged)
- [ ] Tests: local directory mocking (no network), repo metadata parsing, discovery report generation, incremental skip logic

## Design Notes

### Discovery Flow

```
1. Read catalog → extract unique repos
2. For each repo (concurrently):
   a. Clone (shallow, HEAD)
   b. Collect repo metadata (git log, du, etc.)
   c. discoverSkills(tempDir) → all SKILL.md files
   d. For each discovered skill:
      - Compute ALL mechanical fields
      - Record discoveredPath
      - Match against catalog entries
   e. Write repo manifest entry
   f. Cleanup clone
3. Produce discovery report
4. Optionally merge into catalog
```

### Repo Metadata Collection

```typescript
interface RepoMetadataOpts {
  tempDir: string  // cloned repo path
}

// Collect from git:
// git log --oneline | wc -l → commitCount
// git log -1 --format=%aI → lastCommitAt
// git shortlog -sn --no-merges | wc -l → contributorCount
// du -sb . → repoSizeBytes (or recursive stat)
// find . -type f | wc -l → totalFiles
```

### What "Simple" vs "Complex" Means

- **Simple skill**: directory contains only `SKILL.md` (no resources, examples, or subdirs)
- **Complex skill**: directory contains `SKILL.md` plus other files (resources/, examples/, assets/, etc.)

This distinction matters for Tier 2 analysis — complex skills have more to review.

### Performance Estimate

~4,500 unique repos at concurrency 5, ~10s per clone + compute = ~2.5 hours for full discovery pass. Incremental runs (only repos changed since last discovery) would be much faster via `treeSha` comparison.
