---
id: b1a2c3d4-e5f6-7890-abcd-ef1234567890
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 0: Spike & Validation"
status: pending
related:
  depends-on: []
---

# Phase 0: Spike & Validation

**ID:** `phase-0`
**Dependencies:** None
**Status:** pending
**Effort:** 0.5 day

## Objective

Eliminate integration risk before committing to the full build. Validate that Vite + Bun hybrid works, ForceAtlas2 bundles in a web worker, Graphology round-trips preserve data, WebSocket upgrades work in Bun, and fs.watch fires reliably.

## Success Criteria

- [ ] ForceAtlas2 runs in a web worker, positions update in Sigma renderer
- [ ] Graphology export preserves all custom node/edge properties through a full round-trip
- [ ] WebSocket connection established between Vite-proxied client and Bun server
- [ ] `fs.watch` callback fires when a file in a watched directory is written
- [ ] `bun run dev:server` starts, `curl http://localhost:3000/api/graphs` returns a response
- [ ] Vite proxy config works — `curl http://localhost:5173/api/graphs` proxies to Bun

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Graphology round-trip test | `.scripts/test/graph-spike.test.ts` | bun:test |
| Spike validation scripts | `.scripts/spike/` | Throwaway TypeScript scripts |
| Phase 0 results report | (conversation output) | Markdown table |

## Files

**Create:**
- `.scripts/test/graph-spike.test.ts` (Graphology round-trip validation — kept)
- `.scripts/spike/ws-test.ts` (WebSocket upgrade test — throwaway)
- `.scripts/spike/watch-test.ts` (fs.watch reliability test — throwaway)
- `.scripts/spike/worker-test.ts` (ForceAtlas2 worker test — throwaway)
- `.scripts/vite.graph-viewer.config.ts` (Vite config for client build)
- `.scripts/bin/graph-viewer.ts` (placeholder Bun.serve)

**Modify:**
- None

## Tasks

- [ ] Scaffold Vite + Bun hybrid project
- [ ] Verify ForceAtlas2 web worker bundles and runs under Vite
- [ ] Verify Graphology round-trip: JSON → Graph.import() → mutate → Graph.export() → JSON
- [ ] Verify Bun.serve() WebSocket upgrade works alongside HTTP routes
- [ ] Verify `fs.watch` on a directory fires reliably for file modifications
- [ ] Report results with pass/fail and any architecture deviations

## Notes

- Spike code is throwaway — won't survive into Phase 1
- If ForceAtlas2 worker fails, fallback to synchronous (acceptable for <1k nodes)
- If `fs.watch` is unreliable, fallback to 5s polling
