# Graph Viewer — Claude Code Implementation Brief

> **How to use this file:** This is the root implementation brief. It is split into two parts:
> - **Part 1 (Reference)** — persistent context that applies across all sessions. Do not re-read ARCHITECTURE.md and ROADMAP.md if you have already read them in this session.
> - **Part 2 (Session Instructions)** — what to do right now. Update this section when starting a new phase.

---

# PART 1: PROJECT REFERENCE (persistent across sessions)

## GOAL

Implement "Graph Viewer" — a local-only static site for interactive visualization and editing of node/edge graphs, backed by local JSON data files. The system uses Sigma.js v3 for WebGL rendering, Graphology for the graph data model, Bun as the backend runtime, and Vite for frontend bundling.

## REFERENCE DOCUMENTS

Before writing any code in a new session, read these files in the project root:

| File | Path | Contents |
|------|------|----------|
| Architecture | `./ARCHITECTURE.md` | Module structure, data model, API contract, state management, error handling |
| Roadmap | `./ROADMAP.md` | Phased delivery plan with acceptance criteria per phase |
| This file | `./PROMPT.md` | Goal, context, constraints, workflow rules |

These three documents are the authoritative specification. If they contradict each other, ask — do not resolve the contradiction yourself.

## CONTEXT

### What this project is

A local developer tool that serves as an interface between a human (me, via browser UI) and an AI agent (via direct JSON file manipulation on disk). The agent reads/writes JSON graph data and JSON Schema files. I interact exclusively through the browser UI. The WebUI detects when the agent changes files and offers to reload.

**This means:** The file watcher → WebSocket → reload-offer flow is the most important integration path. It is Phase 1 infrastructure, not Phase 5 polish.

### Key design decisions (already made — do not revisit)

1. **Vite + Bun hybrid**: Vite bundles the frontend + provides HMR. Bun runs the backend API + file I/O + WebSocket. In dev mode, Vite proxies `/api/*` and WebSocket `/ws` to Bun. In production, Bun serves Vite's `dist/` output as static files alongside API routes.

2. **Graphology as single source of truth in-browser**: All graph state lives in one Graphology instance. Sigma renders from it. CRUD mutates it. Serialization exports from it. No parallel/shadow state.

3. **JSON Schema as agent-human contract**: `data/schemas/graph.schema.json` defines structural shape. Validated server-side (Ajv) on save. Does NOT encode graph-level invariants (e.g., referential integrity of edge source/target). Structural validation only.

4. **`.graph.lock.json` for view state**: Node positions, camera state, layout preferences — separated from graph data. 1:1 relationship with graph data files. The agent never touches lock files.

5. **`data/manifest.json` for graph registry**: Enumerates available graphs and their schema associations. Source of truth for what graphs exist.

6. **`_source` metadata on all nodes/edges**: On load, tag every node/edge with which file it came from. Enables future multi-graph overlay without refactoring.

7. **WebSocket for file change push**: Bun watches `data/` → broadcasts via WebSocket → client shows toast + reload offer. No auto-reload.

8. **ID convention**: `node-{nanoid}` and `edge-{nanoid}`. Enforced by JSON Schema `pattern`. Use the `nanoid` package.

9. **Vanilla TypeScript UI**: No React/Vue/Svelte. Centralized state store + typed EventEmitter for cross-module communication.

10. **Event-driven client architecture**: Modules communicate via typed event bus. Direct imports between interaction/layout/filter/ui modules are prohibited. Graphology instance and state store are shared data; events coordinate.

### Technical constraints

- Sigma.js is browser-only (WebGL). Bun never renders graphs.
- ForceAtlas2 runs in a web worker. Must verify it bundles under Vite in Phase 0. Fallback: synchronous execution (acceptable for <1k nodes).
- Bun's `fs.watch` behavior may differ from Node's. Verify in Phase 0.
- Bun server binds to `localhost` only. No auth, no CORS, no public exposure.
- **Claude Code cannot open a browser.** All programmatic verification must use CLI tools (curl, bun test, process exit codes). Visual verification is deferred to the human after each phase.

## PRIORITIES (in order)

1. **Working software** — every phase produces something I can open in a browser and use
2. **Clean separation** — server code has no browser deps, client code has no Bun deps, shared types in `src/shared/`
3. **Agent integration path** — file watcher + WebSocket + reload is critical infrastructure
4. **Incremental delivery** — don't build Phase 3 features during Phase 1

## TOOLING & CONFIGURATION DECISIONS

### Dev scripts (`package.json`)

