---
id: e4d5f6a7-b8c9-0123-defa-234567890123
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 3: CRUD Operations"
status: pending
related:
  depends-on: [d3c4e5f6-a7b8-9012-cdef-123456789012]
---

# Phase 3: CRUD Operations

**ID:** `phase-3`
**Dependencies:** phase-2
**Status:** pending
**Effort:** 1.5 days

## Objective

Create, edit, and delete nodes and edges through the UI. Undo/redo support.

## Success Criteria

- [ ] Create a node with properties → visible in graph immediately
- [ ] Create an edge between two nodes → rendered with label
- [ ] Delete a node → node and all connected edges removed
- [ ] Edit a property in sidebar → graph reflects change
- [ ] Undo 3 operations → graph reverts to prior state
- [ ] Save → all CRUD changes persisted to disk

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| CRUD handlers | `.scripts/client/graph-viewer/interaction/crud.ts` | Graphology mutations |
| Property editor | `.scripts/client/graph-viewer/ui/sidebar.ts` | Sidebar inspector |
| Undo/redo system | `.scripts/client/graph-viewer/interaction/undo.ts` | Command pattern |

## Files

**Create:**
- `.scripts/client/graph-viewer/interaction/crud.ts`
- `.scripts/client/graph-viewer/interaction/undo.ts`
- `.scripts/client/graph-viewer/ui/sidebar.ts`

**Modify:**
- `.scripts/client/graph-viewer/ui/controls.ts` — add action buttons (delete, undo, redo)
- `.scripts/client/graph-viewer/state/store.ts` — add undo stack

## Tasks

- [ ] Implement node creation (double-click canvas → modal → add to Graphology)
- [ ] Implement edge creation (select source → edge mode → click target → modal)
- [ ] Implement deletion (Delete key, cascade edges on node delete, confirm for >3 items)
- [ ] Implement sidebar property editor (schema-informed: enum → dropdown, string → text)
- [ ] Implement undo/redo with command pattern (50 ops, Ctrl+Z / Ctrl+Shift+Z)
- [ ] Wire CRUD events through event bus (graph:node-added, graph:edge-removed, etc.)

## Notes

- IDs use nanoid convention: `node-{nanoid}`, `edge-{nanoid}`
- Validate no duplicate edges between same source/target with same type
- Undo stack clears on graph reload (not on save)
