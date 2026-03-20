/**
 * GraphSource — metadata for a loaded graph.
 *
 * Holds identifying information about a graph independent of its
 * Graphology representation. Used to track which graph is active
 * and where its data originated.
 */

// ---------------------------------------------------------------------------
// Types (browser-safe duplicates of server types)
// ---------------------------------------------------------------------------

/** Node type discriminator (mirrors lib/graph.ts). */
export type NodeType = 'Concept' | 'Component' | 'Document' | 'Fragment'

/** Edge type discriminator (mirrors lib/graph.ts). */
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

/** Metadata block from the graph JSON file. */
export interface GraphMetadata {
  readonly id: string
  readonly version: number
  readonly created?: string
  readonly modified?: string
}

/** The top-level JSON graph file structure returned by the API. */
export interface GraphData {
  readonly metadata: GraphMetadata
  readonly nodes: readonly GraphNode[]
  readonly edges: readonly GraphEdge[]
}

/** Camera state stored in lock files. */
export interface CameraState {
  readonly x: number
  readonly y: number
  readonly ratio: number
  readonly angle: number
}

/** Layout configuration stored in lock files. */
export interface LayoutConfig {
  readonly algorithm: string
  readonly params?: Record<string, unknown>
}

/** Node position in 2D space. */
export interface NodePosition {
  readonly x: number
  readonly y: number
}

/** Lock file structure for view state persistence. */
export interface LockFile {
  readonly version: 1
  readonly graphId: string
  readonly layout: LayoutConfig
  readonly positions: Record<string, NodePosition>
  readonly view: {
    readonly camera: CameraState
  }
  readonly filters: Record<string, unknown>
}

/** List item returned by GET /api/graphs. */
export interface GraphListItem {
  readonly id: string
  readonly label: string
  readonly description: string
  readonly file: string
}

// ---------------------------------------------------------------------------
// GraphSource class
// ---------------------------------------------------------------------------

export class GraphSource {
  readonly id: string
  readonly label: string
  readonly description: string
  readonly file: string

  constructor(item: GraphListItem) {
    this.id = item.id
    this.label = item.label
    this.description = item.description
    this.file = item.file
  }
}
