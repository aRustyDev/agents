/**
 * Source string parser for skill management.
 *
 * Parses various source formats (short form, tree URLs, SSH, local paths)
 * into a normalized ParsedSource structure.
 */
import * as v from 'valibot'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Types & schemas
// ---------------------------------------------------------------------------

export const SourceType = v.picklist(['github', 'gitlab', 'git', 'local', 'well-known', 'smithery'])
export type SourceType = v.InferOutput<typeof SourceType>

export const ParsedSource = v.object({
  type: SourceType,
  url: v.optional(v.string()),
  ref: v.optional(v.string()),
  subpath: v.optional(v.string()),
  skillFilter: v.optional(v.string()),
  localPath: v.optional(v.string()),
  namespace: v.optional(v.string()),
})
export type ParsedSource = v.InferOutput<typeof ParsedSource>

// ---------------------------------------------------------------------------
// Regex patterns
// ---------------------------------------------------------------------------

const SHORT_RE = /^([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+)(?:#([^:@]+))?(?::([^@]+))?(?:@(.+))?$/
const GITHUB_TREE_RE = /^(?:https?:\/\/)?github\.com\/([^/]+\/[^/]+)\/tree\/([^/]+)(?:\/(.+))?$/
const GITLAB_TREE_RE = /^(?:https?:\/\/)?gitlab\.com\/([^/]+\/[^/]+)\/-\/tree\/([^/]+)(?:\/(.+))?$/
const SSH_RE = /^git@[^:]+:.+\.git$/
const HTTPS_GIT_RE = /^https?:\/\/.+\.git$/
const SMITHERY_RE = /^smithery:\/\/([^/]+)\/([^/]+)$/
const LOCAL_RE = /^[./]/

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Parse a source string into a normalized ParsedSource.
 *
 * Supported formats:
 * - Short form: `owner/repo`, `owner/repo#ref`, `owner/repo#ref:subpath@skill`
 * - GitHub tree URL: `github.com/o/r/tree/branch/path`
 * - GitLab tree URL: `gitlab.com/o/r/-/tree/branch/path`
 * - SSH URL: `git@host:repo.git`
 * - HTTPS .git URL: `https://host/repo.git`
 * - Local path: `./path` or `../path` or `/absolute`
 * - Smithery URI: `smithery://namespace/slug`
 * - Well-known URL: any other `https://` or `http://` URL
 */
export function parseSource(source: string): Result<ParsedSource> {
  const trimmed = source.trim()
  if (!trimmed) {
    return err(
      new CliError('Empty source string', 'E_INVALID_SOURCE', 'Provide a non-empty source')
    )
  }

  // Local path
  if (LOCAL_RE.test(trimmed)) {
    return ok({ type: 'local' as const, localPath: trimmed })
  }

  // GitHub tree URL
  const ghTree = GITHUB_TREE_RE.exec(trimmed)
  if (ghTree) {
    return ok({
      type: 'github' as const,
      url: `https://github.com/${ghTree[1]}.git`,
      ref: ghTree[2],
      subpath: ghTree[3],
    })
  }

  // GitLab tree URL
  const glTree = GITLAB_TREE_RE.exec(trimmed)
  if (glTree) {
    return ok({
      type: 'gitlab' as const,
      url: `https://gitlab.com/${glTree[1]}.git`,
      ref: glTree[2],
      subpath: glTree[3],
    })
  }

  // SSH git URL
  if (SSH_RE.test(trimmed)) {
    return ok({ type: 'git' as const, url: trimmed })
  }

  // HTTPS .git URL
  if (HTTPS_GIT_RE.test(trimmed)) {
    return ok({ type: 'git' as const, url: trimmed })
  }

  // Short form: owner/repo#ref:subpath@skill
  const short = SHORT_RE.exec(trimmed)
  if (short) {
    const parsed: ParsedSource = {
      type: 'github',
      url: `https://github.com/${short[1]}.git`,
    }
    if (short[2]) parsed.ref = short[2]
    if (short[3]) {
      const subResult = sanitizeSubpath(short[3])
      if (!subResult.ok) return subResult
      parsed.subpath = subResult.value
    }
    if (short[4]) parsed.skillFilter = short[4]
    return ok(parsed)
  }

  // Smithery URI: smithery://namespace/slug
  const smithery = SMITHERY_RE.exec(trimmed)
  if (smithery) {
    return ok({
      type: 'smithery' as const,
      url: `https://smithery.ai/server/${smithery[1]}/${smithery[2]}`,
      namespace: smithery[1],
      subpath: smithery[2],
    })
  }

  // Well-known HTTPS URL (no .git suffix)
  if (trimmed.startsWith('https://') || trimmed.startsWith('http://')) {
    return ok({ type: 'well-known' as const, url: trimmed })
  }

  return err(
    new CliError(
      `Cannot parse source: "${trimmed}"`,
      'E_INVALID_SOURCE',
      'Expected owner/repo, ./local/path, or https:// URL'
    )
  )
}

/**
 * Extract the `owner/repo` slug from a parsed source's URL.
 * Returns null for local paths or URLs that don't match GitHub/GitLab patterns.
 */
export function getOwnerRepo(parsed: ParsedSource): string | null {
  if (!parsed.url) return null
  const match = parsed.url.match(/(?:github|gitlab)\.com\/([^/]+\/[^/]+?)(?:\.git)?$/)
  return match?.[1] ?? null
}

/**
 * Sanitize a subpath by rejecting `..` traversals and normalizing slashes.
 */
export function sanitizeSubpath(subpath: string): Result<string> {
  const segments = subpath.split('/')
  if (segments.some((s) => s === '..')) {
    return err(
      new CliError(
        `Subpath contains ".." traversal: "${subpath}"`,
        'E_UNSAFE_SUBPATH',
        'Subpaths must not contain ".." segments'
      )
    )
  }
  return ok(segments.filter(Boolean).join('/'))
}
