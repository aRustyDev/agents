# Graph Viewer — Project Architecture

## Overview

A local static site for interactive visualization and editing of node/edge graphs, backed by local JSON data files. The system serves as an interface between a developer (via WebUI) and an AI agent (via direct JSON file manipulation). The agent reads/writes JSON and JSON Schema files; the developer interacts exclusively through the browser UI.

## Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Runtime | Bun | Backend server, package management |
| Build | Vite | Frontend bundling, HMR, dev server |
| Graph model | Graphology | In-memory graph data structure |
| Renderer | Sigma.js v3 | WebGL-based graph rendering + interaction |
| Validation | Ajv | JSON Schema validation (server + client) |
| Transport | WebSocket | Server→client push for file change notifications |

### Why Vite + Bun (not Bun bundler alone)

Bun serves three roles: JS/TS runtime, package manager, and bundler. These are independent. For this project, Bun handles runtime (1) and packages (2), but Vite handles bundling (3) because:

- **Web Worker support**: ForceAtlas2 runs in a web worker. Vite's `?worker` import syntax and Rollup-based bundling handles this reliably. Bun's bundler support for workers is less battle-tested.
- **Browser HMR**: Vite provides true hot module replacement in the browser. `bun --hot` restarts the server process — it doesn't do browser HMR.
- **Plugin ecosystem**: Vite has mature plugins for edge cases (raw imports, CSS modules, etc.).
- **Production builds**: Rollup-backed tree-shaking, code splitting, asset hashing.

**Dev mode topology:**
```
Browser ←→ Vite dev server (:5173) ──proxy /api/*──→ Bun API server (:3000)
                                     proxy /ws/*
```

**Production/local deployment topology:**
```
Bun server (:3000)
  ├── serves static assets from dist/   (Vite build output)
  ├── handles /api/* routes
  └── handles /ws WebSocket connections
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Browser (SPA)                                           │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐            │
│  │ Sigma.js │←→│Graphology │←→│  State     │            │
│  │ Renderer │  │ Instance  │  │  Store     │            │
│  └──────────┘  └───────────┘  └─────┬─────┘            │
│       ↑                             │                   │
│  ┌────┴─────┐  ┌───────────┐  ┌─────┴─────┐            │
│  │Interaction│  │  Filter   │  │  Layout   │            │
│  │ Handlers │  │  Engine   │  │  Manager  │            │
│  └──────────┘  └───────────┘  └───────────┘            │
│       ↑              ↑              ↑                   │
│  ┌────┴──────────────┴──────────────┴────┐              │
│  │              UI Layer                  │              │
│  │  Controls │ Sidebar │ Status │ Toast   │              │
│  └────────────────────┬──────────────────┘              │
│                       │                                 │
│              HTTP (fetch) + WebSocket                   │
└───────────────────────┼─────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────┐
│ Bun Server            │                                 │
│                       │                                 │
│  ┌────────────────────┴──────────────────┐              │
│  │           Router                       │              │
│  │  /api/graphs/* │ /api/git/* │ /ws      │              │
│  └───┬────────────────┬──────────┬───────┘              │
│      │                │          │                       │
│  ┌───┴───┐    ┌───────┴──┐  ┌───┴──────┐               │
│  │ Graph │    │   Git    │  │ File     │               │
│  │ Routes│    │  Routes  │  │ Watcher  │               │
│  └───┬───┘    └──────────┘  └───┬──────┘               │
│      │                          │                       │
│  ┌───┴──────┐            ┌──────┴──────┐               │
│  │Validation│            │  fs.watch   │               │
│  │  (Ajv)   │            │  on data/   │               │
│  └──────────┘            └─────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Filesystem (data/)                                      │
│                                                         │
│  manifest.json           ← enumerates graphs + schemas  │
│  schemas/                                               │
│    graph.schema.json     ← JSON Schema contract         │
│  my-graph.json           ← graph data                   │
│  my-graph.graph.lock.json← view state (positions, etc.) │
│  other-graph.json                                       │
│  other-graph.graph.lock.json                            │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
graph-viewer/
├── src/
│   ├── server/
│   │   ├── index.ts                 # Bun.serve() entry — static files, API, WebSocket
│   │   ├── routes/
│   │   │   ├── graphs.ts            # CRUD: list, load, save graph files
│   │   │   └── git.ts               # GET /api/git/status
│   │   ├── watcher.ts               # fs.watch on data/ → WebSocket broadcast
│   │   ├── validation.ts            # Ajv validation against schemas
│   │   └── fs-helpers.ts            # Read/write/atomic-save helpers
│   │
│   ├── client/
│   │   ├── main.ts                  # Entry: init Sigma, connect WebSocket, mount UI
│   │   ├── state/
│   │   │   ├── store.ts             # Centralized state (graph, selection, filters, dirty)
│   │   │   └── events.ts            # Typed EventEmitter for cross-module communication
│   │   ├── graph/
│   │   │   ├── source.ts            # GraphSource class: file path, schema ref, metadata
│   │   │   ├── loader.ts            # JSON → Graphology (tags _source, _type metadata)
│   │   │   ├── serializer.ts        # Graphology → JSON (partitions by _source on save)
│   │   │   ├── lock.ts              # Read/write .graph.lock.json (positions, camera, layout)
│   │   │   └── reconcile.ts         # Reconcile lock file with graph changes (orphan cleanup)
│   │   ├── interaction/
│   │   │   ├── drag.ts              # Node drag handler (Sigma mouse events)
│   │   │   ├── crud.ts              # Add/remove nodes/edges (mutates Graphology + state)
│   │   │   └── selection.ts         # Click/hover selection, multi-select
│   │   ├── layout/
│   │   │   ├── manager.ts           # Layout algorithm switcher + worker lifecycle
│   │   │   └── presets.ts           # ForceAtlas2, circular, random configs
│   │   ├── filter/
│   │   │   ├── engine.ts            # Property-based filter logic
│   │   │   └── reducers.ts          # Sigma nodeReducer/edgeReducer for visibility/styling
│   │   └── ui/
│   │       ├── controls.ts          # Layout selector, file picker, action buttons
│   │       ├── sidebar.ts           # Filter panel, property inspector/editor
│   │       ├── status.ts            # Git dirty indicator, connection status
│   │       └── toast.ts             # Save/error/reload notifications
│   │
│   └── shared/
│       ├── types.ts                 # Shared types: API contracts, graph schema runtime types
│       └── constants.ts             # Shared constants: API paths, event names
│
├── data/
│   ├── manifest.json                # Graph registry: file → schema mapping
│   ├── schemas/
│   │   └── graph.schema.json        # JSON Schema contract
│   ├── example.json                 # Sample graph data
│   └── example.graph.lock.json      # Sample view state
│
├── public/
│   └── index.html                   # SPA shell
│
├── vite.config.ts                   # Vite config with proxy to Bun backend
├── tsconfig.json
├── bunfig.toml
├── package.json
└── README.md
```

