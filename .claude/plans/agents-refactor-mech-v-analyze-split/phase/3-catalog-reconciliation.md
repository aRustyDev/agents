---
id: b62a5469-b722-4cee-ad9a-41c7f446d0ad
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
status: pending
related:
  depends-on: [945af810-a69c-450a-ba64-7e5024e579d3]
---

# Phase 3: Catalog Reconciliation & State Management

**ID:** `phase-3`
**Dependencies:** phase-2
**Status:** pending
**Effort:** Medium

## Objective

Match discovery results against the existing catalog to detect moves, renames, additions, and removals. Update catalog entry states and manage the lifecycle of skills that appear, move, or disappear from repos.

## Success Criteria

- [ ] Skill moves detected: same `name` in frontmatter, different `discoveredPath` than last run
- [ ] New skills reported: found in repo but not in catalog
- [ ] Removed skills marked: in catalog but not found in repo (soft-delete, not removed)
- [ ] Renamed skills detected: same `discoveredPath`, different frontmatter `name`
- [ ] `lastSeenAt` and `lastSeenHeadSha` updated on every successful discovery
- [ ] New catalog state `removed_from_repo` added (not terminal — `--force` re-checks)
- [ ] State machine diagram updated with new states and transitions
- [ ] Reconciliation is idempotent (running twice produces same result)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Reconciliation engine | `cli/lib/catalog-reconcile.ts` | TypeScript module |
| Reconciliation report type | `cli/lib/catalog.ts` | TypeScript interface |
| Updated state machine | `docs/src/catalog-state-machine.md` | Mermaid + tables |
| Tests | `cli/test/catalog-reconcile.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/catalog-reconcile.ts`
- `cli/test/catalog-reconcile.test.ts`

**Modify:**
- `cli/lib/catalog.ts` — add `removed_from_repo` availability status, reconciliation report type
- `cli/commands/skill.ts` — wire reconciliation into `catalog discover` output
- `cli/lib/catalog-stale.ts` — use `discoveredPath` when available for stale checks
- `docs/src/catalog-state-machine.md` — add new states and transitions

## Tasks

- [ ] Define `ReconciliationReport` type: `{ moved, added, removed, renamed, unchanged, errors }`
- [ ] Implement `reconcile(catalogEntries, discoveryResults)` — pure function, no I/O
- [ ] Move detection: same frontmatter `name`, different `discoveredPath` → update `discoveredPath`, set `movedFrom`
- [ ] Addition detection: skill found in repo but no catalog entry exists → report as `newSkill`
- [ ] Removal detection: catalog entry exists but skill not found in latest clone → set `status: removed_from_repo`
- [ ] Rename detection: same `discoveredPath`, different frontmatter `name` → report as `renamed`
- [ ] Update `lastSeenAt` / `lastSeenHeadSha` on all discovered skills
- [ ] Add `removed_from_repo` to `AvailabilityStatus` type
- [ ] Implement `--auto-discover` behavior: auto-add new skills with `availability: available`
- [ ] Implement `--include-removed` flag: re-check `removed_from_repo` entries
- [ ] Update state machine diagram with new states: `removed_from_repo`, `discovered_new`, move transitions
- [ ] Reclassify remaining `batch_failed` entries via discovery (moved from Phase 1 — needs repo access)
- [ ] Update `catalog-stale.ts` to use `discoveredPath` when available, falling back to `SKILL_LOOKUP_DIRS` for pre-discovery entries
- [ ] Handle simultaneous move+rename: compare `contentHash` before classifying as removal+addition — if content matches, copy analysis data to new entry
- [ ] Specify catalog key mutation for renames: old `source@old-name` entry gets `removed_from_repo` status, new `source@new-name` entry created with copied analysis data
- [ ] Tests: move detection, addition detection, removal detection, rename detection, move+rename with contentHash preservation, idempotency

## State Transitions (New)

| From | To | Trigger |
|------|----|---------|
| FullyComplete | RemovedFromRepo | Discovery doesn't find skill in repo |
| PartiallyAnalyzed | RemovedFromRepo | Discovery doesn't find skill in repo |
| RemovedFromRepo | Available | `--include-removed` finds it again (repo restored, skill re-added) |
| (new) | Available | `--auto-discover` adds newly found skill |
| FullyComplete | FullyComplete | Discovery finds skill at different path (move detected, `movedFrom` set) |

## Notes

- `removed_from_repo` is a soft-delete — the entry stays in the catalog with all its analysis data intact
- Move detection uses frontmatter `name` as the stable identifier, not filesystem path
- Rename detection uses `discoveredPath` as the stable identifier, not frontmatter name
- Both moves AND renames can happen simultaneously (different name AND different path) — this is treated as a removal + addition
- The reconciliation function is pure (no I/O) — it takes data in and returns a report. The caller decides what to persist.
