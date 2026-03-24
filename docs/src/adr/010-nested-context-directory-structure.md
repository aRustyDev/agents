# ADR-010: Nested Context Directory Structure

## Status

Accepted

## Context

The `content/` directory contains reusable AI context components organized by type: `rules/`, `plugins/`, `agents/`, `skills/`, `commands/`. As the library grew, flat directories became difficult to navigate:

- `content/rules/` had 33 markdown files with naming-convention prefixes (`pre-commit-bash.md`, `pre-commit-python.md`, `cicd-github-actions.md`) to group related rules
- `content/plugins/` had 20 plugin directories (6 published, 14 scaffolded stubs) at a single level

The prefix-based grouping created long file names, made browsing tedious, and provided no structural indication of which rules/plugins relate to each other.

## Decision

**Organize context components into nested category subdirectories.**

### Rules Structure

```
content/rules/
  agent/              # Claude Code configuration
    plugin/           # Plugin-specific rules
    skills/           # Skill-specific rules
  arustydev/          # Organization-wide conventions
  cloudflare/         # Cloudflare platform rules
  docs/               # Documentation rules
  github/             # GitHub CI/CD and workflow rules
  patterns/           # Development patterns
  pre-commit/         # Pre-commit hook rules
  justfile            # Rules justfile (stays flat)
  justfile.md         # Documentation for the justfile (stays flat)
```

### Plugins Structure

```
content/plugins/
  .template/          # Plugin scaffold template
  blog-workflow/      # (top-level, published)
  job-hunting/        # (top-level, published)
  frontend/
    design-to-code/   # (published)
    swiftui-dev/      # (published)
  releases/
    homebrew-dev/     # (published)
  web/
    browser-extension-dev/  # (published)
```

### Pattern

```
content/<component-type>/
  <category>/                    # Optional grouping directory
    <component-name>/            # The actual component
      .claude-plugin/plugin.json # (plugins only)
      SKILL.md                   # (skills only)
      ...
```

Categories are **optional** — components can remain at the top level if they don't fit a natural group (e.g., `blog-workflow`). Category directories contain no files of their own, only component subdirectories.

### Impact on Discovery

All glob patterns that reference context components must use recursive globs (`**`) to discover nested files:

| Before | After |
|--------|-------|
| `content/rules/*.md` | `content/rules/**/*.md` |
| `content/plugins/*/.claude-plugin/plugin.json` | `content/plugins/**/.claude-plugin/plugin.json` |

Files updated:
- `.claude/devrag.json` — document patterns
- `cli/embed.py` — entity type patterns
- `cli/watch-embed.py` — uses recursive watchdog (no change needed)
- `.pre-commit-config.yaml` — exclusion patterns
- `.claude/settings.json` — cclint hook patterns (expanded for absolute paths)
- `content/commands/content/rule/create.md` — target path documentation
- `content/commands/content/rule/promote.md` — listing commands
- `content/rules/justfile` — list/validate recipes use `find` instead of `ls`

### Relative Path Impact

Plugins that use `../../output-styles/` relative paths must add an extra `../` when moved into a category subdirectory:

| Location | Path to shared output-styles |
|----------|------------------------------|
| `content/plugins/<name>/` (top-level) | `../../output-styles/` |
| `content/plugins/<category>/<name>/` (nested) | `../../../output-styles/` |

Plugins that bundle their own styles locally (`./styles/`) are unaffected.

### Stubbed Components

Template-only scaffolds (directories containing only `.gitkeep` files) should not be committed. Record planned components in a `TODO.md` at the component-type root (e.g., `content/plugins/TODO.md`) and create them with the appropriate `/context:<type>:create` command when ready to implement.

## Consequences

### Positive

- Browsing `content/rules/` shows 8 category directories instead of 33 files
- Related rules are co-located (all 9 pre-commit rules in one directory)
- Plugin categories make the ecosystem structure visible at a glance
- Naming prefixes eliminated — `pre-commit/python.md` instead of `pre-commit-python.md`
- Category directories serve as lightweight taxonomy without metadata overhead

### Negative

- All glob patterns across the project must be audited and updated to `**` recursive form
- Relative paths in plugin manifests may break when plugins move between top-level and categorized positions
- `bash` `case` statements (used in hooks) don't support `**` — must enumerate depth levels
- Justfile recipes require `find` instead of `ls` for discovery
- Adding a new plugin requires choosing a category (or explicitly placing at top-level)

### Neutral

- File content is unchanged — this is a pure organizational restructure
- Git history tracks moves cleanly via `git mv`
- No impact on Claude Code's rule loading (it discovers all `.md` files recursively)
