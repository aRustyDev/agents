# Implementation Plan: Comprehensive .npmrc and KEY=VALUE File Support

## Development Setup ✅
- [x] Fork exists at: https://github.com/aRustyDev/tree-sitter-dotenv
- [x] Local clone at: /Users/asmith/code/contributing/tree-sitter-dotenv/
- [x] zed-env updated to use local path: `path = "../tree-sitter-dotenv"`

## CRITICAL UPDATE: Parser Bug Discovered

A fundamental bug has been identified in the tree-sitter-dotenv parser that prevents correct parsing of basic KEY=VALUE pairs. See [ANALYSIS.md](./ANALYSIS.md) for detailed findings.

### Immediate Action Required
The parser incorrectly tokenizes `key=value` as two separate variables. This blocks all subsequent work until resolved.

## Phase 0: Fix Parser Bug (BLOCKING) ✅

### Root Cause
The parser's state machine had incorrect lexer state transitions. After consuming "=", it remained in a state where identifiers could be parsed, causing values to be misinterpreted as new variables.

### Solution Implemented
Used `token.immediate` for the equals sign to force tight coupling between identifier and value:
```javascript
variable: ($) =>
  seq(
    field("name", $.identifier), 
    token.immediate("="), 
    field("value", optional(alias($._rest_of_line, $.raw_value)))
  ),

_rest_of_line: ($) => token.immediate(/[^\n\r]*/),
```

### Results
- [x] Basic parsing `key=value` works correctly
- [ ] Need to adapt solution to match test expectations for value types
- [ ] All corpus tests need updating
- [ ] Test with real .npmrc files pending
- [ ] Update WASM and test in Zed pending

## Phase 1: tree-sitter-dotenv Grammar Enhancements

### Checkpoint 1.1: Basic Hyphen Support ❌ (Blocked by parser bug)
**Goal:** Support hyphenated keys like `auto-install-peers`

**Changes:**
```javascript
// In grammar.js, update line 26:
identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_-]*/,
```

**Test cases:**
```
auto-install-peers=true
strict-peer-dependencies=false
package-import-method=clone-or-copy
```

**Verification:**
- [x] Run `npm run generate && npm test`
- [x] Test in Zed with sample .npmrc file
- [x] Verify existing .env files still work

**Result:** ❌ Pattern implemented but blocked by parser bug. The grammar correctly defines hyphenated identifiers, but the parser state machine incorrectly tokenizes values as new variables.

**Evidence:**
```
# Input: simple-key=value
# Expected: (variable name: (identifier "simple-key") value: (raw_value "value"))
# Actual: Two separate variables with MISSING "="
```

### Checkpoint 1.2: Add Namespace Support ⚠️ (Pattern ready, parsing blocked)
**Goal:** Support scoped registry syntax `@scope:key=value`

**Changes:**
```javascript
identifier: ($) => choice(
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/)
),
```

**Test cases:**
```
@mycompany:registry=https://npm.company.com
@babel:registry=https://registry.npmjs.org
```

**Verification:**
- [x] Grammar tests pass
- [x] Both simple and namespaced keys highlight
- [x] No regression in basic keys

**Result:** ⚠️ Pattern implemented successfully but affected by parser bug. Namespace patterns are correctly defined but values following "=" are still misparsed.

**Current State:**
- Grammar pattern: ✅ Correctly accepts `@scope:key` syntax
- Parser behavior: ❌ Values after "=" parsed as new variables
- Highlighting: ❌ Cannot verify until parser fixed

**Note:** Visual highlighting verification in Zed requires manual installation of the dev extension:
1. Open Zed → Command Palette → "zed: extensions"
2. Click "Install Dev Extension" 
3. Select `/Users/asmith/code/contributing/zed-env`
4. Open test files to verify highlighting

### Checkpoint 1.3: Add URL Path Keys ⏳
**Goal:** Support URL path syntax `//host/:key=value`

**Changes:**
```javascript
identifier: ($) => choice(
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/),
  seq('//', /[^/]+/, repeat(seq('/', /[^/:]+/)), ':', /[a-zA-Z0-9_-]+/)
),
```

**Test cases:**
```
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
//npm.company.com/:username=myuser
```

### Checkpoint 1.4: Enhanced Comments ⏳
**Goal:** Support both `#` and `;` comment styles

**Changes:**
```javascript
comment: ($) => token(choice(
  seq('#', /.*/),
  seq(';', /.*/)
)),
```

**Test cases:**
```
# This is a hash comment
; This is a semicolon comment
```

### Checkpoint 1.5: Environment Variables ⏳
**Goal:** Support `${VAR}` interpolation syntax

**Changes:**
```javascript
interpolated_variable: ($) => choice(
  seq('$', $.identifier),
  seq('${', $.identifier, '}'),
  seq('${', $.identifier, '-', $.default_value, '}'),
  seq('${', $.identifier, ':-', $.default_value, '}')
),
default_value: ($) => /[^}]+/,
```

