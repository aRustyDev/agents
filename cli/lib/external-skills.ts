/**
 * External skill dependency management.
 *
 * Provides the core business logic for the `skill deps` subcommand tree:
 * check, sync, issues, links, and status.
 *
 * External skills live in `context/skills/.external/` and are declared in
 * `sources.yaml` (hand-edited) with state tracked in `sources.lock.json`
 * (machine-managed).
 */

import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, relative } from 'node:path'
import yaml from 'js-yaml'
import * as v from 'valibot'
import { cloneRepo, gitRaw, lsRemote } from './git'
import { addComment, createIssue, type Issue, searchIssues } from './github'
import { formatHash, hashDirectory, lockKey } from './hash'
import { spawnSync } from './runtime'
import { type ExternalLockEntry, type ExternalSkillEntry, ExternalSourcesManifest } from './schemas'
import { checkSymlink, createSymlink } from './symlink'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type DriftStatus = 'current' | 'changed' | 'unavail' | 'new'

export interface CheckResult {
  skill: string
  source: string
  status: DriftStatus
  lastSynced?: string
  ref?: string
  upstreamCommit?: string
  lockCommit?: string
}

export interface StatusResult {
  skill: string
  source: string
  mode: 'passthrough' | 'derived'
  hash?: string
  symlink?: 'healthy' | 'broken' | '\u2014'
  issue?: string
}

// ---------------------------------------------------------------------------
// Manifest & lock I/O
// ---------------------------------------------------------------------------

/**
 * Read and validate `sources.yaml` from the external skills directory.
 */
export function readManifest(externalDir: string): Result<ExternalSourcesManifest> {
  const manifestPath = join(externalDir, 'sources.yaml')

  if (!existsSync(manifestPath)) {
    return err(
      new CliError(
        `External sources manifest not found: ${manifestPath}`,
        'E_MANIFEST_NOT_FOUND',
        'Create sources.yaml in context/skills/.external/'
      )
    )
  }

  let raw: string
  try {
    raw = readFileSync(manifestPath, 'utf-8')
  } catch (e) {
    return err(
      new CliError(`Failed to read manifest: ${manifestPath}`, 'E_READ_FAILED', undefined, e)
    )
  }

  let parsed: unknown
  try {
    parsed = yaml.load(raw)
  } catch (e) {
    return err(
      new CliError(
        `Invalid YAML in manifest: ${manifestPath}`,
        'E_INVALID_YAML',
        'Check the file for syntax errors',
        e
      )
    )
  }

  const result = v.safeParse(ExternalSourcesManifest, parsed)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new CliError(`Manifest validation failed: ${manifestPath}`, 'E_VALIDATION_FAILED', issues)
    )
  }

  return ok(result.output)
}

/**
 * Read `sources.lock.json` from the external skills directory.
 *
 * Returns an empty record if the file does not exist.
 */
export function readLock(externalDir: string): Record<string, ExternalLockEntry> {
  const lockPath = join(externalDir, 'sources.lock.json')
  if (!existsSync(lockPath)) return {}

  try {
    const raw = readFileSync(lockPath, 'utf-8')
    return JSON.parse(raw) as Record<string, ExternalLockEntry>
  } catch {
    return {}
  }
}

/**
 * Write `sources.lock.json` with 2-space indent and trailing newline.
 */
export function writeLock(externalDir: string, data: Record<string, ExternalLockEntry>): void {
  const lockPath = join(externalDir, 'sources.lock.json')
  mkdirSync(externalDir, { recursive: true })
  writeFileSync(lockPath, `${JSON.stringify(data, null, 2)}\n`, 'utf-8')
}

// ---------------------------------------------------------------------------
// Git helpers
// ---------------------------------------------------------------------------

/**
 * Run `git ls-remote` to resolve a remote ref to a commit SHA.
 *
 * Delegates to `lsRemote()` from `lib/git.ts` (simple-git).
 *
 * - If `ref` is provided: queries tags for that ref.
 * - If no `ref`: queries HEAD.
 *
 * @returns The commit SHA or an error.
 */
