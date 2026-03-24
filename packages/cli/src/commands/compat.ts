/**
 * Backward-compatibility aliases for the noun-first -> verb-first migration.
 *
 * Each helper creates a Citty subcommand that:
 *   1. Accepts the same args as the verb-first module (minus the `type` positional).
 *   2. Prints a deprecation warning to stderr.
 *   3. Delegates to the verb module's run() with `type` injected.
 *
 * Usage in skill.ts / plugin.ts:
 *
 *   import { nounAlias } from './compat'
 *   subCommands: {
 *     add:  nounAlias('skill', 'add',  { source: { type: 'positional', ... }, ... }),
 *     list: nounAlias('skill', 'list'),
 *   }
 *
 * Aliases will be removed in the next major version.
 */
import type { ArgDef, CommandDef } from 'citty'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

// -------------------------------------------------------------------------
// The core factory
// -------------------------------------------------------------------------

/**
 * Create a backward-compat alias subcommand that proxies to a verb-first module.
 *
 * @param noun      The component type that's implied (e.g. 'skill', 'plugin').
 * @param verb      The verb command name (e.g. 'add', 'list', 'remove').
 * @param extraArgs Additional args beyond globalArgs (e.g. source, copy, yes).
 *                  Do NOT include `type` -- it is injected automatically.
 */
export function nounAlias(
  noun: string,
  verb: string,
  extraArgs?: Record<string, ArgDef>
): CommandDef {
  const oldUsage = `agents ${noun} ${verb}`
  const newUsage = `agents ${verb} ${noun}`

  return defineCommand({
    meta: {
      name: verb,
      description: `[deprecated] Use "${newUsage}" instead`,
    },
    args: {
      ...globalArgs,
      ...(extraArgs ?? {}),
    },
    async run({ args }) {
      // Deprecation warning to stderr so it does not pollute JSON output
      if (!args.json && !args.quiet) {
        console.error(
          `\n  Deprecated: "${oldUsage}" will be removed in a future version.` +
          `\n  Use: "${newUsage}" instead.\n`
        )
      }

      // Dynamically import the verb module and delegate
      const mod = await import(`./${verb}`)
      const cmd = mod.default as CommandDef

      if (typeof cmd.run !== 'function') {
        console.error(`Internal error: verb module "${verb}" has no run function`)
        process.exit(1)
      }

      // Inject the noun as the `type` arg so the verb module sees it
      await cmd.run({ args: { ...args, type: noun } as typeof args })
    },
  })
}

// -------------------------------------------------------------------------
// Standalone alias: commands that route to a skill-specific lib function
// rather than a generic verb module (find, outdated)
// -------------------------------------------------------------------------

/**
 * Create a standalone deprecated command that calls a custom handler.
 * Used for commands like `skill find` and `skill outdated` that don't have
 * a direct verb-first equivalent.
 */
export function deprecatedCommand(
  oldUsage: string,
  newUsage: string,
  name: string,
  extraArgs: Record<string, ArgDef>,
  handler: (args: Record<string, unknown>) => Promise<void>
): CommandDef {
  return defineCommand({
    meta: {
      name,
      description: `[deprecated] Use "${newUsage}" instead`,
    },
    args: {
      ...globalArgs,
      ...extraArgs,
    },
    async run({ args }) {
      if (!args.json && !args.quiet) {
        console.error(
          `\n  Deprecated: "${oldUsage}" will be removed in a future version.` +
          `\n  Use: "${newUsage}" instead.\n`
        )
      }
      await handler(args as Record<string, unknown>)
    },
  })
}
