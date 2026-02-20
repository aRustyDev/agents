# Plugin Version Sync

When editing any plugin's `plugin.json` file, you MUST keep versions synchronized.

## Rule

If you modify a `version` field in any file matching:

- `context/plugins/*/. claude-plugin/plugin.json`

You MUST also update the corresponding version in:

- `.claude-plugin/marketplace.json`

## Why

The marketplace.json file is the central registry of all plugins. Version mismatches cause:

- Installation failures
- Incorrect version reporting
- Cache invalidation issues

## How

1. After editing a plugin's version in `plugin.json`:

   ```json
   "version": "1.0.5",  // Changed from 1.0.4
   ```

2. Find the matching entry in `.claude-plugin/marketplace.json` and update:

   ```json
   {
     "name": "<plugin-name>",
     "version": "1.0.5",  // Must match plugin.json
     ...
   }
   ```

3. Commit both files together in the same commit

## Checklist

When bumping a plugin version:

- [ ] Update `context/plugins/<name>/.claude-plugin/plugin.json`
- [ ] Update `.claude-plugin/marketplace.json` (same version)
- [ ] Commit both files together
