---
name: design-tokens-extraction
description: Extract design tokens (colors, typography, spacing, shadows) from Figma, Sketch, and Penpot design files via MCP servers and normalize to W3C format
created: 2026-02-22
updated: 2026-02-22
tags: [design, tokens, figma, sketch, penpot, w3c]
extends: design-brand-applying-dev
---

# Design Tokens Extraction

Extract and normalize design tokens from design files into standardized formats.

## Overview

This skill enables extraction of design tokens from Figma, Sketch, and Penpot design files using their respective MCP servers. Extracted tokens are normalized to the W3C Design Tokens Community Group format for platform-agnostic storage and conversion.

**This skill covers:**

- Connecting to design files via MCP servers (Figma, Sketch, Penpot)
- Extracting color, typography, spacing, and shadow tokens
- Normalizing extracted data to W3C DTCG format
- Converting to platform-specific formats (Swift, CSS, Tailwind)

**This skill does NOT cover:**

- Design file creation or modification
- Visual design decisions
- Component code generation (see `design-to-swiftui` skill)

## Quick Reference

### MCP Server Tools

| Server | Tool | Purpose |
|--------|------|---------|
| `figma` | `get_file` | Read Figma file structure |
| `figma` | `get_styles` | Extract published styles |
| `figma` | `get_local_variables` | Extract variables/tokens |
| `sketch-context` | `get_document` | Read Sketch document |
| `sketch-context` | `get_shared_styles` | Extract shared styles |
| `sketch-context` | `get_color_assets` | Extract color variables |
| `penpot` | `get_file` | Read Penpot file |
| `penpot` | `get_components` | List design components |

### Token Categories

| Category | Properties Extracted |
|----------|---------------------|
| Color | hex, rgb, hsl, opacity, description |
| Typography | family, size, weight, lineHeight, letterSpacing |
| Spacing | value (px, rem), description |
| Shadow | color, offsetX, offsetY, blur, spread |
| Border Radius | value (px, rem) |
| Duration | value (ms) |

## Workflow: Extract Tokens from Design File

### Step 1: Connect to Design Source

Determine the design source and use the appropriate MCP server:

**Figma:**

```text
Use figma MCP server with get_file tool
Input: file_key from Figma URL (e.g., "abc123" from figma.com/file/abc123/...)
```

**Sketch:**

```text
Use sketch-context MCP server with get_document tool
Input: file path to .sketch file
```

**Penpot:**

```text
Use penpot MCP server with get_file tool
Input: project_id and file_id from Penpot URL
```

### Step 2: Extract Raw Design Data

Query the MCP server for design tokens:

**Colors:**

1. Get published color styles (Figma: `get_styles`, Sketch: `get_shared_styles`)
2. Get color variables (Figma: `get_local_variables`, Sketch: `get_color_assets`)
3. Extract from component fills if no styles defined

**Typography:**

1. Get text styles from design system
2. Extract font family, size, weight, line height, letter spacing
3. Map font weights to numeric values (400, 500, 600, etc.)

**Spacing:**

1. Look for spacing tokens in variables/styles
2. Extract from auto-layout settings if available
3. Check for spacing scale documentation

**Shadows:**

1. Get effect styles (drop shadows, inner shadows)
2. Extract color, offset, blur, spread values

### Step 3: Normalize to W3C Format

Transform extracted data to W3C Design Tokens structure:

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "color": {
    "<category>": {
      "<name>": {
        "$value": "#hexcode",
        "$type": "color",
        "$description": "From design file"
      }
    }
  },
  "typography": {
    "fontFamily": { ... },
    "fontSize": { ... },
    "fontWeight": { ... }
  },
  "spacing": { ... },
  "shadow": { ... }
}
```

### Step 4: Output in Requested Format

Use the appropriate output style:

- `design-token-json` - W3C DTCG format (default)
- `design-token-swift` - Swift extensions
- `design-token-css` - CSS custom properties
- `design-token-tailwind` - Tailwind config

## Extraction Patterns

### Figma Color Extraction

When reading from Figma:

1. **Published Styles** (preferred):
   - Use `get_styles` with `style_type: "FILL"`
   - Returns named color styles with descriptions

2. **Variables** (Figma variables):
   - Use `get_local_variables`
   - Filter by `resolvedType: "COLOR"`
   - Group by collection name

3. **Component Fills** (fallback):
   - Traverse component nodes
   - Extract unique fill colors
   - Auto-generate names from component path

### Sketch Color Extraction

When reading from Sketch:

1. **Shared Styles**:
   - Use `get_shared_styles` with `style_type: "layer"`
   - Extract fill colors from style attributes

2. **Color Assets**:
   - Use `get_color_assets`
   - Returns swatch library colors

3. **Document Colors**:
   - Access document-level color palette
   - Often contains brand colors

### Penpot Color Extraction

When reading from Penpot:

1. **Color Library**:
   - Access file's color library
   - Returns named colors with metadata

2. **Component Colors**:
   - Extract from component definitions
   - Track color references

## Normalization Rules

### Color Normalization

| Source Format | Target Format |
|---------------|---------------|
| `rgba(r, g, b, a)` | `#RRGGBBAA` |
| `rgb(r, g, b)` | `#RRGGBB` |
| `hsl(h, s%, l%)` | `#RRGGBB` (converted) |
| `{ r, g, b }` (0-1) | `#RRGGBB` (scaled) |
| `{ r, g, b }` (0-255) | `#RRGGBB` |

### Typography Normalization

| Property | Source Variations | Target |
|----------|-------------------|--------|
| Font Size | `12px`, `0.75rem`, `12` | `"0.75rem"` or `12` |
| Font Weight | `"bold"`, `700`, `"semibold"` | `700` (numeric) |
| Line Height | `1.5`, `150%`, `24px` | `1.5` (unitless ratio) |
| Letter Spacing | `0.5px`, `0.02em` | `"0.02em"` |

### Naming Normalization

| Source Style | Target Style | Example |
|--------------|--------------|---------|
| `color/primary/500` | `color.primary.500` | Nested groups |
| `Primary Color` | `primaryColor` | camelCase |
| `primary-color` | `primaryColor` | camelCase |
| `PRIMARY_COLOR` | `primaryColor` | camelCase |

## Source Metadata

Preserve source information for traceability:

```json
{
  "color": {
    "primary": {
      "$value": "#2196F3",
      "$type": "color",
      "$extensions": {
        "com.figma": {
          "variableId": "VariableID:1234",
          "styleId": "S:abc123",
          "collectionName": "Brand Colors"
        }
      }
    }
  }
}
```

## Troubleshooting

### No Tokens Found

**Symptoms:** Extraction returns empty or minimal tokens

**Solution:**

1. Verify design file has published styles (not just local colors)
2. Check if using Figma variables vs. older style system
3. Look for design system component library
4. Try extracting from specific frames/components

### Authentication Failed

**Symptoms:** MCP server returns 401 or access denied

**Solution:**

1. Verify `FIGMA_ACCESS_TOKEN` is set for Figma
2. Ensure Sketch app is running for sketch-context
3. Check Penpot MCP server is running locally

### Inconsistent Naming

**Symptoms:** Token names don't match expected format

**Solution:**

1. Check original design file naming conventions
2. Use normalization rules consistently
3. Consider mapping file to enforce naming standards

## See Also

- `design-token-json` style - W3C format output
- `design-token-swift` style - Swift code output
- `design-to-swiftui` skill - Generate SwiftUI views from tokens
- `design-system-management` skill - Manage token libraries
