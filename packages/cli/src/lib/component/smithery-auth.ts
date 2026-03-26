import { CliError, err, ok, type Result } from '@agents/core/types'

const SMITHERY_API_BASE = 'https://registry.smithery.ai/api/v1'

export interface SmitheryAuth {
  readonly apiKey: string
}

/**
 * Resolve Smithery API key from available sources.
 *
 * Priority:
 * 1. Explicit `opts.apiKey` parameter
 * 2. `SMITHERY_API_KEY` environment variable
 * 3. Error (no interactive login in MVP)
 */
export function resolveSmitheryAuth(opts?: { apiKey?: string }): Result<SmitheryAuth> {
  if (opts?.apiKey) {
    return ok({ apiKey: opts.apiKey })
  }

  const envKey = process.env.SMITHERY_API_KEY
  if (envKey) {
    return ok({ apiKey: envKey })
  }

  return err(
    new CliError(
      'No Smithery API key found',
      'E_AUTH_REQUIRED',
      'Set SMITHERY_API_KEY environment variable or pass --api-key'
    )
  )
}

/**
 * Validate an API key against Smithery's API.
 *
 * Makes a lightweight authenticated request to check if the key is valid.
 * Returns true if the API responds with 200, false for 401/403.
 */
export async function validateSmitheryApiKey(
  apiKey: string,
  baseUrl?: string
): Promise<Result<boolean>> {
  const url = baseUrl ?? SMITHERY_API_BASE

  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 5_000)

    let response: Response
    try {
      response = await fetch(`${url}/servers?pageSize=1`, {
        headers: { Authorization: `Bearer ${apiKey}` },
        signal: controller.signal,
      })
    } finally {
      clearTimeout(timer)
    }

    if (response.status === 401 || response.status === 403) {
      return ok(false)
    }

    if (!response.ok) {
      return err(
        new CliError(
          `Smithery API returned HTTP ${response.status}`,
          'E_API_ERROR',
          'The Smithery API may be temporarily unavailable'
        )
      )
    }

    return ok(true)
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === 'AbortError') {
      return err(
        new CliError('Smithery API request timed out', 'E_TIMEOUT', 'Check your network connection')
      )
    }
    return err(
      new CliError(
        'Failed to validate Smithery API key',
        'E_NETWORK',
        cause instanceof Error ? cause.message : String(cause)
      )
    )
  }
}
