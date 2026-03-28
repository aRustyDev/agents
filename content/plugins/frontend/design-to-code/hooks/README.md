# Design-to-Code Hooks

## validate-design-tokens

Validates design token JSON files when saved.

### Trigger

Files matching:
- `*design-tokens*.json`
- `*tokens.json`

### Validation

1. Parses JSON to verify syntax
2. Counts root-level token keys (excluding `$` prefixed metadata)
3. Reports validation status

### Example Output

```text
✓ Valid design tokens: 12 root keys
```

### Configuration

Located in `hooks/hooks.json`. The hook runs on PostToolUse for Write/Edit/MultiEdit operations.

### Disabling

To disable temporarily, rename `hooks.json` to `hooks.json.bak`.
