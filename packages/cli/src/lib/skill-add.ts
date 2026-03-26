/**
 * Skill installation orchestrator.
 *
 * Handles the full workflow of adding a skill from any supported source:
 *
 * 1. Parse the source string (local path, GitHub shorthand, URL, etc.)
 * 2. Clone the repository (if remote) into a temp directory
 * 3. Discover SKILL.md files in the source
 * 4. Filter to requested skill(s)
 * 5. Detect installed agents and determine target directories
 * 6. Copy skill to canonical `content/skills/<name>/` directory
 * 7. Create symlinks from each agent's skills dir to the canonical copy
 * 8. Update the skills lockfile
 *
 * The public `addSkill` function never throws -- all errors are returned
 * as structured `AddResult` objects.
 */

import { existsSync } from 'node:fs'
import { cp, mkdir, readdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { CliError, err, ok, type Result } from '@agents/core/types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AddOptions {
  /** Working directory (project root). Defaults to cwd. */
  cwd?: string
  /** Agents to install for. If empty, auto-detects installed agents. */
  agents?: string[]
  /** Copy files instead of symlinking. */
  copy?: boolean
  /** Skip confirmation prompts. */
  yes?: boolean
  /** JSON output mode. */
  json?: boolean
  /** Quiet mode. */
  quiet?: boolean
}

export interface InstalledEntry {
  /** Skill name (from frontmatter). */
  name: string
  /** Source string that was used. */
  source: string
  /** Canonical install path (content/skills/<name>). */
  canonicalPath: string
  /** Agent directories where symlinks were created. */
  agentLinks: string[]
}

