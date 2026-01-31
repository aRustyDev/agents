# Tree-sitter Grammar Development Guide

This guide covers the development process for tree-sitter grammars, with examples from the tree-sitter-dotenv (kvconf) project.

## Table of Contents
1. [Understanding Grammar Limitations](#understanding-grammar-limitations)
2. [Development Environment Setup](#development-environment-setup)
3. [Grammar Development Process](#grammar-development-process)
4. [Common Grammar Patterns](#common-grammar-patterns)
5. [Testing and Validation](#testing-and-validation)
6. [Common Issues and Solutions](#common-issues-and-solutions)
7. [Best Practices](#best-practices)

## Understanding Grammar Limitations

### Initial Assessment
Before modifying a grammar, understand its current limitations:

1. **Analyze the existing grammar**: Review `grammar.js` to identify pattern restrictions
2. **Test edge cases**: Create test files with the syntax you want to support
3. **Document the gaps**: List specific patterns that fail to parse

### Example: Restrictive Identifier Pattern
```javascript
// Original pattern - only uppercase and underscores
identifier: ($) => /[A-Z_][0-9a-zA-Z_]*/

// Updated pattern - supports lowercase, hyphens, and namespaces
identifier: ($) => choice(
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/)
)
```

## Development Environment Setup

### Prerequisites
- Node.js 14+ and npm
- Tree-sitter CLI: `npm install -g tree-sitter-cli`
- C compiler (for native builds)

### Initial Setup
```bash
cd tree-sitter-dotenv
npm install
```

### Project Structure
```
tree-sitter-dotenv/
├── grammar.js          # Grammar definition
├── src/               # Generated parser code
├── test/
│   └── corpus/        # Test cases
├── package.json
└── binding.gyp        # Native build config
```

## Grammar Development Process

### Step 1: Modify Grammar
Edit `grammar.js` to add or modify rules:

```javascript
module.exports = grammar({
  name: 'env',
  
  rules: {
    source_file: ($) => repeat($.line),
    
    line: ($) => choice(
      $.comment,
      $.variable,
      $._empty
    ),
    
    variable: ($) => seq(
      field("name", $.identifier),
      "=",
      field("value", optional($.value))
    ),
    
    // Add new patterns here
  }
});
```

### Step 2: Generate Parser
```bash
npx tree-sitter generate
# or
npm run generate
```

This creates:
- `src/parser.c` - C parser implementation
- `src/grammar.json` - Grammar in JSON format
- `src/node-types.json` - AST node type definitions

### Step 3: Test Grammar
```bash
# Parse a single file
npx tree-sitter parse test.env

# Run corpus tests
npx tree-sitter test

# Test specific corpus file
npx tree-sitter test -f hyphens
```

### Step 4: Build WASM (for web/editor use)
```bash
npx tree-sitter build --wasm
# Creates tree-sitter-env.wasm
```

## Common Grammar Patterns

### Supporting Multiple Character Sets
```javascript
// Basic identifier with letters, numbers, underscores
identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_]*/

// With hyphens (place hyphen at end to avoid range issues)
identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_-]*/

// Case-insensitive pattern
identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_]*/i
```

### Namespace Support
```javascript
identifier: ($) => choice(
  // Regular identifier
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  // Namespaced identifier (@scope:key)
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/)
)
```

### URL Path Keys
```javascript
identifier: ($) => choice(
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  // URL-style keys for .npmrc
  /\/\/[a-zA-Z0-9.-]+(?::[0-9]+)?(?:\/[^\s:=]*)?\/?:[a-zA-Z0-9_-]+/
)
```

### Fixing Parser State Issues with token.immediate
```javascript
// Problem: Parser stays in identifier-accepting state after "="
variable: ($) => seq(
  field("name", $.identifier),
  "=",  // Parser can still accept identifiers here!
  field("value", optional($.value))
),

// Solution: Use token.immediate to force tight coupling
variable: ($) => seq(
  field("name", $.identifier),
  token.immediate("="),  // No whitespace/state change allowed
  field("value", optional(alias(
    token.immediate(/[^\n\r]*/), 
    $.value
  )))
),
```

## Testing and Validation

### Corpus Test Format
Create test files in `test/corpus/`:

```
==================
Test name here
==================
INPUT_TEXT_HERE
---
(expected_parse_tree
  (with proper structure))
```

Example corpus test:
```
==================
hyphenated key
==================
auto-install-peers=true
---
(source_file
  (variable
    name: (identifier)
    value: (value)))
```

### Running Tests
```bash
# Run all tests
npx tree-sitter test

# Run specific test file
npx tree-sitter test -f hyphens

# Debug mode (shows detailed output)
npx tree-sitter test --debug
```

### Manual Testing
```bash
# Interactive parse
echo "key=value" | npx tree-sitter parse -

# Parse file with debug info
npx tree-sitter parse test.env --debug
```

## Common Issues and Solutions

### Issue 1: Parser State Machine Bug
**Symptoms**: `key=value` parsed as two separate variables

**Solution**: Use `token.immediate`:
```javascript
variable: ($) => seq(
  field("name", $.identifier),
  token.immediate("="),
  field("value", optional($._value))
)
```

### Issue 2: Regex Pattern Conflicts
**Symptoms**: Parse errors or unexpected tokenization

**Solutions**:
1. Use `choice()` with specific order (most specific first)
2. Add explicit precedence:
   ```javascript
   identifier: ($) => choice(
     prec(2, /special-pattern/),
     prec(1, /general-pattern/)
   )
   ```

### Issue 3: Character Escaping in Patterns
**Problem**: Special regex characters need escaping

```javascript
// Wrong - hyphen creates range
/[a-z-A-Z]/

// Correct - hyphen at end
/[a-zA-Z-]/

// Or escaped
/[a-z\-A-Z]/
```

### Issue 4: Performance Issues
**Symptoms**: Slow parsing on large files

**Solutions**:
1. Avoid backtracking with `token()`:
   ```javascript
   value: ($) => token(/[^\n\r]*/)
   ```
2. Use `repeat1()` instead of `seq(item, repeat(item))`
3. Minimize use of `choice()` with many alternatives

## Best Practices

### 1. Grammar Organization
```javascript
module.exports = grammar({
  name: 'env',
  
  // Define precedences
  precedences: ($) => [
    ['string', 'boolean', 'number', 'raw']
  ],
  
  // Main rules
  rules: {
    // Entry point
    source_file: ($) => ...,
    
    // Major structures
    variable: ($) => ...,
    
    // Leaf nodes
    identifier: ($) => ...,
    value: ($) => ...,
    
    // Hidden rules (start with _)
    _spacing: ($) => /[ \t]*/
  }
});
```

### 2. Testing Strategy
- Write tests before implementing features
- Test edge cases explicitly
- Include error recovery tests
- Test performance with large files

### 3. Documentation
```javascript
// Document complex patterns
identifier: ($) => choice(
  // Standard identifier: letter/underscore followed by alphanumeric
  /[a-zA-Z_][a-zA-Z0-9_-]*/,
  
  // NPM scoped package: @scope:key
  seq('@', /[a-zA-Z0-9_-]+/, ':', /[a-zA-Z0-9_-]+/)
)
```

### 4. Version Control
```bash
# Commit grammar and generated files separately
git add grammar.js
git commit -m "feat: add hyphenated identifier support"

git add src/
git commit -m "chore: regenerate parser"
```

## Debugging Techniques

### 1. View Grammar JSON
```bash
cat src/grammar.json | jq '.rules.identifier'
```

### 2. Test Incremental Changes
```bash
# Create minimal test case
echo "problem-case=value" > debug.env
npx tree-sitter parse debug.env --debug
```

### 3. Use Playground
Tree-sitter playground allows interactive grammar testing:
```bash
npx tree-sitter playground
```

## Performance Optimization

### 1. Token Optimization
```javascript
// Slow - regex with backtracking
value: ($) => /[^\n\r]*/

// Fast - explicit token
value: ($) => token(/[^\n\r]*/)
```

### 2. Precedence Instead of Ordering
```javascript
// Instead of relying on choice order
value: ($) => choice(
  prec(3, $.string),
  prec(2, $.boolean),
  prec(1, $.number),
  $.raw_value
)
```

## Resources

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Grammar Development Guide](https://tree-sitter.github.io/tree-sitter/creating-parsers)
- [Parser Performance Guide](https://tree-sitter.github.io/tree-sitter/creating-parsers#performance)
- [Corpus Test Format](https://tree-sitter.github.io/tree-sitter/creating-parsers#testing)

## Troubleshooting Checklist

- [ ] Grammar has no syntax errors: `node -c grammar.js`
- [ ] Parser generates successfully: `npx tree-sitter generate`
- [ ] No shift/reduce conflicts in output
- [ ] Basic parsing works: `echo "test=123" | npx tree-sitter parse -`
- [ ] Corpus tests pass: `npx tree-sitter test`
- [ ] WASM builds: `npx tree-sitter build --wasm`
- [ ] Performance acceptable on large files
- [ ] Error recovery works for malformed input