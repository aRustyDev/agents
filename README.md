# AI Configuration Library

Shareable source of truth for AI-related configurations: rules, skills, commands, hooks, context, and MCP server definitions.

## Architecture

```text
Project .claude/  ──promote──▶  ai/ (source)  ──build──▶  global (~/.claude/)
                                    │
                                    ▼
                              dotfiles/
                          (deployment layer)
```

This repo contains atomic, reusable components that can be composed into tool-specific configurations based on machine profiles.

## Directory Structure

```text
ai/
├── components/          # Atomic, reusable pieces
│   ├── rules/           # Instruction rules (schema'd JSON, future)
│   ├── skills/          # Claude Code skills (SKILL.md + files)
│   ├── commands/        # Slash command templates
│   ├── hooks/           # Hook definitions
│   └── context/         # Shared context fragments
│
├── profiles/            # Machine/use-case profiles (future)
│   ├── personal.profile.json
│   ├── work.profile.json
│   └── minimal.profile.json
│
├── tools/               # Tool-specific output schemas (future)
│   ├── claude-code/
│   ├── zed/
│   ├── claude-desktop/
│   └── vscode/
│
├── mcp/                 # MCP server definitions
│   ├── global/          # Remote/HTTP MCP servers
│   └── local/           # Project-scoped MCP templates
│
├── schemas/             # JSON schemas for validation (future)
├── build/               # Build/compile tooling (future)
├── dist/                # Generated output (gitignored)
│
└── legacy/              # Previous content (migrating from)
```

## Usage

### As a Submodule (Recommended)

```bash
# In your dotfiles repo
git submodule add git@github.com:aRustyDev/agents.git ai/
git submodule update --init --recursive
```

### Installing Components

For now, manually copy components to target locations:

```bash
# Claude Code
cp -r ai/components/commands/* ~/.claude/commands/
cp -r ai/components/skills/* ~/.claude/skills/
cp -r ai/components/rules/* ~/.claude/rules/
```

Future: Use `just ai-build` and `just ai-deploy` from dotfiles repo.

## Plugin Marketplace

This repo includes a plugin marketplace at `.claude-plugin/marketplace.json` with curated plugin bundles.

### Available Plugins

| Plugin | Description |
|--------|-------------|
| `homebrew-dev` | Homebrew formula development toolkit |
| `browser-extension-dev` | Cross-browser extension development (Firefox, Chrome, Safari) |
| `blog-workflow` | Technical blog post creation workflow |
| `job-hunting` | Job hunting toolkit (resume, applications, research) |
| `swiftui-dev` | SwiftUI development with testing and data analytics |

### Installing a Plugin

```bash
# Clone or add as submodule
git clone https://github.com/aRustyDev/agents.git ~/ai-plugins

# Copy a plugin to your Claude Code config
cp -r ~/ai-plugins/context/plugins/homebrew-dev ~/.claude/plugins/

# Or symlink for auto-updates
ln -s ~/ai-plugins/context/plugins/homebrew-dev ~/.claude/plugins/homebrew-dev
```

### Adding This Marketplace

To use this marketplace as a plugin source:

1. **Via settings.json** (Claude Code):

```json
{
  "pluginMarketplaces": [
    {
      "name": "arustydev",
      "url": "https://raw.githubusercontent.com/aRustyDev/agents/main/.claude-plugin/marketplace.json"
    }
  ]
}
```

2. **Via ccpm** (Claude Code Plugin Manager):

```bash
ccpm registry add arustydev https://raw.githubusercontent.com/aRustyDev/agents/main/.claude-plugin/marketplace.json
ccpm search swiftui
ccpm install arustydev/swiftui-dev
```

3. **Via local clone**:

```bash
# Add to your .claude/settings.json
{
  "pluginMarketplaces": [
    {
      "name": "arustydev-local",
      "path": "~/repos/ai/.claude-plugin/marketplace.json"
    }
  ]
}
```

### Marketplace Schema

Each plugin entry in `marketplace.json` follows this structure:

```json
{
  "name": "plugin-name",
  "source": "./context/plugins/plugin-name",
  "description": "What the plugin does",
  "version": "1.0.0",
  "keywords": ["keyword1", "keyword2"],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/plugin-name",
  "repository": "https://github.com/aRustyDev/agents.git"
}
```

## Workflow

### 1. Develop in Project

Create/test configs in your project's `.claude/` directory.

### 2. Promote to Source

```bash
# Future: promote-component script
cp -r .claude/skills/new-skill/ ~/repos/configs/ai/components/skills/
cd ~/repos/configs/ai
git add -A && git commit -m "feat: add new-skill"
git push
```

### 3. Deploy to Global

```bash
# On each machine
cd ~/repos/configs/dotfiles
git submodule update --remote ai/
just install-ai
```

## Roadmap

- [x] Phase 1: Directory structure and legacy migration
- [ ] Phase 2: Basic promote/build/deploy workflow
- [ ] Phase 3: JSON schemas and compilation
- [ ] Phase 4: Profiles and dynamic MCP config generation

See [Issue #1](https://github.com/aRustyDev/agents/issues/1) for full details.

## Legacy Content

Previous content is preserved in `legacy/` during migration. This includes:

### From arustydev/agents (archived)

- `agents/` - Agent definitions

### From arustydev/prompts (archived)

- `prompts/commands/` - Slash commands (/audit, /plan, /report, etc.)
- `prompts/processes/` - Workflow processes (CI/CD, code-review, testing)
- `prompts/core/` - Core patterns (error handling, validation, git operations)
- `prompts/patterns/` - Development patterns (BDD, TDD, CDD)
- `prompts/templates/` - Issue, report, and documentation templates
- `prompts/roles/` - Role definitions (developer levels, security engineer)
- `prompts/guides/` - Tool usage guides
- `prompts/knowledge/` - Knowledge bases
- `prompts/hooks/` - Validation hooks and scripts
- `prompts/automation/` - Automation scripts
- `prompts/docs/` - Architecture and planning documentation

### Original legacy

- `commands/` - Slash commands
- `rules/` - Instruction rules
- `skills/` - Skill definitions
- `plugins/` - Various plugins
- `roles/` - Role definitions
- `context/` - Context documents
- And more...

Content will be migrated to the new structure over time. Valuable content can be promoted to `components/` using the `/promote-skill` command or similar workflows.

## Merged Repositories

The following repositories have been archived and merged into this repo:

- **arustydev/agents** → `legacy/agents/`
- **arustydev/prompts** → `legacy/prompts/`

See `.ai/plans/merge-agents-prompts.md` for the full merge plan and history.

## License

MIT
