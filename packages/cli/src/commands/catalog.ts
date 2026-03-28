/**
 * Catalog inspection pipeline commands.
 *
 * Named exception to the verb-first grammar — accessible as both:
 *   agents catalog <subcommand>
 *   agents skill catalog <subcommand>  (backward-compat)
 *
 * Subcommands: analyze, summary, forks, cleanup, errors, scrub, stale, backfill, discover
 */

import { exec as execCb, execSync } from 'node:child_process'
import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { join, resolve } from 'node:path'
import { promisify } from 'node:util'
// downloadBatch removed — analyze now uses discoverAllRepos (imported dynamically)
import { createGit } from '@agents/core/git'
import { currentDir } from '@agents/core/runtime'
import { EXIT } from '@agents/core/types'
import { uuid7 } from '@agents/core/uuid'
import {
  createBatches,
  detectForks,
  filterForProcessing,
  formatBatchPrompt,
  mergeTier1Results,
  parseTier1Output,
  readCatalog,
  readErrorLog,
  validateBatchResults,
} from '@agents/sdk/catalog/pipeline/io'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')
const SKILLS_DIR = join(PROJECT_ROOT, 'content/skills')

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

export default defineCommand({
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
        force: {
          type: 'boolean',
          description: 'Process all available entries regardless of state',
          default: false,
        },
        'retry-errors': {
          type: 'boolean',
          description: 'Process only retryable failed entries',
          default: false,
        },
        'git-protocol': {
          type: 'string',
          description: 'Force git protocol: ssh|https|auto (default: auto)',
          default: 'auto',
        },
        missing: {
          type: 'string',
          description:
            'Only process analyzed entries missing this field (e.g., complexity, keywords)',
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')

        if (!existsSync(catalogPath)) {
          out.error('Catalog not found. Run availability check first: bun run cli/lib/catalog.ts')
          process.exit(EXIT.ERROR)
        }

        const allEntries = readCatalog(
          catalogPath
        ) as import('../lib/catalog').CatalogEntryWithTier1[]
        const force = args.force as boolean
        const retryErrors = args['retry-errors'] as boolean
        const missingField = args.missing as string | undefined

        let toProcess: import('../lib/catalog').CatalogEntryWithTier1[]
        if (missingField) {
          // Target only analyzed entries missing a specific field
          toProcess = allEntries.filter(
            (e) =>
              e.availability === 'available' &&
              e.wordCount != null &&
              (e as Record<string, unknown>)[missingField] == null
          )
        } else {
          toProcess = filterForProcessing(allEntries, { force, retryErrors })
        }
        const totalAvailable = allEntries.filter((e) => e.availability === 'available').length
        const skipped = totalAvailable - toProcess.length
        const batchSize = parseInt(args['batch-size'] as string, 10) || 15
        const batches = createBatches(toProcess, batchSize)
        const limit = args.limit ? parseInt(args.limit as string, 10) : batches.length

        out.info(`Catalog: ${allEntries.length} total, ${totalAvailable} available`)
        out.info(
          `Processing: ${toProcess.length} entries (${skipped} skipped)${force ? ' [--force]' : ''}${retryErrors ? ' [--retry-errors]' : ''}`
        )
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
        const execAsync = promisify(execCb)

        const WORKTREE_BASE = '/tmp/worktrees'
        const concurrency = parseInt(args.concurrency as string, 10) || 3

        // Generate run-level UUID7 (timestamp-sortable, unique per invocation)
        const runId = uuid7()
        out.info(`Concurrency: ${concurrency} parallel agents`)
        out.info(`Run ID: ${runId}`)

        // --- Discovery phase: clone each unique repo ONCE, compute all fields ---
        const gitProtocol = args['git-protocol'] as string
        const protocol = gitProtocol === 'auto' ? undefined : (gitProtocol as 'ssh' | 'https')
        const { discoverAllRepos } = await import('../lib/catalog-discover')
        out.info('Discovering skills across all repos...')
        const discoverySummary = await discoverAllRepos(
          toProcess as import('../lib/catalog').CatalogEntryWithTier1[],
          {
            concurrency: 5,
            protocol,
            onProgress: (done, total, repo) => {
              if (done % 10 === 0 || done === total) {
                out.info(`  Discovery: ${done}/${total} repos (${repo})`)
              }
            },
          }
        )

        // Build lookup map: "source:skill" → DiscoveredSkillResult
        const discoveryMap = new Map<
          string,
          import('../lib/catalog-discover').DiscoveredSkillResult
        >()
        for (const repoResult of discoverySummary.results) {
          for (const skill of repoResult.skills) {
            discoveryMap.set(`${skill.source}:${skill.skill}`, skill)
          }
        }

        // Collect discovery-level errors (clone failures, missing skills)
        const discoveryErrors = new Map<
          string,
          { error: string; errorType: import('../lib/catalog').Tier1ErrorType }
        >()
        for (const repoResult of discoverySummary.results) {
          for (const e of repoResult.errors) {
            // errors have source-level scope; apply to all skills in that source
            for (const entry of toProcess.filter((en) => en.source === e.source)) {
              discoveryErrors.set(`${entry.source}:${entry.skill}`, {
                error: e.error,
                errorType: e.errorType,
              })
            }
          }
          for (const m of repoResult.missing) {
            discoveryErrors.set(`${m.source}:${m.skill}`, {
              error: `skill "${m.skill}" not found in ${m.source}`,
              errorType: 'download_failed',
            })
          }
        }

        out.info(
          `Discovery complete: ${discoveryMap.size} skills found, ${discoveryErrors.size} errors`
        )

        /** Create a git worktree for a batch using simple-git, returns worktree path */
        async function createWorktree(batchId: number): Promise<string> {
          const wtPath = join(WORKTREE_BASE, `skill-inspect-${batchId}`)
          const git = createGit(PROJECT_ROOT)

          if (existsSync(wtPath)) {
            try {
              await git.raw(['worktree', 'unlock', wtPath])
            } catch {
              /* ignore */
            }
            try {
              await git.raw(['worktree', 'remove', '--force', wtPath])
            } catch {
              /* ignore */
            }
            try {
              rmSync(wtPath, { recursive: true, force: true })
            } catch {
              /* ignore */
            }
          }

          await git.raw(['worktree', 'add', '--detach', wtPath, 'HEAD'])
          return wtPath
        }

        /** Remove a git worktree using simple-git */
        async function removeWorktree(wtPath: string): Promise<void> {
          const git = createGit(PROJECT_ROOT)
          try {
            await git.raw(['worktree', 'unlock', wtPath])
          } catch {
            /* ignore */
          }
          try {
            await git.raw(['worktree', 'remove', '--force', wtPath])
          } catch {
            /* ignore */
          }
          try {
            rmSync(wtPath, { recursive: true, force: true })
          } catch {
            /* ignore */
          }
        }

        // Ensure worktree base dir exists
        mkdirSync(WORKTREE_BASE, { recursive: true })

        // Agent uses no tools — judgment-only prompt receives content inline

        let totalProcessed = 0
        let totalErrors = 0
        const allResults: import('../lib/catalog').Tier1Result[] = []

        /**
         * Process a single batch: create worktree, build manifests from discovery, analyze, cleanup.
         * Uses pre-computed discovery results (discoveryMap) instead of per-batch downloads.
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
            // Phase 1: Create worktree + resolve skills from discovery map
            wtPath = await createWorktree(batchNum)
            out.info(
              `[${batchNum}/${totalBatches}] Worktree ready, resolving ${batch.length} skills from discovery...`
            )

            // Collect per-skill error results from discovery
            const discoveryErrorResults: import('../lib/catalog').Tier1Result[] = []
            const resolvedEntries: Array<{
              entry: import('../lib/catalog').CatalogEntry
              discovered: import('../lib/catalog-discover').DiscoveredSkillResult
            }> = []

            for (const entry of batch) {
              const key = `${entry.source}:${entry.skill}`
              const discovered = discoveryMap.get(key)
              const discError = discoveryErrors.get(key)

              if (discovered?.content) {
                resolvedEntries.push({ entry, discovered })
              } else if (discError) {
                discoveryErrorResults.push({
                  source: entry.source,
                  skill: entry.skill,
                  error: discError.error,
                  errorType: discError.errorType,
                  retryable: discError.errorType === 'download_timeout',
                  tier2Reviewed: false,
                })
              } else {
                discoveryErrorResults.push({
                  source: entry.source,
                  skill: entry.skill,
                  error: `skill "${entry.skill}" not found in discovery results for ${entry.source}`,
                  errorType: 'download_failed',
                  retryable: false,
                  tier2Reviewed: false,
                })
              }
            }

            const successCount = resolvedEntries.length
            const failCount = batch.length - successCount

            if (successCount === 0) {
              out.error(`[${batchNum}/${totalBatches}] All skills failed discovery`)
              return stamp(discoveryErrorResults)
            }

            if (failCount > 0) {
              out.info(
                `[${batchNum}/${totalBatches}] Resolved ${successCount}/${batch.length} (${failCount} failed)`
              )
            }

            // Build manifests from discovery results (content is already available)
            const { buildManifest, buildTier1AgentPrompt } = await import('../lib/catalog-manifest')
            const manifests = resolvedEntries.map(({ discovered }) =>
              buildManifest(discovered, discovered.content as string)
            )

            // Phase 2: Dispatch agent (judgment-only — no tools, content inline)
            const agentPrompt = buildTier1AgentPrompt(manifests)

            // Write prompt to file to avoid shell arg length limits
            const promptFile = join(wtPath, '.inspect-prompt.txt')
            writeFileSync(promptFile, agentPrompt, 'utf8')

            const { stdout } = await execAsync(
              `cat ${JSON.stringify(promptFile)} | claude --model haiku -p -`,
              {
                encoding: 'utf8',
                timeout: 300_000,
                maxBuffer: 10 * 1024 * 1024,
                cwd: wtPath,
              }
            )

            const agentResults = parseTier1Output(stdout)

            // Merge orchestrator mechanical data (authoritative) with agent judgment data
            const batchResults: import('../lib/catalog').Tier1Result[] = []
            for (const { entry, discovered } of resolvedEntries) {
              const agentResult = agentResults.find(
                (r) => r.source === entry.source && r.skill === entry.skill
              )

              // Success: discovery mechanical fields + agent judgment fields
              batchResults.push({
                source: entry.source,
                skill: entry.skill,
                // Discovery mechanical data (authoritative)
                contentHash: discovered.mechanical.contentHash,
                wordCount: discovered.mechanical.wordCount,
                sectionCount: discovered.mechanical.sectionCount,
                fileCount: discovered.mechanical.fileCount,
                headingTree: discovered.mechanical.headingTree,
                treeSha: discovered.mechanical.treeSha,
                discoveredPath: discovered.mechanical.discoveredPath,
                lastSeenAt: discovered.mechanical.lastSeenAt,
                lastSeenHeadSha: discovered.mechanical.lastSeenHeadSha,
                lineCount: discovered.mechanical.lineCount,
                sectionMap: discovered.mechanical.sectionMap,
                fileTree: discovered.mechanical.fileTree,
                skillSizeBytes: discovered.mechanical.skillSizeBytes,
                isSimple: discovered.mechanical.isSimple,
                // Agent judgment data (overlay)
                ...(agentResult
                  ? {
                      keywords: agentResult.keywords,
                      complexity: agentResult.complexity,
                      progressiveDisclosure: agentResult.progressiveDisclosure,
                      pdTechniques: agentResult.pdTechniques,
                      bestPracticesMechanical: agentResult.bestPracticesMechanical,
                      securityMechanical: agentResult.securityMechanical,
                      internalLinks: agentResult.internalLinks,
                      externalLinks: agentResult.externalLinks,
                    }
                  : {}),
                tier2Reviewed: false,
              })
            }

            // Combine with discovery errors
            const combined = [...batchResults, ...discoveryErrorResults]
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
            if (wtPath) {
              await removeWorktree(wtPath)
            }
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
        const workers = Array.from({ length: Math.min(concurrency, totalBatches) }, () => runNext())
        await Promise.all(workers)

        // Fork detection pass
        if (allResults.length > 0) {
          out.info('\nRunning fork detection...')
          detectForks(allResults)
          const forks = allResults.filter((r) => r.possibleForkOf)
          if (forks.length > 0) {
            out.info(`  Detected ${forks.length} possible forks`)
          }

          // Merge results into catalog + error log
          const errorLogPath = join(PROJECT_ROOT, 'content/skills/.catalog-errors.ndjson')
          out.info(`Merging ${allResults.length} results into catalog...`)
          mergeTier1Results(catalogPath, errorLogPath, allResults)

          // Validate batch results
          const validation = validateBatchResults(allResults)
          if (validation.issues.length > 0) {
            out.info(`\nValidation warnings (${validation.issues.length}):`)
            for (const issue of validation.issues.slice(0, 10)) {
              process.stderr.write(`  ${issue}\n`)
            }
            if (validation.issues.length > 10) {
              process.stderr.write(`  ... and ${validation.issues.length - 10} more\n`)
            }
          }
        }

        out.info(`\nDone: ${totalProcessed} analyzed, ${totalErrors} errors`)

        if (args.json) {
          out.raw({
            total: allEntries.length,
            available: totalAvailable,
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
        description: 'Show catalog availability and analysis summary',
      },
      args: { ...globalArgs },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')

        if (!existsSync(catalogPath)) {
          out.error('Catalog not found. Run: bun run cli/lib/catalog.ts')
          process.exit(EXIT.ERROR)
        }

        const entries = readCatalog(catalogPath) as Array<Record<string, unknown>>
        const counts: Record<string, number> = {}
        for (const e of entries) {
          counts[e.availability as string] = (counts[e.availability as string] || 0) + 1
        }

        // Analysis status breakdown
        let analyzed = 0
        let failedOnce = 0
        let failedTwicePlus = 0
        let neverAttempted = 0
        const attemptDist: Record<number, number> = {}

        for (const e of entries) {
          if (e.availability !== 'available') continue
          const attempts = (e.attemptCount as number) ?? 0
          const hasData = e.wordCount != null

          attemptDist[attempts] = (attemptDist[attempts] || 0) + 1

          if (hasData && attempts === 0) analyzed++
          else if (attempts === 0) neverAttempted++
          else if (attempts === 1) failedOnce++
          else failedTwicePlus++
        }

        if (args.json) {
          out.raw({
            total: entries.length,
            availability: counts,
            analysis: { analyzed, failedOnce, failedTwicePlus, neverAttempted },
            attemptDistribution: attemptDist,
          })
        } else {
          out.info(`Total entries: ${entries.length}`)
          for (const [status, count] of Object.entries(counts).sort((a, b) => b[1] - a[1])) {
            out.info(`  ${status}: ${count}`)
          }
          out.info('')
          out.info('Analysis status:')
          out.info(`  Analyzed (attemptCount=0): ${analyzed}`)
          out.info(`  Failed once (attemptCount=1): ${failedOnce}`)
          out.info(`  Failed twice+ (attemptCount>=2): ${failedTwicePlus}`)
          out.info(`  Never attempted: ${neverAttempted}`)
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

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')

        if (!existsSync(catalogPath)) {
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

        const results = detectForks(withHash as unknown as import('../lib/catalog').Tier1Result[])
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
        const dryRun = args['dry-run'] as boolean
        const WORKTREE_BASE = '/tmp/worktrees'
        const cleaned: { type: string; path: string; size?: string }[] = []

        // 1. Find stale git worktrees
        try {
          const wtList = execSync('git worktree list --porcelain', {
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
                execSync(`git worktree unlock ${JSON.stringify(wt)}`, {
                  cwd: PROJECT_ROOT,
                  stdio: 'pipe',
                })
              } catch {
                /* ignore */
              }
              try {
                execSync(`git worktree remove --force ${JSON.stringify(wt)}`, {
                  cwd: PROJECT_ROOT,
                  stdio: 'pipe',
                })
              } catch {
                /* ignore */
              }
              try {
                rmSync(wt, { recursive: true, force: true })
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
        if (existsSync(WORKTREE_BASE)) {
          try {
            const dirs = readdirSync(WORKTREE_BASE).filter((d: string) =>
              d.startsWith('skill-inspect')
            )
            for (const dir of dirs) {
              const fullPath = join(WORKTREE_BASE, dir)
              try {
                if (!statSync(fullPath).isDirectory()) continue
              } catch {
                continue
              }

              // Check if already cleaned as a worktree above
              if (cleaned.some((c) => c.path === fullPath)) continue

              if (dryRun) {
                cleaned.push({ type: 'orphan-dir', path: fullPath })
              } else {
                try {
                  rmSync(fullPath, { recursive: true, force: true })
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
            execSync('git worktree prune', { cwd: PROJECT_ROOT, stdio: 'pipe' })
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
        description: 'Show error breakdown from error log',
      },
      args: {
        ...globalArgs,
        retryable: {
          type: 'boolean',
          description: 'Show only retryable errors',
          default: false,
        },
        prune: {
          type: 'boolean',
          description: 'Remove resolved errors (skills with attemptCount=0)',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const errorLogPath = join(PROJECT_ROOT, 'content/skills/.catalog-errors.ndjson')
        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')

        if (args.prune) {
          // Prune: remove error records for skills that have been resolved (attemptCount=0)
          if (!existsSync(errorLogPath)) {
            out.info('No error log found. Nothing to prune.')
            process.exit(EXIT.OK)
          }
          const catalog = readCatalog(catalogPath) as Array<Record<string, unknown>>
          const resolved = new Set<string>()
          for (const e of catalog) {
            if ((e.attemptCount ?? 0) === 0 && e.wordCount) {
              resolved.add(`${e.source}\0${e.skill}`)
            }
          }
          const errors = readErrorLog(errorLogPath)
          const kept = errors.filter((e) => !resolved.has(`${e.source}\0${e.skill}`))
          const pruned = errors.length - kept.length
          writeFileSync(
            errorLogPath,
            kept.map((e) => JSON.stringify(e)).join('\n') + (kept.length > 0 ? '\n' : ''),
            'utf8'
          )
          out.info(`Pruned ${pruned} resolved error records. ${kept.length} remaining.`)
          process.exit(EXIT.OK)
        }

        const errors = readErrorLog(errorLogPath)
        if (errors.length === 0) {
          out.info('No errors in error log.')
          process.exit(EXIT.OK)
        }

        if (args.retryable) {
          const retryable = errors.filter((e) => e.retryable)
          if (args.json) {
            out.raw({ total: retryable.length, entries: retryable })
          } else {
            out.info(`Retryable errors: ${retryable.length}`)
            const byType: Record<string, number> = {}
            for (const e of retryable) {
              byType[e.errorType] = (byType[e.errorType] || 0) + 1
            }
            for (const [t, c] of Object.entries(byType).sort((a, b) => b[1] - a[1])) {
              out.info(`  ${t}: ${c}`)
            }
          }
        } else {
          const byType: Record<string, number> = {}
          for (const e of errors) {
            byType[e.errorType] = (byType[e.errorType] || 0) + 1
          }

          if (args.json) {
            out.raw({ total: errors.length, byType })
          } else {
            out.info(`Total error records: ${errors.length}`)
            out.info('\nBy type:')
            for (const [t, c] of Object.entries(byType).sort((a, b) => b[1] - a[1])) {
              out.info(`  ${c.toString().padStart(5)}  ${t}`)
            }
          }
        }

        process.exit(EXIT.OK)
      },
    }),
    scrub: defineCommand({
      meta: {
        name: 'scrub',
        description: 'Backfill: separate error data from catalog into error log',
      },
      args: {
        ...globalArgs,
        'dry-run': {
          type: 'boolean',
          description: 'Show what would change without modifying files',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })
        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')
        const errorLogPath = join(PROJECT_ROOT, 'content/skills/.catalog-errors.ndjson')
        const lockPath = join(PROJECT_ROOT, 'content/skills/.catalog.lock')

        if (!existsSync(catalogPath)) {
          out.error('Catalog not found.')
          process.exit(EXIT.ERROR)
        }

        if (existsSync(lockPath)) {
          out.error('Catalog is locked (.catalog.lock exists). Another operation in progress?')
          process.exit(EXIT.ERROR)
        }

        const dryRun = args['dry-run'] as boolean

        // Read all entries
        const content = readFileSync(catalogPath, 'utf8') as string
        const entries: Array<Record<string, unknown>> = []
        for (const line of content.split('\n')) {
          const trimmed = line.trim()
          if (!trimmed) continue
          try {
            entries.push(JSON.parse(trimmed))
          } catch {
            // skip
          }
        }

        // Classify entries
        let dataAndError = 0 // has wordCount AND error
        let errorOnly = 0 // has error but no wordCount
        const errorRecords: Array<Record<string, unknown>> = []

        for (const e of entries) {
          const hasData = e.wordCount != null
          const hasError = e.error != null

          if (hasData && hasError) {
            dataAndError++
          } else if (hasError && !hasData) {
            errorOnly++
            errorRecords.push({
              source: e.source,
              skill: e.skill,
              runId: e.runId ?? '',
              batchId: e.batchId ?? '',
              timestamp: (e.analyzedAt as string) ?? new Date().toISOString(),
              errorType: e.errorType ?? 'batch_failed',
              errorDetail: e.errorDetail ?? e.error ?? '',
              errorCode: e.errorCode,
              retryable: e.retryable ?? true,
            })
          }
        }

        if (dryRun) {
          out.info('[DRY RUN] catalog scrub')
          out.info('')
          out.info(
            `Entries to clean (have data + error): ${dataAndError} — error fields stripped, attemptCount reset`
          )
          out.info(
            `Entries to move to error log (error only): ${errorOnly} — moved to .catalog-errors.ndjson`
          )
          out.info('')
          out.info(`Summary:`)
          out.info(`  Catalog entries modified: ${dataAndError + errorOnly}`)
          out.info(`  Error log entries created: ${errorOnly}`)
          out.info(`  Catalog size: ${entries.length} entries (count unchanged, fields stripped)`)
          process.exit(EXIT.OK)
        }

        // Acquire lock
        writeFileSync(lockPath, `pid=${process.pid}\n`, 'utf8')

        try {
          // Process entries
          const cleaned: Array<Record<string, unknown>> = []
          for (const e of entries) {
            const hasData = e.wordCount != null
            const hasError = e.error != null
            const entry = { ...e }

            if (hasData && hasError) {
              // Clean: strip error fields, reset attemptCount
              delete entry.error
              delete entry.errorDetail
              delete entry.errorCode
              delete entry.errorType
              delete entry.retryable
              entry.attemptCount = 0
            } else if (hasError && !hasData) {
              // Move error to log, set cache fields
              delete entry.error
              delete entry.errorDetail
              delete entry.errorCode
              entry.attemptCount = 1
              entry.lastErrorType = entry.errorType ?? 'batch_failed'
              entry.retryable = e.retryable ?? true
              delete entry.errorType
            }

            cleaned.push(entry)
          }

          // Write error log
          if (errorRecords.length > 0) {
            const errorLines = `${errorRecords.map((r) => JSON.stringify(r)).join('\n')}\n`
            appendFileSync(errorLogPath, errorLines, 'utf8')
          }

          // Write catalog atomically
          const tmpPath = `${catalogPath}.tmp`
          writeFileSync(tmpPath, `${cleaned.map((e) => JSON.stringify(e)).join('\n')}\n`, 'utf8')
          renameSync(tmpPath, catalogPath)

          out.info(`Scrub complete:`)
          out.info(`  ${dataAndError} entries cleaned (error fields stripped)`)
          out.info(`  ${errorOnly} entries moved to error log`)
        } finally {
          // Release lock
          try {
            unlinkSync(lockPath)
          } catch {
            /* ignore */
          }
        }

        process.exit(EXIT.OK)
      },
    }),
    stale: defineCommand({
      meta: {
        name: 'stale',
        description: 'Find analyzed skills with upstream content changes',
      },
      args: {
        ...globalArgs,
        limit: {
          type: 'string',
          description: 'Max entries to check (default: 100)',
          default: '100',
        },
        concurrency: {
          type: 'string',
          description: 'Parallel API requests (default: 5)',
          default: '5',
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')
        if (!existsSync(catalogPath)) {
          out.error('Catalog not found.')
          process.exit(EXIT.ERROR)
        }

        const { identifyStaleEntries, fetchUpstreamHashes } = await import('../lib/catalog-stale')
        const allEntries = readCatalog(
          catalogPath
        ) as import('../lib/catalog').CatalogEntryWithTier1[]
        const analyzed = allEntries.filter(
          (e) => e.treeSha && e.wordCount && e.availability === 'available'
        )
        const limit = parseInt(args.limit as string, 10) || 100
        const concurrency = parseInt(args.concurrency as string, 10) || 5
        const toCheck = analyzed.slice(0, limit)

        out.info(`Checking ${toCheck.length} analyzed skills against upstream...`)

        const upstreamHashes = await fetchUpstreamHashes(toCheck, { concurrency })
        const results = identifyStaleEntries(toCheck, upstreamHashes)
        const stale = results.filter((r) => r.status === 'stale')

        if (args.json) {
          out.raw({ checked: toCheck.length, stale: stale.length, results: stale })
        } else {
          out.info(`Checked: ${results.length}, Stale: ${stale.length}`)
          for (const r of stale) {
            out.info(
              `  ${r.source}@${r.skill} (local: ${r.localHash?.slice(0, 16)}... remote: ${r.remoteHash?.slice(0, 16)}...)`
            )
          }
          if (stale.length > 0) {
            out.info('\nRe-analyze stale skills with: just agents skill catalog analyze --force')
          }
        }

        process.exit(EXIT.OK)
      },
    }),

    backfill: defineCommand({
      meta: {
        name: 'backfill',
        description:
          'Fill missing mechanical fields (headingTree, treeSha, keywords) on analyzed entries',
      },
      args: {
        ...globalArgs,
        limit: {
          type: 'string',
          description: 'Max entries to backfill (default: all)',
        },
        concurrency: {
          type: 'string',
          description: 'Parallel clone operations (default: 5)',
          default: '5',
        },
        'include-errors': {
          type: 'boolean',
          description: 'Also reclassify batch_failed errors',
          default: true,
        },
        'dry-run': {
          type: 'boolean',
          description: 'Show what would be backfilled without doing it',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')
        if (!existsSync(catalogPath)) {
          out.error('Catalog not found.')
          process.exit(EXIT.ERROR)
        }

        const { backfillEntries } = await import('../lib/catalog-download')
        const { mergeBackfillResults } = await import('../lib/catalog')
        const errorLogPath = join(PROJECT_ROOT, 'content/skills/.catalog-errors.ndjson')

        const allEntries = readCatalog(
          catalogPath
        ) as import('../lib/catalog').CatalogEntryWithTier1[]

        // Select entries needing backfill
        const needsBackfill = allEntries.filter((e) => {
          if (e.availability !== 'available') return false
          const missingFields =
            e.wordCount != null &&
            (!e.headingTree || !e.treeSha || !e.keywords || e.keywords.length === 0)
          const needsReclassify = args['include-errors'] && e.lastErrorType === 'batch_failed'
          return missingFields || needsReclassify
        })

        const limit = args.limit ? parseInt(args.limit as string, 10) : needsBackfill.length
        const toProcess = needsBackfill.slice(0, limit)
        const concurrency = parseInt(args.concurrency as string, 10) || 5

        const missingHeadingTree = toProcess.filter(
          (e) => e.wordCount != null && !e.headingTree
        ).length
        const missingTreeSha = toProcess.filter((e) => e.wordCount != null && !e.treeSha).length
        const missingKeywords = toProcess.filter(
          (e) => e.wordCount != null && (!e.keywords || e.keywords.length === 0)
        ).length
        const batchFailed = toProcess.filter((e) => e.lastErrorType === 'batch_failed').length

        out.info(`Backfill candidates: ${needsBackfill.length} (processing ${toProcess.length})`)
        out.info(`  Missing headingTree: ${missingHeadingTree}`)
        out.info(`  Missing treeSha:     ${missingTreeSha}`)
        out.info(`  Missing keywords:    ${missingKeywords}`)
        out.info(`  batch_failed errors: ${batchFailed}`)

        if (args['dry-run']) {
          process.exit(EXIT.OK)
        }

        out.info(`\nBackfilling with concurrency ${concurrency}...`)

        const results = await backfillEntries(toProcess, {
          concurrency,
          onProgress: (done, total) => {
            if (done % 50 === 0 || done === total) {
              out.info(`  Progress: ${done}/${total}`)
            }
          },
        })

        out.info(`\nMerging ${results.length} results into catalog...`)
        const { updated, reclassified, failed } = mergeBackfillResults(
          catalogPath,
          errorLogPath,
          results
        )

        if (args.json) {
          out.raw({
            processed: toProcess.length,
            updated,
            reclassified,
            failed,
          })
        } else {
          out.info(
            `Done: ${updated} updated, ${reclassified} reclassified, ${failed} download failures`
          )
        }

        process.exit(EXIT.OK)
      },
    }),

    discover: defineCommand({
      meta: {
        name: 'discover',
        description: 'Clone unique repos, discover all skills, compute mechanical fields',
      },
      args: {
        ...globalArgs,
        limit: {
          type: 'string',
          description: 'Max repos to discover (default: all)',
        },
        concurrency: {
          type: 'string',
          description: 'Parallel clone operations (default: 5)',
          default: '5',
        },
        incremental: {
          type: 'boolean',
          description: 'Skip repos whose HEAD matches cached manifest',
          default: true,
        },
        full: {
          type: 'boolean',
          description: 'Force re-cloning all repos (bypass incremental cache)',
          default: false,
        },
        apply: {
          type: 'boolean',
          description: 'Apply reconciliation changes to catalog (add/remove/update entries)',
          default: false,
        },
        'dry-run': {
          type: 'boolean',
          description: 'Show repo count without cloning',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({
          json: args.json as boolean,
          quiet: args.quiet as boolean,
        })

        const catalogPath = join(PROJECT_ROOT, 'content/skills/.catalog.ndjson')
        if (!existsSync(catalogPath)) {
          out.error('Catalog not found.')
          process.exit(EXIT.ERROR)
        }

        const { discoverAllRepos } = await import('../lib/catalog-discover')
        const { readRepoManifest, mergeRepoManifest } = await import('../lib/catalog')
        const { reconcile, detectMoveRenames, applyReconciliation } = await import(
          '../lib/catalog-reconcile'
        )
        const manifestPath = join(PROJECT_ROOT, 'content/skills/.catalog-repos.ndjson')

        const allEntries = readCatalog(
          catalogPath
        ) as import('../lib/catalog').CatalogEntryWithTier1[]
        const available = allEntries.filter((e) => e.availability === 'available')
        const uniqueRepos = new Set(available.map((e) => e.source))
        const concurrency = parseInt(args.concurrency as string, 10) || 5
        const forceFullClone = args.full as boolean
        const incremental = forceFullClone ? false : (args.incremental as boolean)
        const cachedManifests = incremental ? readRepoManifest(manifestPath) : []

        out.info(`Catalog: ${allEntries.length} entries, ${uniqueRepos.size} unique repos`)
        out.info(
          `Mode: ${forceFullClone ? 'full (--full)' : incremental ? 'incremental' : 'full'} (${cachedManifests.length} cached)`
        )

        if (args['dry-run']) {
          if (args.json) {
            out.raw({ repos: uniqueRepos.size, cached: cachedManifests.length })
          }
          process.exit(EXIT.OK)
        }

        const limit = args.limit ? parseInt(args.limit as string, 10) : undefined
        const toProcess = limit
          ? available.filter((_, i) => i < limit * 25) // rough: limit repos * avg skills
          : available

        out.info(`\nDiscovering with concurrency ${concurrency}...`)

        const summary = await discoverAllRepos(toProcess, {
          concurrency,
          incremental,
          cachedManifests,
          onProgress: (done, total, repo) => {
            if (done % 10 === 0 || done === total) {
              out.info(`  Progress: ${done}/${total} repos (${repo})`)
            }
          },
        })

        // Write repo manifests
        for (const result of summary.results) {
          mergeRepoManifest(manifestPath, result.manifest)
        }

        // Summary
        const totalSkills = summary.results.reduce((n, r) => n + r.skills.length, 0)
        const totalMissing = summary.results.reduce((n, r) => n + r.missing.length, 0)
        const totalErrors = summary.results.reduce((n, r) => n + r.errors.length, 0)

        out.info(`\nDiscovery complete:`)
        out.info(
          `  Skipped ${summary.skipped} repos (unchanged HEAD), cloned ${summary.cloned} repos`
        )
        out.info(`  Skills found: ${totalSkills}`)
        out.info(`  Missing from repos: ${totalMissing}`)
        out.info(`  Clone errors: ${totalErrors}`)

        // Reconcile discovery results against existing catalog
        const report = reconcile(allEntries, summary.results)
        detectMoveRenames(report, allEntries)

        out.info(`\nReconciliation:`)
        out.info(`  Updated: ${report.updated.length}`)
        out.info(`  Added: ${report.added.length}`)
        out.info(`  Removed: ${report.removed.length}`)
        out.info(`  Moved: ${report.moved.length}`)
        out.info(`  Renamed: ${report.renamed.length}`)
        out.info(`  Errors: ${report.errors.length}`)

        // Apply reconciliation changes if requested
        if (args.apply) {
          const allDiscovered = summary.results.flatMap((r) => r.skills)
          const stats = applyReconciliation(catalogPath, report, allDiscovered)
          out.info(`\nApplied to catalog:`)
          out.info(
            `  ${stats.added} added, ${stats.removed} removed, ${stats.updated} updated, ${stats.moved} moved`
          )
        }

        if (args.json) {
          out.raw({
            repos: summary.totalRepos,
            cloned: summary.cloned,
            skipped: summary.skipped,
            skillsFound: totalSkills,
            missing: totalMissing,
            errors: totalErrors,
            reconciliation: {
              updated: report.updated.length,
              added: report.added.length,
              removed: report.removed.length,
              moved: report.moved.length,
              renamed: report.renamed.length,
              errors: report.errors.length,
            },
            applied: !!args.apply,
          })
        }

        process.exit(EXIT.OK)
      },
    }),
  },
})
