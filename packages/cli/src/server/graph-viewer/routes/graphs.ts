/**
 * Graph CRUD API routes.
 *
 * Serves graph data from the `.data/graphs/` directory. The manifest file
 * (`manifest.json`) is the index of all available graphs. Individual graph
 * files and their lock files are read on demand.
 *
 * Uses runtime-agnostic `readJson` / `fileExists` helpers so this works on
 * both Bun and Node.js.
 */

import { resolve } from 'node:path'
import { fileExists, readJson } from '@agents/core/runtime'
import type { GraphData } from '../../../lib/graph'
import type { LockFile } from '../../../lib/graph-lock'
import { atomicWrite, directWrite } from '../fs-helpers'
import { validateGraph } from '../validation'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** A single entry in manifest.json. */
interface ManifestEntry {
  readonly id: string
  readonly file: string
  readonly schema: string
  readonly label: string
  readonly description: string
}

/** The top-level manifest structure. */
interface Manifest {
  readonly version: number
  readonly graphs: readonly ManifestEntry[]
}

/** Shape returned by GET /api/graphs */
interface GraphListItem {
  readonly id: string
  readonly label: string
  readonly description: string
  readonly file: string
}

/** Shape returned by GET /api/graphs/:id */
interface GraphDetail {
  readonly graph: GraphData
  readonly lock: LockFile | null
}

/** Body for POST /api/graphs (create new graph). */
interface CreateGraphBody {
  readonly id: string
  readonly label: string
  readonly description?: string
  readonly schema?: string
}

