# External Skill Tracking System

## Goal

Track external skills vendored into this repo, detect upstream drift, and create GH issues when derived local skills need review.

## Architecture

Two modes of external skill usage:

| Mode | Mechanism | Diff tracking |
|------|-----------|---------------|
| **Passthrough** | Symlink `context/skills/<name> -> .external/<source>/<skill>/` | No |
| **Derived** | Vendored snapshot in `.external/`, local skill independently authored | Yes |

**Constraint:** `passthrough` and `derived_by` are mutually exclusive. A skill cannot be both — if you need direct use AND drift tracking, create two manifest entries: one passthrough (for the symlink) and one derived (for tracking). This prevents unreviewed upstream changes from going live via symlink while a drift review is pending.

## Directory Layout

```
context/skills/
  .external/
    justfile                          # Module: just external:*
    sources.yaml                      # Manifest (hand-edited, declarative)
    sources.lock.yaml                 # Lock file (machine-managed, committed)
    steveyegge/beads/
      beads/                          # Committed snapshot
        SKILL.md
        ...
    vercel-labs/skills/
      find-skills/
        SKILL.md
    some-org/repo/
      their-skill/
        SKILL.md
  beads -> .external/steveyegge/beads/beads/         # passthrough symlink
  find-skills -> .external/vercel-labs/skills/find-skills/  # passthrough symlink
  my-local-skill/                     # Derived skill (yours)
    SKILL.md
  justfile                            # Imports .external/justfile as module
  .gitignore                          # .claude/ .agents/ (existing)

cli/
  bin/ai-tools.ts                     # CLI entry (Citty router)
  commands/skill.ts                   # skill deps check|sync|issues|status
  lib/
    schemas.ts                        # Valibot schemas for sources.yaml, lock
    hash.ts                           # Content-addressed hashing
    symlink.ts                        # Symlink health checks
    github.ts                         # Octokit issue CRUD
    output.ts                         # Table + JSON dual output
    lockfile.ts                       # Schema-driven lockfile ops
```

### Discovery Isolation

Verified: `npx skills ls` and `npx skills --full-depth *` skip dotdirs. SKILL.md files inside `.external/` are not discovered. No rename needed.

`.skillsignore` is not a feature of `npx skills`.

## Manifest: `sources.yaml`

Hand-edited. Declares what external skills exist and how they're used.

```yaml
skills:
  beads:
    source: steveyegge/beads        # GitHub owner/repo
    skill: beads                    # Skill name within that repo
    passthrough: true

  find-skills:
    source: vercel-labs/skills
    skill: find-skills
    passthrough: true

  some-upstream:
    source: some-org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-local-skill
      - another-local-skill

  pinned-legacy:
    source: old-org/archived-repo
    skill: legacy-skill
    ref: v2.1.0                     # Tag or commit SHA (not branches)
    passthrough: false
    derived_by:
      - my-modern-skill
```

### Valibot Schema

```typescript
// In lib/schemas.ts
export const ExternalSkillEntry = v.object({
  source: v.string(),                                    // owner/repo
  skill: v.string(),                                     // skill name in repo
  passthrough: v.boolean(),
  ref: v.optional(v.string()),                           // pin to tag or commit SHA (not branches)
  derived_by: v.optional(v.array(v.string())),           // local skills that depend on this
  // Validation: passthrough=true and derived_by are mutually exclusive
})

export const ExternalSourcesManifest = v.object({
  skills: v.record(v.string(), ExternalSkillEntry),
})
```

### `ref` Field: Pinning for Archived/Deprecated Skills

`npx skills` does not support ref pinning. When `ref` is present, `sync` bypasses `npx skills` and uses:

- Tag: `git clone --depth 1 --branch <tag> <repo-url>`
- Commit SHA: `git clone <repo-url>` + `git checkout <sha>`

**`ref` must be a tag or commit SHA, not a branch name.** Branches advance over time, which defeats the purpose of pinning. The Valibot schema should validate that `ref` looks like a semver tag (`v1.2.3`), a bare tag, or a hex SHA (40 chars). `check` verifies the ref still exists via `git ls-remote --tags` or `git ls-remote` with the SHA; content at a pinned ref is immutable, so CHANGED state cannot occur — only CURRENT or UNAVAIL.

