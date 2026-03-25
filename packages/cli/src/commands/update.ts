/**
 * Verb-first command: agents update [component-type] [name] [options]
 *
 * Updates installed components to their latest versions.
 * Currently supported: skill. Other types show a "not yet supported" message.
 */
import { defineCommand } from 'citty'
import { COMPONENT_TYPES, getActiveTypes, getComponentMeta, parseComponentType } from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'update', description: 'Update installed components' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')}). Omit to update all.`,
      required: false,
    },
    name: {
      type: 'positional',
      description: 'Specific component name to update',
      required: false,
    },
    copy: {
      type: 'boolean',
      description: 'Copy files instead of symlinking on update',
      default: false,
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip confirmation prompts',
      default: false,
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const typeArg = args.type as string | undefined

    if (!typeArg) {
      const activeTypes = getActiveTypes()
      out.error(`No component type specified. Use: agents update <type>`)
      out.info(`Valid types: ${activeTypes.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    const parsedType = parseComponentType(typeArg)

    if (!parsedType) {
      out.error(`Unknown component type: ${typeArg}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    const type = parsedType

    // Skill has a dedicated update implementation
    if (type === 'skill') {
      const { updateSkills } = await import('../lib/skill-update')
      const results = await updateSkills({
        skills: args.name ? [args.name as string] : undefined,
        copy: args.copy as boolean,
        yes: args.yes as boolean,
        json: args.json as boolean,
        quiet: args.quiet as boolean,
      })

      if (args.json) {
        out.raw(results)
        process.exit(EXIT.OK)
      }

      const updated = results.filter((r) => r.status === 'updated')
      const failed = results.filter((r) => r.status === 'failed')
      const current = results.filter((r) => r.status === 'current')

      if (updated.length > 0) {
        out.success(`Updated ${updated.length} skill(s): ${updated.map((r) => r.skill).join(', ')}`)
      }
      if (current.length > 0) {
        out.info(`Already current: ${current.length} skill(s)`)
      }
      if (failed.length > 0) {
        for (const f of failed) {
          out.error(`Failed to update ${f.skill}: ${f.error ?? 'unknown'}`)
        }
        process.exit(EXIT.FAILURES)
      }
      process.exit(EXIT.OK)
    }

    // Placeholder for other types
    const meta = getComponentMeta(type)
    if (meta.placeholder) {
      out.warn(`Update for ${type} is not yet implemented (placeholder type)`)
    } else {
      out.warn(`Update for ${meta.pluralName} is not yet supported. Coming soon.`)
    }

    if (args.json) {
      out.raw({ type, supported: false })
    }
    process.exit(EXIT.OK)
  },
})