```jsonc
{
  "scripts": {
    "dev": "concurrently \"bun run dev:server\" \"bun run dev:client\"",
    "dev:server": "bun --watch src/server/index.ts",
    "dev:client": "vite",
    "build": "vite build",
    "preview": "bun src/server/index.ts",  // serves built assets + API
    "typecheck": "tsc --noEmit"
  }
}
```

`concurrently` (or a similar process runner) starts both Vite and Bun in one terminal for `bun run dev`. If you prefer two terminals, document it in README.md — but a single `dev` command is strongly preferred.

### TypeScript configuration

- `strict: true`
- `target: "ES2022"`
- `module: "ESNext"`, `moduleResolution: "bundler"`
- Separate `tsconfig.json` for server vs. client is acceptable if needed (Bun server uses Bun types, client uses DOM types)

### CSS strategy

Use a **single plain CSS file** (`src/client/styles.css`) imported in `main.ts`. No CSS modules, no preprocessors, no CSS-in-JS. The UI scope is small enough that a single file with BEM-style class naming is sufficient. If it grows past ~500 lines, split into `layout.css`, `sidebar.css`, `controls.css` — but don't do this preemptively.

### Vite configuration specifics

```typescript
// vite.config.ts — key settings
{
  root: './',
  publicDir: 'public',
  build: { outDir: 'dist' },
  server: {
    proxy: {
      '/api': { target: 'http://localhost:3000' },
      '/ws': { target: 'ws://localhost:3000', ws: true }
    }
  }
}
```

The WebSocket proxy requires `ws: true` — this is distinct from HTTP proxying and is a common misconfiguration.

### Sample data requirements

`data/example.json` must exercise the full schema:
- **15–20 nodes** spanning all defined types (`Concept`, `Component`, `Document`, `Fragment`)
- **20–25 edges** with at least 3 different edge types (e.g., `relates_to`, `depends_on`, `contains`)
- **Diverse properties**: at least 3 distinct property keys across node types, with a mix of string and enum-like values
- **Domain**: Use a software architecture domain (e.g., a simplified ML pipeline with concepts like "Training Data", "Feature Extraction", "Model", "Inference API", components like "Data Loader", "GPU Cluster", documents like "API Spec", fragments like "Config Schema"). This gives filtering and type-based features meaningful content to work with in later phases.

## NON-GOALS

Do not build any of these, even if they seem useful:

- Authentication or access control
- Multi-user collaboration / CRDT
- Git commit/branch UI (user runs git manually)
- Schema editor in the browser (agent manages schemas)
- Image/PNG/SVG export
- Graph algorithm analysis (centrality, clustering)
- Server-side rendering
- React, Vue, Svelte, or any UI framework
- Database or persistent storage beyond JSON files
- Remote deployment
- Unit test coverage targets or CI pipeline (tests are ad-hoc verification, not gated)

## FAILURE CONDITIONS

**Stop immediately, report the issue, and wait for my input if any of these occur:**

1. **ForceAtlas2 web worker fails to bundle under Vite** — do not silently switch to synchronous. Report the error output.
2. **Graphology round-trip loses data** — custom `properties` objects must survive `import()` → mutate → `export()` unchanged.
3. **Bun `fs.watch` is unreliable** — misses events, double-fires unpredictably, or doesn't fire at all.
4. **Sigma's event model blocks a required interaction pattern** — e.g., no clean way to do "select source → click target" for edge creation.
5. **Architecture drift** — you need a module, dependency, or pattern not in ARCHITECTURE.md. (Exception: Phase 0 spike has permission to discover and report deviations — see Phase 0 workflow below.)
6. **Scope creep** — a task is taking 2x expected effort. Flag it as a possible design problem rather than powering through.
7. **Document contradiction** — ARCHITECTURE.md, ROADMAP.md, and PROMPT.md disagree. Do not resolve it yourself.

---

# PART 2: SESSION INSTRUCTIONS (update per session)

## CURRENT PHASE: 0 (Spike & Validation)

### Workflow for this session

Follow these steps in exact order:

1. **Read reference docs.** Read `ARCHITECTURE.md` and `ROADMAP.md` in full. Do not skim.

2. **Output your Phase 0 plan.** Before writing any code, output a numbered task list of what you will do to validate each spike point. Format:
   ```
   ## Phase 0 Plan
   1. [task] — [what it validates]
   2. [task] — [what it validates]
   ...
   ```
   Then **stop and wait for my approval.** Do not proceed until I confirm.

3. **Execute the plan.** After approval, implement each task. After each task, report:
   - What you did
   - Whether it passed or failed
   - If failed: exact error output

