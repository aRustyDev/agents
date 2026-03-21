/**
 * Smithery publish + deployment polling.
 *
 * Two publish modes:
 *   1. External URL -- registers a remote MCP server endpoint
 *   2. Pre-built bundle -- uploads manifest.json + JS artefact
 *
 * Both paths return a deploymentId that is polled until the deployment
 * reaches a terminal status (SUCCESS, FAILURE, CANCELLED, etc.) or
 * the configured timeout elapses.
 */

import { CliError, err, ok, type Result } from '../types'
import type { PublishResult } from './types'

const SMITHERY_API_BASE = 'https://registry.smithery.ai/api/v1'
const POLL_INTERVAL_MS = 2_000
const POLL_TIMEOUT_MS = 5 * 60 * 1_000 // 5 minutes

// Re-export for external consumers that only need the result shape.
export type { PublishResult }

export interface SmitheryPublishOptions {
  /** Qualified name: "namespace/server-name" */
  readonly qualifiedName: string
  /** Smithery API key */
  readonly apiKey: string
  /** External MCP server URL (for URL-based publish) */
  readonly externalUrl?: string
  /** JSON Schema for server configuration */
  readonly configSchema?: Record<string, unknown>
  /** Pre-built bundle directory (for bundle-based publish) */
  readonly bundleDir?: string
  /** Just validate, don't upload */
  readonly dryRun?: boolean
  /** Override API base URL */
  readonly baseUrl?: string
}

/**
 * Publish an MCP server to Smithery.
 *
 * Two modes:
 * 1. External URL: registers a server URL with optional config schema
 *    (POST /servers/{name}/releases with type: "external")
 * 2. Pre-built bundle: uploads manifest.json + JS bundle
 *    (POST /servers/{name}/releases with multipart form data)
 *
 * In both cases, returns a deploymentId that can be polled for status.
 */
export async function publishToSmithery(
  opts: SmitheryPublishOptions
): Promise<Result<PublishResult>> {
  const base = opts.baseUrl ?? SMITHERY_API_BASE

  // Validate qualifiedName format
  if (!opts.qualifiedName.includes('/')) {
    return err(
      new CliError(
        `Invalid qualified name: "${opts.qualifiedName}"`,
        'E_INVALID_NAME',
        'Expected format: namespace/server-name'
      )
    )
  }

  // Dry run: validate only
  if (opts.dryRun) {
    if (!opts.externalUrl && !opts.bundleDir) {
      return err(
        new CliError(
          'Either --url or --bundle-dir is required',
          'E_MISSING_SOURCE',
          'Provide an external URL or a pre-built bundle directory'
        )
      )
    }
    return ok({
      ok: true,
      status: 'published' as const,
      warnings: ['Dry run -- no changes made'],
    })
  }

  // Mode 1: External URL
  if (opts.externalUrl) {
    return publishExternalUrl(base, opts)
  }

  // Mode 2: Pre-built bundle
  if (opts.bundleDir) {
    return publishBundle(base, opts)
  }

  return err(new CliError('Either externalUrl or bundleDir must be provided', 'E_MISSING_SOURCE'))
}

async function publishExternalUrl(
  base: string,
  opts: SmitheryPublishOptions
): Promise<Result<PublishResult>> {
  const payload = {
    type: 'external',
    upstreamUrl: opts.externalUrl,
    ...(opts.configSchema ? { configSchema: opts.configSchema } : {}),
  }

  try {
    const response = await fetch(
      `${base}/servers/${encodeURIComponent(opts.qualifiedName)}/releases`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${opts.apiKey}`,
        },
        body: JSON.stringify({ payload: JSON.stringify(payload) }),
      }
    )

    if (response.status === 404) {
      return err(
        new CliError(
          `Server "${opts.qualifiedName}" not found on Smithery`,
          'E_SERVER_NOT_FOUND',
          'Create the server first on smithery.ai, or check the qualified name'
        )
      )
    }

    if (response.status === 401 || response.status === 403) {
      return err(
        new CliError('Authentication failed', 'E_AUTH_FAILED', 'Check your SMITHERY_API_KEY')
      )
    }

    if (response.status === 429) {
      return err(
        new CliError('Rate limited by Smithery', 'E_RATE_LIMITED', 'Wait a moment and try again')
      )
    }

    if (!response.ok) {
      const text = await response.text().catch(() => '')
      return err(
        new CliError(
          `Smithery API error: HTTP ${response.status}`,
          'E_API_ERROR',
          text || undefined
        )
      )
    }

    const body = (await response.json()) as { deploymentId?: string }
    const deploymentId = body.deploymentId

    if (!deploymentId) {
      return ok({
        ok: true,
        registryUrl: `https://smithery.ai/server/${opts.qualifiedName}`,
        status: 'published' as const,
        warnings: [],
      })
    }

    // Poll for completion
    return pollDeployment(opts.qualifiedName, deploymentId, opts.apiKey, {
      baseUrl: base,
    })
  } catch (cause) {
    return err(
      new CliError(
        'Failed to publish to Smithery',
        'E_PUBLISH_FAILED',
        cause instanceof Error ? cause.message : String(cause)
      )
    )
  }
}

