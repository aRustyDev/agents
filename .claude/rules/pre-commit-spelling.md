# Spell Checking Rules (cspell)

Configuration: `.github/pre-commit/cspell.json` (symlinked to `.cspell.json`)

## When to Modify

Modify the cspell configuration when:
- Adding project-specific technical terms
- Adding new file patterns to ignore
- Excluding new generated file types
- Adding domain-specific dictionaries

## Key Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `words` | Custom list | Project-specific terms |
| `ignorePaths` | Patterns | Skip generated/binary files |
| `ignoreRegExpList` | Regexes | Skip code blocks, URLs, etc. |

## Pre-commit Hook

- `cspell`: Checks spelling in text files (runs on commit)

## Running Manually

```bash
# Check all files
cspell lint "**/*"

# Check specific file
cspell lint path/to/file.md

# Add word to dictionary
# Edit .github/pre-commit/cspell.json, add to "words" array
```

## Adding Custom Words

Edit `.github/pre-commit/cspell.json`:

```json
{
  "words": [
    "existingword",
    "newword"
  ]
}
```

## Ignoring Files

Add to `ignorePaths`:

```json
{
  "ignorePaths": [
    "existing/**",
    "newpattern/**"
  ]
}
```
