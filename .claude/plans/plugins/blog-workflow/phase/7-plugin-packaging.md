# Phase 7: Plugin Packaging

## Objective

Extract into a marketplace plugin with proper namespacing and delegation.

## Deliverables

### 1. Plugin Manifest

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "blog-workflow",
  "version": "2.0.0",
  "description": "Multi-phase blog content creation with personas, templates, and iterative review",
  "author": {
    "name": "Adam Smith",
    "email": "developer@gh.arusty.dev"
  },
  "keywords": [
    "blog",
    "content",
    "writing",
    "persona",
    "workflow"
  ],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/blog-workflow",
  "repository": "https://github.com/aRustyDev/ai.git",
  "skills": [
    "./skills/init.md",
    "./skills/idea/brainstorm.md",
    "./skills/idea/review.md",
    "./skills/idea/refine.md",
    "./skills/idea/draft-plan.md",
    "./skills/research/spec/draft.md",
    "./skills/research/spec/plan.md",
    "./skills/research/spec/review.md",
    "./skills/research/draft.md",
    "./skills/research/plan.md",
    "./skills/research/refine.md",
    "./skills/research/review.md",
    "./skills/content/draft.md",
    "./skills/content/plan.md",
    "./skills/content/refine.md",
    "./skills/content/review.md",
    "./skills/post/spec.md",
    "./skills/post/plan.md",
    "./skills/post/draft.md",
    "./skills/post/refine.md",
    "./skills/post/review.md",
    "./skills/publish/seo-review.md",
    "./skills/publish/pre-check.md",
    "./skills/publish/promote.md",
    "./skills/publish/validate.md",
    "./skills/persona/draft.md",
    "./skills/persona/plan.md",
    "./skills/persona/review.md",
    "./skills/template/draft.md",
    "./skills/template/plan.md",
    "./skills/template/review.md"
  ],
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "Write|Edit",
      "command": "${CLAUDE_PROJECT_ROOT}/.claude/hooks/validate-blog-frontmatter.sh",
      "timeout": 5
    },
    {
      "event": "PreToolUse",
      "matcher": "Write",
      "command": "${CLAUDE_PROJECT_ROOT}/.claude/hooks/promote-safety.sh",
      "timeout": 5
    }
  ],
  "outputStyles": [
    "../../output-styles/feedback-submission.md"
  ],
  "requiredDirectories": [
    "content/_projects",
    "content/_drafts",
    "content/_templates/personas",
    "content/_templates/outlines",
    "content/_templates/research-plans",
    "content/_templates/review-checklists",
    "content/_templates/brainstorm-plans",
    "content/_templates/schemas"
  ]
}
```

### 2. Plugin Directory Structure

```text
context/plugins/blog-workflow/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── init.md                 # Initialization skill
│   ├── idea/
│   │   ├── brainstorm.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   └── draft-plan.md
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
│   ├── publish/
│   │   ├── seo-review.md
│   │   ├── pre-check.md
│   │   ├── promote.md
│   │   └── validate.md
│   ├── persona/
│   │   ├── draft.md
│   │   ├── plan.md
│   │   └── review.md
│   └── template/
│       ├── draft.md
│       ├── plan.md
│       └── review.md
├── templates/
│   ├── outlines/          # Default outline templates (18 files)
│   ├── personas/          # Default persona (practitioner.md)
│   ├── research-plans/    # Default research plan template
│   └── review-checklists/ # Review checklists
├── hooks/
│   ├── validate-blog-frontmatter.sh
│   └── promote-safety.sh
├── README.md
└── CHANGELOG.md
```

### 3. Command Namespacing

Plugin skills invoked with `blog:` namespace:

```text
/blog:idea:brainstorm      → ./skills/idea/brainstorm.md
/blog:research:draft       → ./skills/research/draft.md
/blog:post:review          → ./skills/post/review.md
/blog:persona:draft        → ./skills/persona/draft.md
/blog:publish:promote      → ./skills/publish/promote.md
```

### 4. Hook Delegation

Hooks reference `${CLAUDE_PROJECT_ROOT}` to find repo-local scripts:

```bash
#!/bin/bash
# Plugin hook that delegates to repo-local
REPO_SCRIPT="${CLAUDE_PROJECT_ROOT}/.claude/hooks/validate-blog-frontmatter.sh"
if [ -f "$REPO_SCRIPT" ]; then
  exec "$REPO_SCRIPT" "$@"
fi
exit 0
```

### 5. Initialization Skill (`/blog:init`)

Create `skills/init.md` for first-run setup:

```markdown
---
name: blog:init
description: Initialize blog workflow in current project
---

## Purpose

Set up the blog workflow directory structure and copy default templates.

## Behavior

1. Check if `content/_templates/` exists
2. If not, create directory structure:
   - `content/_projects/`
   - `content/_drafts/`
   - `content/_templates/personas/`
   - `content/_templates/outlines/`
   - `content/_templates/research-plans/`
   - `content/_templates/review-checklists/`
   - `content/_templates/brainstorm-plans/`
   - `content/_templates/schemas/`
