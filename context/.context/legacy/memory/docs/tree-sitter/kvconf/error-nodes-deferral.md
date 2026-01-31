# Error Node Types Deferral Documentation

## Original Plan (Phase 4)

Phase 4 originally specified implementing error node types:

```javascript
// From Phase 4 plan:
error_trailing_comma: ($) => ',',
error_multiple_values: ($) => /[^\n\r#]+/,
error: ($) => /[^\n\r]+/,  // Catch-all
```

## Why Deferred

During Phase 4 implementation, error node types were deferred because:

1. **Tree-sitter's built-in error recovery** is already handling most error cases adequately
2. **Grammar complexity** - Adding specific error nodes would require significant restructuring of the parsing rules
3. **Limited benefit** - The current ERROR nodes from tree-sitter provide sufficient information for most use cases
4. **Better suited for edge case handling** - Error nodes make more sense when addressing specific edge cases rather than as a general implementation

## Current Error Handling

Currently, tree-sitter automatically generates ERROR nodes when:
- Unexpected tokens are encountered (e.g., `KEY=123abc` → integer + ERROR)
- Missing required tokens (e.g., missing `=` in variable declaration)
- Invalid token sequences

## Deferred To

Error node types have been **explicitly added to Phase 5** (Edge Cases and Polish) in section 5.1:

```markdown
5. **Error Node Types (deferred from Phase 4)**
   - Specific error types for better error reporting
   - Test cases for multiple values, trailing content, missing equals
   - Implementation checklist includes error node highlighting
```

## Phase 5 Implementation Plan

When implementing in Phase 5:

1. **Identify common error patterns** from real-world usage
2. **Create specific error nodes** for those patterns
3. **Add highlighting rules** for error nodes (red color in Zed)
4. **Test error recovery** doesn't break existing functionality
5. **Document error node behavior** for users

## Benefits When Implemented

- More precise error messages
- Better syntax highlighting for errors
- Clearer feedback for users about what's wrong
- Potential for better error recovery strategies

## Current Status

✅ Phase 4 complete without error nodes
📋 Error nodes documented in Phase 5 plan
⏳ To be implemented when Phase 5 begins