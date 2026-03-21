---
id: c3e48e7b-0900-48fb-9bef-5129cf813ad6
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 4a: Skill Commands + GitHub"
status: pending
related:
  depends-on: [1105f062-33cf-4eff-a759-f17fb55296c3, c4d1eba9-dea5-4b58-af0a-53113a016208]
---

# Phase 4a: Skill Commands + GitHub

**ID:** `phase-4a`
**Dependencies:** phase-1, phase-2
**Status:** pending
**Effort:** Medium

## Objective

Migrate existing skill validation/hashing commands to TypeScript and build the GitHub integration module (Octokit + Device Flow). This establishes the foundation that Phase 4b's external skill tracking builds on.

## Success Criteria

- [ ] `ai-tools skill validate <name>` validates SKILL.md frontmatter and structure
- [ ] `ai-tools skill hash <name>` produces correct hashes matching Python output
- [ ] `ai-tools skill lint [<name>]` runs cclint SDK and reports results
- [ ] `ai-tools skill check-all` validates all skills with aggregate results
- [ ] `lib/github.ts` authenticates via Device Flow (with `gh auth token` fallback)
- [ ] `lib/github.ts` can search, read, create, and update issues on `aRustyDev/agents`
- [ ] Exit codes: 0=success, 1=validation failures found, 2=process error
- [ ] All justfile skill recipes (validate, hash, lint) point to TypeScript

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| GitHub integration | `.scripts/lib/github.ts` | TypeScript |
| Skill commands | `.scripts/commands/skill.ts` | TypeScript |
| Updated justfile | `context/skills/justfile` | Just |
| Test suites | `.scripts/test/{github,skill}.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/lib/github.ts`
- `.scripts/test/github.test.ts`
- `.scripts/test/skill.test.ts`

**Modify:**
- `.scripts/commands/skill.ts` (replace stub with validate/hash/lint/check-all + deps stub)
- `context/skills/justfile` (update skill recipes to use `ai-tools`)

## Tasks

### lib/github.ts
- [ ] Implement `createClient()` — initialize Octokit with Device Flow auth
- [ ] Implement auth fallback order: cached token -> `gh auth token` -> Device Flow
- [ ] Implement token caching (persist to `~/.config/ai-tools/github-token`)
- [ ] Implement `searchIssues(repo, query)` — wraps `octokit.request('GET /search/issues')`
- [ ] Implement `readIssue(repo, number)` — wraps GET single issue
- [ ] Implement `createIssue(repo, opts)` — wraps POST with Result return
- [ ] Implement `updateIssue(repo, number, opts)` — wraps PATCH with Result return
- [ ] Implement `addComment(repo, number, body)` — wraps POST with Result return
- [ ] Write integration test: read a real public issue from `aRustyDev/agents` (no auth needed)
- [ ] Write unit test: mock Octokit for create/update operations

### commands/skill.ts — validate
- [ ] Read SKILL.md from `context/skills/<name>/SKILL.md`
- [ ] Parse frontmatter via `lib/chunker.ts` parseFrontmatter
- [ ] Validate against `SkillFrontmatter` schema from `lib/schemas.ts`
- [ ] Report validation errors via OutputFormatter
- [ ] Exit code 1 if validation failures found

### commands/skill.ts — hash
- [ ] Compute skill directory hash via `lib/hash.ts` hashDirectory
- [ ] Output hash with `sha256:` prefix
- [ ] Parity test: compare output against Python `build-plugin.py hash` for same skill

### commands/skill.ts — lint
- [ ] Import and invoke cclint SDK: `new CClint().lintProject()`
- [ ] If `<name>` provided, lint only that skill's directory
- [ ] If no name, lint all skills
- [ ] Report via OutputFormatter (table in human mode, JSON in --json mode)
- [ ] Exit code 1 if errors found

### commands/skill.ts — check-all
- [ ] Iterate all skill directories in `context/skills/`
- [ ] Skip dotdirs (`.external/`, `.templates/`)
- [ ] Run validate on each, aggregate results
- [ ] Show progress via spinner/progress bar
- [ ] Report summary table

### commands/skill.ts — deps stub
- [ ] Add `deps` subcommand group with placeholder subcommands
- [ ] Each returns "not yet implemented — see Phase 4b" message
- [ ] This ensures the CLI surface is discoverable before Phase 4b lands

### Justfile cutover
- [ ] Update `skill validate` recipe in `context/skills/justfile`
- [ ] Update `skill hash` recipe
- [ ] Add `skill lint` recipe (new)
- [ ] Verify all skill recipes work end-to-end

### Device Flow auth testing
- [ ] Manual test: `gh auth token` fallback works when `gh` is authenticated
- [ ] Manual test: Device Flow triggers when no cached token and no `gh`
- [ ] Manual test: subsequent runs use cached token

## Notes

- `lib/github.ts` is built here but fully exercised in Phase 4b (deps issues)
- Auth fallback order: cached token -> `gh auth token` -> Device Flow — this means users with `gh` installed get zero-friction auth
- The `deps` stub ensures `ai-tools skill deps --help` works immediately, showing what's coming
- Exit codes follow the same pattern as Phase 4b: 0=ok, 1=issues found, 2=process error
