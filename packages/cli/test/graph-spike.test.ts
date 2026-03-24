/**
 * Phase 0 spike: Graphology round-trip validation.
 *
 * Verifies that custom properties on nodes and edges survive
 * import → mutate → export without data loss.
 */

import { describe, expect, test } from 'bun:test'
import Graph from 'graphology'

describe('Graphology round-trip', () => {
  const sampleData = {
    attributes: { name: 'test-graph' },
    nodes: [
      {
        key: 'node-a',
        attributes: {
          type: 'Concept',
          label: 'Neural Network',
          properties: {
            domain: 'ML',
            complexity: 'high',
            nested: { deep: true },
          },
        },
      },
      {
        key: 'node-b',
        attributes: {
          type: 'Component',
          label: 'GPU Cluster',
          properties: { cores: 8192, vendor: 'nvidia' },
        },
      },
    ],
    edges: [
      {
        key: 'edge-1',
        source: 'node-a',
        target: 'node-b',
        attributes: {
          type: 'depends_on',
          properties: { weight: 0.8, critical: true },
        },
      },
    ],
  }

  test('import preserves all node attributes', () => {
    const graph = new Graph()
    graph.import(sampleData)

    expect(graph.order).toBe(2)
    expect(graph.getNodeAttribute('node-a', 'label')).toBe('Neural Network')
    expect(graph.getNodeAttribute('node-a', 'properties')).toEqual({
      domain: 'ML',
      complexity: 'high',
      nested: { deep: true },
    })
  })

  test('import preserves all edge attributes', () => {
    const graph = new Graph()
    graph.import(sampleData)

    expect(graph.size).toBe(1)
    expect(graph.getEdgeAttribute('edge-1', 'type')).toBe('depends_on')
    expect(graph.getEdgeAttribute('edge-1', 'properties')).toEqual({
      weight: 0.8,
      critical: true,
    })
  })

  test('mutate then export preserves original + new data', () => {
    const graph = new Graph()
    graph.import(sampleData)

    // Add a node with custom properties
    graph.addNode('node-c', {
      type: 'Document',
      label: 'API Spec',
      properties: { format: 'openapi', version: '3.1' },
    })

    // Add an edge
    graph.addEdge('node-b', 'node-c', {
      type: 'produces',
      properties: { automated: true },
    })

    // Modify existing node
    graph.setNodeAttribute('node-a', 'properties', {
      ...graph.getNodeAttribute('node-a', 'properties'),
      updated: true,
    })

    // Export
    const exported = graph.export()

    // Verify original nodes preserved
    const nodeA = exported.nodes.find((n) => n.key === 'node-a')
    expect(nodeA).toBeDefined()
    expect(nodeA?.attributes.properties.domain).toBe('ML')
    expect(nodeA?.attributes.properties.updated).toBe(true)
    expect(nodeA?.attributes.properties.nested).toEqual({ deep: true })

    // Verify new node preserved
    const nodeC = exported.nodes.find((n) => n.key === 'node-c')
    expect(nodeC).toBeDefined()
    expect(nodeC?.attributes.properties).toEqual({
      format: 'openapi',
      version: '3.1',
    })

    // Verify original edge preserved
    const edge1 = exported.edges.find((e) => e.key === 'edge-1')
    expect(edge1).toBeDefined()
    expect(edge1?.attributes.properties).toEqual({
      weight: 0.8,
      critical: true,
    })

    // Verify new edge preserved
    const newEdge = exported.edges.find((e) => e.source === 'node-b' && e.target === 'node-c')
    expect(newEdge).toBeDefined()
    expect(newEdge?.attributes.properties).toEqual({ automated: true })
  })

  test('re-import exported data is lossless', () => {
    const graph1 = new Graph()
    graph1.import(sampleData)
    graph1.addNode('node-c', {
      type: 'Fragment',
      label: 'Config',
      properties: { x: 1 },
    })

    const exported = graph1.export()

    const graph2 = new Graph()
    graph2.import(exported)

    expect(graph2.order).toBe(graph1.order)
    expect(graph2.size).toBe(graph1.size)
    expect(graph2.getNodeAttribute('node-a', 'properties')).toEqual(
      graph1.getNodeAttribute('node-a', 'properties')
    )
    expect(graph2.getNodeAttribute('node-c', 'properties')).toEqual(
      graph1.getNodeAttribute('node-c', 'properties')
    )
  })

  test('graph attributes survive round-trip', () => {
    const graph = new Graph()
    graph.import(sampleData)

    const exported = graph.export()
    expect(exported.attributes).toEqual({ name: 'test-graph' })
  })
})
