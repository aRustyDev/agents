# Plugin Marketplace Registration

When creating a new plugin, always register it in `.claude-plugin/marketplace.json`.

## When This Applies

- After scaffolding a new plugin with `/create-plugin` or `/scaffold-plugin`
- When manually creating a plugin in `context/plugins/<name>/`
- When restoring or migrating plugins from another source

## Registration Steps

1. Read the plugin's manifest: `context/plugins/<name>/.claude-plugin/plugin.json`
2. Read the existing marketplace: `.claude-plugin/marketplace.json`
3. Add a new entry to the `plugins` array with these fields:

| Field | Source | Required |
|-------|--------|----------|
| `name` | `plugin.json` → `name` | Yes |
| `source` | `./context/plugins/<name>` | Yes |
| `description` | `plugin.json` → `description` | Yes |
| `version` | `plugin.json` → `version` | Yes |
| `author` | `plugin.json` → `author` | Yes |
| `keywords` | `plugin.json` → `keywords` | Yes |
| `license` | `plugin.json` → `license` or `"MIT"` | Yes |
| `homepage` | `plugin.json` → `homepage` | Yes |
| `repository` | `plugin.json` → `repository` | Yes |

4. Write the updated marketplace.json

## Example Entry

```json
{
  "name": "terraform-dev",
  "source": "./context/plugins/terraform-dev",
  "description": "Terraform development toolkit...",
  "version": "0.1.0",
  "author": {
    "name": "Adam Smith",
    "email": "developer@gh.arusty.dev"
  },
  "keywords": ["terraform", "infrastructure", "iac"],
  "license": "MIT",
  "homepage": "https://docs.arusty.dev/ai/plugins/terraform-dev",
  "repository": "https://github.com/aRustyDev/ai.git"
}
```

## Validation

After registration, verify:
- The entry is valid JSON (no trailing commas, proper quoting)
- The `source` path exists and contains a valid plugin
- The `name` matches the directory name
- No duplicate entries exist for the same plugin name

## Related Files

- `.claude-plugin/marketplace.json` - Plugin registry
- `context/plugins/<name>/.claude-plugin/plugin.json` - Individual plugin manifests
- `.claude/rules/plugin-version-sync.md` - Version update rules (for existing plugins)