async function publishBundle(
  base: string,
  opts: SmitheryPublishOptions
): Promise<Result<PublishResult>> {
  const { existsSync } = await import('node:fs')
  const { readFile } = await import('node:fs/promises')
  const { join } = await import('node:path')

  const bundleDir = opts.bundleDir!
  const manifestPath = join(bundleDir, 'manifest.json')

  if (!existsSync(manifestPath)) {
    return err(
      new CliError(
        `Missing manifest.json in bundle directory: ${bundleDir}`,
        'E_MISSING_MANIFEST',
        'The bundle directory must contain a manifest.json file'
      )
    )
  }

  let manifest: Record<string, unknown>
  try {
    const raw = await readFile(manifestPath, 'utf-8')
    manifest = JSON.parse(raw) as Record<string, unknown>
  } catch {
    return err(
      new CliError(
        'Failed to read manifest.json',
        'E_INVALID_MANIFEST',
        'Ensure manifest.json is valid JSON'
      )
    )
  }

  // Build multipart form data
  const formData = new FormData()
  formData.append('payload', JSON.stringify(manifest.payload ?? manifest))

  // Look for module file referenced in artefacts
  const artifacts = manifest.artifacts as Record<string, string> | undefined
  if (artifacts?.module) {
    const modulePath = join(bundleDir, artifacts.module)
    if (existsSync(modulePath)) {
      const moduleContent = await readFile(modulePath)
      formData.append('module', new Blob([moduleContent]), artifacts.module)
    }
  }

  try {
    const response = await fetch(
      `${base}/servers/${encodeURIComponent(opts.qualifiedName)}/releases`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${opts.apiKey}` },
        body: formData,
      }
    )

    if (response.status === 404) {
      return err(new CliError(`Server "${opts.qualifiedName}" not found`, 'E_SERVER_NOT_FOUND'))
    }

    if (response.status === 401 || response.status === 403) {
      return err(new CliError('Authentication failed', 'E_AUTH_FAILED'))
    }

    if (!response.ok) {
      return err(new CliError(`Smithery API error: HTTP ${response.status}`, 'E_API_ERROR'))
    }

    const body = (await response.json()) as { deploymentId?: string }
    if (body.deploymentId) {
      return pollDeployment(opts.qualifiedName, body.deploymentId, opts.apiKey, {
        baseUrl: base,
      })
    }

    return ok({
      ok: true,
      registryUrl: `https://smithery.ai/server/${opts.qualifiedName}`,
      status: 'published' as const,
      warnings: [],
    })
  } catch (cause) {
    return err(
      new CliError(
        'Failed to upload bundle to Smithery',
        'E_UPLOAD_FAILED',
        cause instanceof Error ? cause.message : String(cause)
      )
    )
  }
}

/**
 * Poll Smithery deployment status until a terminal state is reached.
 *
 * Terminal states: SUCCESS, FAILURE, FAILURE_SCAN, INTERNAL_ERROR, CANCELLED
 * Non-terminal: PENDING, IN_PROGRESS
 */
export async function pollDeployment(
  qualifiedName: string,
  deploymentId: string,
  apiKey: string,
  opts?: { baseUrl?: string; timeoutMs?: number; intervalMs?: number }
): Promise<Result<PublishResult>> {
  const base = opts?.baseUrl ?? SMITHERY_API_BASE
  const timeout = opts?.timeoutMs ?? POLL_TIMEOUT_MS
  const interval = opts?.intervalMs ?? POLL_INTERVAL_MS
  const start = Date.now()

  while (Date.now() - start < timeout) {
    try {
      const response = await fetch(
        `${base}/servers/${encodeURIComponent(qualifiedName)}/releases/${deploymentId}`,
        { headers: { Authorization: `Bearer ${apiKey}` } }
      )

      if (!response.ok) {
        return err(
          new CliError(`Failed to poll deployment: HTTP ${response.status}`, 'E_POLL_FAILED')
        )
      }

      const body = (await response.json()) as {
        status: string
        mcpUrl?: string
        logs?: Array<{ stage: string; level: string; message: string }>
      }

      switch (body.status) {
        case 'SUCCESS':
          return ok({
            ok: true,
            registryUrl: body.mcpUrl ?? `https://smithery.ai/server/${qualifiedName}`,
            releaseId: deploymentId,
            status: 'published' as const,
            warnings: [],
          })

        case 'FAILURE':
        case 'FAILURE_SCAN':
        case 'INTERNAL_ERROR':
        case 'CANCELLED': {
          const lastLog = body.logs?.at(-1)
          return ok({
            ok: false,
            releaseId: deploymentId,
            status: 'failed' as const,
            error: lastLog?.message ?? `Deployment ${body.status.toLowerCase()}`,
            warnings: [],
          })
        }

        case 'PENDING':
        case 'IN_PROGRESS':
          // Continue polling
          break

        default:
          // Unknown status -- keep polling
          break
      }
    } catch {
      // Network error during poll -- retry on next iteration
    }

    await new Promise((resolve) => setTimeout(resolve, interval))
  }

  return err(
    new CliError(
      `Deployment timed out after ${timeout / 1000}s`,
      'E_DEPLOY_TIMEOUT',
      `Deployment ID: ${deploymentId}. Check status on smithery.ai.`
    )
  )
}
