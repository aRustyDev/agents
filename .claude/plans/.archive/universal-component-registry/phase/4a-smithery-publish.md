# Phase 4a: Publish to Smithery

**ID:** `phase-4a`
**Dependencies:** phase-2 (complete), phase-3a (complete)
**Status:** planned

## Objective

Add a `publish` operation to the component system and implement it for Smithery's MCP server registry. This lets users publish MCP server packages to `smithery.ai` via `just agents mcp publish`.

## Success Criteria

- [ ] `publish()` method added to `ComponentProvider` interface
- [ ] `ComponentManager.publish()` routes to capable providers
- [ ] `SmitheryProvider` gains `publish: ['mcp_server']` capability
- [ ] Smithery publish flow: authenticate → validate → upload → poll for status
- [ ] `PublishOptions` and `PublishResult` types defined
- [ ] Authentication via `SMITHERY_API_KEY` env var or interactive login
- [ ] Dry-run mode shows what would be published without uploading
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Publish types + interface extension | `cli/lib/component/types.ts` | TypeScript (additions) |
| Smithery publish implementation | `cli/lib/component/smithery-publish.ts` | TypeScript |
| Smithery auth module | `cli/lib/component/smithery-auth.ts` | TypeScript |
| Updated SmitheryProvider | `cli/lib/component/provider-smithery.ts` | TypeScript (modifications) |
| Updated ComponentManager | `cli/lib/component/manager.ts` | TypeScript (additions) |
| Tests | `cli/test/component/smithery-publish.test.ts` | bun:test |
| Tests | `cli/test/component/smithery-auth.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/component/smithery-publish.ts`
- `cli/lib/component/smithery-auth.ts`
- `cli/test/component/smithery-publish.test.ts`
- `cli/test/component/smithery-auth.test.ts`

**Modify:**
- `cli/lib/component/types.ts` (add `publish()` to `ComponentProvider`, add `PublishOptions`/`PublishResult`)
- `cli/lib/component/provider-smithery.ts` (add `publish` capability + delegate to smithery-publish)
- `cli/lib/component/manager.ts` (add `publish()` method)

## Design

### Smithery Publish API (from prior research)

Smithery uses a multipart POST to create a "release" for a server:

```
POST /servers/{qualifiedName}/releases
Content-Type: multipart/form-data

Parts:
  - payload: JSON string (deployment descriptor)
  - module: JavaScript bundle (esbuild output)
  - sourcemap: Source map (optional)
```

Response: `{ deploymentId: string }`

Poll: `GET /servers/{qualifiedName}/releases/{deploymentId}` returns `{ status, logs, mcpUrl }`

Terminal statuses: `SUCCESS`, `FAILURE`, `AUTH_REQUIRED`, `CANCELLED`

### What We Actually Need (MVP)

For MVP, we do NOT need to replicate Smithery's full build pipeline (esbuild, workerd, shttp). Instead, we support **publishing a pre-built directory** or **an external URL**:

1. **External URL publish** — register an existing MCP server URL with Smithery (no build)
2. **Pre-built directory publish** — upload a pre-built bundle (user runs their own build)

This avoids depending on `esbuild`, `miniflare`, and Smithery's transport-specific build logic. Users who need the full Smithery build pipeline can use `npx @smithery/cli mcp publish` directly.

### Authentication

Smithery API key from (in order):
1. `SMITHERY_API_KEY` environment variable
2. Settings file at platform-specific path (same as Smithery CLI)
3. Interactive device-code flow (open browser, poll for token)

For MVP: support env var + manual input only. Device-code flow deferred.

## Tasks

### Task 4a.1: Extend ComponentProvider with publish()

**Files:** Modify `cli/lib/component/types.ts`, `cli/lib/component/manager.ts`

Add to `types.ts`:

```typescript
/** Options for publishing a component to a registry. */
export interface PublishOptions {
  /** Qualified name (namespace/server for Smithery). */
  readonly name?: string
  /** Namespace to publish under. */
  readonly namespace?: string
  /** API key for authentication. */
  readonly apiKey?: string
  /** URL of an external MCP server (no build needed). */
  readonly externalUrl?: string
  /** JSON Schema for server configuration. */
  readonly configSchema?: Record<string, unknown>
  /** Pre-built bundle directory path. */
  readonly bundleDir?: string
  /** Dry run — validate without uploading. */
  readonly dryRun?: boolean
  /** Working directory. */
  readonly cwd?: string
}

/** Result of a publish operation. */
export interface PublishResult {
  readonly ok: boolean
  /** Registry URL where the component is now available. */
  readonly registryUrl?: string
  /** Deployment/release identifier. */
  readonly releaseId?: string
  /** Status: 'published', 'pending', 'failed'. */
  readonly status: 'published' | 'pending' | 'failed'
  readonly error?: string
  readonly warnings: string[]
}
```

Add `publish()` to `ComponentProvider`:
```typescript
publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>>
```

