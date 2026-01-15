# Gist-Based Templates Strategy

## Overview

Template files are stored in GitHub Gists using a hierarchical naming convention. This document defines the structure, conventions, and guidelines for creating and maintaining template gists.

---

## Naming Convention

### Gist Description Format
```
templates.hbs(<category>[/<subcategory>[/<specific>]])
```

### Justfile Key Format
Gist descriptions use `/` for human readability, but justfile lookup keys use `_` (underscores).

| Gist Description (Human) | Justfile Key (Machine) |
|--------------------------|------------------------|
| `templates.hbs(github/workflows)` | `github_workflows` |
| `templates.hbs(lang/rust)` | `lang_rust` |
| `templates.hbs(github/labels/mcp-server)` | `github_labels_mcp` |

---

## Required Gist Structure

### Mandatory Files

Every gist **must** include a justfile named `<category>.just` (e.g., `lang_rust.just`).

### Required Justfile Recipes

```just
# Install templates to destination
# Supports --dry-run flag
install *FLAGS:
    #!/usr/bin/env bash
    # Pipeline: hbs.json → mustache → 1Password (if needed) → envsubst → destination

# Remove installed templates
# Supports --dry-run flag
uninstall *FLAGS:
    #!/usr/bin/env bash
    # Remove files installed by this gist
```

### Optional Files

| File | Purpose |
|------|---------|
| `README.md` | Documentation (preferred, must have frontmatter if included) |
| `hbs.json` | Flat key-value map of template variables |
| `.env` | Public values or `op://` URLs for 1Password secrets |
| `*.hbs` | Handlebars/Mustache template files |

### Install Pipeline

```
hbs.json → mustache template → 1Password secrets (if op://) → envsubst/eval → destination
```

**Secrets**: Templates do not require secrets, but if a secret IS needed, it MUST use 1Password `op://` URL syntax.

---

## README Frontmatter Schema

If a gist includes a README.md, it **must** have frontmatter:

```markdown
---
schema: https://schema.arusty.dev/draft/2020-12/frontmatter.schema.json
title: Rust Library Template
id: <uuidv4>
description: Base configuration for Rust library projects
version: 1.0.0
status: <emoji> "status string"
tags:
  - lang
  - rust
  - lib
authors:
  - john doe <jdoe@example.com>
  - claude opus-4.5 <feedback@anthropic.com>
related:
  - <uuidv4>                              # local file
  - <uuidv4>@<project-id>                 # remote file in <project-id>
  - https://foo.bar.com/path/to/resource.md
---

# Title
```

---

## Category Hierarchy

### Category Definitions

| Category | Purpose | Examples |
|----------|---------|----------|
| `common` | Universal project files | CoC, CONTRIBUTING, gitignore, SECURITY |
| `github/*` | GitHub-specific files and configs | workflows, rulesets, labels, issues, prs |
| `lang/*` | Language tooling and configs | rust, python, go, javascript |
| `registry/*` | Distribution registry configs | homebrew, helm, npm, pre-commit |
| `focus/*` | Project-type specific configs | precommit configs, curated labels/issues |
| `obsidian/*` | Obsidian vault configs | templates, fileClasses, plugins |

### Category Distinction

- **`lang/*`**: Language tooling (Cargo.toml, pyproject.toml, go.mod, linters, formatters)
- **`registry/*`**: Distribution registries (homebrew formulas, helm charts, npm publishing)

### Removed Categories

- ~~`platform/*`~~ → Merged into `github/*` or appropriate category
  - `platform/cloudflare` → Keep as-is (not GitHub-related)
  - `platform/github` → Merge into `github/*`
  - `platform/docker` → Keep as-is (not GitHub-related)

---

## Language Templates

Language templates use **conditional logic** for subtypes rather than separate gists.

### Structure
```
templates.hbs(lang/rust)
├── Cargo.toml.hbs           # Has lib/bin conditional sections
├── rust-toolchain.toml
├── clippy.toml
├── rustfmt.toml
├── .gitignore
├── deny.toml
├── hbs.json
└── lang_rust.just
```

### Usage with Subtypes
```bash
# Library project
just apply-gist lang_rust type=lib

# Binary project
just apply-gist lang_rust type=bin
```

### Language Gist Justfile Pattern
```just
install type="lib" *FLAGS:
    #!/usr/bin/env bash
    # type can be: lib, bin
    # Conditionally include/exclude sections based on type
```

---

## GitHub Templates

GitHub templates follow a subtype pattern for project types and languages.

### Structure
```
templates.hbs(
├── github                           # Root: FUNDING, dependabot, renovate
├── github/workflows                 # GitHub Actions
├── github/rulesets                  # Core branch protection
├── github/rulesets/strict           # Strict protection (signed commits, etc.)
├── github/rulesets/oss              # OSS-friendly rules
├── github/labels/<type|lang>        # Labels by project type or language
├── github/issues/<type|lang>        # Issue templates by project type or language
├── github/prs/<type|lang>           # PR templates by project type or language
)
```

