/**
 * Tests for graph core libraries:
 *   - graph.ts — Graphology wrapper (load, serialize, round-trip, _source tagging)
 *   - graph-lock.ts — Lock file read/write/reconcile
 *   - graph-schema.ts — Ajv validation for graph JSON
 */

import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

import {
  EDGE_ID_PREFIX,
  type GraphData,
  loadGraph,
  NODE_ID_PREFIX,
  serializeGraph,
} from '../src/lib/graph'
import { type LockFile, readLock, reconcileLock, writeLock } from '../src/lib/graph-lock'
import { validateGraphData } from '../src/lib/graph-schema'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const SAMPLE_DATA: GraphData = {
  metadata: {
    id: 'test-graph',
    version: 1,
    created: '2026-03-19T00:00:00Z',
    modified: '2026-03-19T00:00:00Z',
  },
  nodes: [
    {
      id: 'node-alpha',
      type: 'Concept',
      label: 'Neural Network',
      properties: { domain: 'ML', complexity: 'high' },
    },
    {
      id: 'node-beta',
      type: 'Component',
      label: 'GPU Cluster',
      properties: { cores: 8192, vendor: 'nvidia' },
    },
    {
      id: 'node-gamma',
      type: 'Document',
      label: 'API Spec',
      properties: { format: 'openapi' },
    },
    {
      id: 'node-delta',
      type: 'Fragment',
      label: 'Loss Function',
      properties: { type: 'cross-entropy' },
    },
  ],
  edges: [
    {
      id: 'edge-001',
      source: 'node-alpha',
      target: 'node-beta',
      type: 'depends_on',
      properties: { weight: 0.8, critical: true },
    },
    {
      id: 'edge-002',
      source: 'node-beta',
      target: 'node-gamma',
      type: 'relates_to',
      properties: { automated: false },
    },
    {
      id: 'edge-003',
      source: 'node-alpha',
      target: 'node-delta',
      type: 'contains',
      properties: {},
    },
  ],
}

const SAMPLE_LOCK: LockFile = {
  version: 1,
  graphId: 'test-graph',
  layout: {
    algorithm: 'forceatlas2',
    params: { gravity: 1.0, scalingRatio: 2.0 },
  },
  positions: {
    'node-alpha': { x: 100, y: 200 },
    'node-beta': { x: -50, y: 100 },
    'node-gamma': { x: 300, y: -75 },
    'node-delta': { x: 0, y: 0 },
  },
  view: {
    camera: { x: 0, y: 0, ratio: 1.0, angle: 0 },
  },
  filters: {},
}

// Temp directory for file-based tests
let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'graph-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ===========================================================================
// graph.ts
// ===========================================================================

