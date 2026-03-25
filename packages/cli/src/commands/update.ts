/**
 * Verb-first command: agents update [component-type] [name] [options]
 *
 * Updates installed components to their latest versions.
 * Currently supported: skill. Other types show a "not yet supported" message.
 */
import { defineCommand } from 'citty'
import { COMPONENT_TYPES, getComponentMeta, parseComponentType } from '../lib/component/types'
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
    const parsedType = typeArg ? parseComponentType(typeArg) : undefined

    if (typeArg && !parsedType) {
      out.error(`Unknown component type: ${typeArg}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    // Default to skill if no type specified (backward compat with `agents skill update`)
    const type = parsedType ?? 'skill'

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
        return
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
      return
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
  },
})
