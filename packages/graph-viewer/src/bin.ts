/**
 * Graph Viewer -- Node-compatible HTTP + WS entry point.
 *
 * Uses `node:http` + `ws` package so this file runs on both Bun and Node.js.
 *
 * Serves the REST API (/api/*), WebSocket (/ws), and static assets (Vite
 * build output). In dev mode Vite proxies to this server; in production
 * this serves dist/ directly.
 *
 * File watcher monitors `.data/graphs/` and broadcasts change events to
 * every connected WebSocket client so the UI can live-reload graph data.
 */

import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer, type IncomingMessage, type ServerResponse } from 'node:http'
import { extname, resolve } from 'node:path'
import { currentDir } from '@agents/core/runtime'
import { WebSocket, WebSocketServer } from 'ws'
import { handleGitRoute } from './server/routes/git'
import { handleGraphsRoute, handleSchemasRoute } from './server/routes/graphs'
import { createWatcher, type FileChangeEvent } from './server/watcher'

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PORT = Number(process.env.GV_PORT) || 3000
const __dir = currentDir(import.meta)
const DIST_DIR = resolve(__dir, '../dist/graph-viewer')
const GRAPHS_DIR = resolve(__dir, '../../../.data/graphs')

// ---------------------------------------------------------------------------
// MIME types for static file serving
// ---------------------------------------------------------------------------

const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.mjs': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.map': 'application/json',
}

// ---------------------------------------------------------------------------
// WebSocket client tracking
// ---------------------------------------------------------------------------

/** All currently connected WebSocket clients. */
const wsClients = new Set<WebSocket>()

/**
 * Broadcast a message to every connected WebSocket client.
 * Silently removes clients that error on send (stale connections).
 */
function broadcast(data: FileChangeEvent): void {
  const payload = JSON.stringify(data)
  for (const ws of wsClients) {
    try {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(payload)
      }
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
// Helpers: bridge Web API Response to node:http ServerResponse
// ---------------------------------------------------------------------------

/**
 * Convert an IncomingMessage to a Web API Request object.
 *
 * Reads the full body from the stream so route handlers (which expect the
 * Web API Request interface) can call `.json()`, `.text()`, etc.
 */
function toWebRequest(req: IncomingMessage): Promise<Request> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = []
    req.on('data', (chunk: Buffer) => chunks.push(chunk))
    req.on('end', () => {
      const body = Buffer.concat(chunks)
      const protocol = 'http'
      const host = req.headers.host ?? `localhost:${PORT}`
      const url = `${protocol}://${host}${req.url ?? '/'}`

      const init: RequestInit = {
        method: req.method,
        headers: req.headers as Record<string, string>,
      }

      // Only attach body for methods that may have one
      if (req.method !== 'GET' && req.method !== 'HEAD' && body.length > 0) {
        init.body = body
      }

      resolve(new Request(url, init))
    })
    req.on('error', reject)
  })
}

/**
 * Pipe a Web API Response into a node:http ServerResponse.
 */
async function sendResponse(webResponse: Response, res: ServerResponse): Promise<void> {
  const headers: Record<string, string> = {}
  webResponse.headers.forEach((value, key) => {
    headers[key] = value
  })
  res.writeHead(webResponse.status, headers)

  const body = await webResponse.arrayBuffer()
  res.end(Buffer.from(body))
}

/**
 * Serve a static file from the dist directory.
 * Returns true if the file was served, false otherwise.
 */
function serveStaticFile(filePath: string, res: ServerResponse): boolean {
  try {
    if (!existsSync(filePath)) return false

    const stat = statSync(filePath)
    if (!stat.isFile()) return false

    const ext = extname(filePath)
    const contentType = MIME_TYPES[ext] ?? 'application/octet-stream'

    res.writeHead(200, {
      'Content-Type': contentType,
      'Content-Length': stat.size,
    })

    const stream = createReadStream(filePath)
    stream.pipe(res)
    return true
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// HTTP server
// ---------------------------------------------------------------------------

const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
  const url = new URL(req.url ?? '/', `http://${req.headers.host ?? `localhost:${PORT}`}`)
  const { pathname } = url

  try {
    // -----------------------------------------------------------------
    // API routes (convert to Web API Request, delegate to handlers)
    // -----------------------------------------------------------------

    // Health check (fast path, no body parsing needed)
    if (pathname === '/api/health' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ status: 'ok' }))
      return
    }

    // API routes that use Web API Request/Response
    if (pathname.startsWith('/api/')) {
      const webReq = await toWebRequest(req)

      // Graph CRUD
      const graphsResponse = await handleGraphsRoute(webReq, pathname, GRAPHS_DIR)
      if (graphsResponse) {
        await sendResponse(graphsResponse, res)
        return
      }

      // Schema serving
      const schemasResponse = await handleSchemasRoute(webReq, pathname, GRAPHS_DIR)
      if (schemasResponse) {
        await sendResponse(schemasResponse, res)
        return
      }

      // Git status
      const gitResponse = await handleGitRoute(webReq, pathname, GRAPHS_DIR)
      if (gitResponse) {
        await sendResponse(gitResponse, res)
        return
      }

      // No API route matched
      res.writeHead(404, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ error: 'Not found' }))
      return
    }

    // -----------------------------------------------------------------
    // Static file serving (production mode)
    // -----------------------------------------------------------------
    const staticPath = pathname === '/' ? '/index.html' : pathname
    const filePath = `${DIST_DIR}${staticPath}`

    if (serveStaticFile(filePath, res)) return

    // SPA fallback: serve index.html for non-API, non-file paths
    const indexPath = `${DIST_DIR}/index.html`
    if (serveStaticFile(indexPath, res)) return

    res.writeHead(404, { 'Content-Type': 'text/plain' })
    res.end('Not found')
  } catch (err) {
    console.error('[server] Request error:', err)
    if (!res.headersSent) {
      res.writeHead(500, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ error: 'Internal server error' }))
    }
  }
})

// ---------------------------------------------------------------------------
// WebSocket server (noServer mode -- we handle upgrade manually)
// ---------------------------------------------------------------------------

const wss = new WebSocketServer({ noServer: true })

wss.on('connection', (ws: WebSocket) => {
  wsClients.add(ws)
  console.log(`[ws] Client connected (${wsClients.size} total)`)

  ws.on('close', () => {
    wsClients.delete(ws)
    console.log(`[ws] Client disconnected (${wsClients.size} total)`)
  })

  ws.on('message', (message: Buffer) => {
    ws.send(`echo:${message.toString()}`)
  })
})

server.on('upgrade', (req, socket, head) => {
  const url = new URL(req.url ?? '/', `http://${req.headers.host ?? `localhost:${PORT}`}`)

  if (url.pathname === '/ws') {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req)
    })
  } else {
    socket.destroy()
  }
})

// ---------------------------------------------------------------------------
// Start listening
// ---------------------------------------------------------------------------

server.listen(PORT, () => {
  console.log(`Graph Viewer server running at http://localhost:${PORT}`)
  console.log(`  API:       http://localhost:${PORT}/api/graphs`)
  console.log(`  WebSocket: ws://localhost:${PORT}/ws`)
  console.log(`  Graphs:    ${GRAPHS_DIR}`)
})

// ---------------------------------------------------------------------------
// Graceful shutdown
// ---------------------------------------------------------------------------

function shutdown(): void {
  console.log('\nShutting down...')
  watcher.stop()

  // Close all WebSocket connections
  for (const ws of wsClients) {
    try {
      ws.close()
    } catch {
      /* ignore */
    }
  }
  wsClients.clear()

  wss.close()
  server.close()
  process.exit(0)
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
