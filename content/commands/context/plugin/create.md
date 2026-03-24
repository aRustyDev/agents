---
description: End-to-end plugin creation workflow — brainstorm, research, plan, scaffold, and issue generation
argument-hint: <plugin-name> [--domain <d>] [--mvp-only] [--skip-research] [--dry-run-issues]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), Bash(cp:*), Bash(bd:*), Bash(ccpm:*), Bash(gh:*), Glob, Grep, WebSearch, WebFetch, Task, AskUserQuestion
---

# Create Plugin

Orchestrate the full plugin creation workflow by chaining sub-commands sequentially. Pauses after roadmap generation for user review before scaffolding.

## Arguments

- `$1` - Plugin name (lowercase, hyphenated). Example: `terraform-dev`
- `--domain` - Domain hint for brainstorming (e.g., "infrastructure", "frontend")
- `--mvp-only` - Only include P0 items in the roadmap
- `--skip-research` - Skip the research phase (use when you already know what exists)
- `--dry-run-issues` - Preview issues without creating them

## Output

- `.plans/plugins/<plugin-name>/brainstorm.md`
- `.plans/plugins/<plugin-name>/research.md` (unless `--skip-research`)
- `.plans/plugins/<plugin-name>/roadmap.md`
- `content/plugins/<plugin-name>/` (scaffolded directory)
- Beads issues (or previews with `--dry-run-issues`)

## Workflow

### Phase 1: Brainstorm

Run the brainstorm sub-command to interactively plan components:

```text
/brainstorm-plugin <plugin-name> --domain <domain>
```

Output: `.plans/plugins/<plugin-name>/brainstorm.md`

### Phase 2: Research (skippable)

If `--skip-research` is NOT set, research existing components:

```text
/research-plugin-components .plans/plugins/<plugin-name>/brainstorm.md
```

Output: `.plans/plugins/<plugin-name>/research.md`

If `--skip-research` IS set, generate a minimal research document marking all components as "create":

```markdown
# Plugin Research: <name>

## Summary

- **Reuse**: 0 components
- **Extend**: 0 components
- **Create**: <all components from brainstorm>

_Research skipped via --skip-research flag._
```

### Phase 3: Roadmap

Generate the prioritized roadmap:

```text
/plan-plugin-roadmap .plans/plugins/<plugin-name>/research.md [--mvp-only]
```

Output: `.plans/plugins/<plugin-name>/roadmap.md`

### --- PAUSE: User Review ---

**Present the roadmap to the user for review.**

Use AskUserQuestion:

- Show the roadmap summary (action counts, P0/P1/P2 breakdown)
- Ask: "Review the roadmap above. Would you like to proceed with scaffolding?"
- Options: "Proceed", "Edit roadmap first", "Stop here"

If "Edit roadmap first": Let the user make changes, then re-read the roadmap.
If "Stop here": End the workflow, report what was generated so far.

### Phase 4: Scaffold

Create the plugin directory structure:

```text
/scaffold-plugin <plugin-name> .plans/plugins/<plugin-name>/roadmap.md
```

Output: `content/plugins/<plugin-name>/`

### Phase 5: Register in Marketplace

Add the plugin to `.claude-plugin/marketplace.json`:

1. Read the generated `content/plugins/<plugin-name>/.claude-plugin/plugin.json`
2. Read the existing `.claude-plugin/marketplace.json`
3. Add a new entry to the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./content/plugins/<plugin-name>",
  "description": "<description from plugin.json>",
  "version": "<version from plugin.json>",
  "author": {
    "name": "<author.name from plugin.json>",
    "email": "<author.email from plugin.json>"
  },
  "keywords": ["<keywords from plugin.json>"],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/<plugin-name>",
  "repository": "https://github.com/aRustyDev/agents.git"
}
```

4. Write the updated marketplace.json

**Note:** This step ensures the plugin is discoverable in the marketplace registry.

### Phase 6: Generate Issues

Create beads issues for extend/create work:

```text
/generate-plugin-issues .plans/plugins/<plugin-name>/roadmap.md [--dry-run]
```

Pass `--dry-run` if `--dry-run-issues` was set.

### Phase 7: Final Report

```text
## Plugin Created: <name>

### Artifacts

| Artifact | Location |
|----------|----------|
| Brainstorm | .plans/plugins/<name>/brainstorm.md |
| Research | .plans/plugins/<name>/research.md |
| Roadmap | .plans/plugins/<name>/roadmap.md |
| Plugin | content/plugins/<name>/ |
| Marketplace | .claude-plugin/marketplace.json (entry added) |
| Issues | N created (or "dry run") |

### Component Summary

| Action | P0 | P1 | P2 | Total |
|--------|----|----|-----|-------|
| Reuse  | N  | N  | N   | N     |
| Extend | N  | N  | N   | N     |
| Create | N  | N  | N   | N     |

### Feedback Infrastructure

The plugin includes built-in feedback mechanisms:
- **Bug Reports**: TROUBLESHOOTING.md links to bug-report.yml template
- **Feature Requests**: CONTRIBUTING.md links to feature-request.yml template
- **Success Stories**: Both docs link to GitHub Discussions Show and Tell
- **Output Style**: plugin.json references feedback-submission.md for consistent formatting

### Next Steps

1. Review and refine plugin files in `content/plugins/<name>/`
2. Customize feedback documentation with plugin-specific examples
3. Start working on P0 issues
4. Run `just build-plugin <name>` to validate the scaffold
```

## Examples

```text
/create-plugin terraform-dev --domain infrastructure
/create-plugin rust-projects --domain "systems programming" --mvp-only
/create-plugin siem-ops --dry-run-issues
/create-plugin frontend-dev --domain frontend --skip-research
```

## Sub-Command Reference

| Phase | Command | Can Skip? |
|-------|---------|-----------|
| 1 | `/brainstorm-plugin` | No |
| 2 | `/research-plugin-components` | Yes (`--skip-research`) |
| 3 | `/plan-plugin-roadmap` | No |
| 4 | `/scaffold-plugin` | User can stop after roadmap |
| 5 | Marketplace registration | No (automatic after scaffold) |
| 6 | `/generate-plugin-issues` | User can stop after scaffold |
