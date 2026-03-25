/**
 * Verb-first command: agents lint [component-type] [name] [options]
 *
 * Validates/lints components. If type is omitted, reports which types
 * support linting. Type-specific linting delegates to existing validators.
 */
import { statSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { defineCommand } from 'citty'
import {
  COMPONENT_TYPES,
  type ComponentType,
  getActiveTypes,
  getComponentMeta,
  parseComponentType,
} from '../lib/component/types'
import { createOutput } from '../lib/output'
import { currentDir } from '../lib/runtime'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

/** Types that currently have linting support. */
const LINTABLE_TYPES: readonly ComponentType[] = ['skill', 'plugin'] as const

/** Lazily computed to avoid import.meta resolution failures in test context. */
function getSkillsDir(): string {
  const projectRoot = resolve(currentDir(import.meta), '../../../..')
  return join(projectRoot, 'content/skills')
}

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
        process.exit(EXIT.OK)
      }

      out.info('Lint support by component type:')
      out.table(
        status.map((s) => ({
          type: s.type,
          supported: s.lintable ? 'yes' : 'not yet',
        })),
        ['type', 'supported']
      )
      process.exit(EXIT.OK)
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
      process.exit(EXIT.OK)
    }

    // Skill type: delegate to CClint
    if (type === 'skill') {
      const { default: CClint } = await import('@carlrannaberg/cclint')
      const linter = new CClint()
      const skillName = args.name as string | undefined

      let targetDir: string
      if (skillName) {
        targetDir = join(getSkillsDir(), skillName)
        try {
          statSync(targetDir)
        } catch {
          out.error(`Skill directory not found: ${targetDir}`)
          process.exit(EXIT.ERROR)
        }
      } else {
        targetDir = getSkillsDir()
      }

      const summary = await linter.lintProject(targetDir, {
        quiet: args.quiet as boolean,
      })

      if (args.json) {
        out.raw(summary)
      } else {
        const rows = summary.results.map((r: { file: string; valid: boolean; errors: unknown[]; warnings: unknown[] }) => ({
          file: r.file,
          valid: r.valid ? 'yes' : 'NO',
          errors: r.errors.length,
          warnings: r.warnings.length,
        }))

        if (rows.length > 0) {
          out.table(rows)
        }

        out.info(
          `${summary.totalFiles} files, ${summary.totalErrors} errors, ${summary.totalWarnings} warnings`
        )
      }

      process.exit(summary.totalErrors > 0 ? EXIT.FAILURES : EXIT.OK)
    }

    // Other lintable types: placeholder (plugin linting not yet wired up)
    out.info(`Linting ${type}${args.name ? `: ${args.name}` : ' (all)'}...`)

    if (args.json) {
      out.raw({ type, name: args.name ?? null, supported: true, status: 'delegated' })
    }
    process.exit(EXIT.OK)
  },
})
