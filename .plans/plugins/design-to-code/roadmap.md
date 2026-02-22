# Plugin Roadmap: design-to-code

## Summary

| Action | Count |
|--------|-------|
| Reuse  | 5     |
| Extend | 3     |
| Create | 19    |

---

## P0 — MVP

Core functionality for extracting design tokens and generating code for primary frameworks.

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path |
|-----------|------|-------------|
| sketch-context-mcp | mcp | `npx sketch-context-mcp` |
| penpot-mcp | mcp | local build from [penpot/penpot-mcp](https://github.com/penpot/penpot-mcp) |
| figma-mcp | mcp | Figma desktop app or `https://mcp.figma.com/mcp` |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| design-tokens-extraction | skill | design-brand-applying-dev | Add extraction logic from MCP server data, token normalization | medium |
| design-system-management | skill | design-theme-factory-dev | Add token CRUD, multi-format export, version tracking | medium |
| design-translator | agent | ui-designer | Add MCP integration, code generation pipelines, framework routing | large |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| design-to-swiftui | skill | Convert design specs to SwiftUI views with proper modifiers | design-tokens-extraction |
| /extract-tokens | command | Extract tokens from design file via MCP, output to chosen format | sketch-context-mcp, penpot-mcp, figma-mcp, design-tokens-extraction |
| /generate-component | command | Analyze design selection, generate code for target framework | design-translator, design-to-swiftui |
| design-token-json | style | W3C Design Tokens format output | - |
| design-token-swift | style | Swift Color/Font extension output | - |

---

## P1 — Enhancement

Additional framework support and design system tooling.

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path |
|-----------|------|-------------|
| iconify-mcp | mcp | `npx iconify-mcp-server@latest` |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| design-to-react | skill | Convert design specs to React components with CSS/styled-components | design-tokens-extraction |
| design-to-flutter | skill | Convert design specs to Flutter widgets with proper theming | design-tokens-extraction |
| design-to-tailwind | skill | Generate Tailwind config and utility classes from design specs | design-tokens-extraction |
| /sync-design-system | command | Sync tokens from design file to codebase, detect drift | design-system-management |
| /export-assets | command | Export and optimize images/icons for target platforms | iconify-mcp |
| design-system-architect | agent | Create comprehensive design systems from design files | design-tokens-extraction, design-system-management |
| design-token-css | style | CSS custom properties output | - |
| design-token-tailwind | style | Tailwind config.js theme output | - |
| component-spec | style | Design specification markdown document | - |
| asset-optimization | skill | Image/icon optimization for iOS, Android, web | iconify-mcp |

---

## P2 — Nice-to-have

Quality of life improvements and advanced features.

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path |
|-----------|------|-------------|
| design-tokens-lsp | lsp | [design-tokens-language-server](https://bennypowers.dev/posts/introducing-design-tokens-language-server/) |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| accessibility-audit | skill | Check designs for WCAG compliance (contrast, touch targets, etc.) | design-tokens-extraction |
| /compare-design | command | Visual diff between design file and implemented code | figma-mcp, sketch-context-mcp |
| asset-pipeline | agent | Batch process assets across multiple platforms | asset-optimization |
| validate-design-tokens | hook | Validate token JSON files on save | design-token-json |

---

## Dependency Graph

```
MCP Servers (foundation)
├── sketch-context-mcp ─┐
├── penpot-mcp ─────────┼──→ design-tokens-extraction ──→ design-to-swiftui
├── figma-mcp ──────────┘              │                    │
│                                      │                    ├──→ design-to-react
│                                      │                    ├──→ design-to-flutter
│                                      │                    └──→ design-to-tailwind
│                                      │
│                                      └──→ design-system-management
│                                                  │
│                                                  └──→ design-system-architect
│
├── iconify-mcp ──────────────────────────────────────→ asset-optimization
│                                                              │
│                                                              └──→ asset-pipeline
│
Commands
├── /extract-tokens ←── design-tokens-extraction + MCP servers
├── /generate-component ←── design-translator + design-to-* skills
├── /sync-design-system ←── design-system-management
├── /export-assets ←── iconify-mcp + asset-optimization
└── /compare-design ←── MCP servers (P2)

Output Styles (parallel, no dependencies)
├── design-token-json
├── design-token-swift
├── design-token-css
├── design-token-tailwind
└── component-spec
```

---

## Implementation Order

### Phase 1: Foundation (P0)
1. Configure MCP servers (sketch, penpot, figma)
2. Extend `design-tokens-extraction` skill
3. Create `design-token-json` and `design-token-swift` output styles
4. Create `/extract-tokens` command
5. Create `design-to-swiftui` skill
6. Extend `design-translator` agent
7. Create `/generate-component` command
8. Extend `design-system-management` skill

### Phase 2: Framework Expansion (P1)
1. Add `iconify-mcp` server
2. Create `design-to-react`, `design-to-flutter`, `design-to-tailwind` skills
3. Create remaining output styles
4. Create `/sync-design-system` and `/export-assets` commands
5. Create `design-system-architect` agent and `asset-optimization` skill

### Phase 3: Polish (P2)
1. Add `design-tokens-lsp` server
2. Create `accessibility-audit` skill
3. Create `/compare-design` command
4. Create `asset-pipeline` agent
5. Create `validate-design-tokens` hook
