/**
 * Knowledge graph commands -- Meilisearch-backed indexing & hybrid search.
 *
 * Subcommands:
 *   init    - Check health & ensure Meilisearch indexes exist
 *   ingest  - Discover & index context entities (with optional embedding)
 *   search  - Hybrid keyword + semantic search
 *   embed   - Standalone (re-)embedding of indexed entities
 *   similar - Find entities similar to a given one
 *   stats   - Show index statistics
 *   dump    - Not applicable (Meilisearch backend)
 *   load    - Not applicable (Meilisearch backend)
 *   watch   - Planned
 */

import { resolve } from 'node:path'
import { hashFile } from '@agents/core/hash'
import { currentDir, readText } from '@agents/core/runtime'
import { type EntityType, EXIT } from '@agents/core/types'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import fg from 'fast-glob'
import { Ollama } from 'ollama'
import picomatch from 'picomatch'
import { chunkMarkdown, parseFrontmatter } from '../lib/chunker'
import { isOllamaAvailable, prepareEmbeddingText } from '../lib/embedder'
import {
  checkHealth,
  createClient,
  type EmbeddedChunk,
  ensureIndexes,
  getStats,
  type IndexableEntity,
  indexChunks,
  indexEntity,
  searchKeyword,
  searchSemantic,
} from '../lib/meilisearch'
import { hybridSearch, type RankedResult } from '../lib/search'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/**
 * Project root, resolved relative to this file's directory
 * (packages/cli/src/commands/ -> ../../../..)
 */
export const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')

/**
 * Glob patterns for discovering context entities by type.
 * Keys match the EntityType union.
 */
export const ENTITY_PATTERNS: Record<string, string[]> = {
  skill: ['content/skills/*/SKILL.md'],
  plugin: [
    'content/plugins/*/.claude-plugin/plugin.json',
    'content/plugins/**/.claude-plugin/plugin.json',
  ],
  command: ['content/commands/**/*.md'],
  rule: ['content/rules/*.md', 'content/rules/**/*.md'],
  agent: ['content/agents/**/*.md'],
  claude_md: ['CLAUDE.md'],
  output_style: ['content/output-styles/*.md'],
}

/**
 * All valid entity type keys.
 */
export const ENTITY_TYPES = Object.keys(ENTITY_PATTERNS) as string[]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Derive a stable entity ID from a file path relative to PROJECT_ROOT.
 * Replaces `/` with `_` and strips the file extension.
 */
export function entityIdFromPath(relPath: string): string {
  return relPath
    .replace(/\.[^.]+$/, '') // strip extension
    .replaceAll('/', '_')
}

/**
 * Derive a human-readable entity name from frontmatter or file path.
 */
function entityNameFromMeta(meta: Record<string, unknown>, relPath: string): string {
  if (typeof meta.name === 'string' && meta.name.trim()) return meta.name.trim()
  if (typeof meta.title === 'string' && meta.title.trim()) return meta.title.trim()
  // Fall back to filename without extension
  const parts = relPath.split('/')
  const filename = parts[parts.length - 1] ?? relPath
  return filename.replace(/\.[^.]+$/, '')
}

/**
 * Detect the entity type from a relative path by matching it against
 * ENTITY_PATTERNS. Returns the first matching type, or 'rule' as fallback.
 */
function detectEntityType(relPath: string): EntityType {
  for (const [type, patterns] of Object.entries(ENTITY_PATTERNS)) {
    for (const pattern of patterns) {
      const isMatch = picomatch(pattern)
      if (isMatch(relPath)) {
        return type as EntityType
      }
    }
  }
  return 'rule'
}

/**
 * Discover files for a given entity type using fast-glob.
 * Returns absolute paths.
 */
export async function discoverFiles(
  types?: string[]
): Promise<{ type: string; absPath: string; relPath: string }[]> {
  const targetTypes = types ?? ENTITY_TYPES
  const results: { type: string; absPath: string; relPath: string }[] = []
  const seen = new Set<string>()

  for (const entityType of targetTypes) {
    const patterns = ENTITY_PATTERNS[entityType]
    if (!patterns) continue

    const matches = await fg(patterns, { cwd: PROJECT_ROOT, onlyFiles: true })
    for (const match of matches) {
      if (seen.has(match)) continue
      seen.add(match)
      results.push({
        type: entityType,
        absPath: resolve(PROJECT_ROOT, match),
        relPath: match,
      })
    }
  }

  return results
}

