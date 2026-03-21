---
id: d3c4e5f6-a7b8-9012-cdef-123456789012
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 2: Multi-File + Persistence"
status: pending
related:
  depends-on: [c2b3d4e5-f6a7-8901-bcde-f12345678901]
---

# Phase 2: Multi-File + Persistence

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** pending
**Effort:** 1–1.5 days

## Objective

Switch between multiple graph files. Save graph data and view state back to disk. Schema validation on save. Lock file reconciliation on load.

## Success Criteria

- [ ] Switch between multiple graphs in the UI
- [ ] Save graph → file on disk reflects changes
- [ ] Close browser, reopen → positions and camera state restored from lock file
- [ ] Delete a node from JSON externally → reload → lock file loses that node's position, no crash
- [ ] Save with invalid data → clear error message, save rejected

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Graph CRUD API | `.scripts/server/graph-viewer/routes/graphs.ts` | REST endpoints |
| Serializer | `.scripts/client/graph-viewer/graph/serializer.ts` | Graphology → JSON |
| Lock reconciliation | `.scripts/lib/graph-lock.ts` | Orphan cleanup + default positions (extends Phase 1) |
| File picker UI | `.scripts/client/graph-viewer/ui/controls.ts` | Dropdown component |
| Schema validation | `.scripts/server/graph-viewer/validation.ts` | Ajv-based (wraps lib/graph-schema.ts) |

## Files

**Create:**
- `.scripts/server/graph-viewer/validation.ts`
- `.scripts/server/graph-viewer/fs-helpers.ts`
- `.scripts/client/graph-viewer/graph/serializer.ts`

**Modify:**
- `.scripts/server/graph-viewer/routes/graphs.ts` — add PUT/POST with validation
- `.scripts/client/graph-viewer/ui/controls.ts` — add file picker
- `.scripts/client/graph-viewer/state/store.ts` — add dirty flag, active graph ID
- `.scripts/bin/graph-viewer.ts` — wire new API routes

## Tasks

- [ ] Implement GET/PUT/POST /api/graphs endpoints with atomic writes
- [ ] Implement GET /api/schemas/:name endpoint
- [ ] Implement Ajv schema validation on save (400 + errors on failure)
- [ ] Implement file picker UI reading from manifest
- [ ] Implement save workflow with dirty flag tracking
- [ ] Implement auto-save lock file on layout change, drag end, camera change (debounced 2s)
- [ ] Implement lock file reconciliation (orphan cleanup, missing position assignment)

## Notes

- Atomic writes: write to .tmp, rename to target
- Lock file writes are the exception — direct overwrite is fine
- Validation error handling: display in toast/sidebar, reject save
- See `refs/project-architecture.md` §View State for lock file format spec
