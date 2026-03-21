---
description: Create plugin directory structure from template using roadmap data
argument-hint: <plugin-name> <roadmap-path>
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(cp:*), Bash(ls:*), Glob
---

# Scaffold Plugin

Create a plugin directory from `.template/` and populate it with metadata from the brainstorm and roadmap.

## Arguments

- `$1` - Plugin name (lowercase, hyphenated). Example: `terraform-dev`
- `$2` - Path to roadmap document. Example: `.plans/plugins/terraform-dev/roadmap.md`

## Output

`context/plugins/<plugin-name>/`

## Workflow

### Step 1: Validate Inputs

1. Validate plugin name: `^[a-z][a-z0-9-]{0,46}[a-z0-9]$`
2. Read roadmap at `$2`
3. Read brainstorm from same directory (`.plans/plugins/<plugin-name>/brainstorm.md`)
4. Check if `context/plugins/<plugin-name>/` already exists — ask to overwrite or abort

### Step 2: Copy Template

```bash
cp -r context/plugins/.template/ context/plugins/<plugin-name>/
```

### Step 3: Generate plugin.json

Read the template `context/plugins/.template/.claude-plugin/plugin.json` and populate:

```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "<purpose from brainstorm>",
  "author": {
    "name": "Adam Smith",
    "email": "developer@gh.arusty.dev",
    "url": "https://im.arusty.dev"
  },
  "homepage": "https://docs.arusty.dev/ai/plugins/<plugin-name>",
  "repository": "https://github.com/aRustyDev/agents.git",
  "license": "MIT",
  "keywords": ["<domain>", "<relevant keywords>"],
  "commands": [],
  "agents": [],
  "skills": [],
  "mcpServers": "./.mcp.json",
  "outputStyles": ["../../output-styles/feedback-submission.md"],
  "lspServers": "./.lsp.json"
}
```

**Important:**

- Use **empty arrays** for commands, agents, skills (NOT directory paths)
- Always include `feedback-submission.md` in outputStyles for consistent feedback formatting
- Do NOT include `"hooks"` field — `hooks/hooks.json` is auto-loaded by Claude Code
- Populate arrays with explicit file paths as components are added

Write to `context/plugins/<plugin-name>/.claude-plugin/plugin.json`.

### Step 4: Generate plugin.sources.json

For all **Reuse** items in the roadmap, create a sources mapping:

```json
{
  "sources": [
    {
      "name": "<component-name>",
      "type": "<skill|command|agent|style|hook|mcp|lsp>",
      "path": "<source path from research>"
    }
  ]
}
```

Write to `context/plugins/<plugin-name>/.claude-plugin/plugin.sources.json`.

### Step 5: Generate .mcp.json

For MCP servers marked as **Reuse** or **Extend** in the roadmap, create server entries:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<install command>",
      "args": ["<args>"]
    }
  }
}
```

Write to `context/plugins/<plugin-name>/.mcp.json`.

### Step 6: Generate .lsp.json

For any LSP servers identified in the roadmap:

```json
{
  "lspServers": {}
}
```

Write to `context/plugins/<plugin-name>/.lsp.json`.

### Step 7: Generate brewfile

Collect all brew dependencies from MCP servers and tools in the roadmap:

```text
# <plugin-name> dependencies
brew "<dep1>"
brew "<dep2>"
```

Write to `context/plugins/<plugin-name>/brewfile`.

### Step 8: Generate README.md

```markdown
# <Plugin Name>

<Purpose from brainstorm>

## Components

| Type | Count | Status |
|------|-------|--------|
| Skills | N | N reuse, N create |
| Commands | N | ... |
| Agents | N | ... |
| Styles | N | ... |
| Hooks | N | ... |
| MCP Servers | N | ... |
| LSP Servers | N | ... |

## Setup

1. Install dependencies: `just install-plugin <plugin-name>`
2. Enable MCP servers: `just enable-mcp <plugin-name>`

## Roadmap

See `.plans/plugins/<plugin-name>/roadmap.md` for the full development plan.
```

Write to `context/plugins/<plugin-name>/README.md`.

### Step 9: Customize Documentation

Update template placeholders in documentation files:

1. **CHANGELOG.md**: Replace `<plugin-name>` with actual plugin name in version links
2. **CONTRIBUTING.md**: Replace `<plugin-name>` placeholders
3. **docs/src/USAGE.md**: Replace `<plugin-name>` and `<command-N>` placeholders
4. **docs/src/TROUBLESHOOTING.md**: Replace `<plugin-name>` placeholders

#### Feedback Infrastructure (Auto-Configured)

The following feedback mechanisms are automatically set up:

| File | Feedback Feature |
|------|------------------|
| `plugin.json` | References `feedback-submission.md` output style |
| `TROUBLESHOOTING.md` | "Getting Help" links to bug reports, "Share Your Success" links to discussions |
| `CONTRIBUTING.md` | "Sharing Success Stories" section with Show and Tell link |

**Verify** these links are correct and add plugin-specific feedback guidance if needed (e.g., common issues, success story examples).

### Step 10: Add to Marketplace

Add a new entry to `.claude-plugin/marketplace.json` in the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./context/plugins/<plugin-name>",
  "description": "<purpose from brainstorm>",
  "version": "0.1.0",
  "author": {
    "name": "Adam Smith",
    "email": "developer@gh.arusty.dev"
  },
  "keywords": ["<keywords from brainstorm>"],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/<plugin-name>",
  "repository": "https://github.com/aRustyDev/agents.git"
}
```

**Important:** This step ensures the plugin is discoverable and version-tracked centrally.

### Step 11: Report

```text
## Plugin Scaffolded

| Field | Value |
|-------|-------|
| Plugin | <name> |
| Location | context/plugins/<name>/ |
| Marketplace | .claude-plugin/marketplace.json |

### Generated Files

| Category | Files |
|----------|-------|
| Configuration | plugin.json, plugin.sources.json, .mcp.json, .lsp.json, brewfile |
| Documentation | README.md, CHANGELOG.md, CONTRIBUTING.md |
| Docs Book | docs/src/USAGE.md, docs/src/TROUBLESHOOTING.md, docs/src/SUMMARY.md |
| Feedback | feedback-submission.md (referenced), bug/feature/success story links |

**Next step**: `/generate-plugin-issues .plans/plugins/<name>/roadmap.md`
```

## Examples

```text
/scaffold-plugin terraform-dev .plans/plugins/terraform-dev/roadmap.md
/scaffold-plugin rust-projects .plans/plugins/rust-projects/roadmap.md
```
