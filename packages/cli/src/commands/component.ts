import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { type Component, type ComponentType, isComponentType } from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'component', description: 'Cross-type component management' },
  subCommands: {
    search: defineCommand({
      meta: { name: 'search', description: 'Search all component types across all providers' },
      args: {
        ...globalArgs,
        query: { type: 'positional', description: 'Search query', required: true },
        type: {
          type: 'string',
          alias: 't',
          description:
            'Filter by type (skill, mcp-server, agent, plugin, rule, command, output-style)',
        },
        limit: { type: 'string', description: 'Max results (default: 10)', default: '10' },
        page: { type: 'string', description: 'Page number (default: 1)', default: '1' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

        const typeFilter = args.type as string | undefined
        if (typeFilter && !isComponentType(typeFilter)) {
          out.error(
            `Invalid type: "${typeFilter}". Valid types: skill, mcp-server, agent, plugin, rule, command, output-style`
          )
          process.exit(EXIT.ERROR)
        }

        const manager = createComponentManager()
        const result = await manager.search({
          query: args.query as string,
          type: typeFilter as ComponentType | undefined,
          limit: Number.parseInt(args.limit as string, 10),
          page: Number.parseInt(args.page as string, 10),
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
          out.info('No components found')
          return
        }

        // Group by type in human output
        const grouped = new Map<string, Component[]>()
        for (const c of result.value.items) {
          if (!grouped.has(c.type)) grouped.set(c.type, [])
          grouped.get(c.type)?.push(c)
        }

        for (const [type, items] of grouped) {
          out.info(`\n${type} (${items.length}):`)
          out.table(
            items.map((c) => ({
              name: c.name,
              source: c.source,
              description: (c.description ?? '').slice(0, 50),
            })),
            ['name', 'source', 'description']
          )
        }

        if (result.value.hasMore) {
          out.info(`\nPage ${result.value.page}. Use --page ${result.value.page + 1} for more.`)
        }
      },
    }),

    list: defineCommand({
      meta: { name: 'list', description: 'List all installed components' },
      args: {
        ...globalArgs,
        type: { type: 'string', alias: 't', description: 'Filter by type' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

        const typeFilter = args.type as string | undefined
        if (typeFilter && !isComponentType(typeFilter)) {
          out.error(`Invalid type: "${typeFilter}"`)
          process.exit(EXIT.ERROR)
        }

        const manager = createComponentManager()
        const types: ComponentType[] = typeFilter
          ? [typeFilter as ComponentType]
          : ['skill', 'agent', 'plugin', 'rule', 'command', 'output-style']

        const allComponents: Component[] = []
        for (const type of types) {
          const result = await manager.list(type)
          if (result.ok) allComponents.push(...result.value)
        }

        if (args.json) {
          out.raw(allComponents)
          return
        }
        if (allComponents.length === 0) {
          out.info('No installed components found')
          return
        }

        // Group by type
        const grouped = new Map<string, Component[]>()
        for (const c of allComponents) {
          if (!grouped.has(c.type)) grouped.set(c.type, [])
          grouped.get(c.type)?.push(c)
        }

        for (const [type, items] of grouped) {
          out.info(`\n${type} (${items.length}):`)
          out.table(
            items.map((c) => ({
              name: c.name,
              source: c.source,
              description: (c.description ?? '').slice(0, 50),
            })),
            ['name', 'source', 'description']
          )
        }
      },
    }),
  },
})
