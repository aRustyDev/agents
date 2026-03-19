/**
 * Skill management commands: validate, hash, lint, check-all, and deps (stub).
 */

import { defineCommand } from 'citty'
import { readdirSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { globalArgs } from './shared-args'
import { createOutput } from '../lib/output'
import { readSkillFrontmatter } from '../lib/manifest'
import { hashDirectory, formatHash } from '../lib/hash'
import { EXIT } from '../lib/types'
import {
  checkDrift,
  syncAll,
  createDriftIssues,
  refreshLinks,
  getStatus,
} from '../lib/external-skills'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PROJECT_ROOT = resolve(import.meta.dir, '../..')
const SKILLS_DIR = join(PROJECT_ROOT, 'context/skills')
const EXTERNAL_DIR = join(SKILLS_DIR, '.external')

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * List all valid skill directory names under context/skills/.
 * Skips dotdirs, .templates, and non-directories (e.g., justfile).
 */
export function listSkills(): string[] {
  return readdirSync(SKILLS_DIR)
    .filter(
      (name) =>
        !name.startsWith('.') && name !== '.templates' && name !== 'justfile',
    )
    .filter((name) => {
      try {
        return statSync(join(SKILLS_DIR, name)).isDirectory()
      } catch {
        return false
      }
    })
    .sort()
}

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: {
    name: 'skill',
    description: 'Skill validation, hashing, and dependency management',
  },
  subCommands: {
    // -----------------------------------------------------------------
    // validate
    // -----------------------------------------------------------------
    validate: defineCommand({
      meta: {
        name: 'validate',
        description: 'Validate SKILL.md frontmatter and structure',
      },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Skill name',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        const skillName = args.name as string
        const skillPath = join(SKILLS_DIR, skillName, 'SKILL.md')

        const result = await readSkillFrontmatter(skillPath)

        if (!result.ok) {
          out.error(`${skillName}: ${result.error.message}`)
          if (result.error.hint) {
            out.error(`  hint: ${result.error.hint}`)
          }
          process.exit(EXIT.FAILURES)
        }

        out.success(`${skillName}: SKILL.md valid`, {
          name: result.value.name,
          description: result.value.description,
          version: result.value.version,
        })
        process.exit(EXIT.OK)
      },
    }),

    // -----------------------------------------------------------------
    // hash
    // -----------------------------------------------------------------
    hash: defineCommand({
      meta: { name: 'hash', description: 'Compute skill directory hash' },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Skill name',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        const skillName = args.name as string
        const skillDir = join(SKILLS_DIR, skillName)

        try {
          statSync(skillDir)
        } catch {
          out.error(`Skill directory not found: ${skillDir}`)
          process.exit(EXIT.ERROR)
        }

        const hex = await hashDirectory(skillDir)
        const prefixed = formatHash(hex)

        if (args.json) {
          out.raw({ skill: skillName, hash: prefixed })
        } else {
          console.log(prefixed)
        }
        process.exit(EXIT.OK)
      },
    }),

    // -----------------------------------------------------------------
    // lint
    // -----------------------------------------------------------------
    lint: defineCommand({
      meta: { name: 'lint', description: 'Lint skill files (via cclint)' },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Skill name (omit to lint all skills)',
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const { default: CClint } = await import('@carlrannaberg/cclint')
        const linter = new CClint()
        const skillName = args.name as string | undefined

        let targetDir: string
        if (skillName) {
          targetDir = join(SKILLS_DIR, skillName)
          try {
            statSync(targetDir)
          } catch {
            out.error(`Skill directory not found: ${targetDir}`)
            process.exit(EXIT.ERROR)
          }
        } else {
          targetDir = SKILLS_DIR
        }

        const summary = await linter.lintProject(targetDir, {
          quiet: args.quiet as boolean,
        })

        if (args.json) {
          out.raw(summary)
        } else {
          const rows = summary.results.map((r) => ({
            file: r.file,
            valid: r.valid ? 'yes' : 'NO',
            errors: r.errors.length,
            warnings: r.warnings.length,
          }))

          if (rows.length > 0) {
            out.table(rows)
          }

          out.info(
            `${summary.totalFiles} files, ${summary.totalErrors} errors, ${summary.totalWarnings} warnings`,
          )
        }

        process.exit(summary.totalErrors > 0 ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    // -----------------------------------------------------------------
    // check-all
    // -----------------------------------------------------------------
    'check-all': defineCommand({
      meta: { name: 'check-all', description: 'Validate all skills' },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const skills = listSkills()
        const spinner = out.spinner(`Validating ${skills.length} skills...`)

        const results: {
          name: string
          valid: boolean
          error?: string
        }[] = []

        for (const skill of skills) {
          spinner.update({ text: `Validating ${skill}...` })
          const skillPath = join(SKILLS_DIR, skill, 'SKILL.md')
          const result = await readSkillFrontmatter(skillPath)

          if (result.ok) {
            results.push({ name: skill, valid: true })
          } else {
            results.push({
              name: skill,
              valid: false,
              error: result.error.message,
            })
          }
        }

        const passed = results.filter((r) => r.valid).length
        const failed = results.filter((r) => !r.valid).length

        if (failed > 0) {
          spinner.error({
            text: `${passed} valid, ${failed} failed out of ${skills.length} skills`,
          })
        } else {
          spinner.success({
            text: `All ${passed} skills valid`,
          })
        }

        if (args.json) {
          out.raw({ total: skills.length, passed, failed, results })
        } else {
          const rows = results.map((r) => ({
            skill: r.name,
            status: r.valid ? 'valid' : 'INVALID',
            ...(r.error ? { error: r.error } : {}),
          }))
          out.table(rows)
        }

        process.exit(failed > 0 ? EXIT.FAILURES : EXIT.OK)
      },
    }),

    // -----------------------------------------------------------------
    // deps
    // -----------------------------------------------------------------
    deps: defineCommand({
      meta: {
        name: 'deps',
        description: 'Manage external skill dependencies',
      },
      subCommands: {
        check: defineCommand({
          meta: {
            name: 'check',
            description: 'Check upstream drift and symlink health',
          },
          args: { ...globalArgs },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const results = await checkDrift(EXTERNAL_DIR, SKILLS_DIR)

            if (results.length === 0) {
              out.info('No external skills configured')
              process.exit(EXIT.OK)
            }

            if (args.json) {
              out.raw(results)
            } else {
              const rows = results.map((r) => ({
                Skill: r.skill,
                Source: r.source,
                Status: r.status === 'changed' ? 'CHANGED' : r.status === 'unavail' ? 'UNAVAIL' : r.status,
                'Last Synced': r.lastSynced?.slice(0, 10) ?? '\u2014',
              }))
              out.table(rows)
            }

            const hasProblems = results.some(
              (r) => r.status === 'changed' || r.status === 'unavail',
            )
            process.exit(hasProblems ? EXIT.FAILURES : EXIT.OK)
          },
        }),
        sync: defineCommand({
          meta: {
            name: 'sync',
            description: 'Sync external dependencies, update lockfile',
          },
          args: {
            ...globalArgs,
            force: {
              type: 'boolean',
              description: 'Force sync all (even current)',
              default: false,
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const spinner = out.spinner('Syncing external skills...')
            const { synced, failed } = await syncAll(EXTERNAL_DIR, SKILLS_DIR, {
              force: args.force as boolean,
            })
            const total = synced.length + failed.length

            if (failed.length > 0) {
              spinner.error({
                text: `Synced ${synced.length}/${total}, ${failed.length} failed`,
              })
            } else if (synced.length > 0) {
              spinner.success({
                text: `Synced ${synced.length} skill(s)`,
              })
            } else {
              spinner.success({ text: 'All skills up to date' })
            }

            if (args.json) {
              out.raw({ synced, failed })
            } else {
              if (synced.length > 0) {
                out.info(`Synced: ${synced.join(', ')}`)
              }
              if (failed.length > 0) {
                out.error(`Failed: ${failed.join(', ')}`)
              }
            }

            process.exit(failed.length > 0 ? EXIT.FAILURES : EXIT.OK)
          },
        }),
        issues: defineCommand({
          meta: {
            name: 'issues',
            description: 'Open GH issues for upstream drift',
          },
          args: {
            ...globalArgs,
            'dry-run': {
              type: 'boolean',
              description: 'Preview without creating',
              default: false,
            },
            repo: {
              type: 'string',
              description: 'GitHub repo (owner/repo)',
              default: 'aRustyDev/ai',
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const repoArg = (args.repo as string) || 'aRustyDev/ai'
            const dryRun = args['dry-run'] as boolean

            const spinner = out.spinner(
              dryRun ? 'Checking drift issues (dry run)...' : 'Creating drift issues...',
            )
            const { created, updated } = await createDriftIssues(
              EXTERNAL_DIR,
              SKILLS_DIR,
              repoArg,
              { dryRun },
            )

            spinner.success({
              text: `Issues: ${created} created, ${updated} updated`,
            })

            if (args.json) {
              out.raw({ created, updated, dryRun })
            }

            process.exit(EXIT.OK)
          },
        }),
        links: defineCommand({
          meta: {
            name: 'links',
            description: 'Create/refresh passthrough symlinks',
          },
          args: { ...globalArgs },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const result = await refreshLinks(EXTERNAL_DIR, SKILLS_DIR)

            if (args.json) {
              out.raw(result)
            } else {
              const rows: Record<string, unknown>[] = []
              for (const name of result.created) {
                rows.push({ Skill: name, Action: 'created' })
              }
              for (const name of result.updated) {
                rows.push({ Skill: name, Action: 'updated' })
              }
              for (const name of result.broken) {
                rows.push({ Skill: name, Action: 'BROKEN (sync needed)' })
              }

              if (rows.length > 0) {
                out.table(rows)
              }

              out.info(
                `${result.created.length} created, ${result.updated.length} updated, ${result.skipped.length} skipped, ${result.broken.length} broken`,
              )
            }

            process.exit(result.broken.length > 0 ? EXIT.FAILURES : EXIT.OK)
          },
        }),
        status: defineCommand({
          meta: {
            name: 'status',
            description: 'Show combined dependency status',
          },
          args: { ...globalArgs },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const results = await getStatus(EXTERNAL_DIR, SKILLS_DIR)

            if (results.length === 0) {
              out.info('No external skills configured')
              process.exit(EXIT.OK)
            }

            if (args.json) {
              out.raw(results)
            } else {
              const rows = results.map((r) => ({
                Skill: r.skill,
                Source: r.source,
                Mode: r.mode,
                Hash: r.hash ?? '\u2014',
                Symlink: r.symlink,
                Issue: r.issue,
              }))
              out.table(rows)
            }

            process.exit(EXIT.OK)
          },
        }),
      },
    }),
  },
})
