---
description: Create a new MCP server configuration
argument-hint: <server-name> [--type stdio|sse]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion, Glob
---

# Create MCP Server Config

Create a new MCP server configuration file for use with Claude Code.

## Arguments

- `$1` - Server name (lowercase, hyphenated). Example: `github-tools`
- `--type` - Transport type:
  - `stdio` (default): Standard I/O transport
  - `sse`: Server-Sent Events transport

## Workflow

### Step 1: Parse and Validate

1. Extract server name from `$1`
2. Validate format: `^[a-z][a-z0-9-]{0,30}[a-z0-9]$`
3. Parse `--type` (default: `stdio`)
4. Determine target path: `settings/mcp/<server-name>.yaml`
5. Check if config exists — ask to overwrite

### Step 2: Gather Server Information

Use AskUserQuestion to collect:

1. **Server Command**: How to start the server?
   - npx command (e.g., `npx @modelcontextprotocol/server-github`)
   - uvx command (e.g., `uvx mcp-server-sqlite`)
   - Direct path (e.g., `/usr/local/bin/my-server`)

2. **Environment Variables**: Any required env vars?
   - API keys
   - Configuration options

3. **Arguments**: Command-line arguments needed?

### Step 3: Check for Existing Configs

Search for similar configs:

```text
Glob: settings/mcp/*.yaml
```

If related config found, ask if this should extend or replace.

### Step 4: Create Config File

Write `settings/mcp/<server-name>.yaml`:

```yaml
# <Server Name> MCP Server
# <brief description>

mcpServers:
  <server-name>:
    command: <command>
    args:
      - <arg1>
      - <arg2>
    env:
      <VAR_NAME>: <value>
```

For SSE type:

```yaml
mcpServers:
  <server-name>:
    url: <sse-url>
    transport: sse
```

### Step 5: Validate

1. Check YAML syntax is valid
2. Verify command exists (if local)
3. Test basic connectivity (optional)

### Step 6: Report

```text
## MCP Server Config Created

| Field | Value |
|-------|-------|
| Server | <name> |
| Location | settings/mcp/<name>.yaml |
| Type | stdio/sse |

**To use:**
1. Copy to your project's `.claude/settings.json`
2. Or merge into `~/.claude/settings.json`

**Test with:**
```

claude --mcp-config settings/mcp/<name>.yaml

```text
```

## Examples

```bash
# Create a GitHub MCP server config
/context:mcp:create github-tools

# Create an SSE-based server config
/context:mcp:create remote-api --type sse
```

## Related Commands

- `/context:mcp:search` - Find existing MCP servers
- `/context:mcp:review` - Review config quality
