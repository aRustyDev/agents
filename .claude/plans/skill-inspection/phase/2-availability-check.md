---
id: a1b2c3d4-2222-4aaa-bbbb-222222222222
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 2: Availability Check"
status: pending
---

# Phase 2: Availability Check

**ID:** `phase-2`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Check the availability of all 13,644 skill source repos via HTTP HEAD requests, rate-limited to respect GitHub API limits, and write initial `.catalog.ndjson` entries with availability status.

## Success Criteria

- [ ] All 13,644 entries have an availability status: `available`, `archived`, `not_found`, `private`, or `error`
- [ ] Rate limiting stays within GitHub API limits (60/min unauthenticated, 5K/hr authenticated)
- [ ] Process is resumable — interrupted runs pick up where they left off
- [ ] `ai-tools skill catalog availability` command works with `--json` and `--concurrency` flags
- [ ] Output is valid NDJSON with one line per entry

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Availability checker | `cli/lib/catalog.ts` | TypeScript |
| Catalog NDJSON output | `context/skills/.catalog.ndjson` | NDJSON |
| CLI subcommand | `cli/commands/skill.ts` (additions) | TypeScript |
| Tests | `cli/test/catalog-availability.test.ts` | TypeScript |

## Files

**Create:**
- `cli/lib/catalog.ts` — NDJSON I/O, availability checking, rate limiting
- `cli/test/catalog-availability.test.ts`
- `context/skills/.catalog.ndjson` — generated output (gitignored)

**Modify:**
- `cli/commands/skill.ts` — add `catalog availability` subcommand
- `cli/lib/schemas.ts` — add `CatalogEntry` schema
- `context/skills/.gitignore` — add `.catalog.ndjson`

## Tasks

### Catalog Entry Schema
- [ ] Define `CatalogEntry` Valibot schema in `schemas.ts` covering all fields from the spec
- [ ] Define `AvailabilityStatus` enum: `available | archived | not_found | private | error`

### Availability Checker
- [ ] Parse `.TODO.yaml` to extract unique `owner/repo` pairs (3,333 repos, not 13K — deduplicate by repo)
- [ ] HTTP HEAD to `https://github.com/<owner>/<repo>` for each unique repo
- [ ] Map HTTP status codes to availability enum (200→available, 301→check for archive, 404→not_found, 401/403→private, timeout→error)
- [ ] Rate limiting: configurable concurrency (default 50), 1s inter-batch delay
- [ ] Use `GITHUB_TOKEN` if available for 5K/hr limit; fall back to 60/min unauthenticated
- [ ] Checkpoint: write results incrementally, skip already-checked repos on resume

### NDJSON Output
- [ ] For each entry in `.TODO.yaml`, write one NDJSON line with: `source`, `skill`, `availability`
- [ ] Entries sharing the same repo inherit the repo's availability status
- [ ] Append category/subcategory from `.taxonomy.yaml` if Phase 1 has run (optional — deferred to Phase 6 if not)

### CLI Subcommand
- [ ] `ai-tools skill catalog availability [--concurrency 50] [--json]`
- [ ] `--concurrency` controls parallel request count
- [ ] `--json` outputs summary as JSON
- [ ] Show progress: table of status counts updated as batches complete

### Follow-up Flagging
- [ ] For `not_found` entries: log as candidates for follow-up search (repo renamed/moved)
- [ ] Write summary: count per status, list repos flagged for follow-up

## Notes

- This phase operates at the **repo level** (3,333 unique repos), not the entry level (13,644)
- Multiple skills from the same repo share one availability check
- Estimated time: ~15 min with concurrency=50 and GITHUB_TOKEN
- Can run in parallel with Phase 1 (no dependencies)
