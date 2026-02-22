# Plugin Research: design-to-code

## Existing Plugins

| Plugin | Domain | Coverage | Recommendation |
|--------|--------|----------|----------------|
| swiftui-dev | iOS UI development | 15% | reference (has sketch/penpot MCP for handoff) |
| frontend-dev | Web frontend | 10% | reference (component generation target) |
| browser-extension-dev | Browser extensions | 5% | reference (CSS generation target) |

No existing plugin covers design-to-code workflows directly. This is a new domain.

## Component Research

### Skills

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| design-tokens-extraction | design-brand-applying-dev | local | 60% | **extend** - has color/font specs, needs extraction logic |
| design-to-swiftui | (none) | - | 0% | **create** |
| design-to-react | (none) | - | 0% | **create** |
| design-to-flutter | (none) | - | 0% | **create** |
| design-to-tailwind | (none) | - | 0% | **create** |
| design-system-management | design-theme-factory-dev | local | 50% | **extend** - has themes, needs token management |
| asset-optimization | (none) | - | 0% | **create** |
| accessibility-audit | (none) | - | 0% | **create** |

### Commands

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| /extract-tokens | (none) | - | 0% | **create** |
| /generate-component | (none) | - | 0% | **create** |
| /sync-design-system | (none) | - | 0% | **create** |
| /export-assets | (none) | - | 0% | **create** |
| /compare-design | (none) | - | 0% | **create** |

### Agents

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| design-translator | ui-designer | local | 40% | **extend** - has design system knowledge, needs translation logic |
| design-system-architect | (none) | - | 0% | **create** |
| asset-pipeline | (none) | - | 0% | **create** |

### Output Styles

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| design-token-json | (none) | - | 0% | **create** |
| design-token-swift | (none) | - | 0% | **create** |
| design-token-css | (none) | - | 0% | **create** |
| design-token-tailwind | (none) | - | 0% | **create** |
| component-spec | (none) | - | 0% | **create** |

### Hooks

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| validate-design-tokens | (none) | - | 0% | **create** |

### MCP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| sketch-context-mcp | sketch-context-mcp | [GitHub](https://github.com/jshmllr/sketch-context-mcp) | 100% | **reuse** - `npx sketch-context-mcp` |
| penpot-mcp | penpot-mcp | [GitHub](https://github.com/penpot/penpot-mcp) | 100% | **reuse** - official, requires local build |
| figma-mcp | figma-mcp | [Figma Official](https://developers.figma.com/docs/figma-mcp-server/) | 100% | **reuse** - official Figma server, desktop or remote |
| iconify-mcp | iconify-mcp-server | [GitHub](https://github.com/imjac0b/iconify-mcp-server) | 100% | **reuse** - `npx iconify-mcp-server@latest` |

### LSP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| design-tokens-lsp | design-tokens-language-server | [Blog](https://bennypowers.dev/posts/introducing-design-tokens-language-server/) | 90% | **reuse** - autocomplete for design tokens |

## MCP Server Details

### Figma MCP (Official)
- **Source**: [Figma Developer Docs](https://developers.figma.com/docs/figma-mcp-server/)
- **Install**: Desktop app integration or remote endpoint `https://mcp.figma.com/mcp`
- **Features**: Read design metadata, frames, components, design tokens, layout constraints
- **Priority**: should (widely used design tool)

### Sketch Context MCP
- **Source**: [GitHub](https://github.com/jshmllr/sketch-context-mcp)
- **Install**: `npx sketch-context-mcp --local-file=/path/to/file.sketch`
- **Features**: get_file, list_components, get_selection, create_rectangle, create_text
- **Priority**: must (already in swiftui-dev)

### Penpot MCP (Official)
- **Source**: [GitHub](https://github.com/penpot/penpot-mcp)
- **Install**: Local build required (npm install && npm run bootstrap)
- **Features**: Data retrieval, design modification, code-to-design workflows
- **Priority**: must (already in swiftui-dev)

### Iconify MCP
- **Source**: [GitHub](https://github.com/imjac0b/iconify-mcp-server)
- **Install**: `npx iconify-mcp-server@latest`
- **Features**: Search 200k+ icons, get icon sets, retrieve icon data with framework examples
- **Priority**: nice (useful for asset workflows)

## Summary

- **Reuse**: 5 components (4 MCP servers, 1 LSP server)
- **Extend**: 3 components (2 skills, 1 agent)
- **Create**: 19 components (6 skills, 5 commands, 2 agents, 5 output styles, 1 hook)

## Key Insights

1. **Design tool integration is well-covered** - Official MCP servers exist for Figma, Penpot, and community servers for Sketch
2. **Code generation is a gap** - No existing skills for design-to-code translation (SwiftUI, React, Flutter, Tailwind)
3. **Local design skills provide foundation** - `design-brand-applying-dev` and `design-theme-factory-dev` can be extended
4. **LSP support exists** - `design-tokens-language-server` provides IDE autocomplete for tokens
