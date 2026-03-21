/**
 * CRUD operations on the Graphology graph.
 *
 * Provides functions to add, remove, and update nodes and edges.
 * Each function returns data sufficient for undo operations.
 *
 * IMPORTANT: Sigma reserves the `type` attribute for render programs.
 * Our domain type is stored as `nodeType` on nodes and `edgeType` on edges.
 */

import type Graph from 'graphology'
import type { EdgeType, NodeType } from '../graph/source'
import { bus } from '../state/events'

// ---------------------------------------------------------------------------
// ID generation
// ---------------------------------------------------------------------------

function generateNodeId(): string {
  return `node-${crypto.randomUUID().slice(0, 8)}`
}

function generateEdgeId(): string {
  return `edge-${crypto.randomUUID().slice(0, 8)}`
}

// ---------------------------------------------------------------------------
// Color maps (must stay in sync with loader.ts)
// ---------------------------------------------------------------------------

export const NODE_COLORS: Record<string, string> = {
  Concept: '#6366f1',
  Component: '#22c55e',
  Document: '#f59e0b',
  Fragment: '#ec4899',
}

export const EDGE_COLORS: Record<string, string> = {
  depends_on: '#94a3b8',
  relates_to: '#64748b',
  contains: '#475569',
}

export const EDGE_SIZES: Record<string, number> = {
  depends_on: 2,
  relates_to: 1.5,
  contains: 0.8,
}

// ---------------------------------------------------------------------------
// Node types and edge types (for validation and UI)
// ---------------------------------------------------------------------------

export const NODE_TYPES: readonly NodeType[] = [
  'Concept',
  'Component',
  'Document',
  'Fragment',
] as const

export const EDGE_TYPES: readonly EdgeType[] = ['depends_on', 'relates_to', 'contains'] as const

// ---------------------------------------------------------------------------
// Removed data types (for undo)
// ---------------------------------------------------------------------------

export interface RemovedEdgeData {
  id: string
  source: string
  target: string
  attrs: Record<string, unknown>
}

export interface RemovedNodeData {
  node: Record<string, unknown>
  edges: RemovedEdgeData[]
}

// ---------------------------------------------------------------------------
// CRUD functions
// ---------------------------------------------------------------------------

/**
 * Add a node to the graph with proper attributes.
 *
 * @returns The new node ID.
 */
export function addNode(
  graph: Graph,
  x: number,
  y: number,
  label: string,
  nodeType: string,
  properties?: Record<string, unknown>
): string {
  const id = generateNodeId()

  graph.addNode(id, {
    label,
    nodeType,
    x,
    y,
    size: 8,
    color: NODE_COLORS[nodeType] ?? '#6366f1',
    properties: properties ?? {},
  })

  bus.emit('graph:node-added', { nodeId: id })
  return id
}

/**
 * Add an edge between two nodes.
 *
 * @returns The new edge ID.
 */
export function addEdge(
  graph: Graph,
  source: string,
  target: string,
  edgeType: string,
  properties?: Record<string, unknown>
): string {
  const id = generateEdgeId()

  graph.addEdgeWithKey(id, source, target, {
    edgeType,
    label: edgeType,
    color: EDGE_COLORS[edgeType] ?? '#64748b',
    size: EDGE_SIZES[edgeType] ?? 1.5,
    properties: properties ?? {},
  })

  bus.emit('graph:edge-added', { edgeId: id })
  return id
}

/**
 * Remove a node and all its connected edges.
 *
 * @returns The removed node attributes and edge data for undo.
 */
export function removeNode(graph: Graph, nodeId: string): RemovedNodeData {
  const nodeAttrs = { ...graph.getNodeAttributes(nodeId) }
  const removedEdges: RemovedEdgeData[] = []

  // Collect all connected edges before removal
  graph.forEachEdge(nodeId, (edgeId, attrs, source, target) => {
    removedEdges.push({
      id: edgeId,
      source,
      target,
      attrs: { ...attrs },
    })
  })

  // Dropping the node also drops all its edges in Graphology
  graph.dropNode(nodeId)

  bus.emit('graph:node-removed', { nodeId })
  for (const edge of removedEdges) {
    bus.emit('graph:edge-removed', { edgeId: edge.id })
  }

  return { node: nodeAttrs, edges: removedEdges }
}

/**
 * Remove an edge from the graph.
 *
 * @returns The removed edge data for undo.
 */
export function removeEdge(
  graph: Graph,
  edgeId: string
): { source: string; target: string; attrs: Record<string, unknown> } {
  const source = graph.source(edgeId)
  const target = graph.target(edgeId)
  const attrs = { ...graph.getEdgeAttributes(edgeId) }

  graph.dropEdge(edgeId)

  bus.emit('graph:edge-removed', { edgeId })

  return { source, target, attrs }
}

/**
 * Update a single attribute on a node.
 *
 * @returns The old value of the attribute for undo.
 */
export function updateNodeAttribute(
  graph: Graph,
  nodeId: string,
  key: string,
  value: unknown
): unknown {
  const oldValue = graph.getNodeAttribute(nodeId, key)
  graph.setNodeAttribute(nodeId, key, value)

  bus.emit('graph:node-updated', {
    nodeId,
    key,
    oldValue,
    newValue: value,
  })

  return oldValue
}