This handles archived repos — as long as the repo exists on GitHub, the pinned ref is retrievable.

## Lock File: `sources.lock.yaml`

Machine-managed. Keyed by content-hash of `source + "/" + skill` (SHA256) so skills can be renamed in `sources.yaml` without losing tracking history.

```yaml
# Key = sha256("steveyegge/beads/beads").slice(0, 12)
a1b2c3d4e5f6:
  upstream_commit: "5045496bbe4b42d1..."     # Commit SHA from git ls-remote at sync time
  snapshot_hash: "sha256:16b0efc72b43..."    # Hash of downloaded snapshot contents (integrity check)
  last_synced: "2026-03-18T12:00:00Z"
  last_reviewed_commit: "abc1234"             # Commit in THIS repo where .external/ was last updated

# Key = sha256("some-org/repo/their-skill").slice(0, 12)
f6e5d4c3b2a1:
  upstream_commit: "d0bd0a7e0d725661..."
  snapshot_hash: "sha256:def456789..."
  last_synced: "2026-03-15T09:00:00Z"
  last_reviewed_commit: "def5678"
  drift_issue: 42                             # Open GH issue number
```

**Two hashes, two purposes:**
- `upstream_commit` — the remote commit SHA recorded at sync time. `check` compares `git ls-remote` output against this to detect drift without downloading.
- `snapshot_hash` — content-addressed hash of the downloaded files. Used for local integrity verification (detect tampering or accidental edits to `.external/`).

### Content-Hash Key Computation

```typescript
// lib/hash.ts
function lockKey(source: string, skill: string): string {
  const input = `${source}/${skill}`
  const hash = createHash('sha256').update(input).digest('hex')
  return hash.slice(0, 12)
}
```

## Justfile Recipes

```just
# context/skills/.external/justfile
# Imported by context/skills/justfile as: mod external ".external/justfile"
# Invoked as: just external:check, just external:sync, etc.

set unstable := true

# ROOT is not inherited from parent module scope, so recompute
ROOT := source_directory() / "../../.."
TOOLS := ROOT / "cli/bin/ai-tools.ts"
run := "bun run " + TOOLS + " skill deps"

# Full workflow: sync -> issues -> links -> status
[group('external')]
update *FLAGS:
    {{ run }} sync {{ FLAGS }}
    {{ run }} issues {{ FLAGS }}
    just external:links
    {{ run }} status {{ FLAGS }}

# Check for upstream changes (network, no local writes)
[group('external')]
check *FLAGS:
    {{ run }} check {{ FLAGS }}

# Pull fresh copies into .external/ (writes files, no commit)
[group('external')]
sync *FLAGS:
    {{ run }} sync {{ FLAGS }}

# Create/update GH issues for drift, update lock (no commit)
[group('external')]
issues *FLAGS:
    {{ run }} issues {{ FLAGS }}

# Create/refresh passthrough symlinks (declarative)
[group('external')]
links:
    {{ run }} links

# Show current state table (hashes, staleness, symlinks, open issues)
[group('external')]
status *FLAGS:
    {{ run }} status {{ FLAGS }}
```

All recipes delegate to `bun run cli/bin/ai-tools.ts skill deps <verb>`.

### Integration with `context/skills/justfile`

```just
# context/skills/justfile (existing, add this line)
mod external ".external/justfile"
```

## CLI Commands: `ai-tools skill deps`

`deps` is a **new top-level subcommand** added to `commands/skill.ts` in the migration spec's Citty structure. It contains five leaf subcommands:

```
ai-tools skill deps check   [--json] [--verbose]
ai-tools skill deps sync    [--force] [--json]
ai-tools skill deps issues  [--dry-run] [--json]
ai-tools skill deps links
ai-tools skill deps status  [--json]
```

### `skill deps check` Flow

1. Read `sources.yaml`
2. For each skill:
   - If `ref` set: `git ls-remote` to check ref still exists
   - If no `ref`: `git ls-remote HEAD` to get latest commit hash
   - Compare remote commit SHA against `sources.lock.yaml` `upstream_commit`
3. Output table:

