/**
 * Git operations wrapper using simple-git.
 *
 * Provides safe clone, ls-remote, and raw git access with
 * Result-based error handling and automatic temp directory cleanup.
 */

import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { type SimpleGit, type SimpleGitOptions, simpleGit } from 'simple-git'
import { getClient, parseRepo } from './github'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export class GitCloneError extends CliError {
  constructor(
    message: string,
    readonly isTimeout: boolean = false,
    readonly isAuthError: boolean = false,
    hint?: string,
    cause?: unknown
  ) {
    super(message, 'E_GIT_CLONE', hint, cause)
  }
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CLONE_TIMEOUT_MS = 60_000
const TEMP_PREFIX = 'skill-clone-'

// ---------------------------------------------------------------------------
// Git factory
// ---------------------------------------------------------------------------

/**
 * Create a configured SimpleGit instance.
 *
 * @param baseDir - Working directory for git commands (defaults to cwd)
 * @param opts.timeout - Max block time in ms (defaults to 60s)
 * @param opts.signal - AbortSignal to cancel in-flight operations
 */
export function createGit(
  baseDir?: string,
  opts?: { timeout?: number; signal?: AbortSignal }
): SimpleGit {
  const config: Partial<SimpleGitOptions> = {
    baseDir: baseDir ?? process.cwd(),
    maxConcurrentProcesses: 4,
    timeout: { block: opts?.timeout ?? CLONE_TIMEOUT_MS },
  }
  const git = simpleGit(config)
  if (opts?.signal) {
    opts.signal.addEventListener('abort', () => git.clean('f', ['-d']))
  }
  return git
}

// ---------------------------------------------------------------------------
// Clone
// ---------------------------------------------------------------------------

/**
 * Shallow-clone a repository into a temporary directory.
 *
 * Returns a cleanup function that removes the temp directory.
 * On failure the temp directory is cleaned up automatically.
 */
export async function cloneRepo(
  url: string,
  ref?: string
): Promise<Result<{ tempDir: string; cleanup: () => Promise<void> }>> {
  const tempDir = await mkdtemp(join(tmpdir(), TEMP_PREFIX))
  const git = createGit(tmpdir())

  try {
    const cloneOpts = ['--depth', '1']
    if (ref) cloneOpts.push('--branch', ref)
    await git.clone(url, tempDir, cloneOpts)
    return ok({
      tempDir,
      cleanup: () => cleanupTempDir(tempDir),
    })
  } catch (e) {
    await rm(tempDir, { recursive: true, force: true })
    const msg = e instanceof Error ? e.message : String(e)

    if (msg.includes('Authentication failed') || msg.includes('could not read Username')) {
      return err(
        new GitCloneError(
          `Authentication failed for ${url}`,
          false,
          true,
          'Set GITHUB_TOKEN or run "gh auth login"'
        )
      )
    }
    if (msg.includes('timed out') || msg.includes('timeout')) {
      return err(
        new GitCloneError(
          `Clone timed out after ${CLONE_TIMEOUT_MS / 1000}s for ${url}`,
          true,
          false,
          'The repository may be too large or the network is slow'
        )
      )
    }
    return err(new GitCloneError(`Clone failed for ${url}`, false, false, msg))
  }
}

// ---------------------------------------------------------------------------
// Temp directory cleanup
// ---------------------------------------------------------------------------

/**
 * Safely remove a temporary directory.
 *
 * Refuses to delete anything outside the system tmpdir to prevent
 * accidental data loss.
 */
export async function cleanupTempDir(dir: string): Promise<void> {
  const resolvedDir = resolve(dir)
  const resolvedTmp = resolve(tmpdir())
  if (!resolvedDir.startsWith(resolvedTmp)) {
    throw new CliError(
      `Refusing to delete directory outside tmpdir: ${dir}`,
      'E_UNSAFE_CLEANUP',
      `Expected path under ${resolvedTmp}`
    )
  }
  await rm(dir, { recursive: true, force: true })
}

// ---------------------------------------------------------------------------
// ls-remote
// ---------------------------------------------------------------------------

/**
 * Resolve the commit SHA for a remote ref without cloning.
 *
 * @param repoUrl - Remote repository URL
 * @param ref - Optional tag or branch to resolve (defaults to HEAD)
 */
export async function lsRemote(repoUrl: string, ref?: string): Promise<Result<string>> {
  const git = createGit()
  try {
    const args = ref ? ['--tags', repoUrl, ref] : [repoUrl, 'HEAD']
    const output = await git.listRemote(args)
    const trimmed = output.trim()
    if (!trimmed) {
      return err(
        new CliError(
          `No refs found for ${repoUrl}${ref ? ` at ${ref}` : ''}`,
          'E_NO_REFS',
          ref
            ? `Tag "${ref}" may not exist. Check with: git ls-remote --tags ${repoUrl}`
            : 'Repository may be empty or inaccessible'
        )
      )
    }
    const sha = trimmed.split(/\s+/)[0]
    if (!sha) {
      return err(new CliError('Could not parse commit SHA from ls-remote output', 'E_PARSE_FAILED'))
    }
    return ok(sha)
  } catch (e) {
    return err(
      new CliError(
        `git ls-remote failed for ${repoUrl}`,
        'E_GIT_LS_REMOTE',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

// ---------------------------------------------------------------------------
// Raw git
// ---------------------------------------------------------------------------

/**
 * Execute an arbitrary git command and return its output.
 *
 * @param args - Arguments to pass to git (e.g. ['status', '--short'])
 * @param baseDir - Working directory for the command
 */
export async function gitRaw(args: string[], baseDir?: string): Promise<Result<string>> {
  const git = createGit(baseDir)
  try {
    const output = await git.raw(args)
    return ok(output)
  } catch (e) {
    return err(
      new CliError(`git ${args[0]} failed`, 'E_GIT_RAW', e instanceof Error ? e.message : String(e))
    )
  }
}

// ---------------------------------------------------------------------------
// GitHub tree API
// ---------------------------------------------------------------------------

/**
 * Fetch the tree SHA for a folder in a GitHub repository.
 *
 * Uses the GitHub Trees API to resolve the SHA of a subtree without
 * cloning. Returns null if the path is not found or the API call fails.
 *
 * @param ownerRepo - Repository in "owner/repo" format
 * @param skillPath - Path to the folder within the repository
 * @param branch - Branch or commit to inspect (defaults to HEAD)
 */
export async function fetchSkillFolderHash(
  ownerRepo: string,
  skillPath: string,
  branch = 'HEAD'
): Promise<string | null> {
  const client = await getClient()
  const { owner, repo } = parseRepo(ownerRepo)
  try {
    const response = await client.request('GET /repos/{owner}/{repo}/git/trees/{tree_sha}', {
      owner,
      repo,
      tree_sha: branch,
      recursive: '1',
    })
    const normalizedPath = skillPath.replace(/\/$/, '')
    const entry = response.data.tree.find(
      (item: { path?: string; type?: string }) =>
        item.path === normalizedPath && item.type === 'tree'
    )
    return entry?.sha ?? null
  } catch {
    return null
  }
}