Add `publish()` to `ComponentManager`:
```typescript
async publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>> {
  const providers = this.findProviders('publish', type)
  if (providers.length === 0) {
    return err(new CliError(`No provider supports publishing ${type}`, 'E_NO_PROVIDER'))
  }
  return providers[0]!.publish(type, opts)
}
```

Update all existing providers to add a stub `publish()` that returns `E_UNSUPPORTED`.

Tests:
- `ComponentProvider` interface accepts `publish` method
- `ComponentManager.publish()` routes to capable provider
- `ComponentManager.publish()` returns E_NO_PROVIDER when none registered

### Task 4a.2: Smithery Authentication Module

**Files:** Create `cli/lib/component/smithery-auth.ts`, `cli/test/component/smithery-auth.test.ts`

```typescript
export interface SmitheryAuth {
  readonly apiKey: string
}

/**
 * Resolve Smithery API key from environment or interactive input.
 * Priority: SMITHERY_API_KEY env → prompt (if TTY) → error
 */
export async function resolveSmitheryAuth(opts?: { apiKey?: string }): Promise<Result<SmitheryAuth>>

/** Validate an API key against Smithery's API. */
export async function validateSmitheryApiKey(apiKey: string, baseUrl?: string): Promise<Result<boolean>>
```

Tests (mock fetch):
- Resolves from explicit apiKey option
- Resolves from SMITHERY_API_KEY env var
- Returns error when no key available (non-TTY)
- validateSmitheryApiKey returns true for 200 response
- validateSmitheryApiKey returns false for 401 response

### Task 4a.3: Smithery Publish Implementation

**Files:** Create `cli/lib/component/smithery-publish.ts`, `cli/test/component/smithery-publish.test.ts`

```typescript
export interface SmitheryPublishOptions {
  readonly qualifiedName: string  // "namespace/server-name"
  readonly apiKey: string
  readonly externalUrl?: string   // External server URL
  readonly configSchema?: Record<string, unknown>
  readonly bundleDir?: string     // Pre-built bundle path
  readonly dryRun?: boolean
  readonly baseUrl?: string       // Override API base URL
}

/**
 * Publish an MCP server to Smithery.
 *
 * Two modes:
 * 1. External URL: registers a server URL with optional config schema
 * 2. Pre-built bundle: uploads a directory containing manifest.json + built JS
 */
export async function publishToSmithery(opts: SmitheryPublishOptions): Promise<Result<PublishResult>>

/**
 * Poll Smithery for deployment status until terminal state.
 */
export async function pollDeployment(
  qualifiedName: string,
  deploymentId: string,
  apiKey: string,
  opts?: { baseUrl?: string; timeoutMs?: number; intervalMs?: number }
): Promise<Result<PublishResult>>
```

Tests (mock fetch):
- External URL publish: sends correct payload, returns registryUrl
- Pre-built bundle publish: reads manifest.json, creates multipart POST
- Dry run: validates without sending
- Poll returns 'published' on SUCCESS status
- Poll returns 'failed' on FAILURE status
- Poll times out after configured duration
- Handles 404 (server not found) — offers to create
- Handles 401 (bad API key) — clear error message

### Task 4a.4: Update SmitheryProvider

**Files:** Modify `cli/lib/component/provider-smithery.ts`

Add `publish: ['mcp_server']` to capabilities. Implement `publish()` method that:
1. Resolves auth via `resolveSmitheryAuth()`
2. Validates qualifiedName format (namespace/slug)
3. Delegates to `publishToSmithery()`

### Task 4a.5: Integration Test

**Files:** Create or extend test file

One end-to-end test with all mocks:
- Register SmitheryProvider with ComponentManager
- Call `manager.publish('mcp_server', { name: 'myns/my-server', externalUrl: 'https://...', apiKey: 'test-key' })`
- Verify the full flow: auth → publish → poll → result

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No API key available | `E_AUTH_REQUIRED` error with hint to set `SMITHERY_API_KEY` |
| Invalid API key (401) | `E_AUTH_FAILED` error |
| Server doesn't exist on Smithery | `E_SERVER_NOT_FOUND` with hint to create it first |
| Namespace doesn't exist | `E_NAMESPACE_NOT_FOUND` error |
| Rate limited (429) | `E_RATE_LIMITED` with retry-after hint |
| Network timeout during upload | `E_UPLOAD_TIMEOUT` |
| Poll exceeds timeout (5 min) | `E_DEPLOY_TIMEOUT` with deployment ID for resume |
| Dry run with invalid config schema | Validate schema structure, report errors without uploading |
| bundleDir missing manifest.json | `E_MISSING_MANIFEST` |

## Acceptance Criteria

- [ ] `publish()` on ComponentProvider interface (all existing providers updated with stubs)
- [ ] `ComponentManager.publish()` routes correctly
- [ ] SmitheryProvider supports external URL publishing
- [ ] SmitheryProvider supports pre-built bundle publishing
- [ ] Auth resolves from env var or explicit option
- [ ] Dry-run mode validates without uploading
- [ ] Poll loop with configurable timeout
- [ ] At least 25 tests across 3 test files
- [ ] No new heavy dependencies (no esbuild, no miniflare)
