---
id: 02b10f86-561d-4c89-bc1e-d1f0c4fb5fd0
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 4b: External Skill Tracking"
status: pending
related:
  depends-on: [c3e48e7b-0900-48fb-9bef-5129cf813ad6]
---

# Phase 4b: External Skill Tracking

**ID:** `phase-4b`
**Dependencies:** phase-4a
**Status:** pending
**Effort:** Large

## Objective

Build the external skill tracking system: vendored snapshots in `.external/`, two-mode usage (passthrough symlinks vs derived skills), upstream drift detection via `git ls-remote`, GitHub issue creation for review, and symlink management.

## Success Criteria

- [ ] `context/skills/.external/` directory exists with `sources.yaml`, `sources.lock.json`, and justfile
- [ ] `ai-tools skill deps check` detects upstream drift via `git ls-remote` without downloading
- [ ] `ai-tools skill deps sync` fetches sources into `.external/`, updates lock file
- [ ] `ai-tools skill deps issues` creates/upserts GitHub issues with diff blocks and `skills`/`review` labels
- [ ] `ai-tools skill deps issues --dry-run` previews issues without creating them
- [ ] `ai-tools skill deps links` creates/refreshes passthrough symlinks from manifest
- [ ] `ai-tools skill deps status` shows combined view (mode, hash, symlink health, issue state)
- [ ] Exit codes: 0=all current, 1=drift detected, 2=process error
- [ ] `just external:update` runs full workflow (sync -> issues -> links -> status)
- [ ] `just external:check` works as a network-only drift check (no local writes)
- [ ] Passthrough and derived_by are validated as mutually exclusive
- [ ] `ref` field supports tag and commit SHA pinning (not branches)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| External skills manifest | `context/skills/.external/sources.yaml` | YAML |
| External skills lock | `context/skills/.external/sources.lock.json` | JSON |
| External justfile module | `context/skills/.external/justfile` | Just |
| Updated skill commands | `.scripts/commands/skill.ts` | TypeScript |
| Updated schemas | `.scripts/lib/schemas.ts` | TypeScript |
| Updated lockfile registry | `.scripts/lib/lockfile.ts` | TypeScript |
| Updated hash module | `.scripts/lib/hash.ts` | TypeScript |
| Test suites | `.scripts/test/skill-deps.test.ts` | TypeScript |

## Files

**Create:**
- `context/skills/.external/sources.yaml` (initial manifest with existing external skills)
- `context/skills/.external/sources.lock.json` (machine-managed, initially empty)
- `context/skills/.external/justfile` (module with external:* recipes)
- `.scripts/test/skill-deps.test.ts`

**Modify:**
- `.scripts/commands/skill.ts` (replace deps stubs with full implementation)
- `.scripts/lib/schemas.ts` (add ExternalSkillEntry, ExternalSourcesManifest, ExternalLockEntry)
- `.scripts/lib/lockfile.ts` (register external-skills lock schema)
- `.scripts/lib/hash.ts` (add lockKey function)
- `context/skills/justfile` (add `mod external ".external/justfile"`)

## Architecture

### Two Modes

| Mode | Mechanism | Drift Tracking |
|------|-----------|----------------|
| **Passthrough** | Symlink `context/skills/<name> -> .external/<source>/<skill>/` | No (upstream used directly) |
| **Derived** | Vendored snapshot in `.external/`, local skill independently authored | Yes (issues on drift) |

`passthrough` and `derived_by` are mutually exclusive per manifest entry.

### Two Hashes

| Hash | Purpose | When Updated |
|------|---------|-------------|
| `upstream_commit` | Remote commit SHA from `git ls-remote` — drift detection without downloading | `sync` and `check` |
| `snapshot_hash` | Content-addressed hash of downloaded files — local integrity verification | `sync` only |

### Lock Key

Content-hash of `source/skill`: `sha256("steveyegge/beads/beads").slice(0, 12)`. Enables renaming skills in manifest without losing tracking history.

### GH Issue Upsert

- Keyed by **local skill** (not external source)
- Multiple upstream drifts affecting same local skill -> append to same open issue
- Closed issues -> create new issue
- Title: `[SKILL DRIFT] upstream changes (<local-skill-name>)`
- Labels: `skills`, `review`
- Body: checklist items per upstream source with `<details>` diff blocks

## Tasks

### lib/schemas.ts — external skill schemas
- [ ] Define `ExternalSkillEntry` — source, skill, passthrough, ref, derived_by
- [ ] Add cross-field validation: `passthrough=true` and `derived_by` are mutually exclusive
- [ ] Add `ref` validation: must be semver tag (`v1.2.3`), bare tag, or 40-char hex SHA (not branches)
- [ ] Define `ExternalSourcesManifest` — `{ skills: Record<string, ExternalSkillEntry> }`
- [ ] Define `ExternalLockEntry` — upstream_commit, snapshot_hash, last_synced, last_reviewed_commit, drift_issue
- [ ] Export inferred types

