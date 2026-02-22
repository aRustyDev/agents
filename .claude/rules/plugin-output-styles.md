# Plugin outputStyles Format

When defining `outputStyles` in a plugin's `plugin.json`, use explicit file paths only.

## Rule

**DO NOT** use directory paths in the `outputStyles` array:

```json
// WRONG - causes validation errors
"outputStyles": [
  "./styles/",
  "../../output-styles/feedback-submission.md"
]
```

**DO** use explicit file paths:

```json
// CORRECT
"outputStyles": [
  "./styles/swift-code.md",
  "./styles/swiftui-view.md",
  "../../output-styles/feedback-submission.md"
]
```

## Why

Directory paths like `"./styles/"` cause plugin validation errors:

```text
Plugin has an invalid manifest file. Validation errors: outputStyles: Invalid input
```

The validator expects each entry to be a path to a specific `.md` file.

## When Scaffolding Plugins

1. If the plugin has custom styles in `./styles/`, list each `.md` file explicitly
2. If no custom styles exist, only include the shared feedback style:

   ```json
   "outputStyles": ["../../output-styles/feedback-submission.md"]
   ```

3. Never copy `outputStyles` from existing plugins without verifying the format

## Template Reference

The correct template format is in `context/plugins/.template/.claude-plugin/plugin.json`:

```json
"outputStyles": ["../../output-styles/feedback-submission.md"]
```
