/**
 * Verb-first command: agents init <component-type> [name]
 *
 * Scaffolds a new component of the given type.
 * Supported: skill (dedicated), persona/hook (template-based). Others: placeholder.
 */

import {
  COMPONENT_TYPES,
  type ComponentType,
  getComponentMeta,
  parseComponentType,
} from '@agents/core/component/types'
import type { OutputFormatter } from '@agents/core/output'
import { createOutput } from '@agents/core/output'
import { EXIT } from '@agents/core/types'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Helpers — extracted to reduce cognitive complexity
// ---------------------------------------------------------------------------

async function handleSkillInit(args: Record<string, unknown>, out: OutputFormatter): Promise<void> {
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
}

async function handleTemplateInit(
  type: ComponentType,
  args: Record<string, unknown>,
  out: OutputFormatter
): Promise<void> {
  const name = args.name as string | undefined
  if (!name) {
    out.error(`Name is required: agents init ${type} <name>`)
    process.exit(EXIT.ERROR)
  }
  const { initComponent } = await import('../lib/init-component')
  const result = await initComponent(type, name, { cwd: process.cwd() })
  if (!result.ok) {
    out.error(result.error.display())
    process.exit(EXIT.ERROR)
  }
  if (args.json) {
    out.raw(result.value)
    process.exit(EXIT.OK)
  }
  out.success(`Created ${type} "${name}" at ${result.value.path}`)
  for (const f of result.value.files) out.info(`  ${f}`)
  process.exit(EXIT.OK)
}

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

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
      await handleSkillInit(args, out)
      return
    }

    // Generic template-based init for types that have a templateDir
    const meta = getComponentMeta(type)
    if (meta.templateDir) {
      await handleTemplateInit(type, args, out)
      return
    }

    // Placeholder for types without templates
    if (meta.placeholder) {
      out.warn(`Init for ${type} is not yet implemented (placeholder type)`)
    } else {
      out.warn(`Init for ${type} is not yet supported. Coming soon.`)
    }

    if (args.json) {
      out.raw({ type, supported: false })
    }
    process.exit(EXIT.OK)
  },
})
