---
id: d2e3f4a5-6b7c-8d9e-0f1a-2b3c4d5e6f7a
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: "Monorepo Workspace Restructure + CLI Decomposition"
status: draft
tags: [architecture, restructure, monorepo, workspace, cli]
related:
  supersedes: []
  references: [678131a9-6bd5-4cd0-9728-610fbc8044df]
---

## Monorepo Workspace Restructure + CLI Decomposition

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure the repo into a Bun workspace monorepo AND decompose the CLI from noun-first commands into a verb-first architecture with shared library modules.

**Two-part plan:**

- **Part A (Phases 0-5):** Repo restructure — move files, rename dirs, configure workspace
- **Part B (Phases 6-9):** CLI decomposition — verb-first commands, shared modules, config system

**Tech Stack:** Bun workspaces, TypeScript, Citty, just

---

### Objectives

| # | Objective | Measurable | Done When |
|---|-----------|------------|-----------|
| 1 | CLI in `packages/cli/` with `src/`+`test/` structure | Yes | `cd packages/cli && bun test` — zero regressions from pre-restructure baseline |
| 2 | Content library in `content/` | Yes | All discovery still works |
| 3 | Dead directories removed | Yes | `crew/`, `polecats/`, `witness/`, `mayor/`, `refinery/` gone |
| 4 | Root workspace configured | Yes | `bun install` from root works |
| 5 | Verb-first CLI grammar | Yes | `agents add skill`, `agents search mcp server`, `agents lint plugin` all work |
| 6 | Shared library modules | Yes | Zero duplication between commands; all commands use shared lib |
| 7 | Component model handles all 11 types | Yes | skill, persona, lsp, mcp-server, mcp-client, mcp-tool, rule, hook, plugin, output-style, command — unified registry |
| 8 | `agents config` manages CLI settings | Yes | Default fail-on, debug, logging, search backends, db config |

### Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| CLI location | `cli/` (flat) | `packages/cli/src/` | No src/test split, no workspace |
| Content location | `context/` | `content/` | Naming mismatch |
| Dead directories | 7 | 0 | Cleanup needed |
| CLI architecture | Noun-first (`skill.ts`: 2000+ lines) | Verb-first (13 command modules) | Full decomposition |
| Component types | 4 implemented (skill, plugin, agent, mcp-server) | 11 (with placeholders) | 7 placeholders needed |
| Shared lib modules | Partial | Full (file-io, git, output, search, storage, config) | Utility layer needed |
| Config system | None (`CLAUDE.md` + `settings.json`) | `agents config` with file-based storage | New feature |

### CLI Grammar

```text
agents [-h, -y/--yes, --json, --output, --fail-on, --debug, --trace, -vvv]
│
│ Component lifecycle (verb-first):
├── init <component-type>       # Scaffold from template
├── add <component-type> <source>  # Install from source
├── remove <component-type> <name> # Remove installed component
├── list <component-type>       # List installed/available
├── search <component-type> <query>  # Search registries
├── lint [component-type] [name]   # Validate against schemas
├── info <component-type> <name>   # Describe a component
├── update [component-type] [name] # Download + update
├── check [component-type] [name]  # Quick health check (deferred)
│
│ Pipeline operations (noun-first exception):
├── catalog                     # Catalog pipeline operations
│   ├── discover                # Clone repos, discover skills, compute fields
│   ├── analyze                 # Tier 1 analysis (Haiku, judgment-only)
│   ├── analyze-deep            # Tier 2 analysis (Sonnet, quality grading)
│   ├── backfill                # Fill missing mechanical fields
│   ├── stale                   # Detect upstream content changes
│   ├── summary                 # Catalog statistics
│   ├── forks                   # Fork detection
│   ├── errors                  # Error log viewer
│   └── scrub                   # Data cleanup
│
│ System commands:
├── config                      # Configure agents CLI settings
├── doctor                      # Runtime health + static analysis
├── completions <shell>         # Shell completions
└── serve [--web, --api]        # Web UI + API (MVP)
```

**Component types (11):** skill, persona (placeholder), lsp (placeholder), mcp server, mcp client (placeholder), mcp tool (placeholder), rule, hook, plugin, output-style, command