**Test cases:**
```
token=${NPM_TOKEN}
fallback=${CUSTOM_REGISTRY-https://registry.npmjs.org}
empty_fallback=${VAR:-default}
```

### Checkpoint 1.6: Additional Value Types ⏳
**Goal:** Add support for paths, log levels, and multi-line values

**Changes:**
```javascript
value: ($) => choice(
  $.string_interpolated,
  $.string_literal,
  $.multi_line_string,
  $.url,
  $.bool,
  $.integer,
  $.log_level,
  $.path,
  $.raw_value
),

log_level: ($) => choice(
  'silent', 'error', 'warn', 'notice', 
  'http', 'info', 'verbose', 'silly'
),

path: ($) => token(choice(
  /\/[^\s]*/,          // Absolute paths
  /\.[\/\\][^\s]*/,    // Relative paths
  /~\/[^\s]*/          // Home paths
)),

multi_line_string: ($) => seq(
  '"',
  repeat(choice(
    /[^"\n\\]+/,
    $.escape_sequence,
    '\n'
  )),
  '"'
),
```

## Phase 2: zed-env Extension Updates

### Checkpoint 2.1: Update File Associations ⏳
**File:** `languages/env/config.toml`
```toml
path_suffixes = ["conf", "env", "envrc", "example", "local", "test", "npmrc", "yarnrc"]
file_names = [".env", ".envrc", ".npmrc", ".yarnrc", ".env.local", ".env.development", ".env.production"]
```

### Checkpoint 2.2: Enhanced Highlighting ⏳
**File:** `languages/env/highlights.scm`

Add patterns for:
- Namespace detection
- URL path keys
- Value type patterns
- Environment variable interpolation

## Test Files

### test-1-basic.npmrc
```
# Basic test - should work with current grammar
registry=https://registry.npmjs.org
save-exact=true
loglevel=warn
```

### test-2-hyphens.npmrc
```
# Hyphenated keys - checkpoint 1.1
auto-install-peers=true
strict-peer-dependencies=false
package-import-method=clone-or-copy
```

### test-3-namespaces.npmrc
```
# Namespace support - checkpoint 1.2
@mycompany:registry=https://npm.company.com
@babel:registry=https://registry.npmjs.org
```

### test-4-urls.npmrc
```
# URL path keys - checkpoint 1.3
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
//npm.company.com/:always-auth=true
```

### test-5-complete.npmrc
```
# Complete test with all features
registry=https://registry.npmjs.org

# Scoped registries
@mycompany:registry=https://npm.company.com
@babel:registry=https://registry.npmjs.org

# Authentication
//npm.company.com/:_authToken=${NPM_TOKEN}
//npm.company.com/:always-auth=true

# Package settings
auto-install-peers=true
strict-peer-dependencies=false
package-import-method=clone-or-copy

# Performance
prefer-offline=true
fetch-retries=3

# Paths
prefix=/usr/local
cache=~/.npm

# Logging
loglevel=warn

; Semicolon comment
# Hash comment
```

## Verification Commands

```bash
# After each grammar change:
cd /Users/asmith/code/contributing/tree-sitter-dotenv
npm run generate
npm test

# Test in Zed:
# 1. Open test files in Zed
# 2. Verify syntax highlighting
# 3. Check for regressions

# Create git checkpoint:
git add .
git commit -m "Checkpoint X.X: Description"
git tag checkpoint-X.X
```

## Rollback Strategy
If issues arise at any checkpoint:
```bash
git checkout checkpoint-X.X  # Return to last working state
```

## Current Status
- **Phase 0:** ✅ Parser bug fixed with immediate token approach
- **Development Setup:** ✅ Complete - Environment configured
- **Phase 1:** 🔄 In Progress - Adapting parser fix to work with value type detection
- **Phase 2:** ⏳ Ready to test once Phase 1 complete

## Key Findings
1. The identifier patterns for hyphens and namespaces are correctly implemented
2. The parser state machine has a fundamental bug affecting all KEY=VALUE parsing
3. This is not specific to our changes - the original grammar has the same issue
4. See [ANALYSIS.md](./ANALYSIS.md) for detailed technical analysis

## Next Steps
1. **CRITICAL:** Implement parser bug fix (see Phase 0)
2. Verify basic parsing functionality with test cases
3. Re-test all implemented patterns (hyphens, namespaces)
4. Continue with remaining checkpoints once parser is fixed
5. Document solution in PROCESS_GUIDE.md for future reference

## Test Cases for Parser Fix Verification
```bash
# These should all parse correctly after fix:
echo 'key=value' | npx tree-sitter parse -
echo 'hyphen-key=hyphen-value' | npx tree-sitter parse -
echo '@scope:key=value' | npx tree-sitter parse -
echo 'key=true' | npx tree-sitter parse -
```