```
┌──────────────────┬─────────────────────────┬──────────┬──────────────┐
│ Skill            │ Source                  │ Status   │ Last Synced  │
├──────────────────┼─────────────────────────┼──────────┼──────────────┤
│ beads            │ steveyegge/beads        │ current  │ 2026-03-18   │
│ find-skills      │ vercel-labs/skills      │ current  │ 2026-03-18   │
│ some-upstream    │ some-org/repo           │ CHANGED  │ 2026-03-15   │
│ pinned-legacy    │ old-org/archived-repo   │ UNAVAIL  │ 2026-03-10   │
└──────────────────┴─────────────────────────┴──────────┴──────────────┘
```

With `--json`:
```json
[
  { "skill": "beads", "source": "steveyegge/beads", "status": "current", "lastSynced": "2026-03-18T12:00:00Z" },
  { "skill": "some-upstream", "source": "some-org/repo", "status": "changed", "lastSynced": "2026-03-15T09:00:00Z" }
]
```

Exit codes: 0 = all current, 1 = drift detected, 2 = process error (network, parse failure).

### `skill deps sync` Flow

1. Read `sources.yaml`
2. For each skill with detected drift (or `--force` for all):
   - Create temp working dir: `mktemp -d`
   - If `ref` set: `git clone --depth 1 --branch <ref> https://github.com/<source>.git <tmpdir>`, then copy `<tmpdir>/<skill>/` to `.external/<source>/<skill>/`
   - If no `ref`: run `npx skills add -y --copy --full-depth <source>@<skill>` with CWD set to `<tmpdir>`, then copy `<tmpdir>/.claude/skills/<skill>/` to `.external/<source>/<skill>/`
   - Clean up temp dir, and any `.claude/` or `.agents/` artifacts created in `.external/`
   - Record `upstream_commit` via `git ls-remote https://github.com/<source>.git HEAD`
3. Update `sources.lock.yaml`: `upstream_commit`, `snapshot_hash`, `last_synced`
4. Do NOT commit — leave changes in working tree for review

### `skill deps issues` Flow

Uses `lib/github.ts` (Octokit wrapper).

1. Validate all `derived_by` entries reference existing directories in `context/skills/`. Warn on any that don't exist.
2. For each skill with `derived_by` AND changed files in `.external/` (detected via `git diff HEAD -- context/skills/.external/<source>/<skill>/`):
   - Group by local skill (`derived_by` value)
   - For each local skill:
     - Search: `gh api search/issues` for `[SKILL DRIFT] upstream changes (<local_skill>) is:open` in `aRustyDev/agents`
     - If open issue exists: append checklist item + diff as `<details>` block
     - If no open issue: create new issue
     - Record issue number in `sources.lock.yaml` -> `drift_issue`
2. Update `sources.lock.yaml` in place (no auto-commit)

All writes — snapshot files, lock file updates — are left uncommitted in the working tree. The user commits everything together after review. The `update` recipe's workflow (`sync -> issues -> links -> status`) produces a single reviewable changeset.

### `skill deps links` Flow

1. Read `sources.yaml`
2. For each skill with `passthrough: true`:
   - Compute target: `.external/<source>/<skill>/`
   - Compute link: `context/skills/<name>`
   - If symlink exists and points to correct target: skip
   - If symlink exists but wrong target: remove, recreate
   - If no symlink: create
   - If target doesn't exist: warn (sync needed)
3. Uses `lib/symlink.ts` for creation and health checks

### `skill deps status` Flow

Combined view of all state:

```
┌──────────────────┬─────────────────────────┬─────────────┬──────────┬──────────┬───────────┐
│ Skill            │ Source                  │ Mode        │ Hash     │ Symlink  │ Issue     │
├──────────────────┼─────────────────────────┼─────────────┼──────────┼──────────┼───────────┤
│ beads            │ steveyegge/beads        │ passthrough │ 16b0ef.. │ healthy  │ —         │
│ find-skills      │ vercel-labs/skills      │ passthrough │ abc123.. │ healthy  │ —         │
│ some-upstream    │ some-org/repo           │ derived     │ def456.. │ —        │ #42 open  │
│ pinned-legacy    │ old-org/archived-repo   │ derived     │ 789abc.. │ —        │ —         │
└──────────────────┴─────────────────────────┴─────────────┴──────────┴──────────┴───────────┘
```

