# Justfile Restructure Plan

## Goal

Reduce the justfile from ~93 recipes / 1212 lines to ~25 recipes / ~300 lines. Delete everything replaced by the agents CLI, delete TODO stubs, keep only what the CLI doesn't cover.

## Recipe Inventory

### KEEP — Root recipes (no group change)

| Recipe | Lines | Why Keep |
|--------|-------|----------|
| `default` | 4-5 | Just `--list` |
| `agents *args` | 16-17 | CLI entry point |
| `matrixng *args` | 20-22 | Viewer CLI entry point |

### KEEP — Install group

| Recipe | Lines | Why Keep |
|--------|-------|----------|
| `init` | 31 | Orchestrates all `_init-*` private recipes — no CLI equivalent |
| `_init-brew` | 35-37 | Homebrew deps |
| `_init-pre-commit` | 40-42 | Pre-commit hooks |
| `_init-bun` | 45-47 | Bun workspace install |
| `_init-python` | 50-52 | uv sync |
| `_init-docker` | 55 | Calls `mcp-up` |
| `_init-ollama` | 58-66 | Ollama model pull |
| `_init-db` | 69-71 | Calls `kg-init` |
| `install target='all'` | 93-95 | Symlink management to `~/.claude/` — unique, not in CLI |
| `_install-*` | 97-152 | Private helpers for install |
| `uninstall target='all'` | 155-157 | Reverse of install |
| `_uninstall-*` | 159-177 | Private helpers for uninstall |
| `list-claude` | 180-189 | List installed components in `~/.claude/` |

### KEEP — Docker group

| Recipe | Lines | Why Keep |
|--------|-------|----------|
| `mcp-up` | 75-78 | Docker compose up |
| `mcp-down` | 81-82 | Docker compose down |
| `mcp-logs` | 85-86 | Docker compose logs |
| `mcp-status` | 89-90 | Docker compose ps |

### KEEP — KG group (Python-based, not in agents CLI)

| Recipe | Lines | Why Keep |
|--------|-------|----------|
| `kg-init` | 1094-1095 | Python init-db.py |
| `kg-ingest` | 1099-1100 | Python embed.py ingest |
| `kg-search query` | 1109-1110 | Python embed.py search |
| `kg-watch` | 1124-1125 | Python watch-embed.py |
| `kg-dump` | 1129-1130 | Python init-db.py --dump |
| `kg-load` | 1133-1135 | Python init-db.py --load |
| `kg-rebuild` | 1150-1157 | Orchestrator: rm db + init + ingest + similarity + dump |

Note: `kg-check`, `kg-similar`, `kg-rebuild-embeddings`, `kg-stats` are available via `just agents kg <subcommand>`. Keep `kg-similarity` because `kg-rebuild` calls it. Keep only the ones CLAUDE.md references or that `_init-db` / `kg-rebuild` depends on.

### DELETE — Replaced by agents CLI

| Recipe | Lines | CLI Replacement |
|--------|-------|-----------------|
| `ls-tags` | 100-101 | `agents list --type skill --tags` |
| `create-skill` | 466-511 | `agents init --type skill <name>` |
| `validate-skill` | 514-571 | `agents lint --type skill <path>` |
| `list-skills` | 575-593 | `agents list --type skill` |
| `validate-all-skills` | 597-620 | `agents lint --type skill --all` |
| `validate-pillars` | 624-715 | `agents lint --type skill <name> --pillars` |
| `validate-all-lang-skills` | 719-763 | `agents lint --type skill --all --pillars` |
| `import-and-normalize` | 767-778 | `agents add --type skill <repo>` |
| `install-plugin` | 783-802 | `agents add --type plugin <name>` |
| `build-plugin` | 806-843 | `agents plugin build <name>` |
| `uninstall-plugin` | 847-859 | `agents remove --type plugin <name>` |
| `check-plugin-sources` | 863-875 | `agents plugin check <name>` |
| `list-plugins` | 879-888 | `agents list --type plugin` |
| `add-feedback-infra` | 892-984 | Not in CLI yet, but rarely used — delete |
| `add-feedback-infra-all` | 988-1002 | Delete |
| `plugin-hash` | 1006-1007 | `agents plugin hash <path>` |
| `plugin-hash-verify` | 1011-1012 | `agents plugin hash <path> --verify <expected>` |
| `plugin-verify-sources` | 1016-1024 | `agents plugin check <name>` |
| `plugin-check` | 1028-1037 | `agents lint --type plugin <name>` |
| `plugin-update` | 1041-1058 | `agents plugin update <name>` |
| `plugin-check-all` | 1062-1063 | `agents lint --type plugin --all` |
| `plugin-build-all` | 1067-1068 | `agents plugin build --all` |
| `plugin-update-all` | 1072-1073 | `agents plugin update --all` |
| `migrate-check` | 1077-1078 | One-time migration, already done |
| `migrate-plugin` | 1082-1083 | One-time migration, already done |
| `migrate-all-plugins` | 1087-1088 | One-time migration, already done |
| `mcp-stats` | 1161-1162 | `agents mcp stats` |
| `mcp-search` | 1165-1166 | `agents mcp search <query>` |
| `mcp-list` | 1169-1170 | `agents mcp list` |
| `mcp-show` | 1173-1174 | `agents mcp show <slug>` |
| `mcp-tools` | 1177-1178 | `agents mcp tools <slug>` |
| `list-external-skills` | 281-294 | `agents list --type skill --external` |
| `search-skills` | 298-314 | `agents search --type skill <query>` |
| `import-skill` | 318-375 | `agents add --type skill <repo>` |
| `import-skill-by-name` | 379-408 | `agents add --type skill <name>` |
| `list-registries` | 412-417 | `agents registry list` |
| `external-version` | 421-422 | `agents info --type skill <name>` |
| `check-external-updates` | 426-458 | `agents update --type skill --check` |
| `sync-anthropic-skills` | 202-249 | `agents update --type skill --upstream` |
| `check-anthropic-updates` | 253-267 | `agents update --type skill --upstream --check` |
| `anthropic-version` | 271-272 | `agents info --type skill --upstream` |

