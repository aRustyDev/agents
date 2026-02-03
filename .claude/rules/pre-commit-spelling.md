# Spell Checking Rules (cspell)

Configuration: `.github/pre-commit/cspell.json`
Dictionaries: `.github/pre-commit/words/*.txt`
Public hook: `https://github.com/streetsidesoftware/cspell-cli` (v9.6.0)

## When to Modify

Modify cspell configuration when:
- Adding new project-specific terms
- Adding tool/library names
- Changing language settings
- Adding file type overrides

## Dictionary Structure

```
.github/pre-commit/
├── cspell.json              # Main configuration
└── words/
    ├── project.txt          # Project-specific terms (arustydev, devrag, etc.)
    └── tools.txt            # Tool/library names (isort, pylint, biomejs, etc.)
```

## Adding New Words

### To existing dictionaries

Add words to the appropriate `.txt` file (one word per line):

```bash
# Project-specific terms
echo "newterm" >> .github/pre-commit/words/project.txt

# Tool/library names
echo "newtool" >> .github/pre-commit/words/tools.txt
```

### Creating new dictionaries

1. Create a new `.txt` file in `.github/pre-commit/words/`:

```bash
echo "domain-term-1" > .github/pre-commit/words/domain.txt
echo "domain-term-2" >> .github/pre-commit/words/domain.txt
```

2. Register it in `cspell.json`:

```json
{
  "dictionaryDefinitions": [
    {
      "name": "domain-words",
      "path": ".github/pre-commit/words/domain.txt",
      "addWords": true
    }
  ],
  "dictionaries": [
    "domain-words"
  ]
}
```

## Configuration Options

### dictionaryDefinitions

Define custom dictionaries:

```json
{
  "dictionaryDefinitions": [
    {
      "name": "project-words",
      "path": ".github/pre-commit/words/project.txt",
      "addWords": true
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `name` | Dictionary identifier (used in `dictionaries` array) |
| `path` | Path to word list file (relative to config) |
| `addWords` | Allow adding words via `cspell --words` |

### Built-in Dictionaries

The config includes these built-in dictionaries:

- `typescript`, `python`, `bash`, `go`, `rust` - Language terms
- `css`, `html` - Web terms
- `npm`, `node` - Node.js ecosystem
- `softwareTerms` - General software terms
- `companies` - Company names
- `misc` - Miscellaneous terms

### Ignore Patterns

```json
{
  "ignorePaths": [
    "node_modules/**",
    ".venv/**",
    "*.lock",
    "*.sql",
    ".data/**"
  ],
  "ignoreRegExpList": [
    "```[\\s\\S]*?```",
    "`[^`]+`",
    "https?://\\S+"
  ]
}
```

### File Overrides

```json
{
  "overrides": [
    {
      "filename": "**/*.md",
      "dictionaries": ["en-gb"]
    },
    {
      "filename": "**/brewfile",
      "enabled": false
    }
  ]
}
```

## Pre-commit Hook

```yaml
- repo: https://github.com/streetsidesoftware/cspell-cli
  rev: v9.6.0
  hooks:
    - id: cspell
      args:
        - '--config=.github/pre-commit/cspell.json'
        - '--no-progress'
        - '--no-summary'
```

## Running Manually

```bash
# Check specific file
cspell --config .github/pre-commit/cspell.json path/to/file.md

# Check all files
cspell --config .github/pre-commit/cspell.json "**/*.md"

# Show suggestions for unknown words
cspell --config .github/pre-commit/cspell.json --show-suggestions file.md
```

## Troubleshooting

### Unknown word in code block

Code blocks should be ignored by default. If not, check `ignoreRegExpList` includes the code block pattern.

### False positive on technical term

Add to appropriate dictionary:
- Project names → `words/project.txt`
- Tool/library names → `words/tools.txt`
- Domain-specific → Create new dictionary

### Slow performance

Add paths to `ignorePaths` for directories that don't need spell checking.
