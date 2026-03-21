---
id: c2b3d4e5-f6a7-8901-bcde-f12345678901
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 1: Skeleton — Render + Interact + Layout"
status: pending
related:
  depends-on: [b1a2c3d4-e5f6-7890-abcd-ef1234567890]
---

# Phase 1: Skeleton — Render + Interact + Layout

**ID:** `phase-1`
**Dependencies:** phase-0
**Status:** pending
**Effort:** 1.5–2 days

## Objective

Load and render a graph from a local JSON file. Basic interaction (drag, select), layout switching (ForceAtlas2, circular, random), file watcher with WebSocket push, and git status indicator.

## Success Criteria

- [ ] Open browser → see rendered graph with labeled nodes and edges
- [ ] Drag nodes, positions update in real-time
- [ ] Switch between 3 layout algorithms
- [ ] Edit `data/example.json` externally → UI shows toast within 2 seconds
- [ ] Git dirty indicator reflects actual working tree status
- [ ] State store and typed event bus operational

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Graph core library | `.scripts/lib/graph.ts` | Graphology wrapper (load, serialize, types) |
| Graph lock library | `.scripts/lib/graph-lock.ts` | Lock file read/write/reconcile |
| Graph schema library | `.scripts/lib/graph-schema.ts` | Ajv validation for graph JSON |
| Graph core tests | `.scripts/test/graph.test.ts` | bun:test |
| Server entry | `.scripts/bin/graph-viewer.ts` | Bun.serve with API + WebSocket + static |
| Server routes | `.scripts/server/graph-viewer/routes/` | graphs.ts, git.ts |
| File watcher | `.scripts/server/graph-viewer/watcher.ts` | fs.watch → WebSocket broadcast |
| Client entry | `.scripts/client/graph-viewer/main.ts` | Sigma init + WebSocket + UI mount |
| Interaction handlers | `.scripts/client/graph-viewer/interaction/` | drag.ts, selection.ts |
| Layout manager | `.scripts/client/graph-viewer/layout/` | manager.ts, presets.ts |
| State + Events | `.scripts/client/graph-viewer/state/` | store.ts, events.ts |
| Styles | `.scripts/client/graph-viewer/styles.css` | Single CSS file (BEM with gv- prefix) |
| Sample data | `.data/graphs/example.json` | 15–20 nodes, 20–25 edges |
| HTML shell | `.scripts/client/graph-viewer/index.html` | SPA container |

## Files

**Create (core library):**
- `.scripts/lib/graph.ts` — Graphology wrapper: load JSON, serialize, types, _source tagging
- `.scripts/lib/graph-lock.ts` — Lock file read/write/reconcile
- `.scripts/lib/graph-schema.ts` — Ajv validation for graph JSON
- `.scripts/test/graph.test.ts` — Round-trip, lock reconciliation, schema validation tests

**Create (server):**
- `.scripts/bin/graph-viewer.ts` — Bun.serve entry (API + WebSocket + static assets)
- `.scripts/server/graph-viewer/routes/graphs.ts` — CRUD endpoints
- `.scripts/server/graph-viewer/routes/git.ts` — Git status endpoint
- `.scripts/server/graph-viewer/watcher.ts` — fs.watch → WebSocket broadcast

**Create (client — Vite source):**
- `.scripts/client/graph-viewer/main.ts`, `.scripts/client/graph-viewer/styles.css`
- `.scripts/client/graph-viewer/index.html`
- `.scripts/client/graph-viewer/state/store.ts`, `.scripts/client/graph-viewer/state/events.ts`
- `.scripts/client/graph-viewer/graph/source.ts`, `.scripts/client/graph-viewer/graph/loader.ts`
- `.scripts/client/graph-viewer/interaction/drag.ts`, `.scripts/client/graph-viewer/interaction/selection.ts`
- `.scripts/client/graph-viewer/layout/manager.ts`, `.scripts/client/graph-viewer/layout/presets.ts`
- `.scripts/client/graph-viewer/ui/controls.ts`, `.scripts/client/graph-viewer/ui/status.ts`, `.scripts/client/graph-viewer/ui/toast.ts`

**Create (config + data):**
- `.scripts/vite.graph-viewer.config.ts` — Vite config for client build
- `.data/graphs/manifest.json`, `.data/graphs/example.json`
- `.data/graphs/schemas/graph.schema.json`

**Modify:**
- `.scripts/package.json` — add sigma, graphology, ajv, concurrently deps
- `.gitignore` — add `.scripts/dist/`

## Tasks

- [ ] Implement `.scripts/lib/graph.ts` — Graphology wrapper with load/serialize/types
- [ ] Implement `.scripts/lib/graph-lock.ts` — lock file read/write/reconcile
- [ ] Implement `.scripts/lib/graph-schema.ts` — Ajv schema validation
- [ ] Write `.scripts/test/graph.test.ts` — round-trip, reconciliation, validation tests
- [ ] Add deps to `.scripts/package.json` (sigma, graphology, graphology-layout-forceatlas2, ajv, concurrently)
- [ ] Create `.scripts/vite.graph-viewer.config.ts` with proxy to Bun backend
- [ ] Implement `.scripts/bin/graph-viewer.ts` — Bun.serve with API routes + static serving
- [ ] Implement server routes and file watcher
- [ ] Implement client entry, Sigma renderer, state store + typed EventEmitter
- [ ] Create `styles.css` with base layout and BEM conventions (`gv-` prefix)
- [ ] Implement node drag handler (Sigma mouse events)
- [ ] Implement click-to-select, click-canvas-to-deselect
- [ ] Implement layout manager with ForceAtlas2 (worker), circular, random presets
- [ ] Implement WebSocket client with auto-reconnect
- [ ] Implement git status endpoint + UI indicator
- [ ] Create sample data at `.data/graphs/` (15–20 nodes, 4 types, 3 edge types)

## Notes

- Core graph logic in `.scripts/lib/` is testable via `bun test` without the frontend
- Server in `.scripts/server/graph-viewer/` imports from `.scripts/lib/` for graph operations
- Client code in `.scripts/client/graph-viewer/` is browser-only (DOM types, no Bun APIs)
- Vite builds client to `.scripts/dist/graph-viewer/` (gitignored)
- `bun run dev:graph` starts both Vite and Bun server via `concurrently`
- ForceAtlas2 runs in a web worker; provide start/stop toggle with convergence timeout
- WebSocket auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s)
- Sample data should use software architecture domain (ML pipeline concepts)
