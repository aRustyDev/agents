---
description: Promote an MCP server configuration to the AI Config Library
argument-hint: <config-path>
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Bash(mkdir:*), Bash(cp:*), AskUserQuestion
---

# Promote MCP Config

Promote an MCP server configuration from the current project to the aRustyDev/agents repository.

## Arguments

- `$1` - Path to the MCP config file. Example: `settings/mcp/github-tools.yaml`

## Configuration

```bash
AI_REPO="${AI_CONFIG_REPO:-$(git config --file .gitmodules --get submodule.ai.path 2>/dev/null || echo "$HOME/repos/configs/ai")}"
```

## Workflow

### Phase 1: Validate and Analyze

1. **Verify config exists**:
   - Confirm the config file exists
   - Verify valid YAML syntax
   - Check for `mcpServers` key

2. **Extract config metadata**:
   - Parse server names from config
   - Identify command type (npx, uvx, docker, direct)
   - Note any env var requirements

3. **Check for existing config in ai repo**:

   ```bash
   ls "$AI_REPO/settings/mcp/"
   ```

4. **Security review**:
   - Flag any hardcoded API keys (should use env vars)
   - Note any sensitive paths

5. **Check for existing branch/issue/PR**:

   ```bash
   git -C "$AI_REPO" branch --list "feat/add-mcp-<name>"
   gh issue list --repo aRustyDev/agents --search "[MCP] <name> in:title"
   ```

### Phase 2: User Decision (if existing)

If existing config found, ask user:

1. **Upgrade existing** - Replace with new version
2. **Merge servers** - Add new servers to existing config
3. **Create separate** - Use different filename
4. **Cancel** - Abort

### Phase 3: Sanitize Config

Before promoting:

- Replace hardcoded values with env var references
- Add comments documenting required env vars
- Ensure consistent formatting

### Phase 4: Create Issue and PR

1. **Create GitHub Issue** with:
   - Server names
   - Command types
   - Required env vars
   - Features/tools provided

2. **Create feature branch**: `feat/add-mcp-<name>`

3. **Copy config file**:

   ```bash
   cp "<path>" "$AI_REPO/settings/mcp/<name>.yaml"
   ```

4. **Commit and push**

5. **Create PR**

### Phase 5: Report

| Item | URL |
|------|-----|
| Issue | `<url>` |
| PR | `<url>` |

**Installation**:

```bash
# Add to Claude Code settings
claude mcp add --config settings/mcp/<name>.yaml
```

## Examples

```bash
/context:mcp:promote settings/mcp/github-tools.yaml
/context:mcp:promote settings/mcp/database-suite.yaml
```

## Related Commands

- `/context:mcp:create` - Create a new MCP config
- `/context:mcp:review` - Review config quality
- `/context:mcp:search` - Find MCP servers
