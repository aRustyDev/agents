# Phase 7: Plugin Packaging

## Objective

Extract into a marketplace plugin with proper namespacing and delegation.

## Architecture Note

This phase packages the complete blog-workflow plugin for distribution. Commands use `/blog/` namespace with `/` separators (not `:`). Plugin bundles templates in `.templates/` (with dot prefix) that `/blog/init` copies to the user's project.

---

## Command Summary

| Command | Purpose | Self-Review |
|---------|---------|-------------|
| `/blog/init` | Initialize blog workflow in target project | Yes - validates structure |

---

## Deliverables

### 1. Plugin Manifest

Update `.claude-plugin/plugin.json`:

```json
{
  "name": "blog-workflow",
  "version": "2.0.0",
  "description": "Multi-phase blog content creation with personas, templates, and iterative review",
  "author": {
    "name": "Adam Smith",
    "email": "developer@gh.arusty.dev",
    "url": "https://im.arusty.dev"
  },
  "keywords": [
    "blog",
    "content",
    "writing",
    "persona",
    "workflow",
    "technical-writing"
  ],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/blog-workflow",
  "repository": "https://github.com/aRustyDev/ai.git",
  "commands": [
    "./commands/init.md",
    "./commands/idea/brainstorm.md",
    "./commands/idea/review.md",
    "./commands/idea/refine.md",
    "./commands/idea/draft-plan.md",
    "./commands/persona/draft.md",
    "./commands/persona/plan.md",
    "./commands/persona/review.md",
    "./commands/template/draft.md",
    "./commands/template/plan.md",
    "./commands/template/review.md",
    "./commands/research/spec/draft.md",
    "./commands/research/spec/plan.md",
    "./commands/research/spec/review.md",
    "./commands/research/draft.md",
    "./commands/research/plan.md",
    "./commands/research/refine.md",
    "./commands/research/review.md",
    "./commands/content/draft.md",
    "./commands/content/plan.md",
    "./commands/content/refine.md",
    "./commands/content/review.md",
    "./commands/post/spec.md",
    "./commands/post/plan.md",
    "./commands/post/draft.md",
    "./commands/post/refine.md",
    "./commands/post/review.md",
    "./commands/publish/seo-review.md",
    "./commands/publish/pre-check.md",
    "./commands/publish/promote.md",
    "./commands/publish/validate.md"
  ],
  "agents": [
    "./agents/research-synthesizer.md",
    "./agents/series-architect.md",
    "./agents/technical-editor.md"
  ],
  "skills": [
    "./skills/code-example-best-practices/SKILL.md",
    "./skills/content-structure-patterns/SKILL.md",
    "./skills/seo-for-developers/SKILL.md",
    "./skills/technical-writing-style/SKILL.md"
  ],
  "outputStyles": [
    "./styles/deep-dive-format.md",
    "./styles/dev-journal-format.md",
    "./styles/feedback-submission.md",
    "./styles/research-summary-format.md",
    "./styles/tutorial-format.md"
  ],
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json",
  "hooks": "./hooks/",
  "requiredDirectories": [
    "content/_projects",
    "content/_drafts",
    "content/_templates/personas",
    "content/_templates/outlines",
    "content/_templates/research-plans",
    "content/_templates/review-checklists",
    "content/_templates/brainstorm-plans"
  ]
}
```

### 2. Legacy Command Migration

The current plugin.json (v1.3.0) includes legacy commands that predate the redesign:

| Legacy Command | Action | Replacement |
|----------------|--------|-------------|
| `draft-post.md` | Deprecate | `/blog/post/draft` |
| `gather-resources.md` | Deprecate | `/blog/research/draft` |
| `outline-post.md` | Deprecate | `/blog/post/plan` |
| `publish-prep.md` | Deprecate | `/blog/publish/pre-check` |
| `refine-research-plan.md` | Deprecate | `/blog/research/spec/plan` |
| `research-topic.md` | Deprecate | `/blog/research/draft` |
| `seo-pass.md` | Deprecate | `/blog/publish/seo-review` |
| `series-plan.md` | Keep | Unique functionality |

**Migration strategy**:

1. Keep legacy commands in v2.0.0 with deprecation notices
2. Each legacy command prints: "DEPRECATED: Use /blog/X/Y instead"
3. Remove in v3.0.0

### 3. Plugin Directory Structure

