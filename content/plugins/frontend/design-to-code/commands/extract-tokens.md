---
name: extract-tokens
description: Extract design tokens from Figma, Sketch, or Penpot design files
---

# Extract Tokens

Extract design tokens (colors, typography, spacing, shadows) from a design file and output in the requested format.

## Arguments

- `<file>` - Design file identifier:
  - Figma: File key from URL (e.g., `abc123` from `figma.com/file/abc123/...`)
  - Sketch: Path to `.sketch` file (e.g., `./design/app.sketch`)
  - Penpot: URL or `project_id/file_id`
- `--source` - Design tool source: `figma`, `sketch`, `penpot` (auto-detected from file)
- `--format` - Output format: `json` (default), `swift`, `css`, `tailwind`
- `--output` - Output file path (default: stdout)
- `--categories` - Token categories to extract: `colors`, `typography`, `spacing`, `shadows`, `all` (default)

## Workflow

### Step 1: Detect Source

If `--source` not provided:

- `.sketch` extension → Sketch
- Figma URL or key pattern → Figma
- Penpot URL pattern → Penpot

### Step 2: Connect via MCP

**Figma:**

```text
Use figma MCP server
- Requires FIGMA_ACCESS_TOKEN environment variable
- Call get_file with file_key
- Call get_styles for published styles
- Call get_local_variables for design tokens
```

**Sketch:**

```text
Use sketch-context MCP server
- Requires Sketch app installed
- Call get_document with file_path
- Call get_shared_styles for layer styles
- Call get_color_assets for swatches
```

**Penpot:**

```text
Use penpot MCP server
- Requires local server running (default port 4401)
- Call get_file with project_id, file_id
- Extract color library and typography
```

### Step 3: Extract Tokens

Use the `design-tokens-extraction` skill to:

1. Query design file for styles and variables
2. Extract colors, typography, spacing, shadows
3. Normalize to W3C Design Tokens format

### Step 4: Format Output

Apply the requested output format:

| Format | Output Style | Description |
|--------|--------------|-------------|
| `json` | `design-token-json` | W3C DTCG format |
| `swift` | `design-token-swift` | Swift Color/Font extensions |
| `css` | `design-token-css` | CSS custom properties |
| `tailwind` | `design-token-tailwind` | Tailwind theme config |

### Step 5: Write Output

If `--output` specified:

- Write to file path
- Report file written with token count

If no output path:

- Display formatted tokens
- Summarize extracted token counts

## Examples

```bash
# Extract from Figma to JSON (default)
/extract-tokens abc123def --source figma

# Extract from Sketch to Swift
/extract-tokens ./design/app.sketch --format swift --output ./Sources/Theme/Colors.swift

# Extract only colors from Figma
/extract-tokens abc123def --categories colors --format css

# Extract from Penpot to Tailwind config
/extract-tokens my-project/design-system --source penpot --format tailwind --output tailwind.config.js
```

## Output Summary

After extraction, display:

```text
## Tokens Extracted

| Category | Count |
|----------|-------|
| Colors | 24 |
| Typography | 8 |
| Spacing | 12 |
| Shadows | 4 |
| **Total** | **48** |

Output: ./tokens/design-tokens.json (W3C DTCG format)
```

## Error Handling

| Error | Resolution |
|-------|------------|
| `FIGMA_ACCESS_TOKEN not set` | Export token from Figma Settings > API |
| `Sketch app not running` | Open Sketch.app before extraction |
| `Penpot MCP not available` | Start server: `cd penpot-mcp && npm start` |
| `No styles found` | Check design file has published styles |
| `File not found` | Verify file key/path is correct |

## Related Commands

- `/generate-component` - Generate code from design components
- `/sync-design-system` - Sync tokens to codebase
- `/compare-design` - Compare implementation to design
