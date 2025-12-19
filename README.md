# AI Configuration Library

Shareable source of truth for AI-related configurations: rules, skills, commands, hooks, context, and MCP server definitions.

## Architecture

```
Project .claude/  ──promote──▶  ai/ (source)  ──build──▶  global (~/.claude/)
                                    │
                                    ▼
                              dotfiles/
                          (deployment layer)
```

This repo contains atomic, reusable components that can be composed into tool-specific configurations based on machine profiles.

## Directory Structure

```
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
git submodule add git@github.com:aRustyDev/ai.git ai/
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

See [Issue #1](https://github.com/aRustyDev/ai/issues/1) for full details.

## Legacy Content

Previous content is preserved in `legacy/` during migration. This includes:
- `agents/` - Agent definitions
- `commands/` - Slash commands
- `rules/` - Instruction rules
- `skills/` - Skill definitions
- `plugins/` - Various plugins
- `roles/` - Role definitions
- `context/` - Context documents
- And more...

Content will be migrated to the new structure over time.

## License

MIT
