---
id: f5e6a7b8-c9d0-1234-efab-345678901234
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 4: Filtering"
status: pending
related:
  depends-on: [e4d5f6a7-b8c9-0123-defa-234567890123]
---

# Phase 4: Filtering

**ID:** `phase-4`
**Dependencies:** phase-3
**Status:** pending
**Effort:** 1 day

## Objective

Filter graph visibility by node/edge properties. Search by label. Combine filters with AND logic.

## Success Criteria

- [ ] Uncheck a node type → those nodes and their edges disappear
- [ ] Filter by a property value → only matching nodes visible
- [ ] Search "neural" → only nodes with "neural" in label highlighted
- [ ] Combine type filter + search → both applied simultaneously
- [ ] Clear all → full graph restored

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Filter engine | `.scripts/client/graph-viewer/filter/engine.ts` | Predicate-based filtering |
| Sigma reducers | `.scripts/client/graph-viewer/filter/reducers.ts` | nodeReducer/edgeReducer |
| Filter UI | `.scripts/client/graph-viewer/ui/sidebar.ts` | Auto-generated from schema |

## Files

**Create:**
- `.scripts/client/graph-viewer/filter/engine.ts`
- `.scripts/client/graph-viewer/filter/reducers.ts`

**Modify:**
- `.scripts/client/graph-viewer/ui/sidebar.ts` — add filter panel (type checkboxes, search input)
- `.scripts/client/graph-viewer/ui/controls.ts` — add active filter count badge, clear button
- `.scripts/client/graph-viewer/state/store.ts` — add activeFilters state

## Tasks

- [ ] Implement filter engine with typed predicates (by node type, edge type, property value)
- [ ] Implement Sigma nodeReducer/edgeReducer for visibility/dimming
- [ ] Implement auto-generated filter UI from schema (enums → checkboxes, strings → search)
- [ ] Implement text search (substring, case-insensitive) with highlight
- [ ] Integrate filters with AND logic (search AND type filters combined)
- [ ] Add "clear all filters" button with active count badge

## Notes

- Filtered-out nodes: hidden or dimmed (configurable)
- Edges connected to hidden nodes: hidden
- Emit `filter:changed` event → reducers update Sigma
