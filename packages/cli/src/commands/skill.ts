/**
 * Skill foundation commands: validate, hash, lint, check-all, deps, and catalog (lazy).
 *
 * Verb-first commands (add, remove, list, search, info, init, lint, update)
 * have been extracted to individual modules under commands/.
 */

import { readdirSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { defineCommand } from 'citty'
import {
  checkDrift,
  createDriftIssues,
  getStatus,
  refreshLinks,
  syncAll,
} from '../lib/external-skills'
import { formatHash, hashDirectory } from '../lib/hash'
import { readSkillFrontmatter } from '../lib/manifest'
import { createOutput } from '../lib/output'
import { currentDir } from '../lib/runtime'
import { EXIT } from '../lib/types'
import { deprecatedCommand, nounAlias } from './compat'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')
const SKILLS_DIR = join(PROJECT_ROOT, 'content/skills')
const EXTERNAL_DIR = join(SKILLS_DIR, '.external')

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * List all valid skill directory names under content/skills/.
 * Skips dotdirs, .templates, and non-directories (e.g., justfile).
 */
export function listSkills(): string[] {
  return readdirSync(SKILLS_DIR)
    .filter((name) => !name.startsWith('.') && name !== '.templates' && name !== 'justfile')
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
            `${summary.totalFiles} files, ${summary.totalErrors} errors, ${summary.totalWarnings} warnings`
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
                Status:
                  r.status === 'changed'
                    ? 'CHANGED'
                    : r.status === 'unavail'
                      ? 'UNAVAIL'
                      : r.status,
                'Last Synced': r.lastSynced?.slice(0, 10) ?? '\u2014',
              }))
              out.table(rows)
            }

            const hasProblems = results.some(
              (r) => r.status === 'changed' || r.status === 'unavail'
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
              default: 'aRustyDev/agents',
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const repoArg = (args.repo as string) || 'aRustyDev/agents'
            const dryRun = args['dry-run'] as boolean

            const spinner = out.spinner(
              dryRun ? 'Checking drift issues (dry run)...' : 'Creating drift issues...'
            )
            const { created, updated } = await createDriftIssues(
              EXTERNAL_DIR,
              SKILLS_DIR,
              repoArg,
              { dryRun }
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
                `${result.created.length} created, ${result.updated.length} updated, ${result.skipped.length} skipped, ${result.broken.length} broken`
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

    // -----------------------------------------------------------------
    // Backward-compat aliases (noun-first → verb-first migration)
    // These proxy to the verb-first modules with a deprecation warning.
    // Remove in the next major version.
    // -----------------------------------------------------------------
    add: nounAlias('skill', 'add', {
      source: { type: 'positional', description: 'Source path, URL, or registry id', required: true },
      copy: { type: 'boolean', description: 'Copy files instead of symlinking', default: false },
      yes: { type: 'boolean', alias: 'y', description: 'Skip prompts', default: false },
      agent: { type: 'string', alias: 'a', description: 'Target agent' },
      client: { type: 'string', alias: 'c', description: 'Target client' },
    }),
    init: nounAlias('skill', 'init', {
      name: { type: 'positional', description: 'Skill name (kebab-case)', required: false },
      description: { type: 'string', alias: 'd', description: 'Short description' },
      template: { type: 'string', alias: 't', description: 'Template file path' },
    }),
    list: nounAlias('skill', 'list', {
      agent: { type: 'string', alias: 'a', description: 'Filter by agent' },
    }),
    search: nounAlias('skill', 'search', {
      query: { type: 'positional', description: 'Search query', required: true },
      limit: { type: 'string', description: 'Max results (default: 10)', default: '10' },
      page: { type: 'string', description: 'Page number (default: 1)', default: '1' },
      verified: { type: 'boolean', description: 'Only verified', default: false },
    }),
    info: nounAlias('skill', 'info', {
      name: { type: 'positional', description: 'Skill name', required: true },
    }),
    update: nounAlias('skill', 'update', {
      name: { type: 'positional', description: 'Skill name', required: false },
      copy: { type: 'boolean', description: 'Copy files on update', default: false },
      yes: { type: 'boolean', alias: 'y', description: 'Skip prompts', default: false },
    }),
    remove: nounAlias('skill', 'remove', {
      name: { type: 'positional', description: 'Skill name', required: true },
      agent: { type: 'string', alias: 'a', description: 'Agent to remove from' },
      yes: { type: 'boolean', alias: 'y', description: 'Skip prompts', default: false },
    }),
    find: deprecatedCommand(
      'agents skill find', 'agents search skill', 'find',
      {
        query: { type: 'positional', description: 'Search query' },
        limit: { type: 'string', description: 'Max results', default: '10' },
        source: { type: 'string', description: 'Backend: auto, skills-sh, meilisearch, catalog' },
        agent: { type: 'string', description: 'Target agent' },
        yes: { type: 'boolean', alias: 'y', description: 'Skip prompts', default: false },
      },
      async (args) => {
        const { findSkills } = await import('../lib/skill-find')
        await findSkills(
          args.query ? [args.query as string] : [],
          {
            limit: args.limit ? Number.parseInt(args.limit as string, 10) : undefined,
            json: args.json as boolean,
            quiet: args.quiet as boolean,
            source: args.source as 'auto' | 'skills-sh' | 'meilisearch' | 'catalog' | undefined,
            agent: args.agent as string | undefined,
            yes: args.yes as boolean,
          },
        )
      },
    ),
    outdated: deprecatedCommand(
      'agents skill outdated', 'agents update skill --check', 'outdated',
      {
        stdin: { type: 'boolean', description: 'Read lockfile from stdin', default: false },
        'from-file': { type: 'string', description: 'Lockfile path' },
        'from-url': { type: 'string', description: 'Lockfile URL' },
      },
      async (args) => {
        const { checkOutdated } = await import('../lib/skill-outdated')
        const out = (await import('../lib/output')).createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        const results = await checkOutdated({
          stdin: args.stdin as boolean,
          fromFile: args['from-file'] as string | undefined,
          fromUrl: args['from-url'] as string | undefined,
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        if (args.json) {
          out.raw(results)
          return
        }

        if (results.length === 0) {
          out.info('No skills in lockfile')
          return
        }

        out.table(
          results.map((r) => ({
            skill: r.skill,
            source: r.source,
            status: r.status,
            error: r.error ?? '',
          })),
          ['skill', 'source', 'status', 'error'],
        )

        const outdated = results.filter((r) => r.status === 'outdated')
        if (outdated.length > 0) {
          out.warn(`${outdated.length} skill(s) outdated`)
          process.exit(1)
        }
      },
    ),

    // -----------------------------------------------------------------
    // catalog (lazy — canonical home is commands/catalog.ts)
    // -----------------------------------------------------------------
    catalog: () => import('./catalog').then((m) => m.default),
  },
})
