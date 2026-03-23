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
- [ ] Tests: move detection, addition detection, removal detection, rename detection, idempotency

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
