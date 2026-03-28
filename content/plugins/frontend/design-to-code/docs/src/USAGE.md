# Usage

## Installation

```bash
# Install the plugin
just install-plugin design-to-code

# Install dependencies
cd content/plugins/design-to-code
brew bundle
```

## Quick Start

1. **Enable the plugin** in your Claude Code settings
2. **Configure MCP servers**:
   - Set `FIGMA_ACCESS_TOKEN` for Figma integration
   - Install Penpot MCP server locally
   - Ensure Sketch app is installed for Sketch integration
3. **Enable MCP servers**: `just enable-mcp design-to-code`
4. **Try a command**: `/extract-tokens`

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/extract-tokens` | Extract design tokens from a design file | `/extract-tokens design.sketch` |
| `/generate-component` | Convert design selection to code | `/generate-component --framework swiftui` |
| `/sync-design-system` | Sync design tokens to codebase | `/sync-design-system --target ./tokens/` |
| `/export-assets` | Export and optimize assets | `/export-assets --platform ios` |
| `/compare-design` | Compare implementation to design | `/compare-design --file component.swift` |

## Skills

| Skill | Description | Invocation |
|-------|-------------|------------|
| `design-tokens-extraction` | Extract colors, fonts, spacing from designs | Via `/extract-tokens` |
| `design-to-swiftui` | Convert designs to SwiftUI views | Via `/generate-component --framework swiftui` |
| `design-to-react` | Convert designs to React components | Via `/generate-component --framework react` |
| `design-to-flutter` | Convert designs to Flutter widgets | Via `/generate-component --framework flutter` |
| `design-to-tailwind` | Generate Tailwind config from designs | Via `/generate-component --framework tailwind` |
| `design-system-management` | Manage design system tokens | Via `/sync-design-system` |
| `asset-optimization` | Optimize images and icons | Via `/export-assets` |
| `accessibility-audit` | Check designs for WCAG compliance | Automatic with token extraction |

## Agents

| Agent | Description | Use Case |
|-------|-------------|----------|
| `design-translator` | Multi-step design to code workflow | Complex component conversion |
| `design-system-architect` | Create comprehensive design systems | Full design system setup |
| `asset-pipeline` | Batch process assets | Multi-platform asset export |

## Configuration

### MCP Servers

| Server | Purpose | Configuration |
|--------|---------|---------------|
| `sketch-context` | Read Sketch files | Requires Sketch app |
| `penpot` | Read Penpot designs | Local build required |
| `figma` | Read Figma files | Requires `FIGMA_ACCESS_TOKEN` |
| `iconify` | Search icon libraries | No config needed |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIGMA_ACCESS_TOKEN` | Figma API access token | For Figma integration |
| `PENPOT_MCP_PORT` | Penpot MCP server port | Default: 4401 |

## Examples

### Example 1: Extract Tokens from Figma

```bash
# Extract design tokens from a Figma file
/extract-tokens --source figma --file-key abc123 --output ./tokens/design-tokens.json
```

### Example 2: Generate SwiftUI Component

```bash
# Convert a design component to SwiftUI
/generate-component --framework swiftui --component "HeaderView" --output ./Sources/Views/
```

### Example 3: Sync Design System

```bash
# Sync tokens from Figma to your codebase
/sync-design-system --source figma --target ./Sources/Theme/
```

## Integration

### With swiftui-dev Plugin

This plugin complements the `swiftui-dev` plugin:

- Use `design-to-code` for design extraction and token generation
- Use `swiftui-dev` for SwiftUI implementation and testing

### Output Formats

| Format | Use Case | Output Style |
|--------|----------|--------------|
| JSON (W3C) | Platform-agnostic tokens | `design-token-json` |
| Swift | iOS/macOS apps | `design-token-swift` |
| CSS | Web applications | `design-token-css` |
| Tailwind | Tailwind CSS projects | `design-token-tailwind` |

## Next Steps

- See [Troubleshooting](./TROUBLESHOOTING.md) for common issues
- Check the [CHANGELOG](../../CHANGELOG.md) for recent updates
- Read [CONTRIBUTING](../../CONTRIBUTING.md) to contribute
