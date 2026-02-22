---
name: design-system-management
description: Manage design system tokens including CRUD operations, multi-format export, version tracking, and synchronization with design files
created: 2026-02-22
updated: 2026-02-22
tags: [design-system, tokens, versioning, sync, multi-format]
extends: design-theme-factory-dev
---

# Design System Management

Comprehensive design token management for maintaining consistency between design files and code.

## Overview

This skill provides tools for managing design system tokens throughout their lifecycle, from extraction to code generation, with support for versioning, conflict detection, and multi-platform export.

**This skill covers:**

- Token CRUD operations (create, read, update, delete)
- Multi-format export (JSON, Swift, CSS, Tailwind, Flutter)
- Version tracking and change history
- Design-to-code synchronization
- Conflict detection and resolution

**This skill does NOT cover:**

- Initial token extraction (see `design-tokens-extraction` skill)
- Component code generation (see `design-to-*` skills)

## Quick Reference

### Token Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| List | `/sync-design-system --list` | Show all tokens |
| Add | Token CRUD workflow | Add new token |
| Update | Token CRUD workflow | Modify token value |
| Delete | Token CRUD workflow | Remove token |
| Export | `/sync-design-system --target <path>` | Export to code |

### Export Formats

| Format | File Extension | Target |
|--------|----------------|--------|
| W3C JSON | `.tokens.json` | Platform-agnostic |
| Swift | `.swift` | iOS/macOS |
| CSS | `.css` | Web (custom properties) |
| Tailwind | `tailwind.config.js` | Tailwind CSS |
| Flutter | `.dart` | Flutter/Dart |

## Workflow: Token Management

### Step 1: Initialize Token Store

Create or locate the design tokens file:

```text
tokens/
├── design-tokens.json      # W3C format (source of truth)
├── generated/
│   ├── Theme.swift         # iOS/macOS output
│   ├── theme.css           # Web output
│   └── tailwind.config.js  # Tailwind output
└── .tokens-history/        # Version history
```

### Step 2: Token CRUD Operations

**Create Token:**

```json
{
  "operation": "create",
  "path": "color.semantic.error",
  "value": {
    "$value": "#DC2626",
    "$type": "color",
    "$description": "Error state color for destructive actions"
  }
}
```

**Read Token:**

```json
{
  "operation": "read",
  "path": "color.semantic.error"
}
// Returns full token definition with metadata
```

**Update Token:**

```json
{
  "operation": "update",
  "path": "color.semantic.error",
  "value": {
    "$value": "#EF4444"
  },
  "reason": "Improved contrast ratio"
}
```

**Delete Token:**

```json
{
  "operation": "delete",
  "path": "color.deprecated.oldRed",
  "reason": "Replaced by color.semantic.error"
}
```

### Step 3: Version Tracking

Track changes to maintain history:

```json
{
  "version": "1.2.0",
  "timestamp": "2026-02-22T10:30:00Z",
  "changes": [
    {
      "type": "update",
      "path": "color.semantic.error",
      "previous": "#DC2626",
      "current": "#EF4444",
      "reason": "Improved contrast ratio"
    }
  ],
  "author": "design-system-sync"
}
```

### Step 4: Multi-Format Export

Export tokens to target formats:

**To Swift:**

```swift
// Generated from design-tokens.json v1.2.0
extension Color {
    enum Semantic {
        static let error = Color(hex: "#EF4444")
    }
}
```

**To CSS:**

```css
/* Generated from design-tokens.json v1.2.0 */
:root {
    --color-semantic-error: #EF4444;
}
```

**To Tailwind:**

```javascript
// Generated from design-tokens.json v1.2.0
module.exports = {
    theme: {
        extend: {
            colors: {
                semantic: {
                    error: '#EF4444'
                }
            }
        }
    }
}
```

## Synchronization Workflow

### Design File to Code

1. **Extract tokens** from design file (Figma/Sketch/Penpot)
2. **Compare** with existing `design-tokens.json`
3. **Detect changes**:
   - New tokens (additions)
   - Modified values (updates)
   - Missing tokens (potential deletions)
4. **Generate diff report**
5. **Apply changes** with confirmation
6. **Export** to target formats

### Code to Design File

