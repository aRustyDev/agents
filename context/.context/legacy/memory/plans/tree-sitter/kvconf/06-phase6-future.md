# Phase 6: Future Enhancements (Optional)

## User's Zed Theme Color Map
- **Orange**: booleans, integers
- **Green**: strings
- **White**: raw_values
- **Grey**: comments
- **Cyan**: operators
- **Red**: errors/keys (variable names)

## Table of Contents
- [6.1 Float/Decimal Support (Deferred from Phase 3)](#61-floatdecimal-support-deferred-from-phase-3)
- [6.2 Array Support (Deferred)](#62-array-support-deferred)

## Critical Zed Integration Steps

### Phase 6 Considerations:
1. **Feature Flag Approach**:
   - Consider feature flags for experimental features
   - Test in Zed with different configurations
   - Gather user feedback before finalizing

2. **Backward Compatibility**:
   - Ensure new features don't break existing highlighting
   - Test with older .env files
   - Maintain separate test suites

3. **Extension Publication**:
   ```bash
   # If contributing back to Zed
   # 1. Fork official zed-env extension
   # 2. Update with improved parser
   # 3. Submit PR with:
   #    - Updated grammar reference
   #    - Comprehensive test coverage
   #    - Performance benchmarks
   #    - Migration guide
   ```

4. **Documentation**:
   - Update README with all supported features
   - Create migration guide from old parser
   - Document known limitations
   - Add examples for each feature

## MCP Tool Integration

### MANDATORY: Use tree-sitter MCP tools as PRIMARY development method

**CRITICAL REQUIREMENT**: MCP tools are NOT optional. They are the PRIMARY method for all development tasks. CLI tools should only be used for final verification.

### Required MCP Tool Usage:
1. **Usage Pattern Research**:
   ```bash
   # Search for array-like patterns in real configs
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="\\[.*\\]|=.*,.*," file_pattern="test/real-world-configs/*"
   
   # Find comma-separated value patterns
   mcp__tree_sitter__find_text project="tree-sitter-dotenv" pattern="=[^,]+,[^,]+" file_pattern="**/*.{env,properties}"
   ```

2. **Grammar Complexity Analysis**:
   ```bash
   # Compare grammar complexity before/after array support
   mcp__tree_sitter__analyze_complexity project="tree-sitter-dotenv" file_path="grammar.js"
   
   # Find similar array implementations in other parsers
   mcp__tree_sitter__find_similar_code project="tree-sitter-dotenv" snippet="seq('[', repeat(" language="javascript"
   ```

3. **Performance Impact Assessment**:
   ```bash
   # Profile array parsing performance
   echo "ARRAY=[1,2,3,4,5]" > test-array.env
   mcp__tree_sitter__get_ast project="tree-sitter-dotenv" path="test-array.env" include_text=true
   ```

## 6.1 Float/Decimal Support (Deferred from Phase 3)

**MCP TOOLS REQUIRED**:
- Use `mcp__tree_sitter__find_text` to find decimal patterns in test files
- Use `mcp__tree_sitter__get_ast` to analyze current tokenization of decimals
- Use `mcp__tree_sitter__run_query` to test float parsing

### Overview
Decimal and float number support was intentionally deferred from Phase 3 to keep the initial implementation focused on integers and booleans. This section documents the planned implementation.

### Grammar Implementation
```javascript
float: ($) => choice(
  // Standard decimal notation: 3.14, 0.5, -2.718
  seq(
    optional(choice('+', '-')),
    /\d+/,
    '.',
    /\d+/
  ),
  // Scientific notation: 1.23e-4, 6.022E23
  seq(
    optional(choice('+', '-')),
    /\d+/,
    optional(seq('.', /\d+/)),
    /[eE]/,
    optional(choice('+', '-')),
    /\d+/
  )
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

### Test Cases
```env
# Basic decimals
PI=3.14
HALF=0.5
NEGATIVE=-2.718
LEADING_ZERO=0.001

# Scientific notation
SMALL=1.23e-4
LARGE=6.022E23
NEGATIVE_EXP=1.5e-10
POSITIVE_EXP=2.5e+3

# Edge cases
ZERO_DECIMAL=0.0
NO_FRACTION=42.
NO_WHOLE=.5
```

### Highlighting
```scheme
(float) @constant.numeric.float
```

### Current Behavior (Phase 3)
- `DECIMAL=3.14` → Parsed as integer(3) + error(.) + integer(14)
- `SCIENTIFIC=6.022e23` → Parsed as integer(6) + error(.) + integer(22) + identifier(e23)

### Implementation Notes
1. Must parse before integer to avoid conflicts
2. Consider whether to support all float formats (e.g., `.5`, `42.`)
3. Ensure scientific notation doesn't conflict with identifiers
4. Test performance impact of complex regex patterns

## 6.2 Array Support (Deferred)

**MCP TOOLS REQUIRED**:
- Use `mcp__tree_sitter__find_text` to search for array-like patterns
- Use `mcp__tree_sitter__analyze_project` to understand usage patterns
- Use `mcp__tree_sitter__build_query` to create array detection queries

### Implementation Plan for Array Support

Arrays would support:
- `key=[true, false]`
- `key=[1, 2, 3]`
- `key=["a", "b", "c"]`
- `key=[https://a.com, https://b.com]`
- `key=[]` (empty arrays)
- Mixed types: `key=[1, "two", true, https://example.com]`

### Grammar Implementation

```javascript
// Array rule
array: ($) => seq(
  '[',
  optional($._array_elements),
  ']'
),

_array_elements: ($) => seq(
  $._array_element,
  repeat(seq(',', optional(/\s+/), $._array_element)),
  optional(',')  // Allow trailing comma
),

_array_element: ($) => choice(
  $.string_double,
  $.string_single,
  $.bool,
  $.integer,
  $.float,  // If implemented
  $.uri,
  $.url,
  $.array,  // Nested arrays
  $.raw_array_value
),

raw_array_value: ($) => /[^,\[\]\s]+/,

// Update _value to include arrays
_value: ($) => choice(
  $.string_double,
  $.string_single,
  $.bool,
  $.float,
  $.integer,
  $.uri,
  $.url,
  $.array,  // Add here
  alias(token.immediate(/[^\n\r]*/), $.raw_value)
),
```

### Test Cases

```
==================
empty array
==================
key=[]
---
(source_file
  (variable
    name: (identifier)
    value: (array)))

==================
boolean array
==================
key=[true, false, true]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (bool)
      (bool)
      (bool))))

==================
integer array
==================
key=[1, 2, 3, -4, +5]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (integer)
      (integer)
      (integer)
      (integer)
      (integer))))

==================
string array
==================
key=["hello", 'world', "test"]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (string_double)
      (string_single)
      (string_double))))

==================
url array
==================
key=[https://a.com, https://b.com/path]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (url)
      (url))))

==================
mixed type array
==================
key=[1, "two", true, https://example.com]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (integer)
      (string_double)
      (bool)
      (url))))

==================
nested array
==================
key=[[1, 2], [3, 4]]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (array (integer) (integer))
      (array (integer) (integer)))))

==================
array with trailing comma
==================
key=[1, 2, 3,]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (integer)
      (integer)
      (integer))))

==================
array with whitespace
==================
key=[ 1 , 2 , 3 ]
---
(source_file
  (variable
    name: (identifier)
    value: (array
      (integer)
      (integer)
      (integer))))
```

### Highlighting Support

```scheme
; Array brackets
(array "[" @punctuation.bracket)
(array "]" @punctuation.bracket)

; Array commas
(array "," @punctuation.delimiter)

; Array values inherit highlighting from their types
(array (bool) @constant.builtin.boolean)
(array (integer) @constant.numeric.integer)
(array (string_double) @string)
(array (string_single) @string)
(array (url) @markup.link.url)
(array (uri) @markup.link.url)
```

### Implementation Considerations

1. **Performance Impact**
   - Arrays add complexity to parsing
   - Nested arrays could impact performance
   - Consider limiting nesting depth

2. **File Format Compatibility**
   - Arrays are not standard in most KEY=VALUE formats
   - `.env` files typically don't support arrays
   - Some formats use comma-separated values instead
   - Consider alternative: `key=value1,value2,value3`

3. **Alternative Approaches**
   ```bash
   # Option 1: Indexed keys (common in .env)
   HOSTS_0=server1.com
   HOSTS_1=server2.com
   HOSTS_2=server3.com
   
   # Option 2: Comma-separated (common in .properties)
   hosts=server1.com,server2.com,server3.com
   
   # Option 3: JSON value (some modern configs)
   hosts=["server1.com","server2.com","server3.com"]
   ```

4. **Escape Sequences in Arrays**
   - How to handle commas in values?
   - Escape syntax: `key=["value\,with\,commas"]`
   - Or require quotes: `key=["value,with,commas"]`

5. **Error Recovery**
   - Missing closing bracket: `key=[1, 2, 3`
   - Extra commas: `key=[1,,2]`
   - Invalid syntax: `key=[1 2 3]` (missing commas)

### Decision Matrix

| Criteria | Include Arrays | Defer Arrays |
|----------|---------------|--------------|
| Complexity | High | Low |
| Performance | Slower | Faster |
| Compatibility | Limited | Universal |
| Use Cases | Modern configs | Traditional |
| Testing Burden | High | Low |

### Recommendation

**Continue deferring array support** because:

1. Most KEY=VALUE formats don't support arrays natively
2. Alternatives exist (indexed keys, comma-separated)
3. Adds significant complexity for limited benefit
4. Could be added in a backwards-compatible way later
5. Focus on perfecting core KEY=VALUE parsing first

### Future Implementation Path

If arrays are needed later:

1. **Phase 6.1**: Research usage in real configs
2. **Phase 6.2**: Implement basic array parsing
3. **Phase 6.3**: Add nested array support
4. **Phase 6.4**: Performance optimization
5. **Phase 6.5**: Error recovery improvements

Note: Array support has been deferred to keep initial implementation focused on universal KEY=VALUE parsing that works across all configuration file formats.