**Named exceptions to verb-first:** `catalog` (pipeline operations on local data), `config` (CLI settings), `doctor` (health check), `completions` (shell integration), `serve` (server mode)

### Phases

| ID | Name | Status | Dependencies | Scope |
|----|------|--------|--------------|-------|
| **Part A: Repo Restructure** |  |  |  |  |
| phase-0 | Fix broken components/ recipes | planned | None | justfile |
| phase-1 | Cleanup dead directories | planned | None | rm dirs, move models |
| phase-2 | Move CLI to packages/cli with src/test split | planned | None | git mv, import rewrites |
| phase-3 | Rename context/ → content/ + update ALL config | planned | None | rename + 34 config updates |
| phase-4 | Root workspace configuration | planned | phase-2 | root package.json, justfile |
| phase-5 | Final verification (Part A) | planned | phase-0-4 | tests, hooks, docs |
| **Part B: CLI Decomposition** |  |  |  |  |
| phase-6 | Shared library modules | planned | phase-5 | file-io, output, config, component model |
| phase-7 | Verb-first command decomposition | planned | phase-6 | 13 command modules replacing noun-first |
| phase-8 | Config system + component placeholders | planned | phase-7 | agents config, placeholder types |
| phase-9 | Doctor + Serve (MVP) | planned | phase-8 | health check, web UI, API |

#### Phase Details

**Part A** phase details are in the sections below (Phases 0-5).
**Part B** phase details:

1. [Phase 6: Shared Library Modules](./phase/6-shared-library.md) *(to be created)*
2. [Phase 7: Verb-First Command Decomposition](./phase/7-verb-decomposition.md) *(to be created)*
3. [Phase 8: Config System + Component Placeholders](./phase/8-config-placeholders.md) *(to be created)*
4. [Phase 9: Doctor + Serve MVP](./phase/9-doctor-serve.md) *(to be created)*

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Import paths break after src/test split | High | High | Systematic regex + test verification after each batch |
| Pre-commit hooks break after context/ rename | Certain | High | Update all config in same commit as rename |
| 2000+ line skill.ts decomposition introduces regressions | High | High | Extract one verb at a time, test after each |
| Verb-first breaks existing `just agents skill ...` commands | Certain | Medium | Backward-compat aliases during transition |
| Config file format bikeshedding | Low | Low | Start with TOML, match gitconfig patterns |

### Design Decisions

#### Verb-First vs Noun-First

Current: `agents skill add foo`, `agents plugin validate bar`
Target: `agents add skill foo`, `agents lint plugin bar`

**Why:** Verbs are the reusable abstraction — `add`, `remove`, `search`, `lint` work the same across all component types. Noun-first leads to duplicated logic per noun file (`skill.ts` has its own add/remove/search, `plugin.ts` has its own validate, etc.).

#### Shared Library Priority

Top-tier utility functions (used by 3+ commands):

1. **file-io** — unified read/write/copy/symlink with error handling
2. **output** — structured output (JSON, table, human-readable) with branding
3. **git** — clone, worktree, rev-parse, ls-remote (already exists)
4. **search** — multi-backend search (skills.sh, smithery, catalog, meilisearch)
5. **component** — type registry, provider dispatch, schema validation (already exists)
6. **config** — CLI settings read/write (TOML-based, gitconfig-style precedence)
7. **source-parser** — URL/source string parsing (already exists)

#### Config Precedence

```text
1. CLI flags (--debug, --json)           # Highest
2. Environment variables (AGENTS_*)
3. Project config (.agents.toml)
4. User config (~/.config/agents/config.toml)
5. Built-in defaults                     # Lowest
```

Managed via `agents config set/get/list`, stored in TOML.

#### Component Type Registry

All 11 component types implement the same interface:

```typescript
interface ComponentType {
  name: string
  pluralName: string
  templateDir: string       // for init
  discoveryPattern: string  // glob for finding installed
  schemaPath?: string       // for lint
  providers: string[]       // for search (e.g., ['github', 'smithery'])
}
```

Placeholder types have `providers: []` and stub implementations.

**Type registry reconciliation needed in Phase 6:**
- Current code (`component/types.ts`): 9 types — skill, mcp_server, agent, plugin, rule, command, hook, output_style, claude_md
- Target: 11 types — skill, persona, lsp, mcp-server, mcp-client, mcp-tool, rule, hook, plugin, output-style, command
- Disposition: `agent` → keep (not a placeholder), `claude_md` → remove (not a component type), add 7 placeholders (persona, lsp, mcp-client, mcp-tool, script, setting + rename mcp_server→mcp-server)