export async function gitLsRemote(repoUrl: string, ref?: string): Promise<Result<string>> {
  const result = await lsRemote(repoUrl, ref)

  if (!result.ok) {
    // Map error codes for backward compatibility: lsRemote already uses
    // E_GIT_LS_REMOTE, E_NO_REFS, and E_PARSE_FAILED which match the
    // codes this function previously returned.
    return result
  }

  return result
}

// ---------------------------------------------------------------------------
// Core operations
// ---------------------------------------------------------------------------

/**
 * Check upstream drift for all external skills.
 *
 * Compares the current remote commit SHA (via `git ls-remote`) against
 * the `upstream_commit` stored in the lock file.
 */
export async function checkDrift(externalDir: string, _skillsDir: string): Promise<CheckResult[]> {
  const manifestResult = readManifest(externalDir)
  if (!manifestResult.ok) return []

  const lock = readLock(externalDir)
  const results: CheckResult[] = []

  for (const [name, entry] of Object.entries(manifestResult.value.skills)) {
    const key = lockKey(entry.source, entry.skill)
    const lockEntry = lock[key]
    const repoUrl = `https://github.com/${entry.source}.git`

    const remoteResult = await gitLsRemote(repoUrl, entry.ref)

    if (!remoteResult.ok) {
      results.push({
        skill: name,
        source: entry.source,
        status: 'unavail',
        lastSynced: lockEntry?.last_synced,
        ref: entry.ref,
      })
      continue
    }

    const remoteCommit = remoteResult.value

    if (!lockEntry) {
      results.push({
        skill: name,
        source: entry.source,
        status: 'new',
        ref: entry.ref,
        upstreamCommit: remoteCommit,
      })
      continue
    }

    const status: DriftStatus = remoteCommit === lockEntry.upstream_commit ? 'current' : 'changed'

    results.push({
      skill: name,
      source: entry.source,
      status,
      lastSynced: lockEntry.last_synced,
      ref: entry.ref,
      upstreamCommit: remoteCommit,
      lockCommit: lockEntry.upstream_commit,
    })
  }

  return results
}

/**
 * Sync a single external skill from its upstream source.
 *
 * Downloads the skill into `.external/<source>/<skill>/` and cleans
 * up any `.claude/` or `.agents/` artifacts.
 */
export async function syncSkill(
  entry: ExternalSkillEntry & { name: string },
  externalDir: string,
  _skillsDir: string,
  _opts?: { force?: boolean }
): Promise<Result<void>> {
  const repoUrl = `https://github.com/${entry.source}.git`
  const destDir = join(externalDir, entry.source, entry.skill)

  if (entry.ref) {
    // Pinned ref: use cloneRepo with ref
    const cloneResult = await cloneRepo(repoUrl, entry.ref)
    if (!cloneResult.ok) {
      // Map GitCloneError to the E_CLONE_FAILED code callers expect
      return err(
        new CliError(
          `Failed to clone ${entry.source} at ref ${entry.ref}`,
          'E_CLONE_FAILED',
          cloneResult.error.hint
        )
      )
    }

    const { tempDir: clonedDir, cleanup } = cloneResult.value
    try {
      // Copy skill directory from cloned repo
      const skillSrc = join(clonedDir, entry.skill)
      if (!existsSync(skillSrc)) {
        // Try looking in .claude/skills/ as fallback
        const altSrc = join(clonedDir, '.claude', 'skills', entry.skill)
        if (existsSync(altSrc)) {
          copyDir(altSrc, destDir)
        } else {
          return err(
            new CliError(
              `Skill "${entry.skill}" not found in cloned repo`,
              'E_SKILL_NOT_FOUND',
              `Searched: ${skillSrc} and ${altSrc}`
            )
          )
        }
      } else {
        copyDir(skillSrc, destDir)
      }
    } finally {
      await cleanup()
    }
  } else {
    // Try npx skills first, fall back to cloneRepo
    // TODO(phase-5.3): Replace with addSkill() from lib/skill-add.ts when Phase 2 is complete
    const npxCheck = spawnSync(['which', 'npx'])
    const tempBase = join(tmpdir(), `skill-sync-${Date.now()}`)

    let synced = false

    if (npxCheck.exitCode === 0) {
      const npxDir = join(tempBase, 'npx')
      mkdirSync(npxDir, { recursive: true })

      const proc = spawnSync(
        ['npx', 'skills', 'add', '-y', '--copy', '--full-depth', `${entry.source}@${entry.skill}`],
        { cwd: npxDir }
      )

      if (proc.exitCode === 0) {
        const npxSkillDir = join(npxDir, '.claude', 'skills', entry.skill)
        if (existsSync(npxSkillDir)) {
          copyDir(npxSkillDir, destDir)
          synced = true
        }
      }

      // Clean up npx temp directory
      try {
        rmSync(tempBase, { recursive: true, force: true })
      } catch {
        // Best-effort cleanup
      }
    }

    if (!synced) {
      // Fallback: cloneRepo without ref (HEAD)
      const cloneResult = await cloneRepo(repoUrl)
      if (!cloneResult.ok) {
        return err(
          new CliError(`Failed to clone ${entry.source}`, 'E_CLONE_FAILED', cloneResult.error.hint)
        )
      }

      const { tempDir: clonedDir, cleanup } = cloneResult.value
      try {
        const skillSrc = join(clonedDir, entry.skill)
        const altSrc = join(clonedDir, '.claude', 'skills', entry.skill)

        if (existsSync(skillSrc)) {
          copyDir(skillSrc, destDir)
        } else if (existsSync(altSrc)) {
          copyDir(altSrc, destDir)
        } else {
          return err(
            new CliError(
              `Skill "${entry.skill}" not found in cloned repo`,
              'E_SKILL_NOT_FOUND',
              `Searched: ${skillSrc} and ${altSrc}`
            )
          )
        }
      } finally {
        await cleanup()
      }
    }
  }

  // Clean up artifacts that should not be in the snapshot
  for (const artifact of ['.claude', '.agents', '.git']) {
    const artifactPath = join(destDir, artifact)
    if (existsSync(artifactPath)) {
      rmSync(artifactPath, { recursive: true, force: true })
    }
  }

  return ok(undefined)
}

