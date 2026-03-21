# ADR-024: Prefer Structured Orchestrators Over Shell-Out Operations

## Status

Accepted

## Context

Several modules in `.scripts/` used shell-out patterns (`exec`, `spawn`, `npx`) to perform operations that could be expressed as structured TypeScript function calls. Shell-outs have recurring costs:

- **Opaque errors** — stderr parsing is fragile; all failures collapse into a single generic error type
- **No type safety** — inputs and outputs are untyped strings; callers must parse and validate manually
- **Process overhead** — each shell-out spawns a subprocess with startup cost, environment inheritance, and cleanup obligations
- **Untestable** — testing requires mocking `exec` or running real processes; unit tests become integration tests

The catalog download pipeline was the most acute case: `npx skills add`, `exec('git worktree ...')`, and `exec('find ...')` were composed in a single function with string-based error classification. But the principle applies broadly — any operation expressible as a function call is better as a function call.

## Decision Drivers

1. **Error classification** — structured error types enable differentiated retry/skip logic
2. **Composability** — modules with typed interfaces compose into orchestrators; shell commands compose into fragile pipelines
3. **Testability** — pure functions and injectable dependencies are testable without I/O
4. **Efficiency** — function calls avoid subprocess overhead; orchestrators can batch operations (e.g., clone once per repo, not per skill)

## Considered Options

### Option 1: Keep Shell-Outs with Better Error Parsing

Wrap `exec()` calls with regex-based stderr classifiers.

- Pro: Minimal code change; reuses existing tools
- Con: Fundamentally fragile — new error messages break parsers; still untyped; still per-invocation process overhead

### Option 2: Structured Orchestrator Composing Typed Modules (Chosen)

Replace shell-outs with TypeScript modules that return `Result<T>` types. Compose them into orchestrators with explicit error handling at each step.

- Pro: Typed errors; injectable for testing; composable; batching possible
- Con: More code to maintain; must replicate behavior previously handled by external tools

## Decision

**When an operation can be expressed as a TypeScript function call, prefer it over shelling out.** Specifically:

| Shell-out | Replacement | Module |
|-----------|-------------|--------|
| `exec('git clone/worktree')` | `simple-git` wrapper | `git.ts` |
| `exec('find -name SKILL.md')` | `discoverSkills()` | `skill-discovery.ts` |
| `npx skills add` | `downloadBatch()` | `catalog-download.ts` |
| `exec('gh auth token')` | `GitHubTokenProvider` | `github.ts` |

Orchestrators compose these modules and return structured `Result<T>` types with classified errors. The `deferCleanup` pattern allows callers to control resource lifecycle.

**When to still shell out:** External CLIs with no JS/TS equivalent (e.g., `shellcheck`, `ruff`, `biome` in pre-commit hooks). The heuristic: if the tool's output is consumed by humans (lint warnings), shell out. If consumed by code (data pipeline), use a library.

## Consequences

### Positive

- Error classification enables differentiated retry logic across the codebase
- Batching patterns are composable (e.g., `downloadBatch` groups by repo)
- Unit tests cover orchestrators without network I/O via injectable overrides

### Negative

- Library dependencies (`simple-git`, `@napi-rs/keyring`) replace CLI dependencies (`git`, `gh`)
- Orchestrator code must track upstream tool behavior changes manually

### Neutral

- Pre-commit hooks remain shell-based — their output is for humans, not code
- The pattern applies retroactively: other shell-outs in the codebase can be migrated incrementally