4. **Phase 0 spike permissions.** During Phase 0 only, you have permission to:
   - Install additional dev dependencies if needed for the spike (document what and why)
   - Deviate from ARCHITECTURE.md to test alternatives (document what you tried)
   - Make throwaway code that won't survive into Phase 1
   
   You must still report all deviations. The spike's job is to surface surprises, not hide them.

5. **Phase 0 completion report.** When all spike points are validated, output a summary:
   ```
   ## Phase 0 Results
   | Spike Point | Status | Notes |
   |------------|--------|-------|
   | Vite + Bun proxy | ✅/❌ | ... |
   | ForceAtlas2 worker | ✅/❌ | ... |
   | Graphology round-trip | ✅/❌ | ... |
   | WebSocket | ✅/❌ | ... |
   | fs.watch | ✅/❌ | ... |
   
   ### Deviations from ARCHITECTURE.md
   - [list any discovered issues or needed changes]
   
   ### Recommended architecture updates
   - [list any changes to ARCHITECTURE.md based on findings]
   ```
   Then **stop and wait.** I will review results and approve moving to Phase 1.

### Phase 0 acceptance criteria (programmatically verifiable)

These are what Claude Code can verify without a browser:

- [ ] `bun run dev:server` starts without errors, `curl http://localhost:3000/api/graphs` returns a response
- [ ] `bun run dev:client` starts Vite dev server without errors
- [ ] Vite proxy config exists and `curl http://localhost:5173/api/graphs` proxies to Bun
- [ ] `graphology` round-trip test: write a script that imports JSON → adds a node with custom properties → exports → asserts the added node's properties are preserved. Run it with `bun run`, exits 0.
- [ ] WebSocket test: write a script that connects to `ws://localhost:3000/ws` and receives a message. Run it, exits 0.
- [ ] `fs.watch` test: write a script that watches `data/`, writes to a file, asserts callback fires. Run it, exits 0.
- [ ] ForceAtlas2 worker: Vite builds without errors when importing `graphology-layout-forceatlas2` with worker usage. (Visual verification — that it actually renders — is deferred to my manual check.)

### What to do after Phase 0

After I approve Phase 0 results, I will update this section to say "CURRENT PHASE: 1" with Phase 1-specific workflow instructions. The Phase 1 workflow will follow the same pattern: plan → approval → execute → report → approval.

---

## PHASE WORKFLOW TEMPLATE (for reference — applied per phase)

Every phase follows this cycle:

```
1. Read phase scope from ROADMAP.md
2. Output numbered implementation plan → STOP, wait for approval
3. Implement incrementally, verify each sub-task
4. Output completion report with:
   - What was built
   - What was verified (programmatically)
   - What needs manual verification (browser)
   - Any deviations or issues
5. STOP, wait for approval before next phase
```

### Verification split

| Can verify programmatically (Claude Code does this) | Requires manual check (I do this) |
|-----------------------------------------------------|-----------------------------------|
| Server starts without errors | Graph renders correctly in browser |
| API endpoints return expected status codes and shapes | Node drag feels responsive |
| TypeScript compiles without errors (`bun run typecheck`) | Layout algorithms produce reasonable arrangements |
| JSON Schema validation rejects invalid data | Toast notifications appear and are readable |
| WebSocket connection establishes | Sidebar UI is usable |
| File watcher fires on modification | Overall visual quality |
| Graphology serialization round-trips correctly | |
| Git status command returns expected output | |

Claude Code should run all programmatic verifications and report results. Do not claim visual/UX criteria are met — flag them as "requires manual verification."

---

## CONVENTIONS

### Code style
- No comments that restate what the code does. Comments explain *why*, not *what*.
- Prefer explicit types over inference for function signatures and public APIs. Inference is fine for locals.
- Error messages should include enough context to diagnose: what was attempted, what went wrong, what file/ID was involved.

### Git (if initialized)
- Do not commit automatically. I will commit manually at phase boundaries.
- Do not initialize a git repo unless I ask. The project may already be in one.

### File operations
- All file writes in the server use atomic write (write to `.tmp`, rename). Never write directly to the target path.
- Lock file writes are the only exception (non-critical, overwrite is fine).

### Naming
- Files: `kebab-case.ts`
- Types/interfaces: `PascalCase`
- Functions/variables: `camelCase`
- Event names: `domain:action` (e.g., `graph:node-added`, `filter:changed`, `ws:reconnected`)
- CSS classes: `gv-block__element--modifier` (BEM with `gv-` prefix to avoid collisions)