/**
 * Sync all external skills that have drifted (or all if `force` is true).
 *
 * Updates the lock file with new commit SHAs, snapshot hashes, and
 * last-synced timestamps.
 */
export async function syncAll(
  externalDir: string,
  skillsDir: string,
  opts?: { force?: boolean }
): Promise<{ synced: string[]; failed: string[] }> {
  const manifestResult = readManifest(externalDir)
  if (!manifestResult.ok) return { synced: [], failed: [] }

  const driftResults = await checkDrift(externalDir, skillsDir)
  const lock = readLock(externalDir)
  const synced: string[] = []
  const failed: string[] = []

  for (const [name, entry] of Object.entries(manifestResult.value.skills)) {
    const drift = driftResults.find((d) => d.skill === name)
    const needsSync = opts?.force || !drift || drift.status === 'changed' || drift.status === 'new'

    if (!needsSync) continue

    const result = await syncSkill({ ...entry, name }, externalDir, skillsDir, opts)

    if (result.ok) {
      synced.push(name)

      // Update lock entry
      const key = lockKey(entry.source, entry.skill)
      const snapshotDir = join(externalDir, entry.source, entry.skill)
      let snapshotHash = ''
      try {
        const hex = await hashDirectory(snapshotDir)
        snapshotHash = formatHash(hex)
      } catch {
        // Directory might not exist if sync failed partially
      }

      // Get upstream commit
      const repoUrl = `https://github.com/${entry.source}.git`
      const remoteResult = await gitLsRemote(repoUrl, entry.ref)
      const upstreamCommit = remoteResult.ok ? remoteResult.value : ''

      lock[key] = {
        upstream_commit: upstreamCommit,
        snapshot_hash: snapshotHash,
        last_synced: new Date().toISOString(),
        ...(lock[key]?.last_reviewed_commit
          ? { last_reviewed_commit: lock[key]?.last_reviewed_commit }
          : {}),
        ...(lock[key]?.drift_issue ? { drift_issue: lock[key]?.drift_issue } : {}),
      }
    } else {
      failed.push(name)
    }
  }

  writeLock(externalDir, lock)
  return { synced, failed }
}

