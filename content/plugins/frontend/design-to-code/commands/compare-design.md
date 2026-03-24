---
name: compare-design
description: Compare design files with generated code to detect drift and inconsistencies
---

# Compare Design

Compare design tokens and components between design files and codebase to detect drift, inconsistencies, and missing implementations.

## Arguments

- `--source` - Design source: `figma:key`, `sketch:path`, `penpot:id`
- `--target` - Code directory or token file to compare against
- `--scope` - Comparison scope: `tokens`, `components`, `all`
- `--format` - Output format: `summary`, `detailed`, `json`
- `--threshold` - Drift tolerance for color values (default: 0)

## Workflow

### Step 1: Extract Design State

Connect to design source via MCP and extract current state:

**Tokens:**

```text
Extract from design:
- Colors: 48 values
- Typography: 12 styles
- Spacing: 10 values
- Shadows: 5 elevations
```

**Components:**

```text
Extract from design:
- Button: 3 variants × 3 sizes × 4 states
- Card: 3 variants
- Input: 5 types
```

### Step 2: Extract Code State

Parse target codebase for implemented values:

**Token Files:**

```text
Scan for:
- design-tokens.json (W3C format)
- Theme.swift / theme.ts / app_theme.dart
- tokens.css / tailwind.config.js
```

**Components:**

```text
Scan for:
- SwiftUI Views
- React components
- Flutter widgets
```

### Step 3: Compare States

Run comparison algorithms:

**Token Comparison:**

```text
For each token:
1. Check existence in both sources
2. Compare values (with threshold for colors)
3. Check naming conventions match
4. Verify hierarchical structure
```

**Component Comparison:**

```text
For each component:
1. Check implementation exists
2. Compare variant coverage
3. Verify token usage
4. Check prop/parameter mapping
```

### Step 4: Generate Drift Report

**Summary Format:**

```text
## Design-Code Comparison

**Source**: figma:abc123
**Target**: ./src/theme/
**Compared**: 2026-02-22 10:30:00

### Summary

| Category | Design | Code | Match | Drift |
|----------|--------|------|-------|-------|
| Colors | 48 | 45 | 44 | 4 |
| Typography | 12 | 12 | 12 | 0 |
| Spacing | 10 | 10 | 10 | 0 |
| Components | 15 | 12 | 10 | 5 |

### Status: ⚠️ Drift Detected

- 3 colors missing in code
- 1 color value mismatch
- 3 components not implemented
- 2 components missing variants
```

**Detailed Format:**

```text
## Token Drift

### Missing in Code (3)

| Token | Design Value | Category |
|-------|--------------|----------|
| color.semantic.info | #3B82F6 | Colors |
| color.semantic.warning | #F59E0B | Colors |
| shadow.2xl | 0 25px 50px... | Shadows |

### Value Mismatch (1)

| Token | Design | Code | Delta |
|-------|--------|------|-------|
| color.primary.500 | #2196F3 | #1E88E5 | ΔE: 2.3 |

### Added in Code (2)

| Token | Code Value | Category |
|-------|------------|----------|
| color.legacy.blue | #0066CC | Colors |
| spacing.3xl | 64px | Spacing |

## Component Drift

### Not Implemented (3)

| Component | Design Variants | Status |
|-----------|-----------------|--------|
| Badge | 4 variants | Not in codebase |
| Tooltip | 2 variants | Not in codebase |
| Skeleton | 3 variants | Not in codebase |

### Missing Variants (2)

| Component | Missing | Implemented |
|-----------|---------|-------------|
| Button | destructive | primary, secondary, ghost |
| Card | elevated | flat, outlined |

### Token Usage Issues (4)

| Component | Issue | Expected | Actual |
|-----------|-------|----------|--------|
| Button | Wrong color | --color-primary | #2196F3 |
| Card | Hardcoded shadow | --shadow-md | 0 4px 6px... |
```

**JSON Format:**

```json
{
  "source": "figma:abc123",
  "target": "./src/theme/",
  "timestamp": "2026-02-22T10:30:00Z",
  "summary": {
    "tokens": { "design": 70, "code": 67, "match": 66, "drift": 4 },
    "components": { "design": 15, "code": 12, "match": 10, "drift": 5 }
  },
  "drift": {
    "tokens": {
      "missing": [
        { "name": "color.semantic.info", "value": "#3B82F6" }
      ],
      "mismatch": [
        { "name": "color.primary.500", "design": "#2196F3", "code": "#1E88E5" }
      ],
      "added": [
        { "name": "color.legacy.blue", "value": "#0066CC" }
      ]
    },
    "components": {
      "missing": ["Badge", "Tooltip", "Skeleton"],
      "incomplete": {
        "Button": { "missing": ["destructive"] },
        "Card": { "missing": ["elevated"] }
      }
    }
  }
}
```

## Examples

```bash
# Compare tokens only
/compare-design --source figma:abc123 --target ./design-tokens.json --scope tokens

# Full comparison with detailed output
/compare-design --source figma:abc123 --target ./src/ --scope all --format detailed

# JSON output for CI integration
/compare-design --source figma:abc123 --target ./theme/ --format json > drift-report.json

# Allow small color differences
/compare-design --source sketch:./app.sketch --target ./Theme.swift --threshold 2
```

## Color Comparison

### Delta E (Color Difference)

When `--threshold` is set, colors are compared using Delta E:

| Delta E | Perception |
|---------|------------|
| 0-1 | Imperceptible |
| 1-2 | Perceptible through close observation |
| 2-10 | Perceptible at a glance |
| 10+ | Colors are different |

### Comparison Algorithm

```javascript
function compareColors(design, code, threshold) {
  const deltaE = calculateDeltaE(design, code);
  return {
    match: deltaE <= threshold,
    delta: deltaE,
    design,
    code
  };
}
```

## CI Integration

### GitHub Actions

```yaml
- name: Check Design Drift
  run: |
    /compare-design --source figma:${{ secrets.FIGMA_KEY }} \
      --target ./src/theme/ \
      --format json > drift.json

    DRIFT=$(jq '.summary.tokens.drift + .summary.components.drift' drift.json)
    if [ "$DRIFT" -gt 0 ]; then
      echo "::warning::Design drift detected: $DRIFT issues"
    fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

DRIFT=$(/compare-design --source ./design-tokens.json --target ./src/theme/ --format json | jq '.summary.tokens.drift')

if [ "$DRIFT" -gt 0 ]; then
  echo "Error: $DRIFT token(s) out of sync with design"
  exit 1
fi
```

## Remediation

After detecting drift, use related commands:

```bash
# Sync tokens from design
/sync-design-system --source figma:abc123 --target ./tokens/

# Generate missing components
/generate-component Badge --source figma:abc123

# Extract updated tokens
/extract-tokens --source figma:abc123 --output ./design-tokens.json
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Design file not accessible | Verify MCP connection and credentials |
| Target not found | Check path exists and is readable |
| Invalid token format | Validate JSON/Swift/CSS syntax |
| Component not parseable | Check framework detection |

## Related Commands

- `/sync-design-system` - Synchronize after drift detected
- `/extract-tokens` - Re-extract design tokens
- `/generate-component` - Generate missing components
