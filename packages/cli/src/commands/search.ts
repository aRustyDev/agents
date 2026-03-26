/**
 * Verb-first command: agents search <component-type> <query> [options]
 *
 * Searches for components of the given type across all providers.
 * Routes through ComponentManager.search().
 */

import { EXIT } from '@agents/core/types'
import { COMPONENT_TYPES, parseComponentType } from '@agents/sdk/context/types'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'search', description: 'Search for components across providers' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')})`,
      required: true,
    },
    query: {
      type: 'positional',
      description: 'Search query',
      required: true,
    },
    limit: {
      type: 'string',
      description: 'Max results (default: 10)',
      default: '10',
    },
    page: {
      type: 'string',
      description: 'Page number (default: 1)',
      default: '1',
    },
    verified: {
      type: 'boolean',
      description: 'Only verified components',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const type = parseComponentType(args.type as string)
    if (!type) {
      out.error(`Unknown component type: ${args.type}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    const manager = createComponentManager()
    const result = await manager.search({
      query: args.query as string,
      type,
      limit: Number.parseInt(args.limit as string, 10),
      page: Number.parseInt(args.page as string, 10),
      verified: args.verified as boolean,
    })

    if (!result.ok) {
      out.error(result.error.display())
      process.exit(EXIT.ERROR)
    }

    if (args.json) {
      out.raw(result.value)
      return
    }

    if (result.value.items.length === 0) {
      out.info(`No ${type} components found`)
      return
    }

    out.table(
      result.value.items.map((c) => ({
        name: c.name,
        source: c.source,
        description: (c.description ?? '').slice(0, 60),
        verified: c.verified ? 'yes' : '-',
      })),
      ['name', 'source', 'description', 'verified']
    )

    if (result.value.hasMore) {
      out.info(`Page ${result.value.page}. Use --page ${result.value.page + 1} for more.`)
    }
    process.exit(EXIT.OK)
  },
})