```text
context/plugins/blog-workflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── init.md                 # Initialization command
│   ├── idea/
│   │   ├── brainstorm.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   └── draft-plan.md
│   ├── persona/
│   │   ├── draft.md
│   │   ├── plan.md
│   │   └── review.md
│   ├── template/
│   │   ├── draft.md
│   │   ├── plan.md
│   │   └── review.md
│   ├── research/
│   │   ├── spec/
│   │   │   ├── draft.md
│   │   │   ├── plan.md
│   │   │   └── review.md
│   │   ├── draft.md
│   │   ├── plan.md
│   │   ├── refine.md
│   │   └── review.md
│   ├── content/
│   │   ├── draft.md
│   │   ├── plan.md
│   │   ├── refine.md
│   │   └── review.md
│   ├── post/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── draft.md
│   │   ├── refine.md
│   │   └── review.md
│   └── publish/
│       ├── seo-review.md
│       ├── pre-check.md
│       ├── promote.md
│       └── validate.md
├── .templates/
│   ├── outlines/           # 18 outline templates
│   ├── personas/           # practitioner.md, educator.md
│   ├── research-plans/     # standard.md
│   ├── review-checklists/  # All phase checklists
│   └── brainstorm-plans/   # standard.md
├── hooks/
│   ├── validate-blog-frontmatter.sh
│   └── promote-safety.sh
├── agents/
│   ├── research-synthesizer.md
│   ├── series-architect.md
│   └── technical-editor.md
├── skills/
│   ├── code-example-best-practices/
│   ├── content-structure-patterns/
│   ├── seo-for-developers/
│   └── technical-writing-style/
├── styles/
│   ├── deep-dive-format.md
│   ├── dev-journal-format.md
│   ├── feedback-submission.md
│   ├── research-summary-format.md
│   └── tutorial-format.md
├── rules/
│   └── blog-workflow.md
├── README.md
└── CHANGELOG.md
```

### 4. Command Namespacing

Plugin commands invoked with `/blog/` namespace:

```text
/blog/init                 → ./commands/init.md
/blog/idea/brainstorm      → ./commands/idea/brainstorm.md
/blog/research/spec/draft  → ./commands/research/spec/draft.md
/blog/post/review          → ./commands/post/review.md
/blog/persona/draft        → ./commands/persona/draft.md
/blog/publish/promote      → ./commands/publish/promote.md
```

---

## `/blog/init` Command

### Frontmatter

```yaml
---
name: blog/init
description: Initialize blog workflow directory structure and copy default templates
arguments:
  - name: force
    description: Overwrite existing templates
    required: false
  - name: no-templates
    description: Create directories only, skip template copying
    required: false
---
```

### Behavior

**Tools**: `Read`, `Write`, `Bash`, `Glob`

**Logic**:

1. **Check existing structure**:
   - Use `Glob` to check if `content/_templates/` exists
   - If exists and `--force` not set, report what already exists

2. **Create directory structure**:

   ```bash
   mkdir -p content/_projects
   mkdir -p content/_drafts
   mkdir -p content/_templates/personas
   mkdir -p content/_templates/outlines
   mkdir -p content/_templates/research-plans
   mkdir -p content/_templates/review-checklists
   mkdir -p content/_templates/brainstorm-plans
   ```

3. **Copy bundled templates** (unless `--no-templates`):
   - Read each template from plugin `.templates/`
   - Write to corresponding `content/_templates/` location
   - Track what was created vs skipped

4. **Create hooks directory** (optional):

   ```bash
   mkdir -p .claude/hooks
   ```

   - Copy hook scripts if user wants local customization

5. **Self-review**:
   - Verify all directories exist
   - Verify template files copied correctly
   - Report any errors

6. **Report summary**:

   ```text
   ## Blog Workflow Initialized

   Created directories:
   - content/_projects/
   - content/_drafts/
   - content/_templates/personas/
   - content/_templates/outlines/
   - content/_templates/research-plans/
   - content/_templates/review-checklists/
   - content/_templates/brainstorm-plans/

   Copied templates:
   - 18 outline templates
   - 2 persona templates (practitioner.md, educator.md)
   - 1 research plan template
   - 6 review checklists
   - 1 brainstorm plan template

   Next steps:
   1. Review personas in content/_templates/personas/
   2. Start with: /blog/idea/brainstorm "Your topic"
   ```

### Example Usage

```text
# Full initialization
/blog/init

# Directories only
/blog/init --no-templates

# Overwrite existing
/blog/init --force
```

---

## Template Bundling

### Plugin Templates (`.templates/`)

Templates bundled with the plugin for distribution:

