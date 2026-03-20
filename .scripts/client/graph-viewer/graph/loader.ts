/**
 * Graph loader — fetches graph data from the API and builds a Graphology instance.
 *
 * This module runs in the browser and cannot import from `../../lib/` (Bun APIs).
 * It duplicates the minimal loading logic needed to parse the API response into
 * a Graphology graph with proper attributes.
 */

import Graph from 'graphology'
import type { EdgeType, GraphData, LockFile, NodeType } from './source'

// ---------------------------------------------------------------------------
// Color mapping for node types
// ---------------------------------------------------------------------------

const NODE_COLORS: Record<NodeType, string> = {
  Concept: '#6366f1', // indigo
  Component: '#22c55e', // green
  Document: '#f59e0b', // amber
  Fragment: '#ec4899', // pink
}

const EDGE_COLORS: Record<EdgeType, string> = {
  depends_on: '#94a3b8', // slate — prominent
  relates_to: '#64748b', // slate darker — medium
  contains: '#475569', // slate darkest — subtle
}

const EDGE_SIZES: Record<EdgeType, number> = {
  depends_on: 2, // thick, prominent
  relates_to: 1.5, // medium
  contains: 0.8, // thin, subtle
}

/** Default node size. */
const NODE_SIZE = 8

/** Selected node size multiplier. */
export const SELECTED_SIZE_MULTIPLIER = 1.5

// ---------------------------------------------------------------------------
// Fetch + Load
// ---------------------------------------------------------------------------

export interface LoadedGraph {
  graph: Graph
  lock: LockFile | null
  data: GraphData
}

/**
 * Fetch a graph from the API by ID and return a populated Graphology instance.
 *
 * If a lock file is available, node positions from the lock are applied to the
 * graph. Otherwise, nodes start with random positions so the layout algorithm
 * has something to work with.
 */
export async function fetchGraph(graphId: string): Promise<LoadedGraph> {
  const response = await fetch(`/api/graphs/${encodeURIComponent(graphId)}`)

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`Failed to fetch graph "${graphId}": ${response.status} ${body}`)
  }

  const payload = (await response.json()) as {
    graph: GraphData
    lock: LockFile | null
  }

  const graph = buildGraph(payload.graph, payload.lock)

  return {
    graph,
    lock: payload.lock,
    data: payload.graph,
  }
}

/**
 * Fetch the list of available graphs from the API.
 */
export async function fetchGraphList(): Promise<
  Array<{ id: string; label: string; description: string; file: string }>
> {
  const response = await fetch('/api/graphs')
  if (!response.ok) {
    throw new Error(`Failed to fetch graph list: ${response.status}`)
  }
  return response.json()
}

// ---------------------------------------------------------------------------
// Graph construction
// ---------------------------------------------------------------------------

/**
 * Build a Graphology graph from raw JSON data, optionally applying lock file
 * positions. Nodes without lock positions get random coordinates.
 */
function buildGraph(data: GraphData, lock: LockFile | null): Graph {
  const graph = new Graph()

  // Store metadata as graph-level attributes
  graph.replaceAttributes({
    metadata: { ...data.metadata },
  })

  for (const node of data.nodes) {
    const position = lock?.positions[node.id]
    const x = position?.x ?? (Math.random() - 0.5) * 100
    const y = position?.y ?? (Math.random() - 0.5) * 100

    graph.addNode(node.id, {
      label: node.label,
      nodeType: node.type,
      x,
      y,
      size: NODE_SIZE,
      color: NODE_COLORS[node.type] ?? '#6366f1',
      properties: { ...(node.properties ?? {}) },
    })
  }

  for (const edge of data.edges) {
    graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
      edgeType: edge.type,
      label: edge.type,
      color: EDGE_COLORS[edge.type] ?? '#94a3b8',
      size: EDGE_SIZES[edge.type] ?? 1.5,
      properties: { ...(edge.properties ?? {}) },
    })
  }

  return graph
}
