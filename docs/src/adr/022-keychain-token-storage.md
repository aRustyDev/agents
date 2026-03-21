# ADR-022: Use System Keychain for GitHub Token Storage Instead of File-Based Cache

## Status

Accepted

## Context

The original token cache wrote GitHub OAuth tokens to a plaintext file at `~/.config/ai-tools/github-token`. This had three concrete problems:

- **Security:** Tokens were readable by any process running as the same user — no encryption at rest.
- **Stale tokens:** No TTL tracking caused 401 errors in long-running batches when tokens expired mid-run.
- **Concurrency:** Parallel batch workers in `processBatch` could race on the auth flow, each triggering a separate device flow prompt when multiple workers detected a missing or expired token simultaneously.

The pipeline also relied on `gh auth token` as a fallback, introducing a CLI dependency that fails in environments where `gh` is not installed or not authenticated.

## Decision Drivers

1. **Security** — tokens must be encrypted at rest, not world-readable plaintext
2. **Concurrency safety** — parallel callers must await a single auth flow, not each trigger their own
3. **TTL handling** — stale tokens must be detected before they cause 401s mid-batch
4. **CI compatibility** — `GITHUB_TOKEN` env var must remain the highest-priority override

## Considered Options

### Option 1: Keep File-Based Cache (Status Quo)

Plaintext file at `~/.config/ai-tools/github-token`.

- Pro: Simple, zero dependencies, works everywhere
- Con: Tokens readable by any process; no TTL; no concurrency safety; 401s on expiry

### Option 2: System Keychain via `@napi-rs/keyring` (Chosen)

Native OS credential storage: macOS Keychain, Windows Credential Manager, Linux Secret Service.

- Pro: Encrypted at rest by the OS; single native dependency; same API across platforms
- Con: Requires native addon compilation; Linux Secret Service daemon must be running

### Option 3: `keytar` (Electron's Keychain Library)

Functionally equivalent to `@napi-rs/keyring`.

- Pro: Battle-tested in VS Code / Electron ecosystem
- Con: Officially deprecated; heavier peer dependency surface; not maintained for standalone CLI use

## Decision

**Replace the plaintext file cache with `@napi-rs/keyring` and a `GitHubTokenProvider` class.**

The `GitHubTokenProvider` class (in `cli/lib/github-token.ts`) has three responsibilities:

1. **Priority chain:** `GITHUB_TOKEN` env var → keychain → device flow prompt
2. **Promise-based mutex:** concurrent callers `await` the same in-flight `Promise<string>` rather than each triggering a new device flow
3. **TTL-based expiry:** tokens stored with a timestamp; `isExpired()` returns true at 55 minutes for tokens with a nominal ~1hr lifetime

**One-time migration:** on first use, if a token exists at the old plaintext path, `GitHubTokenProvider` reads it, validates it with a lightweight API call, stores it in the keychain, and deletes the plaintext file.

## Consequences

### Positive

- Tokens encrypted at rest via OS-native credential store — not visible to other processes
- Mutex eliminates duplicate device flow prompts in concurrent batch workers
- TTL check prevents mid-batch 401s on long-running catalog runs
- `GITHUB_TOKEN` env var override keeps CI pipelines working without any keychain

### Negative

- `@napi-rs/keyring` is a native addon — adds a compilation step; binary must match Node/Bun ABI
- Linux requires a Secret Service daemon (e.g., `gnome-keyring`, `kwallet`) — headless servers may lack one

### Neutral

- The device flow prompt path is unchanged — only the storage and concurrency model changes
- The old plaintext file path is read once during migration, then deleted