/**
 * Generate an embedding vector for a text string.
 */
async function embedText(text: string, model: string): Promise<number[]> {
  const ollama = new Ollama()
  const resp = await ollama.embed({ model, input: text })
  return resp.embeddings[0]
}

// ---------------------------------------------------------------------------
// init
// ---------------------------------------------------------------------------

const initCommand = defineCommand({
  meta: { name: 'init', description: 'Initialize Meilisearch indexes for the knowledge graph' },
  args: {
    ...globalArgs,
    force: { type: 'boolean', description: 'Force re-initialization', default: false },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const spinner = out.spinner('Connecting to Meilisearch...')

    const client = createClient()
    const health = await checkHealth(client)

    if (!health.ok) {
      spinner.error({ text: 'Meilisearch not running' })
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    spinner.update({ text: 'Creating indexes...' })
    await ensureIndexes(client)

    spinner.success({ text: 'Indexes ready' })
    out.success('Meilisearch indexes initialized', {
      indexes: ['documents', 'chunks'],
      status: health.value.status,
    })
  },
})

// ---------------------------------------------------------------------------
// ingest
// ---------------------------------------------------------------------------

const ingestCommand = defineCommand({
  meta: { name: 'ingest', description: 'Ingest context files into Meilisearch' },
  args: {
    ...globalArgs,
    all: { type: 'boolean', description: 'Ingest all entity types', default: false },
    type: { type: 'string', description: 'Entity type to ingest (e.g. skill, rule, plugin)' },
    file: { type: 'string', description: 'Single file to ingest (relative to project root)' },
    embed: { type: 'boolean', description: 'Generate embeddings via Ollama', default: false },
    model: { type: 'string', description: 'Embedding model', default: 'nomic-embed-text' },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const spinner = out.spinner('Connecting to Meilisearch...')

    // Validate arguments
    if (!args.all && !args.type && !args.file) {
      spinner.error({ text: 'No target specified' })
      out.error('Specify --all, --type <type>, or --file <path>')
      process.exit(EXIT.FAILURES)
    }

    // Health check
    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      spinner.error({ text: 'Meilisearch not running' })
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    await ensureIndexes(client)

    // Discover files
    spinner.update({ text: 'Discovering files...' })
    let files: { type: string; absPath: string; relPath: string }[]

    if (args.file) {
      const relPath = args.file
      const absPath = resolve(PROJECT_ROOT, relPath)
      const entityType = detectEntityType(relPath)
      files = [{ type: entityType, absPath, relPath }]
    } else if (args.type) {
      if (!ENTITY_PATTERNS[args.type]) {
        spinner.error({ text: `Unknown entity type: ${args.type}` })
        out.error(`Unknown entity type: ${args.type}. Valid types: ${ENTITY_TYPES.join(', ')}`)
        process.exit(EXIT.FAILURES)
      }
      files = await discoverFiles([args.type])
    } else {
      files = await discoverFiles()
    }

    spinner.update({ text: `Processing ${files.length} files...` })

    let indexed = 0
    let skipped = 0
    let embedded = 0
    const model = args.model

    // Check Ollama availability if embedding requested
    let canEmbed = false
    if (args.embed) {
      canEmbed = await isOllamaAvailable()
      if (!canEmbed) {
        out.warn('Ollama not available -- skipping embeddings')
      }
    }

    for (let i = 0; i < files.length; i++) {
      const file = files[i]!
      spinner.update({ text: `[${i + 1}/${files.length}] ${file.relPath}` })

      try {
        // Read and parse
        const content = await readText(file.absPath)
        const fileHash = await hashFile(file.absPath)

        // Check if already indexed with same hash (incremental)
        try {
          const docsIndex = client.index('documents')
          const existing = await docsIndex.search('', {
            filter: `fileHash = "${fileHash}"`,
            limit: 1,
          })
          if (existing.hits.length > 0 && existing.hits[0].id === entityIdFromPath(file.relPath)) {
            skipped++
            continue
          }
        } catch {
          // Index may not have fileHash as filterable yet; proceed with indexing
        }

        // Parse content
        const parsed = chunkMarkdown(content, { overlapChars: 256 })
        const meta = parsed.frontmatter
        const entityId = entityIdFromPath(file.relPath)
        const entityName = entityNameFromMeta(meta, file.relPath)

        const entity: IndexableEntity = {
          id: entityId,
          type: file.type as EntityType,
          name: entityName,
          title: typeof meta.title === 'string' ? meta.title : undefined,
          description: typeof meta.description === 'string' ? meta.description : undefined,
          content: parsed.content,
          tags: Array.isArray(meta.tags) ? meta.tags.map(String) : undefined,
          filePath: file.relPath,
          fileHash,
          updatedAt: new Date().toISOString(),
        }

        await indexEntity(client, entity)
        indexed++

        // Embedding
        if (args.embed && canEmbed) {
          const chunks = parsed.chunks.filter((c) => c.level !== 'file')
          const embeddedChunks: EmbeddedChunk[] = []

          for (let ci = 0; ci < chunks.length; ci++) {
            const chunk = chunks[ci]!
            const textForEmbed = prepareEmbeddingText(entityName, chunk.text)

            try {
              const embedding = await embedText(textForEmbed, model)
              embeddedChunks.push({
                id: `${entityId}_chunk_${ci}`,
                entityId,
                chunkIndex: ci,
                text: chunk.text,
                embedding,
              })
            } catch {
              // Skip chunk if embedding fails
            }
          }

          if (embeddedChunks.length > 0) {
            await indexChunks(client, entityId, embeddedChunks)
            embedded += embeddedChunks.length
          }
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e)
        out.warn(`Failed to process ${file.relPath}: ${msg}`)
      }
    }

    spinner.success({ text: 'Ingestion complete' })

    const summary = {
      indexed,
      skipped,
      embedded,
      total: files.length,
    }

    out.success(
      `Indexed ${indexed} entities, skipped ${skipped} unchanged, embedded ${embedded} chunks`,
      summary
    )
  },
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

const searchCommand = defineCommand({
  meta: { name: 'search', description: 'Hybrid search across indexed entities' },
  args: {
    ...globalArgs,
    query: { type: 'positional', required: true, description: 'Search query' },
    limit: { type: 'string', default: '10', description: 'Max results' },
    type: { type: 'string', description: 'Filter by entity type' },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const limit = Number.parseInt(args.limit, 10) || 10

    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    const typeFilter = args.type as EntityType | undefined

    // Build keyword search function
    const kwSearch = async (query: string): Promise<RankedResult[]> => {
      const results = await searchKeyword(client, query, { limit: limit * 2, type: typeFilter })
      return results.map((r) => ({
        id: r.id,
        source: 'keyword' as const,
        name: r.name,
        type: r.type,
        description: r.description,
        snippet: r.snippet,
        score: r.score,
        filePath: r.filePath,
      }))
    }

    // Build semantic search function (optional)
    let semSearch: ((query: string) => Promise<RankedResult[]>) | undefined

    const ollamaOk = await isOllamaAvailable()
    if (ollamaOk) {
      semSearch = async (query: string): Promise<RankedResult[]> => {
        const embedding = await embedText(query, 'nomic-embed-text')
        const results = await searchSemantic(client, embedding, { limit: limit * 2 })
        return results.map((r) => ({
          id: r.id,
          source: 'semantic' as const,
          name: r.name,
          type: r.type,
          snippet: r.snippet,
          score: r.score,
          filePath: r.filePath,
        }))
      }
    }

    const result = await hybridSearch(args.query, {
      keywordSearch: kwSearch,
      semanticSearch: semSearch,
      limit,
    })

    if (result.results.length === 0) {
      out.warn(`No results found for: ${args.query}`)
      process.exit(EXIT.FAILURES)
    }

    if (args.json) {
      out.raw({ results: result.results, meta: result.meta })
    } else {
      const tableData = result.results.map((r) => ({
        Name: String(r.name ?? r.id),
        Type: String(r.type ?? ''),
        Score: typeof r.rrfScore === 'number' ? r.rrfScore.toFixed(4) : '',
        Snippet: String(r.snippet ?? '').slice(0, 60),
      }))

      out.info(`Search mode: ${result.meta.mode}`)
      out.table(tableData)
    }
  },
})

// ---------------------------------------------------------------------------
// embed
// ---------------------------------------------------------------------------

const embedCommand = defineCommand({
  meta: {
    name: 'embed',
    description: 'Re-embed all indexed entities without re-indexing from files',
  },
  args: {
    ...globalArgs,
    model: { type: 'string', description: 'Embedding model', default: 'nomic-embed-text' },
    reset: {
      type: 'boolean',
      description: 'Clear existing chunks and regenerate all',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })
    const spinner = out.spinner('Connecting to Meilisearch...')

    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      spinner.error({ text: 'Meilisearch not running' })
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    // Check Ollama
    const ollamaOk = await isOllamaAvailable()
    if (!ollamaOk) {
      spinner.error({ text: 'Ollama not available' })
      out.error(
        `Ollama is not running. Install and start Ollama, then run: ollama pull ${args.model}`
      )
      process.exit(EXIT.ERROR)
    }

    // Reset chunks if requested
    if (args.reset) {
      spinner.update({ text: 'Clearing existing chunks...' })
      try {
        const chunksIndex = client.index('chunks')
        const task = await chunksIndex.deleteAllDocuments()
        await client.waitForTask(task.taskUid)
      } catch {
        // ignore if chunks index does not exist yet
      }
    }

    // Fetch all entities from documents index
    spinner.update({ text: 'Fetching entities from documents index...' })
    const docsIndex = client.index('documents')

    let offset = 0
    const batchSize = 100
    let totalEmbedded = 0
    let entityCount = 0

    // Paginate through all documents
    while (true) {
      const batch = await docsIndex.getDocuments({ limit: batchSize, offset })
      if (batch.results.length === 0) break

      for (const doc of batch.results) {
        entityCount++
        spinner.update({ text: `Embedding entity ${entityCount}: ${doc.name ?? doc.id}` })

        // Read the original file to get content for chunking
        const filePath = doc.filePath as string | undefined
        if (!filePath) continue

        const absPath = resolve(PROJECT_ROOT, filePath)
        let content: string
        try {
          content = await readText(absPath)
        } catch {
          continue // skip if file no longer exists
        }

        const parsed = chunkMarkdown(content, { overlapChars: 256 })
        const chunks = parsed.chunks.filter((c) => c.level !== 'file')
        const entityId = String(doc.id)
        const entityName = String(doc.name ?? doc.id)
        const embeddedChunks: EmbeddedChunk[] = []

        for (let ci = 0; ci < chunks.length; ci++) {
          const chunk = chunks[ci]!
          const textForEmbed = prepareEmbeddingText(entityName, chunk.text)

          try {
            const embedding = await embedText(textForEmbed, args.model)
            embeddedChunks.push({
              id: `${entityId}_chunk_${ci}`,
              entityId,
              chunkIndex: ci,
              text: chunk.text,
              embedding,
            })
          } catch {
            // Skip chunk on embed failure
          }
        }

        if (embeddedChunks.length > 0) {
          await indexChunks(client, entityId, embeddedChunks)
          totalEmbedded += embeddedChunks.length
        }
      }

      offset += batch.results.length
      if (batch.results.length < batchSize) break
    }

    spinner.success({ text: 'Embedding complete' })
    out.success(`Embedded ${totalEmbedded} chunks from ${entityCount} entities`, {
      entities: entityCount,
      chunks: totalEmbedded,
      model: args.model,
    })
  },
})

// ---------------------------------------------------------------------------
// similar
// ---------------------------------------------------------------------------

const similarCommand = defineCommand({
  meta: { name: 'similar', description: 'Find entities similar to a given one' },
  args: {
    ...globalArgs,
    slug: { type: 'positional', required: true, description: 'Entity slug (ID)' },
    k: { type: 'string', default: '10', description: 'Number of similar entities' },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })

    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    // Fetch the target entity
    const docsIndex = client.index('documents')
    let entity: Record<string, unknown>
    try {
      entity = await docsIndex.getDocument(args.slug)
    } catch {
      out.error(`Entity not found: ${args.slug}`)
      process.exit(EXIT.FAILURES)
    }

    // Check Ollama
    const ollamaOk = await isOllamaAvailable()
    if (!ollamaOk) {
      out.error('Ollama is not running. Semantic similarity requires embeddings.')
      process.exit(EXIT.ERROR)
    }

    const k = Number.parseInt(args.k, 10) || 10
    const entityName = String(entity.name ?? entity.id)
    const filePath = String(entity.filePath ?? '')

    // Read entity content for embedding
    let content: string
    try {
      const absPath = resolve(PROJECT_ROOT, filePath)
      content = await readText(absPath)
    } catch {
      out.error(`Cannot read entity file: ${filePath}`)
      process.exit(EXIT.ERROR)
    }

    const parsed = parseFrontmatter(content)
    const textForEmbed = prepareEmbeddingText(entityName, parsed.body.slice(0, 2000))
    const embedding = await embedText(textForEmbed, 'nomic-embed-text')

    // Search semantically, fetching extra to filter self
    const results = await searchSemantic(client, embedding, { limit: k + 1 })
    const filtered = results.filter((r) => r.id !== args.slug)
    const topK = filtered.slice(0, k)

    if (topK.length === 0) {
      out.warn(`No similar entities found for: ${args.slug}`)
      process.exit(EXIT.FAILURES)
    }

    // Resolve names from documents index
    const enriched: Record<string, unknown>[] = []
    for (const r of topK) {
      try {
        const doc = await docsIndex.getDocument(r.id)
        enriched.push({
          Name: String(doc.name ?? r.id),
          Type: String(doc.type ?? r.type),
          Score: r.score?.toFixed(4) ?? '',
          Path: String(doc.filePath ?? r.filePath),
        })
      } catch {
        enriched.push({
          Name: r.name,
          Type: r.type,
          Score: r.score?.toFixed(4) ?? '',
          Path: r.filePath,
        })
      }
    }

    if (args.json) {
      out.raw(enriched)
    } else {
      out.info(`Entities similar to: ${entityName}`)
      out.table(enriched)
    }
  },
})