## Data Model

### manifest.json

Enumerates all graph files and their schema associations. This is what the file picker reads.

```jsonc
{
  "version": 1,
  "graphs": [
    {
      "id": "example",
      "file": "example.json",
      "schema": "schemas/graph.schema.json",
      "label": "Example Graph",           // display name in UI
      "description": "Sample graph data"  // optional
    }
  ]
}
```

### Graph Data (*.json)

```jsonc
{
  "metadata": {
    "id": "example",
    "version": 1,
    "created": "2026-03-18T00:00:00Z",
    "modified": "2026-03-18T00:00:00Z"
  },
  "nodes": [
    {
      "id": "node-a1b2c3",       // nanoid, prefixed by convention
      "type": "Concept",
      "label": "Neural Network",
      "properties": {             // type-specific, schema-defined
        "domain": "ML",
        "complexity": "high"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-d4e5f6",
      "source": "node-a1b2c3",
      "target": "node-g7h8i9",
      "type": "relates_to",
      "properties": {
        "weight": 0.8
      }
    }
  ]
}
```

### View State (*.graph.lock.json)

Separated from graph data so the agent never needs to care about rendering concerns.

```jsonc
{
  "version": 1,
  "graphId": "example",
  "layout": {
    "algorithm": "forceatlas2",
    "params": { "gravity": 1.0, "scalingRatio": 2.0 }
  },
  "positions": {
    "node-a1b2c3": { "x": 120.5, "y": -34.2 },
    "node-g7h8i9": { "x": 200.0, "y": 50.0 }
  },
  "view": {
    "camera": { "x": 0, "y": 0, "ratio": 1.0, "angle": 0 }
  },
  "filters": {}  // optional: persisted filter state
}
```

**Lock file reconciliation rules:**
- On load: if lock file has positions for node IDs not in the graph → drop them (orphans from deleted nodes)
- On load: if graph has nodes without positions in lock file → assign positions via the configured layout algorithm
- On save: always write positions for all current nodes

### JSON Schema (graph.schema.json)

