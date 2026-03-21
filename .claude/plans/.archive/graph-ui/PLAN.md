---
id: a7c3e1f0-4d2b-4a8e-b6f1-9e8d7c5a3b20
project:
  id: 00000000-0000-0000-0000-000000000000
title: Graph Viewer — Local Interactive Graph Visualization
status: archived
tags: [graph, visualization, sigma, graphology, bun, vite]
---

# Graph Viewer — Local Interactive Graph Visualization

**Created:** 2026-03-19
**Updated:** 2026-03-19
**Owner:** aRustyDev

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Interactive graph visualization in the browser | Yes | Sigma.js renders nodes/edges from local JSON, drag/select/layout work |
| 2 | Agent-human bridge via file watching | Yes | Agent writes JSON → WebSocket push → UI offers reload within 2s |
| 3 | Full CRUD for graph data through the UI | Yes | Create/edit/delete nodes and edges, save to disk, undo/redo |
| 4 | Filtering and search | Yes | Filter by node/edge type, search by label, combine with AND logic |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Graph visualization | None (JSON files only) | Browser-based WebGL rendering | No UI exists |
| Agent integration | Manual file editing + reload | Auto-detect changes via fs.watch + WebSocket | No watcher |
| Graph editing | Edit JSON by hand | CRUD via browser UI with validation | No editor |
| View persistence | None | Positions/camera saved in .graph.lock.json | No lock files |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-0 | Spike & Validation | **done** | - | ForceAtlas2 worker, Graphology round-trip, WebSocket, fs.watch verified |
| phase-1 | Skeleton — Render + Interact + Layout | **done** | phase-0 | Graph renders, drag/select work, 3 layouts, file watcher + WebSocket live |
| phase-2 | Multi-File + Persistence | **done** | phase-1 | Switch graphs, save to disk, lock file positions restored |
| phase-3 | CRUD Operations | **done** | phase-2 | Create/edit/delete nodes+edges, undo/redo (50 ops) |
| phase-4 | Filtering | **done** | phase-3 | Filter by type, search by label, combine filters + subgraph model |
| phase-5 | Polish & Multi-Graph Overlay | **done** | phase-4 | Keyboard shortcuts, visual styling, edge cases (multi-graph skipped) |

### Phase Details

1. [Phase 0: Spike & Validation](./phase/0-spike.md)
2. [Phase 1: Skeleton — Render + Interact + Layout](./phase/1-skeleton.md)
3. [Phase 2: Multi-File + Persistence](./phase/2-persistence.md)
4. [Phase 3: CRUD Operations](./phase/3-crud.md)
5. [Phase 4: Filtering](./phase/4-filtering.md)
6. [Phase 5: Polish & Multi-Graph Overlay](./phase/5-polish.md)

## Architecture

See [refs/project-architecture.md](./refs/project-architecture.md) for full details.

**Stack:** Bun (backend) + Vite (frontend bundling) + Sigma.js v3 (WebGL) + Graphology (graph model) + Ajv (validation)

**Dev topology:**
```
Browser ←→ Vite (:5173) ──proxy /api/*──→ Bun API (:3000)
                           proxy /ws/*
```

**Key decisions:** Vanilla TypeScript (no React/Vue), event-driven architecture, JSON Schema as agent-human contract, `.graph.lock.json` for view state separation.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ForceAtlas2 web worker fails under Vite | Low | High | Phase 0 spike validates this; fallback to synchronous layout |
| Bun fs.watch unreliable | Low | High | Phase 0 spike validates; fallback to 5s polling |
| Graphology round-trip loses custom properties | Low | High | Phase 0 spike validates import→mutate→export preserves data |
| Sigma event model blocks edge creation UX | Medium | Medium | Phase 0 spike; alternative: toolbar mode toggle |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-19 | 2026-03-19 |
| Phase 0 complete (spike) | | |
| Phase 1 complete (skeleton) | | |
| Phase 2 complete (persistence) | | |
| Phase 3 complete (CRUD) | | |
| Phase 4 complete (filtering) | | |
| Phase 5 complete (polish) | | |

## Rollback Strategy

Each phase produces a working artifact. If a phase fails, revert to the prior phase's state. The project is greenfield with no existing dependencies — abandonment has zero cost.

## Project Location

Everything lives inside `cli/` alongside `ai-tools`. The entry point is `cli/bin/graph-viewer.ts` (Bun server). Vite builds the frontend client from `cli/client/graph-viewer/` into `cli/dist/graph-viewer/`. The Bun server serves those static assets in production mode.

```
cli/
├── bin/
│   ├── ai-tools.ts           # Existing CLI
│   └── graph-viewer.ts       # Bun.serve entry — API + WebSocket + static assets
├── lib/
│   ├── graph.ts              # Graphology wrapper: load, serialize, types
│   ├── graph-schema.ts       # Ajv validation for graph JSON
│   └── graph-lock.ts         # Lock file read/write/reconcile
├── server/graph-viewer/      # Server-side routes and file watcher
│   ├── routes/
│   │   ├── graphs.ts         # CRUD: list, load, save graph files
│   │   └── git.ts            # GET /api/git/status
│   ├── watcher.ts            # fs.watch → WebSocket broadcast
│   └── validation.ts         # Ajv validation wrapper
├── client/graph-viewer/      # Vite frontend source (browser code)
│   ├── main.ts               # Entry: init Sigma, connect WebSocket, mount UI
│   ├── styles.css            # Single CSS file (BEM with gv- prefix)
│   ├── state/                # store.ts, events.ts
│   ├── graph/                # source.ts, loader.ts
│   ├── interaction/          # drag.ts, selection.ts, crud.ts, undo.ts
│   ├── layout/               # manager.ts, presets.ts
│   ├── filter/               # engine.ts, reducers.ts
│   └── ui/                   # controls.ts, sidebar.ts, status.ts, toast.ts
├── test/
│   └── graph.test.ts         # Graph core tests (round-trip, lock, schema)
├── dist/graph-viewer/        # Vite build output (gitignored)
├── vite.graph-viewer.config.ts  # Vite config for graph-viewer client
├── package.json              # Shared — adds sigma, graphology, ajv deps
└── tsconfig.json             # Existing (server uses Bun types)
```

**TypeScript split:** Server/lib code uses the existing `tsconfig.json` (Bun types). Vite handles its own TS compilation for `client/graph-viewer/` via `vite.graph-viewer.config.ts` — no separate tsconfig needed for the client since Vite uses esbuild internally.

**Graph data** lives at `.data/graphs/` (alongside existing `.data/mcp/`):
```
.data/graphs/
├── manifest.json
├── schemas/graph.schema.json
├── example.json
└── example.graph.lock.json
```

## Notes

- Claude Code cannot open a browser — all programmatic verification uses CLI tools (curl, bun test). Visual verification deferred to human after each phase.
- Estimated total effort: 8–11 working days
- Core graph logic in `cli/lib/` is testable via `bun test` without the frontend
- Browser deps (`sigma`, `graphology-layout-forceatlas2`) added to shared `package.json` — cosmetic concern only, tree-shakes out of CLI code
- `concurrently` needed as dev dep for `bun run dev:graph` (Vite + Bun server in one terminal)
- See [refs/prompt.md](./refs/prompt.md) for implementation brief and session workflow
- See [refs/project-architecture.md](./refs/project-architecture.md) for data model, API contract, directory structure