// ---------------------------------------------------------------------------
// stats
// ---------------------------------------------------------------------------

const statsCommand = defineCommand({
  meta: { name: 'stats', description: 'Show knowledge graph statistics' },
  args: { ...globalArgs },
  async run({ args }) {
    const out = createOutput({ json: args.json, quiet: args.quiet })

    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      out.error('Meilisearch not running. Start with: just mcp-up')
      process.exit(EXIT.ERROR)
    }

    const stats = await getStats(client)

    if (args.json) {
      out.raw(stats)
    } else {
      out.info(`Documents: ${stats.documents}`)
      out.info(`Chunks: ${stats.chunks}`)
      out.info(`Embeddings: ${stats.embeddings}`)

      if (Object.keys(stats.byType).length > 0) {
        const typeTable = Object.entries(stats.byType).map(([type, count]) => ({
          Type: type,
          Count: count,
        }))
        out.table(typeTable)
      } else {
        out.info('No entities indexed yet')
      }
    }
  },
})

// ---------------------------------------------------------------------------
// dump, load, watch -- stubs
// ---------------------------------------------------------------------------

const dumpCommand = defineCommand({
  meta: { name: 'dump', description: 'Dump database to SQL file' },
  args: { ...globalArgs },
  run() {
    console.log(
      'dump/load not supported with Meilisearch backend. Use ai-tools kg ingest to re-index.'
    )
  },
})

const loadCommand = defineCommand({
  meta: { name: 'load', description: 'Load database from SQL dump' },
  args: { ...globalArgs },
  run() {
    console.log(
      'dump/load not supported with Meilisearch backend. Use ai-tools kg ingest to re-index.'
    )
  },
})

const watchCommand = defineCommand({
  meta: { name: 'watch', description: 'Watch for file changes and auto-embed' },
  args: { ...globalArgs, model: { type: 'string', default: 'nomic-embed-text' } },
  run() {
    console.log('not yet implemented -- file watching for Meilisearch coming soon')
  },
})

// ---------------------------------------------------------------------------
// Main command
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'kg', description: 'Knowledge graph embedding and search' },
  subCommands: {
    init: initCommand,
    ingest: ingestCommand,
    search: searchCommand,
    embed: embedCommand,
    similar: similarCommand,
    stats: statsCommand,
    dump: dumpCommand,
    load: loadCommand,
    watch: watchCommand,
  },
})
