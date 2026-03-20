/**
 * Graph Viewer -- Bun.serve entry point.
 *
 * Serves the REST API (/api/*), WebSocket (/ws), and static assets (Vite
 * build output). In dev mode Vite proxies to this server; in production
 * this serves dist/ directly.
 *
 * File watcher monitors `.data/graphs/` and broadcasts change events to
 * every connected WebSocket client so the UI can live-reload graph data.
 */

import { resolve } from 'node:path'
import type { ServerWebSocket } from 'bun'
import { handleGitRoute } from '../server/graph-viewer/routes/git'
import { handleGraphsRoute, handleSchemasRoute } from '../server/graph-viewer/routes/graphs'
import { createWatcher, type FileChangeEvent } from '../server/graph-viewer/watcher'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = Number(process.env.GV_PORT) || 3000
const DIST_DIR = resolve(import.meta.dir, '../dist/graph-viewer')
const GRAPHS_DIR = resolve(import.meta.dir, '../../.data/graphs')

// ---------------------------------------------------------------------------
// WebSocket client tracking
// ---------------------------------------------------------------------------

/** All currently connected WebSocket clients. */
const wsClients = new Set<ServerWebSocket<unknown>>()

/**
 * Broadcast a message to every connected WebSocket client.
 * Silently removes clients that error on send (stale connections).
 */
function broadcast(data: FileChangeEvent): void {
  const payload = JSON.stringify(data)
  for (const ws of wsClients) {
    try {
      ws.send(payload)
    } catch {
      wsClients.delete(ws)
    }
  }
}

// ---------------------------------------------------------------------------
// File watcher
// ---------------------------------------------------------------------------

const watcher = createWatcher(GRAPHS_DIR)

watcher.onFileChange((event) => {
  console.log(
    `[watcher] ${event.type}: ${event.file}${event.graphId ? ` (graph: ${event.graphId})` : ''}`
  )
  broadcast(event)
})

watcher.start()

// ---------------------------------------------------------------------------
// HTTP + WebSocket server
// ---------------------------------------------------------------------------

const server = Bun.serve({
  port: PORT,

  async fetch(req, server) {
    const url = new URL(req.url)
    const { pathname } = url

    // -----------------------------------------------------------------------
    // WebSocket upgrade
    // -----------------------------------------------------------------------
    if (pathname === '/ws') {
      const upgraded = server.upgrade(req)
      if (!upgraded) {
        return new Response('WebSocket upgrade failed', { status: 400 })
      }
      return undefined as unknown as Response
    }

    // -----------------------------------------------------------------------
    // API routes
    // -----------------------------------------------------------------------

    // Health check
    if (pathname === '/api/health') {
      return Response.json({ status: 'ok' })
    }

    // Graph CRUD
    const graphsResponse = await handleGraphsRoute(req, pathname, GRAPHS_DIR)
    if (graphsResponse) return graphsResponse

    // Schema serving
    const schemasResponse = await handleSchemasRoute(req, pathname, GRAPHS_DIR)
    if (schemasResponse) return schemasResponse

    // Git status
    const gitResponse = await handleGitRoute(req, pathname, GRAPHS_DIR)
    if (gitResponse) return gitResponse

    // -----------------------------------------------------------------------
    // Static file serving (production mode)
    // -----------------------------------------------------------------------
    const staticPath = pathname === '/' ? '/index.html' : pathname
    const filePath = `${DIST_DIR}${staticPath}`
    const file = Bun.file(filePath)
    if (await file.exists()) {
      return new Response(file)
    }

    // SPA fallback: serve index.html for non-API, non-file paths
    if (!pathname.startsWith('/api/')) {
      const indexFile = Bun.file(`${DIST_DIR}/index.html`)
      if (await indexFile.exists()) {
        return new Response(indexFile)
      }
    }

    return new Response('Not found', { status: 404 })
  },

  websocket: {
    open(ws) {
      wsClients.add(ws)
      console.log(`[ws] Client connected (${wsClients.size} total)`)
    },

    close(ws) {
      wsClients.delete(ws)
      console.log(`[ws] Client disconnected (${wsClients.size} total)`)
    },

    message(ws, message) {
      // Echo back for ping/pong or future client-to-server messages
      ws.send(`echo:${message}`)
    },
  },
})

// ---------------------------------------------------------------------------
// Graceful shutdown
// ---------------------------------------------------------------------------

function shutdown(): void {
  console.log('\nShutting down...')
  watcher.stop()
  server.stop()
  process.exit(0)
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)

// ---------------------------------------------------------------------------
// Startup banner
// ---------------------------------------------------------------------------

console.log(`Graph Viewer server running at http://localhost:${PORT}`)
console.log(`  API:       http://localhost:${PORT}/api/graphs`)
console.log(`  WebSocket: ws://localhost:${PORT}/ws`)
console.log(`  Graphs:    ${GRAPHS_DIR}`)
