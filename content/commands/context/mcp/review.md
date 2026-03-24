---
description: Review an MCP server configuration for correctness
argument-hint: <config-path>
allowed-tools: Read, Bash(command:*), Bash(npx:*), Bash(uvx:*)
---

# Review MCP Config

Analyze an MCP server configuration for correctness and best practices.

## Arguments

- `$1` - Path to MCP config file (required)

## Workflow

### Step 1: Load Config

1. Read config file at `$1`
2. Parse YAML structure
3. Identify server entries

### Step 2: Syntax Validation

Check:

- [ ] Valid YAML syntax
- [ ] Has `mcpServers` key
- [ ] Each server has `command` or `url`
- [ ] Args are array format
- [ ] Env vars are key-value pairs

### Step 3: Command Validation

For each server:

- [ ] Command executable exists
- [ ] Package is available (npx/uvx)
- [ ] Required env vars documented

### Step 4: Security Check

Flag potential issues:

- ⚠️ Hardcoded API keys (should use env vars)
- ⚠️ Wildcard permissions
- ⚠️ Unrestricted file access

### Step 5: Generate Report

```markdown
# MCP Config Review: <filename>

## Servers

| Server | Command | Status |
|--------|---------|--------|
| <name> | <cmd> | ✅/⚠️/❌ |

## Findings

### Issues

- <issues>

### Warnings

- <warnings>

## Recommendation

<Ready | Needs Fixes>
```

## Examples

```bash
/context:mcp:review settings/mcp/github-tools.yaml
```

## Related Commands

- `/context:mcp:create` - Create new config
- `/context:mcp:search` - Find MCP servers
