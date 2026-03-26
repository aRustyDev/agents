/**
 * Verb-first command: agents add <component-type> <source> [options]
 *
 * Adds a component of the given type from the specified source.
 * Routes through ComponentManager.add() for all supported types.
 */

import { createOutput } from '@agents/core/output'
import { EXIT } from '@agents/core/types'
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { COMPONENT_TYPES, parseComponentType } from '../lib/component/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'add', description: 'Add a component (skill, mcp-server, plugin, ...)' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')})`,
      required: true,
    },
    source: {
      type: 'positional',
      description: 'Source path, URL, or registry identifier',
      required: true,
    },
    copy: {
      type: 'boolean',
      description: 'Copy files instead of symlinking',
      default: false,
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip confirmation prompts',
      default: false,
    },
    agent: {
      type: 'string',
      alias: 'a',
      description: 'Target agent name',
    },
    client: {
      type: 'string',
      alias: 'c',
      description: 'Target client (for mcp-server)',
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
    const result = await manager.add(args.source as string, type, {
      copy: args.copy as boolean,
      yes: args.yes as boolean,
      agents: args.agent ? [args.agent as string] : undefined,
      client: args.client as string | undefined,
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
      const names = result.value.components.map((c) => c.name).join(', ')
      out.success(`Added ${type}: ${names}`)
      if (result.value.installedTo.length > 0) {
        out.info(`Installed to: ${result.value.installedTo.join(', ')}`)
      }
    } else {
      out.error(result.value.error ?? 'Add failed')
      process.exit(EXIT.FAILURES)
    }

    for (const w of result.value.warnings) out.warn(w)
    process.exit(EXIT.OK)
  },
})
