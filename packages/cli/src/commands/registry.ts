/**
 * Registry crawling and component discovery commands.
 *
 * Subcommands:
 *   crawl    - Crawl registries for Claude components (by tier)
 *   validate - Validate existing NDJSON crawl output
 *   stats    - Show crawl statistics from checkpoint state
 */

import { existsSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import {
  computeStats,
  crawlTier,
  loadState,
  saveState,
  validateNdjson,
} from '@agents/sdk/catalog/pipeline/crawl'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

const DEFAULT_OUTPUT_DIR = '/private/etc/dotfiles/adam/services/databases/meilisearch/indices'

export default defineCommand({
  meta: { name: 'registry', description: 'Registry crawling and component discovery' },
  subCommands: {
    crawl: defineCommand({
      meta: { name: 'crawl', description: 'Crawl registries for Claude components' },
      args: {
        ...globalArgs,
        tier: {
          type: 'string',
          description: 'Registry tier (api|scrape|awesome|all)',
          default: 'all',
        },
        output: {
          type: 'string',
          description: 'Output directory',
          default: DEFAULT_OUTPUT_DIR,
        },
        resume: {
          type: 'boolean',
          description: 'Resume from checkpoint',
          default: false,
        },
        dryRun: {
          type: 'boolean',
          description: 'Show what would be crawled',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const tier = args.tier as string
        const outputDir = args.output as string

        // Validate tier argument
        const validTiers = ['api', 'scrape', 'awesome', 'all']
        if (!validTiers.includes(tier)) {
          out.error(`Invalid tier: ${tier}. Must be one of: ${validTiers.join(', ')}`)
          process.exit(2)
        }

        // Ensure output directory exists
        if (!existsSync(outputDir)) {
          mkdirSync(outputDir, { recursive: true })
        }

        const outputFile = join(outputDir, 'components.json')
        const statePath = join(outputDir, '.crawl-state.json')

        // Load or create state
        const state = args.resume ? loadState(statePath) : loadState(statePath)

        const spin = out.spinner(`Crawling ${tier} tier...`)

        try {
          const total = await crawlTier(tier, state, outputFile, {
            dryRun: args.dryRun,
            resume: args.resume,
          })

          // Save final state
          saveState(state, statePath)

          spin.success({ text: `Crawl complete: ${total} components fetched` })

          // Show stats
          const stats = computeStats(state)
          const tableData = stats.tiers.flatMap((t) =>
            t.registries.map((r) => ({
              tier: t.name,
              registry: r.name,
              status: r.status,
              fetched: r.fetched,
            }))
          )

          if (tableData.length > 0) {
            out.table(tableData, ['tier', 'registry', 'status', 'fetched'])
          }

          if (stats.failureCount > 0) {
            out.warn(`${stats.failureCount} failures recorded`)
          }

          out.success(`Total: ${stats.totalFetched} components`)
        } catch (e) {
          // Save state even on error so progress is preserved
          saveState(state, statePath)
          spin.error({ text: 'Crawl failed' })
          out.error(e instanceof Error ? e.message : String(e))
          process.exit(2)
        }
      },
    }),

    validate: defineCommand({
      meta: { name: 'validate', description: 'Validate existing crawl output' },
      args: {
        ...globalArgs,
        output: {
          type: 'string',
          description: 'Output directory to validate',
          default: DEFAULT_OUTPUT_DIR,
        },
      },
      run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const outputDir = args.output as string
        const componentsFile = join(outputDir, 'components.json')

        if (!existsSync(componentsFile)) {
          out.error(`Components file not found: ${componentsFile}`)
          out.info('Run "ai-tools registry crawl" first')
          process.exit(2)
        }

        const result = validateNdjson(componentsFile)

        if (args.json) {
          out.raw(result)
        } else {
          out.info(`Validated: ${result.valid} valid, ${result.invalid} invalid`)
          for (const error of result.errors) {
            out.error(error)
          }
        }

        if (result.invalid > 0) {
          process.exit(1)
        }

        out.success(`${componentsFile}: all ${result.valid} records valid`)
      },
    }),

    stats: defineCommand({
      meta: { name: 'stats', description: 'Show crawl statistics' },
      args: {
        ...globalArgs,
        output: {
          type: 'string',
          description: 'Output directory containing state file',
          default: DEFAULT_OUTPUT_DIR,
        },
      },
      run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const statePath = join(args.output as string, '.crawl-state.json')

        if (!existsSync(statePath)) {
          out.error(`No crawl state found at: ${statePath}`)
          out.info('Run "ai-tools registry crawl" first')
          process.exit(2)
        }

        const state = loadState(statePath)
        const stats = computeStats(state)

        if (args.json) {
          out.raw(stats)
          return
        }

        out.info(`Started: ${stats.startedAt ?? 'unknown'}`)
        out.info(`Updated: ${stats.lastUpdated ?? 'unknown'}`)

        const tableData = stats.tiers.flatMap((t) =>
          t.registries.map((r) => ({
            tier: t.name,
            registry: r.name,
            status: r.status,
            fetched: r.fetched,
          }))
        )

        if (tableData.length > 0) {
          out.table(tableData, ['tier', 'registry', 'status', 'fetched'])
        } else {
          out.info('No crawl data yet')
        }

        out.info(`Total fetched: ${stats.totalFetched}`)
        out.info(`Failures: ${stats.failureCount}`)

        if (stats.recentFailures.length > 0) {
          out.warn('Recent failures:')
          for (const f of stats.recentFailures) {
            out.warn(`  ${f.timestamp}: ${f.url.slice(0, 60)}...`)
          }
        }
      },
    }),
  },
})
