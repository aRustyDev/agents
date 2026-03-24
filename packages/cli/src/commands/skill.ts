/**
 * Skill management commands: validate, hash, lint, check-all, deps, and catalog (lazy).
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
// Phase 5.5 – new skill management imports
import { addSkill } from '../lib/skill-add'
import { filterArgs } from '../lib/skill-filters'
import { findSkills } from '../lib/skill-find'
import { skillInfo } from '../lib/skill-info'
import { initSkill } from '../lib/skill-init'
import { listSkills as listSkillsDetailed } from '../lib/skill-list'
import { checkOutdated } from '../lib/skill-outdated'
import { removeSkills } from '../lib/skill-remove'
import { updateSkills } from '../lib/skill-update'
import { EXIT } from '../lib/types'
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
    // catalog (lazy — canonical home is commands/catalog.ts)
    // -----------------------------------------------------------------
    catalog: () => import('./catalog').then((m) => m.default),

    // -----------------------------------------------------------------
    // add  (Phase 5.5)
    // -----------------------------------------------------------------
    add: defineCommand({
      meta: { name: 'add', description: 'Install skills from a source' },
      args: {
        ...globalArgs,
        source: {
          type: 'positional',
          description: 'Source (owner/repo, local path, or URL)',
          required: true,
        },
        copy: {
          type: 'boolean',
          description: 'Copy files instead of symlinking',
          default: false,
        },
        agent: {
          type: 'string',
          description: 'Target agent (e.g. claude-code)',
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
        const result = await addSkill(args.source as string, {
          copy: args.copy as boolean,
          agents: args.agent ? [args.agent as string] : undefined,
          yes: args.yes as boolean,
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        if (args.json) {
          out.raw(result)
          return
        }
        if (!result.ok) {
          out.error(result.error?.display() ?? 'Failed to install skill')
          process.exit(EXIT.ERROR)
        }
        for (const entry of result.installed) {
          out.success(`Installed ${entry.name} from ${entry.source}`)
        }
        for (const w of result.warnings) {
          out.warn(w)
        }
      },
    }),

    // -----------------------------------------------------------------
    // init  (Phase 5.5)
    // -----------------------------------------------------------------
    init: defineCommand({
      meta: { name: 'init', description: 'Scaffold a new skill from a template' },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Skill name (lowercase kebab-case)',
          required: true,
        },
        description: {
          type: 'string',
          alias: 'd',
          description: 'Short description for the skill',
        },
        template: {
          type: 'string',
          alias: 't',
          description: 'Path to a custom template file',
        },
        path: {
          type: 'string',
          description: 'Base directory for the new skill (default: content/skills/)',
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const result = await initSkill(args.name as string, {
          description: args.description as string | undefined,
          template: args.template as string | undefined,
          baseDir: args.path as string | undefined,
        })
        if (args.json) {
          out.raw(result)
          return
        }
        if (!result.ok) {
          out.error(result.error?.display() ?? 'Failed to scaffold skill')
          process.exit(EXIT.ERROR)
        }
        out.success(`Created skill at ${result.skillDir}`)
      },
    }),

    // -----------------------------------------------------------------
    // list  (Phase 5.5)
    // -----------------------------------------------------------------
    list: defineCommand({
      meta: { name: 'list', description: 'List installed skills with agent info' },
      args: {
        ...globalArgs,
        ...filterArgs,
        path: {
          type: 'positional',
          description: 'Skills directory to scan (default: content/skills/)',
          required: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const result = await listSkillsDetailed({
          skillsDir: args.path as string | undefined,
          agent: args.agent as string | undefined,
          skill: args.skill as string | undefined,
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        if (args.json) {
          out.raw(result)
          return
        }
        if (!result.ok) {
          out.error(result.error?.display() ?? 'Failed to list skills')
          process.exit(EXIT.ERROR)
        }
        if (result.skills.length === 0) {
          out.info('No skills found')
          return
        }
        for (const s of result.skills) {
          const agents = s.agents.length > 0 ? ` [${s.agents.join(', ')}]` : ''
          out.info(`${s.name}${agents}${s.version ? ` v${s.version}` : ''}`)
        }
      },
    }),

    // -----------------------------------------------------------------
    // find  (Phase 5.5)
    // -----------------------------------------------------------------
    find: defineCommand({
      meta: { name: 'find', description: 'Search for skills across registries' },
      args: {
        ...globalArgs,
        ...filterArgs,
        query: {
          type: 'positional',
          description: 'Search query string',
          required: false,
        },
        limit: {
          type: 'string',
          alias: 'l',
          description: 'Maximum number of results (default: 10)',
        },
        source: {
          type: 'string',
          alias: 's',
          description: 'Restrict search to a single backend (catalog, meilisearch)',
        },
      },
      async run({ args }) {
        const limit = args.limit ? Number.parseInt(args.limit as string, 10) : undefined
        await findSkills(args.query ? [args.query as string] : [], {
          limit,
          json: args.json as boolean,
          quiet: args.quiet as boolean,
          source: args.source as 'catalog' | 'meilisearch' | undefined,
          agent: args.agent as string | undefined,
        })
      },
    }),

    // -----------------------------------------------------------------
    // outdated  (Phase 5.5)
    // -----------------------------------------------------------------
    outdated: defineCommand({
      meta: { name: 'outdated', description: 'Check for skills with upstream changes' },
      args: {
        ...globalArgs,
        stdin: {
          type: 'boolean',
          description: 'Read lockfile from stdin',
          default: false,
        },
        'from-file': {
          type: 'string',
          description: 'Read lockfile from a file path',
        },
        'from-url': {
          type: 'string',
          description: 'Fetch lockfile from a URL',
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
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
        const outdated = results.filter((r) => r.status === 'outdated')
        const unavailable = results.filter((r) => r.status === 'unavailable')
        if (outdated.length === 0 && unavailable.length === 0) {
          out.success('All skills are up to date')
          return
        }
        for (const r of outdated) {
          out.warn(`${r.skill} is outdated (source: ${r.source})`)
        }
        for (const r of unavailable) {
          out.warn(`${r.skill} could not be checked: ${r.error ?? 'unknown'}`)
        }
      },
    }),

    // -----------------------------------------------------------------
    // update  (Phase 5.5)
    // -----------------------------------------------------------------
    update: defineCommand({
      meta: { name: 'update', description: 'Update outdated skills from upstream' },
      args: {
        ...globalArgs,
        skills: {
          type: 'positional',
          description: 'Skill names to update (default: all outdated)',
          required: false,
        },
        copy: {
          type: 'boolean',
          description: 'Copy files instead of symlinking',
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
        const skillNames = args.skills
          ? ((Array.isArray(args.skills) ? args.skills : [args.skills]) as string[])
          : undefined
        const results = await updateSkills({
          skills: skillNames,
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
        if (updated.length === 0 && failed.length === 0) {
          out.success('Nothing to update')
          return
        }
        for (const r of updated) {
          out.success(`Updated ${r.skill} from ${r.source}`)
        }
        for (const r of failed) {
          out.error(`Failed to update ${r.skill}: ${r.error ?? 'unknown'}`)
        }
      },
    }),

    // -----------------------------------------------------------------
    // remove  (Phase 5.5)
    // -----------------------------------------------------------------
    remove: defineCommand({
      meta: { name: 'remove', description: 'Remove installed skills' },
      args: {
        ...globalArgs,
        names: {
          type: 'positional',
          description: 'Skill names to remove',
          required: true,
        },
        agent: {
          type: 'string',
          description: 'Only remove from a specific agent',
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
        const names = Array.isArray(args.names) ? args.names : [args.names]
        const results = await removeSkills(names as string[], {
          agent: args.agent as string | undefined,
          yes: args.yes as boolean,
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        if (args.json) {
          out.raw(results)
          return
        }
        for (const r of results) {
          if (r.error) {
            out.error(`${r.skill}: ${r.error}`)
          } else {
            out.success(`Removed ${r.skill} from ${r.removedFrom.join(', ') || 'no agents'}`)
          }
        }
      },
    }),

    // -----------------------------------------------------------------
    // info  (Phase 5.5)
    // -----------------------------------------------------------------
    info: defineCommand({
      meta: { name: 'info', description: 'Show detailed metadata for an installed skill' },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Skill name',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const result = await skillInfo(args.name as string, {
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        if (args.json) {
          out.raw(result.ok ? result.value : { ok: false, error: result.error })
          return
        }
        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        const d = result.value
        out.info(`Name:           ${d.name}`)
        out.info(`Path:           ${d.path}`)
        out.info(`Source:         ${d.source ?? 'unknown'}`)
        out.info(`Source type:    ${d.sourceType ?? 'unknown'}`)
        out.info(`Hash (disk):    ${d.computedHash ?? 'n/a'}`)
        out.info(`Hash (lock):    ${d.lockHash ?? 'n/a'}`)
        out.info(`Hash match:     ${d.hashMatch ? 'yes' : 'no'}`)
        out.info(
          `Symlink:        ${d.symlinkStatus}${d.symlinkTarget ? ` -> ${d.symlinkTarget}` : ''}`
        )
        out.info(
          `Agents:         ${d.installedAgents.length > 0 ? d.installedAgents.join(', ') : 'none'}`
        )
        if (d.frontmatter) {
          if (d.frontmatter.description) out.info(`Description:    ${d.frontmatter.description}`)
          if (d.frontmatter.version) out.info(`Version:        ${d.frontmatter.version}`)
          if (d.frontmatter.tags?.length)
            out.info(`Tags:           ${d.frontmatter.tags.join(', ')}`)
        }
      },
    }),
  },
})