```text
.templates/
├── outlines/
│   ├── algorithm-deep-dive.outline.md
│   ├── api-integration.outline.md
│   ├── architecture-decision.outline.md
│   ├── comparison.outline.md
│   ├── conference-paper-blog.outline.md
│   ├── debug-error.outline.md
│   ├── experiment.outline.md
│   ├── first-look.outline.md
│   ├── getting-started.outline.md
│   ├── how-i-built.outline.md
│   ├── library-evaluation.outline.md
│   ├── literature-review.outline.md
│   ├── novel-computing.outline.md
│   ├── performance.outline.md
│   ├── principal-eng.outline.md
│   ├── security.outline.md
│   ├── staff-eng.outline.md
│   └── tutorial.outline.md
├── personas/
│   ├── practitioner.md
│   └── educator.md
├── research-plans/
│   └── standard.md
├── review-checklists/
│   ├── idea.md
│   ├── plan.md
│   ├── research-plan.md
│   ├── research-findings.md
│   ├── research-analysis.md
│   ├── content-brainstorm.md
│   ├── post-spec.md
│   ├── post-outline.md
│   ├── post-draft.md
│   └── seo.md
└── brainstorm-plans/
    └── standard.md
```

### Target Project Templates (`content/_templates/`)

After `/blog/init`, user's project has:

```text
content/_templates/
├── outlines/           # Copied from plugin
├── personas/           # Copied, user customizes
├── research-plans/     # Copied from plugin
├── review-checklists/  # Copied from plugin
└── brainstorm-plans/   # Copied from plugin
```

---

## Hook Configuration

### Plugin Hooks Directory

```text
hooks/
├── validate-blog-frontmatter.sh
└── promote-safety.sh
```

### Hook Delegation Model

Hooks have two layers for flexibility:

**Plugin Layer** (in plugin directory):

- Contains the actual implementation
- Fires on configured events
- Can check for repo-local overrides

**Repo Layer** (optional, in project `.claude/hooks/`):

- User customizations
- Override plugin behavior
- Work independently of plugin

### Delegation Script Pattern

```bash
#!/bin/bash
# Plugin hook that checks for repo-local override first
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
REPO_OVERRIDE="${CLAUDE_PROJECT_ROOT:-.}/.claude/hooks/${SCRIPT_NAME}"

# If repo has a local override, use it
if [ -f "$REPO_OVERRIDE" ]; then
  exec "$REPO_OVERRIDE" "$@"
fi

# Otherwise, run plugin implementation
# ... plugin logic here ...
```

### Settings.json Configuration

