# Usage

> **Note**: Replace `blog-workflow` with your actual plugin name throughout this document.

## Installation

```bash
# Install the plugin
just install-plugin blog-workflow

# Install dependencies
cd context/plugins/blog-workflow
brew bundle
```

## Quick Start

1. **Enable the plugin** in your Claude Code settings
2. **Install MCP servers** (if any): `just enable-mcp blog-workflow`
3. **Try a command**: `/<command-name>`

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/<command-1>` | Description of command 1 | `/<command-1> arg1` |
| `/<command-2>` | Description of command 2 | `/<command-2> --flag` |

## Skills

| Skill | Description | Invocation |
|-------|-------------|------------|
| `skill-1` | Description of skill 1 | Automatic when relevant |
| `skill-2` | Description of skill 2 | Via `/skill-2` command |

## Agents

| Agent | Description | Use Case |
|-------|-------------|----------|
| `agent-1` | Description of agent 1 | Complex multi-step tasks |

## Configuration

### MCP Servers

This plugin uses the following MCP servers:

| Server | Purpose | Configuration |
|--------|---------|---------------|
| `server-1` | Description | `.mcp.json` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VAR_NAME` | Description | `default-value` |

## Examples

### Example 1: Basic Usage

```bash
# Description of what this example does
/<command> argument
```

### Example 2: Advanced Usage

```bash
# Description of advanced scenario
/<command> --option value
```

## Integration

### With Other Plugins

This plugin works well with:

- `other-plugin`: Description of integration

### CI/CD

Example GitHub Actions workflow:

```yaml
- name: Use plugin
  run: |
    # Plugin usage in CI
```

## Next Steps

- See [Troubleshooting](./TROUBLESHOOTING.md) for common issues
- Check the [CHANGELOG](../CHANGELOG.md) for recent updates
- Read [CONTRIBUTING](../CONTRIBUTING.md) to contribute
