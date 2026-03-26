/**
 * Plugin build and verification commands.
 *
 * Port of cli/build-plugin.py -- implements the same subcommands:
 *   build, check, hash, lint, check-all, build-all, update, update-all
 *
 * Uses the lib modules for hashing, manifest I/O, and output formatting.
 * Core logic lives in ../lib/plugin-ops.ts; this file contains only
 * the Citty command definitions.
 */

import { existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { computeHash, formatHash } from '@agents/core/hash'
import { EXIT } from '@agents/core/types'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import {
  type BuildResult,
  buildResultSuccess,
  countStatuses,
  listPlugins,
  PLUGINS_DIR,
  Plugin,
  printBuildSummary,
  printValidationResult,
  type SourceStatus,
  sourceToDict,
  type ValidationResult,
  validateMarketplace,
  validatePlugin,
} from '../lib/plugin-ops'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Re-exports for backwards compatibility (tests import from this module)
// ---------------------------------------------------------------------------

export {
  listPlugins,
  validatePlugin,
  validateMarketplace,
  printValidationResult,
  sourceToDict,
  countStatuses,
  buildResultSuccess,
  PLUGINS_DIR,
  type SourceStatus,
  type BuildResult,
  type ValidationResult,
}

// ---------------------------------------------------------------------------
// Command definitions
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'plugin', description: 'Plugin build and verification' },
  subCommands: {
    build: defineCommand({
      meta: { name: 'build', description: 'Build a plugin (copy sources, verify hashes)' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
        force: {
          type: 'boolean',
          alias: 'f',
          description: 'Force rebuild, update hashes',
          default: false,
        },
        checkOnly: {
          type: 'boolean',
          alias: 'c',
          description: 'Verify hashes only, do not copy',
          default: false,
        },
        updateHashes: {
          type: 'boolean',
          alias: 'u',
          description: 'Update hashes without prompting',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const result = await plugin.build({
          force: args.force,
          checkOnly: args.checkOnly,
          updateHashes: args.updateHashes,
        })

        if (args.json) {
          out.raw({
            plugin: result.pluginName,
            sources: result.sources.map(sourceToDict),
            copied: result.copied,
            skipped: result.skipped,
            updated: result.updated,
            errors: result.errors,
            success: buildResultSuccess(result),
          })
        } else {
          printBuildSummary(out, result)
        }

        process.exit(buildResultSuccess(result) ? EXIT.OK : EXIT.FAILURES)
      },
    }),

    check: defineCommand({
      meta: { name: 'check', description: 'Verify plugin source hashes' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const sources = await plugin.verifySources()
        const counts = countStatuses(sources)

        // JSON output mode
        if (args.json) {
          const output = {
            plugin: plugin.name,
            sources: sources.map(sourceToDict),
            summary: counts,
            ok: !(counts.stale ?? 0) && !(counts.missing ?? 0),
          }
          out.raw(output)
          process.exit(output.ok ? EXIT.OK : EXIT.FAILURES)
        }

        // Text output
        out.info(`Plugin: ${plugin.name}\n`)

        if (args.verbose) {
          for (const s of sources) {
            console.log(`  ${s.icon} ${s.localPath} (${s.status})`)
            console.log(`      Source: ${s.sourcePath}`)
            if (s.expectedHash) {
              console.log(`      Expected: ${formatHash(s.expectedHash)}`)
            }
            if (s.actualHash) {
              console.log(`      Actual:   ${formatHash(s.actualHash)}`)
            }
            if (s.forkedAt) {
              console.log(`      Forked at: ${s.forkedAt}`)
            }
          }
        } else {
          for (const s of sources) {
            console.log(`  ${s.icon} ${s.localPath} (${s.status})`)
          }
        }

        const fresh = counts.fresh ?? 0
        const stale = counts.stale ?? 0
        const forked = counts.forked ?? 0
        const noHash = counts['no-hash'] ?? 0
        const missing = counts.missing ?? 0

        console.log(
          `\nSummary: ${fresh} fresh, ${stale} stale, ` +
            `${forked} forked, ${noHash} no-hash, ${missing} missing`
        )

        if (stale || missing) {
          process.exit(EXIT.FAILURES)
        }
        if (noHash) {
          out.warn('Plugin uses legacy format without hashes')
        }
        process.exit(EXIT.OK)
      },
    }),

    hash: defineCommand({
      meta: { name: 'hash', description: 'Compute hash of a path' },
      args: {
        ...globalArgs,
        path: { type: 'positional', description: 'File or directory to hash', required: true },
        hexOnly: {
          type: 'boolean',
          description: 'Output raw hex only, no sha256: prefix',
          default: false,
        },
      },
      async run({ args }) {
        const targetPath = resolve(args.path)
        if (!existsSync(targetPath)) {
          console.error(`Error: Path not found: ${targetPath}`)
          process.exit(EXIT.FAILURES)
        }

        const hex = await computeHash(targetPath)

        if (args.json) {
          console.log(JSON.stringify({ path: targetPath, hash: formatHash(hex) }))
        } else if (args.hexOnly) {
          console.log(hex)
        } else {
          console.log(formatHash(hex))
        }
        process.exit(EXIT.OK)
      },
    }),

    lint: defineCommand({
      meta: { name: 'lint', description: 'Lint plugin Claude Code files (via cclint)' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name (omit to lint all)' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })

        let pluginNames: string[]
        if (args.name) {
          const plugin = new Plugin(args.name)
          if (!existsSync(plugin.dir)) {
            out.error(`Plugin not found: ${args.name}`)
            process.exit(EXIT.FAILURES)
          }
          pluginNames = [args.name]
        } else {
          pluginNames = listPlugins()
          if (pluginNames.length === 0) {
            out.info('No plugins found')
            process.exit(EXIT.OK)
          }
        }

        const { CClint } = await import('@carlrannaberg/cclint')
        const linter = new CClint()
        let hasErrors = false
        const allResults: Record<string, unknown>[] = []

        for (const name of pluginNames) {
          const pluginDir = join(PLUGINS_DIR, name)
          try {
            const summary = await linter.lintProject(pluginDir, { quiet: true })
            const errorCount = summary.totalErrors
            const warnCount = summary.totalWarnings

            if (args.json) {
              allResults.push({
                plugin: name,
                totalFiles: summary.totalFiles,
                errors: errorCount,
                warnings: warnCount,
                valid: errorCount === 0,
              })
            } else {
              if (errorCount > 0) {
                console.log(`  \u2717 ${name}: ${errorCount} error(s), ${warnCount} warning(s)`)
                hasErrors = true
              } else if (warnCount > 0) {
                console.log(`  \u26A0 ${name}: ${warnCount} warning(s)`)
              } else {
                console.log(`  \u2713 ${name}: OK`)
              }
            }

            if (errorCount > 0) hasErrors = true
          } catch (e) {
            if (args.json) {
              allResults.push({ plugin: name, error: String(e) })
            } else {
              console.log(`  \u2717 ${name}: lint error - ${e}`)
            }
            hasErrors = true
          }
        }

        if (args.json) {
          out.raw(allResults)
        }

        process.exit(hasErrors ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    validate: defineCommand({
      meta: { name: 'validate', description: 'Validate plugin.json manifest and referenced files' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const result = await validatePlugin(args.name)

        if (args.json) {
          out.raw(result)
        } else {
          printValidationResult(out, result)
        }

        process.exit(result.valid ? EXIT.OK : EXIT.FAILURES)
      },
    }),

    'validate-marketplace': defineCommand({
      meta: {
        name: 'validate-marketplace',
        description: 'Validate marketplace.json manifest',
      },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const result = await validateMarketplace()

        if (args.json) {
          out.raw(result)
        } else {
          printValidationResult(out, result)
        }

        process.exit(result.valid ? EXIT.OK : EXIT.FAILURES)
      },
    }),

    'validate-all': defineCommand({
      meta: { name: 'validate-all', description: 'Validate all plugin manifests' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Validating ${plugins.length} plugins...`)
        const results: ValidationResult[] = []
        const failed: string[] = []

        for (const name of plugins) {
          spinner.update({ text: `Validating ${name}...` })
          const result = await validatePlugin(name)
          results.push(result)
          if (!result.valid) failed.push(name)
        }

        spinner.success({ text: `Validated ${plugins.length} plugins` })

        if (args.json) {
          out.raw({
            plugins: results,
            summary: {
              total: plugins.length,
              ok: plugins.length - failed.length,
              failed: failed.length,
            },
            failed,
            ok: failed.length === 0,
          })
        } else {
          for (const r of results) {
            if (r.valid && r.warnings.length === 0) {
              console.log(`  \u2713 ${r.plugin}: OK`)
            } else if (r.valid) {
              console.log(`  \u26A0 ${r.plugin}: ${r.warnings.length} warning(s)`)
            } else {
              console.log(
                `  \u2717 ${r.plugin}: ${r.errors.length} error(s), ${r.warnings.length} warning(s)`
              )
            }
          }

          const okCount = plugins.length - failed.length
          const icon = failed.length ? '\u2717' : '\u2713'
          console.log(`\n${icon} ${okCount}/${plugins.length} plugins valid`)
          if (failed.length) {
            console.log(`\nFailed: ${failed.join(', ')}`)
          }
        }

        process.exit(failed.length ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    update: defineCommand({
      meta: { name: 'update', description: 'Update all hashes for a plugin' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugin = new Plugin(args.name)

        if (!plugin.exists()) {
          out.error(`Plugin not found: ${args.name}`)
          process.exit(EXIT.FAILURES)
        }

        const updated = await plugin.updateAllHashes()

        if (args.json) {
          out.raw({ plugin: args.name, updated })
        } else {
          out.info(`Updating hashes for ${args.name}...`)
          for (const localPath of updated) {
            console.log(`  \u2713 ${localPath}`)
          }
          out.success(`Updated ${updated.length} component(s)`)
        }

        process.exit(EXIT.OK)
      },
    }),

    'check-all': defineCommand({
      meta: { name: 'check-all', description: 'Verify all plugin sources' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Checking ${plugins.length} plugins...`)
        const results: Record<string, unknown>[] = []
        const failed: string[] = []

        for (const name of plugins) {
          spinner.update({ text: `Checking ${name}...` })
          const plugin = new Plugin(name)
          const sources = await plugin.verifySources()
          const counts = countStatuses(sources)

          const stale = counts.stale ?? 0
          const missing = counts.missing ?? 0
          const fresh = counts.fresh ?? 0
          const total = sources.length
          const ok = !(stale || missing)

          results.push({
            name,
            fresh,
            stale,
            missing,
            forked: counts.forked ?? 0,
            no_hash: counts['no-hash'] ?? 0,
            total,
            ok,
          })

          if (!ok) failed.push(name)
        }

        spinner.success({ text: `Checked ${plugins.length} plugins` })

        if (args.json) {
          out.raw({
            plugins: results,
            summary: {
              total: plugins.length,
              ok: plugins.length - failed.length,
              failed: failed.length,
            },
            failed,
            ok: failed.length === 0,
          })
        } else {
          for (const r of results) {
            if (r.ok) {
              console.log(`  \u2713 ${r.name}: ${r.fresh}/${r.total} fresh`)
            } else {
              console.log(
                `  \u2717 ${r.name}: ${r.fresh}/${r.total} fresh, ` +
                  `${r.stale} stale, ${r.missing} missing`
              )
            }
          }

          const okCount = plugins.length - failed.length
          const icon = failed.length ? '\u2717' : '\u2713'
          console.log(`\n${icon} ${okCount}/${plugins.length} plugins OK`)
          if (failed.length) {
            console.log(`\nFailed: ${failed.join(', ')}`)
          }
        }

        process.exit(failed.length ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    'build-all': defineCommand({
      meta: { name: 'build-all', description: 'Build all plugins' },
      args: {
        ...globalArgs,
        force: {
          type: 'boolean',
          alias: 'f',
          description: 'Force rebuild, update hashes',
          default: false,
        },
        checkOnly: {
          type: 'boolean',
          alias: 'c',
          description: 'Verify hashes only, do not copy',
          default: false,
        },
        updateHashes: {
          type: 'boolean',
          alias: 'u',
          description: 'Update hashes without prompting',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Building ${plugins.length} plugins...`)
        const failed: string[] = []
        const allResults: Record<string, unknown>[] = []

        for (const name of plugins) {
          spinner.update({ text: `Building ${name}...` })
          const plugin = new Plugin(name)
          const result = await plugin.build({
            force: args.force,
            checkOnly: args.checkOnly,
            updateHashes: args.updateHashes,
          })

          if (buildResultSuccess(result)) {
            if (!args.json) {
              console.log(
                `  \u2713 ${name}: ${result.copied.length} copied, ${result.updated.length} updated`
              )
            }
          } else {
            if (!args.json) {
              console.log(`  \u2717 ${name}: ${result.errors[0] ?? 'unknown error'}`)
            }
            failed.push(name)
          }

          if (args.json) {
            allResults.push({
              name,
              copied: result.copied.length,
              updated: result.updated.length,
              errors: result.errors,
              success: buildResultSuccess(result),
            })
          }
        }

        spinner.success({ text: `Built ${plugins.length} plugins` })

        if (args.json) {
          out.raw({
            plugins: allResults,
            summary: {
              total: plugins.length,
              ok: plugins.length - failed.length,
              failed: failed.length,
            },
            failed,
            ok: failed.length === 0,
          })
        } else {
          const okCount = plugins.length - failed.length
          const icon = failed.length ? '\u2717' : '\u2713'
          console.log(`\n${icon} ${okCount}/${plugins.length} plugins built`)
          if (failed.length) {
            console.log(`\nFailed: ${failed.join(', ')}`)
          }
        }

        process.exit(failed.length ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    'update-all': defineCommand({
      meta: { name: 'update-all', description: 'Update all plugin hashes' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({ json: args.json, quiet: args.quiet })
        const plugins = listPlugins()

        if (plugins.length === 0) {
          if (args.json) {
            out.raw({ plugins: [], ok: true })
          } else {
            out.info('No plugins found')
          }
          process.exit(EXIT.OK)
        }

        const spinner = out.spinner(`Updating ${plugins.length} plugins...`)
        const allResults: Record<string, unknown>[] = []

        for (const name of plugins) {
          spinner.update({ text: `Updating ${name}...` })
          const plugin = new Plugin(name)
          const updated = await plugin.updateAllHashes()

          if (args.json) {
            allResults.push({ name, updated: updated.length })
          } else {
            console.log(`  \u2713 ${name}: ${updated.length} hashes updated`)
          }
        }

        spinner.success({ text: `Updated ${plugins.length} plugins` })

        if (args.json) {
          out.raw({ plugins: allResults })
        } else {
          out.success(`${plugins.length} plugins updated`)
        }

        process.exit(EXIT.OK)
      },
    }),
  },
})
