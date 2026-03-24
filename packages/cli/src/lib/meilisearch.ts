/**
 * Meilisearch client module for indexing and searching context entities.
 *
 * Provides keyword search (full-text with typo tolerance) and vector
 * similarity search (semantic via stored embeddings). Two indexes are
 * managed:
 *
 *   - `documents` -- one document per context entity (skill, plugin, etc.)
 *   - `chunks`    -- one document per embedded text chunk, with `_vectors`
 *
 * All public functions accept an explicit `MeiliSearch` client so that
 * callers control instantiation and lifecycle.
 */

import { type EnqueuedTask, MeiliSearch, type SearchResponse } from 'meilisearch'
import { CliError, type EntityType, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface IndexableEntity {
  id: string
  type: EntityType
  name: string
  title?: string
  description?: string
  content: string
  tags?: string[]
  filePath: string
  fileHash: string
  createdAt?: string
  updatedAt?: string
}

export interface SearchOpts {
  limit?: number
  offset?: number
  type?: EntityType
  tags?: string[]
  sort?: string
}

export interface SearchResult {
  id: string
  type: EntityType
  name: string
  description?: string
  snippet?: string
  score?: number
  filePath: string
}

export interface EmbeddedChunk {
  id: string
  entityId: string
  chunkIndex: number
  text: string
  embedding: number[]
}

export interface MeiliStats {
  documents: number
  chunks: number
  embeddings: number
  byType: Record<string, number>
}

// ---------------------------------------------------------------------------
// Index configuration
// ---------------------------------------------------------------------------

const DOCUMENTS_INDEX = 'documents'
const CHUNKS_INDEX = 'chunks'

const DOCUMENTS_CONFIG = {
  searchableAttributes: ['name', 'title', 'description', 'content'],
  filterableAttributes: ['type', 'tags', 'fileHash'],
  sortableAttributes: ['updatedAt', 'createdAt'],
  displayedAttributes: ['id', 'type', 'name', 'title', 'description', 'filePath', 'tags'],
} as const

const CHUNKS_CONFIG = {
  searchableAttributes: ['text'],
  filterableAttributes: ['entityId'],
} as const

// ---------------------------------------------------------------------------
// Connection
// ---------------------------------------------------------------------------

/**
 * Create a new MeiliSearch client.
 *
 * Reads `MEILI_HOST` and `MEILI_MASTER_KEY` from the environment when
 * explicit values are not provided.
 */
export function createClient(opts?: { host?: string; apiKey?: string }): MeiliSearch {
  const host = opts?.host ?? process.env.MEILI_HOST ?? 'http://localhost:7700'
  const apiKey = opts?.apiKey ?? process.env.MEILI_MASTER_KEY
  return new MeiliSearch({ host, apiKey })
}

/**
 * Check that the Meilisearch instance is reachable and healthy.
 */
export async function checkHealth(client: MeiliSearch): Promise<Result<{ status: string }>> {
  try {
    const health = await client.health()
    return ok({ status: health.status })
  } catch (e) {
    return err(
      new CliError(
        'Meilisearch health check failed',
        'MEILI_HEALTH',
        'Is Meilisearch running? Try: docker compose -f .docker/compose.yaml up -d',
        e
      )
    )
  }
}

/**
 * Create the `documents` and `chunks` indexes if they do not exist, then
 * configure searchable, filterable, and sortable attributes.
 */
export async function ensureIndexes(client: MeiliSearch): Promise<void> {
  // Create indexes (idempotent -- Meilisearch ignores if they exist)
  await waitForTask(client, await client.createIndex(DOCUMENTS_INDEX, { primaryKey: 'id' }))
  await waitForTask(client, await client.createIndex(CHUNKS_INDEX, { primaryKey: 'id' }))

  // Configure documents index
  const docsIndex = client.index(DOCUMENTS_INDEX)
  await waitForTask(
    client,
    await docsIndex.updateSearchableAttributes([...DOCUMENTS_CONFIG.searchableAttributes])
  )
  await waitForTask(
    client,
    await docsIndex.updateFilterableAttributes([...DOCUMENTS_CONFIG.filterableAttributes])
  )
  await waitForTask(
    client,
    await docsIndex.updateSortableAttributes([...DOCUMENTS_CONFIG.sortableAttributes])
  )
  await waitForTask(
    client,
    await docsIndex.updateDisplayedAttributes([...DOCUMENTS_CONFIG.displayedAttributes])
  )

  // Configure chunks index
  const chunksIndex = client.index(CHUNKS_INDEX)
  await waitForTask(
    client,
    await chunksIndex.updateSearchableAttributes([...CHUNKS_CONFIG.searchableAttributes])
  )
  await waitForTask(
    client,
    await chunksIndex.updateFilterableAttributes([...CHUNKS_CONFIG.filterableAttributes])
  )
}

// ---------------------------------------------------------------------------
// Indexing
// ---------------------------------------------------------------------------

/**
 * Add or update a single entity in the `documents` index.
 */
export async function indexEntity(client: MeiliSearch, entity: IndexableEntity): Promise<void> {
  const index = client.index(DOCUMENTS_INDEX)
  await waitForTask(client, await index.addDocuments([entity]))
}

/**
 * Batch-add entities to the `documents` index. Returns the number
 * successfully indexed and any error messages.
 */
export async function indexBatch(
  client: MeiliSearch,
  entities: IndexableEntity[]
): Promise<{ indexed: number; errors: string[] }> {
  if (entities.length === 0) return { indexed: 0, errors: [] }

  const errors: string[] = []
  const index = client.index(DOCUMENTS_INDEX)

  // Meilisearch handles batches well, but we chunk into groups of 1000
  // to keep memory bounded and provide granular error reporting.
  const BATCH_SIZE = 1000
  let indexed = 0

  for (let i = 0; i < entities.length; i += BATCH_SIZE) {
    const batch = entities.slice(i, i + BATCH_SIZE)
    try {
      const task = await index.addDocuments(batch)
      const result = await client.waitForTask(task.taskUid)
      if (result.status === 'succeeded') {
        indexed += batch.length
      } else {
        errors.push(
          `Batch ${i / BATCH_SIZE}: task ${result.status} -- ${result.error?.message ?? 'unknown error'}`
        )
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      errors.push(`Batch ${i / BATCH_SIZE}: ${msg}`)
    }
  }

  return { indexed, errors }
}

/**
 * Delete an entity by ID from the `documents` index. Also removes any
 * associated chunks from the `chunks` index.
 */
export async function deleteEntity(client: MeiliSearch, id: string): Promise<void> {
  // Delete from documents
  const docsIndex = client.index(DOCUMENTS_INDEX)
  await waitForTask(client, await docsIndex.deleteDocument(id))

  // Delete associated chunks by filter
  const chunksIndex = client.index(CHUNKS_INDEX)
  try {
    await waitForTask(client, await chunksIndex.deleteDocuments({ filter: `entityId = "${id}"` }))
  } catch {
    // Chunk deletion is best-effort -- the entity may never have had chunks.
  }
}

// ---------------------------------------------------------------------------
// Keyword search
// ---------------------------------------------------------------------------

/**
 * Full-text keyword search on the `documents` index.
 *
 * Supports filtering by entity type and tags, sorting, and highlighted
 * snippet extraction.
 */
export async function searchKeyword(
  client: MeiliSearch,
  query: string,
  opts?: SearchOpts
): Promise<SearchResult[]> {
  const index = client.index(DOCUMENTS_INDEX)

  const filter = buildFilter(opts)
  const searchParams: Record<string, unknown> = {
    limit: opts?.limit ?? 20,
    offset: opts?.offset ?? 0,
    attributesToHighlight: ['content', 'description'],
    attributesToCrop: ['content'],
    cropLength: 80,
    showRankingScore: true,
  }

  if (filter) searchParams.filter = filter
  if (opts?.sort) searchParams.sort = [opts.sort]

  const response: SearchResponse = await index.search(query, searchParams)

  return (response.hits ?? []).map((hit) => ({
    id: String(hit.id),
    type: hit.type as EntityType,
    name: String(hit.name),
    description: hit.description ? String(hit.description) : undefined,
    snippet: extractSnippet(hit),
    score: hit._rankingScore as number | undefined,
    filePath: String(hit.filePath),
  }))
}

// ---------------------------------------------------------------------------
// Vector / semantic search
// ---------------------------------------------------------------------------

/**
 * Store embedded text chunks in the `chunks` index.
 *
 * Each chunk is stored with its vector in the `_vectors` field so that
 * Meilisearch can perform vector similarity search.
 */
export async function indexChunks(
  client: MeiliSearch,
  entityId: string,
  chunks: EmbeddedChunk[]
): Promise<void> {
  if (chunks.length === 0) return

  const index = client.index(CHUNKS_INDEX)

  const documents = chunks.map((chunk) => ({
    id: chunk.id,
    entityId,
    chunkIndex: chunk.chunkIndex,
    text: chunk.text,
    _vectors: { default: chunk.embedding },
  }))

  await waitForTask(client, await index.addDocuments(documents))
}

/**
 * Semantic similarity search using a pre-computed embedding vector.
 *
 * Searches the `chunks` index and deduplicates results by `entityId`
 * so that each entity appears at most once.
 */
export async function searchSemantic(
  client: MeiliSearch,
  embedding: number[],
  opts?: SearchOpts
): Promise<SearchResult[]> {
  const index = client.index(CHUNKS_INDEX)

  const filter = buildChunkFilter(opts)
  const searchParams: Record<string, unknown> = {
    vector: embedding,
    limit: (opts?.limit ?? 20) * 3, // Over-fetch before dedup
    showRankingScore: true,
    hybrid: { semanticRatio: 1.0 },
  }

  if (filter) searchParams.filter = filter

  const response = await index.search('', searchParams)

  // Deduplicate by entityId, keeping the best score
  const seen = new Map<string, SearchResult>()

  for (const hit of response.hits ?? []) {
    const entityId = String(hit.entityId)
    if (!seen.has(entityId)) {
      seen.set(entityId, {
        id: entityId,
        type: 'skill' as EntityType, // Will be resolved at a higher layer
        name: entityId,
        snippet: hit.text ? String(hit.text).slice(0, 200) : undefined,
        score: hit._rankingScore as number | undefined,
        filePath: '',
      })
    }
  }

  const limit = opts?.limit ?? 20
  return [...seen.values()].slice(0, limit)
}

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

/**
 * Gather counts of documents, chunks, and embeddings across indexes.
 */
export async function getStats(client: MeiliSearch): Promise<MeiliStats> {
  const allStats = await client.getStats()

  const docsStats = allStats.indexes[DOCUMENTS_INDEX]
  const chunksStats = allStats.indexes[CHUNKS_INDEX]

  const documents = docsStats?.numberOfDocuments ?? 0
  const chunks = chunksStats?.numberOfDocuments ?? 0

  // Count by type via faceted search
  const byType: Record<string, number> = {}
  try {
    const docsIndex = client.index(DOCUMENTS_INDEX)
    const facets = await docsIndex.search('', {
      limit: 0,
      facets: ['type'],
    })
    const typeFacets = facets.facetDistribution?.type
    if (typeFacets) {
      for (const [t, count] of Object.entries(typeFacets)) {
        byType[t] = count
      }
    }
  } catch {
    // facets may not work if index is empty or type is not filterable yet
  }

  return {
    documents,
    chunks,
    embeddings: chunks, // Each chunk has exactly one embedding vector
    byType,
  }
}

// ---------------------------------------------------------------------------
// Health / availability checks (for Phase 5 fallback logic)
// ---------------------------------------------------------------------------

/**
 * Quick connectivity check. Returns `false` on any connection error.
 */
export async function isAvailable(client: MeiliSearch): Promise<boolean> {
  try {
    const health = await client.health()
    return health.status === 'available'
  } catch {
    return false
  }
}

/**
 * Check whether the `chunks` index has any documents (implying embeddings
 * have been indexed).
 */
export async function hasEmbeddings(client: MeiliSearch): Promise<boolean> {
  try {
    const stats = await client.getStats()
    return (stats.indexes[CHUNKS_INDEX]?.numberOfDocuments ?? 0) > 0
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Wait for an enqueued Meilisearch task to complete.
 */
async function waitForTask(client: MeiliSearch, task: EnqueuedTask): Promise<void> {
  await client.waitForTask(task.taskUid)
}

/**
 * Build a Meilisearch filter string from search options.
 * Applies to the `documents` index.
 */
function buildFilter(opts?: SearchOpts): string | undefined {
  if (!opts) return undefined

  const parts: string[] = []

  if (opts.type) {
    parts.push(`type = "${opts.type}"`)
  }

  if (opts.tags && opts.tags.length > 0) {
    // Meilisearch array filter: tags = "value" OR tags = "value2"
    const tagFilters = opts.tags.map((t) => `tags = "${t}"`)
    parts.push(`(${tagFilters.join(' OR ')})`)
  }

  return parts.length > 0 ? parts.join(' AND ') : undefined
}

/**
 * Build a filter string for the `chunks` index.
 */
function buildChunkFilter(opts?: SearchOpts): string | undefined {
  // Currently chunks only support entityId filtering, which is not
  // exposed through SearchOpts. Reserved for future extension.
  return undefined
}

/**
 * Extract a highlighted snippet from a Meilisearch hit.
 *
 * Prefers the cropped content highlight, falls back to description highlight,
 * then raw description.
 */
function extractSnippet(hit: Record<string, unknown>): string | undefined {
  const formatted = hit._formatted as Record<string, unknown> | undefined
  if (formatted) {
    if (formatted.content) return String(formatted.content)
    if (formatted.description) return String(formatted.description)
  }
  if (hit.description) return String(hit.description)
  return undefined
}
