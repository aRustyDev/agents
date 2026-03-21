import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import type { MeiliSearch } from 'meilisearch'
import {
  checkHealth,
  createClient,
  deleteEntity,
  type EmbeddedChunk,
  ensureIndexes,
  getStats,
  hasEmbeddings,
  type IndexableEntity,
  indexBatch,
  indexChunks,
  indexEntity,
  isAvailable,
  searchKeyword,
  searchSemantic,
} from '../lib/meilisearch'

// ---------------------------------------------------------------------------
// Skip logic -- all integration tests are skipped if Meilisearch is down
// ---------------------------------------------------------------------------

let skip = false
let client: MeiliSearch

// Test-specific index suffix to avoid clobbering real data. The module
// uses fixed index names ("documents", "chunks"), so we rely on cleanup
// rather than isolation.
const TEST_PREFIX = '__test_meili_'
const TEST_ENTITY_ID = `${TEST_PREFIX}entity_1`
const TEST_ENTITY_ID_2 = `${TEST_PREFIX}entity_2`
const TEST_CHUNK_ID_1 = `${TEST_PREFIX}chunk_0`
const TEST_CHUNK_ID_2 = `${TEST_PREFIX}chunk_1`

function makeTestEntity(overrides?: Partial<IndexableEntity>): IndexableEntity {
  return {
    id: TEST_ENTITY_ID,
    type: 'skill',
    name: 'test-skill',
    title: 'Test Skill',
    description: 'A test skill for Meilisearch integration tests',
    content:
      'This is the full text content of the test skill. It covers TypeScript patterns and best practices.',
    tags: ['test', 'typescript'],
    filePath: 'context/skills/test-skill/SKILL.md',
    fileHash: 'abc123def456',
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-03-18T00:00:00Z',
    ...overrides,
  }
}

function makeTestEntity2(): IndexableEntity {
  return makeTestEntity({
    id: TEST_ENTITY_ID_2,
    type: 'command',
    name: 'test-command',
    title: 'Test Command',
    description: 'A test command for filtering',
    content: 'This command handles deployment automation for Kubernetes clusters.',
    tags: ['test', 'kubernetes'],
    filePath: 'context/commands/test-command.md',
    fileHash: 'def789ghi012',
  })
}

function makeTestChunks(): EmbeddedChunk[] {
  // Use simple 3-dimensional vectors for testing. Real embeddings are
  // typically 768+ dimensions but Meilisearch accepts any dimensionality.
  return [
    {
      id: TEST_CHUNK_ID_1,
      entityId: TEST_ENTITY_ID,
      chunkIndex: 0,
      text: 'TypeScript patterns and best practices for type safety.',
      embedding: [0.1, 0.2, 0.3],
    },
    {
      id: TEST_CHUNK_ID_2,
      entityId: TEST_ENTITY_ID,
      chunkIndex: 1,
      text: 'Advanced generics and conditional types in modern TypeScript.',
      embedding: [0.4, 0.5, 0.6],
    },
  ]
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

beforeAll(async () => {
  client = createClient()

  try {
    const resp = await fetch('http://localhost:7700/health')
    skip = !resp.ok
  } catch {
    skip = true
  }

  if (skip) {
    console.log('Meilisearch not running -- skipping integration tests')
    return
  }

  // Ensure indexes exist before tests
  await ensureIndexes(client)
})

afterAll(async () => {
  if (skip) return

  // Clean up test documents by deleting them individually
  const docsIndex = client.index('documents')
  const chunksIndex = client.index('chunks')

  try {
    const deleteDocTask = await docsIndex.deleteDocuments({
      filter: 'fileHash = "abc123def456" OR fileHash = "def789ghi012"',
    })
    await client.waitForTask(deleteDocTask.taskUid)
  } catch {
    // Best-effort cleanup
  }

  try {
    const deleteChunkTask = await chunksIndex.deleteDocuments({
      filter: `entityId = "${TEST_ENTITY_ID}"`,
    })
    await client.waitForTask(deleteChunkTask.taskUid)
  } catch {
    // Best-effort cleanup
  }
})

// ---------------------------------------------------------------------------
// createClient
// ---------------------------------------------------------------------------

describe('createClient', () => {
  test('returns a MeiliSearch instance', () => {
    const c = createClient()
    // The MeiliSearch class exposes .health() among other methods
    expect(typeof c.health).toBe('function')
    expect(typeof c.index).toBe('function')
  })

  test('uses custom host when provided', () => {
    const c = createClient({ host: 'http://custom:9999' })
    expect(typeof c.health).toBe('function')
  })
})

// ---------------------------------------------------------------------------
// checkHealth
// ---------------------------------------------------------------------------

describe('checkHealth', () => {
  test('returns ok with status when Meilisearch is up', async () => {
    if (skip) return

    const result = await checkHealth(client)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.status).toBe('available')
    }
  })

  test('returns error for unreachable host', async () => {
    const badClient = createClient({ host: 'http://localhost:19999' })
    const result = await checkHealth(badClient)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('MEILI_HEALTH')
    }
  })
})

