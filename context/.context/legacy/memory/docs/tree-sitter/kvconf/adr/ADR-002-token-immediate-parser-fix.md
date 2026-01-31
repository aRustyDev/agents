# ADR-002: Token.immediate for Parser Fix

## Status
Accepted

## Context
A critical parser bug was discovered where `key=value` was being parsed as two separate variables:
- `key` as a variable with MISSING "="
- `value` as another variable with MISSING "="

The issue occurred because after consuming the "=" token, the parser remained in a state where it could still accept identifiers, causing the value portion to be incorrectly tokenized as a new variable declaration.

### Example of the Bug
Input: `key=value`

Incorrect parse tree:
```
(source_file
  (variable (identifier) (MISSING "="))
  (variable (identifier) (MISSING "=")))
```

Expected parse tree:
```
(source_file
  (variable
    name: (identifier)
    value: (value)))
```

## Decision
Use `token.immediate` to create a tight coupling between the "=" token and the value that follows it, preventing the parser from transitioning to a state where it can accept new identifiers.

### Implementation
```javascript
variable: ($) =>
  seq(
    field("name", $.identifier),
    token.immediate("="),  // Tight coupling, no state transition
    field("value", optional(alias(
      token.immediate(/[^\n\r]*/),  // Immediately consume value
      $.value
    )))
  ),
```

## Consequences

### Positive
- **Fixes the parser bug**: Values are correctly associated with their keys
- **Prevents ambiguity**: Parser state machine cannot misinterpret values
- **Maintains performance**: No additional parsing overhead
- **Simple solution**: Minimal code change with maximum impact

### Negative
- **No spacing after =**: Cannot have `key= value` (space after equals)
- **Less flexibility**: Tighter grammar rules
- **Learning curve**: `token.immediate` is less commonly used

### Neutral
- Changes the tokenization behavior for all KEY=VALUE pairs
- May affect error recovery in malformed input
- Requires understanding of tree-sitter's lexer states

## Technical Explanation
`token.immediate` works by:
1. Preventing the lexer from returning control to the parser
2. Forcing immediate consumption of the next pattern
3. Avoiding state transitions that would allow identifier recognition

Without `token.immediate`, the parser's state machine would:
1. Parse `key` as identifier ✓
2. Parse `=` as equals token ✓
3. Return to a state accepting identifiers ✗
4. Parse `value` as a new identifier ✗

With `token.immediate`, the parser:
1. Parse `key` as identifier ✓
2. Parse `=` with immediate continuation ✓
3. Immediately parse value content ✓
4. Cannot interpret value as identifier ✓

## Verification
```bash
# Test the fix
echo 'key=value' | npx tree-sitter parse -
# Should show: (variable name: (identifier) value: (value))

# Test edge cases
echo 'key=' | npx tree-sitter parse -        # Empty value
echo 'key=123' | npx tree-sitter parse -     # Numeric value
echo 'key=true' | npx tree-sitter parse -    # Boolean value
```

## References
- [Parser Bug Analysis](../analysis/ANALYSIS.md)
- [Tree-sitter token.immediate documentation](https://tree-sitter.github.io/tree-sitter/creating-parsers#immediate-tokens)
- Test cases demonstrating the fix