describe('graph.ts', () => {
  // -------------------------------------------------------------------------
  // ID prefix constants
  // -------------------------------------------------------------------------

  describe('constants', () => {
    test('NODE_ID_PREFIX is "node-"', () => {
      expect(NODE_ID_PREFIX).toBe('node-')
    })

    test('EDGE_ID_PREFIX is "edge-"', () => {
      expect(EDGE_ID_PREFIX).toBe('edge-')
    })
  })

  // -------------------------------------------------------------------------
  // loadGraph
  // -------------------------------------------------------------------------

  describe('loadGraph', () => {
    test('creates correct number of nodes and edges', () => {
      const graph = loadGraph(SAMPLE_DATA)
      expect(graph.order).toBe(4)
      expect(graph.size).toBe(3)
    })

    test('preserves node attributes', () => {
      const graph = loadGraph(SAMPLE_DATA)
      expect(graph.getNodeAttribute('node-alpha', 'type')).toBe('Concept')
      expect(graph.getNodeAttribute('node-alpha', 'label')).toBe('Neural Network')
      expect(graph.getNodeAttribute('node-alpha', 'properties')).toEqual({
        domain: 'ML',
        complexity: 'high',
      })
    })

    test('preserves edge attributes', () => {
      const graph = loadGraph(SAMPLE_DATA)
      expect(graph.getEdgeAttribute('edge-001', 'type')).toBe('depends_on')
      expect(graph.getEdgeAttribute('edge-001', 'properties')).toEqual({
        weight: 0.8,
        critical: true,
      })
    })

    test('tags all nodes with _source from metadata.id', () => {
      const graph = loadGraph(SAMPLE_DATA)
      graph.forEachNode((_id, attrs) => {
        expect(attrs._source).toBe('test-graph')
      })
    })

    test('tags all edges with _source from metadata.id', () => {
      const graph = loadGraph(SAMPLE_DATA)
      graph.forEachEdge((_id, attrs) => {
        expect(attrs._source).toBe('test-graph')
      })
    })

    test('uses custom sourceId when provided', () => {
      const graph = loadGraph(SAMPLE_DATA, 'custom-source')
      graph.forEachNode((_id, attrs) => {
        expect(attrs._source).toBe('custom-source')
      })
      graph.forEachEdge((_id, attrs) => {
        expect(attrs._source).toBe('custom-source')
      })
    })

    test('stores metadata as graph-level attributes', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const attrs = graph.getAttributes() as {
        metadata: typeof SAMPLE_DATA.metadata
      }
      expect(attrs.metadata.id).toBe('test-graph')
      expect(attrs.metadata.version).toBe(1)
    })

    test('handles nodes with no properties', () => {
      const data: GraphData = {
        metadata: { id: 'minimal', version: 1 },
        nodes: [{ id: 'node-bare', type: 'Concept', label: 'Bare' }],
        edges: [],
      }
      const graph = loadGraph(data)
      expect(graph.order).toBe(1)
      expect(graph.getNodeAttribute('node-bare', 'properties')).toEqual({})
    })

    test('handles edges with no properties', () => {
      const data: GraphData = {
        metadata: { id: 'minimal', version: 1 },
        nodes: [
          { id: 'node-a', type: 'Concept', label: 'A' },
          { id: 'node-b', type: 'Concept', label: 'B' },
        ],
        edges: [
          {
            id: 'edge-ab',
            source: 'node-a',
            target: 'node-b',
            type: 'depends_on',
          },
        ],
      }
      const graph = loadGraph(data)
      expect(graph.size).toBe(1)
      expect(graph.getEdgeAttribute('edge-ab', 'properties')).toEqual({})
    })

    test('handles empty graph', () => {
      const data: GraphData = {
        metadata: { id: 'empty', version: 1 },
        nodes: [],
        edges: [],
      }
      const graph = loadGraph(data)
      expect(graph.order).toBe(0)
      expect(graph.size).toBe(0)
    })
  })

  // -------------------------------------------------------------------------
  // serializeGraph
  // -------------------------------------------------------------------------

  describe('serializeGraph', () => {
    test('serializes all nodes and edges', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)
      expect(result.nodes).toHaveLength(4)
      expect(result.edges).toHaveLength(3)
    })

    test('preserves node data through serialization', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)
      const alpha = result.nodes.find((n) => n.id === 'node-alpha')
      expect(alpha).toBeDefined()
      expect(alpha?.type).toBe('Concept')
      expect(alpha?.label).toBe('Neural Network')
      expect(alpha?.properties).toEqual({ domain: 'ML', complexity: 'high' })
    })

    test('preserves edge data through serialization', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)
      const edge = result.edges.find((e) => e.id === 'edge-001')
      expect(edge).toBeDefined()
      expect(edge?.source).toBe('node-alpha')
      expect(edge?.target).toBe('node-beta')
      expect(edge?.type).toBe('depends_on')
      expect(edge?.properties).toEqual({ weight: 0.8, critical: true })
    })

    test('strips _source from serialized properties', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)

      // _source should not leak into the properties object
      for (const node of result.nodes) {
        expect(node.properties).not.toHaveProperty('_source')
      }
      for (const edge of result.edges) {
        expect(edge.properties).not.toHaveProperty('_source')
      }
    })

    test('updates modified timestamp on serialization', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)
      expect(result.metadata.modified).toBeDefined()
      // The modified timestamp should be a recent ISO string
      const modified = new Date(result.metadata.modified!)
      expect(modified.getTime()).toBeGreaterThan(Date.now() - 5000)
    })

    test('preserves original metadata fields', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)
      expect(result.metadata.id).toBe('test-graph')
      expect(result.metadata.version).toBe(1)
      expect(result.metadata.created).toBe('2026-03-19T00:00:00Z')
    })

    test('filters by sourceId when provided', () => {
      const graph = loadGraph(SAMPLE_DATA, 'source-a')

      // Add a node from a different source manually
      graph.addNode('node-other', {
        type: 'Concept',
        label: 'Other',
        properties: {},
        _source: 'source-b',
      })

      const resultA = serializeGraph(graph, 'source-a')
      const resultB = serializeGraph(graph, 'source-b')

      expect(resultA.nodes).toHaveLength(4) // Original 4 nodes
      expect(resultB.nodes).toHaveLength(1) // Just the added node
      expect(resultB.nodes[0]?.id).toBe('node-other')
    })

    test('returns all nodes when sourceId is undefined', () => {
      const graph = loadGraph(SAMPLE_DATA, 'source-a')
      graph.addNode('node-other', {
        type: 'Concept',
        label: 'Other',
        properties: {},
        _source: 'source-b',
      })

      const result = serializeGraph(graph)
      expect(result.nodes).toHaveLength(5) // All nodes regardless of source
    })
  })

  // -------------------------------------------------------------------------
  // Round-trip
  // -------------------------------------------------------------------------

  describe('round-trip', () => {
    test('load then serialize preserves all data', () => {
      const graph = loadGraph(SAMPLE_DATA)
      const result = serializeGraph(graph)

      // Verify structural equivalence (modified timestamp will differ)
      expect(result.nodes).toHaveLength(SAMPLE_DATA.nodes.length)
      expect(result.edges).toHaveLength(SAMPLE_DATA.edges.length)

      for (const origNode of SAMPLE_DATA.nodes) {
        const serialized = result.nodes.find((n) => n.id === origNode.id)
        expect(serialized).toBeDefined()
        expect(serialized?.type).toBe(origNode.type)
        expect(serialized?.label).toBe(origNode.label)
        expect(serialized?.properties).toEqual(origNode.properties ?? {})
      }

      for (const origEdge of SAMPLE_DATA.edges) {
        const serialized = result.edges.find((e) => e.id === origEdge.id)
        expect(serialized).toBeDefined()
        expect(serialized?.source).toBe(origEdge.source)
        expect(serialized?.target).toBe(origEdge.target)
        expect(serialized?.type).toBe(origEdge.type)
        expect(serialized?.properties).toEqual(origEdge.properties ?? {})
      }
    })

    test('double round-trip is stable', () => {
      const graph1 = loadGraph(SAMPLE_DATA)
      const serialized1 = serializeGraph(graph1)

      const graph2 = loadGraph(serialized1)
      const serialized2 = serializeGraph(graph2)

      // Node/edge content should be identical across both round-trips
      expect(serialized2.nodes).toHaveLength(serialized1.nodes.length)
      expect(serialized2.edges).toHaveLength(serialized1.edges.length)

      for (const node of serialized1.nodes) {
        const match = serialized2.nodes.find((n) => n.id === node.id)
        expect(match).toBeDefined()
        expect(match?.type).toBe(node.type)
        expect(match?.label).toBe(node.label)
        expect(match?.properties).toEqual(node.properties)
      }
    })

    test('mutations survive round-trip', () => {
      const graph = loadGraph(SAMPLE_DATA)

      // Add a new node
      graph.addNode('node-new', {
        type: 'Fragment',
        label: 'New Config',
        properties: { added: true },
        _source: 'test-graph',
      })

      // Modify an existing node
      graph.setNodeAttribute('node-alpha', 'label', 'Updated NN')

      const result = serializeGraph(graph)
      expect(result.nodes).toHaveLength(5)

      const newNode = result.nodes.find((n) => n.id === 'node-new')
      expect(newNode).toBeDefined()
      expect(newNode?.properties).toEqual({ added: true })

      const updated = result.nodes.find((n) => n.id === 'node-alpha')
      expect(updated?.label).toBe('Updated NN')
    })
  })
})

