/**
 * Skill management commands: validate, hash, lint, check-all, and deps (stub).
 */

import { readdirSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { defineCommand } from 'citty'
import {
  createBatches,
  detectForks,
  filterAvailable,
  formatBatchPrompt,
  mergeTier1Results,
  parseTier1Output,
  readCatalog,
} from '../lib/catalog'
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
import { uuid7 } from '../lib/uuid'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PROJECT_ROOT = resolve(currentDir(import.meta), '../..')
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
    // catalog
    // -----------------------------------------------------------------
    catalog: defineCommand({
      meta: {
        name: 'catalog',
        description: 'Skill catalog inspection pipeline operations',
      },
      subCommands: {
        analyze: defineCommand({
          meta: {
            name: 'analyze',
            description: 'Dispatch Tier 1 analysis agents on available skills',
          },
          args: {
            ...globalArgs,
            'batch-size': {
              type: 'string',
              description: 'Skills per agent batch (default: 15)',
              default: '15',
            },
            limit: {
              type: 'string',
              description: 'Max batches to process (default: all)',
            },
            concurrency: {
              type: 'string',
              description: 'Parallel agent dispatches (default: 3)',
              default: '3',
            },
            'dry-run': {
              type: 'boolean',
              description: 'Show batches without dispatching agents',
              default: false,
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const catalogPath = join(PROJECT_ROOT, 'context/skills/.catalog.ndjson')

            if (!require('node:fs').existsSync(catalogPath)) {
              out.error(
                'Catalog not found. Run availability check first: bun run .scripts/lib/catalog.ts'
              )
              process.exit(EXIT.ERROR)
            }

            const allEntries = readCatalog(catalogPath)
            const available = filterAvailable(allEntries)
            const batchSize = parseInt(args['batch-size'] as string, 10) || 15
            const batches = createBatches(available, batchSize)
            const limit = args.limit ? parseInt(args.limit as string, 10) : batches.length

            out.info(`Catalog: ${allEntries.length} total, ${available.length} available`)
            out.info(`Batches: ${batches.length} (size ${batchSize}), processing ${limit}`)

            if (args['dry-run']) {
              out.info('\n[DRY RUN] First 3 batches:')
              for (let i = 0; i < Math.min(3, limit); i++) {
                const prompt = formatBatchPrompt(batches[i])
                const lines = prompt.split('\n')
                out.info(`\nBatch ${i + 1} (${lines.length} skills):`)
                for (const line of lines.slice(0, 5)) {
                  out.info(`  ${line}`)
                }
                if (lines.length > 5) {
                  out.info(`  ... and ${lines.length - 5} more`)
                }
              }
              process.exit(EXIT.OK)
            }

            // Dispatch agents in isolated git worktrees with pre-downloaded skills
            // All I/O is async to enable true concurrent execution
            const { exec: execCb, spawn: spawnCb } = require('node:child_process')
            const {
              existsSync: fsExists,
              rmSync,
              mkdirSync,
              writeFileSync: fsWriteSync,
            } = require('node:fs')
            const { promisify } = require('node:util')
            const execAsync = promisify(execCb)

            const WORKTREE_BASE = '/tmp/worktrees'
            const concurrency = parseInt(args.concurrency as string, 10) || 3

            // Generate run-level UUID7 (timestamp-sortable, unique per invocation)
            const runId = uuid7()
            out.info(`Concurrency: ${concurrency} parallel agents`)
            out.info(`Run ID: ${runId}`)

            /** Create a git worktree for a batch (async), returns worktree path */
            async function createWorktree(batchId: number): Promise<string> {
              const wtPath = join(WORKTREE_BASE, `skill-inspect-${batchId}`)
              if (fsExists(wtPath)) {
                try {
                  await execAsync(`git worktree unlock ${JSON.stringify(wtPath)}`, {
                    cwd: PROJECT_ROOT,
                  })
                } catch {
                  /* ignore */
                }
                try {
                  await execAsync(`git worktree remove --force ${JSON.stringify(wtPath)}`, {
                    cwd: PROJECT_ROOT,
                  })
                } catch {
                  /* ignore */
                }
                try {
                  rmSync(wtPath, { recursive: true, force: true })
                } catch {
                  /* ignore */
                }
              }
              await execAsync(`git worktree add --detach ${JSON.stringify(wtPath)} HEAD`, {
                cwd: PROJECT_ROOT,
              })
              return wtPath
            }

            /** Remove a git worktree (async) */
            async function removeWorktree(wtPath: string): Promise<void> {
              try {
                await execAsync(`git worktree unlock ${JSON.stringify(wtPath)}`, {
                  cwd: PROJECT_ROOT,
                })
              } catch {
                /* ignore */
              }
              try {
                await execAsync(`git worktree remove --force ${JSON.stringify(wtPath)}`, {
                  cwd: PROJECT_ROOT,
                })
              } catch {
                /* ignore */
              }
              try {
                rmSync(wtPath, { recursive: true, force: true })
              } catch {
                /* ignore */
              }
            }

            interface DownloadResult {
              path: string | null
              error?: string
              errorType?: 'download_failed' | 'download_timeout'
              errorDetail?: string
              errorCode?: number
            }

            /**
             * Pre-download SKILL.md files for a batch (async).
             * Downloads are sequential within a batch (same worktree) but
             * batches run concurrently in separate worktrees.
             * Returns per-skill download results with detailed error info.
             */
            async function preDownloadSkills(
              batch: import('../lib/catalog').CatalogEntry[],
              wtPath: string
            ): Promise<Map<string, DownloadResult>> {
              const results = new Map<string, DownloadResult>()
              const skillsDir = join(wtPath, '.claude', 'skills')

              for (const entry of batch) {
                const ref = `${entry.source}@${entry.skill}`
                try {
                  await execAsync(`npx -y skills add -y --copy --full-depth ${ref}`, {
                    cwd: wtPath,
                    encoding: 'utf8',
                    timeout: 30_000,
                  })
                  const skillDir = join(skillsDir, entry.skill)
                  const skillMd = join(skillDir, 'SKILL.md')
                  if (fsExists(skillMd)) {
                    results.set(entry.skill, { path: skillMd })
                  } else {
                    try {
                      const { stdout: files } = await execAsync(
                        `find ${JSON.stringify(skillDir)} -name '*.md' -type f`,
                        { encoding: 'utf8' }
                      )
                      const trimmed = (files as string).trim()
                      results.set(entry.skill, {
                        path: trimmed ? trimmed.split('\n')[0] : null,
                        ...(trimmed
                          ? {}
                          : {
                              error: 'no SKILL.md found in downloaded files',
                              errorType: 'download_failed' as const,
                            }),
                      })
                    } catch {
                      results.set(entry.skill, {
                        path: null,
                        error: 'skill directory not found after download',
                        errorType: 'download_failed',
                      })
                    }
                  }
                } catch (err: unknown) {
                  const isTimeout =
                    err instanceof Error &&
                    (err.message.includes('TIMEOUT') ||
                      err.message.includes('timed out') ||
                      err.message.includes('killed'))
                  const stderr = (err as { stderr?: string })?.stderr ?? ''
                  const exitCode = (err as { code?: number })?.code
                  results.set(entry.skill, {
                    path: null,
                    error: isTimeout
                      ? 'download timed out (30s)'
                      : `download failed: ${stderr.slice(0, 300) || (err instanceof Error ? err.message.slice(0, 300) : 'unknown')}`,
                    errorType: isTimeout ? 'download_timeout' : 'download_failed',
                    errorDetail: stderr.slice(0, 500) || undefined,
                    errorCode: exitCode,
                  })
                }
              }
              return results
            }

            // Ensure worktree base dir exists
            mkdirSync(WORKTREE_BASE, { recursive: true })

            const ALLOWED_TOOLS =
              'Bash(mdq:*,wc:*,find:*,stat:*,sha256sum:*,shasum:*) Read Glob Grep'

            let totalProcessed = 0
            let totalErrors = 0
            const allResults: import('../lib/catalog').Tier1Result[] = []

            /**
             * Process a single batch: create worktree, download, analyze, cleanup.
             * Returns the Tier1Results for this batch with detailed error info.
             */
            async function processBatch(
              batch: import('../lib/catalog').CatalogEntry[],
              batchNum: number,
              totalBatches: number
            ): Promise<import('../lib/catalog').Tier1Result[]> {
              const batchId = uuid7()
              const analyzedAt = new Date().toISOString()
              let wtPath: string | null = null

              /** Stamp run/batch/time metadata onto all results */
              function stamp(results: import('../lib/catalog').Tier1Result[]) {
                for (const r of results) {
                  r.runId = runId
                  r.batchId = batchId
                  r.analyzedAt = analyzedAt
                }
                return results
              }

              try {
                // Phase 1: Create worktree and pre-download skills (async)
                wtPath = await createWorktree(batchNum)
                out.info(
                  `[${batchNum}/${totalBatches}] Worktree ready, downloading ${batch.length} skills...`
                )

                const downloaded = await preDownloadSkills(batch, wtPath)
                const successCount = [...downloaded.values()].filter((r) => r.path).length
                const failCount = batch.length - successCount

                // Collect per-skill download error results immediately
                const downloadErrorResults: import('../lib/catalog').Tier1Result[] = []
                for (const entry of batch) {
                  const dl = downloaded.get(entry.skill)
                  if (dl && !dl.path && dl.error) {
                    downloadErrorResults.push({
                      source: entry.source,
                      skill: entry.skill,
                      error: dl.error,
                      errorType: dl.errorType,
                      errorDetail: dl.errorDetail,
                      errorCode: dl.errorCode,
                      retryable: dl.errorType === 'download_timeout',
                      tier2Reviewed: false,
                    })
                  }
                }

                if (successCount === 0) {
                  out.error(`[${batchNum}/${totalBatches}] All downloads failed`)
                  return stamp(downloadErrorResults)
                }

                if (failCount > 0) {
                  out.info(
                    `[${batchNum}/${totalBatches}] Downloaded ${successCount}/${batch.length} (${failCount} failed)`
                  )
                }

                // Build manifest (only successfully downloaded skills get paths)
                const manifest = batch.map((entry) => {
                  const dl = downloaded.get(entry.skill)
                  return {
                    source: entry.source,
                    skill: entry.skill,
                    localPath: dl?.path ?? 'DOWNLOAD_FAILED',
                  }
                })

                // Phase 2: Dispatch agent (async — this is the slow part we parallelize)
                const agentPrompt = [
                  'You are a skill inspector. Analyze each pre-downloaded skill and output ONE NDJSON line per skill to stdout.',
                  'Skills are already downloaded in this worktree. Do NOT attempt network downloads.',
                  '',
                  'For each skill:',
                  '1. Read the SKILL.md at the given path',
                  '2. Run: wc -w on it for word count',
                  '3. Count sections (## headings)',
                  '4. Count files in the skill directory with find',
                  '5. Extract keywords from headings and first paragraph',
                  '6. Check for <details> blocks (progressive disclosure)',
                  '7. Check frontmatter for name/description (best practices)',
                  '8. Grep for hardcoded tokens/paths (security)',
                  '9. Compute content hash: shasum -a 256 SKILL.md',
                  '',
                  'Output format (one JSON line per skill, no markdown, no prose):',
                  '{"source":"org/repo","skill":"name","wordCount":N,"sectionCount":N,"fileCount":N,"keywords":["k1","k2"],"complexity":"simple|moderate|complex","progressiveDisclosure":bool,"bestPracticesMechanical":{"score":N,"violations":[]},"securityMechanical":{"score":N,"concerns":[]},"contentHash":"sha256:...","tier2Reviewed":false}',
                  '',
                  'For failed downloads, output: {"source":"org/repo","skill":"name","error":"download failed","tier2Reviewed":false}',
                  '',
                  'Skills to analyze:',
                  JSON.stringify(manifest, null, 2),
                ].join('\n')

                // Write prompt to file to avoid shell arg length limits
                const promptFile = join(wtPath, '.inspect-prompt.txt')
                fsWriteSync(promptFile, agentPrompt, 'utf8')

                const { stdout } = await execAsync(
                  `cat ${JSON.stringify(promptFile)} | claude --model haiku --allowedTools ${JSON.stringify(ALLOWED_TOOLS)} -p -`,
                  {
                    encoding: 'utf8',
                    timeout: 300_000,
                    maxBuffer: 10 * 1024 * 1024,
                    cwd: wtPath,
                  }
                )

                const batchResults = parseTier1Output(stdout)
                // Merge download errors with analysis results
                const combined = [...batchResults, ...downloadErrorResults]
                const errors = combined.filter((r) => r.error)
                out.info(
                  `[${batchNum}/${totalBatches}] Analyzed ${batchResults.length}/${batch.length}${errors.length > 0 ? ` (${errors.length} errors)` : ''}`
                )

                return stamp(combined)
              } catch (err: unknown) {
                // Classify the batch-level failure
                const msg = err instanceof Error ? err.message : String(err)
                const stderr = (err as { stderr?: string })?.stderr ?? ''
                const exitCode = (err as { code?: number })?.code

                const isTimeout =
                  msg.includes('TIMEOUT') || msg.includes('timed out') || msg.includes('killed')
                const isRateLimit =
                  stderr.includes('rate') || stderr.includes('429') || stderr.includes('overloaded')

                const errorType = isTimeout
                  ? ('analysis_timeout' as const)
                  : isRateLimit
                    ? ('rate_limited' as const)
                    : ('batch_failed' as const)

                out.error(`[${batchNum}/${totalBatches}] ${errorType}: ${msg.slice(0, 200)}`)
                if (stderr) {
                  out.error(`  stderr: ${stderr.slice(0, 300)}`)
                }

                return stamp(
                  batch.map((e) => ({
                    source: e.source,
                    skill: e.skill,
                    error: `${errorType}: ${msg.slice(0, 200)}`,
                    errorType,
                    errorDetail: stderr.slice(0, 500) || msg.slice(0, 500),
                    errorCode: exitCode,
                    retryable: isTimeout || isRateLimit,
                    tier2Reviewed: false,
                  }))
                )
              } finally {
                if (wtPath) await removeWorktree(wtPath)
              }
            }

            // Process batches with concurrency pool
            const batchesToProcess = batches.slice(0, limit)

            // Concurrency-limited execution
            let nextIdx = 0
            const totalBatches = batchesToProcess.length

            async function runNext(): Promise<void> {
              while (nextIdx < totalBatches) {
                const idx = nextIdx++
                const batch = batchesToProcess[idx]
                const results = await processBatch(batch, idx + 1, totalBatches)
                allResults.push(...results)
                totalProcessed += results.filter((r) => !r.error).length
                totalErrors += results.filter((r) => r.error).length
              }
            }

            // Launch `concurrency` workers
            const workers = Array.from({ length: Math.min(concurrency, totalBatches) }, () =>
              runNext()
            )
            await Promise.all(workers)

            // Fork detection pass
            if (allResults.length > 0) {
              out.info('\nRunning fork detection...')
              detectForks(allResults)
              const forks = allResults.filter((r) => r.possibleForkOf)
              if (forks.length > 0) {
                out.info(`  Detected ${forks.length} possible forks`)
              }

              // Merge results into catalog
              out.info(`Merging ${allResults.length} results into catalog...`)
              mergeTier1Results(catalogPath, allResults)
            }

            out.info(`\nDone: ${totalProcessed} analyzed, ${totalErrors} errors`)

            if (args.json) {
              out.raw({
                total: allEntries.length,
                available: available.length,
                batches: batches.length,
                batchSize,
                limit,
                processed: totalProcessed,
                errors: totalErrors,
                forks: allResults.filter((r) => r.possibleForkOf).length,
              })
            }

            process.exit(totalErrors > 0 ? EXIT.FAILURES : EXIT.OK)
          },
        }),
        summary: defineCommand({
          meta: {
            name: 'summary',
            description: 'Show catalog availability summary',
          },
          args: { ...globalArgs },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const catalogPath = join(PROJECT_ROOT, 'context/skills/.catalog.ndjson')

            if (!require('node:fs').existsSync(catalogPath)) {
              out.error('Catalog not found. Run: bun run .scripts/lib/catalog.ts')
              process.exit(EXIT.ERROR)
            }

            const entries = readCatalog(catalogPath)
            const counts: Record<string, number> = {}
            for (const e of entries) {
              counts[e.availability] = (counts[e.availability] || 0) + 1
            }

            if (args.json) {
              out.raw({ total: entries.length, ...counts })
            } else {
              out.info(`Total entries: ${entries.length}`)
              for (const [status, count] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
                out.info(`  ${status}: ${count}`)
              }
            }

            process.exit(EXIT.OK)
          },
        }),
        forks: defineCommand({
          meta: {
            name: 'forks',
            description: 'Detect forks among analyzed skills by content hash',
          },
          args: { ...globalArgs },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const catalogPath = join(PROJECT_ROOT, 'context/skills/.catalog.ndjson')

            if (!require('node:fs').existsSync(catalogPath)) {
              out.error('Catalog not found.')
              process.exit(EXIT.ERROR)
            }

            const entries = readCatalog(catalogPath)
            // Filter to entries that have contentHash (Tier 1 analyzed)
            const withHash = entries.filter((e: Record<string, unknown>) => e.contentHash)

            if (withHash.length === 0) {
              out.info('No Tier 1 analyzed entries found. Run `catalog analyze` first.')
              process.exit(EXIT.OK)
            }

            const results = detectForks(
              withHash as unknown as import('../lib/catalog').Tier1Result[]
            )
            const forks = results.filter((r) => r.possibleForkOf)

            if (args.json) {
              out.raw(forks)
            } else {
              if (forks.length === 0) {
                out.info('No forks detected.')
              } else {
                out.info(`Found ${forks.length} possible forks:`)
                for (const f of forks) {
                  out.info(`  ${f.source}@${f.skill} → fork of ${f.possibleForkOf}`)
                }
              }
            }

            process.exit(EXIT.OK)
          },
        }),
        cleanup: defineCommand({
          meta: {
            name: 'cleanup',
            description: 'Remove stale worktrees and temp files from interrupted runs',
          },
          args: {
            ...globalArgs,
            'dry-run': {
              type: 'boolean',
              description: 'Show what would be cleaned without deleting',
              default: false,
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })
            const { execSync: execS } = require('node:child_process')
            const {
              rmSync: rmS,
              existsSync: existsS,
              readdirSync: readdirS,
              statSync: statS,
            } = require('node:fs')

            const dryRun = args['dry-run'] as boolean
            const WORKTREE_BASE = '/tmp/worktrees'
            const cleaned: { type: string; path: string; size?: string }[] = []

            // 1. Find stale git worktrees
            try {
              const wtList = execS('git worktree list --porcelain', {
                cwd: PROJECT_ROOT,
                encoding: 'utf8',
              }) as string

              const staleWorktrees: string[] = []
              for (const line of wtList.split('\n')) {
                if (line.startsWith('worktree ') && line.includes('/tmp/worktrees/skill-inspect')) {
                  staleWorktrees.push(line.replace('worktree ', ''))
                }
              }

              for (const wt of staleWorktrees) {
                if (dryRun) {
                  cleaned.push({ type: 'worktree', path: wt })
                } else {
                  try {
                    execS(`git worktree unlock ${JSON.stringify(wt)}`, {
                      cwd: PROJECT_ROOT,
                      stdio: 'pipe',
                    })
                  } catch {
                    /* ignore */
                  }
                  try {
                    execS(`git worktree remove --force ${JSON.stringify(wt)}`, {
                      cwd: PROJECT_ROOT,
                      stdio: 'pipe',
                    })
                  } catch {
                    /* ignore */
                  }
                  try {
                    rmS(wt, { recursive: true, force: true })
                  } catch {
                    /* ignore */
                  }
                  cleaned.push({ type: 'worktree', path: wt })
                }
              }
            } catch {
              /* no worktrees */
            }

            // 2. Find orphaned /tmp/worktrees/skill-inspect-* dirs not tracked by git
            if (existsS(WORKTREE_BASE)) {
              try {
                const dirs = readdirS(WORKTREE_BASE).filter((d: string) =>
                  d.startsWith('skill-inspect')
                )
                for (const dir of dirs) {
                  const fullPath = join(WORKTREE_BASE, dir)
                  try {
                    if (!statS(fullPath).isDirectory()) continue
                  } catch {
                    continue
                  }

                  // Check if already cleaned as a worktree above
                  if (cleaned.some((c) => c.path === fullPath)) continue

                  if (dryRun) {
                    cleaned.push({ type: 'orphan-dir', path: fullPath })
                  } else {
                    try {
                      rmS(fullPath, { recursive: true, force: true })
                    } catch {
                      /* ignore */
                    }
                    cleaned.push({ type: 'orphan-dir', path: fullPath })
                  }
                }
              } catch {
                /* ignore */
              }
            }

            // 3. Prune git worktree refs for already-deleted directories
            if (!dryRun) {
              try {
                execS('git worktree prune', { cwd: PROJECT_ROOT, stdio: 'pipe' })
                cleaned.push({ type: 'prune', path: 'git worktree prune' })
              } catch {
                /* ignore */
              }
            }

            if (args.json) {
              out.raw({ dryRun, cleaned })
            } else {
              if (cleaned.length === 0) {
                out.info('Nothing to clean up.')
              } else {
                out.info(`${dryRun ? '[DRY RUN] Would clean' : 'Cleaned'} ${cleaned.length} items:`)
                for (const c of cleaned) {
                  out.info(`  ${c.type}: ${c.path}`)
                }
              }
            }

            process.exit(EXIT.OK)
          },
        }),
        errors: defineCommand({
          meta: {
            name: 'errors',
            description: 'Show error breakdown from catalog analysis',
          },
          args: {
            ...globalArgs,
            retryable: {
              type: 'boolean',
              description: 'Show only retryable errors',
              default: false,
            },
          },
          async run({ args }) {
            const out = createOutput({
              json: args.json as boolean,
              quiet: args.quiet as boolean,
            })

            const catalogPath = join(PROJECT_ROOT, 'context/skills/.catalog.ndjson')
            if (!require('node:fs').existsSync(catalogPath)) {
              out.error('Catalog not found.')
              process.exit(EXIT.ERROR)
            }

            const entries = readCatalog(catalogPath) as Array<Record<string, unknown>>
            const withErrors = entries.filter((e) => e.error)

            if (args.retryable) {
              const retryable = withErrors.filter((e) => e.retryable === true)
              if (args.json) {
                out.raw({ total: retryable.length, entries: retryable })
              } else {
                out.info(`Retryable errors: ${retryable.length}`)
                const byType: Record<string, number> = {}
                for (const e of retryable) {
                  const t = (e.errorType as string) || 'unknown'
                  byType[t] = (byType[t] || 0) + 1
                }
                for (const [t, c] of Object.entries(byType).sort((a, b) => b[1] - a[1])) {
                  out.info(`  ${t}: ${c}`)
                }
              }
            } else {
              const byType: Record<string, number> = {}
              for (const e of withErrors) {
                const t = (e.errorType as string) || (e.error as string)?.slice(0, 40) || 'unknown'
                byType[t] = (byType[t] || 0) + 1
              }

              if (args.json) {
                out.raw({ total: withErrors.length, byType })
              } else {
                out.info(`Total errors: ${withErrors.length} / ${entries.length} entries`)
                out.info('\nBy type:')
                for (const [t, c] of Object.entries(byType).sort((a, b) => b[1] - a[1])) {
                  out.info(`  ${c.toString().padStart(5)}  ${t}`)
                }
              }
            }

            process.exit(EXIT.OK)
          },
        }),
      },
    }),
  },
})
