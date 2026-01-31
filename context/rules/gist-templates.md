# Gist-Based Templates

Template files are stored in GitHub Gists for reuse across projects. This rule defines how to discover, use, and maintain templates.

## Quick Reference

### Discover Templates
```bash
# List all template gists
gh gist list --filter templates

# List available template keys
just list-gists

# Filter by category
just list-gists lang
just list-gists github
```

### Apply Templates
```bash
# Apply a template (uses underscore keys)
just apply-gist common
just apply-gist lang_rust
just apply-gist github_labels_mcp

# With options
just apply-gist lang_rust type=lib
just apply-gist lang_rust type=bin --dry-run

# Remove a template
just remove-gist lang_rust
```

### Automation Justfile
- **GitHub**: https://github.com/aRustyDev/just/blob/main/modules/templates/justfile
- **CDN**: https://just.arusty.dev/templates/justfile

---

## Naming Convention

| Gist Description | Justfile Key |
|------------------|--------------|
| `templates.hbs(github/workflows)` | `github_workflows` |
| `templates.hbs(lang/rust)` | `lang_rust` |
| `templates.hbs(github/labels/mcp-server)` | `github_labels_mcp` |

**Rule**: Descriptions use `/` for readability; keys use `_` for machine parsing.

---

## Category Reference

| Category | Purpose | When to Use |
|----------|---------|-------------|
| `common` | Universal files | Every project (CoC, CONTRIBUTING, gitignore) |
| `github/*` | GitHub configs | Workflows, rulesets, labels, issues, PRs |
| `lang/*` | Language tooling | Language-specific setup (Cargo.toml, pyproject.toml) |
| `registry/*` | Distribution | Publishing to registries (homebrew, helm, npm) |
| `focus/*` | Project-type configs | Curated pre-commit configs by language |
| `obsidian/*` | Obsidian vault | Note templates, plugins, fileClasses |
| `platform/*` | Platform configs | Cloudflare, Docker (non-GitHub platforms) |

### Subtype Composition

GitHub subtypes can be **project type** OR **language**. They compose:

```bash
# Rust MCP server gets BOTH:
just apply-gist github_labels_rust    # Language labels
just apply-gist github_labels_mcp     # Project-type labels
```

---

## When to Use Templates

### Suggest Templates When:
- Setting up a **new project from scratch**
- Configuring an **empty repository**
- Adding **standard GitHub config** (workflows, labels, issues)
- Setting up a **new language** in a project

### Suggest Updating Templates When:
- Discovering a **reusable configuration** pattern
- Improving an **existing template** based on project experience
- Adding a **missing file** that belongs in an existing gist

---

## When to Update vs Create

### Update Existing Gist (Preferred)
- File fits the gist's scope and purpose
- Adding a missing configuration to an existing category
- Improving existing template content

### Create New Gist
- Content doesn't align with any existing gist
- New category or subcategory needed
- After checking related gists and confirming no fit

### Decision Process
1. Check if file fits an existing gist's scope
2. Scan related gists for better fit
3. If unsure, **ask the user**
4. Only create new gist if no existing fit

---

## Workflow for Template Changes

### Applying Templates
1. **Check available templates**: `just list-gists`
2. **Preview changes**: `just apply-gist <key> --dry-run`
3. **Apply**: `just apply-gist <key>`
4. **Modify locally** if needed for project-specific adjustments

### Contributing Back to Templates
1. **Apply template first** to local project
2. **Make local modifications** as needed
3. **Evaluate**: Are changes project-specific or universally useful?
4. **If universal**: Propose updating the gist
5. **Always consult user** before modifying gists

---

## Gist Structure Requirements

Every template gist **must** have:

| File | Required | Purpose |
|------|----------|---------|
| `<category>.just` | **Yes** | Install/uninstall recipes |
| `hbs.json` | If variables needed | Flat key-value variable map |
| `.env` | If secrets needed | Public values or `op://` URLs |
| `README.md` | Preferred | Documentation with frontmatter |

### Install Pipeline
```
hbs.json → mustache → 1Password (if op://) → envsubst → destination
```

### Required Justfile Recipes
```just
install *FLAGS:    # Supports --dry-run
uninstall *FLAGS:  # Supports --dry-run
```

---

## Secrets Handling

- Templates do **not require** secrets
- If a secret IS needed, it **must** use 1Password `op://` URL syntax
- Never hardcode secrets in templates

---

## README Frontmatter

If a gist has a README, it must include frontmatter:

```yaml
---
schema: https://schema.arusty.dev/draft/2020-12/frontmatter.schema.json
title: Template Name
id: <uuidv4>
description: What this template provides
version: 1.0.0
status: <emoji> "status"
tags: [category, subcategory]
authors:
  - name <email>
related:
  - <uuidv4>           # local file
  - <uuidv4>@<project> # remote file
  - https://url        # external resource
---
```

---

## Caution Areas

- **Be very cautious** modifying justfile recipes
- **Always consult user** before adding/updating gists
- **Explain reasoning** for proposed changes
- **Test with --dry-run** before applying

---

## File Conflicts

| Scenario | Resolution |
|----------|------------|
| Same file from multiple gists | Append → uniq (no sort) |
| Key conflicts in structured files | Latest write wins |

---

## Full Strategy

See `.ai/plans/gist-templates-strategy.md` for:
- Complete hierarchy
- Implementation priority
- Detailed category definitions
- Example convenience recipes