### DELETE — Unused KG recipes (available via agents kg subcommand)

| Recipe | Lines | CLI Replacement |
|--------|-------|-----------------|
| `kg-check` | 1104-1105 | `agents kg check` |
| `kg-similar` | 1114-1115 | `agents kg similar <entity>` |
| `kg-similarity` | 1119-1120 | `agents kg similarity` — BUT `kg-rebuild` calls it. Inline the call in `kg-rebuild` instead. |
| `kg-rebuild-embeddings` | 1139-1141 | `agents kg rebuild-embeddings` |
| `kg-stats` | 1145-1146 | `agents kg stats` |

### DELETE — TODO stubs

| Recipe | Lines | Why Delete |
|--------|-------|------------|
| `opencode` | 1180-1181 | Empty stub |
| `zed` | 1183-1184 | Empty stub |
| `vscode` | 1186-1187 | Empty stub |
| `windsurf` | 1189-1190 | Empty stub |
| `cursor` | 1192-1193 | Empty stub |
| `mcp-setup` | 1195-1196 | Empty stub |
| `sitemap` | 1198-1212 | Broken/incomplete |

### DELETE — Module declarations (content justfiles are dead code)

| Recipe | Lines | Why Delete |
|--------|-------|------------|
| `mod plugin` | 8 | content/plugins/justfile — not used, CLI handles everything |
| `mod skill` | 9 | content/skills/justfile — not used |
| `mod command` | 10 | content/commands/justfile — not used |
| `mod agent` | 11 | content/agents/justfile — not used |
| `mod rule` | 12 | content/rules/justfile — not used |

Verify these modules are unused: `grep -r 'just plugin\|just skill\|just command\|just agent\|just rule' .pre-commit-config.yaml CLAUDE.md docs/`

### DELETE — Variables (orphaned after recipe deletion)

| Variable | Line | Why Delete |
|----------|------|------------|
| `ANTHROPIC_SKILLS_REPO` | 193 | Used by deleted sync-anthropic-skills |
| `ANTHROPIC_VERSION_FILE` | 194 | Used by deleted sync-anthropic-skills |
| `ANTHROPIC_SKILL_MAP` | 198 | Used by deleted sync-anthropic-skills |
| `EXTERNAL_MANIFEST` | 276 | Used by deleted external recipes |
| `EXTERNAL_VERSION_DIR` | 277 | Used by deleted external recipes |
| `SKILL_TEMPLATE_DIR` | 462 | Used by deleted create-skill |

## References to Update

| File | Recipe Referenced | Action |
|------|------------------|--------|
| `CLAUDE.md:71` | `just kg-init` | Keep (recipe stays) |
| `CLAUDE.md:74` | `just kg-ingest` | Keep (recipe stays) |
| `CLAUDE.md:77` | `just kg-search "..."` | Keep (recipe stays) |
| `CLAUDE.md:80` | `just kg-watch` | Keep (recipe stays) |
| `CLAUDE.md:134` | `just skill external:check` | Change to `just agents update --type skill --check` |
| `CLAUDE.md:135` | `just kg-search "query"` | Keep |
| `.pre-commit-config.yaml:275` | `just --fmt --check` | Keep (justfile self-format, not a recipe) |

## Target justfile structure (~25 recipes, ~300 lines)

```
set unstable := true

default:                          # just --list

# Tools
[group('tools')]
agents *args                      # CLI entry point
matrixng *args                    # Viewer CLI entry point

# Variables
CLAUDE_DIR, EMBEDDING_MODEL

# Install
[group('install')]
init                              # Orchestrates _init-*
install target='all'              # Symlinks to ~/.claude/
uninstall target='all'
list-claude

# Private init helpers
_init-brew, _init-pre-commit, _init-bun, _init-python, _init-docker, _init-ollama, _init-db
# Private install/uninstall helpers
_install-all, _install-claude, _install-claude-{settings,commands,rules,skills,hooks}
_uninstall-all, _uninstall-claude

# Docker
[group('docker')]
mcp-up, mcp-down, mcp-logs, mcp-status

# KG (Python-based)
[group('kg')]
kg-init, kg-ingest, kg-search, kg-watch, kg-dump, kg-load, kg-rebuild (inline kg-similarity call)
```

## Acceptance Criteria

- [ ] `just --list` shows only ~25 recipes in clean groups: tools, install, docker, kg
- [ ] `just init` still works (all _init-* helpers present)
- [ ] `just install` / `just uninstall` / `just list-claude` work
- [ ] `just agents <verb> <type>` works
- [ ] `just matrixng build <workspace>` works
- [ ] `just kg-search "test"` works
- [ ] No broken references in `.pre-commit-config.yaml`, `CLAUDE.md`, or docs
- [ ] Content module justfiles (`content/*/justfile`) deleted or emptied
- [ ] All tests pass: `bun test packages/matrixng/ && bun test packages/cli/`
