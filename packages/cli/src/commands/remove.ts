/**
 * Verb-first command: agents remove <component-type> <name> [options]
 *
 * Removes a component of the given type by name.
 * Routes through ComponentManager.remove() for all supported types.
 */
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { COMPONENT_TYPES, parseComponentType } from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'remove', description: 'Remove a component (skill, mcp-server, plugin, ...)' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')})`,
      required: true,
    },
    name: {
      type: 'positional',
      description: 'Component name to remove',
      required: true,
    },
    agent: {
      type: 'string',
      alias: 'a',
      description: 'Agent to remove from',
    },
    // Confirmation prompts are not yet implemented in ComponentProvider.remove()
    // TODO: add --yes flag when interactive confirmation is supported
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const type = parseComponentType(args.type as string)
    if (!type) {
      out.error(`Unknown component type: ${args.type}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    const manager = createComponentManager()
    const result = await manager.remove(args.name as string, type, {
      agent: args.agent as string | undefined,
    })

    if (!result.ok) {
      out.error(result.error.display())
      process.exit(EXIT.ERROR)
    }

    if (args.json) {
      out.raw(result.value)
      return
    }

    if (result.value.ok) {
      out.success(`Removed ${type}: ${result.value.component}`)
      if (result.value.removedFrom.length > 0) {
        out.info(`Removed from: ${result.value.removedFrom.join(', ')}`)
      }
    } else {
      out.error(result.value.error ?? 'Remove failed')
      process.exit(EXIT.FAILURES)
    }
    process.exit(EXIT.OK)
  },
})
