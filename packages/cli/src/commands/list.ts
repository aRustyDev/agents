/**
 * Verb-first command: agents list [component-type] [options]
 *
 * Lists installed components. If type is omitted, lists ALL active types.
 * Routes through ComponentManager.list() per type.
 */
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import {
  type Component,
  COMPONENT_TYPES,
  type ComponentType,
  getActiveTypes,
  parseComponentType,
} from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'list', description: 'List installed components' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')}). Omit to list all.`,
      required: false,
    },
    agent: {
      type: 'string',
      alias: 'a',
      description: 'Filter by agent name',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const typeArg = args.type as string | undefined
    const parsedType = typeArg ? parseComponentType(typeArg) : undefined
    if (typeArg && !parsedType) {
      out.error(`Unknown component type: ${typeArg}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    const manager = createComponentManager()
    const types: ComponentType[] = parsedType ? [parsedType] : getActiveTypes()

    const allComponents: Component[] = []
    for (const type of types) {
      const result = await manager.list(type, { agent: args.agent as string | undefined })
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

    // Group by type for human-readable output
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
    process.exit(EXIT.OK)
  },
})