export interface AddResult {
  /** Whether the operation completed successfully. */
  ok: boolean
  /** Skills that were successfully installed. */
  installed: InstalledEntry[]
  /** Error that caused the operation to fail. */
  error?: CliError
  /** Non-fatal warnings collected during the operation. */
  warnings: string[]
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Install one or more skills from a source string.
 *
 * Never throws -- all errors are captured in the returned `AddResult`.
 */
export async function addSkill(source: string, opts: AddOptions = {}): Promise<AddResult> {
  const warnings: string[] = []
  const installed: InstalledEntry[] = []
  const cwd = opts.cwd ?? process.cwd()

  // Step 1: Parse the source
  const { parseSource } = await import('@agents/core/source-parser')
  const parseResult = parseSource(source)
  if (!parseResult.ok) {
    return { ok: false, installed, error: parseResult.error, warnings }
  }
  const parsed = parseResult.value

  // Step 2: Resolve the source to a local directory
  let searchDir: string
  let cleanup: (() => Promise<void>) | undefined

  if (parsed.type === 'local') {
    const localPath = resolve(cwd, parsed.localPath ?? source)
    if (!existsSync(localPath)) {
      return {
        ok: false,
        installed,
        error: new CliError(
          `Local path does not exist: ${localPath}`,
          'E_LOCAL_NOT_FOUND',
          'Verify the path and try again'
        ),
        warnings,
      }
    }
    searchDir = localPath
  } else {
    // Remote source -- clone
    const { cloneRepo } = await import('@agents/core/git')
    // biome-ignore lint/style/noNonNullAssertion: url is guaranteed set for non-local parsed sources
    const cloneResult = await cloneRepo(parsed.url!, parsed.ref)
    if (!cloneResult.ok) {
      return { ok: false, installed, error: cloneResult.error, warnings }
    }
    searchDir = cloneResult.value.tempDir
    cleanup = cloneResult.value.cleanup
  }

  try {
    // Step 3: Discover skills in the source
    const { discoverSkills, filterSkills } = await import('./skill-discovery')
    const discoverResult = await discoverSkills(searchDir, parsed.subpath)
    if (!discoverResult.ok) {
      return { ok: false, installed, error: discoverResult.error, warnings }
    }

    let skills = discoverResult.value
    if (skills.length === 0) {
      return {
        ok: false,
        installed,
        error: new CliError(
          `No SKILL.md files found in source: ${source}`,
          'E_NO_SKILLS',
          parsed.subpath
            ? `Check that the subpath "${parsed.subpath}" contains SKILL.md files`
            : 'The source directory does not contain any valid SKILL.md files'
        ),
        warnings,
      }
    }

    // Step 4: Filter by skill name if specified
    if (parsed.skillFilter) {
      skills = filterSkills(skills, [parsed.skillFilter])
      if (skills.length === 0) {
        return {
          ok: false,
          installed,
          error: new CliError(
            `Skill "${parsed.skillFilter}" not found in source: ${source}`,
            'E_SKILL_NOT_FOUND',
            `Available skills: ${discoverResult.value.map((s) => s.name).join(', ')}`
          ),
          warnings,
        }
      }
    }

    // Step 5: Detect target agents
    const { detectInstalledAgents, getAgentBaseDir } = await import('./agents')
    let targetAgents = opts.agents ?? []
    if (targetAgents.length === 0) {
      targetAgents = await detectInstalledAgents()
      if (targetAgents.length === 0) {
        warnings.push('No agents detected on this machine. Skill installed to canonical path only.')
      }
    }

    // Step 6 & 7: Install each skill
    const canonicalBase = join(cwd, 'content', 'skills')

    for (const skill of skills) {
      const skillName = skill.name
      const canonicalDir = join(canonicalBase, skillName)
      const skillSourceDir = join(skill.path, '..')

      // Copy the skill directory to the canonical location
      await mkdir(canonicalDir, { recursive: true })
      const entries = await readdir(skillSourceDir, { withFileTypes: true })
      for (const entry of entries) {
        const srcPath = join(skillSourceDir, entry.name)
        const destPath = join(canonicalDir, entry.name)
        await cp(srcPath, destPath, { recursive: true, force: true })
      }

      // Create symlinks from each agent's skills dir
      const agentLinks: string[] = []
      const { createSymlink } = await import('@agents/core/symlink')

      for (const agentName of targetAgents) {
        const baseDirResult = getAgentBaseDir(
          agentName as Parameters<typeof getAgentBaseDir>[0],
          false,
          cwd
        )
        if (!baseDirResult.ok) {
          warnings.push(
            `Could not resolve skills dir for agent "${agentName}": ${baseDirResult.error.message}`
          )
          continue
        }

        const agentSkillDir = join(baseDirResult.value, skillName)

        if (opts.copy) {
          // Copy mode: duplicate to agent dir too
          await mkdir(agentSkillDir, { recursive: true })
          const copyEntries = await readdir(canonicalDir, {
            withFileTypes: true,
          })
          for (const entry of copyEntries) {
            await cp(join(canonicalDir, entry.name), join(agentSkillDir, entry.name), {
              recursive: true,
              force: true,
            })
          }
        } else {
          // Symlink mode (default)
          try {
            await createSymlink(canonicalDir, agentSkillDir)
          } catch (e) {
            const msg = e instanceof Error ? e.message : String(e)
            warnings.push(`Failed to create symlink for agent "${agentName}": ${msg}`)
            continue
          }
        }

        agentLinks.push(agentSkillDir)
      }

      installed.push({
        name: skillName,
        source,
        canonicalPath: canonicalDir,
        agentLinks,
      })
    }

    // Step 8: Update the lockfile
    const lockResult = await updateLockfile(cwd, source, parsed.type, installed)
    if (!lockResult.ok) {
      warnings.push(`Failed to update lockfile: ${lockResult.error.message}`)
    }

    return { ok: true, installed, warnings }
  } finally {
    if (cleanup) {
      await cleanup()
    }
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Update the skills lockfile with newly installed skills.
 */
async function updateLockfile(
  cwd: string,
  source: string,
  sourceType: string,
  installed: InstalledEntry[]
): Promise<Result<void>> {
  const lockfilePath = join(cwd, 'skills-lock.json')
  const { computeHash } = await import('@agents/core/hash')

  // Read existing lockfile or create a fresh one
  let lockData: {
    version: 1
    skills: Record<string, { source: string; sourceType: string; computedHash: string }>
  }

  if (existsSync(lockfilePath)) {
    const { readText } = await import('@agents/core/runtime')
    try {
      const raw = await readText(lockfilePath)
      lockData = JSON.parse(raw)
    } catch {
      lockData = { version: 1, skills: {} }
    }
  } else {
    lockData = { version: 1, skills: {} }
  }

  // Add entries for each installed skill
  for (const entry of installed) {
    const hash = await computeHash(entry.canonicalPath)
    lockData.skills[entry.name] = {
      source,
      sourceType,
      computedHash: hash,
    }
  }

  // Write the lockfile
  const { writeText } = await import('@agents/core/runtime')
  try {
    await writeText(lockfilePath, `${JSON.stringify(lockData, null, 2)}\n`)
    return ok(undefined)
  } catch (e) {
    return err(
      new CliError(
        `Failed to write lockfile: ${lockfilePath}`,
        'E_WRITE_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}
