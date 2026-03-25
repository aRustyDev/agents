/**
 * Verb-first command: agents info <component-type> <name>
 *
 * Shows detailed information about a single component.
 * Routes through ComponentManager.info().
 */
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { COMPONENT_TYPES, parseComponentType } from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'info', description: 'Show details for a component' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')})`,
      required: true,
    },
    name: {
      type: 'positional',
      description: 'Component name',
      required: true,
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
    const result = await manager.info(args.name as string, type)

    if (!result.ok) {
      out.error(result.error.display())
      process.exit(EXIT.ERROR)
    }

    if (args.json) {
      out.raw(result.value)
      return
    }

    const c = result.value
    out.info(`Name: ${c.name}`)
    out.info(`Type: ${c.type}`)
    out.info(`Source: ${c.source}`)
    if (c.description) out.info(`Description: ${c.description}`)
    if (c.version) out.info(`Version: ${c.version}`)
    if (c.author) out.info(`Author: ${c.author}`)
    if (c.url) out.info(`URL: ${c.url}`)
    if (c.tags && c.tags.length > 0) out.info(`Tags: ${c.tags.join(', ')}`)
    if (c.installs !== undefined) out.info(`Installs: ${c.installs}`)
    if (c.stars !== undefined) out.info(`Stars: ${c.stars}`)
    if (c.verified) out.info('Verified: yes')
    if (c.namespace) out.info(`Namespace: ${c.namespace}`)
    if (c.installedAt) out.info(`Installed: ${c.installedAt}`)
    if (c.installMode) out.info(`Install mode: ${c.installMode}`)
    if (c.localPath) out.info(`Local path: ${c.localPath}`)
  },
})