// ---------------------------------------------------------------------------
// ensureIndexes
// ---------------------------------------------------------------------------

describe('ensureIndexes', () => {
  test('creates indexes without error', async () => {
    if (skip) return

    // Should be idempotent -- calling again should not throw
    await ensureIndexes(client)

    // Verify indexes exist
    const indexes = await client.getIndexes()
    const names = indexes.results.map((i) => i.uid)
    expect(names).toContain('documents')
    expect(names).toContain('chunks')
  })
})

// ---------------------------------------------------------------------------
// indexEntity + searchKeyword round-trip
// ---------------------------------------------------------------------------

describe('indexEntity + searchKeyword', () => {
  test('indexes a test entity and finds it via keyword search', async () => {
    if (skip) return

    const entity = makeTestEntity()
    await indexEntity(client, entity)

    // Meilisearch indexing is async -- wait a moment for processing
    await Bun.sleep(500)

    const results = await searchKeyword(client, 'TypeScript patterns')
    expect(results.length).toBeGreaterThan(0)

    const found = results.find((r) => r.id === TEST_ENTITY_ID)
    expect(found).toBeDefined()
    expect(found!.type).toBe('skill')
    expect(found!.name).toBe('test-skill')
    expect(found!.filePath).toBe('context/skills/test-skill/SKILL.md')
  })

  test('returns highlighted snippets', async () => {
    if (skip) return

    const results = await searchKeyword(client, 'TypeScript patterns')
    const found = results.find((r) => r.id === TEST_ENTITY_ID)
    expect(found).toBeDefined()
    // snippet should exist (either highlighted or raw description)
    expect(found!.snippet).toBeDefined()
  })

  test('returns ranking scores', async () => {
    if (skip) return

    const results = await searchKeyword(client, 'TypeScript')
    const found = results.find((r) => r.id === TEST_ENTITY_ID)
    expect(found).toBeDefined()
    expect(found!.score).toBeDefined()
    expect(typeof found!.score).toBe('number')
  })
})

// ---------------------------------------------------------------------------
// Filtering
// ---------------------------------------------------------------------------