3. Copy bundled templates from plugin to repo:
   - All 18 outline templates
   - Seed personas (practitioner, educator)
   - Research plan template
   - Review checklists
   - Brainstorm plan template
4. Report what was created

## Usage

```

/blog:init

```text

## Flags

- `--force`: Overwrite existing templates
- `--no-templates`: Create directories only
```

### 6. Default Templates Bundling

Plugin bundles templates for distribution at `templates/`:

```text
templates/
├── outlines/           # 18 outline templates
├── personas/           # practitioner.md, educator.md
├── research-plans/     # standard.md
├── review-checklists/  # idea.md, plan.md, research-plan.md, content-plan.md, post-draft.md, seo.md
├── brainstorm-plans/   # standard.md
└── schemas/            # artifact-schema.md
```

The `/blog:init` skill copies these to the user's `content/_templates/`.

### 7. Hook Delegation Model

Hooks have two layers:

**Plugin Layer** (in plugin cache):

- Stub scripts that delegate to repo
- Fire on the configured events
- No-op if repo scripts don't exist

**Repo Layer** (in project `.claude/hooks/`):

- Actual implementation
- Can be customized per-project
- Work independently of plugin

**Delegation Script Pattern**:

```bash
#!/bin/bash
# Plugin hook that delegates to repo-local implementation
REPO_SCRIPT="${CLAUDE_PROJECT_ROOT}/.claude/hooks/validate-blog-frontmatter.sh"
if [ -f "$REPO_SCRIPT" ]; then
  exec "$REPO_SCRIPT" "$@"
else
  # No repo script - either skip or use bundled default
  exit 0
fi
```

This allows:

- Plugin works out-of-box (delegates to repo scripts created by init)
- Users can customize hooks without modifying plugin
- Removing plugin doesn't break existing hooks

### 8. README.md

````markdown
# Blog Workflow Plugin

Multi-phase blog content creation with personas, templates, and iterative review.

## Installation

```bash
claude plugin install blog-workflow
```

## Quick Start

1. Start with an idea:

   ```text
   /blog:idea:brainstorm "Your topic here"
   ```

2. Review and refine:

   ```text
   /blog:idea:review content/_projects/<slug>/idea.md
   ```

3. Continue through phases: research → content → post → publish

## Commands

### Ideation (`/blog:idea:*`)
- `brainstorm` - Start a new idea
- `review` - Evaluate idea/plan
- `refine` - Improve based on feedback
- `draft-plan` - Create project plan

### Research (`/blog:research:*`)
- `spec:draft` - Plan research
- `draft` - Execute research
- `review` - Compile report

... [etc]

## Configuration

The plugin expects these directories in your project:
- `content/_projects/` - Project files
- `content/_drafts/` - Post drafts
- `content/_templates/` - Personas, outlines, checklists

## Personas

Define authorial voice in `content/_templates/personas/<name>.md`.
See `practitioner.md` for an example.

## Templates

Outline templates in `content/_templates/outlines/` define post structure.
18 templates included by default.
````

## Tasks

- [ ] Create plugin manifest `plugin.json`
- [ ] Restructure skills into `skills/` directory
- [ ] Create `skills/init.md` initialization skill
- [ ] Move hooks to plugin `hooks/` directory
- [ ] Create hook delegation scripts (stubs that delegate to repo)
- [ ] Bundle default templates in plugin `templates/` directory
- [ ] Include all review checklists in bundle
- [ ] Include brainstorm-plans template
- [ ] Write plugin README
- [ ] Update CHANGELOG
- [ ] Register in marketplace.json
- [ ] Test installation flow
- [ ] Test `/blog:init` creates structure and copies templates
- [ ] Test all commands via `blog:` namespace
- [ ] Verify repo-local hook overrides work

## Acceptance Tests

- [ ] Plugin installs via `claude plugin install`
- [ ] `/blog:idea:brainstorm` invokes same workflow as local command
- [ ] All phase commands accessible via `blog:` prefix
- [ ] Plugin skills read repo-local personas/templates via `Read` tool
- [ ] Plugin hooks delegate to repo-local scripts when present
- [ ] Plugin hooks no-op gracefully if repo scripts don't exist
- [ ] Removing plugin doesn't break repo-local commands
- [ ] Missing `content/_templates/` gives clear error pointing to `/blog:init`
- [ ] `/blog:init` creates all required directories
- [ ] `/blog:init` copies all bundled templates to repo
- [ ] `/blog:init --force` overwrites existing templates
- [ ] Plugin bundle includes all 18 outline templates
- [ ] Plugin bundle includes both seed personas
- [ ] Plugin bundle includes all review checklists
- [ ] Plugin bundle includes brainstorm-plans/standard.md

## Dependencies

- Phase 0-6 complete (all commands implemented)

## Estimated Effort

2-3 hours
