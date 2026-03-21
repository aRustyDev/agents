/**
 * Phase 0 spike: Bun.serve WebSocket upgrade test.
 * Verifies WebSocket works alongside HTTP routes in a single Bun server.
 * Exit 0 = pass, exit 1 = fail.
 */

const PORT = 39123 // ephemeral port to avoid conflicts

const server = Bun.serve({
  port: PORT,
  fetch(req, server) {
    const url = new URL(req.url)
    if (url.pathname === '/ws') {
      const upgraded = server.upgrade(req)
      if (!upgraded) return new Response('WebSocket upgrade failed', { status: 400 })
      return undefined as unknown as Response
    }
    if (url.pathname === '/api/graphs') {
      return Response.json([])
    }
    return new Response('Not found', { status: 404 })
  },
  websocket: {
    message(ws, message) {
      ws.send(`echo:${message}`)
    },
    open(ws) {
      ws.send('hello')
    },
  },
})

// Test HTTP route
const httpRes = await fetch(`http://localhost:${PORT}/api/graphs`)
if (!httpRes.ok) {
  console.error('FAIL: HTTP route returned', httpRes.status)
  server.stop()
  process.exit(1)
}
const data = await httpRes.json()
console.log('HTTP /api/graphs:', JSON.stringify(data))

// Test WebSocket
const ws = new WebSocket(`ws://localhost:${PORT}/ws`)

const result = await new Promise<string>((resolve, reject) => {
  const timeout = setTimeout(() => reject(new Error('WebSocket timeout')), 3000)
  ws.onmessage = (event) => {
    clearTimeout(timeout)
    resolve(String(event.data))
  }
  ws.onerror = (_event) => {
    clearTimeout(timeout)
    reject(new Error('WebSocket error'))
  }
})

if (result === 'hello') {
  console.log('WebSocket open message received:', result)

  // Test echo
  ws.send('ping')
  const echo = await new Promise<string>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Echo timeout')), 3000)
    ws.onmessage = (event) => {
      clearTimeout(timeout)
      resolve(String(event.data))
    }
  })

  if (echo === 'echo:ping') {
    console.log('WebSocket echo:', echo)
    console.log('PASS: WebSocket + HTTP coexist in Bun.serve')
    ws.close()
    server.stop()
    process.exit(0)
  }
}

console.error('FAIL: unexpected WebSocket response:', result)
ws.close()
server.stop()
process.exit(1)