## GH Issue Format

### Title

```
[SKILL DRIFT] upstream changes (<local-skill-name>)
```

### Labels

`skills`, `review`

### Body

```markdown
## Upstream Changes Affecting `<local-skill>`

- [ ] `some-org/repo@their-skill` changed (detected 2026-03-18, last reviewed at commit `abc1234`)
- [ ] `other-org/repo@other-skill` changed (detected 2026-03-20, last reviewed at commit `def5678`)

<details><summary>Diff: some-org/repo@their-skill</summary>

\`\`\`diff
<git diff output of .external/some-org/repo/their-skill/>
\`\`\`

</details>

## Local Skill
`context/skills/<local-skill>/SKILL.md`

## Action Required
Review upstream changes and decide whether to incorporate into local skill.
```

### Upsert Semantics

- Keyed by **local skill** (not external source)
- If `ext-skill-foo` drifts -> issue created for `my-local-skill`
- If `ext-skill-bar` also drifts (affects same `my-local-skill`) -> update existing open issue with new checklist item
- If issue was closed -> create new issue

### Source Unavailable

```markdown
- [ ] `old-org/archived-repo@legacy-skill` -- **SOURCE UNAVAILABLE** (detected 2026-03-18)
  Repository may be archived, renamed, or deleted.
  Last known snapshot: commit `abc1234` (2026-03-15)
  Pinned ref: `v2.1.0`
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| `npx skills add` fails (404, timeout) | Mark as UNAVAILABLE in check output, include in issue |
| `ref` doesn't exist on remote | Mark as UNAVAILABLE, suggest updating `ref` in sources.yaml |
| Symlink target missing | `links` warns "sync needed", `status` shows "broken" |
| GitHub API rate limit | Retry with backoff via `lib/github.ts` |
| `sources.yaml` parse error | Exit 1 with Valibot validation error |
| Lock key collision (astronomically unlikely) | Use longer hash prefix (16 chars) |

## Workflow: Day-to-Day Usage

### Initial setup

```bash
# Add an external skill to the manifest
vim context/skills/.external/sources.yaml  # Add entry

# Pull and commit the snapshot
just external:sync
git add context/skills/.external/
git commit -m "chore(skills): vendor <skill-name> from <source>"

# Create symlinks if passthrough
just external:links
```

### Periodic check (CI or manual)

```bash
just external:check          # Network check, no writes
# If drift detected:
just external:update         # sync -> issues -> links -> status
git add context/skills/.external/
git commit -m "chore(skills): update external skill snapshots"
```

### Reviewing drift

```bash
# Check open issues
just external:status --json | jq '.[] | select(.issue != null)'

# Review the diff in git
git diff HEAD~1 -- context/skills/.external/some-org/repo/their-skill/

# After incorporating changes into local skill:
# Close the GH issue manually
```

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `context/skills/.external/sources.yaml` | Create | Manifest |
| `context/skills/.external/sources.lock.yaml` | Create | Lock file (machine-managed) |
| `context/skills/.external/justfile` | Create | Module with external:* recipes |
| `context/skills/justfile` | Modify | Add `mod external ".external/justfile"` |
| `cli/commands/skill.ts` | Modify | Add `deps` subcommand tree |
| `cli/lib/schemas.ts` | Modify | Add ExternalSkillEntry, ExternalSourcesManifest schemas |
| `cli/lib/lockfile.ts` | Modify | Register external-skills lock schema |
| `context/skills/.gitignore` | Verify | Ensure `.external/` is NOT listed |

## Dependencies (already in migration spec)

No new dependencies beyond what the migration spec already includes:

- `lib/hash.ts` — content hashing for lock keys and snapshot comparison
- `lib/symlink.ts` — symlink creation and health checks
- `lib/github.ts` — Octokit wrapper for issue CRUD
- `lib/output.ts` — `console-table-printer` for tables, JSON mode
- `lib/schemas.ts` — Valibot schemas
- `lib/lockfile.ts` — lock file operations