For projects using the plugin, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in content/_drafts/*|content/_projects/*) ~/.claude/plugins/blog-workflow/hooks/validate-blog-frontmatter.sh \"$FILE\";; esac; true'",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in src/data/blog/*) ~/.claude/plugins/blog-workflow/hooks/promote-safety.sh \"$FILE\";; esac; true'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## README.md

````markdown
# Blog Workflow Plugin

Multi-phase blog content creation with personas, templates, and iterative review.

## Installation

```bash
claude plugin install blog-workflow
```

## Quick Start

1. Initialize the workflow in your project:

   ```text
   /blog/init
   ```

2. Start with an idea:

   ```text
   /blog/idea/brainstorm "Your topic here"
   ```

3. Review and refine:

   ```text
   /blog/idea/review content/_projects/<slug>/idea.md
   ```

4. Continue through phases: research → content → post → publish

## Commands

### Initialization

| Command | Purpose |
|---------|---------|
| `/blog/init` | Set up directories and copy templates |

### Ideation (`/blog/idea/*`)

| Command | Purpose |
|---------|---------|
| `brainstorm` | Start a new idea from raw concept |
| `review` | Evaluate idea or plan |
| `refine` | Improve based on feedback |
| `draft-plan` | Create project plan from approved idea |

### Research (`/blog/research/*`)

| Command | Purpose |
|---------|---------|
| `spec/draft` | Create research plan |
| `spec/plan` | Refine research plan |
| `spec/review` | Evaluate research plan |
| `draft` | Execute research |
| `plan` | Create analysis from findings |
| `refine` | Update research artifacts |
| `review` | Evaluate analysis + compile report |

### Content Planning (`/blog/content/*`)

| Command | Purpose |
|---------|---------|
| `draft` | Brainstorm content pieces |
| `plan` | Decompose into phases |
| `refine` | Update content plan |
| `review` | Validate decomposition |

### Post Writing (`/blog/post/*`)

| Command | Purpose |
|---------|---------|
| `spec` | Create post specification |
| `plan` | Create outline from spec |
| `draft` | Write full draft |
| `refine` | Update post artifacts |
| `review` | Evaluate draft quality |

### Publishing (`/blog/publish/*`)

| Command | Purpose |
|---------|---------|
| `seo-review` | Optimize for search |
| `pre-check` | Validate before publish |
| `promote` | Move to live location |
| `validate` | Verify build success |

### Meta Commands

| Command | Purpose |
|---------|---------|
| `/blog/persona/*` | Manage authorial personas |
| `/blog/template/*` | Manage structural templates |

## Configuration

The plugin expects these directories in your project:

- `content/_projects/` - Project files
- `content/_drafts/` - Post drafts
- `content/_templates/` - Personas, outlines, checklists

Run `/blog/init` to create this structure automatically.

## Personas

Define authorial voice in `content/_templates/personas/<name>.md`.
Two personas included by default: `practitioner.md` and `educator.md`.

## Templates

Outline templates in `content/_templates/outlines/` define post structure.
18 templates included covering tutorials, deep-dives, experiments, and more.

## Hooks

The plugin includes validation hooks:

- **validate-blog-frontmatter.sh** - Validates artifact frontmatter on save
- **promote-safety.sh** - Prevents accidental writes to `src/data/blog/`

Customize by copying to `.claude/hooks/` in your project.
````

---

## Tasks

### Setup

- [ ] Update plugin manifest to v2.0.0
- [ ] Add `commands` array with all phase commands
- [ ] Create `commands/init.md` initialization command
- [ ] Add deprecation notices to legacy commands

### Templates

- [ ] Verify all 18 outline templates in `.templates/outlines/`
- [ ] Create `educator.md` persona (practitioner.md exists)
- [ ] Verify all review checklists in `.templates/review-checklists/`
- [ ] Verify `brainstorm-plans/standard.md` exists

### Hooks

- [ ] Update hook scripts with delegation pattern
- [ ] Document settings.json configuration
- [ ] Test hook delegation to repo-local overrides

### Documentation

- [ ] Write plugin README.md
- [ ] Update CHANGELOG.md with v2.0.0 changes
- [ ] Document migration from legacy commands

### Registration

- [ ] Update `.claude-plugin/marketplace.json` to v2.0.0
- [ ] Verify plugin validates with `claude plugin validate`

### Testing

- [ ] Test `/blog/init` creates structure
- [ ] Test `/blog/init --force` overwrites
- [ ] Test `/blog/init --no-templates` directories only
- [ ] Test all commands via `/blog/` namespace
- [ ] Test legacy command deprecation notices

---

## Acceptance Tests

### Installation

- [ ] Plugin installs via `claude plugin install blog-workflow`
- [ ] Plugin validates without errors
- [ ] All 31 commands accessible

### Initialization

- [ ] `/blog/init` creates all required directories
- [ ] `/blog/init` copies all bundled templates
- [ ] `/blog/init` reports what was created
- [ ] `/blog/init --force` overwrites existing templates
- [ ] `/blog/init --no-templates` creates directories only
- [ ] Running `/blog/init` twice without `--force` skips existing files

### Commands

- [ ] `/blog/idea/brainstorm` invokes same workflow as local command
- [ ] `/blog/research/spec/draft` works with nested path
- [ ] All phase commands accessible via `/blog/` prefix
- [ ] Commands read repo-local personas via `Read` tool
- [ ] Commands read repo-local templates via `Read` tool

### Hooks

- [ ] Plugin hooks fire on configured events
- [ ] Repo-local hook overrides take precedence
- [ ] Plugin hooks no-op gracefully if validation passes
- [ ] Removing plugin doesn't break repo-local hooks

### Templates

- [ ] Plugin bundle includes all 18 outline templates
- [ ] Plugin bundle includes both seed personas
- [ ] Plugin bundle includes all review checklists
- [ ] Plugin bundle includes `brainstorm-plans/standard.md`
- [ ] Plugin bundle includes `research-plans/standard.md`

### Migration

- [ ] Legacy commands print deprecation notices
- [ ] Legacy commands still function in v2.0.0
- [ ] Documentation explains migration path

### Error Handling

- [ ] Missing `content/_templates/` gives clear error pointing to `/blog/init`
- [ ] Invalid persona reference gives helpful error
- [ ] Invalid template reference gives helpful error

---

## Dependencies

- Phase 0-6 complete (all commands implemented)

## Estimated Effort

3-4 hours

---

## Version History

| Version | Changes |
|---------|---------|
| 2.0.0 | Full redesign: phases, personas, templates, hooks |
| 1.3.0 | Added research commands |
| 1.2.0 | Added persona/template commands |
| 1.1.0 | Initial workflow commands |
