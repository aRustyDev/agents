import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'registry', description: 'Registry crawling and component discovery' },
  subCommands: {
    crawl: defineCommand({
      meta: { name: 'crawl', description: 'Crawl registries for Claude components' },
      args: {
        ...globalArgs,
        tier: { type: 'string', description: 'Registry tier (api|scrape|awesome|all)', default: 'all' },
        output: { type: 'string', description: 'Output directory' },
        resume: { type: 'boolean', description: 'Resume from checkpoint', default: false },
        dryRun: { type: 'boolean', description: 'Show what would be crawled', default: false },
      },
      run() { console.error('registry crawl: not yet implemented (Phase 5)'); process.exit(2) },
    }),
    validate: defineCommand({
      meta: { name: 'validate', description: 'Validate existing crawl output' },
      args: { ...globalArgs },
      run() { console.error('registry validate: not yet implemented (Phase 5)'); process.exit(2) },
    }),
    stats: defineCommand({
      meta: { name: 'stats', description: 'Show crawl statistics' },
      args: { ...globalArgs },
      run() { console.error('registry stats: not yet implemented (Phase 5)'); process.exit(2) },
    }),
  },
})
