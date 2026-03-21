/**
 * Git status API route.
 *
 * Shells out to `git status --porcelain` scoped to the graphs data directory
 * to report whether graph files have uncommitted changes. This lets the UI
 * show a dirty/clean indicator.
 *
 * Uses the runtime-agnostic `spawnAsync` helper so this works on both
 * Bun and Node.js.
 */

import { spawnAsync } from '../../../lib/runtime'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape returned by GET /api/git/status */
interface GitStatusResponse {
  readonly status: 'clean' | 'dirty' | 'unknown'
  readonly files?: string[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function jsonResponse(data: unknown, status = 200): Response {
  return Response.json(data, { status })
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

/**
 * Handle requests to `/api/git/status`.
 *
 * Runs `git status --porcelain` scoped to the graphs directory. Returns:
 * - `{ status: 'clean' }` when there are no uncommitted changes
 * - `{ status: 'dirty', files: [...] }` when there are changes
 * - `{ status: 'unknown' }` if git is unavailable or the command fails
 *
 * @param req - The incoming HTTP request.
 * @param pathname - The URL pathname.
 * @param graphsDir - Absolute path to the graphs data directory.
 * @returns A Response, or null if the route does not match.
 */
export async function handleGitRoute(
  req: Request,
  pathname: string,
  graphsDir: string
): Promise<Response | null> {
  if (pathname !== '/api/git/status' || req.method !== 'GET') return null

  try {
    const result = await spawnAsync(['git', 'status', '--porcelain', graphsDir], {
      cwd: graphsDir,
    })

    if (!result.success) {
      const response: GitStatusResponse = { status: 'unknown' }
      return jsonResponse(response)
    }

    const lines = result.stdout.trim().split('\n').filter(Boolean)

    if (lines.length === 0) {
      const response: GitStatusResponse = { status: 'clean' }
      return jsonResponse(response)
    }

    // Extract file paths from porcelain output (format: "XY filename")
    const files = lines.map((line) => line.slice(3).trim())
    const response: GitStatusResponse = { status: 'dirty', files }
    return jsonResponse(response)
  } catch {
    const response: GitStatusResponse = { status: 'unknown' }
    return jsonResponse(response)
  }
}
