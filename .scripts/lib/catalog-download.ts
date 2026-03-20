/**
 * Catalog download orchestrator.
 *
 * Composes git.ts, source-parser.ts, and skill-discovery.ts to replace
 * the npx-skills shell-out in the analyze pipeline.
 */

import {
  detectGitProtocol,
  type GitProtocol,
  getOwnerRepo,
  parseSource,
  resolveCloneUrl,
} from './source-parser'
import { CliError, err, ok, type Result } from './types'

/** Well-known subdirectory prefixes where skills may live in a repo. */
export const SKILL_LOOKUP_DIRS = ['', 'skills/', 'context/skills/', '.claude/skills/']

/** Validated catalog source with resolved clone URL. */
export interface CatalogSource {
  ownerRepo: string
  cloneUrl: string
  ref?: string
  subpath?: string
  skillFilter?: string
}

/**
 * Validate a catalog source string. Accepts:
 * - `owner/repo` — standard entry
 * - `owner/repo#ref` — pinned to branch/tag
 * - `github.com/owner/repo/tree/ref/path` — pinned tree URL
 *
 * Rejects local paths, SSH raw URLs, non-GitHub sources.
 * Resolves clone URL using the detected git protocol (SSH/HTTPS).
 */
export function validateCatalogSource(
  source: string,
  protocol?: GitProtocol
): Result<CatalogSource> {
  const parsed = parseSource(source)
  if (!parsed.ok) return parsed as Result<never>

  // Must be a GitHub source
  if (parsed.value.type !== 'github') {
    return err(
      new CliError(
        `Catalog source must be GitHub (owner/repo or tree URL), got type "${parsed.value.type}": ${source}`,
        'E_NOT_GITHUB',
        'Supported: owner/repo, owner/repo#ref, github.com/o/r/tree/branch/path'
      )
    )
  }

  const ownerRepo = getOwnerRepo(parsed.value)
  if (!ownerRepo) {
    return err(
      new CliError(
        `Could not extract owner/repo from: ${source}`,
        'E_NOT_GITHUB',
        'Expected format: owner/repo'
      )
    )
  }

  const proto = protocol ?? detectGitProtocol()
  return ok({
    ownerRepo,
    cloneUrl: resolveCloneUrl(ownerRepo, proto),
    ref: parsed.value.ref,
    subpath: parsed.value.subpath,
    skillFilter: parsed.value.skillFilter,
  })
}
