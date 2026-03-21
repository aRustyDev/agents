# ADR-023: Detect Git Protocol from System Configuration (SSH-First)

## Status

Accepted

## Context

The catalog download pipeline hardcoded `https://github.com/${owner}/${repo}.git` for all clone URLs in the `resolveCloneUrl` helper. On systems configured for SSH (the common case with 1Password SSH agent or Secretive), HTTPS clones fail with "Authentication failed" because the git credential helper is not configured for HTTPS. Analysis of the catalog's 499 failed-once entries showed this was the root cause of approximately 20% of download failures — not transient network errors or missing repos.

The fix is not simply "use SSH everywhere" — systems without SSH keys configured would break. The correct behavior is to detect what the system is already configured to use.

## Decision Drivers

1. **Zero-config correctness** — clones should work out of the box on both SSH-configured and HTTPS-configured systems
2. **Explicit override** — users must be able to force a protocol regardless of detection
3. **Detection latency** — detection runs once per session, not per clone
4. **1Password / Secretive compatibility** — `IdentityAgent` entries in `~/.ssh/config` are the canonical signal for SSH agent presence

## Considered Options

### Option 1: Always HTTPS + Credential Helper

Require users to configure a git credential helper for HTTPS.

- Pro: Uniform URL format, no detection logic
- Con: Breaks SSH-configured systems silently; credential helper setup is non-trivial; fails 1Password SSH users

### Option 2: Always SSH

Use `git@github.com:` for all clone URLs.

- Pro: Works for the majority of developer workstations
- Con: Breaks on systems without SSH keys (CI, fresh machines, containers)

### Option 3: Auto-Detect from System Config with `--git-protocol` Override (Chosen)

Check system config in priority order; accept an explicit flag for overrides.

- Pro: Works on both SSH and HTTPS systems; explicit override for edge cases; detection is fast (file read + one `git config` call)
- Con: Detection logic adds complexity; `~/.ssh/config` parsing must be robust to non-standard configs

### Option 4: Try HTTPS, Fallback to SSH on Failure

Attempt HTTPS clone; if it fails, retry with SSH.

- Pro: Eventually correct
- Con: Doubles clone time on SSH-configured systems; error classification is unreliable (auth failures look like network failures)

## Decision

**Add `detectGitProtocol()` and `resolveCloneUrl(ownerRepo, protocol)` to `cli/lib/git.ts`.**

`detectGitProtocol()` checks in order:

1. `~/.ssh/config` — presence of `IdentityAgent` block (1Password `~/.1password/agent.sock`, Secretive `/var/folders/.../agent`) signals SSH is active
2. `git config url."git@github.com:".insteadOf` — explicit rewrite rule signals SSH preference
3. `gh auth status --hostname github.com` — parses the `Protocol:` line from `gh`'s output
4. Falls back to `https` if none of the above match

`resolveCloneUrl` constructs `git@github.com:${ownerRepo}.git` for `ssh` and `https://github.com/${ownerRepo}.git` for `https`.

A `--git-protocol ssh|https` CLI flag on `catalog download` overrides detection entirely.

## Consequences

### Positive

- SSH-configured systems (1Password IdentityAgent, Secretive) work automatically without any flags
- HTTPS systems (CI, fresh workstations) work automatically without any flags
- `--git-protocol` flag provides an explicit escape hatch for non-standard configs

### Negative

- `~/.ssh/config` parsing must handle non-standard syntax gracefully — malformed entries must not throw
- Detection adds ~10ms per session (one file read, one `git config` subprocess call)

### Neutral

- Detection result is cached for the lifetime of the process — called once, reused across all clones in a batch
- The `gh auth status` fallback introduces a soft dependency on `gh` being installed, but is not required — it is the last fallback before the HTTPS default
