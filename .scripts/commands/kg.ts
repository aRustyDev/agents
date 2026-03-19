import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'kg', description: 'Knowledge graph embedding and search' },
  subCommands: {
    init: defineCommand({
      meta: { name: 'init', description: 'Initialize or reset the knowledge graph database' },
      args: { ...globalArgs, force: { type: 'boolean', description: 'Force re-initialization', default: false } },
      run() { console.error('kg init: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    ingest: defineCommand({
      meta: { name: 'ingest', description: 'Ingest context files into the knowledge graph' },
      args: {
        ...globalArgs,
        all: { type: 'boolean', description: 'Ingest all entity types', default: false },
        type: { type: 'string', description: 'Entity type to ingest' },
        file: { type: 'string', description: 'Single file to ingest' },
        model: { type: 'string', description: 'Embedding model', default: 'nomic-embed-text' },
      },
      run() { console.error('kg ingest: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    search: defineCommand({
      meta: { name: 'search', description: 'Semantic search across the knowledge graph' },
      args: { ...globalArgs, query: { type: 'positional', required: true }, limit: { type: 'string', default: '10' } },
      run() { console.error('kg search: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    similar: defineCommand({
      meta: { name: 'similar', description: 'Find entities similar to a given one' },
      args: { ...globalArgs, slug: { type: 'positional', required: true }, k: { type: 'string', default: '10' } },
      run() { console.error('kg similar: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    stats: defineCommand({
      meta: { name: 'stats', description: 'Show knowledge graph statistics' },
      args: { ...globalArgs },
      run() { console.error('kg stats: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    dump: defineCommand({
      meta: { name: 'dump', description: 'Dump database to SQL file' },
      args: { ...globalArgs },
      run() { console.error('kg dump: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    load: defineCommand({
      meta: { name: 'load', description: 'Load database from SQL dump' },
      args: { ...globalArgs },
      run() { console.error('kg load: not yet implemented (Phase 6)'); process.exit(2) },
    }),
    watch: defineCommand({
      meta: { name: 'watch', description: 'Watch for file changes and auto-embed' },
      args: { ...globalArgs, model: { type: 'string', default: 'nomic-embed-text' } },
      run() { console.error('kg watch: not yet implemented (Phase 6)'); process.exit(2) },
    }),
  },
})
