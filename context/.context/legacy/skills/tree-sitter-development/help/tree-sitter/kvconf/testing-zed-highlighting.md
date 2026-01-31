# Testing Zed Extension Highlighting

## Setup Instructions

1. Open Zed
2. Open the command palette (Cmd+Shift+P)
3. Type "zed: extensions" and press Enter
4. Click "Install Dev Extension"
5. Navigate to and select: `/Users/asmith/code/contributing/zed-env`
6. The extension should build and install

## Verification Steps

After installation:
1. Open test files in Zed to verify highlighting:
   - `/Users/asmith/code/contributing/.claude/tests/tree-sitter/kvconf/fixtures/test-1-basic.npmrc`
   - `/Users/asmith/code/contributing/.claude/tests/tree-sitter/kvconf/fixtures/test-2-hyphens.npmrc`
   - `/Users/asmith/code/contributing/.claude/tests/tree-sitter/kvconf/fixtures/test-3-namespaces.npmrc`

## Expected Results

### test-1-basic.npmrc
- Comments starting with `#` should be highlighted as comments
- Keys like `registry`, `save-exact`, `loglevel` should be highlighted
- URLs should be highlighted as links
- Boolean values `true`/`false` should be highlighted

### test-2-hyphens.npmrc  
- Hyphenated keys like `auto-install-peers` should be highlighted correctly
- Values `true`, `false`, `clone-or-copy` should have appropriate highlighting

### test-3-namespaces.npmrc
- Namespace keys like `@mycompany:registry` should be highlighted
- The `@` prefix and `:` should be part of the key highlighting

## Current Status

- ✅ Grammar updated to support hyphens (checkpoint 1.1)
- ✅ Grammar updated to support namespaces (checkpoint 1.2)
- ⏳ Extension needs to be installed in Zed for visual verification