describe('type and tag filtering', () => {
  test('filters by entity type', async () => {
    if (skip) return

    // Index a second entity of different type
    await indexEntity(client, makeTestEntity2())
    await Bun.sleep(500)

    const skillResults = await searchKeyword(client, 'test', { type: 'skill' })
    const commandResults = await searchKeyword(client, 'test', { type: 'command' })

    // Skill results should include our skill, not the command
    const skillIds = skillResults.map((r) => r.id)
    const commandIds = commandResults.map((r) => r.id)

    if (skillIds.includes(TEST_ENTITY_ID)) {
      expect(skillIds).not.toContain(TEST_ENTITY_ID_2)
    }
    if (commandIds.includes(TEST_ENTITY_ID_2)) {
      expect(commandIds).not.toContain(TEST_ENTITY_ID)
    }
  })

  test('filters by tags', async () => {
    if (skip) return

    const results = await searchKeyword(client, 'test', {
      tags: ['kubernetes'],
    })

    // Should find the command (tagged kubernetes) but not the skill
    const found = results.find((r) => r.id === TEST_ENTITY_ID_2)
    if (found) {
      expect(found.type).toBe('command')
    }

    const notFound = results.find((r) => r.id === TEST_ENTITY_ID)
    expect(notFound).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// indexBatch
// ---------------------------------------------------------------------------

describe('indexBatch', () => {
  test('batch indexes multiple entities', async () => {
    if (skip) return

    const entities = [makeTestEntity(), makeTestEntity2()]
    const result = await indexBatch(client, entities)

    expect(result.indexed).toBe(2)
    expect(result.errors).toHaveLength(0)
  })

  test('returns zero for empty batch', async () => {
    if (skip) return

    const result = await indexBatch(client, [])
    expect(result.indexed).toBe(0)
    expect(result.errors).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// indexChunks
// ---------------------------------------------------------------------------

describe('indexChunks', () => {
  test('stores chunks in the chunks index', async () => {
    if (skip) return

    const chunks = makeTestChunks()
    await indexChunks(client, TEST_ENTITY_ID, chunks)

    // Verify by searching the chunks index directly
    await Bun.sleep(500)

    const chunksIndex = client.index('chunks')
    const searchResult = await chunksIndex.search('TypeScript patterns')
    expect(searchResult.hits.length).toBeGreaterThan(0)

    const found = searchResult.hits.find((h) => h.id === TEST_CHUNK_ID_1)
    expect(found).toBeDefined()
    expect(found!.entityId).toBe(TEST_ENTITY_ID)
  })
})

// ---------------------------------------------------------------------------
// deleteEntity
// ---------------------------------------------------------------------------

describe('deleteEntity', () => {
  test('removes entity from documents index', async () => {
    if (skip) return

    // Ensure entity exists first
    await indexEntity(client, makeTestEntity())
    await Bun.sleep(300)

    // Delete it
    await deleteEntity(client, TEST_ENTITY_ID)
    await Bun.sleep(500)

    // Verify it is gone
    const docsIndex = client.index('documents')
    try {
      await docsIndex.getDocument(TEST_ENTITY_ID)
      // If we get here, the document still exists -- fail
      expect(true).toBe(false)
    } catch (e) {
      // Expected: document not found
      expect(String(e)).toContain('not found')
    }
  })
})

// ---------------------------------------------------------------------------
// getStats
// ---------------------------------------------------------------------------

describe('getStats', () => {
  test('returns document and chunk counts', async () => {
    if (skip) return

    const stats = await getStats(client)
    expect(typeof stats.documents).toBe('number')
    expect(typeof stats.chunks).toBe('number')
    expect(typeof stats.embeddings).toBe('number')
    expect(stats.documents).toBeGreaterThanOrEqual(0)
    expect(stats.chunks).toBeGreaterThanOrEqual(0)
    expect(typeof stats.byType).toBe('object')
  })
})

// ---------------------------------------------------------------------------
// isAvailable
// ---------------------------------------------------------------------------

describe('isAvailable', () => {
  test('returns true when Meilisearch is running', async () => {
    if (skip) return

    const available = await isAvailable(client)
    expect(available).toBe(true)
  })

  test('returns false for unreachable host', async () => {
    const badClient = createClient({ host: 'http://localhost:19999' })
    const available = await isAvailable(badClient)
    expect(available).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// hasEmbeddings
// ---------------------------------------------------------------------------

describe('hasEmbeddings', () => {
  test('returns a boolean', async () => {
    if (skip) return

    const result = await hasEmbeddings(client)
    expect(typeof result).toBe('boolean')
  })
})