/**
 * Create or update GitHub issues for drift detected in derived skills.
 *
 * Groups drifted external skills by the local skills they feed (`derived_by`),
 * then upserts issues with checklist items and diff snippets.
 */
export async function createDriftIssues(
  externalDir: string,
  skillsDir: string,
  repo: string,
  opts?: { dryRun?: boolean }
): Promise<{ created: number; updated: number }> {
  const manifestResult = readManifest(externalDir)
  if (!manifestResult.ok) return { created: 0, updated: 0 }

  const lock = readLock(externalDir)
  let created = 0
  let updated = 0

  // Group drifted skills by local derived skill
  const driftByLocal = new Map<
    string,
    { name: string; entry: ExternalSkillEntry; diff: string }[]
  >()

  for (const [name, entry] of Object.entries(manifestResult.value.skills)) {
    if (!entry.derived_by?.length) continue

    // Check if there are uncommitted changes in the snapshot
    const snapshotPath = join(externalDir, entry.source, entry.skill)
    if (!existsSync(snapshotPath)) continue

    const diffResult = await gitRaw(['diff', 'HEAD', '--', snapshotPath])
    const diff = diffResult.ok ? diffResult.value.trim() : ''
    if (!diff) continue

    for (const localSkill of entry.derived_by) {
      const localSkillDir = join(skillsDir, localSkill)
      if (!existsSync(localSkillDir)) {
        console.error(`[warn] derived_by target "${localSkill}" does not exist at ${localSkillDir}`)
        continue
      }

      if (!driftByLocal.has(localSkill)) {
        driftByLocal.set(localSkill, [])
      }
      driftByLocal.get(localSkill)?.push({ name, entry, diff })
    }
  }

  // Upsert issues per local skill
  for (const [localSkill, driftedEntries] of driftByLocal) {
    if (opts?.dryRun) {
      console.log(
        `[dry-run] Would create/update issue for "${localSkill}" with ${driftedEntries.length} drifted source(s)`
      )
      created++
      continue
    }

    const issueTitle = `[SKILL DRIFT] upstream changes (${localSkill})`

    // Search for existing open issue
    let existingIssue: Issue | undefined
    try {
      const issues = await searchIssues(repo, `"${issueTitle}" is:open`)
      existingIssue = issues.find((i) => i.title === issueTitle)
    } catch {
      // Search failed, treat as no existing issue
    }

    // Build checklist items
    const checklist = driftedEntries
      .map((d) => {
        const key = lockKey(d.entry.source, d.entry.skill)
        const lockEntry = lock[key]
        const reviewed = lockEntry?.last_reviewed_commit ?? 'unknown'
        return `- [ ] \`${d.entry.source}@${d.entry.skill}\` changed (detected ${new Date().toISOString().slice(0, 10)}, last reviewed at commit \`${reviewed}\`)`
      })
      .join('\n')

    const details = driftedEntries
      .map((d) => {
        return `<details><summary>Diff: ${d.entry.source}@${d.entry.skill}</summary>\n\n\`\`\`diff\n${d.diff.slice(0, 5000)}\n\`\`\`\n\n</details>`
      })
      .join('\n\n')

    if (existingIssue) {
      // Append comment with new drift info
      const commentBody = `## Additional Drift Detected\n\n${checklist}\n\n${details}`
      await addComment(repo, existingIssue.number, commentBody)
      updated++

      // Record issue number in lock for each drifted entry
      for (const d of driftedEntries) {
        const key = lockKey(d.entry.source, d.entry.skill)
        if (lock[key]) {
          lock[key].drift_issue = existingIssue.number
        }
      }
    } else {
      // Create new issue
      const body = `## Upstream Changes Affecting \`${localSkill}\`\n\n${checklist}\n\n${details}\n\n## Local Skill\n\`context/skills/${localSkill}/SKILL.md\`\n\n## Action Required\nReview upstream changes and decide whether to incorporate into local skill.`

      const issueResult = await createIssue(repo, {
        title: issueTitle,
        body,
        labels: ['skills', 'review'],
      })

      if (issueResult.ok) {
        created++
        // Record issue number in lock for each drifted entry
        for (const d of driftedEntries) {
          const key = lockKey(d.entry.source, d.entry.skill)
          if (lock[key]) {
            lock[key].drift_issue = issueResult.value.number
          }
        }
      }
    }
  }

  // Persist updated lock with drift_issue references
  if (!opts?.dryRun) {
    writeLock(externalDir, lock)
  }

  return { created, updated }
}