1. **Read** current `design-tokens.json`
2. **Compare** with design file tokens
3. **Report drift**:
   - Tokens in code but not design
   - Value mismatches
   - Naming inconsistencies
4. **Generate suggestions** for design updates

## Conflict Resolution

When conflicts are detected:

### Value Conflicts

```text
## Token Conflict: color.primary

| Source | Value |
|--------|-------|
| Design | #2196F3 |
| Code | #1E88E5 |

Resolution Options:
1. Use design value (update code)
2. Use code value (flag for design update)
3. Keep both (create variant)
4. Manual review
```

### Naming Conflicts

```text
## Naming Conflict

Design: "Primary Blue"
Code: "color.brand.primary"

Suggested mapping:
- Create alias: "Primary Blue" → "color.brand.primary"
- Or rename in design to match code convention
```

## Token Organization

### Recommended Structure

```json
{
  "color": {
    "primitive": {
      "blue": { "50": {}, "100": {}, "500": {}, "900": {} }
    },
    "semantic": {
      "background": {},
      "surface": {},
      "text": {},
      "error": {},
      "success": {}
    },
    "component": {
      "button": {
        "primary": {},
        "secondary": {}
      }
    }
  },
  "typography": {
    "fontFamily": {},
    "fontSize": {},
    "fontWeight": {},
    "lineHeight": {}
  },
  "spacing": {},
  "borderRadius": {},
  "shadow": {},
  "duration": {}
}
```

### Token Naming Convention

| Level | Pattern | Example |
|-------|---------|---------|
| Category | `<category>` | `color` |
| Subcategory | `<category>.<subcategory>` | `color.semantic` |
| Token | `<category>.<subcategory>.<name>` | `color.semantic.error` |
| Variant | `<token>.<variant>` | `color.semantic.error.light` |

## Validation Rules

Before applying changes, validate:

1. **Type Consistency:**
   - Color values are valid hex/rgb/hsl
   - Dimensions include units
   - Font weights are numeric

2. **Reference Integrity:**
   - All token references resolve
   - No circular references
   - Aliases point to existing tokens

3. **Naming Compliance:**
   - Follows established convention
   - No duplicate paths
   - Valid JSON keys

## Export Configuration

Configure per-format output:

```json
{
  "exports": {
    "swift": {
      "output": "./Sources/Theme/",
      "template": "swift-extensions",
      "colorFormat": "hex-initializer"
    },
    "css": {
      "output": "./styles/tokens.css",
      "prefix": "--design-",
      "colorFormat": "hex"
    },
    "tailwind": {
      "output": "./tailwind.config.js",
      "mode": "extend",
      "includeCategories": ["color", "spacing", "borderRadius"]
    }
  }
}
```

## Change Report

After sync, generate report:

```markdown
## Design System Sync Report

**Version**: 1.2.0 → 1.3.0
**Timestamp**: 2026-02-22T10:30:00Z

### Changes Applied

| Category | Added | Updated | Removed |
|----------|-------|---------|---------|
| Colors | 3 | 2 | 0 |
| Typography | 0 | 1 | 0 |
| Spacing | 2 | 0 | 0 |

### Details

#### Added

- `color.semantic.warning`: #F59E0B
- `color.semantic.info`: #3B82F6
- `color.semantic.neutral`: #6B7280

#### Updated

- `color.semantic.error`: #DC2626 → #EF4444 (contrast improvement)
- `typography.fontSize.xl`: 1.25rem → 1.375rem

### Files Updated

- tokens/design-tokens.json
- Sources/Theme/Colors.swift
- styles/tokens.css
```

## Troubleshooting

### Sync Fails

**Symptoms:** Export fails or produces invalid output

**Solution:**

1. Validate source tokens with JSON schema
2. Check for special characters in token names
3. Verify all references resolve

### Version Conflict

**Symptoms:** Multiple sources have different versions

**Solution:**

1. Identify authoritative source
2. Generate full diff between versions
3. Merge changes with conflict resolution
4. Increment version after merge

## See Also

- `design-tokens-extraction` skill - Initial token extraction
- `/sync-design-system` command - Sync tokens to code
- `design-token-json` style - W3C format output
- `design-token-swift` style - Swift output format
