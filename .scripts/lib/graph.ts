/**
 * Graphology wrapper for loading and serializing graph data.
 *
 * Converts between the project's JSON graph format and Graphology's internal
 * representation. Every node is tagged with `_source` metadata on load so that
 * multi-file graphs can be partitioned back to their origin files on save.
 */

import Graph from 'graphology'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

export const NODE_ID_PREFIX = 'node-'
export const EDGE_ID_PREFIX = 'edge-'

// ---------------------------------------------------------------------------
// Types — matches the JSON file format from the architecture doc
// ---------------------------------------------------------------------------

/** Node type discriminator. */
export type NodeType = 'Concept' | 'Component' | 'Document' | 'Fragment'

/** Edge type discriminator. */
export type EdgeType = 'depends_on' | 'relates_to' | 'contains'

/** A single node in the JSON graph format. */
export interface GraphNode {
  readonly id: string
  readonly type: NodeType
  readonly label: string
  readonly properties?: Record<string, unknown>
}

/** A single edge in the JSON graph format. */
export interface GraphEdge {
  readonly id: string
  readonly source: string
  readonly target: string
  readonly type: EdgeType
  readonly properties?: Record<string, unknown>
}

/** Metadata block at the top of every graph JSON file. */
export interface GraphMetadata {
  readonly id: string
  readonly version: number
  readonly created?: string
  readonly modified?: string
}

/** The top-level JSON graph file structure. */
export interface GraphData {
  readonly metadata: GraphMetadata
  readonly nodes: readonly GraphNode[]
  readonly edges: readonly GraphEdge[]
}

// ---------------------------------------------------------------------------
// Node/Edge attribute types inside Graphology
// ---------------------------------------------------------------------------

/** Attributes stored on each Graphology node after loading. */
export interface GraphNodeAttributes {
  type: NodeType
  label: string
  properties: Record<string, unknown>
  _source: string
}

/** Attributes stored on each Graphology edge after loading. */
export interface GraphEdgeAttributes {
  type: EdgeType
  properties: Record<string, unknown>
  _source: string
}

// ---------------------------------------------------------------------------
// Load — JSON → Graphology
// ---------------------------------------------------------------------------

/**
 * Parse a {@link GraphData} object into a Graphology graph instance.
 *
 * Every node and edge is tagged with `_source: sourceId` so that
 * {@link serializeGraph} can partition the graph back by origin file.
 *
 * If no `sourceId` is provided, the metadata `id` from the data is used.
 *
 * @param data - Validated graph JSON data.
 * @param sourceId - Optional source identifier for `_source` tagging.
 * @returns A populated Graphology graph.
 */
export function loadGraph(data: GraphData, sourceId?: string): Graph {
  const source = sourceId ?? data.metadata.id

  const graph = new Graph()

  // Store metadata as graph-level attributes
  graph.replaceAttributes({
    metadata: { ...data.metadata },
  })

  for (const node of data.nodes) {
    graph.addNode(node.id, {
      type: node.type,
      label: node.label,
      properties: { ...(node.properties ?? {}) },
      _source: source,
    })
  }

  for (const edge of data.edges) {
    graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
      type: edge.type,
      properties: { ...(edge.properties ?? {}) },
      _source: source,
    })
  }

  return graph
}

// ---------------------------------------------------------------------------
// Serialize — Graphology → JSON
// ---------------------------------------------------------------------------

/**
 * Export a Graphology graph back to the project's JSON format.
 *
 * When `sourceId` is provided, only nodes and edges whose `_source` attribute
 * matches are included in the output. This enables multi-file round-trips
 * where each file only gets its own nodes back.
 *
 * The `_source` attribute is stripped from the serialized output since it is
 * internal metadata that should not appear in persisted JSON files.
 *
 * @param graph - The Graphology graph instance to serialize.
 * @param sourceId - If provided, filter to only nodes/edges with this `_source`.
 * @returns A {@link GraphData} object ready for JSON serialization.
 */
export function serializeGraph(graph: Graph, sourceId?: string): GraphData {
  const graphAttrs = graph.getAttributes() as { metadata?: GraphMetadata }
  const metadata: GraphMetadata = graphAttrs.metadata ?? {
    id: sourceId ?? 'unknown',
    version: 1,
  }

  const nodes: GraphNode[] = []
  graph.forEachNode((nodeId, attrs) => {
    if (sourceId !== undefined && attrs._source !== sourceId) return

    nodes.push({
      id: nodeId,
      type: attrs.type as NodeType,
      label: attrs.label as string,
      properties: stripInternal(attrs.properties as Record<string, unknown> | undefined),
    })
  })

  const edges: GraphEdge[] = []
  graph.forEachEdge((edgeId, attrs, source, target) => {
    if (sourceId !== undefined && attrs._source !== sourceId) return

    edges.push({
      id: edgeId,
      source,
      target,
      type: attrs.type as EdgeType,
      properties: stripInternal(attrs.properties as Record<string, unknown> | undefined),
    })
  })

  return {
    metadata: {
      ...metadata,
      modified: new Date().toISOString(),
    },
    nodes,
    edges,
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Return a shallow copy of properties, or an empty object if undefined.
 * Strips any keys prefixed with `_` (internal metadata).
 */
function stripInternal(props: Record<string, unknown> | undefined): Record<string, unknown> {
  if (!props) return {}
  const result: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(props)) {
    if (!key.startsWith('_')) {
      result[key] = value
    }
  }
  return result
}