/** Writable form of the manifest used during mutation. */
interface MutableManifest {
  version: number
  graphs: ManifestEntry[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function jsonResponse(data: unknown, status = 200): Response {
  return Response.json(data, { status })
}

function errorResponse(message: string, status: number): Response {
  return Response.json({ error: message }, { status })
}

/**
 * Read and parse the manifest file. Returns null if it does not exist or
 * cannot be parsed.
 */
async function readManifest(graphsDir: string): Promise<Manifest | null> {
  try {
    const manifestPath = resolve(graphsDir, 'manifest.json')
    if (!(await fileExists(manifestPath))) return null
    return await readJson<Manifest>(manifestPath)
  } catch {
    return null
  }
}

/**
 * Atomically write the manifest file back to disk.
 */
async function writeManifest(graphsDir: string, manifest: MutableManifest): Promise<void> {
  const json = `${JSON.stringify(manifest, null, 2)}\n`
  await atomicWrite(resolve(graphsDir, 'manifest.json'), json)
}

/**
 * Safely parse a JSON request body. Returns the parsed object on success
 * or an error Response on failure.
 */
async function parseJsonBody(req: Request): Promise<unknown | Response> {
  try {
    return await req.json()
  } catch {
    return errorResponse('Invalid JSON in request body', 400)
  }
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

/**
 * Handle requests to `/api/graphs` and `/api/graphs/:id`.
 *
 * @param req - The incoming HTTP request.
 * @param pathname - The URL pathname (already parsed by the caller).
 * @param graphsDir - Absolute path to the graphs data directory.
 * @returns A Response, or null if the route does not match.
 */
export async function handleGraphsRoute(
  req: Request,
  pathname: string,
  graphsDir: string
): Promise<Response | null> {
  // GET /api/graphs -- list all available graphs
  if (pathname === '/api/graphs' && req.method === 'GET') {
    const manifest = await readManifest(graphsDir)
    if (!manifest) {
      return errorResponse('manifest.json not found or unreadable', 500)
    }

    const items: GraphListItem[] = manifest.graphs.map((entry) => ({
      id: entry.id,
      label: entry.label,
      description: entry.description,
      file: entry.file,
    }))

    return jsonResponse(items)
  }

  // GET /api/graphs/:id -- return graph data + optional lock file
  const graphMatch = pathname.match(/^\/api\/graphs\/([a-zA-Z0-9_-]+)$/)
  if (graphMatch && req.method === 'GET') {
    const graphId = graphMatch[1]

    const manifest = await readManifest(graphsDir)
    if (!manifest) {
      return errorResponse('manifest.json not found or unreadable', 500)
    }

    const entry = manifest.graphs.find((g) => g.id === graphId)
    if (!entry) {
      return errorResponse(`Graph "${graphId}" not found`, 404)
    }

    // Read graph data
    const graphPath = resolve(graphsDir, entry.file)
    if (!(await fileExists(graphPath))) {
      return errorResponse(`Graph file "${entry.file}" not found on disk`, 404)
    }

    let graphData: GraphData
    try {
      graphData = await readJson<GraphData>(graphPath)
    } catch {
      return errorResponse(`Failed to parse graph file "${entry.file}"`, 500)
    }

    // Read lock file (optional, never fails the request)
    let lock: LockFile | null = null
    const lockFileName = entry.file.replace(/\.json$/, '.graph.lock.json')
    const lockPath = resolve(graphsDir, lockFileName)
    try {
      if (await fileExists(lockPath)) {
        lock = await readJson<LockFile>(lockPath)
      }
    } catch {
      // Lock file is optional; corrupt lock files are silently ignored
    }

    const detail: GraphDetail = { graph: graphData, lock }
    return jsonResponse(detail)
  }

  // PUT /api/graphs/:id -- save graph data
  if (graphMatch && req.method === 'PUT') {
    const graphId = graphMatch[1]

    const manifest = await readManifest(graphsDir)
    if (!manifest) {
      return errorResponse('manifest.json not found or unreadable', 500)
    }

    const entry = manifest.graphs.find((g) => g.id === graphId)
    if (!entry) {
      return errorResponse(`Graph "${graphId}" not found`, 404)
    }

    const body = await parseJsonBody(req)
    if (body instanceof Response) return body

    const validation = validateGraph(body)
    if (!validation.valid) {
      return jsonResponse({ error: 'Validation failed', errors: validation.errors }, 400)
    }

    // Stamp the modified timestamp before writing
    const graphData = body as GraphData
    const stamped = {
      ...graphData,
      metadata: {
        ...graphData.metadata,
        modified: new Date().toISOString(),
      },
    }

    const json = `${JSON.stringify(stamped, null, 2)}\n`
    await atomicWrite(resolve(graphsDir, entry.file), json)

    return jsonResponse({ saved: true })
  }

  // PUT /api/graphs/:id/lock -- save lock file
  const lockMatch = pathname.match(/^\/api\/graphs\/([a-zA-Z0-9_-]+)\/lock$/)
  if (lockMatch && req.method === 'PUT') {
    const graphId = lockMatch[1]

    const manifest = await readManifest(graphsDir)
    if (!manifest) {
      return errorResponse('manifest.json not found or unreadable', 500)
    }

    const entry = manifest.graphs.find((g) => g.id === graphId)
    if (!entry) {
      return errorResponse(`Graph "${graphId}" not found`, 404)
    }

    const body = await parseJsonBody(req)
    if (body instanceof Response) return body

    const lockFileName = entry.file.replace(/\.json$/, '.graph.lock.json')
    const json = `${JSON.stringify(body, null, 2)}\n`
    await directWrite(resolve(graphsDir, lockFileName), json)

    return jsonResponse({ saved: true })
  }

  // POST /api/graphs -- create new graph
  if (pathname === '/api/graphs' && req.method === 'POST') {
    const body = await parseJsonBody(req)
    if (body instanceof Response) return body

    const { id, label, description, schema } = body as CreateGraphBody

    // Validate required fields
    if (!id || typeof id !== 'string') {
      return errorResponse('Missing or invalid "id" field', 400)
    }
    if (!label || typeof label !== 'string') {
      return errorResponse('Missing or invalid "label" field', 400)
    }

    // Validate id format (same pattern as route matching)
    if (!/^[a-zA-Z0-9_-]+$/.test(id)) {
      return errorResponse('Invalid "id" — must match [a-zA-Z0-9_-]+', 400)
    }

    const manifest = await readManifest(graphsDir)
    if (!manifest) {
      return errorResponse('manifest.json not found or unreadable', 500)
    }

    // Check for duplicate
    if (manifest.graphs.some((g) => g.id === id)) {
      return errorResponse(`Graph "${id}" already exists`, 409)
    }

    // Build the new graph data
    const now = new Date().toISOString()
    const newGraph: GraphData = {
      metadata: { id, version: 1, created: now, modified: now },
      nodes: [],
      edges: [],
    }

    const fileName = `${id}.json`
    const schemaRef = schema ?? 'schemas/graph.schema.json'

    // Write graph file
    const json = `${JSON.stringify(newGraph, null, 2)}\n`
    await atomicWrite(resolve(graphsDir, fileName), json)

    // Update manifest
    const newEntry: ManifestEntry = {
      id,
      file: fileName,
      schema: schemaRef,
      label,
      description: description ?? '',
    }

    const mutableManifest: MutableManifest = {
      version: manifest.version,
      graphs: [...manifest.graphs, newEntry],
    }
    await writeManifest(graphsDir, mutableManifest)

    return jsonResponse(newEntry, 201)
  }

  return null
}

/**
 * Handle requests to `/api/schemas/:name`.
 *
 * Serves JSON schema files from the `schemas/` subdirectory of the graphs
 * data directory. Only `.json` files are served.
 *
 * @param req - The incoming HTTP request.
 * @param pathname - The URL pathname.
 * @param graphsDir - Absolute path to the graphs data directory.
 * @returns A Response, or null if the route does not match.
 */
export async function handleSchemasRoute(
  req: Request,
  pathname: string,
  graphsDir: string
): Promise<Response | null> {
  const schemaMatch = pathname.match(/^\/api\/schemas\/([a-zA-Z0-9_.-]+)$/)
  if (!schemaMatch || req.method !== 'GET') return null

  const schemaName = schemaMatch[1]

  // Prevent directory traversal
  if (schemaName.includes('..') || schemaName.includes('/')) {
    return errorResponse('Invalid schema name', 400)
  }

  // Only serve .json files
  if (!schemaName.endsWith('.json')) {
    return errorResponse('Only .json schema files are served', 400)
  }

  const schemaPath = resolve(graphsDir, 'schemas', schemaName)

  // Verify resolved path is still inside the schemas directory
  const schemasDir = resolve(graphsDir, 'schemas')
  if (!schemaPath.startsWith(schemasDir)) {
    return errorResponse('Invalid schema path', 400)
  }

  if (!(await fileExists(schemaPath))) {
    return errorResponse(`Schema "${schemaName}" not found`, 404)
  }

  try {
    const data = await readJson(schemaPath)
    return jsonResponse(data)
  } catch {
    return errorResponse(`Failed to parse schema "${schemaName}"`, 500)
  }
}
