# Plugin Feedback Infrastructure Brainstorm

**Issue**: ai-44c
**Status**: Research Complete

## Research Findings

### What Exists (Legacy)

| Component | Location | Status |
|-----------|----------|--------|
| `/report` command system | `context/.context/legacy/prompts/commands/report*` | Legacy, not migrated |
| Bug memory filesystem | `context/.context/legacy/memory/bugs/` | Legacy pattern |
| Bug report template | `context/.context/legacy/prompts/templates/issues/bug-report.md` | Legacy |
| GitHub issue templates | `.github/ISSUE_TEMPLATE/*.yml` | Active, but component-focused |

### What's Missing

1. **No feedback commands** - Legacy `/report` system never migrated to `context/commands/`
2. **No user-facing issue templates** - All templates are for adding components, not reporting bugs
3. **No CONTRIBUTING.md** - Not at repo root or in any plugin
4. **No plugin documentation** - `docs/` directories are stub placeholders only
5. **No CHANGELOG.md** - No version history tracking in plugins

## Proposed Components

### 1. GitHub Issue Templates (Priority: Must)

Add user-focused templates to `.github/ISSUE_TEMPLATE/`:

| Template | Purpose |
|----------|---------|
| `bug-report.yml` | Report bugs in plugins/skills |
| `feature-request.yml` | Request new features |
| `feedback.yml` | General feedback/questions |

### 2. Plugin Documentation (Priority: Must)

Add to plugin template and scaffold workflow:

| File | Purpose |
|------|---------|
| `docs/USAGE.md` | How to use the plugin |
| `docs/TROUBLESHOOTING.md` | Common issues and solutions |
| `CHANGELOG.md` | Version history (root level) |
| `CONTRIBUTING.md` | How to contribute |

### 3. Feedback Command (Priority: Should)

Migrate and modernize the legacy `/report` system:

| Subcommand | Purpose |
|------------|---------|
| `/feedback bug` | Report a bug with context |
| `/feedback feature` | Request a feature |
| `/feedback improve` | Suggest an improvement |

### 4. Feedback Prompts (Priority: Nice)

Add contextual feedback prompts:

- Error message footer: "Having issues? Run `/feedback bug`"
- Command completion: "Was this helpful? Run `/feedback` to let us know"

## Implementation Plan

### Phase 1: GitHub Templates (P0)

1. Create `bug-report.yml` with:
   - Plugin/skill selector dropdown
   - Version field
   - Reproduction steps
   - Expected vs actual behavior
   - Environment info

2. Create `feature-request.yml` with:
   - Component type dropdown
   - Use case description
   - Proposed solution

3. Create `feedback.yml` with:
   - Feedback type dropdown
   - Free-form description

### Phase 2: Plugin Template Docs (P0)

1. Update `context/plugins/.template/docs/`:
   - Replace stub `chapter_1.md` with `USAGE.md`
   - Add `TROUBLESHOOTING.md` template
   - Update `SUMMARY.md`

2. Add `CHANGELOG.md` to template root

3. Add `CONTRIBUTING.md` to template root

4. Update `scaffold.md` to copy and customize these files

### Phase 3: Feedback Command (P1)

1. Create `/feedback` command at `context/commands/feedback.md`
2. Implement subcommands: bug, feature, improve
3. Auto-gather context (plugin version, recent errors)
4. Generate GitHub issue via `gh` CLI

### Phase 4: Retrofit Script (P2)

1. Create `just add-feedback-infra <plugin>` task
2. Add missing docs to existing plugins
3. Generate CHANGELOG from git history

## Questions

1. Should feedback command create GitHub issues or local files?
2. Should we preserve the `/report` command name from legacy?
3. How much auto-context gathering is helpful vs noisy?

## Dependencies

- Template fixes (ai-brx, ai-gmn, ai-dok, ai-b8p) ✅ Complete
- Marketplace.json step (ai-p4n) ✅ Complete

## Next Steps

1. Create GitHub issue templates (Phase 1)
2. Update plugin template docs (Phase 2)
3. Update scaffold workflow
