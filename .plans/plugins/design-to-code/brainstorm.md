# Plugin Brainstorm: design-to-code

## Domain & Purpose

**Domain**: UI/UX Design Integration
**Purpose**: Bridge design tools and code generation, enabling seamless translation of design files into production-ready UI code across multiple frameworks.

## Use Cases

1. Extract design tokens (colors, typography, spacing) from Sketch/Penpot/Figma and generate framework-specific code
2. Convert design components to SwiftUI, React, Flutter, or CSS code
3. Maintain design system consistency across codebases
4. Export and optimize assets (icons, images) for target platforms
5. Validate implemented code against original designs

## Components

### Skills

| Name | Purpose | Priority |
|------|---------|----------|
| design-tokens-extraction | Extract colors, fonts, spacing, shadows from design files | must |
| design-to-swiftui | Convert design components to SwiftUI views | must |
| design-to-react | Convert design components to React/CSS | should |
| design-to-flutter | Convert design components to Flutter widgets | should |
| design-to-tailwind | Generate Tailwind CSS from design specs | should |
| design-system-management | Create/maintain design system tokens and documentation | must |
| asset-optimization | Export and optimize images, icons for platforms | should |
| accessibility-audit | Check designs for accessibility compliance (contrast, touch targets) | nice |

### Commands

| Name | Purpose | Priority |
|------|---------|----------|
| /extract-tokens | Extract design tokens from a design file | must |
| /generate-component | Convert selected design to code | must |
| /sync-design-system | Sync design tokens to codebase | should |
| /export-assets | Export and optimize assets | should |
| /compare-design | Compare implementation to design | nice |

### Agents

| Name | Purpose | Priority |
|------|---------|----------|
| design-translator | Multi-step workflow: analyze design → extract specs → generate code | must |
| design-system-architect | Create comprehensive design systems from designs | should |
| asset-pipeline | Batch process and optimize assets for multiple platforms | nice |

### Output Styles

| Name | Purpose | Priority |
|------|---------|----------|
| design-token-json | JSON format for design tokens | must |
| design-token-swift | Swift code for design tokens | must |
| design-token-css | CSS custom properties format | should |
| design-token-tailwind | Tailwind config format | should |
| component-spec | Design specification document | should |

### Hooks

| Name | Purpose | Priority |
|------|---------|----------|
| validate-design-tokens | Validate token files on save | nice |

### MCP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| sketch-context-mcp | Read Sketch design files | must |
| penpot-mcp | Read/write Penpot design files | must |
| figma-mcp | Read Figma design files (if available) | should |
| iconify-mcp | Icon library access | nice |

### LSP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| design-tokens-lsp | Autocomplete for design token references | nice |

## Summary

| Category | Must | Should | Nice | Total |
|----------|------|--------|------|-------|
| Skills   | 3    | 4      | 1    | 8     |
| Commands | 2    | 2      | 1    | 5     |
| Agents   | 1    | 1      | 1    | 3     |
| Styles   | 2    | 3      | 0    | 5     |
| Hooks    | 0    | 0      | 1    | 1     |
| MCP      | 2    | 1      | 1    | 4     |
| LSP      | 0    | 0      | 1    | 1     |
| **Total**| 10   | 11     | 6    | 27    |
