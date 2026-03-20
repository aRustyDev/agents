/**
 * Graph serializer -- converts a Graphology instance back to the API's
 * GraphData format for saving, and builds lock file objects for view state
 * persistence.
 *
 * Strips Sigma-specific rendering attributes (x, y, size, color, fixed,
 * highlighted, etc.) and maps internal attribute names back to their API
 * equivalents (e.g. `nodeType` -> `type`, `edgeType` -> `type`).
 */

import type Graph from 'graphology'
import type { CameraState, GraphData, GraphEdge, GraphNode, LockFile } from './source'

// ---------------------------------------------------------------------------
// Graph -> GraphData
// ---------------------------------------------------------------------------

/**
 * Serialize a Graphology graph back to the JSON format the API expects.
 *
 * The loader maps `GraphNode.type` to `nodeType` (because Sigma reserves
 * `type` for render programs). This function reverses that mapping.
 */
export function serializeGraph(graph: Graph): GraphData {
  const metadata = graph.getAttribute('metadata') || {
    id: 'unknown',
    version: 1,
  }

  const nodes: GraphNode[] = graph.mapNodes((nodeId, attrs) => ({
    id: nodeId,
    type: attrs.nodeType || 'Concept',
    label: attrs.label || nodeId,
    properties: attrs.properties || {},
  }))

  const edges: GraphEdge[] = graph.mapEdges((edgeId, attrs, source, target) => ({
    id: edgeId,
    source,
    target,
    type: attrs.edgeType || 'relates_to',
    properties: attrs.properties || {},
  }))

  return {
    metadata: { ...metadata, modified: new Date().toISOString() },
    nodes,
    edges,
  }
}

// ---------------------------------------------------------------------------
// Lock file builder
// ---------------------------------------------------------------------------

/**
 * Build a lock file object from the current graph state and Sigma camera.
 *
 * Lock files persist node positions and camera state so the graph can be
 * restored to its previous visual state on reload.
 */
export function buildLockFile(
  graph: Graph,
  graphId: string,
  camera?: CameraState,
  activeLayout?: string
): LockFile {
  const positions: Record<string, { x: number; y: number }> = {}

  graph.forEachNode((nodeId, attrs) => {
    positions[nodeId] = { x: attrs.x ?? 0, y: attrs.y ?? 0 }
  })

  return {
    version: 1,
    graphId,
    layout: { algorithm: activeLayout || 'forceatlas2' },
    positions,
    view: { camera: camera || { x: 0, y: 0, ratio: 1, angle: 0 } },
    filters: {},
  }
}
