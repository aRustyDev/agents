# Tree-sitter-dotenv Parser Bug Analysis

## Executive Summary

The tree-sitter-dotenv parser has a critical bug where it fails to correctly parse even the simplest environment variable assignments. The parser incorrectly tokenizes `key=value` as two separate variables instead of one variable with a value.

## Problem Description

### Expected Behavior
```
key=value
```
Should parse as:
```
(source_file
  (variable
    name: (identifier "key")
    value: (raw_value "value")))
```

### Actual Behavior
```
(source_file
  (variable
    name: (identifier "key"))
  (variable
    name: (identifier "value")))
  (MISSING "=")
```

## Root Cause Analysis

### Parser State Machine Issue

The bug occurs due to incorrect lexer state transitions in the generated parser. After consuming an identifier and the "=" token, the parser enters a state where the lexer can still parse identifiers, causing it to interpret the value as a new variable declaration.

### Evidence from Parser Debugging

1. **Simple Test Case**
   ```bash
   echo 'key=value' > test.env
   npx tree-sitter parse test.env
   ```
   
   Output:
   ```
   (source_file [0, 0] - [0, 9]
     (variable [0, 0] - [0, 4]
       name: (identifier [0, 0] - [0, 3]))
     (variable [0, 4] - [0, 9]
       name: (identifier [0, 4] - [0, 9])))
   (MISSING "=")
   ```

2. **Debug Trace Analysis**
   Using `npx tree-sitter parse --debug`:
   - Parser starts in state 1, parses "key" as identifier
   - Sees "=" at position 3 and shifts to state 2
   - **Critical Issue**: State 2 uses lex_state 13
   - In lex_state 13, the lexer sees "value" and parses it as an identifier token
   - This causes the parser to reduce the current variable with only the identifier
   - It then tries to parse "value" as a new variable

3. **Parser.c Analysis**
   From the generated parser.c file:
   ```c
   [2] = {.lex_state = 13},
   ```
   
   State 2 (after consuming "=") uses lex_state 13, which includes identifier parsing rules.

## Reproduction Steps

### Prerequisites
```bash
cd tree-sitter-dotenv
npm install
```

### Test Cases

1. **Basic Assignment (FAILS)**
   ```bash
   echo 'KEY=value' > test1.env
   npx tree-sitter parse test1.env
   # Result: Parses as two variables
   ```

2. **Hyphenated Value (FAILS)**
   ```bash
   echo 'KEY=clone-or-copy' > test2.env
   npx tree-sitter parse test2.env
   # Result: "clone-or-copy" parsed as two variables
   ```

3. **Multiple Lines (WORKS)**
   ```bash
   echo -e 'KEY1=value1\nKEY2=value2' > test3.env
   npx tree-sitter parse test3.env
   # Result: Correctly parses when on separate lines
   ```

4. **Quoted Values (WORKS)**
   ```bash
   echo 'KEY="value"' > test4.env
   npx tree-sitter parse test4.env
   # Result: Quoted strings parse correctly
   ```

### Corpus Test Results
```bash
npx tree-sitter test
```

Multiple failures in basic_identifiers and hyphenated_identifiers tests confirm the issue.

## Impact Analysis

### Affected Scenarios
1. Any unquoted value that matches the identifier pattern
2. Hyphenated values (e.g., `package-import-method=clone-or-copy`)
3. Simple boolean values when unquoted
4. Any value starting with a letter or underscore

### Unaffected Scenarios
1. Quoted string values (single or double quotes)
2. Numeric values
3. URLs (due to specific token pattern)
4. Values on separate lines (due to newline handling)

## Technical Details

### Grammar Structure
```javascript
variable: ($) =>
  seq(field("name", $.identifier), "=", optional(field("value", $.value))),

identifier: ($) => /[a-zA-Z_][a-zA-Z0-9_-]*/,

value: ($) =>
  choice(
    $.string_interpolated,
    $.string_literal,
    $.url,
    $.bool,
    $.integer,
    $.raw_value,
  ),

raw_value: ($) => token(prec(-1, /[^#=\n]+/)),
```

### The Ambiguity Problem
The parser cannot distinguish between:
- An identifier that's part of a value
- An identifier that starts a new variable

This is because after "=", the lexer state still allows identifier tokens.

## Potential Solutions

### Solution 1: External Scanner
Implement a custom external scanner in C that handles tokenization more carefully:
- Track context (before/after "=")
- Return different token types based on position

### Solution 2: Grammar Restructuring
Restructure the grammar to eliminate ambiguity:
```javascript
variable: ($) =>
  seq(
    field("name", $.identifier),
    token.immediate("="),
    field("value", $._value_content)
  ),

_value_content: ($) =>
  token(prec(-1, /[^\n]+/))
```

### Solution 3: Inline Values
Make value parsing inline to prevent identifier matching:
```javascript
variable: ($) =>
  seq(
    field("name", $.identifier),
    "=",
    field("value", token(prec(-1, /[^\n]+/)))
  )
```

### Solution 4: State-based Lexing
Use tree-sitter's state-based lexing features to define different token sets for different contexts.

## Verification Method

To verify a fix works:
1. Run the reproduction test cases above
2. Run `npx tree-sitter test` - all tests should pass
3. Test in Zed editor - syntax highlighting should work correctly
4. Parse complex .npmrc files with various value types

## References

1. Tree-sitter documentation on lexing: https://tree-sitter.github.io/tree-sitter/creating-parsers#lexical-analysis
2. Similar issues in other grammars: https://github.com/tree-sitter/tree-sitter/issues/search?q=lexer+state
3. External scanner examples: https://github.com/tree-sitter/tree-sitter-rust/blob/master/src/scanner.c

## Solution Found

The parser bug was successfully fixed using `token.immediate` for both the equals sign and value capture:

```javascript
variable: ($) =>
  seq(
    field("name", $.identifier), 
    token.immediate("="), 
    field("value", optional(alias($._rest_of_line, $.raw_value)))
  ),

_rest_of_line: ($) => token.immediate(/[^\n\r]*/),
```

This approach forces the parser to immediately consume the equals sign and the rest of the line as the value, preventing the lexer from interpreting the value as a new identifier.

### Key Insights

1. The bug was caused by the parser remaining in a state where identifiers could be parsed after the "=" token
2. Using `token.immediate` ensures tight coupling between the equals sign and value capture
3. The solution required simplifying the grammar structure and being explicit about token boundaries

## Conclusion

This was a fundamental bug in the tree-sitter-dotenv parser that affected its core functionality. The issue stemmed from incorrect lexer state management in the generated parser, causing values to be misinterpreted as new variable declarations. The bug was resolved by using tree-sitter's `token.immediate` feature to enforce proper token sequencing.