---
name: sync-design-system
description: Synchronize design tokens between design files and codebase, detecting drift and applying updates
---

# Sync Design System

Synchronize design tokens from a design file to your codebase, or detect drift between design and code.

## Arguments

- `--source` - Design source: `figma`, `sketch`, `penpot`, or path to tokens JSON
- `--target` - Target directory or file for generated tokens
- `--format` - Output format: `json`, `swift`, `css`, `tailwind`, `flutter`
- `--diff` - Show changes without applying (dry run)
- `--force` - Apply changes without confirmation
- `--watch` - Watch for design file changes and auto-sync

## Workflow

### Step 1: Load Current Tokens

If target exists:

1. Read existing token file from `--target`
2. Parse and normalize to internal format
3. Track version and last sync timestamp

If no target:

1. Create new token file at `--target`
2. Initialize with empty token set

### Step 2: Extract Design Tokens

Connect to design source and extract current tokens:

**From Figma/Sketch/Penpot:**

- Use MCP server to read design file
- Extract colors, typography, spacing, shadows
- Normalize to W3C format

**From JSON file:**

- Read and validate W3C token format
- Use as source of truth

### Step 3: Compute Diff

Compare source tokens with target tokens:

```text
## Token Diff

### Added (5 tokens)
+ color.semantic.info: #3B82F6
+ color.semantic.warning: #F59E0B
+ spacing.2xl: 48px
+ typography.display: {...}
+ shadow.xl: {...}

### Modified (2 tokens)
~ color.primary.500: #1E88E5 → #2196F3
~ spacing.lg: 20px → 24px

### Removed (1 token)
- color.deprecated.oldBlue: #0066CC

### Unchanged: 47 tokens
```

### Step 4: Apply Changes

If `--diff` (dry run):

- Display diff report
- Exit without changes

If changes detected:

1. Prompt for confirmation (unless `--force`)
2. Update target token file
3. Regenerate format-specific output
4. Update version and timestamp
5. Report applied changes

### Step 5: Generate Output

Export to requested format(s):

| Format | Output |
|--------|--------|
| `json` | W3C Design Tokens JSON |
| `swift` | Swift Color/Font extensions |
| `css` | CSS custom properties |
| `tailwind` | tailwind.config.js theme |
| `flutter` | Dart theme file |

## Examples

```bash
# Sync from Figma to Swift theme
/sync-design-system --source figma:abc123 --target ./Sources/Theme/ --format swift

# Preview changes without applying
/sync-design-system --source figma:abc123 --target ./tokens/ --diff

# Sync from local JSON to multiple formats
/sync-design-system --source ./design-tokens.json --target ./theme/ --format css,tailwind

# Watch mode for continuous sync
/sync-design-system --source figma:abc123 --target ./tokens/ --watch

# Force sync without confirmation
/sync-design-system --source sketch:./design.sketch --target ./theme/ --force
```

## Output Summary

```text
## Sync Complete

| Action | Count |
|--------|-------|
| Added | 5 |
| Modified | 2 |
| Removed | 1 |
| Unchanged | 47 |

### Files Updated
- tokens/design-tokens.json (source)
- Sources/Theme/Colors.swift
- Sources/Theme/Typography.swift
- Sources/Theme/Spacing.swift

### Version
- Previous: 1.2.0
- Current: 1.3.0
- Synced at: 2026-02-22T10:30:00Z
```

## Conflict Resolution

When tokens conflict:

```text
## Conflict: color.primary.500

Design value: #2196F3
Code value: #1E88E5
Last synced: 2026-02-20T15:00:00Z

Options:
1. Use design value (recommended)
2. Keep code value
3. Skip this token
4. Abort sync

Choice [1]:
```

## Watch Mode

In watch mode (`--watch`):

1. Monitor design file for changes (via MCP webhook or polling)
2. On change detected:
   - Extract updated tokens
   - Compute diff
   - If `--force`: auto-apply changes
   - Otherwise: notify and prompt

```text
[10:30:15] Watching figma:abc123 for changes...
[10:32:45] Change detected: 3 tokens modified
[10:32:45] Run /sync-design-system --diff to preview
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Design file not found | Verify source path/ID |
| Target not writable | Check file permissions |
| Invalid token format | Validate JSON against schema |
| Network timeout | Retry or check MCP connection |
| Version conflict | Resolve manually or use --force |

## Related Commands

- `/extract-tokens` - Initial token extraction
- `/generate-component` - Generate components using tokens
- `/compare-design` - Visual diff between design and code