### Subtype Composition

Subtypes can be **either** a project type OR a language. They compose together.

Example for a Rust MCP server:
```bash
just apply-gist github_labels_rust       # Language-specific labels
just apply-gist github_labels_mcp        # Project-type labels
just apply-gist github_issues_mcp        # MCP-specific issue templates
```

---

## File Conflict Handling

### Merge Strategy

| Scenario | Strategy |
|----------|----------|
| Same file from multiple gists | Append → uniq (remove duplicate lines, no sort) |
| Key conflicts in structured files | Latest write wins |
| Append-only vs overwrite | Not distinguished (evaluate if needed later) |

---

## Automation Justfile

The template system is automated via:

- **GitHub**: https://github.com/aRustyDev/just/blob/main/modules/templates/justfile
- **CDN**: https://just.arusty.dev/templates/justfile

### Core Recipes

| Recipe | Purpose |
|--------|---------|
| `apply-gist <key> [--dry-run]` | Clone gist and run its install recipe |
| `remove-gist <key> [--dry-run]` | Clone gist and run its uninstall recipe |
| `list-gists [filter]` | List available template gists |
| `init-github` | Apply all GitHub templates |
| `init-obsidian` | Apply all Obsidian templates |

### Gist ID Registry

Gist IDs are stored in the justfile's `gists` JSON object:

```just
gists := """
    {
        "common": "3d2a93d76c023eba50a2d037e36cf28e",
        "github": "c60f1e34d9d2afdc78f9383abad01108",
        "github_workflows": "a1c2a0a87b3fd9ca22f369198058b8f4",
        "lang_rust": "<gist-id>",
        "github_labels_mcp": "<gist-id>"
    }
    """
```

---

## Agent Guidelines

### When to Suggest Templates

| Scenario | Action |
|----------|--------|
| New project from scratch | Proactively suggest applicable templates |
| Configuring empty repo | Suggest templates based on project type/language |
| Discovered reusable config | Suggest updating or creating a template |

### Update vs Create Decision

1. **Update existing gist**: Preferred when adding files that fit the gist's scope
2. **Scan related gists**: Check if the file fits better elsewhere
3. **Analyze purpose**: If unsure, ask the user
4. **Create new gist**: Only if content doesn't align with existing gists

### Workflow for Template Changes

1. **Apply template first**: Install to local project
2. **Modify locally**: Make project-specific adjustments
3. **Evaluate changes**: Determine if modifications should go back to the gist
4. **Consult user**: Always discuss intent before updating gists

### Caution Areas

- **Be very cautious** when modifying justfile recipes
- **Always consult the user** before adding or updating a gist
- **Explain reasoning** for proposed changes

---

## Complete Hierarchy

```
templates.hbs(
├── common                           # Base project files
│
├── github                           # GitHub root (FUNDING, dependabot, renovate)
├── github/workflows                 # GitHub Actions
├── github/rulesets                  # Core rulesets
├── github/rulesets/strict           # Strict rulesets
├── github/rulesets/oss              # OSS rulesets
├── github/labels/<type|lang>        # Labels by type or language
├── github/issues/<type|lang>        # Issue templates by type or language
├── github/prs/<type|lang>           # PR templates by type or language
│
├── lang/rust                        # Rust (with type=lib|bin)
├── lang/python                      # Python
├── lang/go                          # Go
├── lang/javascript                  # JavaScript/TypeScript
│
├── registry/homebrew                # Homebrew tap
├── registry/helm                    # Helm charts
├── registry/npm                     # NPM publishing
├── registry/pre-commit              # Pre-commit hook registry
│
├── focus/precommit/<lang>           # Curated pre-commit configs by language
│
├── obsidian                         # Obsidian root
├── obsidian/templates               # Note templates
├── obsidian/fileClasses             # FileClass definitions
├── obsidian/plugin/<name>           # Plugin-specific configs
│
├── platform/cloudflare              # Cloudflare Workers/Pages
└── platform/docker                  # Docker/containers
)
```

---

## Implementation Priority

### Phase 1: Core Extensions
1. `lang/rust` (with type=lib|bin)
2. `lang/python`
3. `registry/homebrew`
4. `platform/cloudflare`

### Phase 2: GitHub Subtypes
5. `github/labels/mcp-server`
6. `github/labels/rust`
7. `github/issues/mcp-server`
8. `github/issues/pre-commit-hooks`

### Phase 3: Additional Languages
9. `lang/go`
10. `lang/javascript`
11. `registry/helm`
12. `registry/pre-commit`

### Phase 4: Focus & PRs
13. `focus/precommit/rust`
14. `focus/precommit/python`
15. `github/prs/library`
