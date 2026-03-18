---
paths:
  - "context/plugins/**/.claude-plugin/plugin.sources.json"
---

# Plugin Sources Format

Plugin sources files MUST use the extended format with content-addressed hashing.

## Required Format

```json
{
  "$schema": "./plugin.sources.schema.json",
  "sources": {
    "<local-path>": {
      "source": "<central-source-path>",
      "hash": "sha256:<64-hex-chars>"
    }
  }
}
```

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `source` | Yes | Path to source component in central context directory |
| `hash` | Yes | SHA256 content hash in format `sha256:<hex>` |
| `forked` | No | Set `true` if component was customized locally |
| `forked_at` | No | ISO 8601 timestamp when forked |

## Computing Hashes

```bash
just plugin-hash <path>
# or
uv run python .scripts/build-plugin.py hash <path>
```

## Validation

```bash
just plugin-check <plugin-name>
```

## Legacy Format (Deprecated)

Do NOT use string values:

```json
{
  "sources": {
    "commands/foo.md": "context/commands/foo.md"
  }
}
```

Convert to extended format with `just migrate-plugin <name>`.

## Planning Format

For components from external sources (not yet implemented), use:

```json
{
  "sources": {
    "skills/feature": {
      "type": "extend",
      "base": "https://github.com/example/repo",
      "notes": "Adapt for specific use case"
    }
  }
}
```

Planning entries are treated as forked (hash not verified).
