# Phase 3: Primitive Types (Checkpoint 3.0)

## Table of Contents
- [3.1 Boolean Values](#31-boolean-values)
- [3.2 Integer Values](#32-integer-values)
- [3.3 Error Handling](#33-error-handling)

**REMINDER: Do not start Phase 3 until Checkpoint 2.0 is approved**

## MCP Tool Integration

### Use tree-sitter MCP for:
1. **Code Search & Analysis**:
   ```bash
   # Search for existing boolean/integer patterns
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="bool|integer" file_pattern="**/*.js"
   
   # Analyze grammar.js structure
   mcp__tree_sitter__get_ast project="tree-sitter-dotenv" path="grammar.js" max_depth=3
   ```

2. **Test Analysis**:
   ```bash
   # Find all test files with boolean/integer tests
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="bool|integer" file_pattern="test/corpus/*.txt"
   
   # Analyze test structure
   mcp__tree_sitter__get_symbols project="tree-sitter-dotenv" file_path="test/corpus/basic.txt"
   ```

3. **Complexity Analysis**:
   ```bash
   # Check grammar complexity before/after changes
   mcp__tree_sitter__analyze_complexity project="tree-sitter-dotenv" file_path="grammar.js"
   ```

## Critical Integration Steps (From Phase 1 & 2 Lessons)

### Extension Sync Requirements:
1. **After adding bool and integer types**:
   - Update queries/highlights.scm in parser repo to include `(bool) @boolean` and `(integer) @number`
   - Copy highlights.scm to zed-env/languages/env/highlights.scm
   - Remove any references to node types not yet implemented
   - Build WASM with `npx tree-sitter build --wasm`
   - Commit and push all changes to feature branch
   - Get full commit hash with `git log -1 --format="%H"`
   - Update zed-env/extension.toml with new commit hash
   - Reinstall extension in Zed

2. **Test node type production**:
   ```bash
   echo "ENABLED=true" | npx tree-sitter parse -
   echo "PORT=3000" | npx tree-sitter parse -
   # Verify these produce (bool) and (integer) nodes respectively
   ```

3. **Regression testing is critical**:
   - Strings must still parse correctly
   - `"true"` must parse as string_double, not bool
   - `"123"` must parse as string_double, not integer

### Zed Extension Debugging Checklist:
1. **Before Each Test**:
   - Ensure grammar changes are committed and pushed
   - Update extension.toml with full commit hash (not short hash)
   - Clear Zed caches if needed: `rm -rf ~/Library/Caches/Zed`
   - Reinstall extension

2. **Common Issues**:
   - "missing field `repository`" - Check extension.toml syntax
   - "failed to fetch revision" - Use full commit hash, ensure pushed
   - Highlighting not updating - Check both highlights.scm files match

3. **Verification Process**:
   - Create phase3-verification.env with test cases
   - Open in Zed to verify highlighting
   - Document any issues before proceeding

## 3.1 Boolean Values

### Implementation Pattern:
1. **Write strict boolean tests**
   ```
   ==================
   boolean true
   ==================
   key=true
   ---
   (source_file
     (variable
       name: (identifier)
       value: (bool)))
   ```

2. **Implement with strict matching**
   ```javascript
   bool: ($) => choice(
     'true',
     'false'
   ),
   ```

3. **Add to _value with correct precedence**
   ```javascript
   _value: ($) => choice(
     $.string_double,
     $.string_single,
     $.bool,  // Add here - before raw_value
     alias(token.immediate(/[^\n\r]*/), $.raw_value)
   ),
   ```

4. **Implement error detection**
   ```javascript
   // Detect "true false" and create error node
   // Pattern: bool followed by non-comment content
   
   // Option 1: Add to variable rule after value field
   variable: ($) =>
     seq(
       field("name", $.identifier),
       optional($._spacing),
       "=",
       optional($._spacing),
       field("value", optional($._value)),
       optional(
         choice(
           $.comment,
           $.error_multiple_values
         )
       )
     ),
   
   // Define error_multiple_values rule
   error_multiple_values: ($) => prec(-1, 
     seq(
       /\s+/,  // Required whitespace
       /[^#\n\r]+/  // Any non-comment content
     )
   ),
   
   // Option 2: Handle in _value rule with lookahead
   _value: ($) => choice(
     $.string_double,
     $.string_single,
     seq(
       $.bool,
       optional(
         choice(
           seq(/\s+/, $.comment),  // Allow space + comment
           seq(/\s*/, '\n'),       // Allow optional space + newline
           alias(seq(/\s+/, /[^#\n\r]+/), $.error_multiple_values)  // Error case
         )
       )
     ),
     // ... rest of choices
   ),
   ```

### Test Cases:
- `key=true` → bool
- `key=false` → bool
- `key=true # comment` → bool (comment ignored)
- `key=true false` → bool + error_multiple_values
- `key=truthy` → raw_value (not bool)
- `key=TRUE` → raw_value (case sensitive)

### Success Criteria:
- [ ] Exact matches only for true/false
- [ ] Case sensitive
- [ ] Errors for trailing content
- [ ] Comments allowed after bools

## 3.2 Integer Values

### Implementation Pattern:
1. **Integer rule with sign support**
   ```javascript
   integer: ($) => /[+-]?\d+/,
   ```

2. **Test edge cases**
   - `key=123` → integer
   - `key=0` → integer  
   - `key=-456` → integer
   - `key=+789` → integer
   - `key=123abc` → raw_value (not integer)
   - `key=12.34` → raw_value (not integer - no float support yet)

### Success Criteria:
- [ ] Positive/negative integers parse
- [ ] No partial matches
- [ ] Precedence correct

### Float Support (Deferred to Phase 6)
**Decision**: Float support will be added in Phase 6 (Future Enhancements) because:
1. Most configuration files use integers for numeric values
2. Floats can be represented as strings when needed
3. Adding floats increases grammar complexity
4. Need to handle scientific notation (1.23e-4) properly

**Future float implementation pattern**:
```javascript
// Phase 6 implementation
float: ($) => choice(
  // Standard decimal notation
  /[+-]?\d+\.\d+/,
  // Scientific notation
  /[+-]?\d+(\.\d+)?[eE][+-]?\d+/
),

// Update _value precedence
_value: ($) => choice(
  $.string_double,
  $.string_single,
  $.bool,
  $.float,     // Higher precedence than integer
  $.integer,
  $.uri,
  $.url,
  alias(token.immediate(/[^\n\r]*/), $.raw_value)
),
```

**Test cases for future implementation**:
- `key=3.14` → float
- `key=0.5` → float
- `key=-2.718` → float
- `key=1.23e-4` → float
- `key=6.022E23` → float
- `key=123.` → raw_value (incomplete float)
- `key=.456` → raw_value (no leading digit)

## 3.3 Error Handling

### Error Detection Patterns:
1. **Multiple values error**
   ```javascript
   // After bool/integer, check for non-comment content
   // If found, create error_multiple_values node
   ```

2. **Trailing comma error**
   ```javascript
   // If value ends with comma, create error_trailing_comma
   ```

3. **Error node highlighting**
   ```scheme
   (error_multiple_values) @error
   (error_trailing_comma) @error
   (error) @error
   ```

### Success Criteria:
- [ ] Errors detected correctly
- [ ] Parsing continues after errors
- [ ] Errors scoped narrowly
- [ ] Error highlighting works

**Checkpoint 3.0 Review Requirements**:
- Primitives parse correctly: bool/integer tests pass
- Precedence order maintained: strings > bool > integer > raw
- Errors highlighted appropriately: visual confirmation
- No feature regressions: all tests pass

**MANDATORY EXTERNAL REVIEW BEFORE PROCEEDING**