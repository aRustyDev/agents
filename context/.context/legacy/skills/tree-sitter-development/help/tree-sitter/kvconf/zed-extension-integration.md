# Zed Extension Integration Guide

This guide documents the critical steps for keeping the Zed extension synchronized with tree-sitter-dotenv parser changes.

## Overview

The Zed extension depends on:
1. The WASM build of the parser
2. The highlights.scm file matching the parser's node types
3. The extension.toml pointing to the correct commit

## Common Issues and Solutions

### Issue: "Invalid node type" Errors
**Symptom**: Zed logs show errors like:
```
ERROR [language::language_registry] failed to load language env:
Error loading highlights query
Caused by:
    Query error at 2:2. Invalid node type raw_value
```

**Causes**:
1. highlights.scm references node types that don't exist in the parser
2. Node types exist in grammar.js but aren't used in actual parsing
3. WASM file is out of sync with the grammar

**Solution**:
1. Only reference node types that are actually produced by the parser
2. Test what nodes are produced: `echo "test=value" | npx tree-sitter parse -`
3. Keep highlights.scm minimal

### Issue: Extension Directory Pollution
**Symptom**: The grammars directory contains subdirectories instead of just the WASM file

**Solution**:
```bash
cd zed-env/grammars
rm -rf env/  # Remove any subdirectories
ls -la       # Should only show env.wasm
```

## Step-by-Step Integration Process

### 1. After Grammar Changes

```bash
# In tree-sitter-dotenv directory
npx tree-sitter generate
npx tree-sitter build --wasm

# Test the parser
echo "key=value" | npx tree-sitter parse -
```

### 2. Identify Node Types

Check what node types are produced:
```bash
# Look at the parse tree output
echo "key=true" | npx tree-sitter parse -
# If it shows (bool), then bool is a valid node type
# If it shows (raw_value), then bool is NOT produced
```

### 3. Update highlights.scm

Only include node types that are actually produced:
```scheme
; ✅ GOOD - only real node types
(comment) @comment
(raw_value) @constant
(identifier) @variable

; ❌ BAD - references non-existent types
(bool) @boolean        ; Only if parser produces bool nodes
(integer) @number      ; Only if parser produces integer nodes
```

### 4. Sync Extension

```bash
# Get the commit hash
cd tree-sitter-dotenv
git add -A && git commit -m "feat: your changes"
COMMIT=$(git rev-parse HEAD)

# Update extension
cd ../zed-env
# Edit extension.toml and update commit = "..."
cp ../tree-sitter-dotenv/tree-sitter-env.wasm grammars/env.wasm
```

### 5. Test in Zed

1. Open a test .env file
2. Check Zed logs for errors: `tail -f ~/Library/Logs/Zed/Zed.log`
3. Verify syntax highlighting works

## Node Type Alignment Strategy

### Phase-by-Phase Node Types

#### Phase 1 (Current)
- `comment` - # comments
- `identifier` - variable names
- `raw_value` - all values (via alias)

#### Phase 2 (Strings)
Will add:
- `string_double` - "double quoted"
- `string_single` - 'single quoted'
- `interpolation` - ${VAR}
- `escape_sequence` - \n, \t, etc.

#### Phase 3 (Primitives)
Will add:
- `bool` - true/false
- `integer` - numeric values

#### Phase 4 (Complex)
Will add:
- `url` - URLs with schemes
- Error node types

### Testing Node Production

Create a test script to verify node types:
```javascript
// test-nodes.js
const Parser = require('tree-sitter');
const Env = require('./');
const parser = new Parser();
parser.setLanguage(Env);

const tests = [
  'key=value',
  'key="string"',
  'key=true',
  'key=123',
  'key=https://example.com'
];

tests.forEach(test => {
  const tree = parser.parse(test);
  console.log(`${test} =>`, tree.rootNode.toString());
});
```

## Troubleshooting Checklist

- [ ] Grammar generates without errors: `npx tree-sitter generate`
- [ ] WASM builds successfully: `npx tree-sitter build --wasm`
- [ ] Parse tree shows expected nodes: `echo "test" | npx tree-sitter parse -`
- [ ] highlights.scm only references real nodes
- [ ] grammars/ directory is clean (only env.wasm)
- [ ] extension.toml has correct commit hash
- [ ] No errors in Zed logs
- [ ] Syntax highlighting appears

## Quick Commands Reference

```bash
# Full sync process
cd tree-sitter-dotenv
npx tree-sitter generate && npx tree-sitter build --wasm
git add -A && git commit -m "update"
cp tree-sitter-env.wasm ../zed-env/grammars/env.wasm
cd ../zed-env
# Update extension.toml commit manually
zed test.env
```