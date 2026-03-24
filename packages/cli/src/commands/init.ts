/**
 * Verb-first command: agents init <component-type> [name]
 *
 * Scaffolds a new component of the given type.
 * Currently supported: skill. Other types show a "not yet supported" message.
 */
import { defineCommand } from 'citty'
import { COMPONENT_TYPES, getComponentMeta, parseComponentType } from '../lib/component/types'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'init', description: 'Scaffold a new component' },
  args: {
    ...globalArgs,
    type: {
      type: 'positional',
      description: `Component type (${COMPONENT_TYPES.join(', ')})`,
      required: true,
    },
    name: {
      type: 'positional',
      description: 'Component name (kebab-case)',
      required: false,
    },
    description: {
      type: 'string',
      alias: 'd',
      description: 'Short description',
    },
    template: {
      type: 'string',
      alias: 't',
      description: 'Template file path',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

    const type = parseComponentType(args.type as string)
    if (!type) {
      out.error(`Unknown component type: ${args.type}. Valid types: ${COMPONENT_TYPES.join(', ')}`)
      process.exit(EXIT.ERROR)
    }

    // Skill has a dedicated init implementation
    if (type === 'skill') {
      const skillName = args.name as string | undefined
      if (!skillName) {
        out.error('Skill name is required: agents init skill <name>')
        process.exit(EXIT.ERROR)
      }

      const { initSkill } = await import('../lib/skill-init')
      const result = await initSkill(skillName, {
        description: args.description as string | undefined,
        template: args.template as string | undefined,
      })

      if (args.json) {
        out.raw(result)
        return
      }

      if (result.ok) {
        out.success(`Created skill: ${result.skillPath}`)
      } else {
        out.error(result.error?.display() ?? 'Init failed')
        process.exit(EXIT.FAILURES)
      }
      return
    }

    // Placeholder for other types
    const meta = getComponentMeta(type)
    if (meta.placeholder) {
      out.warn(`Init for ${type} is not yet implemented (placeholder type)`)
    } else {
      out.warn(`Init for ${type} is not yet supported. Coming soon.`)
    }

    if (args.json) {
      out.raw({ type, supported: false })
    }
  },
})