#### Catalog Commands (Pipeline Exception)

The `catalog` subcommand tree is a **named exception** to the verb-first grammar. Catalog commands are pipeline operations on local data (`.catalog.ndjson`), not component lifecycle operations. They stay as `agents catalog <subcommand>`.

During Phase 7 decomposition of `skill.ts`, the ~1,300 lines of catalog code move to `packages/cli/src/commands/catalog.ts` as a standalone command module. This is not a verb — it's a pipeline noun, like `config` and `doctor`.

#### Test Baseline

92 pre-existing test failures exist before restructuring. Phase 0 includes a baseline task:
- Document which tests fail and categorize (stale schemas, missing fixtures, etc.)
- Success criterion for Phases 2-5: "zero regressions from baseline" not "all tests pass"
- Fixing baseline failures is a separate effort, tracked independently

#### Backward-Compat Aliases

During the noun-first → verb-first transition:
- Aliases implemented via Citty's `alias` option on each subcommand
- `agents skill add foo` routes to `agents add skill foo` with a deprecation warning
- Aliases active for one major version after Phase 7 ships
- Removed in the next major version; deprecation warnings guide users to new grammar
- Catalog subcommands (`agents skill catalog ...`) route directly to `agents catalog ...`

---

### Phase 0: Fix Broken components/ References

The justfile has 22 references to `components/` which doesn't exist.

#### Task 0.1: Audit and fix components/ references

- [ ] Identify all components/ references: `grep -n 'components/' justfile`
- [ ] Replace: `components/` → `context/` (will become `content/` in Phase 3)
- [ ] Verify recipes work
- [ ] Commit

#### Task 0.2: Establish test baseline

- [ ] Run `bun test --cwd cli` and record pass/fail counts
- [ ] Categorize the 92 pre-existing failures (stale schemas, missing fixtures, etc.)
- [ ] Document baseline in a `test-baseline.md` file for reference during restructure
- [ ] This baseline is the regression benchmark for Phases 2-5

---

### Phase 1: Cleanup Dead Directories

#### Task 1.1: Remove empty/abandoned directories

- [ ] Remove: `crew/`, `polecats/`, `witness/`, `mayor/`, `refinery/`
- [ ] Move `models/*` to `.data/models/`
- [ ] Remove `build/`, add to `.gitignore`
- [ ] Commit

---

### Phase 2: Move CLI to packages/cli with src/test Split

#### Task 2.1: Create structure and move files

- [ ] Create `packages/cli/src/` and `packages/cli/test/`
- [ ] `git mv cli/bin → packages/cli/src/bin`
- [ ] `git mv cli/commands → packages/cli/src/commands`
- [ ] `git mv cli/lib → packages/cli/src/lib`
- [ ] `git mv cli/test/* → packages/cli/test/`
- [ ] Move config files (package.json, tsconfig.json)
- [ ] Move Python files to `packages/cli/` level:
  - `cli/embed.py`, `cli/watch-embed.py`, `cli/init-db.py`, `cli/kg-stats.py`
  - `cli/plugin-hash.py`, `cli/build-plugin.py`, `cli/migrate-plugin-sources.py`
  - Note: CLAUDE.md references `.scripts/embed.py` (stale) — fix in Phase 5
- [ ] Move lint-context.sh

#### Task 2.2: Update test imports

- [ ] All `../lib/` → `../src/lib/` in test files
- [ ] All `../commands/` → `../src/commands/` in test files
- [ ] Update tsconfig.json include array
- [ ] Update package.json scripts
- [ ] Run tests: `cd packages/cli && bun test`

---

### Phase 3: Rename context/ → content/ + Update ALL Config

**MUST commit ALL config changes together with the rename.**

#### Task 3.1: Rename and update everything

