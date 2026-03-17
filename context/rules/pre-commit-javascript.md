# JavaScript/TypeScript Linting Rules (biome)

Configuration: `.github/pre-commit/biome.json` (symlinked to `biome.json`)

## When to Modify

Modify the biome configuration when:
- Changing formatting preferences (quotes, semicolons)
- Enabling/disabling linting rules
- Adjusting complexity thresholds
- Adding file/directory exclusions

## Key Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `indentWidth` | 2 | Spaces per indent |
| `lineWidth` | 100 | Max line length |
| `quoteStyle` | single | Prefer single quotes |
| `semicolons` | asNeeded | Minimal semicolons |

## Enabled Rules

- **Recommended**: All recommended rules enabled
- **Complexity**: Cognitive complexity warnings
- **Correctness**: Unused variables/imports
- **Style**: `const` preference, no non-null assertions
- **Suspicious**: Explicit `any` warnings

## Pre-commit Hooks

- `biome-check`: Lints JS/TS files (runs on commit)
- `biome-fix`: Auto-fixes issues (manual stage)

## Running Manually

```bash
# Check files
biome check src/

# Check and fix
biome check --write src/

# Format only
biome format --write src/
```

## File Exclusions

Edit `.github/pre-commit/biome.json`:

```json
{
  "files": {
    "ignore": [
      "existing/**",
      "newpattern/**"
    ]
  }
}
```

## Disabling Rules

```json
{
  "linter": {
    "rules": {
      "suspicious": {
        "noExplicitAny": "off"
      }
    }
  }
}
```