// ===========================================================================
// graph-lock.ts
// ===========================================================================

describe('graph-lock.ts', () => {
  // -------------------------------------------------------------------------
  // readLock
  // -------------------------------------------------------------------------

  describe('readLock', () => {
    test('reads a valid lock file', async () => {
      const path = join(tmp, 'test.graph.lock.json')
      await writeFile(path, JSON.stringify(SAMPLE_LOCK))

      const lock = await readLock(path)
      expect(lock).not.toBeNull()
      expect(lock?.version).toBe(1)
      expect(lock?.graphId).toBe('test-graph')
      expect(lock?.positions['node-alpha']).toEqual({ x: 100, y: 200 })
    })

    test('returns null for non-existent file', async () => {
      const lock = await readLock(join(tmp, 'nonexistent.json'))
      expect(lock).toBeNull()
    })

    test('returns null for invalid JSON', async () => {
      const path = join(tmp, 'bad.json')
      await writeFile(path, '{ not valid json }')

      const lock = await readLock(path)
      expect(lock).toBeNull()
    })

    test('returns null for wrong version', async () => {
      const path = join(tmp, 'wrong-version.json')
      await writeFile(path, JSON.stringify({ ...SAMPLE_LOCK, version: 99 }))

      const lock = await readLock(path)
      expect(lock).toBeNull()
    })

    test('returns null for data missing required fields', async () => {
      const path = join(tmp, 'missing-fields.json')
      await writeFile(path, JSON.stringify({ version: 1 })) // missing graphId, positions

      const lock = await readLock(path)
      expect(lock).toBeNull()
    })
  })

  // -------------------------------------------------------------------------
  // writeLock
  // -------------------------------------------------------------------------

  describe('writeLock', () => {
    test('writes valid JSON with 2-space indent and trailing newline', async () => {
      const path = join(tmp, 'output.graph.lock.json')
      await writeLock(path, SAMPLE_LOCK)

      const raw = await Bun.file(path).text()
      expect(raw.endsWith('\n')).toBe(true)
      expect(raw).toContain('  ') // 2-space indent

      const parsed = JSON.parse(raw)
      expect(parsed.version).toBe(1)
      expect(parsed.graphId).toBe('test-graph')
    })

    test('round-trips through read', async () => {
      const path = join(tmp, 'roundtrip.graph.lock.json')
      await writeLock(path, SAMPLE_LOCK)

      const lock = await readLock(path)
      expect(lock).not.toBeNull()
      expect(lock?.graphId).toBe(SAMPLE_LOCK.graphId)
      expect(lock?.positions).toEqual(SAMPLE_LOCK.positions)
      expect(lock?.view.camera).toEqual(SAMPLE_LOCK.view.camera)
      expect(lock?.layout).toEqual(SAMPLE_LOCK.layout)
    })
  })

  // -------------------------------------------------------------------------
  // reconcileLock
  // -------------------------------------------------------------------------

  describe('reconcileLock', () => {
    test('returns unchanged lock when all nodes match', () => {
      const nodeIds = ['node-alpha', 'node-beta', 'node-gamma', 'node-delta']
      const [reconciled, report] = reconcileLock(SAMPLE_LOCK, nodeIds)

      expect(report.orphansRemoved).toHaveLength(0)
      expect(report.missingNodes).toHaveLength(0)
      expect(Object.keys(reconciled.positions)).toHaveLength(4)
    })

    test('removes orphan positions', () => {
      // Only alpha and beta exist in the graph now
      const nodeIds = ['node-alpha', 'node-beta']
      const [reconciled, report] = reconcileLock(SAMPLE_LOCK, nodeIds)

      expect(report.orphansRemoved).toContain('node-gamma')
      expect(report.orphansRemoved).toContain('node-delta')
      expect(report.orphansRemoved).toHaveLength(2)
      expect(Object.keys(reconciled.positions)).toHaveLength(2)
      expect(reconciled.positions['node-alpha']).toEqual({ x: 100, y: 200 })
      expect(reconciled.positions['node-beta']).toEqual({ x: -50, y: 100 })
      expect(reconciled.positions['node-gamma']).toBeUndefined()
    })

    test('reports missing nodes', () => {
      const nodeIds = ['node-alpha', 'node-beta', 'node-gamma', 'node-delta', 'node-new']
      const [reconciled, report] = reconcileLock(SAMPLE_LOCK, nodeIds)

      expect(report.missingNodes).toContain('node-new')
      expect(report.missingNodes).toHaveLength(1)
      // Existing positions are preserved
      expect(Object.keys(reconciled.positions)).toHaveLength(4)
    })

    test('handles both orphans and missing simultaneously', () => {
      const nodeIds = ['node-alpha', 'node-new1', 'node-new2']
      const [reconciled, report] = reconcileLock(SAMPLE_LOCK, nodeIds)

      expect(report.orphansRemoved).toHaveLength(3) // beta, gamma, delta removed
      expect(report.missingNodes).toHaveLength(2) // new1, new2 missing
      expect(Object.keys(reconciled.positions)).toHaveLength(1) // only alpha kept
    })

    test('handles empty node list (all orphaned)', () => {
      const [reconciled, report] = reconcileLock(SAMPLE_LOCK, [])

      expect(report.orphansRemoved).toHaveLength(4)
      expect(report.missingNodes).toHaveLength(0)
      expect(Object.keys(reconciled.positions)).toHaveLength(0)
    })

    test('handles empty lock positions (all missing)', () => {
      const emptyLock: LockFile = { ...SAMPLE_LOCK, positions: {} }
      const nodeIds = ['node-alpha', 'node-beta']
      const [reconciled, report] = reconcileLock(emptyLock, nodeIds)

      expect(report.orphansRemoved).toHaveLength(0)
      expect(report.missingNodes).toHaveLength(2)
      expect(Object.keys(reconciled.positions)).toHaveLength(0)
    })

    test('preserves non-position fields', () => {
      const nodeIds = ['node-alpha']
      const [reconciled] = reconcileLock(SAMPLE_LOCK, nodeIds)

      expect(reconciled.version).toBe(1)
      expect(reconciled.graphId).toBe('test-graph')
      expect(reconciled.layout).toEqual(SAMPLE_LOCK.layout)
      expect(reconciled.view).toEqual(SAMPLE_LOCK.view)
      expect(reconciled.filters).toEqual(SAMPLE_LOCK.filters)
    })
  })
})

