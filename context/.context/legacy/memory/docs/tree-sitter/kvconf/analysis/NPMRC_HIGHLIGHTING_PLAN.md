# Plan: Fix .npmrc Syntax Highlighting - Contributing to Both Repos

## Problem Summary
The zed-env extension uses tree-sitter-dotenv grammar which has a restrictive identifier pattern that doesn't support hyphenated keys commonly used in .npmrc files.

### Current Grammar Issue
- **Location**: `grammar.js` in tree-sitter-dotenv
- **Problem**: `identifier: ($) => /[A-Z_][0-9a-zA-Z_]*/`
  - Only allows uppercase start or underscore
  - No hyphens allowed
  - This breaks common npmrc keys like `auto-install-peers`, `strict-peer-dependencies`, etc.

### What Works vs What Doesn't
**Works:**
- `registry=https://registry.npmjs.org` (URL highlights)
- Simple keys without hyphens in test files
- `=` operator highlighting

**Doesn't Work:**
- Any key with hyphens (parsed as ERROR tokens)
- Type-specific value highlighting for hyphenated keys

## Contribution Plan

### Part 1: Fix tree-sitter-dotenv Repository

#### 1.1 Update Grammar
In `grammar.js`, change the identifier pattern:
```javascript
// Current (broken)
identifier: ($) => /[A-Z_][0-9a-zA-Z_]*/,

// Proposed fix
identifier: ($) => /[a-zA-Z_][0-9a-zA-Z_-]*/,
```

This allows:
- Start with any letter (upper/lowercase) or underscore
- Contains letters, numbers, underscores, AND hyphens

#### 1.2 Update Tests
Add test cases for hyphenated keys in test corpus:
```
auto-install-peers=true
strict-peer-dependencies=false
package-import-method=clone-or-copy
MY_TRADITIONAL_VAR=value
_underscore_var=test
```

#### 1.3 Build and Test
```bash
cd tree-sitter-dotenv
npm install
npm run generate
npm test
```

#### 1.4 Submit PR to tree-sitter-dotenv
- Title: "Add support for hyphenated identifiers (common in .npmrc files)"
- Explain the use case for .npmrc files
- Show before/after parsing examples

### Part 2: Enhance zed-env Repository

#### 2.1 Add npmrc Support to env Language
Update `languages/env/config.toml`:
```toml
name = "env"
grammar = "env"
path_suffixes = ["conf", "env", "envrc", "example", "local", "test", "npmrc"]  # Add npmrc
```

#### 2.2 Enhance Syntax Highlighting
Update `languages/env/highlights.scm` to add npmrc-specific patterns while keeping base env support:
```scheme
; Base env highlighting (keep existing)
(comment) @comment
(variable (identifier) @variable)
(bool) @constant.builtin.boolean
(integer) @constant.numeric
(url) @string.special.url
(string_interpolated) @string
(string_literal) @string
(interpolated_variable) @variable
(raw_value) @constant
"=" @operator

; Enhanced patterns for npmrc values (add these)
; Boolean values in raw_value
((raw_value) @constant.builtin.boolean
  (#match? @constant.builtin.boolean "^(true|false)$"))

; NPM-specific configuration values
((raw_value) @constant.builtin
  (#match? @constant.builtin "^(auto|always|never|warn-only|clone|clone-or-copy|hardlink|copy)$"))

; Registry URLs (override raw_value for URLs)
((raw_value) @string.special.url
  (#match? @string.special.url "^https?://"))

; Package scopes
((raw_value) @namespace
  (#match? @namespace "^@[a-zA-Z0-9-]+/"))

; File paths
((raw_value) @string.special.path
  (#match? @string.special.path "^(/|\\./|\\.\\./|~/)"))
```

#### 2.3 Update README
Add documentation about npmrc support:
- Mention that .npmrc files are now supported
- List the enhanced highlighting features for npmrc files
- Note the dependency on tree-sitter-dotenv version that supports hyphens

#### 2.4 Submit PR to zed-env
- Title: "Add .npmrc file support with enhanced syntax highlighting"
- Reference the tree-sitter-dotenv PR if not yet merged
- Show examples of the enhanced highlighting

## Testing Both Changes Together
1. Use your forked tree-sitter-dotenv in zed-env for testing:
   ```toml
   [grammars.env]
   repository = "https://github.com/YOUR_USERNAME/tree-sitter-dotenv"
   commit = "YOUR_COMMIT_HASH"
   ```

2. Test with `/Users/asmith/code/public/mermaid/.npmrc`:
   ```
   registry=https://registry.npmjs.org
   auto-install-peers=true
   strict-peer-dependencies=false
   package-import-method=clone-or-copy
   ```

Expected highlighting:
- All keys (including hyphenated) in variable color
- `true`/`false` in boolean color  
- URLs in special URL color
- `clone-or-copy` in constant color
- `=` in operator color

## PR Strategy
1. Submit tree-sitter-dotenv PR first
2. Submit zed-env PR referencing the grammar fix
3. zed-env can temporarily use your fork until tree-sitter-dotenv merges
4. Update zed-env to official tree-sitter-dotenv once merged

This approach benefits all .env file users while adding specific enhancements for .npmrc files.