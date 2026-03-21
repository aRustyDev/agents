---
id: a6f7b8c9-d0e1-2345-fabc-456789012345
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 5: Polish & Multi-Graph Overlay"
status: pending
related:
  depends-on: [f5e6a7b8-c9d0-1234-efab-345678901234]
---

# Phase 5: Polish & Multi-Graph Overlay

**ID:** `phase-5`
**Dependencies:** phase-4
**Status:** pending
**Effort:** 2–3 days

## Objective

Production-quality UX — keyboard shortcuts, visual polish, edge case handling. Optional multi-graph overlay for cross-ontology analysis.

## Success Criteria

- [ ] All keyboard shortcuts functional (Delete, Ctrl+Z, Ctrl+S, Escape, F, /)
- [ ] Nodes visually distinct by type (color-coded)
- [ ] Edges styled by type (solid, dashed)
- [ ] Corrupted JSON file → error toast, app remains functional
- [ ] 500-node graph renders and interacts smoothly
- [ ] (Optional) Load 2 graphs, see both color-coded, filter by source

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Keyboard shortcuts | `cli/client/graph-viewer/interaction/shortcuts.ts` | Key handler |
| Visual styling | `cli/client/graph-viewer/styles.css` | Type-based colors |
| Multi-graph overlay | `cli/client/graph-viewer/graph/serializer.ts` | _source partitioning |

## Files

**Create:**
- `cli/client/graph-viewer/interaction/shortcuts.ts`

**Modify:**
- `cli/client/graph-viewer/styles.css` — type-based node/edge colors
- `cli/client/graph-viewer/filter/reducers.ts` — source-based visibility toggle
- `cli/client/graph-viewer/graph/serializer.ts` — partition by _source on save
- `cli/client/graph-viewer/ui/controls.ts` — keyboard shortcut help overlay

## Tasks

- [ ] Implement keyboard shortcuts (Delete, Ctrl+Z/Shift+Z, Ctrl+S, Escape, Ctrl+A, F, /)
- [ ] Implement node color-coding by type (configurable palette)
- [ ] Implement edge styling by type (solid/dashed/weighted)
- [ ] Implement label rendering threshold (hide when zoomed out)
- [ ] Handle malformed JSON gracefully (parse error → toast, don't crash)
- [ ] Handle concurrent writes (agent writes while UI has unsaved → conflict toast)
- [ ] Handle empty graph state (no nodes → "Double-click to create a node")
- [ ] (Optional) Multi-graph overlay: load multiple graphs, color by source, filter by source
- [ ] Performance tuning if needed (label threshold, ForceAtlas2 iteration cap, debounce filters)

## Notes

- Multi-graph overlay is optional — build only if time allows
- 500-node graph is the performance target (well within Sigma.js WebGL capacity)
- Help overlay showing all shortcuts accessible via `?` key