### lib/lockfile.ts — register schema
- [ ] Register `external-skills` lock schema in the schema registry
- [ ] Lock keys are content-hashes, not skill names — `readLockfile`/`writeLockfile` must handle this

### lib/hash.ts — lock key
- [ ] Add `lockKey(source: string, skill: string): string` — `sha256(${source}/${skill}).slice(0, 12)`

### deps check
- [ ] Read and validate `sources.yaml` via Valibot schema
- [ ] For each skill entry:
  - If `ref` set: `git ls-remote --tags <repo-url>` to verify ref exists
  - If no `ref`: `git ls-remote HEAD <repo-url>` to get current commit
- [ ] Compare remote commit against lock's `upstream_commit`
- [ ] Output table: Skill | Source | Status (current/CHANGED/UNAVAIL) | Last Synced
- [ ] With `--json`: array of status objects
- [ ] Exit code: 0=all current, 1=drift detected, 2=error (network, parse)
- [ ] This is network-only — no local writes

### deps sync
- [ ] For each drifted skill (or `--force` for all):
  - Create temp dir via `mktemp -d`
  - If `ref` set: `git clone --depth 1 --branch <ref> https://github.com/<source>.git`
  - If no `ref`: `npx skills add -y --copy --full-depth <source>@<skill>` with CWD=tmpdir
  - Copy result to `.external/<source>/<skill>/`
  - Clean up temp dir and any `.claude/` or `.agents/` artifacts in `.external/`
  - Record `upstream_commit` via `git ls-remote`
- [ ] Update lock: `upstream_commit`, `snapshot_hash` (via `hashDirectory`), `last_synced`
- [ ] Do NOT auto-commit — leave in working tree for review
- [ ] Fallback: if `npx skills` not available, fall back to `git clone` for all entries

### deps issues
- [ ] Validate all `derived_by` entries reference existing dirs in `context/skills/` — warn on missing
- [ ] Detect changed files via `git diff HEAD -- context/skills/.external/<source>/<skill>/`
- [ ] Group by local skill (`derived_by` value)
- [ ] For each local skill with drift:
  - Search for open `[SKILL DRIFT]` issue for that local skill
  - If open: append checklist item + diff in `<details>` block
  - If closed/none: create new issue
  - Record issue number in lock's `drift_issue` field
- [ ] Support `--dry-run` — print formatted issue bodies without creating
- [ ] Support `--repo` flag (default: `aRustyDev/agents`)
- [ ] Handle UNAVAILABLE sources: include in issue body with warning text

### deps links
- [ ] Read `sources.yaml`, filter `passthrough: true` entries
- [ ] For each: compute target (`.external/<source>/<skill>/`) and link (`context/skills/<name>`)
- [ ] If symlink exists and correct target: skip
- [ ] If symlink exists but wrong target: remove and recreate
- [ ] If no symlink: create via `lib/symlink.ts`
- [ ] If target doesn't exist: warn "sync needed"
- [ ] Report: table of symlinks with action taken (created/updated/skipped/broken)

### deps status
- [ ] Combined view merging check, links, and issue state
- [ ] Table: Skill | Source | Mode (passthrough/derived) | Hash (truncated) | Symlink (healthy/broken/—) | Issue (#N open/—)
- [ ] With `--json`: full status array
- [ ] Exit code: 0=all healthy, 1=any issues

### External justfile module
- [ ] Create `context/skills/.external/justfile` with recipes:
  - `update *FLAGS` — sync -> issues -> links -> status
  - `check *FLAGS` — network check, no writes
  - `sync *FLAGS` — pull fresh copies
  - `issues *FLAGS` — create/update GH issues
  - `links` — create/refresh symlinks
  - `status *FLAGS` — show combined state
- [ ] All delegate to `bun run .scripts/bin/ai-tools.ts skill deps <verb>`
- [ ] Add `mod external ".external/justfile"` to `context/skills/justfile`
- [ ] Invoked as: `just external:check`, `just external:update`, etc.

### Initial manifest population
- [ ] Identify existing external skills (beads, handoff from current `skills-lock.json`)
- [ ] Create initial `sources.yaml` with correct entries
- [ ] Run `sync` to populate `.external/` snapshots
- [ ] Run `links` to create symlinks
- [ ] Verify `status` shows healthy state

## Notes

- `deps check` is safe for CI — network-only, no local writes
- `deps sync` leaves changes uncommitted — user reviews and commits the changeset
- `npx skills add` skips dotdirs, so `.external/` files are not discovered by skill tools
- Discovery isolation verified: no `.skillsignore` needed
- Lock file uses JSON (consistent with `skills-lock.json`, `plugin.sources.json`)
- Manifest uses YAML (hand-edited, more readable for humans)
- `js-yaml` dependency installed in Phase 0 handles YAML parsing
- Auth for GitHub issues uses `lib/github.ts` from Phase 4a
- Consider future CI job: `just external:check` on a schedule, auto-opening PRs with `just external:update`
