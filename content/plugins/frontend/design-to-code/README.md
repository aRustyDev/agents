# Design to Code

Bridge design tools and code generation, enabling seamless translation of design files into production-ready UI code across multiple frameworks.

## Use Cases

1. Extract design tokens (colors, typography, spacing) from Sketch/Penpot/Figma
2. Convert design components to SwiftUI, React, Flutter, or CSS code
3. Maintain design system consistency across codebases
4. Export and optimize assets (icons, images) for target platforms
5. Validate implemented code against original designs

## Components

| Type | Count | Status |
|------|-------|--------|
| Skills | 8 | 2 extend, 6 create |
| Commands | 5 | 5 create |
| Agents | 3 | 1 extend, 2 create |
| Styles | 5 | 5 create |
| Hooks | 1 | 1 create |
| MCP Servers | 4 | 4 reuse |
| LSP Servers | 1 | 1 reuse |

## Setup

1. Install dependencies:

   ```bash
   just install-plugin design-to-code
   ```

2. Configure MCP servers:
   - **Figma**: Set `FIGMA_ACCESS_TOKEN` environment variable
   - **Penpot**: Clone and build from <https://github.com/penpot/penpot-mcp>
   - **Sketch**: Requires Sketch app installed on macOS

3. Enable MCP servers:

   ```bash
   just enable-mcp design-to-code
   ```

## MCP Servers

| Server | Purpose | Setup |
|--------|---------|-------|
| sketch-context | Read Sketch design files | `npx sketch-context-mcp` |
| penpot | Read/write Penpot designs | Local build required |
| figma | Read Figma design files | Figma access token |
| iconify | Search 200k+ icons | `npx iconify-mcp-server` |

## Roadmap

See `.plans/plugins/design-to-code/roadmap.md` for the full development plan.

### P0 — MVP

- Design token extraction from Sketch/Penpot/Figma
- SwiftUI code generation
- `/extract-tokens` and `/generate-component` commands

### P1 — Enhancement

- React, Flutter, Tailwind code generation
- Design system sync and asset export
- Additional output formats

### P2 — Nice-to-have

- Accessibility auditing
- Visual diff between design and implementation
- Design tokens LSP autocomplete