// ===========================================================================
// graph-schema.ts
// ===========================================================================

describe('graph-schema.ts', () => {
  // -------------------------------------------------------------------------
  // Valid data
  // -------------------------------------------------------------------------

  describe('valid data', () => {
    test('accepts well-formed graph data', () => {
      const result = validateGraphData(SAMPLE_DATA)
      expect(result.valid).toBe(true)
      expect(result.errors).toBeUndefined()
    })

    test('accepts minimal valid graph', () => {
      const minimal = {
        metadata: { id: 'min', version: 1 },
        nodes: [],
        edges: [],
      }
      const result = validateGraphData(minimal)
      expect(result.valid).toBe(true)
    })

    test('accepts nodes with all four types', () => {
      const allTypes = {
        metadata: { id: 'types', version: 1 },
        nodes: [
          { id: 'node-c1', type: 'Concept', label: 'A' },
          { id: 'node-c2', type: 'Component', label: 'B' },
          { id: 'node-c3', type: 'Document', label: 'C' },
          { id: 'node-c4', type: 'Fragment', label: 'D' },
        ],
        edges: [],
      }
      const result = validateGraphData(allTypes)
      expect(result.valid).toBe(true)
    })

    test('accepts edges with all three types', () => {
      const allEdgeTypes = {
        metadata: { id: 'etypes', version: 1 },
        nodes: [
          { id: 'node-a', type: 'Concept', label: 'A' },
          { id: 'node-b', type: 'Concept', label: 'B' },
          { id: 'node-c', type: 'Concept', label: 'C' },
          { id: 'node-d', type: 'Concept', label: 'D' },
        ],
        edges: [
          {
            id: 'edge-dep',
            source: 'node-a',
            target: 'node-b',
            type: 'depends_on',
          },
          {
            id: 'edge-rel',
            source: 'node-b',
            target: 'node-c',
            type: 'relates_to',
          },
          {
            id: 'edge-con',
            source: 'node-c',
            target: 'node-d',
            type: 'contains',
          },
        ],
      }
      const result = validateGraphData(allEdgeTypes)
      expect(result.valid).toBe(true)
    })

    test('accepts the example.json data file', async () => {
      const raw = await Bun.file(
        resolve(import.meta.dir, '../../..', '.data/graphs/example.json')
      ).text()
      const data = JSON.parse(raw)
      const result = validateGraphData(data)
      expect(result.valid).toBe(true)
    })
  })

  // -------------------------------------------------------------------------
  // Invalid data
  // -------------------------------------------------------------------------

  describe('invalid data', () => {
    test('rejects missing metadata', () => {
      const result = validateGraphData({ nodes: [], edges: [] })
      expect(result.valid).toBe(false)
      expect(result.errors).toBeDefined()
      expect(result.errors?.length).toBeGreaterThan(0)
    })

    test('rejects missing nodes array', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        edges: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects missing edges array', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects invalid node type', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [{ id: 'node-bad', type: 'InvalidType', label: 'Bad' }],
        edges: [],
      })
      expect(result.valid).toBe(false)
      expect(result.errors?.some((e) => e.includes('type'))).toBe(true)
    })

    test('rejects invalid edge type', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [
          { id: 'node-a', type: 'Concept', label: 'A' },
          { id: 'node-b', type: 'Concept', label: 'B' },
        ],
        edges: [
          {
            id: 'edge-bad',
            source: 'node-a',
            target: 'node-b',
            type: 'invalid_edge_type',
          },
        ],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects node ID without prefix', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [{ id: 'no-prefix', type: 'Concept', label: 'Bad' }],
        edges: [],
      })
      expect(result.valid).toBe(false)
      expect(result.errors?.some((e) => e.includes('pattern'))).toBe(true)
    })

    test('rejects edge ID without prefix', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [
          { id: 'node-a', type: 'Concept', label: 'A' },
          { id: 'node-b', type: 'Concept', label: 'B' },
        ],
        edges: [
          {
            id: 'no-prefix',
            source: 'node-a',
            target: 'node-b',
            type: 'depends_on',
          },
        ],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects empty label', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [{ id: 'node-empty', type: 'Concept', label: '' }],
        edges: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects metadata with version < 1', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 0 },
        nodes: [],
        edges: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects non-integer version', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1.5 },
        nodes: [],
        edges: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects node missing required id', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [{ type: 'Concept', label: 'No ID' }],
        edges: [],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects edge missing required source', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 1 },
        nodes: [
          { id: 'node-a', type: 'Concept', label: 'A' },
          { id: 'node-b', type: 'Concept', label: 'B' },
        ],
        edges: [{ id: 'edge-ns', target: 'node-b', type: 'depends_on' }],
      })
      expect(result.valid).toBe(false)
    })

    test('rejects completely wrong type', () => {
      const result = validateGraphData('not an object')
      expect(result.valid).toBe(false)
    })

    test('rejects null input', () => {
      const result = validateGraphData(null)
      expect(result.valid).toBe(false)
    })

    test('provides meaningful error messages', () => {
      const result = validateGraphData({
        metadata: { id: 'x', version: 0 },
        nodes: [{ id: 'bad-id', type: 'BadType', label: '' }],
        edges: [],
      })
      expect(result.valid).toBe(false)
      expect(result.errors).toBeDefined()
      // Each error should contain a path and description
      for (const error of result.errors ?? []) {
        expect(error.length).toBeGreaterThan(0)
      }
    })
  })
})
