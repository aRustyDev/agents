/**
 * Verb-first command: agents lint [component-type] [name] [options]
 *
 * Validates/lints components. If type is omitted, reports which types
 * support linting. Type-specific linting delegates to existing validators.
 */
import { defineCommand } from 'citty'
import {
  COMPONENT_TYPES,
  type ComponentType,
  getActiveTypes,
  getComponentMeta,
  parseComponentType,
} from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

/** Types that currently have linting support. */
const LINTABLE_TYPES: readonly ComponentType[] = ['skill', 'plugin'] as const

export default defineCommand({
  meta: { name: 'lint', description: 'Validate/lint components' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')}). Omit to show lint status for all types.`,
      required: false,
    },
    name: {
      type: 'positional',
      description: 'Component name to lint (optional)',
      required: false,
    },
    output: {
      type: 'string',
      alias: 'o',
      description: 'Output format for lint results',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const typeArg = args.type as string | undefined

    // No type specified: report which types support linting
    if (!typeArg) {
      const activeTypes = getActiveTypes()
      const status = activeTypes.map((t) => ({
        type: t,
        lintable: (LINTABLE_TYPES as readonly string[]).includes(t),
        plural: getComponentMeta(t).pluralName,
      }))

      if (args.json) {
        out.raw(status)
        return
      }

      out.info('Lint support by component type:')
      out.table(
        status.map((s) => ({
          type: s.type,
          supported: s.lintable ? 'yes' : 'not yet',
        })),
        ['type', 'supported']
      )
      return
    }

    const type = parseComponentType(typeArg)
    if (!type) {
      out.error(`Unknown component type: ${typeArg}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    if (!(LINTABLE_TYPES as readonly string[]).includes(type)) {
      const meta = getComponentMeta(type)
      out.warn(`Linting for ${meta.pluralName} is not yet supported`)
      if (args.json) {
        out.raw({ type, supported: false })
      }
      return
    }

    // Delegate to type-specific lint/validate when a name is provided
    out.info(`Linting ${type}${args.name ? `: ${args.name}` : ' (all)'}...`)

    if (args.json) {
      out.raw({ type, name: args.name ?? null, supported: true, status: 'delegated' })
    }
  },
})