Defines the structural contract between agent and UI. Validates field types, required properties, enum values. Does NOT encode graph-level invariants (e.g., "edge source must reference existing node").

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Graph Data",
  "type": "object",
  "required": ["metadata", "nodes", "edges"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["id", "version"],
      "properties": {
        "id": { "type": "string" },
        "version": { "type": "integer", "minimum": 1 },
        "created": { "type": "string", "format": "date-time" },
        "modified": { "type": "string", "format": "date-time" }
      }
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "label"],
        "properties": {
          "id": { "type": "string", "pattern": "^node-[a-zA-Z0-9]+$" },
          "type": { "type": "string", "enum": ["Concept", "Component", "Document", "Fragment"] },
          "label": { "type": "string", "minLength": 1 },
          "properties": { "type": "object" }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "source", "target", "type"],
        "properties": {
          "id": { "type": "string", "pattern": "^edge-[a-zA-Z0-9]+$" },
          "source": { "type": "string" },
          "target": { "type": "string" },
          "type": { "type": "string" },
          "properties": { "type": "object" }
        }
      }
    }
  }
}
```

**NOTE:** The schema above is a starting template. The node `type` enum and edge `type` values should be customized per project. The `properties` object on nodes/edges is intentionally loose (`"type": "object"`) — tighten it per node type using JSON Schema `oneOf` + discriminator if you need strict per-type validation.

### ID Generation Convention

All IDs use `nanoid` (21-char default) with a type prefix:
- Nodes: `node-{nanoid}` (e.g., `node-V1StGXR8_Z5jdHi6B-myT`)
- Edges: `edge-{nanoid}` (e.g., `edge-FkDm3iR9_Q7nJhY2A-pLx`)

This convention is enforced by the schema `pattern` field. Both the UI (on create) and the agent (on write) must follow it. Prefixes prevent ambiguity and make grep/debugging easier.

## API Contract

All endpoints prefixed with `/api/`.

### Graph Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/graphs` | List all graphs from manifest.json |
| `GET` | `/api/graphs/:id` | Load graph JSON + lock file |
| `PUT` | `/api/graphs/:id` | Save graph JSON (validates against schema) |
| `PUT` | `/api/graphs/:id/lock` | Save lock file (positions, camera, layout) |
| `POST` | `/api/graphs` | Create new graph (adds to manifest) |
| `GET` | `/api/schemas/:name` | Load a JSON Schema file |

### Git Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/git/status` | Returns dirty/clean status for data/ directory |

### WebSocket

| Event (server→client) | Payload | Trigger |
|-----------------------|---------|---------|
| `file:changed` | `{ file: string, graphId: string }` | fs.watch detects modification in data/ |
| `file:created` | `{ file: string }` | New file in data/ |
| `file:deleted` | `{ file: string, graphId: string }` | File removed from data/ |

Client behavior on `file:changed`:
1. If the changed graph is currently loaded → show toast "Graph updated externally. Reload?"
2. User confirms → reload graph data, reconcile lock file
3. User declines → continue with stale data, mark as diverged

## Client State Management

No framework. Vanilla TS with a centralized store + typed event bus.

```typescript
// Conceptual — not literal implementation
interface AppState {
  // Graph data
  activeGraphId: string | null;
  loadedSources: Map<string, GraphSource>;  // for future multi-graph
  graph: Graph;                              // Graphology instance

  // View state
  selectedNodes: Set<string>;
  selectedEdges: Set<string>;
  hoveredNode: string | null;

  // Filter state
  activeFilters: FilterSet;

  // UI state
  isDirty: boolean;               // unsaved local changes
  isExternallyModified: boolean;  // file changed on disk since last load
  gitStatus: 'clean' | 'dirty' | 'unknown';
  wsConnected: boolean;
}
```

Modules communicate through the event bus, not direct imports:
- `crud.ts` emits `graph:node-added` → `status.ts` listens, sets dirty flag
- `watcher` WebSocket emits `file:changed` → `toast.ts` listens, shows notification
- `filter/engine.ts` emits `filter:changed` → `reducers.ts` listens, updates Sigma reducers

## Error Handling Strategy

| Layer | Pattern |
|-------|---------|
| Server file I/O | Try/catch, return 500 with error message. Atomic writes (write to tmp, rename). |
| Schema validation | On save: reject with 400 + validation errors. On load: warn in UI, render anyway. |
| WebSocket | Auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s). Status indicator in UI. |
| Client state | Never throw from event handlers. Log errors, show toast. |
| Lock file reconciliation | Silent — drop orphans, assign defaults for new nodes. Log to console. |

## Performance Boundaries

Sigma.js + WebGL handles 10k–50k nodes comfortably. Beyond that:
- Label rendering becomes the bottleneck → use `labelRenderedSizeThreshold`
- ForceAtlas2 convergence time scales poorly → run with iteration cap
- Filter reducers on every frame → debounce filter changes

For this project's scope (agent-generated concept/ontology graphs), graphs will likely stay under 1k nodes. No special optimization needed.

## Security Considerations

This is a **local-only** tool. No authentication, no CORS restrictions, no public exposure. The Bun server binds to `localhost` only. If you ever need remote access, add authentication before exposing the port.