- [ ] `git mv context content`
- [ ] Update TypeScript source (36+ files)
- [ ] Update `.pre-commit-config.yaml` (34 patterns)
- [ ] Update `.claude/devrag.json` (7 patterns)
- [ ] Update `.claude/settings.json`
- [ ] Update `justfile`
- [ ] Update `CLAUDE.md`, `README.md`
- [ ] Update `.mcp.json`
- [ ] Update `content/rules/**/*.md` prose references
- [ ] Update catalog path hardcodes in skill.ts (~10 occurrences of `context/skills/.catalog.ndjson`)
- [ ] Verify no remaining `context/` references
- [ ] Run tests

---

### Phase 4: Root Workspace Configuration

#### Task 4.1: Create root package.json and update justfile

- [ ] Create workspace root package.json (`"workspaces": ["packages/*"]`)
- [ ] Move bun.lock to root
- [ ] Update all 24 `cli/` references in justfile
- [ ] Update `.claude/settings.json` hooks
- [ ] Test workspace resolution from root and packages/cli
- [ ] Commit

---

### Phase 5: Final Verification (Part A)

#### Task 5.1: Comprehensive check

- [ ] Full test suite passes
- [ ] `just agents --help` works
- [ ] Pre-commit hooks pass
- [ ] Grep for stale paths: 0 refs to `.scripts/`, `cli/`, `context/`, `components/`
- [ ] Update CLAUDE.md directory structure
- [ ] Update README.md
- [ ] Update memory files

---

### Phase 6-9: CLI Decomposition

Phase documents to be created after Part A is complete and the file structure is stable. Phase details outlined in the Design Decisions section above.

**Phase 6:** Extract shared library modules (file-io, output, config, component type registry)
**Phase 7:** Decompose skill.ts (2000+ lines) + plugin.ts into verb-first command modules (init, add, remove, list, search, lint, info, update, config, completions)
**Phase 8:** Add `agents config` CLI with TOML storage + placeholder component types (persona, lsp, mcp-client, mcp-tool, script, setting)
**Phase 9:** `agents doctor` (runtime health + static analysis) + `agents serve` MVP (web UI from graph-viewer + API endpoints)

---

### Complete File Change Inventory

#### Part A: Repo Restructure

Same as original plan — see Files moved/modified/removed sections in the detailed phase docs.

#### Part B: CLI Decomposition (New Files)

| File | Phase | Purpose |
|------|-------|---------|
| `packages/cli/src/commands/init.ts` | 7 | Scaffold from templates |
| `packages/cli/src/commands/add.ts` | 7 | Install components |
| `packages/cli/src/commands/remove.ts` | 7 | Remove components |
| `packages/cli/src/commands/list.ts` | 7 | List components |
| `packages/cli/src/commands/search.ts` | 7 | Search registries |
| `packages/cli/src/commands/lint.ts` | 7 | Validate schemas |
| `packages/cli/src/commands/info.ts` | 7 | Describe components |
| `packages/cli/src/commands/update.ts` | 7 | Download + update |
| `packages/cli/src/commands/catalog.ts` | 7 | Pipeline operations (analyze, discover, backfill, stale, etc.) |
| `packages/cli/src/commands/config.ts` | 8 | CLI settings management |
| `packages/cli/src/commands/doctor.ts` | 9 | Health check |
| `packages/cli/src/commands/serve.ts` | 9 | Web UI + API |
| `packages/cli/src/commands/completions.ts` | 8 | Shell completions |
| `packages/cli/src/lib/file-io.ts` | 6 | Unified file operations |
| `packages/cli/src/lib/config.ts` | 6 | TOML config read/write |
| `packages/cli/src/lib/component-registry.ts` | 6 | Type registry for all 11 types |

#### Part B: Files Removed (Decomposed)

| File | Replaced By | Phase |
|------|------------|-------|
| `packages/cli/src/commands/skill.ts` (2000+ lines) | `add.ts`, `remove.ts`, `list.ts`, `search.ts`, `lint.ts`, `info.ts`, `update.ts` | 7 |
| `packages/cli/src/commands/plugin.ts` (1000+ lines) | Same verb modules | 7 |

### Notes

- Part A and Part B are sequential — Part B depends on the stable file structure from Part A
- `git mv` for all moves to preserve history
- Phase 3 MUST commit all config changes atomically
- Phase 7 decomposes one verb at a time, testing after each
- Backward-compat aliases (`agents skill add` → `agents add skill`) during transition period
- Phase 6-9 phase docs created after Part A completion when structure is finalized