/**
 * Create or refresh passthrough symlinks for all passthrough entries.
 *
 * For each passthrough skill, creates a symlink from
 * `context/skills/<name>` to `.external/<source>/<skill>/`.
 */
export async function refreshLinks(
  externalDir: string,
  skillsDir: string
): Promise<{
  created: string[]
  updated: string[]
  skipped: string[]
  broken: string[]
}> {
  const manifestResult = readManifest(externalDir)
  if (!manifestResult.ok) {
    return { created: [], updated: [], skipped: [], broken: [] }
  }

  const created: string[] = []
  const updatedLinks: string[] = []
  const skipped: string[] = []
  const broken: string[] = []

  for (const [name, entry] of Object.entries(manifestResult.value.skills)) {
    if (!entry.passthrough) {
      skipped.push(name)
      continue
    }

    const target = join(externalDir, entry.source, entry.skill)
    const link = join(skillsDir, name)

    // Check if target exists
    if (!existsSync(target)) {
      broken.push(name)
      continue
    }

    // Compute relative target for the symlink
    const relTarget = relative(skillsDir, target)

    // Check if symlink already exists and is correct
    try {
      const status = await checkSymlink(link)
      if (status.valid && status.target === relTarget) {
        skipped.push(name)
        continue
      }
      // Exists but wrong target or broken -- recreate
      await createSymlink(relTarget, link)
      updatedLinks.push(name)
    } catch {
      // Symlink doesn't exist or path is not a symlink -- create new
      try {
        await createSymlink(relTarget, link)
        created.push(name)
      } catch (_e) {
        // Path exists but is not a symlink (real directory)
        broken.push(name)
      }
    }
  }

  return { created, updated: updatedLinks, skipped, broken }
}

/**
 * Get combined status for all external skills.
 *
 * Merges data from the manifest, lock file, symlink health, and
 * issue state into a single table view.
 */
export async function getStatus(externalDir: string, skillsDir: string): Promise<StatusResult[]> {
  const manifestResult = readManifest(externalDir)
  if (!manifestResult.ok) return []

  const lock = readLock(externalDir)
  const results: StatusResult[] = []

  for (const [name, entry] of Object.entries(manifestResult.value.skills)) {
    const key = lockKey(entry.source, entry.skill)
    const lockEntry = lock[key]
    const mode = entry.passthrough ? 'passthrough' : 'derived'

    // Compute snapshot hash
    let hash: string | undefined
    const snapshotDir = join(externalDir, entry.source, entry.skill)
    if (existsSync(snapshotDir)) {
      try {
        const hex = await hashDirectory(snapshotDir)
        hash = `${hex.slice(0, 8)}..`
      } catch {
        // Ignore hash errors
      }
    }

    // Check symlink health for passthrough entries
    let symlinkStatus: 'healthy' | 'broken' | '\u2014' = '\u2014'
    if (entry.passthrough) {
      const linkPath = join(skillsDir, name)
      try {
        const status = await checkSymlink(linkPath)
        symlinkStatus = status.valid ? 'healthy' : 'broken'
      } catch {
        symlinkStatus = 'broken'
      }
    }

    // Issue info
    let issue = '\u2014'
    if (lockEntry?.drift_issue) {
      issue = `#${lockEntry.drift_issue} open`
    }

    results.push({
      skill: name,
      source: entry.source,
      mode,
      hash,
      symlink: symlinkStatus,
      issue,
    })
  }

  return results
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Recursively copy a directory tree, creating the destination if needed.
 */
function copyDir(src: string, dest: string): void {
  mkdirSync(dest, { recursive: true })

  const entries = readdirSync(src, { withFileTypes: true })
  for (const entry of entries) {
    const srcPath = join(src, entry.name)
    const destPath = join(dest, entry.name)

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath)
    } else {
      const content = readFileSync(srcPath)
      writeFileSync(destPath, content)
    }
  }
}
