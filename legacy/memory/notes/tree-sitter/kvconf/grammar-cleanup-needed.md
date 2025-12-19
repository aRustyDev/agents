# Grammar Cleanup Needed

## Date: 2025-08-31

### Current State

The grammar.js file contains several orphaned rules that are defined but never used in the parsing flow:

1. **Unused String Rules**:
   - `string_interpolated` - for double-quoted strings
   - `string_literal` - for single-quoted strings
   - `_interpolated_content` - helper for interpolation
   - `escape_sequence` - for escape sequences

2. **Unused Primitive Rules**:
   - `bool` - for true/false
   - `integer` - for numeric values

3. **Unused Complex Rules**:
   - `url` - for URL values
   - `interpolated_variable` - for ${VAR} syntax
   - `shell_command` - for $(command) syntax

4. **Miscellaneous**:
   - `value` - seems to be a leftover alias

### The Problem

These rules exist in the grammar but aren't connected to the main `_value` choice, so they're never used during parsing. However, the highlights.scm file references some of these types, causing "Invalid node type" errors.

### Recommended Approach

#### Option 1: Clean Removal (Before Phase 2)
```javascript
// Remove all unused rules
// Keep only what's actively used:
// - source_file
// - _line
// - comment
// - variable
// - identifier
// - _spacing
// - _value
```

#### Option 2: Gradual Integration (During Phases 2-4)
```javascript
// Phase 2: Connect string rules
_value: ($) => choice(
  $.string_interpolated,  // Was orphaned, now connected
  $.string_literal,       // Was orphaned, now connected
  alias(token.immediate(/[^\n\r]*/), $.raw_value)
)

// Phase 3: Connect primitive rules
_value: ($) => choice(
  $.string_interpolated,
  $.string_literal,
  $.bool,                 // Was orphaned, now connected
  $.integer,              // Was orphaned, now connected
  alias(token.immediate(/[^\n\r]*/), $.raw_value)
)
```

### Decision Factors

1. **Clean Removal Pros**:
   - Cleaner grammar file
   - No confusion about what's used
   - Easier to understand

2. **Gradual Integration Pros**:
   - Rules are already written
   - Just need to connect them
   - Might save implementation time

### Recommendation

**Use Gradual Integration** but with modifications:
1. Test each orphaned rule to see if it works correctly
2. Modify as needed to match the plan specifications
3. Remove `value` alias entirely - it's confusing
4. Document which rules are placeholder vs active

### Action Items

- [ ] Decision needed at start of Phase 2
- [ ] Update Phase 2 plan based on decision
- [ ] Clean up `value` alias regardless of approach